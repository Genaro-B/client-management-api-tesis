"""Constructor de contexto para el cerebro Ollama.

Compone un string en español con **datos reales** del sistema reutilizando
los handlers ya probados de `AdminBotService` (ventas del día, stock bajo,
métricas generales y, si corresponde, ticket de un cliente). El objetivo es
que Ollama tenga números reales en el prompt y no tenga que inventarlos.
"""
from sqlalchemy.orm import Session

from src.services.admin_bot.admin_intent_router import INTENT_NO_ENTENDIDO


def _seccion(titulo: str, builder) -> str:
    """Ejecuta un builder de sección; si falla, no rompe el contexto."""
    try:
        return f"- {titulo}: {builder()}"
    except Exception:
        return f"- {titulo}: (no disponible)"


def construir_contexto(
    db: Session, texto: str = "", intent: str = INTENT_NO_ENTENDIDO
) -> str:
    """Devuelve un contexto estructurado en español con datos reales.

    Reutiliza los handlers reales de `AdminBotService.respond()` para
    garantizar que los números coinciden con el resto del sistema.
    """
    # Import local para evitar ciclos de importación con el servicio.
    from src.services.admin_bot.admin_bot_service import AdminBotService

    servicio = AdminBotService(db)

    partes = [
        f"Consulta del administrador: {texto}" if texto else "Consulta del administrador: (sin texto)",
        "Datos reales del sistema:",
        _seccion("Ventas de hoy", lambda: servicio.respond("ventas-hoy", texto=texto)),
        _seccion("Productos con stock bajo", lambda: servicio.respond("stock-bajo")),
        _seccion("Resumen general", lambda: servicio.respond("metricas-generales")),
    ]

    # Si la consulta apunta a un cliente puntual, incluimos su ticket.
    if intent == "ticket-cliente":
        partes.append(_seccion("Ticket del cliente", lambda: servicio.respond("ticket-cliente", texto=texto)))

    return "\n".join(partes)
