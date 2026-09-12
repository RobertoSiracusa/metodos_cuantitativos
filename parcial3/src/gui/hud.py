"""
Panel lateral de telemetria (HUD), comun a las dos vistas.

Lee unicamente de `controller` y de `controller.sim` en cada frame: no guarda
ningun valor de dominio de una llamada a la siguiente. El unico estado propio
es un contador de parpadeo puramente visual (fase del parpadeo de
"REPONIENDO"), que vive en la vista de fabrica, no aca.
"""

from typing import Dict, List, Tuple

import pygame

from src.gui.styles import (
    ANCHO_HUD,
    ANCHO_PLANTA,
    ALTO_VENTANA,
    COLOR_ALERTA,
    COLOR_BORDE,
    COLOR_CRITICO,
    COLOR_OK,
    COLOR_PANEL_HUD,
    COLOR_TARJETA,
    COLOR_TEXTO_ACENTO,
    COLOR_TEXTO_MUTED,
    COLOR_TEXTO_PRINCIPAL,
)


def _formatear_hhmmss(segundos: float) -> str:
    """Formatea segundos simulados como HH:MM:SS."""
    total = max(0, int(segundos))
    horas, resto = divmod(total, 3600)
    minutos, segs = divmod(resto, 60)
    return f"{horas:02d}:{minutos:02d}:{segs:02d}"


class Hud:
    """Dibuja el panel derecho de telemetria para la vista activa."""

    def __init__(self, fonts: Dict[str, "pygame.font.Font"]) -> None:
        self.fonts = fonts

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------

    def dibujar(self, surface: pygame.Surface, controller, fps: float) -> None:
        """Punto de entrada: dibuja el fondo del panel y delega en el problema."""
        rect = pygame.Rect(ANCHO_PLANTA, 0, ANCHO_HUD, ALTO_VENTANA)
        pygame.draw.rect(surface, COLOR_PANEL_HUD, rect)
        pygame.draw.line(surface, COLOR_BORDE, (ANCHO_PLANTA, 0), (ANCHO_PLANTA, ALTO_VENTANA), 2)

        x = ANCHO_PLANTA + 14
        y = self._encabezado(surface, x, controller, fps)

        if controller.problema == 1:
            self._panel_fabrica(surface, x, y, controller)
        else:
            self._panel_cluster(surface, x, y, controller)

    # ------------------------------------------------------------------
    # Encabezado comun: tiempo, progreso, escala, FPS y estado de pausa
    # ------------------------------------------------------------------

    def _encabezado(self, surface: pygame.Surface, x: int, controller, fps: float) -> int:
        y = 14
        titulo = "PROBLEMA 1 - FABRICA" if controller.problema == 1 else "PROBLEMA 2 - CLUSTER"
        surface.blit(self.fonts["bold"].render(titulo, True, COLOR_TEXTO_ACENTO), (x, y))
        y += 24

        tiempo_txt = (
            f"T: {_formatear_hhmmss(controller.sim.tiempo_actual)} / "
            f"{_formatear_hhmmss(controller.tiempo_objetivo_s)}"
        )
        surface.blit(self.fonts["normal"].render(tiempo_txt, True, COLOR_TEXTO_PRINCIPAL), (x, y))
        y += 18

        # Barra de progreso
        ancho_barra = ANCHO_HUD - 28
        pygame.draw.rect(surface, (20, 24, 30), (x, y, ancho_barra, 8), border_radius=2)
        avance = round(ancho_barra * controller.progreso)
        pygame.draw.rect(surface, COLOR_OK, (x, y, avance, 8), border_radius=2)
        y += 16

        estado_txt = "MOTOR DETENIDO" if controller.pausa_total else (
            "ANIMACION EN PAUSA" if controller.pausa_animacion else "EN MARCHA"
        )
        color_estado = COLOR_CRITICO if controller.pausa_total else (
            COLOR_ALERTA if controller.pausa_animacion else COLOR_OK
        )
        surface.blit(self.fonts["chico"].render(estado_txt, True, color_estado), (x, y))

        escala_txt = f"Escala: x{int(controller.escala_tiempo)} | {fps:4.0f} FPS"
        escala_render = self.fonts["chico"].render(escala_txt, True, COLOR_TEXTO_MUTED)
        surface.blit(escala_render, (x + 150, y))
        y += 22

        if controller.terminado:
            fin = self.fonts["bold"].render("CORRIDA FINALIZADA", True, COLOR_TEXTO_ACENTO)
            surface.blit(fin, (x, y))
            y += 20

        pygame.draw.line(surface, COLOR_BORDE, (x, y), (x + ancho_barra, y), 1)
        y += 10
        return y

    # ------------------------------------------------------------------
    # Panel Problema 1
    # ------------------------------------------------------------------

    def _panel_fabrica(self, surface: pygame.Surface, x: int, y: int, controller) -> None:
        sim = controller.sim
        m = sim.obtener_metricas()
        teo = sim.modelo_analitico.resumen()

        filas: List[Tuple[str, str]] = [
            ("Ordenes generadas", f"{sim.estadisticas.ordenes_generadas}"),
            ("Ordenes completadas", f"{sim.estadisticas.ordenes_completadas}"),
            ("En cola ahora", f"{len(sim.ordenes_en_cola)}"),
            ("Wq simulado / teorico", f"{m['wq_promedio_min']:.2f} / {teo['wq_min']:.2f} min"),
            ("W simulado / teorico", f"{m['w_promedio_min']:.2f} / {teo['w_min']:.2f} min"),
            ("L simulado / teorico", f"{m['l_promedio']:.2f} / {teo['l']:.2f}"),
            ("Lq simulado / teorico", f"{m['lq_promedio']:.2f} / {teo['lq']:.2f}"),
            ("Utilizacion estacion", f"{m['utilizacion_estacion_pct']:.1f} %"),
            ("Stock actual / umbral", f"{sim.inventario.nivel} / {sim.inventario.umbral_critico}"),
            ("Pedidos disparados", f"{sim.inventario.pedidos_disparados}"),
            ("Lotes recibidos", f"{sim.inventario.lotes_recibidos}"),
            ("Nivel minimo alcanzado", f"{sim.inventario.nivel_minimo}"),
            ("Paradas de linea", f"{sim.estadisticas.paradas_por_falta_stock}"),
        ]
        self._dibujar_tarjeta_filas(surface, x, y, "TELEMETRIA - FABRICA", filas)

    # ------------------------------------------------------------------
    # Panel Problema 2
    # ------------------------------------------------------------------

    def _panel_cluster(self, surface: pygame.Surface, x: int, y: int, controller) -> None:
        sim = controller.sim
        m = sim.obtener_metricas()

        filas: List[Tuple[str, str]] = [
            ("Trafico actual", f"{sim.trafico_actual:.2f} Gbps"),
            ("Temperatura actual", f"{sim.temperatura_actual:.2f} C"),
            ("Temperatura equilibrio", f"{sim.temperatura_equilibrio_actual:.2f} C"),
            ("Eficiencia actual", f"{sim.eficiencia_actual * 100.0:.1f} %"),
            ("Throughput actual", f"{sim.throughput_actual:.2f} Gbps"),
            ("TB acumulados", f"{sim.tb_acumulados:.4f} TB"),
            ("% tiempo con throttling", f"{m['pct_tiempo_throttling']:.1f} %"),
        ]
        self._dibujar_tarjeta_filas(surface, x, y, "TELEMETRIA - CLUSTER", filas)

    # ------------------------------------------------------------------
    # Utilidad de dibujo compartida
    # ------------------------------------------------------------------

    def _dibujar_tarjeta_filas(
        self, surface: pygame.Surface, x: int, y: int, titulo: str, filas: List[Tuple[str, str]]
    ) -> int:
        alto_fila = 22
        alto = 34 + alto_fila * len(filas)
        ancho = ANCHO_HUD - 28
        rect = pygame.Rect(x, y, ancho, alto)
        pygame.draw.rect(surface, COLOR_TARJETA, rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_BORDE, rect, width=1, border_radius=6)

        surface.blit(self.fonts["bold"].render(titulo, True, COLOR_TEXTO_PRINCIPAL), (x + 10, y + 8))

        fila_y = y + 32
        for etiqueta, valor in filas:
            surface.blit(
                self.fonts["chico"].render(etiqueta, True, COLOR_TEXTO_MUTED), (x + 10, fila_y)
            )
            surface.blit(
                self.fonts["chico"].render(valor, True, COLOR_TEXTO_PRINCIPAL), (x + 195, fila_y)
            )
            fila_y += alto_fila

        return y + alto + 10


def _selfcheck() -> None:
    """Verifica el formateo de tiempo, la unica logica pura de este modulo."""
    assert _formatear_hhmmss(0) == "00:00:00"
    assert _formatear_hhmmss(59) == "00:00:59"
    assert _formatear_hhmmss(60) == "00:01:00"
    assert _formatear_hhmmss(3661) == "01:01:01"
    assert _formatear_hhmmss(-5) == "00:00:00"
    print("selfcheck hud: OK")


if __name__ == "__main__":
    _selfcheck()
