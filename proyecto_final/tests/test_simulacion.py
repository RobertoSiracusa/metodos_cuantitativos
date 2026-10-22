"""Tests del motor SimPy (R6): reproducibilidad, integracion de M1/M2 y metricas."""

import math

import pytest

from src.simulation.metricas import MetricasColas
from src.simulation.motor_simpy import MotorSimulacion
from src.utils.config import Configuracion
from src.utils.validators import ErrorValidacion


def _correr(semilla=7, hasta=120.0, **parametros):
    configuracion = Configuracion.por_defecto()
    if parametros:
        datos = configuracion.datos
        datos["parametros"]["simulacion"].update(parametros)
        configuracion = Configuracion(datos)
    motor = MotorSimulacion(configuracion, semilla=semilla)
    motor.avanzar(hasta)
    return motor


def test_misma_semilla_misma_corrida():
    a = _correr(semilla=3).estado()
    b = _correr(semilla=3).estado()
    assert a.metricas == b.metricas
    assert a.eventos == b.eventos


def test_conservacion_de_paquetes():
    estado = _correr().estado()
    m = estado.metricas
    # cada paquete generado esta completado, perdido, en un servidor o todavia en transito
    assert m["generados"] == m["completados"] + m["perdidos"] + m["en_sistema"] + len(estado.en_transito)


def test_servidores_nunca_exceden_su_capacidad():
    motor = _correr(hasta=1)
    for t in range(2, 150):
        motor.avanzar(t)
        assert all(0 <= c <= 100 for c in motor.estado().carga_servidores.values())


def test_lagrange_reparte_toda_la_energia_en_cada_tick():
    estado = _correr().estado()
    e_max = Configuracion.por_defecto().construir_lagrange().e_max
    assert sum(estado.energia_clusteres.values()) == pytest.approx(e_max)
    assert len(estado.series_lagrange["tiempo"]) == len(estado.series_gradiente["tiempo"]) > 100


def test_observador_recibe_fallas_y_cambios_de_ruta():
    configuracion = Configuracion.por_defecto()
    motor = MotorSimulacion(configuracion, semilla=11)
    recibidos = []
    motor.suscribir(recibidos.append)
    motor.avanzar(300)
    tipos = {e.tipo for e in recibidos}
    assert {"falla", "reparacion", "cambio_ruta"} <= tipos


def test_estado_es_una_copia():
    motor = _correr()
    estado = motor.estado()
    estado.colas.clear()
    assert motor.estado().colas


def test_parametro_desconocido_es_error():
    with pytest.raises(ErrorValidacion):
        _correr(velocidad_luz=3)


def test_parametro_fuera_de_rango_es_error():
    with pytest.raises(ErrorValidacion):
        _correr(tasa_llegada=0)


def test_mm1_formulas_a_mano():
    # lambda = 1, mu = 2 -> rho = 0.5, Lq = 0.25/0.5 = 0.5, Wq = 0.5/1 = 0.5, W = 1
    r = MetricasColas.comparar_mm1(1, 2)
    assert r == pytest.approx({"rho": 0.5, "Lq": 0.5, "Wq": 0.5, "W": 1.0})
    assert math.isinf(MetricasColas.comparar_mm1(3, 2)["Wq"])
