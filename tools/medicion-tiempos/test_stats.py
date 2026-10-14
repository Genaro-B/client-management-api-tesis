"""Tests de las funciones puras de estadística de la medición de tiempos.

TDD: estos tests definen el contrato de stats.py antes de que exista.
Cubren: media, mediana (par/impar), percentil (interpolación lineal),
desviación muestral, intervalo de confianza con z = 1,96, coeficiente de
variación y el resumen de estabilidad por código de estado HTTP.
"""
import math

import pytest

from stats import (
    coeficiente_variacion,
    desviacion,
    intervalo_confianza,
    media,
    mediana,
    percentil,
    resumen_estabilidad,
)


# --- media -----------------------------------------------------------------

def test_media_par_de_pares():
    assert media([2.0, 4.0, 6.0]) == 4.0


def test_media_con_un_elemento():
    assert media([10.0]) == 10.0


def test_media_lista_vacia_levanta_value_error():
    with pytest.raises(ValueError):
        media([])


# --- mediana ---------------------------------------------------------------

def test_mediana_cantidad_impar():
    assert mediana([3.0, 1.0, 2.0]) == 2.0


def test_mediana_cantidad_par_es_el_promedio_de_los_dos_centrales():
    assert mediana([1.0, 2.0, 3.0, 4.0]) == 2.5


def test_mediana_no_depende_del_orden():
    assert mediana([4.0, 1.0, 3.0, 2.0]) == 2.5


def test_mediana_lista_vacia_levanta_value_error():
    with pytest.raises(ValueError):
        mediana([])


# --- percentil (interpolación lineal, mismo criterio que numpy 'linear') ----

def test_percentil_0_devuelve_el_minimo():
    assert percentil([10.0, 20.0, 30.0], 0) == 10.0


def test_percentil_100_devuelve_el_maximo():
    assert percentil([10.0, 20.0, 30.0], 100) == 30.0


def test_percentil_50_coincide_con_la_mediana():
    datos = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert percentil(datos, 50) == mediana(datos) == 3.0


def test_percentil_95_con_cien_valores_interpola():
    datos = [float(v) for v in range(1, 101)]
    # idx = 0.95 * 99 = 94.05 -> entre 95 y 96 -> 95 + 0.05 * 1
    assert percentil(datos, 95) == pytest.approx(95.05)


def test_percentil_con_un_solo_valor_devuelve_ese_valor():
    assert percentil([5.0], 95) == 5.0


def test_percentil_lista_vacia_levanta_value_error():
    with pytest.raises(ValueError):
        percentil([], 95)


def test_percentil_fuera_de_rango_levanta_value_error():
    with pytest.raises(ValueError):
        percentil([1.0, 2.0], 101)
    with pytest.raises(ValueError):
        percentil([1.0, 2.0], -1)


# --- desviación estándar muestral (división por n - 1) ---------------------

def test_desviacion_de_1_2_3_es_1():
    assert desviacion([1.0, 2.0, 3.0]) == pytest.approx(1.0)


def test_desviacion_de_valores_iguales_es_cero():
    assert desviacion([5.0, 5.0, 5.0]) == 0.0


def test_desviacion_lista_vacia_levanta_value_error():
    with pytest.raises(ValueError):
        desviacion([])


# --- intervalo de confianza 95 % (x̄ ± 1,96 · s / √n, fórmula de la tesis) ---

def test_ic95_usa_z_1_96_y_raiz_de_n():
    # x̄ = 2, s = 1, n = 3 -> semiancho = 1,96 / √3 = 1,1316065...
    low, high = intervalo_confianza([1.0, 2.0, 3.0])
    assert low == pytest.approx(0.8683935)
    assert high == pytest.approx(3.1316065)


def test_ic95_es_simetrico_alrededor_de_la_media():
    low, high = intervalo_confianza([2.0, 4.0, 6.0, 8.0])
    assert (low + high) / 2 == pytest.approx(media([2.0, 4.0, 6.0, 8.0]))


def test_ic95_de_valores_iguales_se_colapsa_a_la_media():
    assert intervalo_confianza([7.0, 7.0, 7.0]) == (7.0, 7.0)


def test_ic95_lista_vacia_levanta_value_error():
    with pytest.raises(ValueError):
        intervalo_confianza([])


# --- coeficiente de variación (s / x̄ · 100) --------------------------------

def test_cv_de_1_2_3_es_50_por_ciento():
    assert coeficiente_variacion([1.0, 2.0, 3.0]) == pytest.approx(50.0)


def test_cv_de_valores_iguales_es_cero():
    assert coeficiente_variacion([9.0, 9.0, 9.0]) == 0.0


def test_cv_lista_vacia_levanta_value_error():
    with pytest.raises(ValueError):
        coeficiente_variacion([])


def test_cv_de_media_cero_levanta_value_error():
    with pytest.raises(ValueError):
        coeficiente_variacion([-1.0, 1.0])


# --- resumen de estabilidad por código de estado ---------------------------

def test_estabilidad_conteo_por_familia():
    res = resumen_estabilidad([200, 201, 200, 404, 500])
    assert res["total"] == 5
    assert res["2xx"] == 3
    assert res["4xx"] == 1
    assert res["5xx"] == 1
    assert res["tasa_5xx"] == pytest.approx(20.0)


def test_estabilidad_sin_errores_da_tasa_cero():
    res = resumen_estabilidad([200] * 100)
    assert res["5xx"] == 0
    assert res["tasa_5xx"] == 0.0


def test_estabilidad_sin_errores_5xx_no_divide_por_cero():
    res = resumen_estabilidad([200, 304, 404])
    assert res["3xx"] == 1
    assert res["tasa_5xx"] == 0.0


def test_estabilidad_lista_vacia_da_totales_en_cero():
    res = resumen_estabilidad([])
    assert res["total"] == 0
    assert res["5xx"] == 0
    assert res["tasa_5xx"] == 0.0
