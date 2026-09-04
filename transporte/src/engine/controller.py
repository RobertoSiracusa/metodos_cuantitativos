"""Controlador central que coordina la simulacion de transporte y el bucle grafico."""

import os
from typing import Any, Dict, Optional
import pygame

from src.constants import FPS, WINDOW_HEIGHT, WINDOW_WIDTH
from src.engine.input_handler import InputHandler
from src.simulation.transport_sim import TransportSimulation
from src.view.hud_view import HudView
from src.view.network_view import NetworkView
from src.view.truck_view import TruckView


class TransportController:
    """Orquesta la sincronizacion temporal, entrada interactiva y renderizado."""

    def __init__(
        self,
        headless: bool = False,
        speed_multiplier: float = 1.0,
        algorithm: str = "dijkstra",
        auto_mode: bool = False,
    ):
        self.headless = headless
        self.speed_multiplier = float(speed_multiplier)
        self.is_paused = False
        self.algorithm = algorithm
        self.auto_mode = auto_mode

        # Motor de simulacion
        self.sim = TransportSimulation(algorithm=self.algorithm, auto_mode=self.auto_mode)

        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.network_view: Optional[NetworkView] = None
        self.truck_view: Optional[TruckView] = None
        self.hud_view: Optional[HudView] = None

        if self.headless:
            # Configurar driver dummy para entornos headless / CI / testing
            os.environ["SDL_VIDEODRIVER"] = "dummy"
        else:
            self._init_pygame()

    def _init_pygame(self):
        """Inicializa los subsistemas graficos de Pygame y las tipografias del sistema."""
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Optimizacion de Redes de Transporte & Asignacion de Flota — Metodos Cuantitativos")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.fonts = {
            "title": pygame.font.SysFont("Helvetica,Arial,sans-serif", 16, bold=True),
            "bold": pygame.font.SysFont("Helvetica,Arial,sans-serif", 12, bold=True),
            "small": pygame.font.SysFont("Helvetica,Arial,sans-serif", 11),
            "tiny": pygame.font.SysFont("Helvetica,Arial,sans-serif", 10),
        }

        self.network_view = NetworkView(self.fonts)
        self.truck_view = TruckView(self.fonts)
        self.hud_view = HudView(self.fonts)

    def reset_simulation(self):
        """Reinicia la simulacion completa conservando configuracion."""
        self.sim = TransportSimulation(algorithm=self.algorithm, auto_mode=self.auto_mode)

    def run(self, max_sim_time: Optional[float] = None) -> Dict[str, Any]:
        """
        Ejecuta el bucle principal de la simulacion interactiva o headless.
        max_sim_time: Duracion maxima en segundos de tiempo simulado.
        """
        if self.headless:
            return self._run_headless(max_sim_time or 60.0)

        running = True
        while running:
            # Medir tiempo real entre fotogramas
            dt_real = self.clock.tick(FPS) / 1000.0
            dt_real = min(dt_real, 0.1)

            # Manejar eventos de entrada
            running = InputHandler.process_events(self)

            # Avanzar simulacion si no esta pausado
            if not self.is_paused:
                dt_sim = dt_real * self.speed_multiplier
                self.sim.step(dt_sim)

            # Dibujar la escena completa
            self.network_view.draw(
                surface=self.screen,
                graph=self.sim.graph,
                selected_origin=self.sim.selected_origin,
                selected_dest=self.sim.selected_dest,
                optimal_path=self.sim.preview_path,
                alt_path=self.sim.preview_alt_path,
            )

            self.truck_view.draw_fleet(self.screen, self.sim.fleet_manager.trucks)

            self.hud_view.draw(
                surface=self.screen,
                sim=self.sim,
                speed_multiplier=self.speed_multiplier,
                is_paused=self.is_paused,
            )

            pygame.display.flip()

            if max_sim_time and self.sim.sim_time >= max_sim_time:
                break

        pygame.quit()
        return self.sim.get_metrics()

    def _run_headless(self, duration_sec: float) -> Dict[str, Any]:
        """Ejecuta la simulacion a maxima velocidad sin abrir ventana grafica."""
        dt_step = 0.05
        steps = int(duration_sec / dt_step)

        # Si no hay ordenes iniciales, crear al menos una para asegurar operacion
        if not self.sim.fleet_manager.pending_orders and not self.sim.auto_mode:
            self.sim.dispatch_selected_route(cargo_tons=14.0)

        for _ in range(steps):
            self.sim.step(dt_step)

        return self.sim.get_metrics()
