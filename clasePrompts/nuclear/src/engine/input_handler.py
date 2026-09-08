"""Manejador de eventos de entrada y controles interactivos del reactor."""

import pygame


class InputHandler:
    """Procesa eventos de teclado y ventana para alterar la dinamica del reactor."""

    @staticmethod
    def process_events(controller) -> bool:
        """
        Retorna True para continuar la ejecucion o False si el usuario decidio salir.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                elif event.key == pygame.K_SPACE:
                    # Inyeccion de neutrones fuente
                    controller.sim.inject_neutron_source(count=15)

                elif event.key == pygame.K_UP:
                    # Extraer barras de control (+ reactividad)
                    controller.sim.core.adjust_control_rods(-0.05)

                elif event.key == pygame.K_DOWN:
                    # Insertar barras de control (- reactividad)
                    controller.sim.core.adjust_control_rods(0.05)

                elif event.key in (pygame.K_s, pygame.K_F1):
                    # SCRAM parada de emergencia
                    controller.sim.core.trigger_scram()
                    controller.sim.stats.scram_events += 1

                elif event.key == pygame.K_b:
                    # Alternar bombas de refrigerante
                    controller.sim.core.toggle_coolant_pumps()

                elif event.key == pygame.K_p:
                    # Pausar / reanudar
                    controller.is_paused = not controller.is_paused

                elif event.key == pygame.K_r:
                    # Reiniciar estado del nucleo
                    controller.reset_simulation()

                elif event.key == pygame.K_1:
                    controller.speed_multiplier = 1.0
                elif event.key == pygame.K_2:
                    controller.speed_multiplier = 2.0
                elif event.key == pygame.K_3:
                    controller.speed_multiplier = 4.0
                elif event.key == pygame.K_4:
                    controller.speed_multiplier = 8.0

        return True
