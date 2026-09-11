"""
Panel Lateral de Control y Telemetria (Dashboard HUD)
Capa de Presentacion — Metodos Cuantitativos
Universidad Jose Antonio Paez
"""

from typing import Dict, Tuple
import pygame

from src.gui.styles import (
    COLOR_HUD_BG,
    COLOR_CARD_BG,
    COLOR_CARD_BORDER,
    COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_DIM,
    COLOR_TEXT_CYAN,
    COLOR_TEXT_GOLD,
    BADGE_GREEN_BG,
    BADGE_GREEN_TXT,
    BADGE_YELLOW_BG,
    BADGE_YELLOW_TXT,
    BADGE_RED_BG,
    BADGE_RED_TXT,
    BADGE_BLUE_BG,
    BADGE_BLUE_TXT,
)
from src.gui.widgets import Button, Card, BannerNotification
from src.services.simulation_service import NetworkSimulation


class NetworkDashboard:
    """Panel lateral de control interactivo, visualizacion de metricas y monitoreo continuo."""

    def __init__(self, x_offset: int, width: int, height: int):
        self.x = x_offset
        self.width = width
        self.height = height

        self.font_title = pygame.font.SysFont("Segoe UI", 13, bold=True)
        self.font_card = pygame.font.SysFont("Segoe UI", 11, bold=True)
        self.font_data = pygame.font.SysFont("Segoe UI", 11)
        self.font_badge = pygame.font.SysFont("Segoe UI", 10, bold=True)

        self.banner = BannerNotification()
        self._crear_botones()

    def actualizar_dimensiones(self, x_offset: int, width: int, height: int) -> None:
        self.x = x_offset
        self.width = width
        self.height = height
        self._crear_botones()

    def _crear_botones(self) -> None:
        bx = self.x + 15
        bw = (self.width - 40) // 2
        btn_h = 24
        btn_y = self.height - 110

        # Botones de control primario
        self.btn_pause = Button(pygame.Rect(bx, btn_y, bw, btn_h), "Pausa [Espacio]", (51, 65, 85))
        self.btn_export = Button(pygame.Rect(bx + bw + 10, btn_y, bw, btn_h), "Exportar [E]", (37, 99, 235))

        # Ajuste de parametros de colas
        self.btn_lam_up = Button(pygame.Rect(bx, btn_y + 28, bw // 2 - 2, 22), "λ +", (71, 85, 105))
        self.btn_lam_down = Button(pygame.Rect(bx + bw // 2 + 2, btn_y + 28, bw // 2 - 2, 22), "λ -", (71, 85, 105))
        self.btn_mu_up = Button(pygame.Rect(bx + bw + 10, btn_y + 28, bw // 2 - 2, 22), "μ +", (71, 85, 105))
        self.btn_mu_down = Button(pygame.Rect(bx + bw + 10 + bw // 2 + 2, btn_y + 28, bw // 2 - 2, 22), "μ -", (71, 85, 105))

        # Simulacion de fallas y pantalla
        self.btn_toggle_link = Button(pygame.Rect(bx, btn_y + 54, bw, 22), "Falla Enlace [F1]", (127, 29, 29))
        self.btn_fullscreen = Button(pygame.Rect(bx + bw + 10, btn_y + 54, bw, 22), "Expandir [F11]", (30, 41, 59))

        # Selectores de velocidad
        sw = (self.width - 40) // 5
        sy = btn_y + 80
        self.btn_speed_025x = Button(pygame.Rect(bx + sw * 0, sy, sw - 2, 20), "0.25x", (51, 65, 85))
        self.btn_speed_05x = Button(pygame.Rect(bx + sw * 1, sy, sw - 2, 20), "0.5x", (51, 65, 85))
        self.btn_speed_1x = Button(pygame.Rect(bx + sw * 2, sy, sw - 2, 20), "1.0x", (51, 65, 85))
        self.btn_speed_2x = Button(pygame.Rect(bx + sw * 3, sy, sw - 2, 20), "2.0x", (51, 65, 85))
        self.btn_speed_4x = Button(pygame.Rect(bx + sw * 4, sy, sw - 2, 20), "4.0x", (51, 65, 85))

        self.btn_reset = Button(pygame.Rect(bx, sy + 24, self.width - 30, 20), "Reiniciar Simulacion [R]", (71, 85, 105))

    def update(self, dt: float, mouse_pos: Tuple[int, int]) -> None:
        for b in [
            self.btn_pause, self.btn_export, self.btn_lam_up, self.btn_lam_down,
            self.btn_mu_up, self.btn_mu_down, self.btn_toggle_link, self.btn_fullscreen,
            self.btn_speed_025x, self.btn_speed_05x, self.btn_speed_1x, self.btn_speed_2x,
            self.btn_speed_4x, self.btn_reset
        ]:
            b.check_hover(mouse_pos)

    def set_banner(self, texto: str, duracion: float = 4.0) -> None:
        self.banner.set_mensaje(texto, duracion)

    def draw(
        self,
        surface: pygame.Surface,
        sim: NetworkSimulation,
        is_paused: bool,
        sim_speed: float,
        is_maximized: bool,
    ) -> None:
        # Fondo lateral
        hud_rect = pygame.Rect(self.x, 0, self.width, self.height)
        pygame.draw.rect(surface, COLOR_HUD_BG, hud_rect)
        pygame.draw.line(surface, COLOR_CARD_BORDER, (self.x, 0), (self.x, self.height), 1)

        # Encabezado principal
        lbl_head = self.font_title.render("TELEMETRIA Y CONTROL", True, COLOR_TEXT_WHITE)
        surface.blit(lbl_head, (self.x + 15, 12))

        # Estado global (Pausa / Activa)
        txt_estado = "PAUSADA" if is_paused else f"EJECUTANDO ({sim_speed}x)"
        col_badge_bg = BADGE_YELLOW_BG if is_paused else BADGE_GREEN_BG
        col_badge_txt = BADGE_YELLOW_TXT if is_paused else BADGE_GREEN_TXT
        self._draw_badge(surface, f"[{txt_estado}]", self.x + self.width - 135, 12, col_badge_bg, col_badge_txt)

        m = sim.obtener_metricas_completas()
        cy = 40
        cw = self.width - 30

        # Tarjeta 1: Trafico y Teoria de Colas
        c1_h = 105
        Card(pygame.Rect(self.x + 15, cy, cw, c1_h)).draw(surface)
        surface.blit(self.font_card.render("1. TEORIA DE COLAS (M/M/1/K)", True, COLOR_TEXT_CYAN), (self.x + 25, cy + 8))

        t_sim = m.get("tiempo_simulacion_s", 0.0)
        lam = m.get("lambda", 0.0)
        mu = m.get("mu", 0.0)
        rho = m.get("factor_utilizacion_rho", 0.0)
        wq = m.get("tiempo_medio_cola_wq_s", 0.0)
        w = m.get("tiempo_medio_sistema_w_s", 0.0)
        l_val = m.get("promedio_paquetes_sistema_l", 0.0)
        lq_val = m.get("promedio_paquetes_cola_lq", 0.0)

        self._render_kv(surface, "Tiempo Simulacion:", f"{t_sim:.1f} s", self.x + 25, cy + 28)
        self._render_kv(surface, "Tasa Llegada (λ):", f"{lam:.1f} paq/s", self.x + 25, cy + 44)
        self._render_kv(surface, "Tasa Servicio (μ):", f"{mu:.1f} paq/s", self.x + 25, cy + 60)
        self._render_kv(surface, "Factor Utilizacion (ρ):", f"{rho:.3f}", self.x + 25, cy + 76)

        # Badge de estabilidad de cola
        badge_stab = "[ESTABLE]" if rho < 0.85 else "[CONGESTION]"
        b_bg = BADGE_GREEN_BG if rho < 0.85 else BADGE_RED_BG
        b_tx = BADGE_GREEN_TXT if rho < 0.85 else BADGE_RED_TXT
        self._draw_badge(surface, badge_stab, self.x + cw - 75, cy + 74, b_bg, b_tx)

        # Tarjeta 2: Tiempos y Encolamiento
        cy += c1_h + 8
        c2_h = 95
        Card(pygame.Rect(self.x + 15, cy, cw, c2_h)).draw(surface)
        surface.blit(self.font_card.render("2. RETARDOS Y METRICAS DE RED", True, COLOR_TEXT_CYAN), (self.x + 25, cy + 8))
        self._render_kv(surface, "Espera en Cola (Wq):", f"{wq:.4f} s ({wq * 1000:.1f} ms)", self.x + 25, cy + 26)
        self._render_kv(surface, "Estancia Total (W):", f"{w:.4f} s ({w * 1000:.1f} ms)", self.x + 25, cy + 42)
        self._render_kv(surface, "Paquetes en Red (L):", f"{l_val:.2f}", self.x + 25, cy + 58)
        self._render_kv(surface, "Paquetes en Cola (Lq):", f"{lq_val:.2f}", self.x + 25, cy + 74)

        # Tarjeta 3: Gestion de Inventario y Buffers
        cy += c2_h + 8
        c3_h = 100
        Card(pygame.Rect(self.x + 15, cy, cw, c3_h)).draw(surface)
        surface.blit(self.font_card.render("3. GESTION DE INVENTARIO (s, Q)", True, COLOR_TEXT_GOLD), (self.x + 25, cy + 8))

        proc = m.get("paquetes_procesados", 0)
        drop = m.get("paquetes_perdidos", 0)
        loss_pct = m.get("tasa_perdida_pct", 0.0)

        self._render_kv(surface, "Capacidad Buffer (S):", f"{m.get('capacidad_buffer_s')} paq", self.x + 25, cy + 26)
        self._render_kv(surface, "Politica (s, Q):", f"s={m.get('umbral_reabastecimiento_s')}, Q={m.get('lote_q')}", self.x + 25, cy + 42)
        self._render_kv(surface, "Paquetes Procesados:", str(proc), self.x + 25, cy + 58)
        self._render_kv(surface, "Perdidos (Overflow):", f"{drop} ({loss_pct:.2f}%)", self.x + 25, cy + 74)

        # Tarjeta 4: Costos Cuantitativos
        cy += c3_h + 8
        c4_h = 75
        Card(pygame.Rect(self.x + 15, cy, cw, c4_h)).draw(surface)
        surface.blit(self.font_card.render("4. COSTOS CUANTITATIVOS", True, COLOR_TEXT_GOLD), (self.x + 25, cy + 8))
        c_alm = m.get("costo_almacenamiento_usd", 0.0)
        c_rup = m.get("costo_penalizacion_usd", 0.0)
        c_tot = m.get("costo_global_usd", 0.0)
        self._render_kv(surface, "Almacenamiento (RAM):", f"${c_alm:.2f}", self.x + 25, cy + 26)
        self._render_kv(surface, "Penalizacion (Ruptura):", f"${c_rup:.2f}", self.x + 25, cy + 40)
        self._render_kv(surface, "Costo Global Total:", f"${c_tot:.2f}", self.x + 25, cy + 54)

        # Dibujar botones de control interactivo
        for b in [
            self.btn_pause, self.btn_export, self.btn_lam_up, self.btn_lam_down,
            self.btn_mu_up, self.btn_mu_down, self.btn_toggle_link, self.btn_fullscreen,
            self.btn_speed_025x, self.btn_speed_05x, self.btn_speed_1x, self.btn_speed_2x,
            self.btn_speed_4x, self.btn_reset
        ]:
            b.draw(surface, self.font_data)

        # Banner temporal de accion
        self.banner.draw(surface, self.font_data, self.x - 380, self.height - 35, 360)

    def _render_kv(self, surface: pygame.Surface, key: str, val: str, x: int, y: int) -> None:
        k_surf = self.font_data.render(key, True, COLOR_TEXT_MUTED)
        v_surf = self.font_data.render(val, True, COLOR_TEXT_WHITE)
        surface.blit(k_surf, (x, y))
        surface.blit(v_surf, (x + 145, y))

    def _draw_badge(self, surface: pygame.Surface, text: str, x: int, y: int, bg_col, txt_col) -> None:
        t_surf = self.font_badge.render(text, True, txt_col)
        pad_x, pad_y = 6, 2
        bg_rect = pygame.Rect(x, y, t_surf.get_width() + (pad_x * 2), t_surf.get_height() + (pad_y * 2))
        pygame.draw.rect(surface, bg_col, bg_rect, border_radius=4)
        surface.blit(t_surf, (x + pad_x, y + pad_y))
