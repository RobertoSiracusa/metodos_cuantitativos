"""Tests del modulo 2 (R3, R4, R5): derivadas, convergencia del gradiente y reparto de Lagrange."""

import math

import pytest

from src.core.no_lineal.base import EntradaOptimizacion, Optimizador
from src.core.no_lineal.gradiente_enfriamiento import GradienteEnfriamiento
from src.core.no_lineal.lagrange_energia import AsignadorLagrange
from src.core.no_lineal.modelo_termico import ModeloTermico
from src.utils.validators import ErrorValidacion


# --- R3: modelo termico -------------------------------------------------------


def test_termico_puntos_estacionarios_calculados_a_mano():
    # T'(c) = 0.0006 (c - 30)(c - 70)
    puntos = ModeloTermico().puntos_estacionarios()
    assert [(round(p.carga, 6), p.tipo) for p in puntos] == [(30.0, "maximo"), (70.0, "minimo")]
    # T(30) = 0.0002*27000 - 0.03*900 + 1.26*30 + 30 = 5.4 - 27 + 37.8 + 30 = 46.2
    assert puntos[0].temperatura == pytest.approx(46.2)
    # T(70) = 68.6 - 147 + 88.2 + 30 = 39.8
    assert puntos[1].temperatura == pytest.approx(39.8)


def test_termico_derivadas_en_puntos_conocidos():
    modelo = ModeloTermico()
    assert modelo.derivada(30) == pytest.approx(0)
    assert modelo.derivada(70) == pytest.approx(0)
    assert modelo.segunda_derivada(50) == pytest.approx(0)
    # derivada analitica contra diferencia finita central
    h = 1e-5
    assert modelo.derivada(12.3) == pytest.approx((modelo.temperatura(12.3 + h) - modelo.temperatura(12.3 - h)) / (2 * h))


def test_termico_inflexion_y_punto_critico():
    modelo = ModeloTermico()
    assert modelo.punto_inflexion() == pytest.approx(50)
    umbral = modelo.carga_umbral()
    assert 70 < umbral < 100
    assert modelo.temperatura(umbral) >= modelo.t_max
    # D3: el critico es el menor entre inflexion (50) y umbral (> 70)
    assert modelo.punto_critico() == pytest.approx(50)


def test_termico_umbral_bajo_gana_a_la_inflexion():
    modelo = ModeloTermico(t_max=40)
    assert modelo.punto_critico() == pytest.approx(modelo.carga_umbral())
    assert modelo.punto_critico() < 50


def test_termico_rechaza_coeficiente_cubico_nulo():
    with pytest.raises(ErrorValidacion):
        ModeloTermico(a=0)


# --- R4: gradiente ------------------------------------------------------------


def test_gradiente_optimo_analitico():
    # v* = (0.05 * 60 / 3)^(1/4) = 1
    assert GradienteEnfriamiento().optimo_analitico(60) == pytest.approx(1.0)


def test_gradiente_converge_al_optimo():
    opt = GradienteEnfriamiento(v_inicial=1.8)
    for t in range(200):
        opt.actualizar(EntradaOptimizacion(t, carga=60))
    assert opt.velocidad_actual == pytest.approx(1.0, abs=1e-4)
    energias = opt.series_para_grafico()["energia"]
    assert energias[-1] <= energias[0]


def test_gradiente_respeta_cotas():
    opt = GradienteEnfriamiento(v_inicial=0.1, alfa=10)
    for t in range(20):
        opt.actualizar(EntradaOptimizacion(t, carga=100))
        assert 0.1 <= opt.velocidad_actual <= 2.0


def test_gradiente_valida_parametros():
    with pytest.raises(ErrorValidacion):
        GradienteEnfriamiento(v_min=2, v_max=1)
    with pytest.raises(ErrorValidacion):
        GradienteEnfriamiento().actualizar(EntradaOptimizacion(0, carga=-5))


# --- R5: Lagrange -------------------------------------------------------------


def test_lagrange_caso_interior_a_mano():
    # lambda = (3 + 1) / (6 + 2) = 0.5;  E1 = 3/0.5 - 1 = 5;  E2 = 1/0.5 - 1 = 1
    r = AsignadorLagrange.resolver({"C1": 3, "C2": 1}, 6)
    assert r.lambda_ == pytest.approx(0.5)
    assert r.asignacion == pytest.approx({"C1": 5, "C2": 1})
    assert r.rendimiento == pytest.approx(3 * math.log(6) + math.log(2))


def test_lagrange_kkt_fija_en_cero_al_cluster_chico():
    # sin KKT: lambda = 3.2/4 = 0.8 y E2 = 0.2/0.8 - 1 < 0 -> se fija E2 = 0, lambda = 3/3 = 1
    r = AsignadorLagrange.resolver({"C1": 3, "C2": 0.2}, 2)
    assert r.asignacion == pytest.approx({"C1": 2, "C2": 0})
    assert r.lambda_ == pytest.approx(1)


def test_lagrange_suma_igual_a_e_max():
    r = AsignadorLagrange.resolver({"C1": 7, "C2": 2, "C3": 0.5, "C4": 0}, 20)
    assert sum(r.asignacion.values()) == pytest.approx(20)
    assert all(e >= 0 for e in r.asignacion.values())


def test_lagrange_sin_demanda_reparte_igual():
    r = AsignadorLagrange.resolver({"C1": 0, "C2": 0}, 10)
    assert r.asignacion == {"C1": 5, "C2": 5}


def test_lagrange_valida_entrada():
    with pytest.raises(ErrorValidacion):
        AsignadorLagrange.resolver({}, 10)
    with pytest.raises(ErrorValidacion):
        AsignadorLagrange.resolver({"C1": -1}, 10)


# --- Polimorfismo -------------------------------------------------------------


def test_optimizadores_se_usan_por_la_interfaz_comun():
    optimizadores: list[Optimizador] = [GradienteEnfriamiento(), AsignadorLagrange(e_max=10)]
    entrada = EntradaOptimizacion(0.0, carga=50, demandas={"C1": 2, "C2": 2})
    for opt in optimizadores:
        resultado = opt.actualizar(entrada)
        assert resultado.tiempo == 0.0
        assert len(opt.historial) == 1
    assert optimizadores[1].historial[0].valores["E_C1"] == pytest.approx(5)
