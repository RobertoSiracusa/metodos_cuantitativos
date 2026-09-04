"""Manejador de eventos de entrada y mapeo de teclas."""

from typing import Optional
import pygame

from ..constants import Direction


class InputHandler:
    """Traduce eventos de Pygame en comandos de la simulacion y direccion de la serpiente."""

    @staticmethod
    def process_event(event: pygame.event.Event) -> dict:
        """
        Procesa un evento individual de Pygame.
        Retorna un diccionario con las acciones detectadas.
        """
        action = {
            "quit": False,
            "direction": None,
            "toggle_pause": False,
            "toggle_mode": False,
            "reset": False,
            "speed": None,
        }

        if event.type == pygame.QUIT:
            action["quit"] = True
            return action

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                action["quit"] = True
            elif event.key == pygame.K_SPACE:
                action["toggle_pause"] = True
            elif event.key == pygame.K_m:
                action["toggle_mode"] = True
            elif event.key == pygame.K_r:
                action["reset"] = True
            elif event.key in (pygame.K_1, pygame.K_KP1):
                action["speed"] = 1.0
            elif event.key in (pygame.K_2, pygame.K_KP2):
                action["speed"] = 2.0
            elif event.key in (pygame.K_3, pygame.K_KP3):
                action["speed"] = 4.0
            # Direcciones de movimiento
            elif event.key in (pygame.K_UP, pygame.K_w):
                action["direction"] = Direction.UP
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                action["direction"] = Direction.DOWN
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                action["direction"] = Direction.LEFT
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                action["direction"] = Direction.RIGHT

        return action
