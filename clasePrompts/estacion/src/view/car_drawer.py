"""Dibujado procedural vectorial de vehiculos en vista cenital (top-down)."""

import math
import pygame
from src.constants import VehicleState


class CarDrawer:
    """Renderiza vehiculos orientados con sombras, ruedas, parabrisas y luces."""

    CAR_LENGTH = 44
    CAR_WIDTH = 24

    @classmethod
    def draw_car(cls, surface: pygame.Surface, vehicle, font: pygame.font.Font):
        """
        Dibuja un vehiculo con su orientacion angular exacta y efectos de estado.
        """
        # Crear superficie para el vehiculo con canal alfa
        car_surf = pygame.Surface((cls.CAR_LENGTH + 12, cls.CAR_WIDTH + 12), pygame.SRCALPHA)
        center_x = (cls.CAR_LENGTH + 12) // 2
        center_y = (cls.CAR_WIDTH + 12) // 2

        # 1. Ruedas (4 neumaticos)
        wheel_w, wheel_h = 9, 4
        wheel_color = (20, 20, 24)
        # Delanteras
        pygame.draw.rect(car_surf, wheel_color, (center_x + 10, center_y - 12, wheel_w, wheel_h), border_radius=1)
        pygame.draw.rect(car_surf, wheel_color, (center_x + 10, center_y + 8, wheel_w, wheel_h), border_radius=1)
        # Traseras
        pygame.draw.rect(car_surf, wheel_color, (center_x - 17, center_y - 12, wheel_w, wheel_h), border_radius=1)
        pygame.draw.rect(car_surf, wheel_color, (center_x - 17, center_y + 8, wheel_w, wheel_h), border_radius=1)

        # 2. Carroceria principal
        body_rect = pygame.Rect(center_x - cls.CAR_LENGTH // 2, center_y - cls.CAR_WIDTH // 2, cls.CAR_LENGTH, cls.CAR_WIDTH)
        pygame.draw.rect(car_surf, vehicle.color, body_rect, border_radius=6)
        pygame.draw.rect(car_surf, (20, 20, 25), body_rect, width=1, border_radius=6)

        # 3. Luces delanteras (faros) y traseras
        pygame.draw.circle(car_surf, (255, 255, 200), (center_x + cls.CAR_LENGTH // 2 - 2, center_y - 7), 2)
        pygame.draw.circle(car_surf, (255, 255, 200), (center_x + cls.CAR_LENGTH // 2 - 2, center_y + 7), 2)
        pygame.draw.rect(car_surf, (220, 38, 38), (center_x - cls.CAR_LENGTH // 2 + 1, center_y - 8, 2, 4))
        pygame.draw.rect(car_surf, (220, 38, 38), (center_x - cls.CAR_LENGTH // 2 + 1, center_y + 4, 2, 4))

        # 4. Cabina / Techo y parabrisas
        windshield_color = (30, 45, 60)
        # Parabrisas frontal
        pygame.draw.polygon(car_surf, windshield_color, [
            (center_x + 3, center_y - 7),
            (center_x + 9, center_y - 6),
            (center_x + 9, center_y + 6),
            (center_x + 3, center_y + 7)
        ])
        # Parabrisas trasero
        pygame.draw.polygon(car_surf, windshield_color, [
            (center_x - 12, center_y - 6),
            (center_x - 7, center_y - 7),
            (center_x - 7, center_y + 7),
            (center_x - 12, center_y + 6)
        ])
        # Techo
        roof_rect = pygame.Rect(center_x - 8, center_y - 6, 12, 12)
        roof_color = (max(0, vehicle.color[0] - 25), max(0, vehicle.color[1] - 25), max(0, vehicle.color[2] - 25))
        pygame.draw.rect(car_surf, roof_color, roof_rect, border_radius=2)

        # Rotacion segun angulo del vehiculo (pygame rota en sentido antihorario con signo opuesto)
        rotated_surf = pygame.transform.rotate(car_surf, -vehicle.angle)
        new_rect = rotated_surf.get_rect(center=(int(vehicle.x), int(vehicle.y)))
        surface.blit(rotated_surf, new_rect)

        # 5. Indicador flotante superior si esta cargando gasolina
        if vehicle.state == VehicleState.FUELING:
            # Barra de recarga sobre el vehiculo
            bar_w = 36
            bar_h = 5
            bar_x = int(vehicle.x - bar_w / 2)
            bar_y = int(vehicle.y - 28)
            prog = min(1.0, vehicle.fuel_dispensed / max(1.0, vehicle.fuel_requested))

            pygame.draw.rect(surface, (20, 24, 30), (bar_x, bar_y, bar_w, bar_h), border_radius=2)
            pygame.draw.rect(surface, (34, 197, 94), (bar_x, bar_y, int(bar_w * prog), bar_h), border_radius=2)
            pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), width=1, border_radius=2)
