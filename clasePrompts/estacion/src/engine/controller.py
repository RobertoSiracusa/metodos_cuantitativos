"""Controlador central que sincroniza el reloj de Pygame con los eventos de SimPy."""

import time
from typing import Dict, Any, Optional
import pygame

from src.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    DEFAULT_SERVERS,
    DEFAULT_LAMBDA,
    DEFAULT_MU,
)
from src.simulation.gas_station_sim import GasStationSimulation
from src.view.station_view import StationView
from src.view.hud_view import HudView
from src.engine.input_handler import InputHandler


class StationController:
    """Orquesta la sincronizacion temporal, vista grafica y eventos."""

    def __init__(
        self,
        headless: bool = False,
        speed_multiplier: float = 1.0,
        num_pumps: int = DEFAULT_SERVERS,
        arrival_rate: float = DEFAULT_LAMBDA,
        service_rate: float = DEFAULT_MU,
    ):
        self.headless = headless
        self.speed_multiplier = float(speed_multiplier)
        self.is_paused = False
        self.num_pumps = num_pumps
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate

        # Instancia del simulador SimPy
        self.sim = GasStationSimulation(
            num_pumps=self.num_pumps,
            arrival_rate_per_min=self.arrival_rate,
            service_rate_per_min=self.service_rate,
        )

        self.screen = None
        self.clock = None
        self.fonts = {}
        self.station_view = None
        self.hud_view = None

        if not self.headless:
            self._init_pygame()

    def _init_pygame(self):
        """Inicializa subsistemas graficos y fuentes."""
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Simulacion Estacion de Gasolina M/M/c — Metodos Cuantitativos")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        # Cargar tipografias seguras del sistema
        self.fonts = {
            "title": pygame.font.SysFont("Helvetica,Arial,sans-serif", 19, bold=True),
            "bold": pygame.font.SysFont("Helvetica,Arial,sans-serif", 13, bold=True),
            "small": pygame.font.SysFont("Helvetica,Arial,sans-serif", 12),
            "tiny": pygame.font.SysFont("Helvetica,Arial,sans-serif", 11),
        }

        self.station_view = StationView(self.fonts)
        self.hud_view = HudView(self.fonts)

    def reset_simulation(self):
        """Reinicia la simulacion completa conservando configuracion."""
        self.sim = GasStationSimulation(
            num_pumps=self.num_pumps,
            arrival_rate_per_min=self.arrival_rate,
            service_rate_per_min=self.service_rate,
        )

    def run(self, max_sim_time: Optional[float] = None) -> Dict[str, Any]:
        """
        Bucle principal de ejecucion.
        max_sim_time: Si se especifica, corre hasta alcanzar dicho tiempo simulado en segundos.
        """
        if self.headless:
            return self._run_headless(max_sim_time or 300.0)

        running = True
        while running:
            # Medir tiempo real entre fotogramas
            dt_real = self.clock.tick(FPS) / 1000.0
            dt_real = min(dt_real, 0.1)  # Prevenir saltos por lag

            # Manejar eventos de teclado/ventana
            running = InputHandler.process_events(self)

            if not self.is_paused:
                # Avanzar tiempo en SimPy segun el multiplicador de velocidad
                sim_dt = dt_real * self.speed_multiplier
                target_sim_time = self.sim.current_sim_time + sim_dt
                self.sim.step(target_sim_time)

            # Comprobar limite de tiempo
            if max_sim_time and self.sim.current_sim_time >= max_sim_time:
                break

            # Renderizado
            self.station_view.update_and_render(self.screen, self.sim, dt_real)
            self.hud_view.render(
                self.screen,
                self.sim,
                self.speed_multiplier,
                self.is_paused,
                self.clock.get_fps(),
            )

            pygame.display.flip()

        pygame.quit()
        return self._generate_report()

    def _run_headless(self, duration_s: float) -> Dict[str, Any]:
        """Ejecuta la simulacion a maxima velocidad sin entorno grafico."""
        step_chunk = 1.0  # Avanzar de 1 en 1 segundo simulado
        while self.sim.current_sim_time < duration_s:
            self.sim.step(min(duration_s, self.sim.current_sim_time + step_chunk))

        return self._generate_report()

    def _generate_report(self) -> Dict[str, Any]:
        """Consolida las metricas cuantitativas finales de la sesion."""
        theo = self.sim.analytical_model
        stats = self.sim.stats

        return {
            "tiempo_simulado_total_min": round(self.sim.current_sim_time / 60.0, 2),
            "bombas_activas_c": self.num_pumps,
            "tasa_llegada_lambda": self.sim.lamb,
            "tasa_servicio_mu": self.sim.mu,
            "utilizacion_teorica_rho": round(theo.rho, 4),
            "P0_prob_vacio_teorica": round(theo.p0, 4) if theo.is_stable else 0.0,
            "Wq_teorico_min": round(theo.wq, 3) if theo.is_stable else -1.0,
            "Wq_simulado_min": round(stats.avg_wait_time_min, 3),
            "W_teorico_min": round(theo.w, 3) if theo.is_stable else -1.0,
            "W_simulado_min": round(stats.avg_system_time_min, 3),
            "Lq_teorico": round(theo.lq, 3) if theo.is_stable else -1.0,
            "Lq_simulado": round(stats.avg_queue_length, 3),
            "L_teorico": round(theo.l, 3) if theo.is_stable else -1.0,
            "L_simulado": round(stats.avg_system_length, 3),
            "total_arribos": stats.total_arrivals,
            "total_atendidos": stats.total_served,
            "total_rechazados_cola_llena": stats.total_balked,
            "combustible_restante_L": round(self.sim.tank.level, 1),
        }
