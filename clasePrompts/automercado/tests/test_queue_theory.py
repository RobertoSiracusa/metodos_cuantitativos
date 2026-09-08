"""Pruebas unitarias para las formulas analiticas de teoria de colas M/M/c y c x M/M/1."""

import pytest
from src.models.queue_model import MMCAnalytical, ParallelMM1Analytical


def test_mmc_stability_condition():
    """Verifica deteccion de estabilidad estocastica segun rho < 1 en M/M/c."""
    # Estable: lambda = 4, mu = 2, c = 3 -> rho = 4 / 6 = 0.667 < 1
    model_stable = MMCAnalytical(lamb=4.0, mu=2.0, c=3)
    assert model_stable.is_stable is True
    assert round(model_stable.rho, 4) == round(4.0 / 6.0, 4)

    # Inestable: lambda = 8, mu = 2, c = 3 -> rho = 8 / 6 = 1.333 >= 1
    model_unstable = MMCAnalytical(lamb=8.0, mu=2.0, c=3)
    assert model_unstable.is_stable is False
    assert model_unstable.lq == float("inf")
    assert model_unstable.wq == float("inf")


def test_mmc_known_literature_values():
    """
    Verifica valores exactos contra caso estandar de literatura (Taha / Hillier):
    lambda = 2 clientes/h, mu = 1 cliente/h, c = 3 servidores.
    rho = 2 / 3 = 0.6667.
    """
    model = MMCAnalytical(lamb=2.0, mu=1.0, c=3)

    assert round(model.rho, 4) == round(2.0 / 3.0, 4)
    assert model.a == 2.0

    # P0 = 1/9 = 0.1111
    assert round(model.p0, 4) == round(1.0 / 9.0, 4)

    # Lq = 8/9 = 0.8889
    assert round(model.lq, 4) == round(8.0 / 9.0, 4)

    # Wq = (8/9) / 2 = 4/9 = 0.4444
    assert round(model.wq, 4) == round(4.0 / 9.0, 4)

    # W = 4/9 + 1 = 13/9 = 1.4444
    assert round(model.w, 4) == round(13.0 / 9.0, 4)


def test_parallel_mm1_comparison():
    """
    Verifica el modelo de colas paralelas c x M/M/1 y contrasta cuantitativamente
    que la cola unica M/M/c siempre produce menor tiempo de espera que colas independientes.
    """
    lamb = 2.0
    mu = 1.0
    c = 3

    mmc = MMCAnalytical(lamb, mu, c)
    parallel = ParallelMM1Analytical(lamb, mu, c)

    assert parallel.is_stable is True
    assert round(parallel.rho, 4) == round(2.0 / 3.0, 4)
    assert round(parallel.lambda_per_queue, 4) == round(2.0 / 3.0, 4)

    # Para M/M/1 con rho = 2/3:
    # Lq_single = (4/9) / (1/3) = 4/3 = 1.3333
    assert round(parallel.lq_single, 4) == round(4.0 / 3.0, 4)

    # Lq_total = 3 * (4/3) = 4.0
    assert round(parallel.lq, 4) == 4.0

    # Wq = Lq_total / lambda = 4.0 / 2.0 = 2.0
    assert round(parallel.wq, 4) == 2.0

    # Comparacion clave de teoria de colas:
    # Wq en colas paralelas (2.0) es significativamente mayor que en cola unica (4/9 = 0.444)
    assert mmc.wq < parallel.wq
    assert mmc.lq < parallel.lq


def test_summary_dictionaries():
    """Comprueba que los metodos get_summary devuelvan todas las metricas estructuradas."""
    mmc = MMCAnalytical(lamb=3.0, mu=2.0, c=2)
    s_mmc = mmc.get_summary()
    assert {"lambda", "mu", "c", "rho", "P0", "Lq", "Wq", "L", "W"}.issubset(s_mmc.keys())

    par = ParallelMM1Analytical(lamb=3.0, mu=2.0, c=2)
    s_par = par.get_summary()
    assert {"lambda", "mu", "c", "rho", "P0", "Lq", "Wq", "L", "W"}.issubset(s_par.keys())
