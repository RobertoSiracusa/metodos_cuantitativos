"""Pruebas para el controlador y ejecucion headless del automercado."""

import pytest
from src.constants import QueueMode
from src.engine.controller import MarketController


def test_headless_run_generates_report():
    """Verifica que la ejecucion headless complete y genere el reporte consolidado."""
    controller = MarketController(
        headless=True,
        speed_multiplier=1.0,
        num_registers=3,
        arrival_rate=8.0,
        service_rate=3.0,
        queue_mode=QueueMode.PARALLEL,
    )

    report = controller.run(max_sim_time=40.0)

    expected_keys = {
        "disciplina_cola",
        "tiempo_simulado_total_min",
        "cajas_activas_c",
        "tasa_llegada_lambda",
        "tasa_servicio_mu",
        "utilizacion_teorica_rho",
        "Wq_teorico_min",
        "Wq_simulado_min",
        "Lq_teorico",
        "Lq_simulado",
        "total_arribos",
        "total_atendidos",
    }
    assert expected_keys.issubset(report.keys())
    assert report["total_arribos"] > 0
    assert report["tiempo_simulado_total_min"] >= 0.5
