"""Manejador de interaccion de usuario mediante teclado y raton."""

import pygame
from src.constants import SIM_WIDTH


class InputHandler:
    """Procesa eventos de entrada en Pygame para interactuar con la simulacion."""

    @staticmethod
    def process_events(controller: "TransportController") -> bool:
        """
        Lee la cola de eventos de Pygame y ejecuta las acciones correspondientes.
        Retorna False si el usuario decidio cerrar la aplicacion, True si continua.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic izquierdo
                    mx, my = event.pos
                    if mx < SIM_WIDTH:
                        clicked_node = controller.sim.graph.find_node_at_pos(mx, my, radius=24.0)
                        if clicked_node:
                            controller.sim.select_node(clicked_node)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                elif event.key == pygame.K_SPACE:
                    controller.is_paused = not controller.is_paused

                elif event.key == pygame.K_d:
                    controller.sim.dispatch_selected_route()

                elif event.key == pygame.K_a:
                    controller.sim.toggle_auto_mode()

                elif event.key == pygame.K_t:
                    controller.sim.toggle_algorithm()

                elif event.key == pygame.K_r:
                    controller.reset_simulation()

                elif event.key == pygame.K_1:
                    controller.speed_multiplier = 1.0
                elif event.key == pygame.K_2:
                    controller.speed_multiplier = 2.0
                elif event.key == pygame.K_3:
                    controller.speed_multiplier = 5.0
                elif event.key == pygame.K_4:
                    controller.speed_multiplier = 10.0

        return True
