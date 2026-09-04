"""Controlador central que sincroniza la vista grafica de Pygame con los eventos de SimPy."""

from typing import Dict, Any, Optional
import pygame

from src.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    DEFAULT_ROD_INSERTION,
    COLOR_BG,
)
from src.simulation.reactor_sim import ReactorSimulation
from src.view.core_view import CoreView
from src.view.hud_view import HudView
from src.engine.input_handler import InputHandler


class NuclearController:
    """Orquesta la sincronizacion temporal, la visualizacion y los comandos del operador."""

    def __init__(
        self,
        headless: bool = False,
        speed_multiplier: float = 1.0,
        enrichment: float = 0.20,
        initial_rod_insertion: float = DEFAULT_ROD_INSERTION,
    ):
        self.headless = headless
        self.speed_multiplier = float(speed_multiplier)
        self.enrichment = float(enrichment)
        self.initial_rod_insertion = float(initial_rod_insertion)
        self.is_paused = False

        # Instancia de simulacion SimPy
        self.sim = ReactorSimulation(
            enrichment=self.enrichment,
            initial_rod_insertion=self.initial_rod_insertion,
        )

        self.screen = None
        self.clock = None
        self.fonts = {}
        self.core_view = None
        self.hud_view = None

        if not self.headless:
            self._init_pygame()

    def _init_pygame(self):
        """Inicializa ventana, reloj y tipografias del sistema."""
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Simulacion de Reactor y Reaccion Nuclear — SimPy + Pygame")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.fonts = {
            "title": pygame.font.SysFont("Helvetica,Arial,sans-serif", 20, bold=True),
            "bold": pygame.font.SysFont("Helvetica,Arial,sans-serif", 13, bold=True),
            "small": pygame.font.SysFont("Helvetica,Arial,sans-serif", 12),
            "tiny": pygame.font.SysFont("Helvetica,Arial,sans-serif", 10),
        }

        self.core_view = CoreView(self.fonts)
        self.hud_view = HudView(self.fonts)

    def reset_simulation(self):
        """Reinicia el reactor a sus condiciones de combustible fresco."""
        self.sim = ReactorSimulation(
            enrichment=self.enrichment,
            initial_rod_insertion=self.initial_rod_insertion,
        )

    def run(self, max_sim_time: Optional[float] = None) -> Dict[str, Any]:
        """
        Bucle principal de ejecucion.
        max_sim_time: Si se especifica, corre hasta dicho tiempo simulado en segundos.
        """
        if self.headless:
            return self._run_headless(max_sim_time or 60.0)

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

            # Renderizado
            self.screen.fill(COLOR_BG)
            self.core_view.render(self.screen, self.sim, dt_real)
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
        """Ejecuta la simulacion a maxima velocidad sin subsistema de video."""
        step_chunk = 0.5
        while self.sim.current_sim_time < duration_s:
            self.sim.step(min(duration_s, self.sim.current_sim_time + step_chunk))

        return self._generate_report()

    def _generate_report(self) -> Dict[str, Any]:
        """Consolida las metricas cuantitativas de la sesion nuclear."""
        core = self.sim.core
        stats = self.sim.stats

        return {
            "tiempo_simulado_total_segundos": round(self.sim.current_sim_time, 2),
            "enriquecimiento_U235_pct": f"{self.enrichment * 100:.1f}%",
            "insercion_barras_control_pct": f"{core.get_average_rod_insertion() * 100:.1f}%",
            "factor_multiplicacion_keff_final": round(core.k_eff, 4),
            "estado_final_reactor": core.state.value,
            "fisiones_totales_producidas": stats.total_fissions,
            "neutrones_prontos_emitidos": stats.total_neutrons_born,
            "neutrones_capturados_en_barras": stats.total_absorbed_rods,
            "neutrones_escapados_vasija": stats.total_escaped,
            "neutrones_activos_finales": len(core.neutrons),
            "potencia_termica_mw_final": round(core.thermal_power_mw, 2),
            "temperatura_nucleo_final_c": round(core.temperature, 2),
            "bombas_refrigerante": "ACTIVAS" if core.coolant_pumps_active else "APAGADAS",
            "eventos_scram_emergencia": stats.scram_events,
        }
