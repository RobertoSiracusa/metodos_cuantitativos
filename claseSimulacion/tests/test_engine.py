"""Pruebas para el controlador del juego en modo headless."""

from src.constants import ControlMode
from src.engine.controller import GameController


def test_headless_game_controller_execution():
    controller = GameController(
        headless=True,
        control_mode=ControlMode.AUTO_AI,
        speed_multiplier=1.0,
    )

    # Ejecutar 1.5 segundos de simulacion discreta
    summary = controller.run(max_sim_time=1.5)

    assert summary["tiempo_simulado_seg"] >= 0.5
    assert summary["pasos_totales"] > 0
    assert "puntos_acumulados" in summary
    assert "alimentos_totales" in summary
