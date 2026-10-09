import pytest

from src.core.volumen_carga import VolumenCarga

NOMBRES = ["Tablet Samsung", "Dron DJI Mini", "Proyector portatil", "Laptop ASUS ZenBook"]
PESOS = [2, 3, 4, 5]
PRECIOS = [40, 50, 65, 60]

F_ESPERADAS = [
    [0, 0, 40, 40, 40, 40, 40, 40, 40, 40, 40],
    [0, 0, 40, 50, 50, 90, 90, 90, 90, 90, 90],
    [0, 0, 40, 50, 65, 90, 105, 115, 115, 155, 155],
    [0, 0, 40, 50, 65, 90, 105, 115, 115, 155, 155],
]


@pytest.fixture
def modelo():
    return VolumenCarga(NOMBRES, PESOS, PRECIOS, 10)


def test_tabla_por_etapas(modelo):
    etapas = modelo.tablas_etapas()
    assert len(etapas) == 4
    for i, esperado in enumerate(F_ESPERADAS):
        obtenido = [fila.f for fila in etapas[i]]
        assert obtenido == esperado


def test_optimo(modelo):
    s = modelo.resolver()
    assert s.productos == [0, 1, 2]
    assert s.peso == 9
    assert s.valor == 155
    assert s.libre == 1


def test_dp_coincide_con_milp(modelo):
    assert modelo.resolver().valor == modelo.resolver_milp().valor == 155


def test_voraz_coincide_con_optimo_en_este_caso(modelo):
    v = modelo.resolver_voraz()
    assert v.productos == [0, 1, 2]
    assert v.valor == 155
    assert modelo.resolver().valor - v.valor == 0


def test_capacidad_cero():
    s = VolumenCarga(NOMBRES, PESOS, PRECIOS, 0).resolver()
    assert s.productos == []
    assert s.valor == 0
    assert s.peso == 0
    assert s.libre == 0


def test_capacidad_14_entran_los_4():
    s = VolumenCarga(NOMBRES, PESOS, PRECIOS, 14).resolver()
    assert s.productos == [0, 1, 2, 3]
    assert s.valor == 215
    assert s.peso == 14
    assert s.libre == 0


def test_enumeracion_completa_16_combinaciones(modelo):
    combinaciones = modelo.enumerar()
    assert len(combinaciones) == 16


def test_una_sola_combinacion_optima(modelo):
    optimas = modelo.optimos_alternativos()
    assert len(optimas) == 1
    assert optimas[0].productos == [0, 1, 2]
    assert optimas[0].valor == 155


@pytest.mark.parametrize(
    "nombres, pesos, precios, cap",
    [
        (["A", "B"], [1], [1, 1], 5),           # largos distintos
        (["A"], [0], [1], 5),                    # peso 0
        (["A"], [1.5], [1], 5),                   # peso no entero
        (["A"], [1], [1], -1),                    # capacidad negativa
        (["A"], [1], [1], True),                  # capacidad bool
        (["A"], [1], [-5], 5),                     # precio negativo
    ],
)
def test_validaciones(nombres, pesos, precios, cap):
    with pytest.raises(ValueError):
        VolumenCarga(nombres, pesos, precios, cap)
