"""Tests para el Problema 4: Multiples restricciones y condiciones KKT."""

import pytest
from scipy.optimize import minimize
from src.core.base import ErrorValidacion
from src.core.problema4_kkt import OptimizadorKKTMultiplesRestricciones


def test_problema4_optimo_no_restringido_y_kkt():
    opt = OptimizadorKKTMultiplesRestricciones()
    x_nr, y_nr, g_nr = opt.optimo_no_restringido()

    assert x_nr == pytest.approx(25.0)
    assert y_nr == pytest.approx(20.0)
    assert (x_nr + y_nr) == pytest.approx(45.0)
    assert (x_nr + y_nr) > 40.0  # Infactible

    res = opt.resolver()
    # x* = 65/3, y* = 55/3, G* = 845/6
    assert res.variables_optimas["x"] == pytest.approx(65.0 / 3.0)
    assert res.variables_optimas["y"] == pytest.approx(55.0 / 3.0)
    assert res.valor_optimo == pytest.approx(845.0 / 6.0)

    # Restriccion activa: x + y = 40
    assert (res.variables_optimas["x"] + res.variables_optimas["y"]) == pytest.approx(40.0)

    # Multiplicador mu1 = 2/3 > 0, mu2 = 0, mu3 = 0
    assert res.multiplicadores["mu_capacidad (mu1)"] == pytest.approx(2.0 / 3.0)
    assert res.multiplicadores["mu_no_neg_x (mu2)"] == pytest.approx(0.0)
    assert res.multiplicadores["mu_no_neg_y (mu3)"] == pytest.approx(0.0)


def test_problema4_comparacion_scipy_slsqp():
    """Valida la solucion analitica KKT frente al optimizador numerico SLSQP de SciPy."""
    opt = OptimizadorKKTMultiplesRestricciones()
    res = opt.resolver()

    # Minimizamos -G(x, y)
    def objetivo(v):
        x, y = v
        return -(5.0 * x + 8.0 * y - 0.1 * (x ** 2) - 0.2 * (y ** 2))

    restricciones = [
        {"type": "ineq", "fun": lambda v: 40.0 - (v[0] + v[1])},  # 40 - (x+y) >= 0
    ]
    cotas = [(0.0, None), (0.0, None)]  # x >= 0, y >= 0

    sol_scipy = minimize(objetivo, [0.0, 0.0], method="SLSQP", bounds=cotas, constraints=restricciones)

    assert sol_scipy.success
    assert sol_scipy.x[0] == pytest.approx(res.variables_optimas["x"], abs=1e-4)
    assert sol_scipy.x[1] == pytest.approx(res.variables_optimas["y"], abs=1e-4)
    assert (-sol_scipy.fun) == pytest.approx(res.valor_optimo, abs=1e-4)


def test_problema4_validaciones():
    with pytest.raises(ErrorValidacion):
        OptimizadorKKTMultiplesRestricciones(coef_x2=0.1)  # debe ser negativo

    with pytest.raises(ErrorValidacion):
        OptimizadorKKTMultiplesRestricciones(capacidad_maxima=-5.0)

    with pytest.raises(ErrorValidacion):
        OptimizadorKKTMultiplesRestricciones(capacidad_maxima=0.0)
