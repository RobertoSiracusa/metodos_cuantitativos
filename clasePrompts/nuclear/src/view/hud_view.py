"""Panel lateral de control e instrumentacion de la central nuclear (HUD)."""

import pygame
from typing import Dict, List
from src.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_PANEL_HEADER,
    COLOR_TEXT_LIGHT,
    COLOR_TEXT_MUTED,
    COLOR_STATE_SHUTDOWN,
    COLOR_STATE_SUBCRITICAL,
    COLOR_STATE_CRITICAL,
    COLOR_STATE_SUPERCRITICAL,
    COLOR_STATE_SCRAM,
    T_INLET_COOLANT,
    T_WARNING_FUEL,
    ReactorState,
)
from src.simulation.reactor_sim import ReactorSimulation


class HudView:
    """Renderiza los instrumentos de medicion, estado de reactividad y graficos."""

    def __init__(self, fonts: Dict[str, pygame.font.Font]):
        self.fonts = fonts
        self.panel_x = 880
        self.panel_y = 16
        self.panel_w = 384
        self.panel_h = WINDOW_HEIGHT - 32

    def render(
        self,
        surface: pygame.Surface,
        sim: ReactorSimulation,
        speed_multiplier: float,
        is_paused: bool,
        fps: float,
    ):
        """Dibuja el panel completo de telemetria."""
        core = sim.core
        stats = sim.stats

        # 1. Fondo del panel
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_w, self.panel_h)
        pygame.draw.rect(surface, COLOR_PANEL_BG, panel_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, panel_rect, width=2, border_radius=8)

        # 2. Encabezado institucional
        header_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_w, 56)
        pygame.draw.rect(surface, COLOR_PANEL_HEADER, header_rect, border_top_left_radius=8, border_top_right_radius=8)
        pygame.draw.line(surface, COLOR_PANEL_BORDER, (self.panel_x, self.panel_y + 56), (self.panel_x + self.panel_w, self.panel_y + 56), 2)

        title_surf = self.fonts["bold"].render("REACTOR NUCLEAR — SALA DE CONTROL", True, COLOR_TEXT_LIGHT)
        surface.blit(title_surf, (self.panel_x + 14, self.panel_y + 10))

        sub_surf = self.fonts["tiny"].render("Simulacion de Reaccion en Cadena (SimPy + Pygame)", True, COLOR_TEXT_MUTED)
        surface.blit(sub_surf, (self.panel_x + 14, self.panel_y + 32))

        # 3. Badge del estado operacional del reactor
        y_cursor = self.panel_y + 68
        state_color = self._get_state_color(core.state)
        state_rect = pygame.Rect(self.panel_x + 14, y_cursor, self.panel_w - 28, 32)
        pygame.draw.rect(surface, (*state_color, 40), state_rect, border_radius=6)
        pygame.draw.rect(surface, state_color, state_rect, width=2, border_radius=6)

        state_text = f"ESTADO: {core.state.value}"
        if is_paused:
            state_text += " [PAUSA]"
        lbl_state = self.fonts["bold"].render(state_text, True, state_color)
        surface.blit(lbl_state, (self.panel_x + 22, y_cursor + 7))

        y_cursor += 44

        # 4. Indicador de Factor de Multiplicacion Efectivo (k_eff)
        keff_box = pygame.Rect(self.panel_x + 14, y_cursor, self.panel_w - 28, 70)
        pygame.draw.rect(surface, (18, 22, 32), keff_box, border_radius=6)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, keff_box, width=1, border_radius=6)

        lbl_k = self.fonts["small"].render("FACTOR DE MULTIPLICACION EFECTIVO (k_eff)", True, COLOR_TEXT_MUTED)
        surface.blit(lbl_k, (self.panel_x + 24, y_cursor + 8))

        k_val_str = f"{core.k_eff:.4f}"
        val_k_surf = self.fonts["title"].render(k_val_str, True, state_color)
        surface.blit(val_k_surf, (self.panel_x + 24, y_cursor + 28))

        # Barra visual de k_eff (rango 0.70 a 1.30, centro en 1.00)
        bar_x = self.panel_x + 140
        bar_y = y_cursor + 38
        bar_w = self.panel_w - 170
        bar_h = 14
        pygame.draw.rect(surface, (35, 42, 58), (bar_x, bar_y, bar_w, bar_h), border_radius=3)

        # Mapeo de k_eff a porcentaje de la barra
        clamped_k = max(0.70, min(1.30, core.k_eff))
        fill_ratio = (clamped_k - 0.70) / 0.60
        pygame.draw.rect(surface, state_color, (bar_x, bar_y, int(bar_w * fill_ratio), bar_h), border_radius=3)
        # Linea de punto critico k=1.00
        center_line_x = bar_x + int(bar_w * ((1.00 - 0.70) / 0.60))
        pygame.draw.line(surface, (255, 255, 255), (center_line_x, bar_y - 2), (center_line_x, bar_y + bar_h + 2), 2)

        y_cursor += 78

        # 5. Metricas termicas y neutronicas
        self._render_metric_row(surface, "Potencia Termica:", f"{core.thermal_power_mw:.1f} MWth", y_cursor, (255, 180, 50))
        y_cursor += 22

        temp_color = (255, 80, 80) if core.temperature > T_WARNING_FUEL else COLOR_TEXT_LIGHT
        self._render_metric_row(surface, "Temperatura Nucleo:", f"{core.temperature:.1f} °C", y_cursor, temp_color)
        y_cursor += 22

        self._render_metric_row(surface, "Neutrones Libres (N):", f"{len(core.neutrons)} particulas", y_cursor, COLOR_TEXT_LIGHT)
        y_cursor += 22

        self._render_metric_row(surface, "Fisiones Totales:", f"{stats.total_fissions}", y_cursor, COLOR_TEXT_LIGHT)
        y_cursor += 22

        rod_pct = core.get_average_rod_insertion() * 100.0
        rod_str = f"{rod_pct:.1f}% [SCRAM]" if core.is_scrammed else f"{rod_pct:.1f}%"
        rod_col = (255, 50, 50) if core.is_scrammed else COLOR_TEXT_LIGHT
        self._render_metric_row(surface, "Barras de Control:", rod_str, y_cursor, rod_col)
        y_cursor += 22

        pump_str = "ACTIVAS (100%)" if core.coolant_pumps_active else "APAGADAS (0%)"
        pump_col = (50, 200, 100) if core.coolant_pumps_active else (240, 70, 70)
        self._render_metric_row(surface, "Bombas Refrigerante:", pump_str, y_cursor, pump_col)
        y_cursor += 30

        # 6. Grafico de telemetria en tiempo real
        graph_box = pygame.Rect(self.panel_x + 14, y_cursor, self.panel_w - 28, 120)
        pygame.draw.rect(surface, (14, 18, 26), graph_box, border_radius=6)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, graph_box, width=1, border_radius=6)

        lbl_g = self.fonts["tiny"].render("HISTORIAL EN VIVO — Neutrones (Azul) | Temp (Rojo)", True, COLOR_TEXT_MUTED)
        surface.blit(lbl_g, (self.panel_x + 22, y_cursor + 6))

        self._draw_graph(surface, graph_box, stats.history_neutrons, stats.history_temperature)
        y_cursor += 130

        # 7. Contadores y balance de neutrones
        bal_title = self.fonts["bold"].render("BALANCE DE NEUTRONES", True, COLOR_TEXT_MUTED)
        surface.blit(bal_title, (self.panel_x + 14, y_cursor))
        y_cursor += 18

        self._render_metric_row(surface, "Emitidos (Fision):", f"{stats.total_neutrons_born}", y_cursor, COLOR_TEXT_MUTED)
        y_cursor += 18
        self._render_metric_row(surface, "Capturados en Barras:", f"{stats.total_absorbed_rods}", y_cursor, COLOR_TEXT_MUTED)
        y_cursor += 18
        self._render_metric_row(surface, "Fugas / Escapes:", f"{stats.total_escaped}", y_cursor, COLOR_TEXT_MUTED)
        y_cursor += 26

        # 8. Leyenda de atajos de teclado
        key_box = pygame.Rect(self.panel_x + 14, y_cursor, self.panel_w - 28, 100)
        pygame.draw.rect(surface, (20, 25, 36), key_box, border_radius=6)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, key_box, width=1, border_radius=6)

        shortcuts = [
            ("[ESPACIO]", "Inyectar pulso neutrones"),
            ("[ARRIBA/ABAJO]", "Subir/bajar barras control"),
            ("[S]", "SCRAM parada de emergencia"),
            ("[B]", "Alternar bombas refrigeracion"),
            ("[1, 2, 4]", f"Velocidad ({speed_multiplier:.0f}x) | FPS: {fps:.0f}"),
            ("[R] Reiniciar", "[ESC] Finalizar sesion"),
        ]

        sy = y_cursor + 8
        for k_label, desc in shortcuts:
            k_surf = self.fonts["tiny"].render(k_label, True, (255, 210, 80))
            d_surf = self.fonts["tiny"].render(desc, True, COLOR_TEXT_MUTED)
            surface.blit(k_surf, (self.panel_x + 22, sy))
            surface.blit(d_surf, (self.panel_x + 130, sy))
            sy += 15

    def _render_metric_row(self, surface: pygame.Surface, label: str, value: str, y: int, val_color):
        lbl_surf = self.fonts["small"].render(label, True, COLOR_TEXT_MUTED)
        val_surf = self.fonts["bold"].render(value, True, val_color)
        surface.blit(lbl_surf, (self.panel_x + 20, y))
        val_w = val_surf.get_width()
        surface.blit(val_surf, (self.panel_x + self.panel_w - 20 - val_w, y))

    def _draw_graph(self, surface: pygame.Surface, rect: pygame.Rect, neutrons: List[int], temps: List[float]):
        if len(neutrons) < 2:
            return

        gx = rect.x + 8
        gy = rect.y + 24
        gw = rect.width - 16
        gh = rect.height - 30

        # Maximos de escala
        max_n = max(50, max(neutrons))
        max_t = max(1200.0, max(temps))

        n_pts = []
        t_pts = []
        count = len(neutrons)

        for i in range(count):
            px = gx + int(gw * (i / max(1, count - 1)))
            py_n = gy + gh - int((neutrons[i] / max_n) * gh)
            py_t = gy + gh - int(((temps[i] - T_INLET_COOLANT) / (max_t - T_INLET_COOLANT + 1e-5)) * gh)

            n_pts.append((px, max(gy, min(gy + gh, py_n))))
            t_pts.append((px, max(gy, min(gy + gh, py_t))))

        if len(n_pts) >= 2:
            pygame.draw.lines(surface, (80, 200, 255), False, n_pts, 2)
        if len(t_pts) >= 2:
            pygame.draw.lines(surface, (255, 90, 90), False, t_pts, 2)

    def _get_state_color(self, state: ReactorState):
        if state == ReactorState.SHUTDOWN:
            return COLOR_STATE_SHUTDOWN
        elif state == ReactorState.SUBCRITICAL:
            return COLOR_STATE_SUBCRITICAL
        elif state == ReactorState.CRITICAL:
            return COLOR_STATE_CRITICAL
        elif state == ReactorState.SUPERCRITICAL:
            return COLOR_STATE_SUPERCRITICAL
        elif state in (ReactorState.SCRAM, ReactorState.PROMPT_CRITICAL):
            return COLOR_STATE_SCRAM
        return COLOR_STATE_SHUTDOWN
