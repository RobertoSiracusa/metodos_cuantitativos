"""
Vista del Problema 1: fabrica de laptops (eventos discretos).

Dibuja, en la zona de planta (x de 0 a ANCHO_PLANTA):
  - la cola de ordenes entrantes, con posicion interpolada (estado visual)
  - la estacion de ensamblaje, verde libre / rojo ocupada
  - el contador de laptops despachadas
  - la barra vertical de inventario de procesadores, con marca de umbral
  - el overlay de alarma si la linea esta detenida por falta de stock

Nunca copia el estado de dominio: cada `dibujar()` lee `sim` en el momento.
Lo unico que esta vista guarda entre frames es la posicion interpolada de
cada caja de la cola y la fase de un parpadeo, que son puramente visuales.
"""

import math
from typing import Dict

import pygame

from src.gui.styles import (
    ANCHO_PLANTA,
    ALTO_VENTANA,
    COLOR_ALERTA,
    COLOR_BORDE,
    COLOR_CAJA_ORDEN,
    COLOR_CRITICO,
    COLOR_ESTACION_BORDE,
    COLOR_FONDO_PLANTA,
    COLOR_OK,
    COLOR_TEXTO_MUTED,
    COLOR_TEXTO_PRINCIPAL,
    color_inventario,
)

# --- Geometria de la planta (dentro de 0..ANCHO_PLANTA x 0..ALTO_VENTANA) ---
CAJA_ANCHO = 55
CAJA_ALTO = 45
CAJA_GAP = 12
MAX_VISIBLE_COLA = 6
COLA_X_DERECHA = 330  # borde derecho de la zona de cola, pegado a la estacion

ESTACION_RECT = pygame.Rect(350, 230, 170, 140)
SALIDA_RECT = pygame.Rect(560, 250, 150, 100)
INVENTARIO_RECT = pygame.Rect(750, 110, 40, 540)

VELOCIDAD_INTERPOLACION = 6.0  # que tan rapido una caja alcanza su objetivo


class FactoryView:
    """Vista interactiva del Problema 1. Estado propio: solo lo visual."""

    def __init__(self, fonts: Dict[str, "pygame.font.Font"]) -> None:
        self.fonts = fonts
        self._posiciones_x: Dict[int, float] = {}
        self._fase_parpadeo: float = 0.0

    # ------------------------------------------------------------------
    # Actualizacion puramente visual (se salta si la animacion esta en pausa)
    # ------------------------------------------------------------------

    def actualizar(self, sim, dt_anim: float) -> None:
        """Interpola las posiciones de las cajas de la cola y avanza el parpadeo."""
        self._fase_parpadeo = (self._fase_parpadeo + dt_anim) % 2.0

        ids_en_cola = {orden.id_orden for orden in sim.ordenes_en_cola}
        for id_orden in list(self._posiciones_x):
            if id_orden not in ids_en_cola:
                del self._posiciones_x[id_orden]

        paso = min(1.0, dt_anim * VELOCIDAD_INTERPOLACION)
        for indice, orden in enumerate(sim.ordenes_en_cola[:MAX_VISIBLE_COLA]):
            objetivo = self._x_objetivo(indice)
            actual = self._posiciones_x.get(orden.id_orden, objetivo + 60.0)
            self._posiciones_x[orden.id_orden] = actual + (objetivo - actual) * paso

    @staticmethod
    def _x_objetivo(indice: int) -> float:
        """Posicion x (borde izquierdo) que le corresponde a la caja de ese lugar en la cola."""
        return COLA_X_DERECHA - CAJA_ANCHO - indice * (CAJA_ANCHO + CAJA_GAP)

    # ------------------------------------------------------------------
    # Dibujo
    # ------------------------------------------------------------------

    def dibujar(self, surface: pygame.Surface, sim) -> None:
        """Dibuja un frame completo de la vista de fabrica."""
        rect_planta = pygame.Rect(0, 0, ANCHO_PLANTA, ALTO_VENTANA)
        pygame.draw.rect(surface, COLOR_FONDO_PLANTA, rect_planta)

        titulo = self.fonts["titulo"].render("PROBLEMA 1: FABRICA DE LAPTOPS", True, COLOR_TEXTO_PRINCIPAL)
        surface.blit(titulo, (20, 16))

        self._dibujar_cola(surface, sim)
        self._dibujar_estacion(surface, sim)
        self._dibujar_salida(surface, sim)
        self._dibujar_inventario(surface, sim)

        if sim.linea_detenida:
            self._dibujar_alarma_linea_detenida(surface)

    def _dibujar_cola(self, surface: pygame.Surface, sim) -> None:
        etiqueta = self.fonts["normal"].render("Cola de ordenes entrantes", True, COLOR_TEXTO_MUTED)
        surface.blit(etiqueta, (20, 200))

        visibles = sim.ordenes_en_cola[:MAX_VISIBLE_COLA]
        for indice, orden in enumerate(visibles):
            x = self._posiciones_x.get(orden.id_orden, self._x_objetivo(indice))
            caja = pygame.Rect(int(x), 230, CAJA_ANCHO, CAJA_ALTO)
            pygame.draw.rect(surface, COLOR_CAJA_ORDEN, caja, border_radius=4)
            pygame.draw.rect(surface, COLOR_BORDE, caja, width=1, border_radius=4)
            texto = self.fonts["chico"].render(f"#{orden.id_orden}", True, COLOR_TEXTO_PRINCIPAL)
            surface.blit(texto, (caja.x + 6, caja.y + 14))

        restantes = len(sim.ordenes_en_cola) - len(visibles)
        if restantes > 0:
            x_extra = self._x_objetivo(len(visibles) - 1) - CAJA_ANCHO - CAJA_GAP if visibles else COLA_X_DERECHA - CAJA_ANCHO
            texto_extra = self.fonts["chico"].render(f"+{restantes} mas", True, COLOR_TEXTO_MUTED)
            surface.blit(texto_extra, (max(20, int(x_extra)), 245))

    def _dibujar_estacion(self, surface: pygame.Surface, sim) -> None:
        estacion = sim.estacion
        color = COLOR_CRITICO if estacion.ocupada else COLOR_OK
        pygame.draw.rect(surface, color, ESTACION_RECT, border_radius=8)
        pygame.draw.rect(surface, COLOR_ESTACION_BORDE, ESTACION_RECT, width=2, border_radius=8)

        titulo = self.fonts["bold"].render("ESTACION DE ENSAMBLAJE", True, COLOR_TEXTO_PRINCIPAL)
        surface.blit(titulo, (ESTACION_RECT.x, ESTACION_RECT.y - 22))

        estado_txt = "OCUPADA" if estacion.ocupada else "LIBRE"
        surface.blit(
            self.fonts["normal"].render(estado_txt, True, COLOR_TEXTO_PRINCIPAL),
            (ESTACION_RECT.x + 10, ESTACION_RECT.y + 10),
        )
        if estacion.orden_actual is not None:
            texto_orden = self.fonts["normal"].render(
                f"Orden #{estacion.orden_actual.id_orden}", True, COLOR_TEXTO_PRINCIPAL
            )
            surface.blit(texto_orden, (ESTACION_RECT.x + 10, ESTACION_RECT.y + 34))

    def _dibujar_salida(self, surface: pygame.Surface, sim) -> None:
        pygame.draw.rect(surface, COLOR_BORDE, SALIDA_RECT, width=2, border_radius=8)
        titulo = self.fonts["bold"].render("SALIDA", True, COLOR_TEXTO_PRINCIPAL)
        surface.blit(titulo, (SALIDA_RECT.x, SALIDA_RECT.y - 22))
        contador = self.fonts["titulo"].render(
            str(sim.estacion.laptops_ensambladas), True, COLOR_OK
        )
        surface.blit(contador, (SALIDA_RECT.x + 20, SALIDA_RECT.y + 25))
        etiqueta = self.fonts["chico"].render("laptops despachadas", True, COLOR_TEXTO_MUTED)
        surface.blit(etiqueta, (SALIDA_RECT.x + 10, SALIDA_RECT.y + 70))

    def _dibujar_inventario(self, surface: pygame.Surface, sim) -> None:
        inv = sim.inventario
        titulo = self.fonts["bold"].render("STOCK", True, COLOR_TEXTO_PRINCIPAL)
        surface.blit(titulo, (INVENTARIO_RECT.x - 15, INVENTARIO_RECT.y - 22))

        pygame.draw.rect(surface, (20, 24, 30), INVENTARIO_RECT, border_radius=4)
        pygame.draw.rect(surface, COLOR_BORDE, INVENTARIO_RECT, width=1, border_radius=4)

        fraccion = 0.0 if inv.capacidad_lote <= 0 else min(1.0, inv.nivel / inv.capacidad_lote)
        alto_relleno = int(INVENTARIO_RECT.height * fraccion)
        color = color_inventario(inv.nivel, inv.capacidad_lote, inv.umbral_critico)

        if inv.en_reposicion:
            # Parpadeo suave: alterna intensidad cada medio segundo (fase 0..2 s)
            intensidad = 0.55 + 0.45 * abs(math.sin(self._fase_parpadeo * math.pi))
            color = tuple(min(255, round(c * intensidad + 40)) for c in color)

        relleno = pygame.Rect(
            INVENTARIO_RECT.x, INVENTARIO_RECT.bottom - alto_relleno, INVENTARIO_RECT.width, alto_relleno
        )
        pygame.draw.rect(surface, color, relleno, border_radius=4)

        if inv.capacidad_lote > 0:
            y_umbral = INVENTARIO_RECT.bottom - int(
                INVENTARIO_RECT.height * min(1.0, inv.umbral_critico / inv.capacidad_lote)
            )
            pygame.draw.line(
                surface, COLOR_ALERTA,
                (INVENTARIO_RECT.x - 4, y_umbral), (INVENTARIO_RECT.right + 4, y_umbral), 2,
            )
            marca = self.fonts["chico"].render(f"s={inv.umbral_critico}", True, COLOR_ALERTA)
            surface.blit(marca, (INVENTARIO_RECT.right + 6, y_umbral - 8))

        numerico = self.fonts["chico"].render(
            f"{inv.nivel}/{inv.capacidad_lote}", True, COLOR_TEXTO_PRINCIPAL
        )
        surface.blit(numerico, (INVENTARIO_RECT.x - 6, INVENTARIO_RECT.bottom + 6))

        if inv.en_reposicion:
            rotulo = self.fonts["chico"].render("REPONIENDO", True, COLOR_ALERTA)
            surface.blit(rotulo, (INVENTARIO_RECT.x - 20, INVENTARIO_RECT.y - 40))

    def _dibujar_alarma_linea_detenida(self, surface: pygame.Surface) -> None:
        franja = pygame.Rect(0, ALTO_VENTANA - 60, ANCHO_PLANTA, 40)
        pygame.draw.rect(surface, COLOR_CRITICO, franja)
        texto = self.fonts["bold"].render(
            "LINEA DETENIDA POR FALTA DE STOCK", True, (255, 255, 255)
        )
        surface.blit(texto, (franja.x + 20, franja.y + 10))
