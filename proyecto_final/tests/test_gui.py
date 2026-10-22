"""Test de humo del dashboard (R8-R10): dibuja todos los paneles sin abrir una ventana."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from src.gui.app import AplicacionPygame  # noqa: E402
from src.simulation.motor_simpy import MotorSimulacion  # noqa: E402
from src.utils.config import Configuracion  # noqa: E402


def test_captura_del_dashboard(tmp_path):
    motor = MotorSimulacion(Configuracion.por_defecto(), semilla=1)
    ruta = AplicacionPygame(motor).capturar(tmp_path / "dashboard.png", 60)
    assert ruta.exists() and ruta.stat().st_size > 10_000


def test_dashboard_en_el_instante_cero(tmp_path):
    # sin historial todavia: los paneles no deben fallar con series vacias
    motor = MotorSimulacion(Configuracion.por_defecto(), semilla=1)
    assert AplicacionPygame(motor).capturar(tmp_path / "t0.png", 0).exists()
