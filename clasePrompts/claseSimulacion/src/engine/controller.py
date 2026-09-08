"""Controlador central que acopla el bucle grafico de Pygame y el reloj de eventos de SimPy."""

import os
import sys
from typing import Optional
import pygame

from ..constants import (
    ControlMode,
    GameState,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from ..simulation.environment import SnakeSimulationEnvironment
from ..view.renderer import GameRenderer
from .input_handler import InputHandler


class GameController:
    """
    Controlador principal (Arquitectura MVC / POO):
    - Mantiene sincronizados el reloj de cuadros de Pygame (60 FPS) y el entorno de SimPy.
    - Administra la maquina de estados (RUNNING, PAUSED, GAME_OVER).
    - Permite ejecucion con interfaz grafica nativa o modo 'headless' (pruebas y benchmarking).
    """

    def __init__(
        self,
        headless: bool = False,
        control_mode: ControlMode = ControlMode.MANUAL,
        speed_multiplier: float = 1.0,
    ):
        self.headless = headless
        self.speed_multiplier = speed_multiplier
        self.state = GameState.RUNNING
        self.running = True

        # Inicializacion de entorno de simulacion SimPy
        self.sim_env = SnakeSimulationEnvironment(
            control_mode=control_mode,
            on_game_over_callback=self._handle_game_over,
        )

        # Reloj acumulado para avanzar SimPy en funcion del tiempo real * multiplicador
        self.sim_target_time = 0.0

        if not self.headless:
            pygame.init()
            pygame.display.set_caption("UJAP - Metodos Cuantitativos | Simulacion Snake")
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.clock = pygame.time.Clock()
            self.renderer = GameRenderer(self.screen)
        else:
            self.screen = None
            self.clock = None
            self.renderer = None

    def _handle_game_over(self) -> None:
        """Callback invocado por SimPy cuando ocurre una colision."""
        self.state = GameState.GAME_OVER

    def run(self, max_sim_time: Optional[float] = None) -> dict:
        """
        Ejecuta el bucle principal de la simulacion.
        Si max_sim_time esta definido, se detiene al alcanzar ese tiempo simulado.
        """
        if self.headless:
            return self._run_headless(max_sim_time or 60.0)

        target_fps = 60
        while self.running:
            dt = self.clock.tick(target_fps) / 1000.0  # Tiempo transcurrido en segundos reales

            # 1. Procesar eventos de entrada
            for event in pygame.event.get():
                action = InputHandler.process_event(event)

                if action["quit"]:
                    self.running = False
                    break

                if action["toggle_pause"]:
                    if self.state == GameState.RUNNING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.RUNNING

                if action["toggle_mode"]:
                    self.sim_env.toggle_control_mode()

                if action["reset"]:
                    self.sim_env.reset()
                    self.sim_target_time = 0.0
                    self.state = GameState.RUNNING

                if action["speed"] is not None:
                    self.speed_multiplier = action["speed"]

                if action["direction"] is not None and self.state == GameState.RUNNING:
                    # En modo manual, el usuario fija la direccion
                    if self.sim_env.control_mode == ControlMode.MANUAL:
                        self.sim_env.snake.set_direction(action["direction"])

            # 2. Actualizar estado de simulacion si esta activo
            if self.state == GameState.RUNNING:
                self.sim_target_time += dt * self.speed_multiplier
                self.sim_env.advance_to(self.sim_target_time)

                if max_sim_time and self.sim_env.env.now >= max_sim_time:
                    self.running = False

            # 3. Renderizar vista
            current_fps = self.clock.get_fps()
            self.renderer.render(
                sim_env=self.sim_env,
                game_state=self.state,
                speed_multiplier=self.speed_multiplier,
                fps=current_fps,
            )
            pygame.display.flip()

        pygame.quit()
        return self.sim_env.stats.get_summary_dict()

    def _run_headless(self, duration_sim_seconds: float, step_dt: float = 0.05) -> dict:
        """Modo sin interfaz grafica para pruebas unitarias y simulaciones de Monte Carlo."""
        t = 0.0
        while t < duration_sim_seconds and self.sim_env.snake.is_alive:
            t += step_dt
            self.sim_env.advance_to(t)

        return self.sim_env.stats.get_summary_dict()
