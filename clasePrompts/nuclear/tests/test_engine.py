"""Pruebas unitarias para el controlador y ejecucion headless."""

import pytest
from src.engine.controller import NuclearController


def test_controller_headless_execution():
    """Verifica que el controlador corra en modo headless y genere un reporte cuantitativo valido."""
    controller = NuclearController(
        headless=True,
        speed_multiplier=1.0,
        enrichment=0.20,
        initial_rod_insertion=0.45,
    )

    report = controller.run(max_sim_time=2.0)
    assert isinstance(report, dict)
    assert "tiempo_simulado_total_segundos" in report
    assert "factor_multiplicacion_keff_final" in report
    assert "estado_final_reactor" in report
    assert "fisiones_totales_producidas" in report
    assert report["tiempo_simulado_total_segundos"] >= 2.0


def test_controller_reset():
    """Verifica que reset_simulation reinicie el estado conservando configuracion."""
    controller = NuclearController(
        headless=True,
        enrichment=0.25,
        initial_rod_insertion=0.35,
    )
    controller.sim.step(1.5)
    assert controller.sim.env.now >= 1.5

    controller.reset_simulation()
    assert controller.sim.env.now == 0.0
    assert controller.sim.enrichment == 0.25
    assert controller.sim.initial_rod_insertion == 0.35
