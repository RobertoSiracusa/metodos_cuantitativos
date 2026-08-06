import math

from src.core.mmc_model import MMCModel


def test_mmc_model_exercise_2_metrics():
    model = MMCModel(lamb=15.0, mu=6.0, servers=3)

    assert math.isclose(model.rho, 0.8333333333, rel_tol=1e-4)
    assert math.isclose(model.p0, 0.0449438202, rel_tol=1e-4)
    assert math.isclose(model.lq, 3.5112359551, rel_tol=1e-4)
    assert math.isclose(model.w, 0.4007490637, rel_tol=1e-4)
    assert math.isclose(model.pw, 0.7022471910, rel_tol=1e-4)
