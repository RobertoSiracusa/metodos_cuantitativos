"""Manejador de eventos de teclado y ventana en Pygame."""

import pygame


class InputHandler:
    """Captura las interacciones del usuario y aplica comandos al controlador."""

    @staticmethod
    def process_events(controller) -> bool:
        """
        Procesa la cola de eventos de Pygame.
        Retorna False si el usuario decidio cerrar la aplicacion, True si continua.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                # Pausa
                elif event.key == pygame.K_SPACE:
                    controller.is_paused = not controller.is_paused

                # Multiplicadores de velocidad
                elif event.key == pygame.K_1:
                    controller.speed_multiplier = 1.0
                elif event.key == pygame.K_2:
                    controller.speed_multiplier = 2.0
                elif event.key == pygame.K_3:
                    controller.speed_multiplier = 5.0
                elif event.key == pygame.K_4:
                    controller.speed_multiplier = 10.0

                # Ajustes de la tasa de llegada lambda
                elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                    controller.sim.set_arrival_rate(controller.sim.lamb + 0.5)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    controller.sim.set_arrival_rate(controller.sim.lamb - 0.5)

                # Abrir / Cerrar cajas registradoras (modificar c)
                elif event.key == pygame.K_a:
                    controller.sim.open_next_register()
                elif event.key == pygame.K_z:
                    controller.sim.close_last_register()

                # Alternar disciplina de cola (Cola Unica vs Colas Paralelas)
                elif event.key == pygame.K_m:
                    controller.sim.toggle_queue_mode()

                # Reinicio
                elif event.key == pygame.K_r:
                    controller.reset_simulation()

        return True
