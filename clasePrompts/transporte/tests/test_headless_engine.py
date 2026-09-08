"""Pruebas unitarias para la ejecucion del controlador en modo headless."""

from src.engine.controller import TransportController


def test_headless_run_produces_valid_report():
    """Verifica que el motor corra en modo headless y devuelva el reporte analitico esperado."""
    controller = TransportController(
        headless=True,
        speed_multiplier=1.0,
        algorithm="dijkstra",
        auto_mode=True,
    )

    report = controller.run(max_sim_time=15.0)

    assert isinstance(report, dict)
    assert "total_camiones" in report
    assert "camiones_disponibles" in report
    assert "ordenes_entregadas" in report
    assert "toneladas_entregadas" in report
    assert "kilometros_totales" in report
    assert "costo_total_operativo" in report
    assert "ahorro_total_optimizacion" in report
    assert report["total_camiones"] == 6
    assert report["tiempo_simulado_seg"] >= 14.0
