"""Panel lateral HUD con telemetria cuantitativa y comparacion teorico vs simulado."""

import pygame
from src.constants import (
    SIM_WIDTH,
    HUD_WIDTH,
    WINDOW_HEIGHT,
    COLOR_HUD_BG,
    COLOR_HUD_CARD,
    COLOR_HUD_BORDER,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_ACCENT,
)


class HudView:
    """Renderiza el tablero de control, parametros estocasticos y metricas M/M/c."""

    def __init__(self, fonts: dict):
        self.fonts = fonts

    def render(
        self,
        surface: pygame.Surface,
        sim,
        speed_multiplier: float,
        is_paused: bool,
        fps: float,
    ):
        """Dibuja el panel lateral derecho con tarjetas de datos estructuradas."""
        hud_rect = pygame.Rect(SIM_WIDTH, 0, HUD_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(surface, COLOR_HUD_BG, hud_rect)
        pygame.draw.line(surface, COLOR_HUD_BORDER, (SIM_WIDTH, 0), (SIM_WIDTH, WINDOW_HEIGHT), 2)

        x_margin = SIM_WIDTH + 14
        y_cursor = 14

        # 1. Cabecera institucional
        h1 = self.fonts["bold"].render("METODOS CUANTITATIVOS", True, COLOR_TEXT_ACCENT)
        surface.blit(h1, (x_margin, y_cursor))
        y_cursor += 20

        h2 = self.fonts["small"].render("Teoria de Colas M/M/c — Estacion de Servicio", True, COLOR_TEXT_MUTED)
        surface.blit(h2, (x_margin, y_cursor))
        y_cursor += 26

        # 2. Tarjeta: Estado de la Simulacion
        y_cursor = self._draw_sim_status(surface, x_margin, y_cursor, sim, speed_multiplier, is_paused, fps)

        # 3. Tarjeta: Comparacion Cuantitativa (Teorica M/M/c vs Simulada SimPy)
        y_cursor = self._draw_comparison_table(surface, x_margin, y_cursor, sim)

        # 4. Tarjeta: Metricas Operativas
        y_cursor = self._draw_operational_metrics(surface, x_margin, y_cursor, sim)

        # 5. Tarjeta: Guia de Controles
        self._draw_controls_guide(surface, x_margin, y_cursor)

    def _draw_sim_status(self, surface, x, y, sim, speed, paused, fps) -> int:
        card_h = 60
        card_w = HUD_WIDTH - 28
        card_rect = pygame.Rect(x, y, card_w, card_h)
        pygame.draw.rect(surface, COLOR_HUD_CARD, card_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_HUD_BORDER, card_rect, width=1, border_radius=6)

        # Formato de tiempo simulado MM:SS
        total_s = int(sim.current_sim_time)
        mins = total_s // 60
        secs = total_s % 60
        time_str = f"T. Simulado: {mins:02d}:{secs:02d}"

        lbl_time = self.fonts["bold"].render(time_str, True, COLOR_TEXT_MAIN)
        surface.blit(lbl_time, (x + 10, y + 10))

        # Estado y velocidad
        status_txt = "PAUSADO" if paused else "EN MARCHA"
        status_col = (239, 68, 68) if paused else (34, 197, 94)
        lbl_status = self.fonts["small"].render(f"Estado: {status_txt}", True, status_col)
        surface.blit(lbl_status, (x + 10, y + 34))

        lbl_spd = self.fonts["small"].render(f"Velocidad: {speed:.1f}x | {int(fps)} FPS", True, COLOR_TEXT_MUTED)
        surface.blit(lbl_spd, (x + 170, y + 34))

        return y + card_h + 12

    def _draw_comparison_table(self, surface, x, y, sim) -> int:
        card_h = 240
        card_w = HUD_WIDTH - 28
        card_rect = pygame.Rect(x, y, card_w, card_h)
        pygame.draw.rect(surface, COLOR_HUD_CARD, card_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_HUD_BORDER, card_rect, width=1, border_radius=6)

        title = self.fonts["bold"].render("MODELO M/M/c: TEORIA vs SIMPY", True, COLOR_TEXT_MAIN)
        surface.blit(title, (x + 10, y + 8))

        headers = ["Parametro", "Teorico", "Simulado"]
        cols_x = [x + 10, x + 180, x + 265]

        for i, h in enumerate(headers):
            lbl = self.fonts["tiny"].render(h, True, COLOR_TEXT_ACCENT)
            surface.blit(lbl, (cols_x[i], y + 30))

        pygame.draw.line(surface, COLOR_HUD_BORDER, (x + 8, y + 46), (x + card_w - 8, y + 46), 1)

        # Calculo analitico
        theo = sim.analytical_model
        stats = sim.stats

        rows = [
            ("Bombas (c)", f"{theo.c}", f"{theo.c}"),
            ("Tasa llegada (λ)", f"{theo.lamb:.1f}/min", f"{theo.lamb:.1f}/min"),
            ("Tasa servicio (μ)", f"{theo.mu:.1f}/min", f"{1.0 / max(0.01, stats.avg_service_time_min):.1f}/min" if stats.avg_service_time_min > 0 else "—"),
            ("Utilizacion (ρ)", f"{theo.rho:.1%}", f"{(len(sim.vehicles_active)/max(1, theo.c)):.1%}"),
            ("Espera cola (Wq)", f"{theo.wq:.2f} min" if theo.is_stable else "Inf", f"{stats.avg_wait_time_min:.2f} min"),
            ("T. en sistema (W)", f"{theo.w:.2f} min" if theo.is_stable else "Inf", f"{stats.avg_system_time_min:.2f} min"),
            ("Longitud cola (Lq)", f"{theo.lq:.2f} aut" if theo.is_stable else "Inf", f"{stats.avg_queue_length:.2f} aut"),
            ("En sistema (L)", f"{theo.l:.2f} aut" if theo.is_stable else "Inf", f"{stats.avg_system_length:.2f} aut"),
        ]

        row_y = y + 52
        for param, val_t, val_s in rows:
            p_lbl = self.fonts["tiny"].render(param, True, COLOR_TEXT_MUTED)
            vt_lbl = self.fonts["tiny"].render(val_t, True, COLOR_TEXT_MAIN)
            vs_lbl = self.fonts["tiny"].render(val_s, True, (34, 197, 94))

            surface.blit(p_lbl, (cols_x[0], row_y))
            surface.blit(vt_lbl, (cols_x[1], row_y))
            surface.blit(vs_lbl, (cols_x[2], row_y))
            row_y += 22

        return y + card_h + 12

    def _draw_operational_metrics(self, surface, x, y, sim) -> int:
        card_h = 135
        card_w = HUD_WIDTH - 28
        card_rect = pygame.Rect(x, y, card_w, card_h)
        pygame.draw.rect(surface, COLOR_HUD_CARD, card_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_HUD_BORDER, card_rect, width=1, border_radius=6)

        title = self.fonts["bold"].render("METRICAS OPERACIONALES", True, COLOR_TEXT_MAIN)
        surface.blit(title, (x + 10, y + 8))

        stats = sim.stats
        items = [
            (f"Total arribos: {stats.total_arrivals}", f"En cola ahora: {len(sim.vehicles_in_queue)}"),
            (f"Atendidos: {stats.total_served}", f"En bombas ahora: {len(sim.vehicles_active)}"),
            (f"Rechazados (Cola llena): {stats.total_balked}", f"Tanque: {int(sim.tank.level)}L / {int(sim.tank.capacity)}L"),
        ]

        row_y = y + 32
        for left_txt, right_txt in items:
            l_lbl = self.fonts["small"].render(left_txt, True, COLOR_TEXT_MUTED)
            r_lbl = self.fonts["small"].render(right_txt, True, COLOR_TEXT_MAIN)
            surface.blit(l_lbl, (x + 10, row_y))
            surface.blit(r_lbl, (x + 180, row_y))
            row_y += 22

        # Barra de tanque en el HUD
        bar_y = row_y + 4
        bar_w = card_w - 20
        pygame.draw.rect(surface, (20, 24, 30), (x + 10, bar_y, bar_w, 8), border_radius=2)
        tank_prog = int(bar_w * (sim.tank.percent / 100.0))
        t_col = (34, 197, 94) if sim.tank.percent > 30 else (239, 68, 68)
        pygame.draw.rect(surface, t_col, (x + 10, bar_y, tank_prog, 8), border_radius=2)

        return y + card_h + 12

    def _draw_controls_guide(self, surface, x, y):
        card_h = 160
        card_w = HUD_WIDTH - 28
        card_rect = pygame.Rect(x, y, card_w, card_h)
        pygame.draw.rect(surface, COLOR_HUD_CARD, card_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_HUD_BORDER, card_rect, width=1, border_radius=6)

        title = self.fonts["bold"].render("CONTROLES DE LA SIMULACION", True, COLOR_TEXT_ACCENT)
        surface.blit(title, (x + 10, y + 8))

        controls = [
            ("[ESPACIO]", "Pausar / Reanudar reloj"),
            ("[1, 2, 3, 4]", "Velocidad (1x, 2x, 5x, 10x)"),
            ("[+] / [-]", "Aumentar / Disminuir tasa λ"),
            ("[C]", "Despachar camion cisterna"),
            ("[R]", "Reiniciar simulacion"),
            ("[ESC]", "Finalizar y ver reporte"),
        ]

        row_y = y + 30
        for key_str, desc_str in controls:
            k_lbl = self.fonts["tiny"].render(key_str, True, (250, 204, 21))
            d_lbl = self.fonts["tiny"].render(desc_str, True, COLOR_TEXT_MUTED)
            surface.blit(k_lbl, (x + 10, row_y))
            surface.blit(d_lbl, (x + 95, row_y))
            row_y += 19
