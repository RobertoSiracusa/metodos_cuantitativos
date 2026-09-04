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
    COLOR_TEXT_EMERALD,
    COLOR_TEXT_WARN,
    QueueMode,
)


class HudView:
    """Renderiza el tablero cuantitativo, parametros estocasticos y tabla comparativa."""

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
        y_cursor = 12

        # 1. Cabecera institucional
        h1 = self.fonts["bold"].render("METODOS CUANTITATIVOS — UJAP", True, COLOR_TEXT_ACCENT)
        surface.blit(h1, (x_margin, y_cursor))
        y_cursor += 18

        h2 = self.fonts["small"].render("Simulacion de Automercado y Lineas de Espera", True, COLOR_TEXT_MUTED)
        surface.blit(h2, (x_margin, y_cursor))
        y_cursor += 24

        # 2. Tarjeta: Estado de la Simulacion
        y_cursor = self._draw_sim_status(surface, x_margin, y_cursor, sim, speed_multiplier, is_paused, fps)

        # 3. Tarjeta: Comparacion Cuantitativa (Teoria vs Simulacion)
        y_cursor = self._draw_comparison_table(surface, x_margin, y_cursor, sim)

        # 4. Tarjeta: Metricas Operativas
        y_cursor = self._draw_operational_metrics(surface, x_margin, y_cursor, sim)

        # 5. Tarjeta: Guia de Controles
        self._draw_controls_guide(surface, x_margin, y_cursor)

    def _draw_sim_status(self, surface, x, y, sim, speed, paused, fps) -> int:
        card_h = 68
        card_w = HUD_WIDTH - 28
        card_rect = pygame.Rect(x, y, card_w, card_h)
        pygame.draw.rect(surface, COLOR_HUD_CARD, card_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_HUD_BORDER, card_rect, width=1, border_radius=6)

        # Tiempo simulado MM:SS
        total_s = int(sim.current_sim_time)
        mins = total_s // 60
        secs = total_s % 60
        time_str = f"T. Simulado: {mins:02d}:{secs:02d}"

        lbl_time = self.fonts["bold"].render(time_str, True, COLOR_TEXT_MAIN)
        surface.blit(lbl_time, (x + 10, y + 8))

        # Disciplina de cola activa
        mode_str = "Cola Unica M/M/c" if sim.queue_mode == QueueMode.SINGLE else "Colas Paralelas c x M/M/1"
        lbl_mode = self.fonts["tiny"].render(f"Disciplina: {mode_str}", True, COLOR_TEXT_ACCENT)
        surface.blit(lbl_mode, (x + 10, y + 28))

        # Estado y velocidad
        status_txt = "PAUSADO" if paused else "EN MARCHA"
        status_col = (239, 68, 68) if paused else (34, 197, 94)
        lbl_status = self.fonts["small"].render(status_txt, True, status_col)
        surface.blit(lbl_status, (x + 10, y + 46))

        lbl_spd = self.fonts["small"].render(f"Vel: {speed:.1f}x | {int(fps)} FPS", True, COLOR_TEXT_MUTED)
        surface.blit(lbl_spd, (x + 180, y + 46))

        return y + card_h + 10

    def _draw_comparison_table(self, surface, x, y, sim) -> int:
        card_h = 246
        card_w = HUD_WIDTH - 28
        card_rect = pygame.Rect(x, y, card_w, card_h)
        pygame.draw.rect(surface, COLOR_HUD_CARD, card_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_HUD_BORDER, card_rect, width=1, border_radius=6)

        title = self.fonts["bold"].render("MODELO MATEMATICO: TEORIA vs SIMPY", True, COLOR_TEXT_MAIN)
        surface.blit(title, (x + 10, y + 7))

        headers = ["Parametro", "Teorico", "Simulado"]
        cols_x = [x + 10, x + 175, x + 265]

        for i, h in enumerate(headers):
            lbl = self.fonts["bold"].render(h, True, COLOR_TEXT_MUTED)
            surface.blit(lbl, (cols_x[i], y + 26))

        pygame.draw.line(surface, COLOR_HUD_BORDER, (x + 10, y + 43), (x + card_w - 10, y + 43), 1)

        theo = sim.current_analytical_model
        stats = sim.stats

        stable = theo.is_stable
        rho_str = f"{theo.rho:.3f}" if stable else f"{theo.rho:.3f} (!)"

        rows = [
            ("Lambda (llegadas/m)", f"{theo.lamb:.1f}", f"{stats.total_arrivals / max(0.1, sim.current_sim_time / 60.0):.1f}"),
            ("Mu (servicio/caja)", f"{theo.mu:.1f}", f"{1.0 / max(0.01, stats.avg_service_time_min):.1f}" if stats.total_served > 0 else "--"),
            ("Cajas activas (c)", f"{theo.c}", f"{sim.active_registers_count}"),
            ("Utilizacion (rho)", rho_str, f"{stats.empirical_rho:.3f}"),
            ("P0 (prob. vacio)", f"{theo.p0:.3f}" if stable else "0.000", "--"),
            ("Lq (clientes cola)", f"{theo.lq:.2f}" if stable else "Inf", f"{stats.avg_queue_length:.2f}"),
            ("Wq (espera cola)", f"{theo.wq:.2f} m" if stable else "Inf", f"{stats.avg_wait_time_min:.2f} m"),
            ("L (clientes tienda)", f"{theo.l:.2f}" if stable else "Inf", f"{stats.avg_system_length:.2f}"),
            ("W (tiempo total)", f"{theo.w:.2f} m" if stable else "Inf", f"{stats.avg_system_time_min:.2f} m"),
        ]

        row_y = y + 48
        for param, t_val, s_val in rows:
            lbl_p = self.fonts["small"].render(param, True, COLOR_TEXT_MAIN)
            surface.blit(lbl_p, (cols_x[0], row_y))

            t_col = COLOR_TEXT_WARN if not stable and param.startswith(("Lq", "Wq", "L", "W")) else COLOR_TEXT_ACCENT
            lbl_t = self.fonts["small"].render(t_val, True, t_col)
            surface.blit(lbl_t, (cols_x[1], row_y))

            lbl_s = self.fonts["small"].render(s_val, True, COLOR_TEXT_EMERALD)
            surface.blit(lbl_s, (cols_x[2], row_y))

            row_y += 21

        return y + card_h + 10

    def _draw_operational_metrics(self, surface, x, y, sim) -> int:
        card_h = 100
        card_w = HUD_WIDTH - 28
        card_rect = pygame.Rect(x, y, card_w, card_h)
        pygame.draw.rect(surface, COLOR_HUD_CARD, card_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_HUD_BORDER, card_rect, width=1, border_radius=6)

        title = self.fonts["bold"].render("TELEMETRIA OPERATIVA", True, COLOR_TEXT_MAIN)
        surface.blit(title, (x + 10, y + 7))

        stats = sim.stats
        c_tot = stats.total_arrivals
        c_srv = stats.total_served
        c_blk = stats.total_balked

        col1_x = x + 10
        col2_x = x + 180

        l1 = self.fonts["small"].render(f"Arribos totales: {c_tot}", True, COLOR_TEXT_MAIN)
        surface.blit(l1, (col1_x, y + 28))

        l2 = self.fonts["small"].render(f"Atendidos: {c_srv}", True, COLOR_TEXT_EMERALD)
        surface.blit(l2, (col2_x, y + 28))

        balk_col = (239, 68, 68) if c_blk > 0 else COLOR_TEXT_MUTED
        l3 = self.fonts["small"].render(f"Rechazos cola: {c_blk} ({stats.balk_rate:.1f}%)", True, balk_col)
        surface.blit(l3, (col1_x, y + 49))

        l4 = self.fonts["small"].render(f"Items vendidos: {stats.total_items_sold}", True, COLOR_TEXT_MAIN)
        surface.blit(l4, (col2_x, y + 49))

        rev_str = f"Ventas estimadas: ${stats.total_revenue:,.2f}"
        l5 = self.fonts["small"].render(rev_str, True, COLOR_TEXT_ACCENT)
        surface.blit(l5, (col1_x, y + 72))

        return y + card_h + 10

    def _draw_controls_guide(self, surface, x, y):
        card_h = 180
        card_w = HUD_WIDTH - 28
        card_rect = pygame.Rect(x, y, card_w, card_h)
        pygame.draw.rect(surface, COLOR_HUD_CARD, card_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_HUD_BORDER, card_rect, width=1, border_radius=6)

        title = self.fonts["bold"].render("CONTROLES INTERACTIVOS", True, COLOR_TEXT_MAIN)
        surface.blit(title, (x + 10, y + 6))

        controls = [
            ("[ESPACIO]", "Pausar / Reanudar"),
            ("[1, 2, 3, 4]", "Velocidad (1x, 2x, 5x, 10x)"),
            ("[+] / [-]", "Ajustar tasa lambda (+/- 0.5)"),
            ("[A] / [Z]", "Abrir / Cerrar caja registradora"),
            ("[M]", "Alternar Cola Unica vs Paralelas"),
            ("[R]", "Reiniciar simulacion"),
            ("[ESC]", "Finalizar y reporte cuantitativo"),
        ]

        cy = y + 26
        for key, desc in controls:
            lbl_k = self.fonts["tiny"].render(key, True, COLOR_TEXT_ACCENT)
            surface.blit(lbl_k, (x + 10, cy))

            lbl_d = self.fonts["tiny"].render(desc, True, COLOR_TEXT_MUTED)
            surface.blit(lbl_d, (x + 115, cy))

            cy += 21
