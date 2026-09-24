import pytest
from scipy.optimize import milp, LinearConstraint, Bounds

from src.core.branch_and_bound import ModeloBranchAndBound

C, A, B = [80, 45], [[1, 1], [12, 5]], [7, 60]


@pytest.fixture
def resultado():
    return ModeloBranchAndBound(C, A, B).resolver()


def test_relajacion_lineal():
    x, z = ModeloBranchAndBound(C, A, B).resolver_relajacion([(0, None), (0, None)])
    assert x == pytest.approx([25 / 7, 24 / 7])
    assert z == pytest.approx(440)


def test_optimo_entero(resultado):
    assert resultado.x_optimo == [3, 4]
    assert resultado.z_optimo == pytest.approx(420)


def test_arbol_del_parcial(resultado):
    esperado = {  # id: (rama, Z)
        1: ("x1 <= 3", 420), 2: ("x1 >= 4", 428), 3: ("x2 <= 2", 423.3333),
        4: ("x2 >= 3", None), 5: ("x1 <= 4", 410), 6: ("x1 >= 5", 400),
    }
    assert len(resultado.nodos) == 7
    for nid, (rama, z) in esperado.items():
        n = resultado.nodos[nid]
        assert n.restriccion == rama
        assert (n.z is None) if z is None else n.z == pytest.approx(z, abs=1e-3)
    assert resultado.nodos[4].estado == "INFACTIBLE"
    assert resultado.nodos[5].estado.startswith("PODADO")


def test_coincide_con_milp(resultado):
    r = milp([-v for v in C], constraints=LinearConstraint(A, ub=B), integrality=[1, 1], bounds=Bounds(0, float("inf")))
    assert -r.fun == pytest.approx(resultado.z_optimo)


def test_problema_infactible():
    res = ModeloBranchAndBound([1, 1], [[1, 1]], [-1]).resolver()
    assert res.x_optimo is None and res.z_optimo is None


def test_dimensiones_invalidas():
    with pytest.raises(ValueError):
        ModeloBranchAndBound([1, 2], [[1, 1, 1]], [5])
