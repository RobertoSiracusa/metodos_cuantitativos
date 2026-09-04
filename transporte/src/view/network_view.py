"""Renderizado grafico de la red de carreteras, nodos y trazado de rutas en Pygame."""

import math
from typing import Dict, List, Optional
import pygame

from src.constants import (
    COLOR_BG,
    COLOR_GRID,
    COLOR_NODE_CITY,
    COLOR_NODE_CROSS,
    COLOR_NODE_HUB,
    COLOR_NODE_SELECTED_DEST,
    COLOR_NODE_SELECTED_ORIGIN,
    COLOR_ROAD_BG,
    COLOR_ROAD_BORDER,
    COLOR_ROAD_DASH,
    COLOR_ROAD_LABEL_BG,
    COLOR_ROUTE_ALT,
    COLOR_ROUTE_OPTIMAL,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    SIM_WIDTH,
    WINDOW_HEIGHT,
)
from src.models.graph import Edge, Node, TransportGraph
from src.models.pathfinding import PathResult


class NetworkView:
    """Gestiona el dibujo estético del grafo vial, vias y nodos en el lienzo de simulacion."""

    def __init__(self, fonts: Dict[str, pygame.font.Font]):
        self.fonts = fonts

    def draw(
        self,
        surface: pygame.Surface,
        graph: TransportGraph,
        selected_origin: Optional[Node],
        selected_dest: Optional[Node],
        optimal_path: Optional[PathResult],
        alt_path: Optional[PathResult] = None,
    ):
        """Renderiza la totalidad de la red en la superficie del simulador."""
        # 1. Fondo de asfalto y cuadricula ingenieril
        surface.fill(COLOR_BG, (0, 0, SIM_WIDTH, WINDOW_HEIGHT))
        self._draw_grid(surface)

        # 2. Carreteras base
        self._draw_roads(surface, graph.edges)

        # 3. Resaltado de ruta alternativa (suboptima de contraste)
        if alt_path and alt_path.found and len(alt_path.edges) > 0:
            self._draw_path_highlight(surface, alt_path.edges, COLOR_ROUTE_ALT, width=4, is_alt=True)

        # 4. Resaltado de la ruta optima (Dijkstra / A*)
        if optimal_path and optimal_path.found and len(optimal_path.edges) > 0:
            self._draw_path_highlight(surface, optimal_path.edges, COLOR_ROUTE_OPTIMAL, width=6, is_alt=False)

        # 5. Nodos, halos y rotulacion de ciudades
        self._draw_nodes(surface, graph.nodes.values(), selected_origin, selected_dest)

    def _draw_grid(self, surface: pygame.Surface):
        """Dibuja una cuadricula suave de referencia logistica."""
        grid_size = 50
        for x in range(0, SIM_WIDTH, grid_size):
            pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, grid_size):
            pygame.draw.line(surface, COLOR_GRID, (0, y), (SIM_WIDTH, y), 1)

    def _draw_roads(self, surface: pygame.Surface, edges: List[Edge]):
        """Dibuja las calzadas y sus etiquetas de distancia."""
        drawn_pairs = set()

        for edge in edges:
            pair = tuple(sorted([edge.source.id, edge.target.id]))
            if pair in drawn_pairs:
                continue
            drawn_pairs.add(pair)

            u = edge.source
            v = edge.target

            # Calzada base ancha
            pygame.draw.line(surface, COLOR_ROAD_BORDER, (int(u.x), int(u.y)), (int(v.x), int(v.y)), 10)
            pygame.draw.line(surface, COLOR_ROAD_BG, (int(u.x), int(u.y)), (int(v.x), int(v.y)), 6)

            # Linea discontinua central
            self._draw_dashed_line(surface, COLOR_ROAD_DASH, (u.x, u.y), (v.x, v.y), dash_length=8, space_length=6)

            # Etiqueta de kilometraje al centro del tramo
            mx = (u.x + v.x) / 2.0
            my = (u.y + v.y) / 2.0
            self._draw_badge(surface, f"{edge.distance_km:.0f} km", mx, my)

    def _draw_dashed_line(
        self,
        surface: pygame.Surface,
        color: tuple,
        start_pos: tuple,
        end_pos: tuple,
        dash_length: float = 8.0,
        space_length: float = 6.0,
    ):
        """Traza una linea con patron discontinuo."""
        x1, y1 = start_pos
        x2, y2 = end_pos
        dist = math.hypot(x2 - x1, y2 - y1)
        if dist == 0:
            return

        dx = (x2 - x1) / dist
        dy = (y2 - y1) / dist

        curr = 0.0
        while curr < dist:
            seg_end = min(curr + dash_length, dist)
            p1 = (x1 + dx * curr, y1 + dy * curr)
            p2 = (x1 + dx * seg_end, y1 + dy * seg_end)
            pygame.draw.line(surface, color, p1, p2, 1)
            curr += dash_length + space_length

    def _draw_badge(self, surface: pygame.Surface, text: str, x: float, y: float):
        """Dibuja una pequeña chapa informativa en las carreteras."""
        font = self.fonts.get("tiny", pygame.font.SysFont("Arial", 10))
        txt_surf = font.render(text, True, COLOR_TEXT_MUTED)
        padding_x = 4
        padding_y = 2
        rect = pygame.Rect(
            int(x - txt_surf.get_width() / 2 - padding_x),
            int(y - txt_surf.get_height() / 2 - padding_y),
            txt_surf.get_width() + padding_x * 2,
            txt_surf.get_height() + padding_y * 2,
        )
        pygame.draw.rect(surface, COLOR_ROAD_LABEL_BG, rect, border_radius=3)
        pygame.draw.rect(surface, COLOR_ROAD_BORDER, rect, width=1, border_radius=3)
        surface.blit(txt_surf, (rect.x + padding_x, rect.y + padding_y))

    def _draw_path_highlight(
        self,
        surface: pygame.Surface,
        edges: List[Edge],
        color: tuple,
        width: int = 5,
        is_alt: bool = False,
    ):
        """Resalta la secuencia de aristas que componen la ruta calculada."""
        for edge in edges:
            u, v = edge.source, edge.target
            # Resplandor exterior
            glow_color = (color[0], color[1], color[2])
            pygame.draw.line(surface, glow_color, (int(u.x), int(u.y)), (int(v.x), int(v.y)), width + 4)
            # Nucleo
            pygame.draw.line(surface, (255, 255, 255) if not is_alt else color, (int(u.x), int(u.y)), (int(v.x), int(v.y)), width - 1)

            # Flecha de flujo orientada en el sentido u -> v
            self._draw_arrow(surface, (u.x, u.y), (v.x, v.y), color)

    def _draw_arrow(self, surface: pygame.Surface, p1: tuple, p2: tuple, color: tuple):
        """Dibuja una flecha indicadora del sentido de circulacion sobre el tramo."""
        mx = (p1[0] + p2[0]) / 2.0
        my = (p1[1] + p2[1]) / 2.0

        angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
        arrow_size = 8

        # Puntos del triangulo de la flecha
        left_angle = angle + math.pi * 0.82
        right_angle = angle - math.pi * 0.82

        tip = (mx + math.cos(angle) * 4, my + math.sin(angle) * 4)
        p_left = (tip[0] + math.cos(left_angle) * arrow_size, tip[1] + math.sin(left_angle) * arrow_size)
        p_right = (tip[0] + math.cos(right_angle) * arrow_size, tip[1] + math.sin(right_angle) * arrow_size)

        pygame.draw.polygon(surface, color, [tip, p_left, p_right])

    def _draw_nodes(
        self,
        surface: pygame.Surface,
        nodes: List[Node],
        selected_origin: Optional[Node],
        selected_dest: Optional[Node],
    ):
        """Renderiza los vertices logisticos con sus halos de seleccion y tipografia."""
        font_bold = self.fonts.get("bold", pygame.font.SysFont("Arial", 12, bold=True))
        font_small = self.fonts.get("small", pygame.font.SysFont("Arial", 11))

        for node in nodes:
            is_origin = selected_origin and selected_origin.id == node.id
            is_dest = selected_dest and selected_dest.id == node.id

            # Halos de seleccion interactiva
            if is_origin:
                pygame.draw.circle(surface, COLOR_NODE_SELECTED_ORIGIN, (int(node.x), int(node.y)), 24, width=3)
            elif is_dest:
                pygame.draw.circle(surface, COLOR_NODE_SELECTED_DEST, (int(node.x), int(node.y)), 24, width=3)

            # Color del cuerpo segun categoria funcional
            if node.node_type == "HUB":
                base_color = COLOR_NODE_HUB
                radius = 16
            elif node.node_type == "CITY":
                base_color = COLOR_NODE_CITY
                radius = 13
            else:
                base_color = COLOR_NODE_CROSS
                radius = 10

            # Sombra y disco principal
            pygame.draw.circle(surface, (15, 23, 42), (int(node.x), int(node.y) + 2), radius)
            pygame.draw.circle(surface, base_color, (int(node.x), int(node.y)), radius)
            pygame.draw.circle(surface, COLOR_TEXT_MAIN, (int(node.x), int(node.y)), radius, width=2)

            # Letra o icono interior identificador
            char_tag = "H" if node.node_type == "HUB" else ("C" if node.node_type == "CITY" else "X")
            tag_surf = font_bold.render(char_tag, True, (255, 255, 255))
            surface.blit(
                tag_surf,
                (node.x - tag_surf.get_width() / 2, node.y - tag_surf.get_height() / 2),
            )

            # Rotulacion de nombre y etiquetas de demanda/oferta
            lbl_surf = font_bold.render(f"[{node.id}] {node.name}", True, COLOR_TEXT_MAIN)
            surface.blit(lbl_surf, (node.x - lbl_surf.get_width() / 2, node.y + radius + 4))

            # Subtitulo con datos de demanda o capacidad
            if node.node_type == "HUB":
                sub_txt = f"Oferta: {node.supply:.0f}t"
                sub_col = (147, 197, 253)
            elif node.node_type == "CITY":
                sub_txt = f"Demanda: {node.remaining_demand:.0f}t"
                sub_col = (110, 231, 183)
            else:
                sub_txt = "Peaje / Enlace"
                sub_col = COLOR_TEXT_MUTED

            sub_surf = font_small.render(sub_txt, True, sub_col)
            surface.blit(sub_surf, (node.x - sub_surf.get_width() / 2, node.y + radius + 19))
