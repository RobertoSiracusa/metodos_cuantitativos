"""
Renderizador Visual de la Topologia de Red a 60 FPS
Capa de Presentacion — Metodos Cuantitativos
Universidad Jose Antonio Paez
"""

import math
from typing import Dict, List, Tuple
import pygame

from src.core.network_entities import PacketState, RouterNode
from src.services.simulation_service import NetworkSimulation
from src.gui.styles import (
    COLOR_BG,
    COLOR_NET_GRID,
    COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_DIM,
    COLOR_BUF_GREEN,
    COLOR_BUF_YELLOW,
    COLOR_BUF_RED,
    COLOR_SOURCE_NODE,
    COLOR_DEST_NODE,
    COLOR_LINK_ACTIVE,
    COLOR_LINK_HIGHLIGHT,
    COLOR_LINK_BROKEN,
)


class NetworkRenderer:
    """Renderiza canvas de topologia, enlaces, routers condicionales y paquetes animados."""

    def __init__(self):
        self.font_small = pygame.font.SysFont("Segoe UI", 11)
        self.font_node = pygame.font.SysFont("Segoe UI", 12, bold=True)
        self.font_label = pygame.font.SysFont("Segoe UI", 13, bold=True)
        self.anim_phase = 0.0

    def update_animation(self, dt: float) -> None:
        """Avanza la fase de animacion sinusoidal para efectos visuales."""
        self.anim_phase = (self.anim_phase + (dt * 3.5)) % (math.pi * 2)

    def draw_network(self, surface: pygame.Surface, sim: NetworkSimulation, net_w: int, net_h: int) -> None:
        """Dibuja todos los componentes de la red en la zona izquierda de la pantalla."""
        canvas_rect = pygame.Rect(0, 0, net_w, net_h)
        surface.fill(COLOR_BG, canvas_rect)

        self._draw_grid(surface, net_w, net_h)
        self._draw_links(surface, sim)
        self._draw_packets(surface, sim)
        self._draw_nodes(surface, sim)

    def _draw_grid(self, surface: pygame.Surface, w: int, h: int) -> None:
        step = 45
        for x in range(0, w, step):
            pygame.draw.line(surface, COLOR_NET_GRID, (x, 0), (x, h), 1)
        for y in range(0, h, step):
            pygame.draw.line(surface, COLOR_NET_GRID, (0, y), (w, y), 1)

    def _draw_links(self, surface: pygame.Surface, sim: NetworkSimulation) -> None:
        todos_enlaces = list(sim.ingress_links.values()) + list(sim.egress_links.values())

        for link in todos_enlaces:
            x1 = sim._get_node_x(link.from_node_id)
            y1 = sim._get_node_y(link.from_node_id)
            x2 = sim._get_node_x(link.to_node_id)
            y2 = sim._get_node_y(link.to_node_id)

            if not link.active:
                color = COLOR_LINK_BROKEN
                ancho = 2
                self._draw_dashed_line(surface, color, (x1, y1), (x2, y2), width=ancho)
            else:
                tiene_flujo = len(link.packets_in_transit) > 0
                color = COLOR_LINK_HIGHLIGHT if tiene_flujo else COLOR_LINK_ACTIVE
                ancho = 2 if tiene_flujo else 1
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), ancho)

            # Etiqueta de latencia en punto medio
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            txt_lat = f"{link.current_latency_ms:.0f}ms" if link.active else "CAIDO"
            color_txt = (248, 113, 113) if not link.active else COLOR_TEXT_DIM
            lbl_surf = self.font_small.render(txt_lat, True, color_txt)
            surface.blit(lbl_surf, (mid_x - 12, mid_y - 8))

    def _draw_dashed_line(self, surface: pygame.Surface, color, p1, p2, width=1, dash_len=6) -> None:
        x1, y1 = p1
        x2, y2 = p2
        dist = math.hypot(x2 - x1, y2 - y1)
        if dist == 0:
            return
        dashes = int(dist / dash_len)
        dx = (x2 - x1) / dist
        dy = (y2 - y1) / dist

        for i in range(0, dashes, 2):
            s_x = x1 + dx * i * dash_len
            s_y = y1 + dy * i * dash_len
            e_x = x1 + dx * min(dist, (i + 1) * dash_len)
            e_y = y1 + dy * min(dist, (i + 1) * dash_len)
            pygame.draw.line(surface, color, (s_x, s_y), (e_x, e_y), width)

    def _draw_packets(self, surface: pygame.Surface, sim: NetworkSimulation) -> None:
        todos_enlaces = list(sim.ingress_links.values()) + list(sim.egress_links.values())

        for link in todos_enlaces:
            for pkt in link.packets_in_transit:
                x1, y1 = pkt.start_pos
                x2, y2 = pkt.end_pos
                prog = min(1.0, max(0.0, pkt.progress))

                cur_x = x1 + (x2 - x1) * prog
                cur_y = y1 + (y2 - y1) * prog

                # Particula luminosa con halo
                pygame.draw.circle(surface, (103, 232, 249), (int(cur_x), int(cur_y)), 5)
                pygame.draw.circle(surface, (255, 255, 255), (int(cur_x), int(cur_y)), 2)

    def _draw_nodes(self, surface: pygame.Surface, sim: NetworkSimulation) -> None:
        # Fuentes (S1, S2, S3)
        for s in sim.sources:
            x, y = int(s["x"]), int(s["y"])
            pygame.draw.circle(surface, COLOR_SOURCE_NODE, (x, y), 24)
            pygame.draw.circle(surface, (15, 23, 42), (x, y), 20)
            txt = self.font_node.render(s["id"], True, COLOR_TEXT_WHITE)
            surface.blit(txt, txt.get_rect(center=(x, y)))
            lbl = self.font_small.render(s["name"].split(" ")[0], True, COLOR_TEXT_MUTED)
            surface.blit(lbl, (x - 22, y + 26))

        # Routers Intermedios (R1, R2, R3, R4) con color condicional
        for r_id, r in sim.routers.items():
            x, y = int(r.x), int(r.y)
            sat = r.saturation_ratio

            # Color condicional requerido por el enunciado:
            # Verde < 50%, Amarillo 50%-80%, Rojo > 80%
            if sat < 0.50:
                color_nodo = COLOR_BUF_GREEN
            elif sat <= 0.80:
                color_nodo = COLOR_BUF_YELLOW
            else:
                color_nodo = COLOR_BUF_RED

            # Halo reactivo cuando esta congestionado (> 80%)
            if sat > 0.80:
                pulso = int(28 + 4 * math.sin(self.anim_phase))
                pygame.draw.circle(surface, (127, 29, 29), (x, y), pulso, 2)

            pygame.draw.circle(surface, color_nodo, (x, y), 26)
            pygame.draw.circle(surface, (15, 23, 42), (x, y), 22)

            txt = self.font_node.render(r_id, True, COLOR_TEXT_WHITE)
            surface.blit(txt, txt.get_rect(center=(x, y)))

            # Texto de ocupacion de buffer: q / S
            txt_q = f"{r.queue_length}/{r.capacidad_s}"
            lbl_q = self.font_small.render(txt_q, True, color_nodo)
            surface.blit(lbl_q, lbl_q.get_rect(center=(x, y + 34)))

        # Destinos (D1, D2)
        for d in sim.destinations:
            x, y = int(d["x"]), int(d["y"])
            pygame.draw.circle(surface, COLOR_DEST_NODE, (x, y), 24)
            pygame.draw.circle(surface, (15, 23, 42), (x, y), 20)
            txt = self.font_node.render(d["id"], True, COLOR_TEXT_WHITE)
            surface.blit(txt, txt.get_rect(center=(x, y)))
            lbl = self.font_small.render(d["name"].split(" ")[0], True, COLOR_TEXT_MUTED)
            surface.blit(lbl, (x - 22, y + 26))
