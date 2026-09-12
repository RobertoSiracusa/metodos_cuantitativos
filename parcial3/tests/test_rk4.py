"""
Pruebas del integrador Runge-Kutta de cuarto orden.

El contraste es contra la solucion cerrada de la EDO lineal con forzante constante:

    T(t) = T_eq + (T0 - T_eq) * exp(-t / tau)

Con paso de 1 s y tau de 120 s el error de RK4 debe quedar por debajo de 1e-9 C,
varios ordenes de magnitud mejor que cualquier tolerancia fisica relevante.
"""

import math

import pytest

from src.core.thermal_model import ModeloTermico
from src.utils.validators import ValidacionError


@pytest.fixture
def modelo():
    return ModeloTermico()


# ----------------------------------------------------------------------
# Exactitud contra la solucion analitica
# ----------------------------------------------------------------------

@pytest.mark.parametrize("trafico", [1.0, 2.0, 3.0, 4.0, 5.0])
@pytest.mark.parametrize("temp_inicial", [25.0, 52.0, 70.0, 88.0, 110.0])
@pytest.mark.parametrize("horizonte", [1.0, 60.0, 300.0, 1800.0, 7200.0])
def test_rk4_contra_solucion_analitica(modelo, trafico, temp_inicial, horizonte):
    numerica = modelo.integrar(temp_inicial, trafico, duracion_s=horizonte, dt_s=1.0)
    exacta = modelo.solucion_analitica(temp_inicial, trafico, horizonte)
    assert numerica == pytest.approx(exacta, abs=1e-9)


def test_un_solo_paso_coincide_con_la_analitica(modelo):
    """
    Error local de RK4 con dt = 1 s y tau = 120 s: del orden de
    |T0 - T_eq| * (dt/tau)^5 / 120, o sea ~1e-11 C. La tolerancia de 1e-9
    lo cubre con margen sin volverse trivial.
    """
    numerica = modelo.paso_rk4(25.0, 3.0, 1.0)
    exacta = modelo.solucion_analitica(25.0, 3.0, 1.0)
    assert numerica == pytest.approx(exacta, abs=1e-9)


def test_la_solucion_analitica_es_coherente(modelo):
    """En t = 0 vale T0, y en el infinito tiende a T_eq."""
    assert modelo.solucion_analitica(25.0, 3.0, 0.0) == pytest.approx(25.0, abs=1e-12)
    assert modelo.solucion_analitica(25.0, 3.0, 100000.0) == pytest.approx(70.0, abs=1e-9)


def test_en_una_constante_de_tiempo_recorre_el_63_por_ciento(modelo):
    """Propiedad del sistema de primer orden: a t = tau queda 1/e del error."""
    t0, trafico = 25.0, 3.0
    t_eq = modelo.temperatura_equilibrio(trafico)
    final = modelo.integrar(t0, trafico, duracion_s=modelo.tau_s, dt_s=1.0)
    esperado = t_eq + (t0 - t_eq) * math.exp(-1.0)
    assert final == pytest.approx(esperado, abs=1e-9)


def test_arrancar_en_el_equilibrio_no_mueve_la_temperatura(modelo):
    for trafico in (1.0, 3.0, 5.0):
        t_eq = modelo.temperatura_equilibrio(trafico)
        assert modelo.integrar(t_eq, trafico, 3600.0, 1.0) == pytest.approx(t_eq, abs=1e-9)


# ----------------------------------------------------------------------
# Orden de convergencia
# ----------------------------------------------------------------------

def test_rk4_es_mas_exacto_que_euler_explicito(modelo):
    """
    Un paso grande donde el error si es medible: con dt = 60 s (medio tau) RK4
    queda unas 400 veces mas cerca de la solucion exacta que Euler explicito.
    Confirma que el integrador no es Euler disfrazado.
    """
    t0, trafico, dt = 25.0, 3.0, 60.0
    exacta = modelo.solucion_analitica(t0, trafico, dt)

    rk4 = modelo.paso_rk4(t0, trafico, dt)
    euler = t0 + dt * modelo.derivada(t0, trafico)

    error_rk4 = abs(rk4 - exacta)
    error_euler = abs(euler - exacta)
    assert error_rk4 < error_euler / 100.0, (error_rk4, error_euler)


def test_el_error_cae_con_el_paso(modelo):
    """Reducir el paso no debe empeorar el resultado."""
    t0, trafico, horizonte = 25.0, 5.0, 300.0
    exacta = modelo.solucion_analitica(t0, trafico, horizonte)
    error_grueso = abs(modelo.integrar(t0, trafico, horizonte, dt_s=10.0) - exacta)
    error_fino = abs(modelo.integrar(t0, trafico, horizonte, dt_s=1.0) - exacta)
    assert error_fino <= error_grueso + 1e-12


# ----------------------------------------------------------------------
# Validacion
# ----------------------------------------------------------------------

@pytest.mark.parametrize("paso", [0.0, -1.0])
def test_paso_no_positivo_se_rechaza(modelo, paso):
    with pytest.raises(ValidacionError):
        modelo.paso_rk4(25.0, 3.0, paso)


def test_tiempo_negativo_se_rechaza(modelo):
    with pytest.raises(ValidacionError):
        modelo.solucion_analitica(25.0, 3.0, -1.0)
    with pytest.raises(ValidacionError):
        modelo.integrar(25.0, 3.0, -10.0)
