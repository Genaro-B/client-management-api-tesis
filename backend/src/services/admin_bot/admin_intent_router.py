"""Router determinístico de intenciones administrativas.

Clasifica texto libre en español en una intención administrativa usando
pattern matching por palabras clave (sin IA ni ML), replicando la técnica
del Bot Router de la tesis: patrones de texto -> intención -> acción.

Las intenciones soportadas son:
    - clientes-nuevos-mes
    - stock-bajo
    - interacciones-hoy
    - producto-top
    - metricas-generales
    - no-entendido (fallback)

El router prioriza los patrones en el orden definido en el mapa y devuelve
la primera coincidencia. Es una función pura: sin estado ni IO, por lo que
es directamente testeable con pytest.
"""
import re
from typing import Dict, List

# Fallback para texto irreconocible. Se usa la constante para no repetir el string.
INTENT_NO_ENTENDIDO = "no-entendido"

# Normalización de texto: minúsculas y sin tildes (métricas == metricas).
_ACCENTS = str.maketrans(
    "áéíóúüñ",
    "aeiouun",
)


def normalizar(texto: str) -> str:
    """Normaliza texto para el matcher: minúsculas y sin tildes."""
    return texto.lower().translate(_ACCENTS)


class AdminIntentRouter:
    """Clasifica texto libre en español en una intención administrativa.

    Uso:
        router = AdminIntentRouter()
        intent = router.match("¿cuántos clientes nuevos hay este mes?")
        # -> "clientes-nuevos-mes"
    """

    # Mapa intención -> lista de patrones (keywords en español, sin tildes).
    # El orden del diccionario define la prioridad: los patrones más
    # específicos se evalúan primero para evitar falsos positivos.
    PATTERNS: Dict[str, List[str]] = {
        "clientes-nuevos-mes": [
            "clientes nuevos",
            "nuevos clientes",
            "cliente nuevo",
            "nuevo cliente",
            "clientes del mes",
            "clientes este mes",
            "registrados este mes",
            "dados de alta este mes",
        ],
        "stock-bajo": [
            "stock bajo",
            "bajo stock",
            "poco stock",
            "sin stock",
            "agotado",
            "agotados",
        ],
        "interacciones-hoy": [
            "interacciones hoy",
            "interacciones de hoy",
            "hubo hoy",
            "interacciones del dia",
            "mensajes hoy",
        ],
        "producto-top": [
            "mas vendido",
            "mejor vendido",
            "vendio mas",
            "vendieron mas",
            "cual vendio mas",
            "producto top",
            "top producto",
        ],
        "metricas-generales": [
            "como vamos",
            "como va",
            "metricas",
            "resumen",
            "como esta el negocio",
            "como va el negocio",
        ],
    }

    def __init__(self) -> None:
        # Compilamos los patrones una sola vez para eficiencia.
        self._compiled = {
            intent: [
                re.compile(rf"\b{re.escape(normalizar(patron))}\b")
                for patron in patrones
            ]
            for intent, patrones in self.PATTERNS.items()
        }

    def match(self, texto: str) -> str:
        """Devuelve la intención detectada para el texto; fallback a no-entendido."""
        texto_normalizado = normalizar(texto or "")
        for intent, patrones in self._compiled.items():
            for patron in patrones:
                if patron.search(texto_normalizado):
                    return intent
        return INTENT_NO_ENTENDIDO