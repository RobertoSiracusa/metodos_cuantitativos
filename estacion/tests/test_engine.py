"""Pruebas de ejecucion del motor en modo headless."""

from src.engine.controller import StationController


def test_headless_run_generates_report():
    """Verifica que el controlador corra en headless y devuelva el reporte esperado."""
    controller = StationController(
        headless=True,
        speed_multiplier=1.0,
        num_pumps=3,
        arrival_rate=5.0,
        service_rate=2.0,
    )

    report = controller.run(max_sim_time=40.0)

    assert isinstance(report, dict)
    assert "total_arribos" in report
    assert "Wq_simulado_min" in report
    assert "utilizacion_teorica_rho" in report
    assert report["bombas_activas_c"] == 3
    assert report["total_arribos"] > 0
