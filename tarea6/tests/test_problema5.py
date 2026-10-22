"""Tests para el Problema 5: Cilindro de volumen fijo y area minima."""

import math
import pytest
from src.core.base import ErrorValidacion
from src.core.problema5_cilindro import OptimizadorCilindroFisico


def test_problema5_cilindro_cerrado():
    opt = OptimizadorCilindroFisico(volumen=500.0, cerrado=True)
    res = opt.resolver()

    r_esp = (250.0 / math.pi) ** (1.0 / 3.0)
    h_esp = 2.0 * r_esp
    area_esp = 2.0 * math.pi * (r_esp ** 2) + 2.0 * math.pi * r_esp * h_esp

    assert res.variables_optimas["radio_r"] == pytest.approx(r_esp)
    assert res.variables_optimas["altura_h"] == pytest.approx(h_esp)
    assert res.variables_optimas["altura_h"] == pytest.approx(2.0 * res.variables_optimas["radio_r"])
    assert res.valor_optimo == pytest.approx(area_esp)
    assert res.valor_optimo == pytest.approx(348.7342, abs=1e-3)

    # Volumen verificado
    vol = opt.evaluar_volumen(res.variables_optimas["radio_r"], res.variables_optimas["altura_h"])
    assert vol == pytest.approx(500.0)

    # Segunda derivada positiva
    d1, d2 = opt.derivadas_unidimensionales(r_esp)
    assert d1 == pytest.approx(0.0, abs=1e-6)
    assert d2 == pytest.approx(12.0 * math.pi)
    assert d2 > 0


def test_problema5_cilindro_abierto():
    opt = OptimizadorCilindroFisico(volumen=500.0, cerrado=False)
    res = opt.resolver()

    r_esp = (500.0 / math.pi) ** (1.0 / 3.0)
    assert res.variables_optimas["radio_r"] == pytest.approx(r_esp)
    assert res.variables_optimas["altura_h"] == pytest.approx(r_esp)  # h = r
    assert res.valor_optimo == pytest.approx(3.0 * math.pi * (r_esp ** 2))

    vol = opt.evaluar_volumen(res.variables_optimas["radio_r"], res.variables_optimas["altura_h"])
    assert vol == pytest.approx(500.0)


def test_problema5_validaciones():
    with pytest.raises(ErrorValidacion):
        OptimizadorCilindroFisico(volumen=-100.0)

    with pytest.raises(ErrorValidacion):
        OptimizadorCilindroFisico(volumen=0.0)

    with pytest.raises(ErrorValidacion):
        OptimizadorCilindroFisico(volumen=500.0, cerrado="no")  # type: ignore
