import math

from src.core.mg_model import MD1Model, MDCModel, MG1Model, MGCModel
from src.core.mmc_model import MMCModel


def test_md1_pollaczek_khinchine():
    m = MD1Model(lamb=0.8, mu=1.0)
    # Lq = rho^2 / (2(1-rho)) = 0.64 / 0.4
    assert math.isclose(m.lq, 1.6, rel_tol=1e-9)
    assert math.isclose(m.l, 1.6 + 0.8, rel_tol=1e-9)
    assert math.isclose(m.wq, 2.0, rel_tol=1e-9)
    assert math.isclose(m.w, 3.0, rel_tol=1e-9)
    assert math.isclose(m.p0, 0.2, rel_tol=1e-9)
    assert m.is_exact


def test_mg1_con_sigma_exponencial_recupera_mm1():
    mu = 1.0
    m = MG1Model(lamb=0.8, mu=mu, sigma=1.0 / mu)  # Cs^2 = 1 -> M/M/1
    assert math.isclose(m.scv, 1.0, rel_tol=1e-9)
    assert math.isclose(m.lq, (0.8 ** 2) / (1 - 0.8), rel_tol=1e-9)


def test_mgc_con_sigma_exponencial_recupera_mmc():
    mu = 6.0
    mmc = MMCModel(lamb=15.0, mu=mu, servers=3)
    mgc = MGCModel(lamb=15.0, mu=mu, servers=3, sigma=1.0 / mu)
    assert math.isclose(mgc.lq, mmc.lq, rel_tol=1e-9)
    assert not mgc.is_exact


def test_mg1_valores_documentados_en_salidas_md():
    m = MG1Model(lamb=0.5, mu=1.2, sigma=0.4)
    assert math.isclose(m.rho, 0.416667, rel_tol=1e-5)
    assert math.isclose(m.p0, 0.583333, rel_tol=1e-5)
    assert math.isclose(m.scv, 0.230400, rel_tol=1e-5)
    assert math.isclose(m.lq, 0.183095, rel_tol=1e-5)
    assert math.isclose(m.l, 0.599762, rel_tol=1e-5)
    assert math.isclose(m.wq, 0.366190, rel_tol=1e-5)
    assert math.isclose(m.w, 1.199524, rel_tol=1e-5)


def test_mgc_valores_documentados_en_salidas_md():
    m = MGCModel(lamb=15.0, mu=6.0, servers=3, sigma=0.1)
    assert math.isclose(m.rho, 0.833333, rel_tol=1e-5)
    assert math.isclose(m.p0, 0.044944, rel_tol=1e-4)
    assert math.isclose(m.scv, 0.360000, rel_tol=1e-5)
    assert math.isclose(m.lq, 2.387640, rel_tol=1e-5)
    assert math.isclose(m.l, 4.887640, rel_tol=1e-5)
    assert math.isclose(m.wq, 0.159176, rel_tol=1e-5)
    assert math.isclose(m.w, 0.325843, rel_tol=1e-5)


def test_mdc_es_mitad_de_mmc():
    mmc = MMCModel(lamb=15.0, mu=6.0, servers=3)
    mdc = MDCModel(lamb=15.0, mu=6.0, servers=3)
    assert mdc.sigma == 0.0
    assert math.isclose(mdc.lq, mmc.lq / 2.0, rel_tol=1e-9)


def test_mmc_steps_no_se_desincroniza_de_las_properties():
    m = MMCModel(lamb=15.0, mu=6.0, servers=3)
    ultimo_paso = m.steps()[-1]
    _titulo, _formula, _sustitucion, resultado = ultimo_paso
    valor_paso = float(resultado.split('=')[-1].strip())
    assert math.isclose(valor_paso, m.pw, rel_tol=1e-6)


def test_mg1_steps_no_se_desincroniza_de_las_properties():
    m = MG1Model(lamb=0.5, mu=1.2, sigma=0.4)
    ultimo_paso = m.steps()[-1]
    _titulo, _formula, _sustitucion, resultado = ultimo_paso
    valor_paso = float(resultado.split('=')[-1].strip())
    assert math.isclose(valor_paso, m.w, rel_tol=1e-6)
