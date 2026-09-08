"""Manejador de eventos y atajos de teclado para la simulacion."""

import pygame


class InputHandler:
    """Traduce eventos de entrada de usuario a comandos de simulacion."""

    @staticmethod
    def process_events(controller) -> bool:
        """
        Procesa la cola de eventos de Pygame.
        Devuelve False si el usuario solicita salir, True para continuar.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    controller.is_paused = not controller.is_paused
                elif event.key == pygame.K_1:
                    controller.speed_multiplier = 1.0
                elif event.key == pygame.K_2:
                    controller.speed_multiplier = 2.0
                elif event.key == pygame.K_3:
                    controller.speed_multiplier = 5.0
                elif event.key == pygame.K_4:
                    controller.speed_multiplier = 10.0
                elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                    controller.sim.set_arrival_rate(controller.sim.lamb + 0.5)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    controller.sim.set_arrival_rate(controller.sim.lamb - 0.5)
                elif event.key == pygame.K_c:
                    controller.sim.trigger_tanker_truck()
                elif event.key == pygame.K_r:
                    controller.reset_simulation()

        return True
