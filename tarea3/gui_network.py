"""
gui_network.py
==============================================================================
Interfaz Gráfica y Dashboard Telemetría con Pygame
Facultad de Ingeniería - Universidad José Antonio Páez
Cátedra: Métodos Cuantitativos y Simulación

Renderiza la topología de red de computadoras en tiempo real:
- Soporte para Pantalla Completa dinámica (F11) y modo ventana adaptable.
- Nodos circulares con color condicional según saturación de buffer:
  * Verde: < 50%
  * Amarillo: 50% - 80%
  * Rojo: > 80%
- Enlaces de comunicación dinámicos con latencia y estado operativo/caído.
- Paquetes animados transitando en tiempo real por los enlaces con estela.
- Dashboard lateral HUD con estadísticas detalladas, explicaciones físicas,
  insignias de estado (badges) y conversiones en milisegundos.
- Controles interactivos en pantalla y teclado.
==============================================================================
"""

import math
import time
from typing import Dict, List, Optional, Tuple
import pygame

from red_simulacion import NetworkSimulation, PacketState, Packet, RouterNode


# ==============================================================================
# DIMENSIONES BASE Y PALETA DE COLORES (SLATE & NEON AESTHETICS)
# ==============================================================================
SCREEN_WIDTH = 1260
SCREEN_HEIGHT = 740
NET_VIEW_WIDTH = 850
HUD_WIDTH = SCREEN_WIDTH - NET_VIEW_WIDTH

# Paleta Slate 900 Moderna
COLOR_BG = (15, 23, 42)              # Fondo principal (Slate 900)
COLOR_NET_GRID = (24, 34, 53)        # Rejilla sutil de la topología
COLOR_HUD_BG = (18, 28, 48)          # Fondo del panel lateral
COLOR_CARD_BG = (30, 41, 59)         # Tarjetas de telemetría (Slate 800)
COLOR_CARD_BORDER = (51, 65, 85)     # Bordes (Slate 700)

COLOR_TEXT_WHITE = (255, 255, 255)       # Blanco puro de máximo contraste
COLOR_TEXT_MUTED = (226, 232, 240)       # Slate 200 de muy alta legibilidad (> 8.5:1 contraste)
COLOR_TEXT_DIM = (160, 174, 192)         # Slate 400 secundario
COLOR_TEXT_CYAN = (103, 232, 249)        # Cian 300 brillante y nítido
COLOR_TEXT_GOLD = (253, 224, 71)         # Oro 300 brillante

# Estados de buffer requeridos por el enunciado (versiones vivas de alto contraste)
COLOR_BUF_GREEN = (74, 222, 128)         # Verde Esmeralda (< 50% saturación)
COLOR_BUF_YELLOW = (250, 204, 21)        # Amarillo Ámbar (50% - 80% saturación)
COLOR_BUF_RED = (248, 113, 113)          # Rojo Coral (> 80% saturación)

COLOR_SOURCE_NODE = (56, 189, 248)       # Nodos de Origen (Cian brillante)
COLOR_DEST_NODE = (192, 132, 252)        # Nodos de Destino (Púrpura claro)
COLOR_LINK_ACTIVE = (80, 95, 120)        # Enlaces normales bien visibles
COLOR_LINK_HIGHLIGHT = (56, 189, 248)    # Enlace con flujo activo (Cian luminoso)
COLOR_LINK_BROKEN = (248, 113, 113)      # Enlace caído (Rojo)

# Colores para Insignias (Badges) con legibilidad y contraste reforzados
BADGE_GREEN_BG = (20, 83, 45)
BADGE_GREEN_TXT = (187, 247, 208)        # Verde muy claro (Legibilidad óptima)
BADGE_YELLOW_BG = (113, 63, 18)
BADGE_YELLOW_TXT = (254, 240, 138)       # Amarillo muy claro
BADGE_RED_BG = (127, 29, 29)
BADGE_RED_TXT = (254, 202, 202)          # Rojo muy claro
BADGE_BLUE_BG = (30, 58, 138)
BADGE_BLUE_TXT = (219, 234, 254)         # Azul muy claro


class Button:
    """Botón interactivo para la interfaz de usuario en Pygame."""
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        bg_color: Tuple[int, int, int],
        text_color: Tuple[int, int, int] = COLOR_TEXT_WHITE,
        border_color: Optional[Tuple[int, int, int]] = None,
        border_width: int = 1,
        border_radius: int = 6
    ):
        self.rect = rect
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        self.hover = False

    def check_hover(self, mouse_pos: Tuple[int, int]):
        self.hover = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        if self.hover:
            color = tuple(min(255, c + 28) for c in self.bg_color)
            b_color = tuple(min(255, c + 25) for c in (self.border_color or COLOR_CARD_BORDER))
        else:
            color = self.bg_color
            b_color = self.border_color if self.border_color else COLOR_CARD_BORDER

        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, b_color, self.rect, width=self.border_width, border_radius=self.border_radius)

        txt_surf = font.render(self.text, True, self.text_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)


class NetworkRenderer:
    """Encargado del renderizado cinemático y geométrico de la red de computadoras."""

    def __init__(self):
        self.font_title = pygame.font.SysFont("segoeui,arial", 18, bold=True)
        self.font_node = pygame.font.SysFont("segoeui,arial", 14, bold=True)
        self.font_node_num = pygame.font.SysFont("segoeui,arial", 13, bold=True)
        self.font_sub = pygame.font.SysFont("segoeui,arial", 12, bold=True)
        self.anim_phase = 0.0

    def update_animation(self, dt: float):
        self.anim_phase = (self.anim_phase + dt * 4.0) % (2.0 * math.pi)

    def draw_network(self, surface: pygame.Surface, sim: NetworkSimulation, net_width: int, screen_height: int):
        # 1. Fondo y rejilla sutil adaptable
        pygame.draw.rect(surface, COLOR_BG, (0, 0, net_width, screen_height))
        for x in range(0, net_width, 40):
            pygame.draw.line(surface, COLOR_NET_GRID, (x, 0), (x, screen_height), 1)
        for y in range(0, screen_height, 40):
            pygame.draw.line(surface, COLOR_NET_GRID, (0, y), (net_width, y), 1)

        # 2. Título de la vista topológica
        title_surf = self.font_title.render("TOPOLOGÍA DE RED EN TIEMPO REAL (SimPy + Pygame)", True, COLOR_TEXT_WHITE)
        surface.blit(title_surf, (24, 18))
        sub_surf = self.font_sub.render("Fuentes Poisson (S) -> Routers Core (R) -> Gateways WAN Destino (D)", True, COLOR_TEXT_MUTED)
        surface.blit(sub_surf, (24, 44))

        # 3. Dibujar enlaces
        self._draw_links(surface, sim)

        # 4. Dibujar paquetes en tránsito con estela luminosa
        self._draw_packets(surface, sim)

        # 5. Dibujar nodos (Fuentes, Routers y Destinos)
        self._draw_nodes(surface, sim)

    def _draw_links(self, surface: pygame.Surface, sim: NetworkSimulation):
        """Dibuja las líneas de enlaces con visualización de estado."""
        todos_enlaces = list(sim.ingress_links.values()) + list(sim.egress_links.values())

        for link in todos_enlaces:
            x1 = sim._get_node_x(link.from_node_id)
            y1 = sim._get_node_y(link.from_node_id)
            x2 = sim._get_node_x(link.to_node_id)
            y2 = sim._get_node_y(link.to_node_id)

            if not link.active:
                # Enlace caído (rojo discontinuo bien visible)
                self._draw_dashed_line(surface, COLOR_LINK_BROKEN, (x1, y1), (x2, y2), width=3, dash_len=8)
                # Símbolo de falla en el centro del enlace
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                pygame.draw.circle(surface, COLOR_LINK_BROKEN, (int(mid_x), int(mid_y)), 12)
                x_font = self.font_node.render("X", True, COLOR_TEXT_WHITE)
                surface.blit(x_font, (int(mid_x) - x_font.get_width() // 2, int(mid_y) - x_font.get_height() // 2))
            else:
                # Enlace activo
                if len(link.packets_in_transit) > 0:
                    pygame.draw.line(surface, COLOR_LINK_HIGHLIGHT, (x1, y1), (x2, y2), 3)
                else:
                    pygame.draw.line(surface, COLOR_LINK_ACTIVE, (x1, y1), (x2, y2), 2)

    def _draw_dashed_line(self, surface, color, start_pos, end_pos, width=1, dash_len=8):
        x1, y1 = start_pos
        x2, y2 = end_pos
        dx = x2 - x1
        dy = y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        num_dashes = int(dist / (dash_len * 2))
        for i in range(num_dashes):
            s = (i * 2 * dash_len) / dist
            e = ((i * 2 + 1) * dash_len) / dist
            p1 = (x1 + dx * s, y1 + dy * s)
            p2 = (x1 + dx * e, y1 + dy * e)
            pygame.draw.line(surface, color, p1, p2, width)

    def _draw_packets(self, surface: pygame.Surface, sim: NetworkSimulation):
        """Renderiza paquetes animados que se desplazan sobre los enlaces con estela brillante."""
        todos_enlaces = list(sim.ingress_links.values()) + list(sim.egress_links.values())

        for link in todos_enlaces:
            for pkt in link.packets_in_transit:
                x1, y1 = pkt.start_pos
                x2, y2 = pkt.end_pos
                prog = min(1.0, max(0.0, pkt.progress))

                px = x1 + (x2 - x1) * prog
                py = y1 + (y2 - y1) * prog

                # Estela sutil que indica dirección del flujo de datos
                if prog > 0.05:
                    tail_prog = max(0.0, prog - 0.07)
                    tx = x1 + (x2 - x1) * tail_prog
                    ty = y1 + (y2 - y1) * tail_prog
                    pygame.draw.line(surface, (56, 189, 248), (int(tx), int(ty)), (int(px), int(py)), 3)

                # Círculo con halo de pulso y núcleo brillante
                glow_r = int(8 + math.sin(self.anim_phase + pkt.id) * 2)
                pygame.draw.circle(surface, (56, 189, 248, 90), (int(px), int(py)), glow_r)
                pygame.draw.circle(surface, (224, 242, 254), (int(px), int(py)), 5)
                pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), 2)

    def _draw_nodes(self, surface: pygame.Surface, sim: NetworkSimulation):
        """Renderiza los nodos con su código de color condicional según saturación."""
        # 1. Nodos de Origen (Fuentes)
        for s in sim.sources:
            nx, ny = int(s["x"]), int(s["y"])

            # Cartel rectangular superior tipo cartel/badge
            cartel_w, cartel_h = 66, 20
            cartel_rect = pygame.Rect(nx - cartel_w // 2, ny - 28 - cartel_h - 4, cartel_w, cartel_h)
            pygame.draw.rect(surface, (15, 28, 48), cartel_rect, border_radius=4)
            pygame.draw.rect(surface, COLOR_SOURCE_NODE, cartel_rect, width=1, border_radius=4)
            lbl_surf = self.font_sub.render("Fuente", True, COLOR_TEXT_CYAN)
            surface.blit(lbl_surf, lbl_surf.get_rect(center=cartel_rect.center))

            # Esfera del nodo Fuente con únicamente el identificador centrado
            pygame.draw.circle(surface, (20, 30, 48), (nx, ny), 28)
            pygame.draw.circle(surface, COLOR_SOURCE_NODE, (nx, ny), 26, width=3)
            id_surf = self.font_node.render(s["id"], True, COLOR_TEXT_WHITE)
            surface.blit(id_surf, id_surf.get_rect(center=(nx, ny)))

        # 2. Routers / Switches Intermedios
        for r_id, r_node in sim.routers.items():
            nx, ny = int(r_node.x), int(r_node.y)

            cat = r_node.status_color_category
            color_nodo = COLOR_BUF_GREEN if cat == "VERDE" else (COLOR_BUF_YELLOW if cat == "AMARILLO" else COLOR_BUF_RED)
            track_color = (20, 55, 35) if cat == "VERDE" else ((65, 52, 15) if cat == "AMARILLO" else (70, 25, 25))

            if cat == "ROJO":
                pulso = int(38 + math.sin(self.anim_phase * 2) * 4)
                pygame.draw.circle(surface, (239, 68, 68, 70), (nx, ny), pulso, width=2)

            # Fondo del interior del router
            pygame.draw.circle(surface, (24, 32, 50), (nx, ny), 30)

            # Trazado de rellenado de buffer ultra limpio y suave (anti-aliased)
            sat = r_node.saturation_ratio
            self._draw_smooth_ring(
                surface=surface,
                cx=nx,
                cy=ny,
                radius=31,
                width=5,
                progress=sat,
                active_color=color_nodo,
                track_color=track_color
            )

            id_surf = self.font_node.render(r_node.node_id, True, COLOR_TEXT_WHITE)
            surface.blit(id_surf, (nx - id_surf.get_width() // 2, ny - 18))

            q_text = f"{r_node.queue_length}/{r_node.capacidad_s}"
            q_surf = self.font_node_num.render(q_text, True, color_nodo)
            surface.blit(q_surf, (nx - q_surf.get_width() // 2, ny - 2))

            # Indicador tipo insignia de saturación de buffer
            badge_w, badge_h = 76, 18
            badge_rect = pygame.Rect(nx - badge_w // 2, ny + 35, badge_w, badge_h)
            pygame.draw.rect(surface, (20, 30, 48), badge_rect, border_radius=4)
            pygame.draw.rect(surface, (51, 65, 85), badge_rect, width=1, border_radius=4)
            pct_surf = self.font_sub.render(f"Buffer {sat * 100:.0f}%", True, COLOR_TEXT_MUTED)
            surface.blit(pct_surf, pct_surf.get_rect(center=badge_rect.center))

        # 3. Nodos de Destino (Redes WAN)
        for d in sim.destinations:
            nx, ny = int(d["x"]), int(d["y"])

            # Cartel rectangular superior tipo cartel/badge
            cartel_w, cartel_h = 76, 20
            cartel_rect = pygame.Rect(nx - cartel_w // 2, ny - 28 - cartel_h - 4, cartel_w, cartel_h)
            pygame.draw.rect(surface, (28, 20, 48), cartel_rect, border_radius=4)
            pygame.draw.rect(surface, COLOR_DEST_NODE, cartel_rect, width=1, border_radius=4)
            lbl_surf = self.font_sub.render("Red WAN", True, (216, 180, 254))
            surface.blit(lbl_surf, lbl_surf.get_rect(center=cartel_rect.center))

            # Esfera del nodo WAN con únicamente el identificador centrado
            pygame.draw.circle(surface, (20, 30, 48), (nx, ny), 28)
            pygame.draw.circle(surface, COLOR_DEST_NODE, (nx, ny), 26, width=3)
            id_surf = self.font_node.render(d["id"], True, COLOR_TEXT_WHITE)
            surface.blit(id_surf, id_surf.get_rect(center=(nx, ny)))

    def _draw_smooth_ring(
        self,
        surface: pygame.Surface,
        cx: int,
        cy: int,
        radius: int,
        width: int,
        progress: float,
        active_color: Tuple[int, int, int],
        track_color: Tuple[int, int, int]
    ):
        """
        Dibuja un anillo de progreso circular ultra limpio, nítido y anti-aliased (2x supersampling).
        Inicia en las 12 en punto (-pi/2) y avanza en sentido horario según la saturación del buffer.
        """
        scale = 2
        size = int((radius + width + 4) * 2)
        sub_size = size * scale
        sub_surf = pygame.Surface((sub_size, sub_size), pygame.SRCALPHA)

        sub_cx = sub_size // 2
        sub_cy = sub_size // 2
        sub_r = radius * scale
        sub_w = width * scale

        # 1. Pista completa perimetral del buffer (100% capacidad S)
        pygame.draw.circle(sub_surf, track_color, (sub_cx, sub_cy), sub_r, width=sub_w)

        # 2. Trazo de rellenado activo de buffer según saturación
        if progress > 0.005:
            prog = min(1.0, max(0.0, progress))
            num_steps = max(16, int(80 * prog))
            start_angle = -math.pi / 2  # 12 o'clock
            end_angle = start_angle + (2 * math.pi * prog)

            r_inner = sub_r - sub_w / 2
            r_outer = sub_r + sub_w / 2

            points_outer = []
            points_inner = []
            for i in range(num_steps + 1):
                theta = start_angle + (end_angle - start_angle) * (i / num_steps)
                points_outer.append((sub_cx + r_outer * math.cos(theta), sub_cy + r_outer * math.sin(theta)))
                points_inner.append((sub_cx + r_inner * math.cos(theta), sub_cy + r_inner * math.sin(theta)))

            poly_points = points_outer + points_inner[::-1]
            pygame.draw.polygon(sub_surf, active_color, poly_points)

            # Extremos redondeados para acabado limpio y suave
            p_start = (sub_cx + sub_r * math.cos(start_angle), sub_cy + sub_r * math.sin(start_angle))
            p_end = (sub_cx + sub_r * math.cos(end_angle), sub_cy + sub_r * math.sin(end_angle))
            cap_r = int(sub_w / 2)
            pygame.draw.circle(sub_surf, active_color, (int(p_start[0]), int(p_start[1])), cap_r)
            pygame.draw.circle(sub_surf, active_color, (int(p_end[0]), int(p_end[1])), cap_r)

        # Escalar con filtro bicúbico anti-aliased
        scaled_surf = pygame.transform.smoothscale(sub_surf, (size, size))
        surface.blit(scaled_surf, (cx - size // 2, cy - size // 2))


class NetworkDashboard:
    """
    Dashboard lateral (HUD) con estadísticas comprensibles, explicaciones físicas,
    insignias de estado y controles interactivos responsivos.
    """

    def __init__(self, x_offset: int, width: int = HUD_WIDTH, height: int = SCREEN_HEIGHT):
        self.x = x_offset
        self.w = width
        self.h = height

        # Tipografías jerárquicas con pesos optimizados para máxima legibilidad
        self.font_h1 = pygame.font.SysFont("segoeui,arial", 16, bold=True)
        self.font_h2 = pygame.font.SysFont("segoeui,arial", 13, bold=True)
        self.font_val = pygame.font.SysFont("segoeui,arial", 14, bold=True)
        self.font_lbl = pygame.font.SysFont("segoeui,arial", 12, bold=True)
        self.font_sub = pygame.font.SysFont("segoeui,arial", 11, bold=False)  # Sin cursiva fina, nítido y legible
        self.font_badge = pygame.font.SysFont("segoeui,arial", 11, bold=True)
        self.font_btn = pygame.font.SysFont("segoeui,arial", 12, bold=True)
        self.font_small = pygame.font.SysFont("segoeui,arial", 11, bold=True)

        self._crear_botones()

        self.banner_mensaje = ""
        self.banner_timer = 0.0

    def actualizar_dimensiones(self, x_offset: int, width: int, height: int):
        """Reconfigura la geometría del HUD para adaptarse a cualquier resolución o pantalla completa."""
        self.x = x_offset
        self.w = width
        self.h = height
        self._crear_botones()

    def _crear_botones(self):
        """Crea o reubica los botones según el ancho y alto del HUD actual."""
        card_w = self.w - 28
        bw = 50
        bh = 27
        # Botones llamativos de ajuste de tráfico y estabilidad en amarillo oscuro (ámbar) de alto contraste
        btn_amber_bg = (185, 130, 15)
        btn_amber_txt = (15, 23, 42)
        btn_amber_border = (245, 195, 40)
        self.btn_lam_down = Button(pygame.Rect(self.x + card_w - 108, 52 + 46, bw, bh), "- λ", btn_amber_bg, btn_amber_txt, border_color=btn_amber_border, border_width=1)
        self.btn_lam_up = Button(pygame.Rect(self.x + card_w - 52, 52 + 46, bw, bh), "+ λ", btn_amber_bg, btn_amber_txt, border_color=btn_amber_border, border_width=1)
        self.btn_mu_down = Button(pygame.Rect(self.x + card_w - 108, 52 + 75, bw, bh), "- μ", btn_amber_bg, btn_amber_txt, border_color=btn_amber_border, border_width=1)
        self.btn_mu_up = Button(pygame.Rect(self.x + card_w - 52, 52 + 75, bw, bh), "+ μ", btn_amber_bg, btn_amber_txt, border_color=btn_amber_border, border_width=1)

        # Botones de acciones principales
        btn_y1 = max(666, self.h - 78)
        btn_y2 = max(700, self.h - 42)

        # Fila de acciones principales
        col_w = (self.w - 36) // 4
        self.btn_pause = Button(pygame.Rect(self.x + 14, btn_y1, col_w - 4, 30), "Pausar", (79, 70, 229))
        self.btn_toggle_link = Button(pygame.Rect(self.x + 14 + col_w, btn_y1, col_w - 4, 30), "Caída (F1)", (225, 29, 72))
        self.btn_export = Button(pygame.Rect(self.x + 14 + col_w * 2, btn_y1, col_w - 4, 30), "Reporte (E)", (16, 185, 129))
        self.btn_fullscreen = Button(pygame.Rect(self.x + 14 + col_w * 3, btn_y1, col_w - 4, 30), "Expandir (F11)", (14, 165, 233))

        # Fila de velocidades (0.25x a 4x) y Reinicio
        sw = (self.w - 36 - 96) // 5
        self.btn_speed_025x = Button(pygame.Rect(self.x + 14, btn_y2, sw - 4, 26), "0.25x", (30, 41, 59))
        self.btn_speed_05x = Button(pygame.Rect(self.x + 14 + sw, btn_y2, sw - 4, 26), "0.5x", (30, 41, 59))
        self.btn_speed_1x = Button(pygame.Rect(self.x + 14 + sw * 2, btn_y2, sw - 4, 26), "1x", (30, 41, 59))
        self.btn_speed_2x = Button(pygame.Rect(self.x + 14 + sw * 3, btn_y2, sw - 4, 26), "2x", (30, 41, 59))
        self.btn_speed_4x = Button(pygame.Rect(self.x + 14 + sw * 4, btn_y2, sw - 4, 26), "4x", (30, 41, 59))
        self.btn_reset = Button(pygame.Rect(self.x + self.w - 14 - 92, btn_y2, 92, 26), "Reiniciar (R)", (71, 85, 105))

    def set_banner(self, mensaje: str, duracion: float = 4.0):
        self.banner_mensaje = mensaje
        self.banner_timer = duracion

    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        if self.banner_timer > 0:
            self.banner_timer -= dt

        botones = [
            self.btn_lam_down, self.btn_lam_up, self.btn_mu_down, self.btn_mu_up,
            self.btn_pause, self.btn_toggle_link, self.btn_export, self.btn_fullscreen,
            self.btn_speed_025x, self.btn_speed_05x, self.btn_speed_1x,
            self.btn_speed_2x, self.btn_speed_4x, self.btn_reset
        ]
        for b in botones:
            b.check_hover(mouse_pos)

    def draw(
        self,
        surface: pygame.Surface,
        sim: NetworkSimulation,
        is_paused: bool,
        sim_speed: float,
        is_fullscreen: bool = False
    ):
        # 1. Fondo del HUD
        pygame.draw.rect(surface, COLOR_HUD_BG, (self.x, 0, self.w, self.h))
        pygame.draw.line(surface, COLOR_CARD_BORDER, (self.x, 0), (self.x, self.h), 1)

        # 2. Cabecera Institucional
        h1_surf = self.font_h1.render("TELEMETRÍA Y CONTROL DE RED", True, COLOR_TEXT_WHITE)
        surface.blit(h1_surf, (self.x + 16, 12))
        h2_surf = self.font_small.render("Facultad de Ingeniería - UJAP | Métodos Cuantitativos", True, COLOR_TEXT_CYAN)
        surface.blit(h2_surf, (self.x + 16, 32))

        metricas = sim.obtener_metricas_completas()

        card_w = self.w - 28
        col_split = self.x + int(card_w * 0.52)

        # ----------------------------------------------------------------------
        # TARJETA 1: PARÁMETROS ESTOCÁSTICOS Y ESTABILIDAD
        # ----------------------------------------------------------------------
        card1_y = 52
        card1_h = 132
        self._draw_card(surface, pygame.Rect(self.x + 14, card1_y, card_w, card1_h), "1. PARÁMETROS DE TRÁFICO Y ESTABILIDAD")

        t_sim = metricas["tiempo_simulacion_s"]
        lam_val = metricas["lambda"]
        mu_val = metricas["mu"]
        rho_val = metricas["factor_utilizacion_rho"]

        # Reloj e Indicador de Estabilidad
        self._draw_metric_row(surface, self.x + 20, card1_y + 24, "Reloj Simulación:", f"{t_sim:.1f} s", COLOR_TEXT_WHITE)
        es_estable = rho_val < 1.0
        badge_txt = "ESTABLE (λ < c·μ)" if es_estable else "INESTABLE (λ ≥ c·μ)"
        badge_bg = BADGE_GREEN_BG if es_estable else BADGE_RED_BG
        badge_fg = BADGE_GREEN_TXT if es_estable else BADGE_RED_TXT
        self._draw_badge(surface, badge_txt, badge_bg, badge_fg, col_split, card1_y + 24)

        # Fila 2: Lambda con explicación y botones
        intervalo_ms = 1000.0 / max(0.1, lam_val)
        self._draw_metric_row(surface, self.x + 20, card1_y + 49, "Llegada (λ):", f"{lam_val:.1f} paq/s", COLOR_TEXT_WHITE)
        lam_sub_surf = self.font_sub.render(f"({intervalo_ms:.0f} ms/paq)", True, COLOR_TEXT_MUTED)
        sub_lam_x = min(self.x + 185, self.x + card_w - 116 - lam_sub_surf.get_width())
        surface.blit(lam_sub_surf, (sub_lam_x, card1_y + 51))

        # Botones lambda más grandes y llamativos
        self.btn_lam_down.rect.x = self.x + card_w - 108
        self.btn_lam_down.rect.y = card1_y + 46
        self.btn_lam_down.rect.w = 50
        self.btn_lam_down.rect.h = 27
        self.btn_lam_up.rect.x = self.x + card_w - 52
        self.btn_lam_up.rect.y = card1_y + 46
        self.btn_lam_up.rect.w = 50
        self.btn_lam_up.rect.h = 27
        self.btn_lam_down.draw(surface, self.font_btn)
        self.btn_lam_up.draw(surface, self.font_btn)

        # Fila 3: Mu con explicación y botones
        serv_ms = 1000.0 / max(0.1, mu_val)
        self._draw_metric_row(surface, self.x + 20, card1_y + 78, "Servicio (μ):", f"{mu_val:.1f} paq/s", COLOR_TEXT_WHITE)
        mu_sub_surf = self.font_sub.render(f"(~{serv_ms:.0f} ms/atención)", True, COLOR_TEXT_MUTED)
        sub_mu_x = min(self.x + 185, self.x + card_w - 116 - mu_sub_surf.get_width())
        surface.blit(mu_sub_surf, (sub_mu_x, card1_y + 80))

        # Botones mu más grandes y llamativos
        self.btn_mu_down.rect.x = self.x + card_w - 108
        self.btn_mu_down.rect.y = card1_y + 75
        self.btn_mu_down.rect.w = 50
        self.btn_mu_down.rect.h = 27
        self.btn_mu_up.rect.x = self.x + card_w - 52
        self.btn_mu_up.rect.y = card1_y + 75
        self.btn_mu_up.rect.w = 50
        self.btn_mu_up.rect.h = 27
        self.btn_mu_down.draw(surface, self.font_btn)
        self.btn_mu_up.draw(surface, self.font_btn)

        # Fila 4: Utilización (rho)
        self._draw_metric_row(surface, self.x + 20, card1_y + 104, "Ocupación CPU (ρ):", f"{rho_val * 100:.1f}%", COLOR_TEXT_CYAN)
        rho_badge = "FLUIDO (<50%)" if rho_val < 0.5 else ("MODERADO" if rho_val <= 0.8 else "CRÍTICO (>80%)")
        rho_bg = BADGE_GREEN_BG if rho_val < 0.5 else (BADGE_YELLOW_BG if rho_val <= 0.8 else BADGE_RED_BG)
        rho_fg = BADGE_GREEN_TXT if rho_val < 0.5 else (BADGE_YELLOW_TXT if rho_val <= 0.8 else BADGE_RED_TXT)
        self._draw_badge(surface, rho_badge, rho_bg, rho_fg, col_split, card1_y + 104)

        # ----------------------------------------------------------------------
        # TARJETA 2: TEORÍA DE LÍNEAS DE ESPERA (COLAS M/M/1/K)
        # ----------------------------------------------------------------------
        card2_y = card1_y + card1_h + 8
        card2_h = 148
        self._draw_card(surface, pygame.Rect(self.x + 14, card2_y, card_w, card2_h), "2. TEORÍA DE COLAS (SIGNIFICADO FÍSICO)")

        l_val = metricas["promedio_paquetes_sistema_l"]
        lq_val = metricas["promedio_paquetes_cola_lq"]
        w_val = metricas["tiempo_medio_sistema_w_s"]
        wq_val = metricas["tiempo_medio_cola_wq_s"]
        proc_val = metricas["paquetes_procesados"]
        drop_val = metricas["paquetes_perdidos"]
        loss_pct = metricas["tasa_perdida_pct"]

        # Fila A: Wq (Demora en cola) y W (Tránsito total)
        wq_ms = wq_val * 1000.0
        w_ms = w_val * 1000.0
        self._draw_metric_row(surface, self.x + 20, card2_y + 24, "Espera Cola (Wq):", f"{wq_ms:.1f} ms", COLOR_TEXT_WHITE)
        surface.blit(self.font_sub.render(f"Demora antes de atención ({wq_val:.4f} s)", True, COLOR_TEXT_MUTED), (self.x + 20, card2_y + 42))

        self._draw_metric_row(surface, col_split, card2_y + 24, "Viaje en Red (W):", f"{w_ms:.1f} ms", COLOR_TEXT_WHITE)
        surface.blit(self.font_sub.render(f"Tiempo total origen-destino ({w_val:.4f} s)", True, COLOR_TEXT_MUTED), (col_split, card2_y + 42))

        # Fila B: L (Paquetes en sistema) y Lq (Paquetes en cola)
        self._draw_metric_row(surface, self.x + 20, card2_y + 64, "En Sistema (L):", f"{l_val:.2f} paq", COLOR_TEXT_WHITE)
        surface.blit(self.font_sub.render("Promedio activos en red simultáneos", True, COLOR_TEXT_MUTED), (self.x + 20, card2_y + 82))

        self._draw_metric_row(surface, col_split, card2_y + 64, "En Espera (Lq):", f"{lq_val:.2f} paq", COLOR_TEXT_WHITE)
        surface.blit(self.font_sub.render("Promedio varados en cola de routers", True, COLOR_TEXT_MUTED), (col_split, card2_y + 82))

        # Fila C: Paquetes Procesados vs Pérdida por Overflow
        self._draw_metric_row(surface, self.x + 20, card2_y + 104, "Paquetes Entregados:", f"{proc_val}", COLOR_BUF_GREEN)
        self._draw_metric_row(surface, col_split, card2_y + 104, "Descartes Overflow:", f"{drop_val} ({loss_pct:.2f}%)", COLOR_BUF_RED if drop_val > 0 else COLOR_BUF_GREEN)

        loss_badge = "CERO PÉRDIDAS (100% Retención)" if drop_val == 0 else ("PÉRDIDA MODERADA" if loss_pct < 3.0 else "ALTA PÉRDIDA")
        l_bg = BADGE_GREEN_BG if drop_val == 0 else (BADGE_YELLOW_BG if loss_pct < 3.0 else BADGE_RED_BG)
        l_fg = BADGE_GREEN_TXT if drop_val == 0 else (BADGE_YELLOW_TXT if loss_pct < 3.0 else BADGE_RED_TXT)
        self._draw_badge(surface, loss_badge, l_bg, l_fg, self.x + 20, card2_y + 125)

        # ----------------------------------------------------------------------
        # TARJETA 3: GESTIÓN DE INVENTARIO Y BUFFERS (s, Q)
        # ----------------------------------------------------------------------
        card3_y = card2_y + card2_h + 8
        card3_h = 118
        self._draw_card(surface, pygame.Rect(self.x + 14, card3_y, card_w, card3_h), "3. GESTIÓN DE INVENTARIO EN BUFFERS (s, Q)")

        cap_s = metricas["capacidad_buffer_s"]
        umb_s = metricas["umbral_reabastecimiento_s"]
        lote_q = metricas["lote_q"]

        self._draw_metric_row(surface, self.x + 20, card3_y + 24, "Capacidad (S):", f"{cap_s} paq", COLOR_TEXT_WHITE)
        self._draw_metric_row(surface, self.x + int(card_w * 0.38), card3_y + 24, "Umbral (s):", f"{umb_s} paq", COLOR_TEXT_WHITE)
        self._draw_metric_row(surface, self.x + int(card_w * 0.70), card3_y + 24, "Lote (Q):", f"{lote_q} paq", COLOR_TEXT_CYAN)

        surface.blit(self.font_sub.render("Regla: Buffer < s emite crédito de flujo Q. Buffer = S descarta paquete.", True, COLOR_TEXT_MUTED), (self.x + 20, card3_y + 43))

        # Monitores individuales R1..R4
        r_y = card3_y + 62
        router_keys = list(sim.routers.keys())
        r_col_w = (card_w - 20) // max(1, len(router_keys))

        for i, r_id in enumerate(router_keys):
            r_node = sim.routers[r_id]
            rx = self.x + 20 + (i * r_col_w)
            cat = r_node.status_color_category
            color_stat = COLOR_BUF_GREEN if cat == "VERDE" else (COLOR_BUF_YELLOW if cat == "AMARILLO" else COLOR_BUF_RED)

            sat_pct = r_node.saturation_ratio * 100.0
            r_txt = f"{r_id}: {r_node.queue_length}/{r_node.capacidad_s}"
            surface.blit(self.font_lbl.render(r_txt, True, COLOR_TEXT_WHITE), (rx, r_y))
            surface.blit(self.font_sub.render(f"({sat_pct:.0f}%)", True, color_stat), (rx, r_y + 16))

            # Barra de buffer
            bw = r_col_w - 14
            fill_w = int(bw * r_node.saturation_ratio)
            pygame.draw.rect(surface, (51, 65, 85), (rx, r_y + 34, bw, 7), border_radius=3)
            if fill_w > 0:
                pygame.draw.rect(surface, color_stat, (rx, r_y + 34, fill_w, 7), border_radius=3)

        # ----------------------------------------------------------------------
        # TARJETA 4: EVALUACIÓN ECONÓMICA Y COSTOS DEL SISTEMA
        # ----------------------------------------------------------------------
        card4_y = card3_y + card3_h + 8
        card4_h = 92
        self._draw_card(surface, pygame.Rect(self.x + 14, card4_y, card_w, card4_h), "4. ANÁLISIS ECONÓMICO Y COSTOS ($)")

        c_alm = metricas["costo_almacenamiento_usd"]
        c_pen = metricas["costo_penalizacion_usd"]
        c_tot = metricas["costo_global_usd"]

        self._draw_metric_row(surface, self.x + 20, card4_y + 24, "Almacén (Ch):", f"${c_alm:.2f}", COLOR_TEXT_WHITE)
        surface.blit(self.font_sub.render("($0.05 / paq·s en RAM)", True, COLOR_TEXT_MUTED), (self.x + 20, card4_y + 42))

        self._draw_metric_row(surface, col_split + 15, card4_y + 24, "Penalización (Cs):", f"${c_pen:.2f}", COLOR_BUF_RED if c_pen > 0 else COLOR_TEXT_MUTED)
        surface.blit(self.font_sub.render("($10.00 / descarte)", True, COLOR_TEXT_MUTED), (col_split + 15, card4_y + 42))

        self._draw_metric_row(surface, self.x + 20, card4_y + 64, "Costo Global:", f"${c_tot:.2f} USD", COLOR_TEXT_GOLD)
        eff_badge = "100% EFICIENTE" if c_pen == 0 else "SOBRECOSTO POR ROTURA"
        eff_bg = BADGE_GREEN_BG if c_pen == 0 else BADGE_RED_BG
        eff_fg = BADGE_GREEN_TXT if c_pen == 0 else BADGE_RED_TXT
        self._draw_badge(surface, eff_badge, eff_bg, eff_fg, col_split + 15, card4_y + 64)

        # ----------------------------------------------------------------------
        # TARJETA 5: ASIGNACIÓN ÓPTIMA (ALGORITMO HÚNGARO)
        # ----------------------------------------------------------------------
        card5_y = card4_y + card4_h + 8
        card5_h = 82
        self._draw_card(surface, pygame.Rect(self.x + 14, card5_y, card_w, card5_h), "5. ENRUTAMIENTO ÓPTIMO (ALGORITMO HÚNGARO)")

        ultimo_h = sim.router_hungaro.ultimo_resultado
        if ultimo_h and ultimo_h.pares_asignados:
            h_str = " | ".join([f"S{f+1}->R{e+1}" for f, e in ultimo_h.pares_asignados[:3]])
            costo_h = f"{ultimo_h.costo_total:.1f} ms"
            metodo_h = ultimo_h.metodo_utilizado
        else:
            h_str = "Evaluando matriz C_ij..."
            costo_h = "0.0 ms"
            metodo_h = "SciPy"

        self._draw_metric_row(surface, self.x + 20, card5_y + 24, "Asignaciones:", h_str, COLOR_TEXT_WHITE)
        self._draw_metric_row(surface, self.x + 20, card5_y + 45, "Costo Enrutamiento:", costo_h, COLOR_TEXT_CYAN)
        surface.blit(self.font_sub.render(f"Fórmula: C_ij = Latencia + 40 × Saturación ({metodo_h[:18]})", True, COLOR_TEXT_MUTED), (self.x + 20, card5_y + 63))

        # ----------------------------------------------------------------------
        # BOTONES DE ACCIÓN Y CONTROL
        # ----------------------------------------------------------------------
        self.btn_pause.text = "Reanudar" if is_paused else "Pausar"
        self.btn_pause.draw(surface, self.font_btn)
        self.btn_toggle_link.draw(surface, self.font_btn)
        self.btn_export.draw(surface, self.font_btn)

        self.btn_fullscreen.text = "Restaurar (F11)" if is_fullscreen else "Expandir (F11)"
        self.btn_fullscreen.draw(surface, self.font_btn)

        # Botones de velocidad con resaltado visual activo
        self.btn_speed_025x.bg_color = (79, 70, 229) if sim_speed == 0.25 else (30, 41, 59)
        self.btn_speed_05x.bg_color = (79, 70, 229) if sim_speed == 0.5 else (30, 41, 59)
        self.btn_speed_1x.bg_color = (79, 70, 229) if sim_speed == 1.0 else (30, 41, 59)
        self.btn_speed_2x.bg_color = (79, 70, 229) if sim_speed == 2.0 else (30, 41, 59)
        self.btn_speed_4x.bg_color = (79, 70, 229) if sim_speed == 4.0 else (30, 41, 59)

        self.btn_speed_025x.draw(surface, self.font_btn)
        self.btn_speed_05x.draw(surface, self.font_btn)
        self.btn_speed_1x.draw(surface, self.font_btn)
        self.btn_speed_2x.draw(surface, self.font_btn)
        self.btn_speed_4x.draw(surface, self.font_btn)
        self.btn_reset.draw(surface, self.font_btn)

        # ----------------------------------------------------------------------
        # BANNER DE NOTIFICACIÓN (TOAST FLOTANTE EN VISTA DE RED)
        # ----------------------------------------------------------------------
        if self.banner_timer > 0 and self.banner_mensaje:
            toast_w = min(560, max(280, self.x - 40))
            toast_x = (self.x - toast_w) // 2
            toast_y = self.h - 48
            banner_rect = pygame.Rect(toast_x, toast_y, toast_w, 36)
            pygame.draw.rect(surface, (24, 34, 53), banner_rect, border_radius=8)
            pygame.draw.rect(surface, (16, 185, 129), banner_rect, width=2, border_radius=8)
            msg_surf = self.font_btn.render(self.banner_mensaje, True, COLOR_TEXT_WHITE)
            surface.blit(msg_surf, msg_surf.get_rect(center=banner_rect.center))

    def _draw_card(self, surface: pygame.Surface, rect: pygame.Rect, title: str):
        pygame.draw.rect(surface, COLOR_CARD_BG, rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_CARD_BORDER, rect, width=1, border_radius=8)
        title_surf = self.font_h2.render(title, True, COLOR_TEXT_CYAN)
        surface.blit(title_surf, (rect.x + 10, rect.y + 6))

    def _draw_metric_row(self, surface: pygame.Surface, x: int, y: int, label: str, value: str, val_color: Tuple[int, int, int]):
        lbl_surf = self.font_lbl.render(label, True, COLOR_TEXT_MUTED)
        surface.blit(lbl_surf, (x, y))
        val_surf = self.font_val.render(value, True, val_color)
        surface.blit(val_surf, (x + lbl_surf.get_width() + 6, y - 1))

    def _draw_badge(self, surface: pygame.Surface, text: str, bg_color: Tuple[int, int, int], text_color: Tuple[int, int, int], x: int, y: int) -> int:
        """Renderiza una insignia estilo pill con fondo redondeado y tipografía nítida."""
        txt_surf = self.font_badge.render(text, True, text_color)
        pad_x = 8
        pad_y = 3
        rect = pygame.Rect(x, y - 2, txt_surf.get_width() + pad_x * 2, txt_surf.get_height() + pad_y * 2)
        pygame.draw.rect(surface, bg_color, rect, border_radius=6)
        surface.blit(txt_surf, (x + pad_x, y + pad_y - 2))
        return rect.right
