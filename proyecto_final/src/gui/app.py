"""Bucle principal del dashboard Pygame: avanza el motor SimPy y dibuja los paneles (R8-R10)."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pygame

from src.gui.paneles import (
    FONDO,
    TEXTO_TENUE,
    Panel,
    PanelEventos,
    PanelGradiente,
    PanelLagrange,
    PanelTermico,
    PanelTopologia,
    texto,
)
from src.simulation.motor_simpy import EstadoSimulacion, MotorSimulacion

ANCHO, ALTO = 1280, 780


class AplicacionPygame:
    """Dashboard en vivo. Teclas: ESPACIO pausa, +/- velocidad, P reporte PDF, S captura, ESC salir.

    La aplicacion solo llama a `motor.avanzar()` y `motor.estado()`; los paneles reciben el
    EstadoSimulacion (de solo lectura) y no conocen al motor.
    """

    def __init__(
        self,
        motor: MotorSimulacion,
        generar_reporte: Callable[[EstadoSimulacion], Path] | None = None,
    ) -> None:
        self._motor = motor
        self._generar_reporte = generar_reporte
        self._velocidad = 5.0  # unidades de simulacion por segundo real
        self._pausado = False
        self._mensaje = ""
        self._paneles: list[Panel] = [
            PanelTopologia(pygame.Rect(10, 40, 800, 500)),
            PanelTermico(pygame.Rect(820, 40, 450, 240)),
            PanelGradiente(pygame.Rect(820, 290, 450, 120)),
            PanelLagrange(pygame.Rect(820, 420, 450, 120)),
            PanelEventos(pygame.Rect(10, 550, 1260, 220)),
        ]

    def dibujar(self, superficie: pygame.Surface, estado: EstadoSimulacion) -> None:
        superficie.fill(FONDO)
        texto(
            superficie,
            f"Simulador de red de centros de datos   t = {estado.tiempo:7.1f} / {self._motor.duracion:.0f}"
            f"   x{self._velocidad:g}{'   PAUSA' if self._pausado else ''}",
            (12, 10),
            tamano=16,
        )
        texto(superficie, "ESPACIO pausa  +/- velocidad  P reporte PDF  S captura  ESC salir", (760, 14), TEXTO_TENUE, 12)
        for panel in self._paneles:
            panel.dibujar(superficie, estado)
        if self._mensaje:
            texto(superficie, self._mensaje, (12, ALTO - 4 - 14), TEXTO_TENUE, 12)

    def capturar(self, ruta: str | Path, tiempo: float) -> Path:
        """Avanza hasta `tiempo` y guarda una imagen del dashboard sin abrir el bucle interactivo."""
        pygame.init()
        superficie = pygame.Surface((ANCHO, ALTO))
        self._motor.avanzar(tiempo)
        self.dibujar(superficie, self._motor.estado())
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(superficie, str(ruta))
        return ruta

    def ejecutar(self) -> None:
        pygame.init()
        pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Simulador de optimizacion - Metodos Cuantitativos")
        reloj = pygame.time.Clock()
        corriendo = True
        while corriendo:
            dt = reloj.tick(30) / 1000
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    corriendo = False
                elif evento.type == pygame.KEYDOWN:
                    corriendo = self._tecla(evento, pantalla)

            if not self._pausado and self._motor.tiempo < self._motor.duracion:
                self._motor.avanzar(min(self._motor.tiempo + dt * self._velocidad, self._motor.duracion))
            self.dibujar(pantalla, self._motor.estado())
            pygame.display.flip()
        pygame.quit()

    def _tecla(self, evento, pantalla: pygame.Surface) -> bool:
        if evento.key == pygame.K_ESCAPE:
            return False
        if evento.key == pygame.K_SPACE:
            self._pausado = not self._pausado
        elif evento.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            self._velocidad = min(self._velocidad * 2, 80)
        elif evento.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self._velocidad = max(self._velocidad / 2, 0.5)
        elif evento.key == pygame.K_s:
            ruta = Path("outputs") / f"captura_t{self._motor.tiempo:.0f}.png"
            ruta.parent.mkdir(exist_ok=True)
            pygame.image.save(pantalla, str(ruta))
            self._mensaje = f"captura guardada en {ruta}"
        elif evento.key == pygame.K_p:
            if self._generar_reporte is None:
                self._mensaje = "el reporte PDF no esta disponible"
            else:
                self._mensaje = "generando reporte PDF..."
                ruta = self._generar_reporte(self._motor.estado())
                self._mensaje = f"reporte guardado en {ruta}"
        return True
