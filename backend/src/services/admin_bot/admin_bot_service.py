"""Servicio del asistente administrativo: compone respuestas con datos REALES.

Usa la misma capa de repositories que alimenta los endpoints existentes
(ClientRepository, ProductRepository y queries directas a Interaction),
garantizando por construcción que las respuestas reflejan el estado real
de la base de datos — nunca datos inventados.
"""
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Tuple

from sqlalchemy.orm import Session

from src.core.config import LOW_STOCK_THRESHOLD
from src.models.client import Client
from src.models.interaction import Interaction
from src.models.product import Product
from src.repositories.client_repo import ClientRepository
from src.repositories.product_repo import ProductRepository
from src.services.admin_bot.admin_intent_router import INTENT_NO_ENTENDIDO

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

    # ------------------------------------------------------------------
    # Punto de entrada
    # ------------------------------------------------------------------

    def respond(self, intent: str) -> str:
        """Devuelve la respuesta textual para la intención dada."""
        handlers = {
            "clientes-nuevos-mes": self._clientes_nuevos_mes,
            "stock-bajo": self._stock_bajo,
            "interacciones-hoy": self._interacciones_hoy,
            "producto-top": self._producto_top,
            "metricas-generales": self._metricas_generales,
        }
        handler = handlers.get(intent)
        if handler is None:
            return self._no_entendido()
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
            "• \"resumen de métricas\""
        )