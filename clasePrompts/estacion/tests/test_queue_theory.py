"""Pruebas unitarias para las formulas analiticas de teoria de colas M/M/c."""

import pytest
from src.models.queue_model import MMCAnalytical


def test_mmc_stability_condition():
    """Verifica la deteccion de estabilidad estocastica segun rho < 1."""
    # Sistema estable: lambda = 4, mu = 2, c = 3 -> rho = 4 / 6 = 0.667 < 1
    model_stable = MMCAnalytical(lamb=4.0, mu=2.0, c=3)
    assert model_stable.is_stable is True
    assert round(model_stable.rho, 4) == round(4.0 / 6.0, 4)

    # Sistema inestable: lambda = 8, mu = 2, c = 3 -> rho = 8 / 6 = 1.333 >= 1
    model_unstable = MMCAnalytical(lamb=8.0, mu=2.0, c=3)
    assert model_unstable.is_stable is False
    assert model_unstable.lq == float('inf')
    assert model_unstable.wq == float('inf')


def test_mmc_known_values():
    """
    Verifica los valores contra un caso teorico estandar de literatura:
    lambda = 2 clientes/hora, mu = 1 cliente/hora, c = 3 servidores.
    a = 2 / 1 = 2 Erlangs.
    rho = 2 / (3 * 1) = 2/3 = 0.6667.
    """
    model = MMCAnalytical(lamb=2.0, mu=1.0, c=3)

    assert round(model.rho, 4) == round(2.0 / 3.0, 4)
    assert model.a == 2.0

    # P0 teorico para c=3, a=2, rho=2/3:
    # suma n=0..2 de a^n/n! = 1 + 2 + 4/2 = 5
    # cola = (8/6) * (1 / (1 - 2/3)) = (4/3) * 3 = 4
    # P0 = 1 / (5 + 4) = 1/9 = 0.1111
    assert round(model.p0, 4) == round(1.0 / 9.0, 4)

    # Lq = P0 * a^c * rho / (c! * (1-rho)^2) = (1/9) * 8 * (2/3) / (6 * (1/9))
    # = (16/27) / (6/9) = (16/27) / (2/3) = (16/27) * (3/2) = 8/9 = 0.8889
    assert round(model.lq, 4) == round(8.0 / 9.0, 4)

    # Wq = Lq / lambda = (8/9) / 2 = 4/9 = 0.4444
    assert round(model.wq, 4) == round(4.0 / 9.0, 4)

    # W = Wq + 1/mu = 4/9 + 1 = 13/9 = 1.4444
    assert round(model.w, 4) == round(13.0 / 9.0, 4)

    # L = Lq + a = 8/9 + 2 = 26/9 = 2.8889
    assert round(model.l, 4) == round(26.0 / 9.0, 4)


def test_mmc_summary_dictionary():
    """Comprueba que el resumen estructurado devuelva todas las claves requeridas."""
    model = MMCAnalytical(lamb=3.0, mu=2.0, c=2)
    res = model.get_summary()

    expected_keys = {"lambda", "mu", "c", "rho", "is_stable", "P0", "Lq", "L", "Wq", "W", "Pw"}
    assert expected_keys.issubset(res.keys())
    assert res["is_stable"] is True
