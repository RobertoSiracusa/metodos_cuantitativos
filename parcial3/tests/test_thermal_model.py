"""
Pruebas del modelo termico y de la curva de eficiencia con thermal throttling.

Los tres equilibrios del enunciado (1 -> 52 C, 3 -> 70 C, 5 -> 88 C) son el
contrato de calibracion: si alguna constante cambia, estos tests se ponen rojos.
"""

import pytest

from src.core.thermal_model import (
    ModeloTermico,
    eficiencia_termica,
    gb_a_tb,
    hay_throttling,
    throughput_gbps,
)
from src.simulation.continuous_sim import ClusterSimulation
from src.utils.config import TEMP_DISENO_C


@pytest.fixture
def modelo():
    """Modelo con la calibracion oficial del enunciado."""
    return ModeloTermico()


# ----------------------------------------------------------------------
# Equilibrio termico
# ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "trafico,esperado",
    [(1.0, 52.0), (3.0, 70.0), (5.0, 88.0)],
    ids=["1Gbps", "3Gbps", "5Gbps"],
)
def test_temperatura_de_equilibrio(modelo, trafico, esperado):
    assert modelo.temperatura_equilibrio(trafico) == pytest.approx(esperado, abs=1e-9)


def test_el_trafico_medio_cae_en_la_temperatura_de_diseno(modelo):
    """La calibracion esta hecha para que 3 Gbps de por resultado 70 C exactos."""
    assert modelo.temperatura_equilibrio(3.0) == pytest.approx(TEMP_DISENO_C, abs=1e-9)


def test_constante_de_tiempo(modelo):
    assert modelo.tau_s == pytest.approx(120.0, abs=1e-9)


def test_la_derivada_se_anula_en_el_equilibrio(modelo):
    for trafico in (1.0, 2.0, 3.0, 4.0, 5.0):
        t_eq = modelo.temperatura_equilibrio(trafico)
        assert modelo.derivada(t_eq, trafico) == pytest.approx(0.0, abs=1e-12)


def test_signo_de_la_derivada(modelo):
    """Por debajo del equilibrio calienta, por encima enfria."""
    assert modelo.derivada(50.0, 3.0) > 0
    assert modelo.derivada(90.0, 3.0) < 0


@pytest.mark.parametrize("trafico,esperado", [(1.0, 52.0), (3.0, 70.0), (5.0, 88.0)])
def test_con_trafico_constante_converge_al_equilibrio(modelo, trafico, esperado):
    """Tras 3600 s (30 tau) la temperatura debe estar pegada al equilibrio."""
    final = modelo.integrar(25.0, trafico, duracion_s=3600.0, dt_s=1.0)
    assert final == pytest.approx(esperado, abs=1e-6)


def test_el_motor_completo_converge_con_trafico_constante():
    """
    Con la distribucion de trafico degenerada en 3 Gbps el cluster debe quedar
    clavado en 70.0 C: es el punto de diseno.
    """
    sim = ClusterSimulation(
        temp_inicial_c=25.0,
        trafico_media=3.0,
        trafico_desv=1e-9,
        trafico_min=2.999999,
        trafico_max=3.000001,
        semilla=1,
    )
    sim.ejecutar(2.0)
    assert sim.temperatura_actual == pytest.approx(70.0, abs=1e-4)


# ----------------------------------------------------------------------
# Eficiencia con throttling
# ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "temp,esperado",
    [
        (25.0, 0.90),
        (69.9, 0.90),
        (70.0, 0.90),
        (75.0, 0.80),
        (80.0, 0.70),
        (88.0, 0.54),
        (100.0, 0.30),
        (500.0, 0.30),
    ],
    ids=["ambiente", "casi70", "diseno", "75C", "80C", "88C", "piso", "extremo"],
)
def test_curva_de_eficiencia(temp, esperado):
    assert eficiencia_termica(temp) == pytest.approx(esperado, abs=1e-12)


def test_eficiencia_es_continua_en_el_umbral():
    assert eficiencia_termica(70.0) == pytest.approx(eficiencia_termica(70.0 + 1e-12), abs=1e-12)


def test_eficiencia_monotona_decreciente_y_acotada():
    """eta nunca crece y nunca baja de 0.30."""
    anterior = 1.0
    temp = 0.0
    while temp <= 300.0:
        actual = eficiencia_termica(temp)
        assert actual <= anterior + 1e-12, f"eta crecio en T = {temp}"
        assert 0.30 <= actual <= 0.90
        anterior = actual
        temp += 0.5


def test_eficiencia_estrictamente_decreciente_sobre_70():
    """Entre 70 y 100 C cada grado cuesta exactamente 2 puntos de eficiencia."""
    for temp in (71.0, 75.0, 80.0, 85.0):
        assert eficiencia_termica(temp) - eficiencia_termica(temp + 1.0) == pytest.approx(
            0.02, abs=1e-12
        )


def test_deteccion_de_throttling():
    assert not hay_throttling(69.9)
    assert not hay_throttling(70.0)
    assert hay_throttling(70.0001)
    assert hay_throttling(88.0)


# ----------------------------------------------------------------------
# Rendimiento y conversion de unidades
# ----------------------------------------------------------------------

def test_throughput_aplica_la_eficiencia():
    assert throughput_gbps(3.0, 70.0) == pytest.approx(2.7, abs=1e-12)
    assert throughput_gbps(5.0, 88.0) == pytest.approx(5.0 * 0.54, abs=1e-12)


def test_throughput_nunca_supera_al_trafico():
    for trafico in (1.0, 3.0, 5.0):
        for temp in (25.0, 70.0, 88.0, 120.0):
            assert throughput_gbps(trafico, temp) <= trafico


def test_conversion_de_unidades():
    """Gb / 8 -> GB, GB / 1000 -> TB."""
    assert gb_a_tb(8000.0) == pytest.approx(1.0, abs=1e-12)
    assert gb_a_tb(0.0) == 0.0
    assert gb_a_tb(80000.0) == pytest.approx(10.0, abs=1e-12)


# ----------------------------------------------------------------------
# Validacion de parametros
# ----------------------------------------------------------------------

def test_parametros_fisicos_invalidos_se_rechazan():
    from src.utils.validators import ValidacionError

    with pytest.raises(ValidacionError):
        ModeloTermico(h_disip=0.0)
    with pytest.raises(ValidacionError):
        ModeloTermico(c_termica=-1.0)
