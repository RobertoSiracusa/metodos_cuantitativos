"""Renderizado procedural vectorial de clientes y carritos de compra en vista top-down."""

import math
import pygame
from src.constants import (
    CustomerState,
    CART_FRAME_COLOR,
    CART_BASKET_COLOR,
)


class CustomerDrawer:
    """Dibuja al cliente cenital con su carrito, articulos, silueta y badges de estado."""

    CART_LENGTH = 32
    CART_WIDTH = 22
    PERSON_RADIUS = 9

    @classmethod
    def draw_customer(cls, surface: pygame.Surface, customer, font: pygame.font.Font):
        """
        Renderiza al cliente y su carrito con orientacion angular exacta.
        surface: Lienzo Pygame
        customer: Instancia de Customer
        font: Tipografia para badges
        """
        total_len = cls.CART_LENGTH + 24
        total_w = cls.CART_WIDTH + 16

        entity_surf = pygame.Surface((total_len, total_w), pygame.SRCALPHA)
        center_x = total_len // 2
        center_y = total_w // 2

        # 1. Carrito de compras (ubicado al frente del cliente, hacia +x)
        cart_front_x = center_x + 10
        cart_rect = pygame.Rect(cart_front_x - cls.CART_LENGTH // 2, center_y - cls.CART_WIDTH // 2, cls.CART_LENGTH, cls.CART_WIDTH)

        # Malla metalica del carrito
        pygame.draw.rect(entity_surf, CART_BASKET_COLOR, cart_rect, border_radius=4)
        pygame.draw.rect(entity_surf, CART_FRAME_COLOR, cart_rect, width=2, border_radius=4)

        # Ruedas del carrito (4 ruedas en los extremos)
        wheel_col = (50, 55, 65)
        pygame.draw.circle(entity_surf, wheel_col, (cart_rect.left + 3, cart_rect.top - 1), 2)
        pygame.draw.circle(entity_surf, wheel_col, (cart_rect.left + 3, cart_rect.bottom + 1), 2)
        pygame.draw.circle(entity_surf, wheel_col, (cart_rect.right - 3, cart_rect.top - 1), 2)
        pygame.draw.circle(entity_surf, wheel_col, (cart_rect.right - 3, cart_rect.bottom + 1), 2)

        # Barra / manillar de agarre del carrito
        pygame.draw.line(
            entity_surf,
            (70, 80, 95),
            (cart_rect.left, cart_rect.top + 2),
            (cart_rect.left, cart_rect.bottom - 2),
            3,
        )

        # 2. Articulos visibles dentro de la cesta del carrito
        # Se muestran hasta 8 cuadritos de colores representativos
        visible_items = min(8, customer.items_remaining)
        for idx in range(visible_items):
            col = customer.item_colors[idx % len(customer.item_colors)]
            ix = cart_rect.left + 5 + (idx % 4) * 6
            iy = cart_rect.top + 4 + (idx // 4) * 7
            pygame.draw.rect(entity_surf, col, (ix, iy, 5, 5), border_radius=1)

        # 3. Brazos sujetando el manillar
        person_x = center_x - 12
        person_y = center_y
        arm_col = customer.skin_color
        # Brazo izquierdo
        pygame.draw.line(entity_surf, arm_col, (person_x + 4, person_y - 6), (cart_rect.left, person_y - 5), 3)
        # Brazo derecho
        pygame.draw.line(entity_surf, arm_col, (person_x + 4, person_y + 6), (cart_rect.left, person_y + 5), 3)

        # 4. Cuerpo y hombros del cliente (torso con franela de color)
        torso_rect = pygame.Rect(person_x - 7, person_y - 8, 14, 16)
        pygame.draw.rect(entity_surf, customer.shirt_color, torso_rect, border_radius=5)
        pygame.draw.rect(entity_surf, (30, 41, 59), torso_rect, width=1, border_radius=5)

        # 5. Cabeza y cabello
        pygame.draw.circle(entity_surf, customer.skin_color, (person_x, person_y), cls.PERSON_RADIUS)
        # Cabello superior
        pygame.draw.circle(entity_surf, customer.hair_color, (person_x - 2, person_y), cls.PERSON_RADIUS - 2)

        # Rotacion segun angulo del cliente
        # En pygame rotate es antihorario, compensamos con -angulo
        rotated_surf = pygame.transform.rotate(entity_surf, -customer.angle)
        new_rect = rotated_surf.get_rect(center=(int(customer.x), int(customer.y)))
        surface.blit(rotated_surf, new_rect)

        # 6. Insignia flotante con cantidad de articulos o estado
        if customer.state in (CustomerState.QUEUED, CustomerState.AT_CHECKOUT, CustomerState.SCANNING):
            badge_text = f"{customer.items_remaining}"
            badge_surf = font.render(badge_text, True, (255, 255, 255))
            bw = max(18, badge_surf.get_width() + 6)
            bh = 14
            bx = int(customer.x - bw // 2)
            by = int(customer.y - 24)

            # Fondo del badge
            bg_col = (37, 99, 235) if customer.state == CustomerState.QUEUED else (234, 179, 8)
            if customer.state == CustomerState.SCANNING:
                bg_col = (239, 68, 68)

            pygame.draw.rect(surface, bg_col, (bx, by, bw, bh), border_radius=4)
            pygame.draw.rect(surface, (255, 255, 255), (bx, by, bw, bh), width=1, border_radius=4)
            surface.blit(badge_surf, (bx + (bw - badge_surf.get_width()) // 2, by + 1))
