"""Cerebro Ollama: intenta responder con el LLM local y hace fallback.

El servicio llama a `resolver_con_ollama(service, texto)` solo cuando
`ADMIN_BOT_BRAIN=ollama`. Ante cualquier fallo (`OllamaError`) cae de vuelta
al matcher determinístico (o a `no-entendido`), garantizando robustez.
"""
from typing import Tuple

from src.services.admin_bot.ollama.client import OllamaError, preguntar
from src.services.admin_bot.ollama.context_builder import construir_contexto


def resolver_con_ollama(service, texto: str) -> Tuple[str, str]:
    """Resuelve la consulta con Ollama; fallback determinístico ante error.

    Args:
        service: instancia de `AdminBotService` (da acceso a db, router y handlers).
        texto: consulta original en lenguaje natural.

    Returns:
        `(intent, respuesta)`. Si Ollama responde, la respuesta es su contenido
        y la intención la provee el matcher determinístico. Si falla, se usa la
        resolución determinística pura.
    """
    intent = service.router.match(texto)
    try:
        contexto = construir_contexto(service.db, texto, intent)
        contenido = preguntar(texto, contexto)
        return intent, contenido
    except OllamaError:
        # Fallback graceful: matcher determinístico (incluye no-entendido).
        return intent, service.respond(intent, texto=texto)
