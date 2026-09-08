"""Renderizado de los camiones con rotacion 2D, estados e indicadores de carga."""

from typing import Dict, List
import pygame

from src.constants import (
    COLOR_TEXT_MAIN,
    COLOR_TEXT_WARNING,
    TruckState,
)
from src.models.truck import Truck


class TruckView:
    """Renderiza la flota de camiones de manera cinemática y orientada en Pygame."""

    def __init__(self, fonts: Dict[str, pygame.font.Font]):
        self.fonts = fonts
        # Cache de plantillas de dibujo para los tipos de camiones
        self._sprite_cache: Dict[str, pygame.Surface] = {}

    def draw_fleet(self, surface: pygame.Surface, trucks: List[Truck]):
        """Dibuja todos los camiones activos en la superficie."""
        for truck in trucks:
            self._draw_truck(surface, truck)

    def _draw_truck(self, surface: pygame.Surface, truck: Truck):
        """Dibuja un camion individual rotado y con su etiqueta de telemetria."""
        # 1. Dimensiones del chasis segun tipo
        width = 30
        height = 16
        color_theme = truck.truck_type.color

        # 2. Construir superficie base horizontal centrada
        truck_surf = pygame.Surface((width, height), pygame.SRCALPHA)

        # Chasis/Remolque (Cuerpo trasero)
        trailer_rect = pygame.Rect(2, 2, 18, 12)
        pygame.draw.rect(truck_surf, (40, 50, 65), trailer_rect, border_radius=2)
        pygame.draw.rect(truck_surf, color_theme, trailer_rect, width=1, border_radius=2)

        # Barra indicadora de nivel de carga dentro del remolque
        if truck.current_cargo_tons > 0 and truck.capacity_tons > 0:
            fill_ratio = min(1.0, truck.current_cargo_tons / truck.capacity_tons)
            cargo_w = int(14 * fill_ratio)
            if cargo_w > 0:
                pygame.draw.rect(truck_surf, color_theme, (4, 4, cargo_w, 8), border_radius=1)

        # Cabina frontal
        cab_rect = pygame.Rect(20, 2, 8, 12)
        pygame.draw.rect(truck_surf, color_theme, cab_rect, border_radius=2)

        # Parabrisas delantero
        pygame.draw.rect(truck_surf, (224, 242, 254), (24, 4, 3, 8), border_radius=1)

        # Ruedas laterales
        wheel_color = (15, 23, 42)
        pygame.draw.rect(truck_surf, wheel_color, (5, 0, 4, 2))
        pygame.draw.rect(truck_surf, wheel_color, (14, 0, 4, 2))
        pygame.draw.rect(truck_surf, wheel_color, (21, 0, 4, 2))
        pygame.draw.rect(truck_surf, wheel_color, (5, 14, 4, 2))
        pygame.draw.rect(truck_surf, wheel_color, (14, 14, 4, 2))
        pygame.draw.rect(truck_surf, wheel_color, (21, 14, 4, 2))

        # 3. Rotar la superficie segun el angulo cinemático del camion
        # En Pygame el eje Y crece hacia abajo, por lo que el angulo se invierte
        rotated_surf = pygame.transform.rotate(truck_surf, -truck.angle)
        new_rect = rotated_surf.get_rect(center=(int(truck.x), int(truck.y)))

        # Sombra proyectada
        shadow_rect = new_rect.copy()
        shadow_rect.y += 3
        pygame.draw.ellipse(surface, (10, 15, 20), shadow_rect)

        # Estampar camion rotado
        surface.blit(rotated_surf, new_rect.topleft)

        # 4. Etiqueta flotante superior con ID y estado
        font_tiny = self.fonts.get("tiny", pygame.font.SysFont("Arial", 10))
        label_text = f"C-0{truck.id}"

        # Color de estado
        if truck.state == TruckState.EN_RUTA:
            status_tag = f"{label_text} [{truck.current_cargo_tons:.0f}t]"
            status_col = COLOR_TEXT_MAIN
        elif truck.state in (TruckState.CARGANDO, TruckState.DESCARGANDO):
            status_tag = f"{label_text} ({truck.state.value})"
            status_col = COLOR_TEXT_WARNING
        elif truck.state == TruckState.EN_TRANSITO_ORIGEN:
            status_tag = f"{label_text} -> Orig"
            status_col = (147, 197, 253)
        else:
            status_tag = f"{label_text} (Libre)"
            status_col = (148, 163, 184)

        lbl_surf = font_tiny.render(status_tag, True, status_col)
        badge_rect = pygame.Rect(
            int(truck.x - lbl_surf.get_width() / 2 - 3),
            int(truck.y - 22),
            lbl_surf.get_width() + 6,
            lbl_surf.get_height() + 2,
        )
        pygame.draw.rect(surface, (15, 23, 42), badge_rect, border_radius=3)
        pygame.draw.rect(surface, (51, 65, 85), badge_rect, width=1, border_radius=3)
        surface.blit(lbl_surf, (badge_rect.x + 3, badge_rect.y + 1))
