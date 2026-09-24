import pytest

from src.core.knapsack import ModeloMochila

PESOS = [10, 20, 15, 25, 30, 12]
VALORES = [60, 100, 90, 120, 150, 80]


@pytest.fixture
def modelo():
    return ModeloMochila(PESOS, VALORES, 50)


def test_optimo_programacion_dinamica(modelo):
    s = modelo.resolver_dp()
    assert s.valor == 270
    assert s.peso <= 50


def test_dp_coincide_con_milp(modelo):
    assert modelo.resolver_dp().valor == modelo.resolver_milp().valor


def test_optimos_alternativos(modelo):
    alt = modelo.optimos_alternativos(270)
    assert [(s.objetos, s.peso) for s in alt] == [([1, 2, 5], 47), ([0, 2, 3], 50)]


def test_voraz_no_es_optimo(modelo):
    v = modelo.resolver_voraz()
    assert v.objetos == [0, 2, 5]
    assert v.valor == 230


def test_capacidad_cero():
    s = ModeloMochila([5], [10], 0).resolver_dp()
    assert s.objetos == [] and s.valor == 0


@pytest.mark.parametrize("pesos, valores, cap", [([1, 2], [1], 5), ([0], [1], 5), ([1.5], [1], 5), ([1], [1], -1)])
def test_validaciones(pesos, valores, cap):
    with pytest.raises(ValueError):
        ModeloMochila(pesos, valores, cap)
