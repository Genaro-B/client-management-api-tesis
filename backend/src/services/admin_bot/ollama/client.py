"""Cliente HTTP para Ollama (opcional, deshabilitado por defecto).

Habla con `POST {OLLAMA_URL}/api/chat` usando `httpx`, con `stream: false`.
La respuesta esperada es `{"message": {"content": "..."}}`.

Todos los errores de red/timeout/HTTP/respuesta inesperada se traducen a
`OllamaError` (excepción **controlada**) para que el servicio pueda hacer
fallback graceful sin romper nunca la app. Nunca se importa ni se requiere
un servidor Ollama para correr la aplicación o los tests.
"""
import httpx

from src.core.config import get_ollama_model, get_ollama_timeout_seconds, get_ollama_url

# Prompt de sistema rioplatense: fija el rol y prohíbe inventar números.
SYSTEM_PROMPT = (
    "Sos un asistente administrativo de un sistema de gestión de clientes. "
    "Respondé en español rioplatense, breve y claro. "
    "Usá SOLO los datos del contexto para números; si no sabés, decilo."
)


class OllamaError(Exception):
    """Error controlado del cerebro Ollama (red, timeout, HTTP o formato)."""


def preguntar(texto: str, contexto: str = "") -> str:
    """Pregunta a Ollama y devuelve el contenido de la respuesta.

    Args:
        texto: consulta original del administrador.
        contexto: datos reales construidos por `context_builder`.

    Returns:
        El texto de `message.content`.

    Raises:
        OllamaError: ante cualquier fallo (conexión, timeout, HTTP, o
            respuesta vacía/inesperada).
    """
    url = f"{get_ollama_url().rstrip('/')}/api/chat"
    payload = {
        "model": get_ollama_model(),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": f"Contexto (datos reales):\n{contexto}"},
            {"role": "user", "content": texto},
        ],
        "stream": False,
    }

    try:
        respuesta = httpx.post(url, json=payload, timeout=get_ollama_timeout_seconds())
        respuesta.raise_for_status()
        data = respuesta.json()
        contenido = (data.get("message") or {}).get("content", "")
    except httpx.ConnectError as exc:
        raise OllamaError(f"No se pudo conectar con Ollama en {url}") from exc
    except httpx.TimeoutException as exc:
        raise OllamaError("Timeout al consultar Ollama") from exc
    except httpx.HTTPStatusError as exc:
        raise OllamaError(f"Ollama respondió con error HTTP: {exc}") from exc
    except (TypeError, ValueError, KeyError, AttributeError) as exc:
        raise OllamaError("Respuesta inesperada de Ollama") from exc

    if not isinstance(contenido, str) or not contenido.strip():
        raise OllamaError("Ollama devolvió una respuesta vacía")
    return contenido
