"""
Componentes Visuales Reutilizables (Botones, Tarjetas, Banners)
Capa de Presentacion — Metodos Cuantitativos
Universidad Jose Antonio Paez
"""

import time
from typing import Optional, Tuple
import pygame

from src.gui.styles import (
    COLOR_CARD_BG,
    COLOR_CARD_BORDER,
    COLOR_TEXT_WHITE,
    COLOR_TEXT_DIM,
)


class Button:
    """Boton interactivo con deteccion de hover y personalizacion visual."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        bg_color: Tuple[int, int, int],
        text_color: Tuple[int, int, int] = COLOR_TEXT_WHITE,
        border_color: Optional[Tuple[int, int, int]] = None,
        border_width: int = 1,
        border_radius: int = 6,
    ):
        self.rect = rect
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        self.hover = False

    def check_hover(self, mouse_pos: Tuple[int, int]) -> bool:
        self.hover = self.rect.collidepoint(mouse_pos)
        return self.hover

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        if self.hover:
            fill_color = tuple(min(255, c + 25) for c in self.bg_color)
            b_color = tuple(min(255, c + 20) for c in (self.border_color or COLOR_CARD_BORDER))
        else:
            fill_color = self.bg_color
            b_color = self.border_color or COLOR_CARD_BORDER

        pygame.draw.rect(surface, fill_color, self.rect, border_radius=self.border_radius)
        if self.border_width > 0:
            pygame.draw.rect(surface, b_color, self.rect, self.border_width, border_radius=self.border_radius)

        txt_surf = font.render(self.text, True, self.text_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)


class Card:
    """Contenedor rectangular estilizado para agrupar metricas de telemetria."""

    def __init__(
        self,
        rect: pygame.Rect,
        bg_color: Tuple[int, int, int] = COLOR_CARD_BG,
        border_color: Tuple[int, int, int] = COLOR_CARD_BORDER,
        border_radius: int = 8,
    ):
        self.rect = rect
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_radius = border_radius

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, self.border_color, self.rect, 1, border_radius=self.border_radius)


class BannerNotification:
    """Banner informativo temporal en la base de la pantalla."""

    def __init__(self):
        self.texto = ""
        self.expira = 0.0

    def set_mensaje(self, texto: str, duracion: float = 4.0) -> None:
        self.texto = texto
        self.expira = time.time() + duracion

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, x: int, y: int, max_width: int) -> None:
        if not self.texto or time.time() > self.expira:
            return

        txt_surf = font.render(self.texto, True, (253, 224, 71))  # Amarillo informativo
        pad = 8
        rect_bg = pygame.Rect(x, y, min(max_width, txt_surf.get_width() + (pad * 2)), txt_surf.get_height() + (pad * 2))
        pygame.draw.rect(surface, (30, 41, 59), rect_bg, border_radius=6)
        pygame.draw.rect(surface, (71, 85, 105), rect_bg, 1, border_radius=6)
        surface.blit(txt_surf, (x + pad, y + pad))
