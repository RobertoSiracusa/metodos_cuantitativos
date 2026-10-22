"""Tests para el Problema 2: Metodo de Lagrange (restriccion de igualdad)."""

import pytest
from src.core.base import ErrorValidacion
from src.core.problema2_lagrange import OptimizadorLagrangeRectangulo


def test_problema2_solucion_oficial():
    opt = OptimizadorLagrangeRectangulo(perimetro=40.0)
    res = opt.resolver()

    assert res.variables_optimas["x"] == pytest.approx(10.0)
    assert res.variables_optimas["y"] == pytest.approx(10.0)
    assert res.valor_optimo == pytest.approx(100.0)
    assert res.multiplicadores["lambda"] == pytest.approx(5.0)
    assert res.tipo_optimo == "maximo"

    # Verificacion de restriccion: 2(10) + 2(10) = 40
    assert opt.evaluar_restriccion(10.0, 10.0) == pytest.approx(40.0)
    assert opt.evaluar_area(10.0, 10.0) == pytest.approx(100.0)


def test_problema2_hessiano_orlado():
    opt = OptimizadorLagrangeRectangulo(perimetro=40.0)
    det_h = opt.determinante_hessiano_orlado()
    assert det_h == 8.0
    assert det_h > 0


def test_problema2_sensibilidad_precio_sombra():
    # Si aumentamos P a 41, dA/dP ~ lambda = 5.
    # Area nueva analitica: (41/4)^2 = 10.25^2 = 105.0625
    # Aproximacion lineal: 100 + 5*(1) = 105.0000
    opt40 = OptimizadorLagrangeRectangulo(perimetro=40.0).resolver()
    opt41 = OptimizadorLagrangeRectangulo(perimetro=41.0).resolver()
    delta_area = opt41.valor_optimo - opt40.valor_optimo
    assert delta_area == pytest.approx(5.0625)
    assert opt40.multiplicadores["lambda"] == pytest.approx(5.0)


def test_problema2_validaciones():
    with pytest.raises(ErrorValidacion):
        OptimizadorLagrangeRectangulo(perimetro=-10.0)

    with pytest.raises(ErrorValidacion):
        OptimizadorLagrangeRectangulo(perimetro=0.0)

    with pytest.raises(ErrorValidacion):
        OptimizadorLagrangeRectangulo(perimetro="invalido")  # type: ignore
