"""Controlador principal que sincroniza el bucle de Pygame con los eventos de SimPy."""

from typing import Dict, Any, Optional
import pygame

from src.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    DEFAULT_REGISTERS,
    DEFAULT_LAMBDA,
    DEFAULT_MU,
    QueueMode,
)
from src.simulation.market_sim import MarketSimulation
from src.view.market_view import MarketView
from src.view.hud_view import HudView
from src.engine.input_handler import InputHandler


class MarketController:
    """Orquesta la sincronizacion temporal, la simulacion estocastica y la vista grafica."""

    def __init__(
        self,
        headless: bool = False,
        speed_multiplier: float = 1.0,
        num_registers: int = DEFAULT_REGISTERS,
        arrival_rate: float = DEFAULT_LAMBDA,
        service_rate: float = DEFAULT_MU,
        queue_mode: QueueMode = QueueMode.PARALLEL,
    ):
        self.headless = headless
        self.speed_multiplier = float(speed_multiplier)
        self.is_paused = False
        self.num_registers = num_registers
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.queue_mode = queue_mode

        # Instancia del simulador SimPy
        self.sim = MarketSimulation(
            num_registers=self.num_registers,
            arrival_rate_per_min=self.arrival_rate,
            service_rate_per_min=self.service_rate,
            queue_mode=self.queue_mode,
        )

        self.screen = None
        self.clock = None
        self.fonts = {}
        self.market_view = None
        self.hud_view = None

        if not self.headless:
            self._init_pygame()

    def _init_pygame(self):
        """Inicializa subsistemas de Pygame y fuentes del sistema."""
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Simulacion Automercado y Lineas de Espera — Metodos Cuantitativos")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.fonts = {
            "title": pygame.font.SysFont("Helvetica,Arial,sans-serif", 19, bold=True),
            "bold": pygame.font.SysFont("Helvetica,Arial,sans-serif", 13, bold=True),
            "small": pygame.font.SysFont("Helvetica,Arial,sans-serif", 12),
            "tiny": pygame.font.SysFont("Helvetica,Arial,sans-serif", 11),
        }

        self.market_view = MarketView(self.fonts)
        self.hud_view = HudView(self.fonts)

    def reset_simulation(self):
        """Reinicia la simulacion completa conservando configuracion vigente."""
        self.sim = MarketSimulation(
            num_registers=self.sim.active_registers_count,
            arrival_rate_per_min=self.sim.lamb,
            service_rate_per_min=self.sim.mu,
            queue_mode=self.sim.queue_mode,
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
            dt_real = self.clock.tick(FPS) / 1000.0
            dt_real = min(dt_real, 0.1)

            running = InputHandler.process_events(self)

            if not self.is_paused:
                sim_dt = dt_real * self.speed_multiplier
                target_sim_time = self.sim.current_sim_time + sim_dt
                self.sim.step(target_sim_time)

            if max_sim_time and self.sim.current_sim_time >= max_sim_time:
                break

            self.market_view.update_and_render(self.screen, self.sim, dt_real)
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
        """Ejecuta la simulacion a maxima velocidad sin entorno grafico para benchmarking."""
        step_chunk = 1.0
        while self.sim.current_sim_time < duration_s:
            self.sim.step(min(duration_s, self.sim.current_sim_time + step_chunk))

        return self._generate_report()

    def _generate_report(self) -> Dict[str, Any]:
        """Consolida las metricas cuantitativas comparativas de la sesion."""
        theo = self.sim.current_analytical_model
        stats = self.sim.stats

        return {
            "disciplina_cola": self.sim.queue_mode.value,
            "tiempo_simulado_total_min": round(self.sim.current_sim_time / 60.0, 2),
            "cajas_activas_c": self.sim.active_registers_count,
            "tasa_llegada_lambda": self.sim.lamb,
            "tasa_servicio_mu": self.sim.mu,
            "utilizacion_teorica_rho": round(theo.rho, 4),
            "utilizacion_simulada_rho": round(stats.empirical_rho, 4),
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
            "articulos_vendidos": stats.total_items_sold,
            "ingresos_estimados_usd": round(stats.total_revenue, 2),
        }
