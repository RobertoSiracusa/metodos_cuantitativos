"""Renderizado cenital (top-down) del entorno fisico del automercado."""

import pygame
from src.constants import (
    SIM_WIDTH,
    WINDOW_HEIGHT,
    COLOR_FLOOR,
    COLOR_FLOOR_GRID,
    COLOR_WALL,
    COLOR_ENTRANCE,
    COLOR_SHELF_BODY,
    COLOR_SHELF_BORDER,
    COLOR_SHELF_GREEN,
    COLOR_SHELF_RED,
    COLOR_SHELF_BLUE,
    COLOR_SHELF_ORANGE,
    COLOR_SHELF_PURPLE,
    COLOR_SHELF_YELLOW,
    COLOR_REGISTER_BODY,
    COLOR_BELT,
    COLOR_SCANNER_ON,
    COLOR_SCANNER_OFF,
    COLOR_CASHIER_UNIFORM,
    COLOR_STATUS_FREE,
    COLOR_STATUS_BUSY,
    COLOR_STATUS_CLOSED,
    COLOR_STANCHION_POST,
    COLOR_STANCHION_BELT,
    CheckoutState,
    QueueMode,
    CustomerState,
    CHECKOUT_POSITIONS,
    ENTRANCE_DOOR,
    CART_STATION,
    SINGLE_QUEUE_HEAD,
    EXIT_TURNSTILES,
    EXIT_DOOR,
)
from src.view.customer_drawer import CustomerDrawer


class MarketView:
    """Gestiona el renderizado de pasillos, cajas, barreras de cola y clientes."""

    def __init__(self, fonts: dict):
        self.fonts = fonts

    def update_and_render(self, surface: pygame.Surface, sim, dt: float):
        """
        Actualiza posiciones cinematicas y dibuja toda la planta del automercado.
        surface: Lienzo Pygame
        sim: Instancia de MarketSimulation
        dt: Delta de tiempo real en segundos
        """
        # 1. Baldosas del piso del automercado
        self._draw_floor(surface)

        # 2. Entrada, estacion de carritos y puerta
        self._draw_entrance_and_carts(surface)

        # 3. Pasillos de gondolas de mercancia
        self._draw_shelves(surface)

        # 4. Delimitadores y postes guia de cola (segun disciplina activa)
        self._draw_queue_guides(surface, sim)

        # 5. Bateria de cajas registradoras
        self._draw_checkouts(surface, sim.checkouts)

        # 6. Zona de salida y molinetes
        self._draw_exit_area(surface)

        # 7. Actualizar y renderizar todos los clientes
        self._update_and_draw_customers(surface, sim, dt)

    def _draw_floor(self, surface: pygame.Surface):
        """Piso con cuadricula de baldosas pulidas claras."""
        floor_rect = pygame.Rect(0, 0, SIM_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(surface, COLOR_FLOOR, floor_rect)

        tile_size = 40
        for x in range(0, SIM_WIDTH, tile_size):
            pygame.draw.line(surface, COLOR_FLOOR_GRID, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, tile_size):
            pygame.draw.line(surface, COLOR_FLOOR_GRID, (0, y), (SIM_WIDTH, y), 1)

        # Muros perimetrales
        pygame.draw.line(surface, COLOR_WALL, (0, 0), (SIM_WIDTH, 0), 4)
        pygame.draw.line(surface, COLOR_WALL, (0, 0), (0, WINDOW_HEIGHT), 4)
        pygame.draw.line(surface, COLOR_WALL, (0, WINDOW_HEIGHT - 1), (SIM_WIDTH, WINDOW_HEIGHT - 1), 4)

    def _draw_entrance_and_carts(self, surface: pygame.Surface):
        """Puerta corrediza y bahia de carritos de compras."""
        # Alfombra de bienvenida
        mat_rect = pygame.Rect(10, 50, 80, 70)
        pygame.draw.rect(surface, (203, 213, 225), mat_rect, border_radius=6)
        pygame.draw.rect(surface, (148, 163, 184), mat_rect, width=2, border_radius=6)

        lbl_in = self.fonts["tiny"].render("ENTRADA >>", True, (30, 41, 59))
        surface.blit(lbl_in, (18, 55))

        # Bahia de carritos apilados
        bay_rect = pygame.Rect(30, 130, 60, 90)
        pygame.draw.rect(surface, (226, 232, 240), bay_rect, border_radius=4)
        pygame.draw.rect(surface, (148, 163, 184), bay_rect, width=1, border_radius=4)
        lbl_carts = self.fonts["tiny"].render("CARROS", True, (71, 85, 105))
        surface.blit(lbl_carts, (36, 135))

        # Carritos apilados esquematicos
        for y_stack in range(155, 210, 14):
            pygame.draw.rect(surface, (148, 163, 184), (40, y_stack, 40, 8), border_radius=2)
            pygame.draw.line(surface, (100, 116, 139), (40, y_stack), (80, y_stack), 1)

    def _draw_shelves(self, surface: pygame.Surface):
        """Gondolas con departamentos comerciales (Frutas, Carnes, etc.)."""
        shelves = [
            # (x, y, w, h, color, titulo)
            (150, 60, 200, 55, COLOR_SHELF_GREEN, "1. Frutas y Verduras"),
            (410, 60, 200, 55, COLOR_SHELF_ORANGE, "2. Abarrotes y Granos"),
            (670, 60, 200, 55, COLOR_SHELF_YELLOW, "3. Panaderia y Dulces"),
            (150, 175, 200, 55, COLOR_SHELF_RED, "4. Carnes y Embutidos"),
            (410, 175, 200, 55, COLOR_SHELF_BLUE, "5. Lacteos y Quesos"),
            (670, 175, 200, 55, COLOR_SHELF_PURPLE, "6. Bebidas y Licores"),
        ]

        for sx, sy, sw, sh, color, title in shelves:
            # Cuerpo de la estanteria
            shelf_rect = pygame.Rect(sx, sy, sw, sh)
            pygame.draw.rect(surface, COLOR_SHELF_BODY, shelf_rect, border_radius=6)
            pygame.draw.rect(surface, COLOR_SHELF_BORDER, shelf_rect, width=2, border_radius=6)

            # Barra superior de color del departamento
            top_bar = pygame.Rect(sx + 2, sy + 2, sw - 4, 14)
            pygame.draw.rect(surface, color, top_bar, border_radius=4)

            # Titulo del pasillo
            txt = self.fonts["tiny"].render(title, True, (255, 255, 255))
            surface.blit(txt, (sx + 8, sy + 3))

            # Mercancia en estanteria (lineas de productos)
            for iy in (sy + 22, sy + 36):
                pygame.draw.line(surface, (148, 163, 184), (sx + 8, iy), (sx + sw - 8, iy), 3)

    def _draw_queue_guides(self, surface: pygame.Surface, sim):
        """Demarcacion de cola segun el modo (Cola Unica o Colas Multiples)."""
        if sim.queue_mode == QueueMode.SINGLE:
            # Poste y cartel de Cola Unica
            hx, hy = SINGLE_QUEUE_HEAD
            post_rect = pygame.Rect(hx - 40, hy - 140, 80, 22)
            pygame.draw.rect(surface, (37, 99, 235), post_rect, border_radius=4)
            lbl = self.fonts["tiny"].render("FILA UNICA", True, (255, 255, 255))
            surface.blit(lbl, (hx - 32, hy - 136))

            # Cintas guia de espera (tensabarrier)
            guide_x = hx + 18
            for y_line in range(hy - 110, hy + 20, 30):
                pygame.draw.circle(surface, COLOR_STANCHION_POST, (guide_x, y_line), 4)
                pygame.draw.line(surface, COLOR_STANCHION_BELT, (guide_x, y_line), (guide_x, y_line + 24), 2)
        else:
            # Guias divisorias entre cajas
            for counter in sim.checkouts:
                if counter.is_active:
                    cx = counter.x
                    cy = counter.y
                    # Linea discontinua de acceso a la caja
                    for y_pt in range(cy - 120, cy - 25, 20):
                        pygame.draw.line(surface, (180, 195, 210), (cx - 15, y_pt), (cx - 15, y_pt + 10), 2)

    def _draw_checkouts(self, surface: pygame.Surface, checkouts):
        """Dibuja las cajas registradoras, cintas, escaner, cajero y luz de estado."""
        for counter in checkouts:
            cx, cy = counter.x, counter.y

            # 1. Mueble de caja (estacion)
            desk_rect = pygame.Rect(cx - 32, cy - 10, 64, 110)
            pygame.draw.rect(surface, COLOR_REGISTER_BODY, desk_rect, border_radius=6)
            pygame.draw.rect(surface, (15, 23, 42), desk_rect, width=2, border_radius=6)

            # 2. Cinta transportadora
            belt_rect = pygame.Rect(cx - 24, cy - 2, 24, 75)
            pygame.draw.rect(surface, COLOR_BELT, belt_rect, border_radius=2)

            # Articulos sobre la cinta en movimiento
            if counter.items_on_belt:
                for idx, col in enumerate(counter.items_on_belt[:5]):
                    ix = belt_rect.left + 5 + (idx % 2) * 8
                    iy = belt_rect.top + 6 + idx * 12
                    pygame.draw.rect(surface, col, (ix, iy, 6, 6), border_radius=1)

            # 3. Escaner laser
            scanner_rect = pygame.Rect(cx - 26, cy + 50, 28, 6)
            scanner_col = COLOR_SCANNER_ON if counter.scanner_active else COLOR_SCANNER_OFF
            pygame.draw.rect(surface, scanner_col, scanner_rect)
            if counter.scanner_active:
                # Luz de haz laser
                pygame.draw.line(surface, (255, 100, 100), (cx - 24, cy + 53), (cx + 2, cy + 53), 2)

            # 4. Cajero / Operador (vista cenital)
            cashier_x = cx + 16
            cashier_y = cy + 45
            if counter.is_active:
                # Hombros
                pygame.draw.circle(surface, COLOR_CASHIER_UNIFORM, (cashier_x, cashier_y), 9)
                # Cabeza
                pygame.draw.circle(surface, (245, 195, 150), (cashier_x, cashier_y), 6)
                pygame.draw.circle(surface, (30, 41, 59), (cashier_x, cashier_y - 2), 4)

            # 5. Monitor / Terminal POS
            pos_rect = pygame.Rect(cx + 4, cy + 20, 12, 10)
            pygame.draw.rect(surface, (56, 189, 248), pos_rect, border_radius=2)

            # 6. Poste con luz LED de estado y numero de caja
            pole_x = cx
            pole_y = cy - 22
            status_col = COLOR_STATUS_CLOSED
            if counter.is_active:
                status_col = COLOR_STATUS_BUSY if counter.state == CheckoutState.BUSY else COLOR_STATUS_FREE

            # Luz LED redonda
            pygame.draw.circle(surface, status_col, (pole_x, pole_y), 8)
            pygame.draw.circle(surface, (255, 255, 255), (pole_x, pole_y), 3)

            # Etiqueta de la caja
            c_label = f"C{counter.id}"
            if counter.is_express:
                c_label += " (EXP)"
            lbl_c = self.fonts["tiny"].render(c_label, True, (15, 23, 42))
            surface.blit(lbl_c, (cx - 20, cy - 36))

    def _draw_exit_area(self, surface: pygame.Surface):
        """Zona de molinetes de salida y pasillo de escape."""
        # Molinetes
        turnstile_rect = pygame.Rect(120, 640, 680, 20)
        pygame.draw.rect(surface, (226, 232, 240), turnstile_rect, border_radius=4)
        pygame.draw.rect(surface, (148, 163, 184), turnstile_rect, width=1, border_radius=4)

        # Letrero de Salida
        out_txt = self.fonts["small"].render("SALIDA >>", True, (71, 85, 105))
        surface.blit(out_txt, (720, 670))

    def _update_and_draw_customers(self, surface: pygame.Surface, sim, dt: float):
        """Actualiza la cinemática de los clientes y los renderiza en pantalla."""
        # Actualizar cinemática de todos los clientes activos
        all_customers = list(sim.customers_in_store)

        for customer in all_customers:
            customer.update_motion(dt)
            CustomerDrawer.draw_customer(surface, customer, self.fonts["tiny"])
