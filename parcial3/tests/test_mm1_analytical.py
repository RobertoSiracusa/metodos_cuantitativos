"""Pruebas del modelo M/M/1 analitico contra las formulas cerradas del enunciado."""

import pytest

from src.core.mm1_analytical import ModeloMM1
from src.utils.config import LAMBDA_ORDENES_HORA, MU_ENSAMBLAJE_HORA, TEORICO_MM1
from src.utils.validators import ValidacionError


@pytest.fixture
def modelo():
    """Modelo con los parametros oficiales: lambda = 10 ordenes/h, mu = 12 laptops/h."""
    return ModeloMM1(lamb=10.0, mu=12.0)


@pytest.mark.parametrize(
    "atributo,esperado",
    [
        ("rho", 0.833333),
        ("p0", 0.166667),
        ("l", 5.0),
        ("lq", 4.166667),
        ("w", 0.5),
        ("wq", 0.416667),
    ],
    ids=["rho", "p0", "L", "Lq", "W", "Wq"],
)
def test_valores_cerrados_del_enunciado(modelo, atributo, esperado):
    assert getattr(modelo, atributo) == pytest.approx(esperado, abs=1e-6)


def test_tiempos_en_minutos(modelo):
    assert modelo.w * 60.0 == pytest.approx(30.0, abs=1e-6)
    assert modelo.wq * 60.0 == pytest.approx(25.0, abs=1e-4)


def test_los_parametros_de_config_reproducen_el_modelo_oficial():
    modelo = ModeloMM1(lamb=LAMBDA_ORDENES_HORA, mu=MU_ENSAMBLAJE_HORA)
    assert MU_ENSAMBLAJE_HORA == pytest.approx(12.0)
    assert modelo.rho == pytest.approx(TEORICO_MM1["rho"], abs=1e-6)
    assert modelo.wq * 60.0 == pytest.approx(TEORICO_MM1["wq_min"], abs=1e-4)


def test_ley_de_little(modelo):
    """L = lambda * W  y  Lq = lambda * Wq deben cumplirse de forma exacta."""
    assert modelo.l == pytest.approx(modelo.lamb * modelo.w, abs=1e-12)
    assert modelo.lq == pytest.approx(modelo.lamb * modelo.wq, abs=1e-12)


def test_relacion_entre_l_y_lq(modelo):
    """L - Lq = rho: las ordenes en servicio son exactamente rho en promedio."""
    assert modelo.l - modelo.lq == pytest.approx(modelo.rho, abs=1e-12)


def test_distribucion_de_estado_suma_uno(modelo):
    assert sum(modelo.probabilidad_n(n) for n in range(400)) == pytest.approx(1.0, abs=1e-6)


def test_probabilidad_mas_de_k(modelo):
    assert modelo.probabilidad_mas_de(0) == pytest.approx(modelo.rho, abs=1e-12)
    assert modelo.probabilidad_mas_de(2) == pytest.approx(modelo.rho ** 3, abs=1e-12)


def test_resumen_expone_todas_las_claves(modelo):
    resumen = modelo.resumen()
    for clave in ("lambda", "mu", "rho", "p0", "l", "lq", "w_horas", "wq_horas", "w_min", "wq_min"):
        assert clave in resumen


def test_pasos_desarrollados_tienen_formula_y_resultado(modelo):
    pasos = modelo.pasos_desarrollados()
    assert len(pasos) == 6
    for nombre, formula, sustitucion, resultado in pasos:
        assert nombre and formula and sustitucion and resultado


def test_sistema_inestable_se_rechaza():
    """Con lambda >= mu las formulas cerradas no aplican: debe fallar al construir."""
    with pytest.raises(ValidacionError, match="inestable"):
        ModeloMM1(lamb=12.0, mu=10.0)
    with pytest.raises(ValidacionError, match="inestable"):
        ModeloMM1(lamb=12.0, mu=12.0)


@pytest.mark.parametrize("valor", [-1, -5])
def test_indices_negativos_se_rechazan(modelo, valor):
    with pytest.raises(ValidacionError):
        modelo.probabilidad_n(valor)
    with pytest.raises(ValidacionError):
        modelo.probabilidad_mas_de(valor)
