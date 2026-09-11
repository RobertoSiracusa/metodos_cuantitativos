"""
Aplicacion Principal Pygame (Ventana, Bucle 60 FPS y Control de Eventos)
Capa de Presentacion — Metodos Cuantitativos
Universidad Jose Antonio Paez
"""

from pathlib import Path
import sys
from typing import Dict, List, Optional, Tuple, Union
import pygame

from src.services.simulation_service import NetworkSimulation
from src.services.ai_auditor import AIAuditorService
from src.services.docx_service import DocxReportService
from src.services.reporter import ReportService
from src.gui.styles import SCREEN_WIDTH, SCREEN_HEIGHT
from src.gui.renderer import NetworkRenderer
from src.gui.dashboard import NetworkDashboard
from src.utils.config import (
    LAMBDA_DEFECTO,
    MU_DEFECTO,
    CAPACIDAD_BUFFER_S,
    UMBRAL_REABASTECER_S,
    LOTE_REABASTECER_Q,
    OUTPUTS_DIR,
)


class SimulatorApp:
    """Aplicacion interactiva de simulacion de redes con Pygame."""

    def __init__(self, headless: bool = False):
        self.headless = headless

        if not self.headless:
            pygame.init()
            pygame.font.init()

            self.screen_w = SCREEN_WIDTH
            self.screen_h = SCREEN_HEIGHT
            self.is_maximized = False

            self.screen = pygame.display.set_mode((self.screen_w, self.screen_h), pygame.RESIZABLE)
            pygame.display.set_caption("Simulador Dinamico de Redes de Computadoras — Metodos Cuantitativos (UJAP)")

            self.clock = pygame.time.Clock()
            self.fps = 60

            self.hud_w = min(480, max(380, int(self.screen_w * 0.32)))
            self.net_w = self.screen_w - self.hud_w

            self.renderer = NetworkRenderer()
            self.dashboard = NetworkDashboard(x_offset=self.net_w, width=self.hud_w, height=self.screen_h)

        # Instanciar servicios del nucleo
        self.sim = NetworkSimulation(
            lam=LAMBDA_DEFECTO,
            mu=MU_DEFECTO,
            capacidad_s=CAPACIDAD_BUFFER_S,
            umbral_s=UMBRAL_REABASTECER_S,
            lote_q=LOTE_REABASTECER_Q,
        )

        if not self.headless:
            self.sim.actualizar_dimensiones_pantalla(self.net_w, self.screen_h)

        self.auditor = AIAuditorService()
        self.is_running = True
        self.is_paused = False
        self.sim_speed = 0.5  # Velocidad por defecto fluida y didactica

        if not self.headless:
            self.dashboard.set_banner("Simulador iniciado. Presione F11 para expandir o Espacio para pausar.", duracion=5.0)

    def run(self) -> None:
        """Ciclo principal de eventos a 60 FPS."""
        if self.headless:
            return

        while self.is_running:
            dt = self.clock.tick(self.fps) / 1000.0

            self._handle_events()

            if not self.is_paused:
                self._update_simulation(dt)

            self.renderer.update_animation(dt)
            mouse_pos = pygame.mouse.get_pos()
            self.dashboard.update(dt, mouse_pos)

            self._draw()

        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._finalizar_y_exportar()
                self.is_running = False

            elif event.type == pygame.VIDEORESIZE:
                surf = pygame.display.get_surface()
                if surf:
                    self.screen = surf
                    self.screen_w, self.screen_h = surf.get_size()
                    self._recalcular_layout()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._finalizar_y_exportar()
                    self.is_running = False

                elif event.key == pygame.K_F11:
                    self._toggle_fullscreen()

                elif event.key in (pygame.K_SPACE, pygame.K_p):
                    self.is_paused = not self.is_paused
                    est = "PAUSADA" if self.is_paused else "EN EJECUCION"
                    self.dashboard.set_banner(f"Simulacion {est}")

                elif event.key == pygame.K_UP:
                    self.sim.lam = round(min(50.0, self.sim.lam + 2.0), 1)
                    self.dashboard.set_banner(f"Tasa lambda incrementada a {self.sim.lam} paq/s")

                elif event.key == pygame.K_DOWN:
                    self.sim.lam = round(max(2.0, self.sim.lam - 2.0), 1)
                    self.dashboard.set_banner(f"Tasa lambda reducida a {self.sim.lam} paq/s")

                elif event.key == pygame.K_RIGHT:
                    self.sim.mu = round(min(50.0, self.sim.mu + 2.0), 1)
                    for r in self.sim.routers.values():
                        r.mu = self.sim.mu
                    self.dashboard.set_banner(f"Tasa mu incrementada a {self.sim.mu} paq/s")

                elif event.key == pygame.K_LEFT:
                    self.sim.mu = round(max(2.0, self.sim.mu - 2.0), 1)
                    for r in self.sim.routers.values():
                        r.mu = self.sim.mu
                    self.dashboard.set_banner(f"Tasa mu reducida a {self.sim.mu} paq/s")

                elif event.key == pygame.K_1:
                    self.sim_speed = 0.25
                    self.dashboard.set_banner("Velocidad: 0.25x")
                elif event.key == pygame.K_2:
                    self.sim_speed = 0.5
                    self.dashboard.set_banner("Velocidad: 0.5x")
                elif event.key == pygame.K_3:
                    self.sim_speed = 1.0
                    self.dashboard.set_banner("Velocidad: 1.0x")
                elif event.key == pygame.K_4:
                    self.sim_speed = 2.0
                    self.dashboard.set_banner("Velocidad: 2.0x")
                elif event.key == pygame.K_5:
                    self.sim_speed = 4.0
                    self.dashboard.set_banner("Velocidad: 4.0x")

                elif event.key == pygame.K_F1:
                    self._toggle_link_by_key("S1-R1")
                elif event.key == pygame.K_F2:
                    self._toggle_link_by_key("S2-R2")
                elif event.key == pygame.K_F3:
                    self._toggle_link_by_key("S3-R3")

                elif event.key == pygame.K_e:
                    self._exportar_y_auditar()

                elif event.key == pygame.K_F12:
                    self._capturar_pantalla()

                elif event.key == pygame.K_r:
                    self._reiniciar_simulacion()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if mx < self.net_w:
                    self._handle_network_click(mx, my)
                else:
                    self._handle_hud_click(mx, my)

    def _handle_network_click(self, mx: int, my: int) -> None:
        for lid, link in {**self.sim.ingress_links, **self.sim.egress_links}.items():
            x1 = self.sim._get_node_x(link.from_node_id)
            y1 = self.sim._get_node_y(link.from_node_id)
            x2 = self.sim._get_node_x(link.to_node_id)
            y2 = self.sim._get_node_y(link.to_node_id)
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            if abs(mx - mid_x) < 22 and abs(my - mid_y) < 22:
                self._toggle_link_by_key(lid)
                return

    def _handle_hud_click(self, mx: int, my: int) -> None:
        if self.dashboard.btn_pause.rect.collidepoint(mx, my):
            self.is_paused = not self.is_paused
            est = "PAUSADA" if self.is_paused else "EN EJECUCION"
            self.dashboard.set_banner(f"Simulacion {est}")

        elif self.dashboard.btn_export.rect.collidepoint(mx, my):
            self._exportar_y_auditar()

        elif self.dashboard.btn_lam_up.rect.collidepoint(mx, my):
            self.sim.lam = round(min(50.0, self.sim.lam + 2.0), 1)
            self.dashboard.set_banner(f"Lambda = {self.sim.lam} paq/s")

        elif self.dashboard.btn_lam_down.rect.collidepoint(mx, my):
            self.sim.lam = round(max(2.0, self.sim.lam - 2.0), 1)
            self.dashboard.set_banner(f"Lambda = {self.sim.lam} paq/s")

        elif self.dashboard.btn_mu_up.rect.collidepoint(mx, my):
            self.sim.mu = round(min(50.0, self.sim.mu + 2.0), 1)
            for r in self.sim.routers.values():
                r.mu = self.sim.mu
            self.dashboard.set_banner(f"Mu = {self.sim.mu} paq/s")

        elif self.dashboard.btn_mu_down.rect.collidepoint(mx, my):
            self.sim.mu = round(max(2.0, self.sim.mu - 2.0), 1)
            for r in self.sim.routers.values():
                r.mu = self.sim.mu
            self.dashboard.set_banner(f"Mu = {self.sim.mu} paq/s")

        elif self.dashboard.btn_toggle_link.rect.collidepoint(mx, my):
            self._toggle_link_by_key("S1-R1")

        elif self.dashboard.btn_fullscreen.rect.collidepoint(mx, my):
            self._toggle_fullscreen()

        elif self.dashboard.btn_speed_025x.rect.collidepoint(mx, my):
            self.sim_speed = 0.25
            self.dashboard.set_banner("Velocidad: 0.25x")
        elif self.dashboard.btn_speed_05x.rect.collidepoint(mx, my):
            self.sim_speed = 0.5
            self.dashboard.set_banner("Velocidad: 0.5x")
        elif self.dashboard.btn_speed_1x.rect.collidepoint(mx, my):
            self.sim_speed = 1.0
            self.dashboard.set_banner("Velocidad: 1.0x")
        elif self.dashboard.btn_speed_2x.rect.collidepoint(mx, my):
            self.sim_speed = 2.0
            self.dashboard.set_banner("Velocidad: 2.0x")
        elif self.dashboard.btn_speed_4x.rect.collidepoint(mx, my):
            self.sim_speed = 4.0
            self.dashboard.set_banner("Velocidad: 4.0x")

        elif self.dashboard.btn_reset.rect.collidepoint(mx, my):
            self._reiniciar_simulacion()

    def _toggle_link_by_key(self, link_id: str) -> None:
        estado_activo = self.sim.toggle_enlace(link_id)
        txt = "OPERATIVO" if estado_activo else "CAIDO"
        self.dashboard.set_banner(f"Enlace {link_id}: {txt}")

    def _reiniciar_simulacion(self) -> None:
        lam = self.sim.lam
        mu = self.sim.mu
        self.sim = NetworkSimulation(
            lam=lam,
            mu=mu,
            capacidad_s=CAPACIDAD_BUFFER_S,
            umbral_s=UMBRAL_REABASTECER_S,
            lote_q=LOTE_REABASTECER_Q,
        )
        self.sim.actualizar_dimensiones_pantalla(self.net_w, self.screen_h)
        self.dashboard.set_banner("Simulacion reiniciada con exito.")

    def _toggle_fullscreen(self) -> None:
        self.is_maximized = not self.is_maximized
        if self.is_maximized:
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((max(1100, info.current_w - 40), max(650, info.current_h - 60)), pygame.RESIZABLE)
            self.dashboard.set_banner("Ventana expandida activa (F11 para restaurar)")
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            self.dashboard.set_banner("Ventana estandar restaurada")
        self._recalcular_layout()

    def _recalcular_layout(self) -> None:
        w = self.screen.get_width()
        h = self.screen.get_height()
        self.screen_w = w
        self.screen_h = h
        self.hud_w = min(480, max(380, int(w * 0.32)))
        self.net_w = w - self.hud_w
        self.sim.actualizar_dimensiones_pantalla(self.net_w, h)
        self.dashboard.actualizar_dimensiones(self.net_w, self.hud_w, h)

    def _update_simulation(self, dt: float) -> None:
        sim_delta = dt * self.sim_speed
        target_time = self.sim.env.now + sim_delta

        try:
            self.sim.env.run(until=target_time)
        except Exception:
            pass

        now = self.sim.env.now
        todos = list(self.sim.ingress_links.values()) + list(self.sim.egress_links.values())
        for link in todos:
            for pkt in link.packets_in_transit:
                elapsed = now - pkt.t_link_start
                dur = max(0.05, pkt.travel_time)
                pkt.progress = min(1.0, max(0.0, elapsed / dur))

    def _capturar_pantalla(self, ruta: Union[str, Path] = "captura_simulacion.png") -> Path:
        ruta_p = Path(ruta)
        if not ruta_p.is_absolute() and len(ruta_p.parts) == 1:
            ruta_p = OUTPUTS_DIR / ruta_p.name
        ruta_p.parent.mkdir(parents=True, exist_ok=True)

        try:
            pygame.image.save(self.screen, str(ruta_p))
            self.dashboard.set_banner(f"Captura guardada en {ruta_p.name}")
            print(f"Captura de pantalla guardada en: {ruta_p}")
        except Exception as ex:
            print(f"Error al guardar captura: {ex}")
        return ruta_p

    def _exportar_y_auditar(self) -> Tuple[Path, Path]:
        """Exporta el reporte .txt, ejecuta la auditoria y genera el informe Word .docx."""
        self.dashboard.set_banner("Exportando reporte y consultando auditoria...")
        ruta_img = self._capturar_pantalla("captura_simulacion.png")

        metricas = self.sim.obtener_metricas_completas()
        ruta_txt = OUTPUTS_DIR / "reporte_simulacion.txt"
        diag_ia = self.auditor.ejecutar_auditoria_completa(metricas, ruta_txt)
        self.sim.exportar_eventos_log(OUTPUTS_DIR / "eventos_desempeno.log")

        ruta_docx = OUTPUTS_DIR / "Informe_Tecnico_Simulador_Redes.docx"
        DocxReportService.compilar_informe_docx(
            metricas=metricas,
            diagnostico_ia=diag_ia,
            ruta_imagen=ruta_img,
            destino_docx=ruta_docx,
        )

        self.dashboard.set_banner("Reporte TXT y Documento DOCX generados con exito.")
        return ruta_txt, ruta_docx

    def _finalizar_y_exportar(self) -> None:
        print("\nCerrando simulador: guardando estado final y exportando reportes...")
        try:
            self._exportar_y_auditar()
        except Exception as ex:
            print(f"Aviso durante exportacion final: {ex}")

    def _draw(self) -> None:
        self.renderer.draw_network(self.screen, self.sim, self.net_w, self.screen_h)
        self.dashboard.draw(self.screen, self.sim, self.is_paused, self.sim_speed, self.is_maximized)
        pygame.display.flip()
