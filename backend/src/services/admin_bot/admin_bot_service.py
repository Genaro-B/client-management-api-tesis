"""Servicio del asistente administrativo: compone respuestas con datos REALES.

Usa la misma capa de repositories que alimenta los endpoints existentes
(ClientRepository, ProductRepository y queries directas a Interaction),
garantizando por construcción que las respuestas reflejan el estado real
de la base de datos — nunca datos inventados.
"""
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Tuple

from sqlalchemy.orm import Session

from src.core.config import LOW_STOCK_THRESHOLD, get_admin_bot_brain, get_admin_bot_nlu_threshold
from src.models.client import Client
from src.models.interaction import Interaction
from src.models.product import Product
from src.repositories.client_repo import ClientRepository
from src.repositories.product_repo import ProductRepository
from src.services.admin_bot.admin_intent_router import (
    INTENT_NO_ENTENDIDO,
    AdminIntentRouter,
    normalizar,
)
from src.services.sale_service import SaleService

# Cantidad máxima de ítems detallados que se listan en una respuesta.
MAX_DETALLE = 5


class AdminBotService:
    """Construye la respuesta para una intención administrativa detectada.

    Uso:
        service = AdminBotService(db)
        intent = AdminIntentRouter().match(texto)
        respuesta = service.respond(intent)
    """

    def __init__(self, db: Session):
        self.db = db
        self.client_repo = ClientRepository(db)
        self.product_repo = ProductRepository(db)
        self.router = AdminIntentRouter()

    # ------------------------------------------------------------------
    # Punto de entrada
    # ------------------------------------------------------------------

    def resolver(self, texto: str) -> Tuple[str, str]:
        """Resuelve una consulta en lenguaje natural: `(intent, respuesta)`.

        Implementa la **cascada de cerebros** seleccionable por
        `ADMIN_BOT_BRAIN`:

        - `deterministic`: SOLO el matcher determinístico (idéntico al actual).
        - `classifier` (default): matcher primero; si devuelve `no-entendido`,
          consulta el clasificador local (umbral configurable). Sigue siendo
          `no-entendido` si la confianza no alcanza.
        - `ollama`: intenta el cerebro Ollama (si está implementado); ante
          error o falta de comprensión cae de vuelta al matcher determinístico.

        El matcher determinístico SIEMPRE corre primero (excepto en modo
        `ollama`), garantizando que no se rompe ningún comportamiento probado.
        """
        texto = (texto or "").strip()
        brain = get_admin_bot_brain()

        if brain == "ollama":
            return self._resolver_ollama(texto)

        intent = self.router.match(texto)

        if brain == "classifier" and intent == INTENT_NO_ENTENDIDO:
            intent = self._clasificar_fallback(texto)

        return intent, self.respond(intent, texto=texto)

    def _clasificar_fallback(self, texto: str) -> str:
        """Consulta el clasificador local y devuelve la intención (o no-entendido)."""
        # Import diferido: evita cargar scikit-learn si el cerebro es determinístico.
        from src.services.admin_bot.nlu.classifier import clasificar

        intent, _confianza = clasificar(texto, get_admin_bot_nlu_threshold())
        return intent

    def _resolver_ollama(self, texto: str) -> Tuple[str, str]:
        """Cerebro Ollama con fallback determinístico (ver grupo 4)."""
        from src.services.admin_bot.ollama.brain import resolver_con_ollama

        return resolver_con_ollama(self, texto)

    def respond(self, intent: str, texto: str = "") -> str:
        """Devuelve la respuesta textual para la intención dada.

        `texto` es el mensaje original: lo necesitan las intenciones que
        extraen parámetros (p. ej. `ticket-cliente`: fecha + nombre).
        """
        handlers = {
            "clientes-nuevos-mes": self._clientes_nuevos_mes,
            "stock-bajo": self._stock_bajo,
            "interacciones-hoy": self._interacciones_hoy,
            "producto-top": self._producto_top,
            "metricas-generales": self._metricas_generales,
            "ventas-hoy": self._ventas_hoy,
            "ticket-cliente": self._ticket_cliente,
        }
        handler = handlers.get(intent)
        if handler is None:
            return self._no_entendido()
        if intent in ("ventas-hoy", "ticket-cliente"):
            return handler(texto)
        return handler()

    # ------------------------------------------------------------------
    # Handlers por intención
    # ------------------------------------------------------------------

    def _clientes_nuevos_mes(self) -> str:
        """Clientes no-admin registrados desde el primer día del mes."""
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        clientes = (
            self.db.query(Client)
            .filter(
                Client.role != "admin",
                Client.fecha_registro >= month_start,
            )
            .order_by(Client.fecha_registro.desc())
            .all()
        )
        if not clientes:
            return "No hay clientes nuevos este mes todavía."

        detalle = ", ".join(
            f"{c.nombre} {c.apellido}" for c in clientes[:MAX_DETALLE]
        )
        resto = len(clientes) - MAX_DETALLE
        if resto > 0:
            detalle += f" y {resto} más."

        return f"Hay {len(clientes)} cliente{'s' if len(clientes) != 1 else ''} nuevo{'s' if len(clientes) != 1 else ''} este mes: {detalle}."

    def _stock_bajo(self) -> str:
        """Productos activos con stock <= LOW_STOCK_THRESHOLD."""
        productos = (
            self.db.query(Product)
            .filter(Product.activo.is_(True))
            .order_by(Product.stock.asc())
            .all()
        )
        bajos = [p for p in productos if p.stock <= LOW_STOCK_THRESHOLD]

        if not bajos:
            return (
                f"No hay productos con stock bajo. Todo el catálogo está por "
                f"encima del umbral de {LOW_STOCK_THRESHOLD} unidades."
            )

        lineas = [
            f"• {p.nombre}: {p.stock} unidad{'es' if p.stock != 1 else ''}"
            for p in bajos[:MAX_DETALLE]
        ]
        resto = len(bajos) - MAX_DETALLE
        if resto > 0:
            lineas.append(f"• y {resto} producto{'s' if resto != 1 else ''} más.")

        return (
            f"Hay {len(bajos)} producto{'s' if len(bajos) != 1 else ''} con stock bajo "
            f"(umbral ≤ {LOW_STOCK_THRESHOLD}):\n" + "\n".join(lineas)
        )

    def _interacciones_hoy(self) -> str:
        """Cantidad de interacciones desde el inicio del día."""
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        total = (
            self.db.query(Interaction)
            .filter(Interaction.timestamp >= today_start)
            .count()
        )
        if total == 0:
            return "Hoy todavía no hubo interacciones registradas."
        return f"Hoy hubo {total} interacción{'es' if total != 1 else ''} registrada{'s' if total != 1 else ''}."

    def _producto_top(self) -> str:
        """Top 5 productos por cantidad total asignada (JSON productos_asignados).

        SQLite no ofrece agregación JSON confiable: una única pasada en Python
        suma las cantidades por producto_id entre todos los clientes no-admin.
        """
        clientes = (
            self.db.query(Client)
            .filter(Client.role != "admin")
            .all()
        )
        cantidades: dict = defaultdict(int)
        for cliente in clientes:
            for item in (cliente.productos_asignados or []):
                if isinstance(item, dict) and item.get("producto_id"):
                    cantidades[item["producto_id"]] += int(item.get("cantidad", 0))

        if not cantidades:
            return "Todavía no hay productos asignados a clientes, así que no hay un producto más vendido."

        top = sorted(cantidades.items(), key=lambda kv: kv[1], reverse=True)[:MAX_DETALLE]

        # Resolver nombres de producto en una sola query
        nombres = {}
        if top:
            ids = [pid for pid, _ in top]
            filas = self.db.query(Product.id, Product.nombre).filter(Product.id.in_(ids)).all()
            nombres = {pid: nombre for pid, nombre in filas}

        primero_id, primero_cantidad = top[0]
        primero_nombre = nombres.get(primero_id, f"ID {primero_id}")

        if len(top) == 1:
            return (
                f"El producto más vendido es {primero_nombre} con "
                f"{primero_cantidad} unidad{'es' if primero_cantidad != 1 else ''} asignada{'s' if primero_cantidad != 1 else ''}."
            )

        lineas = [
            f"{i + 1}. {nombres.get(pid, f'ID {pid}')} ({cantidad} uds.)"
            for i, (pid, cantidad) in enumerate(top)
        ]
        return (
            f"El producto más vendido es {primero_nombre} con {primero_cantidad} "
            f"unidad{'es' if primero_cantidad != 1 else ''}. Top {len(top)}:\n"
            + "\n".join(lineas)
        )

    def _metricas_generales(self) -> str:
        """Resumen general: mismos cálculos que GET /metrics/dashboard summary."""
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today_start - timedelta(days=7)

        total_clientes = (
            self.db.query(Client).filter(Client.role != "admin").count()
        )
        activos = (
            self.db.query(Client)
            .filter(Client.role != "admin", Client.activo.is_(True))
            .count()
        )
        inactivos = total_clientes - activos

        total_interacciones = self.db.query(Interaction).count()
        hoy = (
            self.db.query(Interaction)
            .filter(Interaction.timestamp >= today_start)
            .count()
        )
        semana = (
            self.db.query(Interaction)
            .filter(Interaction.timestamp >= week_ago)
            .count()
        )

        return (
            f"Resumen del negocio:\n"
            f"• Clientes: {total_clientes} totales ({activos} activos, {inactivos} inactivos)\n"
            f"• Interacciones: {total_interacciones} totales, {hoy} hoy, {semana} en la última semana"
        )

    def _no_entendido(self) -> str:
        """Fallback amigable que lista las consultas soportadas."""
        return (
            "No entendí tu consulta. Probá con alguna de estas opciones:\n"
            "• \"clientes nuevos del mes\"\n"
            "• \"productos con stock bajo\"\n"
            "• \"interacciones de hoy\"\n"
            "• \"producto más vendido\"\n"
            "• \"cuántas ventas hubo hoy\"\n"
            "• \"qué compró Juan ayer\"\n"
            "• \"resumen de métricas\""
        )

    # ------------------------------------------------------------------
    # Intenciones de ventas
    # ------------------------------------------------------------------

    def _ventas_hoy(self, texto: str = "") -> str:
        """Cantidad e ingresos de las ventas de HOY (solo base contable)."""
        hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        ventas = SaleService(self.db).ventas_del_dia(hoy)
        if not ventas:
            return "Hoy no hubo ventas registradas."
        ingresos = sum(v.total for v in ventas)
        plural = "s" if len(ventas) != 1 else ""
        return (
            f"Hoy hubo {len(ventas)} venta{plural} por un total de "
            f"${ingresos:.2f}."
        )

    def _extraer_fecha(self, texto: str) -> str:
        """Extrae `YYYY-MM-DD` de 'hoy'/'ayer'/'dd-mm-yyyy'; default hoy."""
        hoy = datetime.now(timezone.utc).date()
        norm = normalizar(texto or "")
        if "ayer" in norm:
            return (hoy - timedelta(days=1)).strftime("%Y-%m-%d")
        m = re.search(r"\b(\d{2})-(\d{2})-(\d{4})\b", norm)
        if m:
            return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
        return hoy.strftime("%Y-%m-%d")

    def _extraer_nombre(self, texto: str) -> str:
        """Quita palabras-consulta y fechas para quedarse con el nombre cliente."""
        norm = normalizar(texto or "")
        norm = re.sub(r"\b\d{1,2}-\d{1,2}-\d{4}\b", " ", norm)
        for kw in (
            "que se compro", "que compro", "ticket cliente",
            "ticket de", "ticket del", "compra de",
        ):
            norm = norm.replace(kw, " ")
        for w in (
            "hoy", "ayer", "ticket", "que", "compro", "compra",
            "el", "la", "los", "las", "de", "del", "un", "una",
        ):
            norm = re.sub(rf"\b{w}\b", " ", norm)
        return " ".join(norm.split())

    def _ticket_cliente(self, texto: str = "") -> str:
        """Detalle del ticket de un cliente (ILIKE) en la fecha indicada."""
        fecha = self._extraer_fecha(texto)
        nombre = self._extraer_nombre(texto)
        if not nombre:
            return "Decime el nombre del cliente para buscar su ticket."

        cliente, ventas = SaleService(self.db).ticket(nombre, fecha)
        if cliente is None or not ventas:
            return "No se encontraron ventas para ese cliente en esa fecha."

        nombres = {}
        ids = {item.product_id for v in ventas for item in v.items}
        if ids:
            filas = (
                self.db.query(Product.id, Product.nombre)
                .filter(Product.id.in_(ids))
                .all()
            )
            nombres = {pid: nombre for pid, nombre in filas}

        lineas = []
        for venta in ventas:
            for item in venta.items:
                pnombre = nombres.get(item.product_id, f"ID {item.product_id}")
                subtotal = item.cantidad * item.precio_unitario
                lineas.append(f"• {item.cantidad} x {pnombre} — ${subtotal:.2f}")

        total = sum(v.total for v in ventas)
        return (
            f"Ticket de {cliente.nombre} {cliente.apellido} ({fecha}):\n"
            + "\n".join(lineas)
            + f"\nTotal: ${total:.2f}"
        )