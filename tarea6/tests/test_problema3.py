"""Tests para el Problema 3: Metodo del Gradiente (busqueda iterativa)."""

import pytest
from src.core.base import ErrorValidacion
from src.core.problema3_gradiente import OptimizadorGradienteAscenso


def test_problema3_gradiente_y_optimo_analitico():
    opt = OptimizadorGradienteAscenso(x0=0.0, y0=0.0)
    # En (0, 0): grad(f) = (-2(0) + 4, -2(0) + 6) = (4, 6)
    gx, gy = opt.gradiente(0.0, 0.0)
    assert gx == pytest.approx(4.0)
    assert gy == pytest.approx(6.0)

    # Optimo teorico: grad(f) = (0, 0) => x=2, y=3, f=13
    x_teo, y_teo, f_teo = opt.optimo_analitico()
    assert x_teo == pytest.approx(2.0)
    assert y_teo == pytest.approx(3.0)
    assert f_teo == pytest.approx(13.0)
    assert opt.evaluar_funcion(2.0, 3.0) == pytest.approx(13.0)


def test_problema3_paso_optimo_un_paso():
    # Con alfa* = 0.5 debe alcanzar el optimo en la primera iteracion
    opt = OptimizadorGradienteAscenso(x0=0.0, y0=0.0, tasa_aprendizaje=0.5, max_iteraciones=5)
    res, hist = opt.resolver_iterativo()

    assert hist[1].x == pytest.approx(2.0)
    assert hist[1].y == pytest.approx(3.0)
    assert hist[1].f_val == pytest.approx(13.0)
    assert res.variables_optimas["x"] == pytest.approx(2.0)
    assert res.variables_optimas["y"] == pytest.approx(3.0)
    assert res.valor_optimo == pytest.approx(13.0)


def test_problema3_convergencia_iterativa_alfa_01():
    opt = OptimizadorGradienteAscenso(x0=0.0, y0=0.0, tasa_aprendizaje=0.1, max_iteraciones=50)
    res, hist = opt.resolver_iterativo()

    assert len(hist) > 10
    # La funcion objetivo debe ser monotona creciente en cada paso
    for i in range(len(hist) - 1):
        assert hist[i + 1].f_val >= hist[i].f_val

    # Al cabo de 50 pasos, debe aproximar (2, 3) con alta precision
    assert res.variables_optimas["x"] == pytest.approx(2.0, abs=1e-3)
    assert res.variables_optimas["y"] == pytest.approx(3.0, abs=1e-3)
    assert res.valor_optimo == pytest.approx(13.0, abs=1e-3)
    assert res.tipo_optimo == "maximo"


def test_problema3_validaciones():
    with pytest.raises(ErrorValidacion):
        OptimizadorGradienteAscenso(tasa_aprendizaje=-0.1)

    with pytest.raises(ErrorValidacion):
        OptimizadorGradienteAscenso(max_iteraciones=0)

    with pytest.raises(ErrorValidacion):
        OptimizadorGradienteAscenso(tolerancia=-1e-5)
