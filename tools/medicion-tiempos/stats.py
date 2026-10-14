"""Funciones puras de estadística para la medición de tiempos y estabilidad.

Sin dependencias más allá de la biblioteca estándar, sin I/O y sin estado:
se pueden probar de forma aislada y reutilizarse desde el script de medición.

Criterios de cálculo declarados para que los números sean reproducibles:

- Desviación estándar **muestral** (división por n - 1), la misma que usa la
  fórmula del intervalo de confianza de la tesis.
- Intervalo de confianza 95 % con **z = 1,96**, exactamente
  ``x̄ ± 1,96 · s / √n``, igual que la sección 5.2 del documento.
- Percentil con **interpolación lineal**, el criterio por defecto de NumPy y
  de la función ``PERCENTILE.INC`` de Excel: ``idx = (p / 100) · (n - 1)``.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence

Z_IC_95 = 1.96


def _valores(xs: Sequence[float] | Iterable[float]) -> list[float]:
    datos = [float(x) for x in xs]
    if not datos:
        raise ValueError("se necesita al menos un valor")
    return datos


def media(xs: Sequence[float] | Iterable[float]) -> float:
    """Media aritmética simple."""
    datos = _valores(xs)
    return sum(datos) / len(datos)


def mediana(xs: Sequence[float] | Iterable[float]) -> float:
    """Mediana: valor central o promedio de los dos centrales si n es par."""
    datos = sorted(_valores(xs))
    n = len(datos)
    medio = n // 2
    if n % 2:
        return datos[medio]
    return (datos[medio - 1] + datos[medio]) / 2


def percentil(xs: Sequence[float] | Iterable[float], p: float) -> float:
    """Percentil `p` por interpolación lineal (criterio de NumPy 'linear')."""
    if not 0 <= p <= 100:
        raise ValueError("p debe estar entre 0 y 100")
    datos = sorted(_valores(xs))
    if len(datos) == 1:
        return datos[0]
    idx = (p / 100) * (len(datos) - 1)
    bajo = math.floor(idx)
    alto = math.ceil(idx)
    if bajo == alto:
        return datos[bajo]
    return datos[bajo] + (idx - bajo) * (datos[alto] - datos[bajo])


def desviacion(xs: Sequence[float] | Iterable[float]) -> float:
    """Desviación estándar muestral (n - 1)."""
    datos = _valores(xs)
    if len(datos) < 2:
        return 0.0
    promedio = sum(datos) / len(datos)
    varianza = sum((x - promedio) ** 2 for x in datos) / (len(datos) - 1)
    return math.sqrt(varianza)


def intervalo_confianza(
    xs: Sequence[float] | Iterable[float], z: float = Z_IC_95
) -> tuple[float, float]:
    """IC 95 % de la media: ``x̄ ± z · s / √n``."""
    datos = _valores(xs)
    promedio = sum(datos) / len(datos)
    if len(datos) < 2:
        return (promedio, promedio)
    semiancho = z * desviacion(datos) / math.sqrt(len(datos))
    return (promedio - semiancho, promedio + semiancho)


def coeficiente_variacion(xs: Sequence[float] | Iterable[float]) -> float:
    """CV = s / x̄ · 100, en porcentaje."""
    datos = _valores(xs)
    promedio = sum(datos) / len(datos)
    if promedio == 0:
        raise ValueError("la media no puede ser cero")
    return desviacion(datos) / promedio * 100


def resumen_estabilidad(codigos: Sequence[int] | Iterable[int]) -> dict:
    """Agrupa códigos de estado HTTP por familia y calcula la tasa de 5xx.

    La tasa se devuelve en porcentaje y es 0 cuando no hubo solicitudes:
    así el umbral de ≥ 1 % de errores 5xx se contrasta sin divisiones por cero.
    """
    conteo = {f"{familia}xx": 0 for familia in range(2, 6)}
    total = 0
    for codigo in codigos:
        total += 1
        familia = int(codigo) // 100
        clave = f"{familia}xx"
        if clave in conteo:
            conteo[clave] += 1
    tasa = (conteo["5xx"] / total * 100) if total else 0.0
    return {
        "total": total,
        **conteo,
        "tasa_5xx": tasa,
    }
