import json
import os

import pytest

from src.core.set_covering import ModeloCubrimiento

RUTA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos", "tiempos.json")


@pytest.fixture
def tiempos():
    with open(RUTA, encoding="utf-8") as f:
        return json.load(f)["tiempos"]


def test_tabla_no_simetrica(tiempos):
    assert tiempos[0][7] == 20 and tiempos[7][0] == 70


def test_cobertura_ida_vuelta(tiempos):
    a = ModeloCubrimiento(tiempos).matriz_cobertura()
    esperado = {1: [1, 2, 3, 4, 5, 10], 8: [2, 3, 8, 9], 9: [7, 8, 9, 10]}
    for ciudad, estaciones in esperado.items():
        assert [j + 1 for j in range(10) if a[ciudad - 1, j]] == estaciones


def test_minimo_ida_vuelta(tiempos):
    m = ModeloCubrimiento(tiempos)
    res = m.resolver()
    assert res.minimo == 3
    assert m._cubre_todo(res.cobertura, res.estaciones)
    assert not m.existe_solucion_con(2)
    assert len(res.optimos_alternativos) == 48
    optimos = [[j + 1 for j in c] for c in res.optimos_alternativos]
    for combinacion in ([2, 3, 9], [1, 2, 7], [8, 9, 10]):
        assert combinacion in optimos


@pytest.mark.parametrize("sentido, estacion", [("ciudad_a_estacion", 8), ("estacion_a_ciudad", 10)])
def test_un_solo_sentido(tiempos, sentido, estacion):
    res = ModeloCubrimiento(tiempos, sentido=sentido).resolver()
    assert res.minimo == 1
    assert res.optimos_alternativos == [[estacion - 1]]


def test_infactible_si_una_ciudad_queda_aislada():
    with pytest.raises(ValueError):
        ModeloCubrimiento([[0, 99], [99, 50]], limite=10).resolver()


def test_validaciones():
    with pytest.raises(ValueError):
        ModeloCubrimiento([[0, 1, 2]])
    with pytest.raises(ValueError):
        ModeloCubrimiento([[0]], sentido="diagonal")
