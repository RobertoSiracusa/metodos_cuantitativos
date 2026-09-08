"""
main.py
==============================================================================
Punto de Entrada Principal: SIMULADOR DINÁMICO DE REDES DE COMPUTADORAS
Facultad de Ingeniería - Universidad José Antonio Páez
Cátedra: Métodos Cuantitativos y Simulación

Entorno de Desarrollo: Python (Pygame, SimPy, SciPy, Requests, python-docx)

Integra:
1. Simulación de Eventos Discretos (SimPy) sincronizada a 60 FPS con Pygame.
2. Teoría de Colas (M/M/1/K) con llegadas de Poisson y servicio exponencial.
3. Modelos de Inventario para gestión de buffers con política (s, Q) y costos.
4. Algoritmo Húngaro (SciPy / Nativo) para enrutamiento dinámico óptimo.
5. Exportación a TXT ('reporte_simulacion.txt') y auditoría automatizada con
   la API de Google Gemini (o Motor Analítico de Contingencia).
6. Captura automática para la elaboración del Informe Técnico en Word (.docx).
==============================================================================
"""

import os
import sys
import time
import pygame

# Asegurar encoding UTF-8 en consolas Windows para evitar UnicodeEncodeError
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Verificación de dependencias críticas
try:
    import simpy
    import numpy
    import scipy
    import requests
except ImportError as e:
    print("\n" + "=" * 60)
    print(f"ERROR: Dependencia faltante detectada ({e}).")
    print("Por favor ejecuta: pip install -r requirements.txt")
    print("=" * 60 + "\n")
    sys.exit(1)

from red_simulacion import (
    NetworkSimulation,
    LAMBDA_DEFECTO,
    MU_DEFECTO,
    CAPACIDAD_BUFFER_S,
    UMBRAL_REABASTECER_S,
    LOTE_REABASTECER_Q
)
from gui_network import (
    NetworkRenderer,
    NetworkDashboard,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    NET_VIEW_WIDTH
)
from gemini_client import GeminiNetworkAuditor


class NetworkSimulatorApp:
    """Aplicación principal del Simulador Dinámico de Redes."""

    def __init__(self):
        pygame.init()
        pygame.font.init()

        # Inicializar ventana redimensionable y maximizarla (Pantalla Expandida)
        self.screen_w = SCREEN_WIDTH
        self.screen_h = SCREEN_HEIGHT
        self.is_maximized = True
        self.is_fullscreen = False

        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h), pygame.RESIZABLE)
        pygame.display.set_caption("Simulador Dinámico de Redes de Computadoras - Métodos Cuantitativos (UJAP)")

        # Maximizar de forma nativa en el sistema operativo (Pantalla Expandida con barra de tareas accesible)
        self._maximizar_ventana()

        self.clock = pygame.time.Clock()
        self.fps = 60

        # Crear simulación de red con SimPy
        self.sim = NetworkSimulation(
            lam=LAMBDA_DEFECTO,
            mu=MU_DEFECTO,
            capacidad_s=CAPACIDAD_BUFFER_S,
            umbral_s=UMBRAL_REABASTECER_S,
            lote_q=LOTE_REABASTECER_Q
        )

        # Dimensionamiento adaptable del HUD
        self.hud_w = min(500, max(390, int(self.screen_w * 0.32)))
        self.net_w = self.screen_w - self.hud_w

        # Módulos gráficos
        self.renderer = NetworkRenderer()
        self.dashboard = NetworkDashboard(x_offset=self.net_w, width=self.hud_w, height=self.screen_h)
        self.auditor = GeminiNetworkAuditor()

        # Ajustar posiciones de red a la resolución
        self.sim.actualizar_dimensiones_pantalla(self.net_w, self.screen_h)

        # Variables de control
        self.is_running = True
        self.is_paused = False
        self.sim_speed = 0.5  # Velocidad por defecto suave y didáctica (0.5x)
        self.dashboard.set_banner("Ventana Expandida Activa (F11 para restaurar) | Velocidad inicial: 0.5x", duracion=6.0)

        print("\n" + "=" * 65)
        print("SIMULADOR DINAMICO DE REDES DE COMPUTADORAS INICIADO")
        print("=" * 65)
        print("  - Pantalla: PANTALLA EXPANDIDA / MAXIMIZADA [F11 para Alternar]")
        print("  - Controles de Teclado:")
        print("      [ESPACIO / P]: Pausar / Reanudar la simulación")
        print("      [1 / 2 / 3 / 4 / 5]: Ajustar velocidad (0.25x, 0.5x, 1x, 2x, 4x)")
        print("      [ [ / ] ]: Reducir / Aumentar velocidad paso a paso")
        print("      [FLECHA ARRIBA / ABAJO]: Modificar Tasa de Llegada (lambda)")
        print("      [FLECHA DER / IZQ]: Modificar Tasa de Servicio (mu)")
        print("      [F1 / F2 / F3] o Clic: Simular caída/restauración de enlaces")
        print("      [F11]: Alternar Ventana Expandida (Maximizada) / Restaurada")
        print("      [E]: Exportar 'reporte_simulacion.txt' y auditar con Gemini")
        print("      [F12]: Capturar pantalla para el Informe Técnico (.png)")
        print("      [R]: Reiniciar simulación desde cero")
        print("      [ESC]: Exportar reporte y salir de la aplicación")
        print("=" * 65 + "\n")

    def run(self):
        """Ciclo principal de ejecución a 60 FPS."""
        while self.is_running:
            dt = self.clock.tick(self.fps) / 1000.0  # Tiempo delta real en segundos

            self._handle_events()

            if not self.is_paused:
                self._update_simulation(dt)

            self.renderer.update_animation(dt)
            mouse_pos = pygame.mouse.get_pos()
            self.dashboard.update(dt, mouse_pos)

            self._draw()

        pygame.quit()

    def _handle_events(self):
        """Procesa entradas de usuario por teclado y ratón."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._finalizar_y_exportar()
                self.is_running = False

            elif event.type in (pygame.VIDEORESIZE, getattr(pygame, 'WINDOWRESIZED', 32778), getattr(pygame, 'WINDOWSIZECHANGED', 32779)):
                surf = pygame.display.get_surface()
                if surf:
                    self.screen = surf
                    self.screen_w, self.screen_h = surf.get_size()
                    self._recalcular_layout()
                    try:
                        import ctypes
                        hwnd = pygame.display.get_wm_info().get("window")
                        if hwnd:
                            self.is_maximized = bool(ctypes.windll.user32.IsZoomed(hwnd))
                    except Exception:
                        pass

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._finalizar_y_exportar()
                    self.is_running = False

                elif event.key == pygame.K_F11:
                    self._toggle_pantalla_expandida()

                elif event.key in (pygame.K_SPACE, pygame.K_p):
                    self.is_paused = not self.is_paused
                    estado = "PAUSADA" if self.is_paused else "EN EJECUCIÓN"
                    self.dashboard.set_banner(f"Simulación {estado}")

                elif event.key == pygame.K_UP:
                    self.sim.lam = round(min(50.0, self.sim.lam + 2.0), 1)
                    self.dashboard.set_banner(f"λ incrementado a {self.sim.lam} paq/s")

                elif event.key == pygame.K_DOWN:
                    self.sim.lam = round(max(2.0, self.sim.lam - 2.0), 1)
                    self.dashboard.set_banner(f"λ reducido a {self.sim.lam} paq/s")

                elif event.key == pygame.K_RIGHT:
                    self.sim.mu = round(min(50.0, self.sim.mu + 2.0), 1)
                    for r in self.sim.routers.values():
                        r.mu = self.sim.mu
                    self.dashboard.set_banner(f"μ incrementado a {self.sim.mu} paq/s")

                elif event.key == pygame.K_LEFT:
                    self.sim.mu = round(max(2.0, self.sim.mu - 2.0), 1)
                    for r in self.sim.routers.values():
                        r.mu = self.sim.mu
                    self.dashboard.set_banner(f"μ reducido a {self.sim.mu} paq/s")

                # Control de velocidad por teclado
                elif event.key == pygame.K_1:
                    self.sim_speed = 0.25
                    self.dashboard.set_banner("Velocidad: 0.25x (Super Lenta / Observación Detallada)")
                elif event.key == pygame.K_2:
                    self.sim_speed = 0.5
                    self.dashboard.set_banner("Velocidad: 0.5x (Modo Didáctico Suave)")
                elif event.key == pygame.K_3:
                    self.sim_speed = 1.0
                    self.dashboard.set_banner("Velocidad: 1.0x (Tiempo Real Normal)")
                elif event.key == pygame.K_4:
                    self.sim_speed = 2.0
                    self.dashboard.set_banner("Velocidad: 2.0x (Rápido)")
                elif event.key == pygame.K_5:
                    self.sim_speed = 4.0
                    self.dashboard.set_banner("Velocidad: 4.0x (Acelerado)")

                elif event.key in (pygame.K_LEFTBRACKET, pygame.K_MINUS):
                    vels = [0.25, 0.5, 1.0, 2.0, 4.0]
                    idx = max(0, vels.index(self.sim_speed) - 1) if self.sim_speed in vels else 1
                    self.sim_speed = vels[idx]
                    self.dashboard.set_banner(f"Velocidad: {self.sim_speed}x")

                elif event.key in (pygame.K_RIGHTBRACKET, pygame.K_PLUS, pygame.K_EQUALS):
                    vels = [0.25, 0.5, 1.0, 2.0, 4.0]
                    idx = min(len(vels) - 1, vels.index(self.sim_speed) + 1) if self.sim_speed in vels else 2
                    self.sim_speed = vels[idx]
                    self.dashboard.set_banner(f"Velocidad: {self.sim_speed}x")

                # Simulación de caída de enlaces
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

    def _handle_network_click(self, mx: int, my: int):
        """Permite hacer clic sobre los enlaces o routers para provocar fallas controladas."""
        # Comprobar clic en enlaces
        for lid, link in {**self.sim.ingress_links, **self.sim.egress_links}.items():
            x1 = self.sim._get_node_x(link.from_node_id)
            y1 = self.sim._get_node_y(link.from_node_id)
            x2 = self.sim._get_node_x(link.to_node_id)
            y2 = self.sim._get_node_y(link.to_node_id)

            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            if abs(mx - mid_x) < 20 and abs(my - mid_y) < 20:
                self._toggle_link_by_key(lid)
                return

    def _handle_hud_click(self, mx: int, my: int):
        """Maneja clics sobre los botones del Dashboard."""
        if self.dashboard.btn_pause.rect.collidepoint(mx, my):
            self.is_paused = not self.is_paused
            estado = "PAUSADA" if self.is_paused else "EN EJECUCIÓN"
            self.dashboard.set_banner(f"Simulación {estado}")

        elif self.dashboard.btn_lam_up.rect.collidepoint(mx, my):
            self.sim.lam = round(min(50.0, self.sim.lam + 2.0), 1)
            self.dashboard.set_banner(f"λ incrementado a {self.sim.lam} paq/s")

        elif self.dashboard.btn_lam_down.rect.collidepoint(mx, my):
            self.sim.lam = round(max(2.0, self.sim.lam - 2.0), 1)
            self.dashboard.set_banner(f"λ reducido a {self.sim.lam} paq/s")

        elif self.dashboard.btn_mu_up.rect.collidepoint(mx, my):
            self.sim.mu = round(min(50.0, self.sim.mu + 2.0), 1)
            for r in self.sim.routers.values():
                r.mu = self.sim.mu
            self.dashboard.set_banner(f"μ incrementado a {self.sim.mu} paq/s")

        elif self.dashboard.btn_mu_down.rect.collidepoint(mx, my):
            self.sim.mu = round(max(2.0, self.sim.mu - 2.0), 1)
            for r in self.sim.routers.values():
                r.mu = self.sim.mu
            self.dashboard.set_banner(f"μ reducido a {self.sim.mu} paq/s")

        elif self.dashboard.btn_toggle_link.rect.collidepoint(mx, my):
            self._toggle_link_by_key("S1-R1")

        elif self.dashboard.btn_export.rect.collidepoint(mx, my):
            self._exportar_y_auditar()

        elif self.dashboard.btn_fullscreen.rect.collidepoint(mx, my):
            self._toggle_pantalla_expandida()

        elif self.dashboard.btn_speed_025x.rect.collidepoint(mx, my):
            self.sim_speed = 0.25
            self.dashboard.set_banner("Velocidad: 0.25x (Super Lenta / Observación)")

        elif self.dashboard.btn_speed_05x.rect.collidepoint(mx, my):
            self.sim_speed = 0.5
            self.dashboard.set_banner("Velocidad: 0.5x (Modo Didáctico Suave)")

        elif self.dashboard.btn_speed_1x.rect.collidepoint(mx, my):
            self.sim_speed = 1.0
            self.dashboard.set_banner("Velocidad: 1.0x (Tiempo Real Normal)")

        elif self.dashboard.btn_speed_2x.rect.collidepoint(mx, my):
            self.sim_speed = 2.0
            self.dashboard.set_banner("Velocidad: 2.0x (Rápido)")

        elif self.dashboard.btn_speed_4x.rect.collidepoint(mx, my):
            self.sim_speed = 4.0
            self.dashboard.set_banner("Velocidad: 4.0x (Acelerado)")

        elif self.dashboard.btn_reset.rect.collidepoint(mx, my):
            self._reiniciar_simulacion()

    def _toggle_link_by_key(self, link_id: str):
        estado_activo = self.sim.toggle_enlace(link_id)
        txt_estado = "OPERATIVO" if estado_activo else "CAÍDO / DESCONECTADO"
        self.dashboard.set_banner(f"Enlace {link_id}: {txt_estado}")

    def _reiniciar_simulacion(self):
        lam = self.sim.lam
        mu = self.sim.mu
        self.sim = NetworkSimulation(
            lam=lam,
            mu=mu,
            capacidad_s=CAPACIDAD_BUFFER_S,
            umbral_s=UMBRAL_REABASTECER_S,
            lote_q=LOTE_REABASTECER_Q
        )
        self.sim.actualizar_dimensiones_pantalla(self.net_w, self.screen_h)
        self.dashboard.set_banner("Simulación reiniciada con éxito.")

    def _maximizar_ventana(self):
        """Maximiza la ventana de forma nativa para ocupar toda la pantalla visible (Pantalla Expandida)."""
        try:
            import ctypes
            wm_info = pygame.display.get_wm_info()
            hwnd = wm_info.get("window")
            if hwnd:
                # SW_MAXIMIZE = 3
                ctypes.windll.user32.ShowWindow(hwnd, 3)
                pygame.event.pump()
                self.is_maximized = True
        except Exception:
            # Fallback multiplataforma
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((max(1100, info.current_w - 40), max(650, info.current_h - 70)), pygame.RESIZABLE)
            self.is_maximized = True

        surf = pygame.display.get_surface()
        if surf:
            self.screen = surf
            self.screen_w, self.screen_h = surf.get_size()

    def _toggle_pantalla_expandida(self):
        """Alterna entre Ventana Expandida (Maximizada) y Ventana Normal Restaurada."""
        try:
            import ctypes
            wm_info = pygame.display.get_wm_info()
            hwnd = wm_info.get("window")
            if hwnd:
                es_max = bool(ctypes.windll.user32.IsZoomed(hwnd))
                if es_max:
                    # SW_RESTORE = 9
                    ctypes.windll.user32.ShowWindow(hwnd, 9)
                    self.is_maximized = False
                    self.dashboard.set_banner("Ventana normal restaurada (F11 para expandir)")
                else:
                    # SW_MAXIMIZE = 3
                    ctypes.windll.user32.ShowWindow(hwnd, 3)
                    self.is_maximized = True
                    self.dashboard.set_banner("Ventana expandida / maximizada (F11 para restaurar)")
                pygame.event.pump()
                surf = pygame.display.get_surface()
                if surf:
                    self.screen = surf
                    self.screen_w, self.screen_h = surf.get_size()
                    self._recalcular_layout()
                return
        except Exception:
            pass

        # Fallback sin ctypes
        self.is_maximized = not self.is_maximized
        if self.is_maximized:
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((max(1100, info.current_w - 40), max(650, info.current_h - 70)), pygame.RESIZABLE)
            self.dashboard.set_banner("Ventana expandida (F11 para restaurar)")
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            self.dashboard.set_banner("Ventana normal restaurada (F11 para expandir)")
        self._recalcular_layout()

    def _recalcular_layout(self):
        """Reconfigura los tamaños y posiciones de red y HUD según la resolución actual."""
        w = self.screen.get_width()
        h = self.screen.get_height()
        self.screen_w = w
        self.screen_h = h

        self.hud_w = min(500, max(390, int(w * 0.32)))
        self.net_w = w - self.hud_w

        self.sim.actualizar_dimensiones_pantalla(self.net_w, h)
        self.dashboard.actualizar_dimensiones(self.net_w, self.hud_w, h)

    def _update_simulation(self, dt: float):
        """Avanza el entorno SimPy y actualiza el progreso cinemático de los paquetes."""
        sim_delta = dt * self.sim_speed
        target_sim_time = self.sim.env.now + sim_delta

        try:
            self.sim.env.run(until=target_sim_time)
        except Exception as ex:
            pass

        # Actualizar progreso visual de paquetes en tránsito por enlaces
        now = self.sim.env.now
        todos_enlaces = list(self.sim.ingress_links.values()) + list(self.sim.egress_links.values())
        for link in todos_enlaces:
            for pkt in link.packets_in_transit:
                elapsed = now - pkt.t_link_start
                dur = max(0.05, pkt.travel_time)
                pkt.progress = min(1.0, max(0.0, elapsed / dur))

    def _capturar_pantalla(self, ruta: str = "captura_simulacion.png"):
        """Guarda una captura de la interfaz de simulación para el informe técnico."""
        try:
            pygame.image.save(self.screen, ruta)
            self.dashboard.set_banner(f"Captura guardada en {ruta}")
            print(f"📸 Captura de pantalla guardada: {ruta}")
        except Exception as e:
            print(f"Error al guardar captura: {e}")

    def _exportar_y_auditar(self):
        """Exporta el reporte a TXT y dispara la auditoría con la API externa (Tecla E o botón HUD)."""
        self.dashboard.set_banner("Exportando reporte TXT y consultando API externa...")
        self._capturar_pantalla("captura_simulacion.png")

        metricas = self.sim.obtener_metricas_completas()
        try:
            self.auditor.auditar_simulacion(metricas, "reporte_simulacion.txt")
            self.dashboard.set_banner("¡Reporte exportado y analizado por API con éxito!")
        except Exception as ex:
            print(f"Error durante auditoría de API: {ex}")
            self.dashboard.set_banner("Error al procesar reporte con la API.")

    def _finalizar_y_exportar(self):
        """Asegura la exportación del reporte estructurado y la auditoría con API al cerrar el simulador (ESC o salir)."""
        print("\n" + "=" * 65)
        print("CERRANDO SIMULADOR: EXPORTANDO REPORTE FINAL Y CONSULTANDO API...")
        print("=" * 65)
        metricas = self.sim.obtener_metricas_completas()
        try:
            self.auditor.auditar_simulacion(metricas, "reporte_simulacion.txt")
        except Exception as ex:
            print(f"Error durante la auditoría de API al salir: {ex}")
            self.auditor.generar_reporte_txt(metricas, "reporte_simulacion.txt")
        self._capturar_pantalla("captura_simulacion.png")

    def _draw(self):
        """Renderiza en pantalla el canvas de la red y el HUD con dimensiones dinámicas."""
        self.renderer.draw_network(self.screen, self.sim, self.net_w, self.screen_h)
        self.dashboard.draw(self.screen, self.sim, self.is_paused, self.sim_speed, self.is_maximized)
        pygame.display.flip()


def main():
    app = NetworkSimulatorApp()
    app.run()


if __name__ == "__main__":
    main()
