"""
Vista del Problema 2: cluster de servidores (simulacion continua).

Dibuja, en la zona de planta (x de 0 a ANCHO_PLANTA):
  - el nodo del servidor, cuyo color interpola de azul a rojo critico segun
    la temperatura actual
  - una barra termica vertical con marca de umbral de throttling (70 C)
  - el oscilograma de `sim.historial_temp` (deque ya acotado por el motor)
  - particulas de trafico entrante, con densidad proporcional a trafico_actual
  - el banner de alarma cuando hay thermal throttling activo

El unico estado propio de esta vista es la posicion de las particulas de
trafico (puramente visual); todo dato de dominio se lee de `sim` en cada frame.
"""

import math
from typing import Dict, List

import pygame

from src.gui.styles import (
    ANCHO_PLANTA,
    ALTO_VENTANA,
    COLOR_ALERTA,
    COLOR_BORDE,
    COLOR_CRITICO,
    COLOR_FONDO_PLANTA,
    COLOR_TEXTO_MUTED,
    COLOR_TEXTO_PRINCIPAL,
    color_por_temperatura,
)

NODO_RECT = pygame.Rect(280, 220, 220, 220)
BARRA_TERMICA_RECT = pygame.Rect(600, 100, 40, 500)
TEMP_ESCALA_MIN_C = 20.0
TEMP_ESCALA_MAX_C = 100.0
UMBRAL_THROTTLING_C = 70.0

OSCILOGRAMA_RECT = pygame.Rect(20, 460, 550, 140)

MAX_PARTICULAS = 24
VELOCIDAD_PARTICULA_PX_S = 90.0


class ParticulaTrafico:
    """Punto visual que entra al nodo desde la izquierda. Sin estado de dominio."""

    __slots__ = ("y", "x")

    def __init__(self, y: float, x: float) -> None:
        self.y = y
        self.x = x


class ClusterView:
    """Vista interactiva del Problema 2. Estado propio: solo lo visual."""

    def __init__(self, fonts: Dict[str, "pygame.font.Font"]) -> None:
        self.fonts = fonts
        self._particulas: List[ParticulaTrafico] = []
        self._acumulador_spawn: float = 0.0

    # ------------------------------------------------------------------
    # Actualizacion puramente visual
    # ------------------------------------------------------------------

    def actualizar(self, sim, dt_anim: float) -> None:
        """Mueve las particulas de trafico y genera nuevas segun la densidad actual."""
        if dt_anim <= 0.0:
            return

        for particula in self._particulas:
            particula.x += VELOCIDAD_PARTICULA_PX_S * dt_anim
        self._particulas = [p for p in self._particulas if p.x < NODO_RECT.centerx]

        # La cadencia de aparicion de particulas es proporcional al trafico actual.
        tasa_spawn_por_s = 0.6 * max(0.0, sim.trafico_actual)
        self._acumulador_spawn += tasa_spawn_por_s * dt_anim
        while self._acumulador_spawn >= 1.0 and len(self._particulas) < MAX_PARTICULAS:
            self._acumulador_spawn -= 1.0
            y = NODO_RECT.centery + ((len(self._particulas) * 37) % 160) - 80
            self._particulas.append(ParticulaTrafico(y=float(y), x=20.0))

    # ------------------------------------------------------------------
    # Dibujo
    # ------------------------------------------------------------------

    def dibujar(self, surface: pygame.Surface, sim) -> None:
        """Dibuja un frame completo de la vista de cluster."""
        rect_planta = pygame.Rect(0, 0, ANCHO_PLANTA, ALTO_VENTANA)
        pygame.draw.rect(surface, COLOR_FONDO_PLANTA, rect_planta)

        titulo = self.fonts["titulo"].render("PROBLEMA 2: CLUSTER DE SERVIDORES", True, COLOR_TEXTO_PRINCIPAL)
        surface.blit(titulo, (20, 16))

        self._dibujar_trafico(surface, sim)
        self._dibujar_nodo(surface, sim)
        self._dibujar_barra_termica(surface, sim)
        self._dibujar_oscilograma(surface, sim)

        if sim.throttling_activo:
            self._dibujar_alarma_throttling(surface)

    def _dibujar_trafico(self, surface: pygame.Surface, sim) -> None:
        for particula in self._particulas:
            pygame.draw.circle(surface, (56, 189, 248), (int(particula.x), int(particula.y)), 4)

        etiqueta = self.fonts["normal"].render(
            f"Trafico entrante: {sim.trafico_actual:.2f} Gbps", True, COLOR_TEXTO_MUTED
        )
        surface.blit(etiqueta, (20, 200))

    def _dibujar_nodo(self, surface: pygame.Surface, sim) -> None:
        color = color_por_temperatura(sim.temperatura_actual)
        pygame.draw.rect(surface, color, NODO_RECT, border_radius=10)
        pygame.draw.rect(surface, COLOR_BORDE, NODO_RECT, width=2, border_radius=10)

        titulo = self.fonts["bold"].render("NODO DEL SERVIDOR", True, COLOR_TEXTO_PRINCIPAL)
        surface.blit(titulo, (NODO_RECT.x, NODO_RECT.y - 22))

        temp_txt = self.fonts["titulo"].render(f"{sim.temperatura_actual:.1f} C", True, (10, 10, 10))
        surface.blit(temp_txt, (NODO_RECT.centerx - 45, NODO_RECT.centery - 15))

    def _dibujar_barra_termica(self, surface: pygame.Surface, sim) -> None:
        titulo = self.fonts["bold"].render("TEMPERATURA", True, COLOR_TEXTO_PRINCIPAL)
        surface.blit(titulo, (BARRA_TERMICA_RECT.x - 20, BARRA_TERMICA_RECT.y - 22))

        pygame.draw.rect(surface, (20, 24, 30), BARRA_TERMICA_RECT, border_radius=4)
        pygame.draw.rect(surface, COLOR_BORDE, BARRA_TERMICA_RECT, width=1, border_radius=4)

        rango = TEMP_ESCALA_MAX_C - TEMP_ESCALA_MIN_C
        fraccion = min(1.0, max(0.0, (sim.temperatura_actual - TEMP_ESCALA_MIN_C) / rango))
        alto_relleno = int(BARRA_TERMICA_RECT.height * fraccion)
        color = color_por_temperatura(sim.temperatura_actual)
        relleno = pygame.Rect(
            BARRA_TERMICA_RECT.x, BARRA_TERMICA_RECT.bottom - alto_relleno,
            BARRA_TERMICA_RECT.width, alto_relleno,
        )
        pygame.draw.rect(surface, color, relleno, border_radius=4)

        # Marca del umbral de throttling (70 C)
        fraccion_umbral = min(1.0, max(0.0, (UMBRAL_THROTTLING_C - TEMP_ESCALA_MIN_C) / rango))
        y_umbral = BARRA_TERMICA_RECT.bottom - int(BARRA_TERMICA_RECT.height * fraccion_umbral)
        pygame.draw.line(
            surface, COLOR_ALERTA,
            (BARRA_TERMICA_RECT.x - 4, y_umbral), (BARRA_TERMICA_RECT.right + 4, y_umbral), 2,
        )
        marca = self.fonts["chico"].render("70 C", True, COLOR_ALERTA)
        surface.blit(marca, (BARRA_TERMICA_RECT.right + 6, y_umbral - 8))

        numerico = self.fonts["chico"].render(
            f"{sim.temperatura_actual:.1f} C", True, COLOR_TEXTO_PRINCIPAL
        )
        surface.blit(numerico, (BARRA_TERMICA_RECT.x - 10, BARRA_TERMICA_RECT.bottom + 6))

    def _dibujar_oscilograma(self, surface: pygame.Surface, sim) -> None:
        pygame.draw.rect(surface, (20, 24, 30), OSCILOGRAMA_RECT, border_radius=4)
        pygame.draw.rect(surface, COLOR_BORDE, OSCILOGRAMA_RECT, width=1, border_radius=4)

        titulo = self.fonts["normal"].render("Historial de temperatura", True, COLOR_TEXTO_MUTED)
        surface.blit(titulo, (OSCILOGRAMA_RECT.x, OSCILOGRAMA_RECT.y - 20))

        historial = list(sim.historial_temp)
        if len(historial) < 2:
            return

        rango = TEMP_ESCALA_MAX_C - TEMP_ESCALA_MIN_C
        fraccion_umbral = min(1.0, max(0.0, (UMBRAL_THROTTLING_C - TEMP_ESCALA_MIN_C) / rango))
        y_umbral = OSCILOGRAMA_RECT.bottom - int(OSCILOGRAMA_RECT.height * fraccion_umbral)
        self._linea_punteada(
            surface, (OSCILOGRAMA_RECT.x, y_umbral), (OSCILOGRAMA_RECT.right, y_umbral), COLOR_ALERTA
        )

        puntos = []
        n = len(historial)
        for i, temp in enumerate(historial):
            x = OSCILOGRAMA_RECT.x + (i / max(1, n - 1)) * OSCILOGRAMA_RECT.width
            fraccion = min(1.0, max(0.0, (temp - TEMP_ESCALA_MIN_C) / rango))
            y = OSCILOGRAMA_RECT.bottom - fraccion * OSCILOGRAMA_RECT.height
            puntos.append((x, y))

        if len(puntos) >= 2:
            pygame.draw.lines(surface, (56, 189, 248), False, puntos, 2)

    @staticmethod
    def _linea_punteada(surface, inicio, fin, color, longitud_trazo=6) -> None:
        x1, y1 = inicio
        x2, y2 = fin
        distancia = math.hypot(x2 - x1, y2 - y1)
        if distancia == 0:
            return
        pasos = max(1, int(distancia / (longitud_trazo * 2)))
        for i in range(pasos):
            t0 = (i * 2) / (pasos * 2)
            t1 = (i * 2 + 1) / (pasos * 2)
            p0 = (x1 + (x2 - x1) * t0, y1 + (y2 - y1) * t0)
            p1 = (x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1)
            pygame.draw.line(surface, color, p0, p1, 1)

    def _dibujar_alarma_throttling(self, surface: pygame.Surface) -> None:
        franja = pygame.Rect(0, ALTO_VENTANA - 60, ANCHO_PLANTA, 40)
        pygame.draw.rect(surface, COLOR_CRITICO, franja)
        texto = self.fonts["bold"].render(
            "THERMAL THROTTLING ACTIVO - RENDIMIENTO DEGRADADO", True, (255, 255, 255)
        )
        surface.blit(texto, (franja.x + 20, franja.y + 10))
