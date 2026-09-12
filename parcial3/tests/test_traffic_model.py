"""
Pruebas del generador de trafico: Normal(3, 1) truncada a [1, 5] Gbps.

Lo critico es el truncamiento ESTRICTO: una sola muestra fuera de rango
rompe el contrato del modelo termico, porque llevaria la temperatura fuera de
los equilibrios declarados en el enunciado.
"""

import pytest

from src.core.traffic_model import GeneradorTrafico
from src.simulation.continuous_sim import ClusterSimulation
from src.utils.config import (
    TRAFICO_DESV_GBPS,
    TRAFICO_MAX_GBPS,
    TRAFICO_MEDIA_GBPS,
    TRAFICO_MIN_GBPS,
)
from src.utils.validators import ValidacionError

N_MUESTRAS = 50_000


@pytest.fixture(scope="module")
def muestras():
    """Muestra grande con semilla fija para las pruebas estadisticas."""
    gen = GeneradorTrafico(semilla=2026)
    return gen.muestrear_serie(N_MUESTRAS), gen


def test_truncamiento_estricto(muestras):
    """Ninguna muestra puede caer fuera de [1, 5] Gbps."""
    valores, _ = muestras
    fuera = [v for v in valores if not (TRAFICO_MIN_GBPS <= v <= TRAFICO_MAX_GBPS)]
    assert not fuera, f"{len(fuera)} muestras fuera de rango, por ejemplo {fuera[:5]}"


def test_media_muestral_cercana_a_la_nominal(muestras):
    valores, _ = muestras
    media = sum(valores) / len(valores)
    assert media == pytest.approx(TRAFICO_MEDIA_GBPS, abs=0.03)


def test_desviacion_muestral_razonable(muestras):
    """
    Truncar a +/- 2 sigma recorta las colas, asi que la desviacion observada es
    algo menor que la nominal de 1.0. Debe quedar entre 0.85 y 1.0.
    """
    from statistics import pstdev

    valores, _ = muestras
    desv = pstdev(valores)
    assert 0.85 < desv < TRAFICO_DESV_GBPS + 1e-9


def test_la_distribucion_es_simetrica(muestras):
    """Con limites simetricos respecto de la media, la mediana debe caer en 3."""
    from statistics import median

    valores, _ = muestras
    assert median(valores) == pytest.approx(TRAFICO_MEDIA_GBPS, abs=0.05)


def test_tasa_de_rechazo_es_la_esperada(muestras):
    """Con limites en +/- 2 sigma se rechaza alrededor del 4.6% de los sorteos."""
    _, gen = muestras
    assert 0.02 < gen.tasa_rechazo < 0.08


def test_cuenta_de_muestras(muestras):
    valores, gen = muestras
    assert len(valores) == N_MUESTRAS
    assert gen.muestras_generadas == N_MUESTRAS


def test_reproducibilidad_con_semilla_fija():
    a = GeneradorTrafico(semilla=42).muestrear_serie(500)
    b = GeneradorTrafico(semilla=42).muestrear_serie(500)
    assert a == b


def test_semillas_distintas_dan_series_distintas():
    a = GeneradorTrafico(semilla=1).muestrear_serie(200)
    b = GeneradorTrafico(semilla=2).muestrear_serie(200)
    assert a != b


def test_rango_estrecho_sigue_respetando_los_limites():
    """Caso borde: un rango angosto no debe colgar ni devolver valores fuera."""
    gen = GeneradorTrafico(media=3.0, desviacion=1.0, minimo=2.9, maximo=3.1, semilla=5)
    valores = gen.muestrear_serie(1000)
    assert all(2.9 <= v <= 3.1 for v in valores)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"desviacion": 0.0},
        {"desviacion": -1.0},
        {"minimo": 5.0, "maximo": 1.0},
        {"minimo": -1.0, "maximo": 5.0},
        {"media": 10.0},
    ],
    ids=["desv_cero", "desv_negativa", "rango_invertido", "minimo_negativo", "media_fuera"],
)
def test_parametros_invalidos_se_rechazan(kwargs):
    with pytest.raises(ValidacionError):
        GeneradorTrafico(**kwargs)


def test_cantidad_negativa_de_muestras_se_rechaza():
    with pytest.raises(ValidacionError):
        GeneradorTrafico(semilla=1).muestrear_serie(-1)


def test_el_motor_continuo_nunca_usa_trafico_fuera_de_rango():
    """El truncamiento debe sostenerse tambien dentro de la simulacion completa."""
    sim = ClusterSimulation(semilla=2026)
    sim.ejecutar(8.0)
    columna_trafico = [float(fila[1]) for fila in sim.tracer.filas]
    assert columna_trafico, "la traza quedo vacia"
    assert all(TRAFICO_MIN_GBPS <= t <= TRAFICO_MAX_GBPS for t in columna_trafico)
