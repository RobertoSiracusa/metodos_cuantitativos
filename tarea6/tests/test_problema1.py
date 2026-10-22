"""Tests para el Problema 1: Minimizacion sin restricciones."""

import pytest
from src.core.base import ErrorValidacion
from src.core.problema1_sin_restricciones import OptimizadorSinRestricciones


def test_problema1_solucion_oficial():
    opt = OptimizadorSinRestricciones()
    res = opt.resolver()

    assert res.variables_optimas["x"] == pytest.approx(2.0)
    assert res.variables_optimas["y"] == pytest.approx(3.0)
    assert res.valor_optimo == pytest.approx(7.0)
    assert res.tipo_optimo == "minimo"
    assert res.convergencia is True

    # Evaluacion manual: 2^2 + 3^2 - 4(2) - 6(3) + 20 = 4 + 9 - 8 - 18 + 20 = 7
    assert opt.evaluar_costo(2.0, 3.0) == pytest.approx(7.0)


def test_problema1_gradiente_y_hessiano():
    opt = OptimizadorSinRestricciones()
    gx, gy = opt.gradiente(2.0, 3.0)
    assert gx == pytest.approx(0.0)
    assert gy == pytest.approx(0.0)

    # Fuera del optimo
    gx_orig, gy_orig = opt.gradiente(0.0, 0.0)
    assert gx_orig == pytest.approx(-4.0)
    assert gy_orig == pytest.approx(-6.0)

    # Hessiano
    h = opt.matriz_hessiana()
    assert h == ((2.0, 0.0), (0.0, 2.0))
    res = opt.resolver()
    assert res.detalles["d1_hessiano"] > 0
    assert res.detalles["det_hessiano"] > 0
    assert "minimo global estricto" in res.detalles["clasificacion_punto"]


def test_problema1_validaciones():
    with pytest.raises(ErrorValidacion):
        OptimizadorSinRestricciones(a=0.0)

    with pytest.raises(ErrorValidacion):
        OptimizadorSinRestricciones(b=0.0)

    with pytest.raises(ErrorValidacion):
        OptimizadorSinRestricciones(a="texto")  # type: ignore

    with pytest.raises(ErrorValidacion):
        OptimizadorSinRestricciones(a=True)  # booleano no permitido
