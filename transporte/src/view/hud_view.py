"""Panel HUD lateral con telemetria, comparativas analiticas y controles interactivos."""

from typing import Dict, Optional
import pygame

from src.constants import (
    COLOR_HUD_BG,
    COLOR_HUD_BORDER,
    COLOR_HUD_CARD,
    COLOR_HUD_DIVIDER,
    COLOR_ROUTE_ALT,
    COLOR_ROUTE_OPTIMAL,
    COLOR_TEXT_ACCENT,
    COLOR_TEXT_DANGER,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_SUCCESS,
    COLOR_TEXT_WARNING,
    HUD_WIDTH,
    SIM_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from src.models.graph import Node
from src.models.pathfinding import PathResult
from src.simulation.transport_sim import TransportSimulation


class HudView:
    """Renderiza el tablero de control, métricas y analitica cuantitativa."""

    def __init__(self, fonts: Dict[str, pygame.font.Font]):
        self.fonts = fonts
        self.x_start = SIM_WIDTH
        self.width = HUD_WIDTH

    def draw(
        self,
        surface: pygame.Surface,
        sim: TransportSimulation,
        speed_multiplier: float,
        is_paused: bool,
    ):
        """Dibuja el panel lateral completo."""
        hud_rect = pygame.Rect(self.x_start, 0, self.width, WINDOW_HEIGHT)
        pygame.draw.rect(surface, COLOR_HUD_BG, hud_rect)
        pygame.draw.line(surface, COLOR_HUD_BORDER, (self.x_start, 0), (self.x_start, WINDOW_HEIGHT), 2)

        y_offset = 12

        # 1. Tarjeta de encabezado universitario
        y_offset = self._draw_header(surface, y_offset, sim, speed_multiplier, is_paused)

        # 2. Tarjeta de ruta optima y comparativa cuantitativa
        y_offset = self._draw_route_card(surface, y_offset, sim.selected_origin, sim.selected_dest, sim.preview_path, sim.preview_alt_path)

        # 3. Tarjeta de estado de la flota
        y_offset = self._draw_fleet_card(surface, y_offset, sim)

        # 4. Tarjeta de metricas acumuladas globales
        y_offset = self._draw_metrics_card(surface, y_offset, sim)

        # 5. Tarjeta de guia de comandos y atajos
        self._draw_controls_card(surface, y_offset)

    def _draw_card_box(self, surface: pygame.Surface, x: int, y: int, w: int, h: int) -> pygame.Rect:
        """Helper para dibujar el contenedor estilizado de una tarjeta."""
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, COLOR_HUD_CARD, rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_HUD_BORDER, rect, width=1, border_radius=6)
        return rect

    def _draw_header(
        self,
        surface: pygame.Surface,
        y: int,
        sim: TransportSimulation,
        speed: float,
        paused: bool,
    ) -> int:
        """Dibuja el banner superior del HUD."""
        font_title = self.fonts.get("title", pygame.font.SysFont("Arial", 14, bold=True))
        font_bold = self.fonts.get("bold", pygame.font.SysFont("Arial", 12, bold=True))
        font_tiny = self.fonts.get("tiny", pygame.font.SysFont("Arial", 10))

        h = 80
        self._draw_card_box(surface, self.x_start + 12, y, self.width - 24, h)

        # Titulo
        t1 = font_title.render("METODOS CUANTITATIVOS", True, COLOR_TEXT_ACCENT)
        surface.blit(t1, (self.x_start + 22, y + 8))

        t2 = font_bold.render("Asignacion de Flota & Rutas Optimas", True, COLOR_TEXT_MAIN)
        surface.blit(t2, (self.x_start + 22, y + 30))

        # Badges de estado (Velocidad, Pausa, Algoritmo)
        badge_x = self.x_start + 22
        badge_y = y + 54

        # Badge Algoritmo
        algo_name = sim.algorithm.upper()
        b_algo = font_tiny.render(f"Algoritmo: {algo_name}", True, (56, 189, 248))
        surface.blit(b_algo, (badge_x, badge_y))

        # Badge Velocidad
        b_speed = font_tiny.render(f"Vel: {speed:.0f}x", True, COLOR_TEXT_WARNING)
        surface.blit(b_speed, (badge_x + 130, badge_y))

        # Badge Estado simulacion
        status_txt = "PAUSADO" if paused else ("AUTO" if sim.auto_mode else "MANUAL")
        status_col = COLOR_TEXT_DANGER if paused else (COLOR_TEXT_SUCCESS if sim.auto_mode else COLOR_TEXT_MUTED)
        b_status = font_tiny.render(f"Modo: {status_txt}", True, status_col)
        surface.blit(b_status, (badge_x + 210, badge_y))

        return y + h + 10

    def _draw_route_card(
        self,
        surface: pygame.Surface,
        y: int,
        orig: Optional[Node],
        dest: Optional[Node],
        path: Optional[PathResult],
        alt_path: Optional[PathResult],
    ) -> int:
        """Dibuja el analisis cuantitativo de la ruta optima seleccionada."""
        font_bold = self.fonts.get("bold", pygame.font.SysFont("Arial", 12, bold=True))
        font_small = self.fonts.get("small", pygame.font.SysFont("Arial", 11))
        font_tiny = self.fonts.get("tiny", pygame.font.SysFont("Arial", 10))

        h = 175
        self._draw_card_box(surface, self.x_start + 12, y, self.width - 24, h)

        # Encabezado
        title = font_bold.render("ANALISIS DE RUTA SELECCIONADA", True, COLOR_TEXT_MAIN)
        surface.blit(title, (self.x_start + 22, y + 8))

        pygame.draw.line(surface, COLOR_HUD_DIVIDER, (self.x_start + 22, y + 26), (self.x_start + self.width - 22, y + 26), 1)

        # Origen y Destino
        orig_str = f"[{orig.id}] {orig.name}" if orig else "Clic en nodo para elegir"
        dest_str = f"[{dest.id}] {dest.name}" if dest else "Clic en nodo para elegir"

        txt_o = font_small.render(f"Origen  : {orig_str}", True, COLOR_TEXT_ACCENT)
        txt_d = font_small.render(f"Destino : {dest_str}", True, COLOR_TEXT_SUCCESS)
        surface.blit(txt_o, (self.x_start + 22, y + 32))
        surface.blit(txt_d, (self.x_start + 22, y + 49))

        if path and path.found and len(path.nodes) > 1:
            # Itinerario de nodos
            itinerary = path.path_str
            if len(itinerary) > 42:
                itinerary = itinerary[:39] + "..."
            txt_itin = font_tiny.render(f"Trayecto: {itinerary}", True, (226, 232, 240))
            surface.blit(txt_itin, (self.x_start + 22, y + 70))

            # Metricas cuantitativas
            m_dist = f"{path.total_distance_km:.1f} km"
            m_cost = f"${path.total_cost:.2f}"
            m_time = f"{path.total_time_hours:.2f} h"

            # Tres cajas de metricas compactas
            box_w = 108
            box_y = y + 90
            for i, (lbl, val, col) in enumerate([("Distancia", m_dist, COLOR_ROUTE_OPTIMAL), ("Costo Opt.", m_cost, COLOR_TEXT_SUCCESS), ("Tiempo Est.", m_time, COLOR_TEXT_WARNING)]):
                bx = self.x_start + 22 + i * 116
                pygame.draw.rect(surface, (15, 23, 42), (bx, box_y, box_w, 36), border_radius=4)
                lbl_s = font_tiny.render(lbl, True, COLOR_TEXT_MUTED)
                val_s = font_bold.render(val, True, col)
                surface.blit(lbl_s, (bx + 8, box_y + 3))
                surface.blit(val_s, (bx + 8, box_y + 17))

            # Comparativa con ruta alternativa
            if alt_path and alt_path.found and alt_path.total_cost > path.total_cost:
                saving_usd = alt_path.total_cost - path.total_cost
                pct = (saving_usd / alt_path.total_cost) * 100.0
                comp_txt = f"Ahorro vs Ruta Alt.: +${saving_usd:.2f} (-{pct:.1f}%) | Alt: {alt_path.total_distance_km:.0f}km"
                comp_col = COLOR_TEXT_SUCCESS
            else:
                comp_txt = "Ruta directa / Unica viable disponible en red"
                comp_col = COLOR_TEXT_MUTED

            c_surf = font_tiny.render(comp_txt, True, comp_col)
            surface.blit(c_surf, (self.x_start + 22, y + 134))

            # Boton / Instruccion de despacho
            disp_txt = font_tiny.render("Presione [D] para despachar camion optimo", True, (251, 191, 36))
            surface.blit(disp_txt, (self.x_start + 22, y + 152))
        else:
            txt_wait = font_small.render("Seleccione dos nodos para calcular ruta...", True, COLOR_TEXT_MUTED)
            surface.blit(txt_wait, (self.x_start + 22, y + 85))

        return y + h + 10

    def _draw_fleet_card(self, surface: pygame.Surface, y: int, sim: TransportSimulation) -> int:
        """Dibuja el estado operacional de cada camion en la flota."""
        font_bold = self.fonts.get("bold", pygame.font.SysFont("Arial", 12, bold=True))
        font_tiny = self.fonts.get("tiny", pygame.font.SysFont("Arial", 10))

        h = 160
        self._draw_card_box(surface, self.x_start + 12, y, self.width - 24, h)

        # Encabezado
        avail = sum(1 for t in sim.fleet_manager.trucks if t.is_available)
        title = font_bold.render(f"FLOTA DE CAMIONES ({avail}/{len(sim.fleet_manager.trucks)} Libres)", True, COLOR_TEXT_MAIN)
        surface.blit(title, (self.x_start + 22, y + 8))

        pygame.draw.line(surface, COLOR_HUD_DIVIDER, (self.x_start + 22, y + 26), (self.x_start + self.width - 22, y + 26), 1)

        # Fila por cada camion
        row_y = y + 32
        for truck in sim.fleet_manager.trucks:
            # Color distintivo segun tipo
            dot_col = truck.truck_type.color
            pygame.draw.circle(surface, dot_col, (self.x_start + 28, row_y + 7), 4)

            # ID y Tipo abreviado
            t_name = f"C-0{truck.id}"
            n_surf = font_bold.render(t_name, True, COLOR_TEXT_MAIN)
            surface.blit(n_surf, (self.x_start + 38, row_y))

            # Ubicacion actual
            loc_txt = f"@{truck.current_node.id}"
            loc_surf = font_tiny.render(loc_txt, True, (147, 197, 253))
            surface.blit(loc_surf, (self.x_start + 85, row_y + 1))

            # Carga / Capacidad
            load_txt = f"{truck.current_cargo_tons:.0f}/{truck.capacity_tons:.0f}t"
            load_surf = font_tiny.render(load_txt, True, COLOR_TEXT_WARNING)
            surface.blit(load_surf, (self.x_start + 145, row_y + 1))

            # Estado actual
            st_val = truck.state.value
            if truck.state.name == "DISPONIBLE":
                st_col = COLOR_TEXT_SUCCESS
            elif truck.state.name == "EN_RUTA":
                st_col = COLOR_ROUTE_OPTIMAL
            else:
                st_col = COLOR_TEXT_WARNING

            st_surf = font_tiny.render(st_val, True, st_col)
            surface.blit(st_surf, (self.x_start + 220, row_y + 1))

            row_y += 20

        return y + h + 10

    def _draw_metrics_card(self, surface: pygame.Surface, y: int, sim: TransportSimulation) -> int:
        """Dibuja el compendio de metricas cuantitativas acumuladas."""
        font_bold = self.fonts.get("bold", pygame.font.SysFont("Arial", 12, bold=True))
        font_small = self.fonts.get("small", pygame.font.SysFont("Arial", 11))

        h = 130
        self._draw_card_box(surface, self.x_start + 12, y, self.width - 24, h)

        # Encabezado
        title = font_bold.render("TELEMETRIA CUANTITATIVA GLOBAL", True, COLOR_TEXT_MAIN)
        surface.blit(title, (self.x_start + 22, y + 8))

        pygame.draw.line(surface, COLOR_HUD_DIVIDER, (self.x_start + 22, y + 26), (self.x_start + self.width - 22, y + 26), 1)

        summary = sim.fleet_manager.get_fleet_summary()

        metrics = [
            ("Viajes Completados", f"{summary['ordenes_entregadas']}"),
            ("Carga Movilizada", f"{summary['toneladas_entregadas']:.1f} ton"),
            ("Recorrido Acumulado", f"{summary['kilometros_totales']:.1f} km"),
            ("Costo Total Operativo", f"${summary['costo_total_operativo']:.2f}"),
            ("Ahorro por Optimizacion", f"${summary['ahorro_total_optimizacion']:.2f}"),
        ]

        row_y = y + 32
        for lbl, val in metrics:
            l_surf = font_small.render(lbl, True, COLOR_TEXT_MUTED)
            v_col = COLOR_TEXT_SUCCESS if "Ahorro" in lbl else COLOR_TEXT_MAIN
            v_surf = font_bold.render(val, True, v_col)
            surface.blit(l_surf, (self.x_start + 22, row_y))
            surface.blit(v_surf, (self.x_start + self.width - 22 - v_surf.get_width(), row_y))
            row_y += 18

        return y + h + 10

    def _draw_controls_card(self, surface: pygame.Surface, y: int) -> int:
        """Dibuja los atajos de teclado y guia interactiva de usuario."""
        font_bold = self.fonts.get("bold", pygame.font.SysFont("Arial", 12, bold=True))
        font_tiny = self.fonts.get("tiny", pygame.font.SysFont("Arial", 10))

        h = 135
        self._draw_card_box(surface, self.x_start + 12, y, self.width - 24, h)

        title = font_bold.render("CONTROLES & ATAJOS", True, COLOR_TEXT_MAIN)
        surface.blit(title, (self.x_start + 22, y + 8))

        pygame.draw.line(surface, COLOR_HUD_DIVIDER, (self.x_start + 22, y + 26), (self.x_start + self.width - 22, y + 26), 1)

        shortcuts = [
            ("[CLIC EN NODO]", "Seleccionar Origen y Destino"),
            ("[D]", "Despachar pedido de ruta seleccionada"),
            ("[A]", "Alternar modo automatico de pedidos"),
            ("[T]", "Alternar Algoritmo (Dijkstra <-> A*)"),
            ("[1, 2, 3, 4]", "Velocidad de simulacion (1x, 2x, 5x, 10x)"),
            ("[ESPACIO] / [R]", "Pausar / Reiniciar simulacion"),
            ("[ESC]", "Salir y desplegar reporte analitico"),
        ]

        row_y = y + 32
        for key, desc in shortcuts:
            k_surf = font_tiny.render(key, True, COLOR_TEXT_ACCENT)
            d_surf = font_tiny.render(desc, True, COLOR_TEXT_MUTED)
            surface.blit(k_surf, (self.x_start + 22, row_y))
            surface.blit(d_surf, (self.x_start + 130, row_y))
            row_y += 14

        return y + h + 10
