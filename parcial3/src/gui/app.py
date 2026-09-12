"""
Punto de entrada de la capa grafica Pygame (Pregunta Bonus, 2 puntos).

Expone `ejecutar_animacion(horas, semilla)`, que es exactamente lo que
`main.py::lanzar_gui` importa. Flujo obligatorio: primero se elige que
problema visualizar (pantalla selectora) y despues se corre SOLO esa vista,
nunca las dos a la vez.

No llama a la API de IA: eso pertenece al flujo de consola (main.py). Esta
capa unicamente lee el estado de los motores de simulacion y lo dibuja.
"""

from typing import Optional

import pygame

from src.gui.cluster_view import ClusterView
from src.gui.controller import SimController
from src.gui.factory_view import FactoryView
from src.gui.hud import Hud
from src.gui.input_handler import InputHandler
from src.gui.styles import (
    ALTO_VENTANA,
    ANCHO_VENTANA,
    COLOR_BORDE,
    COLOR_FONDO_PLANTA,
    COLOR_OK,
    COLOR_TARJETA,
    COLOR_TEXTO_ACENTO,
    COLOR_TEXTO_MUTED,
    COLOR_TEXTO_PRINCIPAL,
    FPS,
    cargar_fuentes,
)

TITULO_VENTANA = "Parcial III - Metodos Cuantitativos - Animacion Pygame (bonus)"


class AppState:
    """
    Estado de la aplicacion: que pantalla esta activa y, si corresponde, el
    controlador de la simulacion en curso. El unico dato de dominio que toca
    es `controller.sim`, siempre por referencia, nunca copiado.
    """

    def __init__(self, horas: float, semilla: Optional[int]) -> None:
        self.horas = horas
        self.semilla = semilla
        self.pantalla: str = "selector"
        self.controller: Optional[SimController] = None
        self.tarjeta_problema1, self.tarjeta_problema2 = calcular_tarjetas_selector()

    def ir_a_vista(self, problema: int) -> None:
        """Crea el controlador del problema elegido y cambia a la vista."""
        self.controller = SimController(problema=problema, horas=self.horas, semilla=self.semilla)
        self.pantalla = "vista"

    def ir_a_selector(self) -> None:
        """Vuelve a la pantalla selectora y libera el controlador activo."""
        self.controller = None
        self.pantalla = "selector"


def calcular_tarjetas_selector() -> tuple:
    """Rectangulos de las dos tarjetas seleccionables, compartidos por dibujo y clic."""
    ancho_tarjeta = 480
    alto_tarjeta = 280
    y = (ALTO_VENTANA - alto_tarjeta) // 2 + 20
    gap = 40
    x1 = ANCHO_VENTANA // 2 - ancho_tarjeta - gap // 2
    x2 = ANCHO_VENTANA // 2 + gap // 2
    return (
        pygame.Rect(x1, y, ancho_tarjeta, alto_tarjeta),
        pygame.Rect(x2, y, ancho_tarjeta, alto_tarjeta),
    )


# ----------------------------------------------------------------------
# Pantalla selectora
# ----------------------------------------------------------------------

def _dibujar_selector(surface: pygame.Surface, fonts: dict, estado: AppState) -> None:
    surface.fill(COLOR_FONDO_PLANTA)

    encabezado = [
        "UNIVERSIDAD JOSE ANTONIO PAEZ",
        "FACULTAD DE INGENIERIA - PARCIAL III",
    ]
    y = 60
    for linea in encabezado:
        render = fonts["titulo"].render(linea, True, COLOR_TEXTO_PRINCIPAL)
        surface.blit(render, (ANCHO_VENTANA // 2 - render.get_width() // 2, y))
        y += 34

    subtitulo = fonts["subtitulo"].render(
        "Seleccione el problema a visualizar (1 o 2, o clic en la tarjeta)",
        True, COLOR_TEXTO_MUTED,
    )
    surface.blit(subtitulo, (ANCHO_VENTANA // 2 - subtitulo.get_width() // 2, y + 10))

    _dibujar_tarjeta_selector(
        surface, fonts, estado.tarjeta_problema1,
        "[1] PROBLEMA 1", "Fabrica de laptops",
        "Eventos discretos (SimPy)",
    )
    _dibujar_tarjeta_selector(
        surface, fonts, estado.tarjeta_problema2,
        "[2] PROBLEMA 2", "Cluster de servidores",
        "Simulacion continua (RK4)",
    )

    pie = fonts["chico"].render("ESC para salir", True, COLOR_TEXTO_MUTED)
    surface.blit(pie, (ANCHO_VENTANA // 2 - pie.get_width() // 2, ALTO_VENTANA - 40))


def _dibujar_tarjeta_selector(
    surface: pygame.Surface, fonts: dict, rect: pygame.Rect, titulo: str, linea1: str, linea2: str
) -> None:
    pygame.draw.rect(surface, COLOR_TARJETA, rect, border_radius=12)
    pygame.draw.rect(surface, COLOR_BORDE, rect, width=2, border_radius=12)

    t1 = fonts["bold"].render(titulo, True, COLOR_TEXTO_ACENTO)
    surface.blit(t1, (rect.x + 24, rect.y + 30))

    t2 = fonts["titulo"].render(linea1, True, COLOR_TEXTO_PRINCIPAL)
    surface.blit(t2, (rect.x + 24, rect.y + 100))

    t3 = fonts["normal"].render(linea2, True, COLOR_TEXTO_MUTED)
    surface.blit(t3, (rect.x + 24, rect.y + 140))


# ----------------------------------------------------------------------
# Panel de cierre al terminar la corrida
# ----------------------------------------------------------------------

def _dibujar_panel_cierre(surface: pygame.Surface, fonts: dict, controller: SimController) -> None:
    ancho, alto = 480, 220
    rect = pygame.Rect(
        (ANCHO_VENTANA - ancho) // 2 - 100, (ALTO_VENTANA - alto) // 2, ancho, alto
    )
    pygame.draw.rect(surface, COLOR_TARJETA, rect, border_radius=10)
    pygame.draw.rect(surface, COLOR_OK, rect, width=2, border_radius=10)

    titulo = fonts["bold"].render("CORRIDA FINALIZADA", True, COLOR_OK)
    surface.blit(titulo, (rect.x + 20, rect.y + 18))

    m = controller.sim.obtener_metricas()
    if controller.problema == 1:
        lineas = [
            f"Ordenes generadas: {m['ordenes_generadas']}",
            f"Ordenes completadas: {m['ordenes_completadas']}",
            f"Wq simulado: {m['wq_promedio_min']:.2f} min",
            f"Paradas de linea: {m['paradas_por_falta_stock']}",
        ]
    else:
        lineas = [
            f"Temperatura media: {m['temp_media_c']:.2f} C",
            f"TB procesados: {m['tb_procesados']:.4f}",
            f"% tiempo throttling: {m['pct_tiempo_throttling']:.1f} %",
            f"Eficiencia global: {m['eficiencia_global_pct']:.1f} %",
        ]

    y = rect.y + 54
    for linea in lineas:
        render = fonts["normal"].render(linea, True, COLOR_TEXTO_PRINCIPAL)
        surface.blit(render, (rect.x + 20, y))
        y += 24

    pie = fonts["chico"].render("ESC para volver al selector", True, COLOR_TEXTO_MUTED)
    surface.blit(pie, (rect.x + 20, rect.bottom - 26))


# ----------------------------------------------------------------------
# Bucle principal
# ----------------------------------------------------------------------

def ejecutar_animacion(horas: float, semilla: Optional[int] = None) -> None:
    """
    Abre la ventana Pygame, muestra el selector de problema y corre la vista
    elegida hasta que el usuario cierra la ventana o sale con ESC.
    """
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption(TITULO_VENTANA)
    screen = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    clock = pygame.time.Clock()
    fonts = cargar_fuentes()

    estado = AppState(horas=horas, semilla=semilla)
    factory_view = FactoryView(fonts)
    cluster_view = ClusterView(fonts)
    hud = Hud(fonts)

    running = True
    while running:
        dt_real = min(clock.tick(FPS) / 1000.0, 0.1)
        running = InputHandler.procesar_eventos(estado)
        if not running:
            break

        if estado.pantalla == "selector" or estado.controller is None:
            _dibujar_selector(screen, fonts, estado)
        else:
            controller = estado.controller
            controller.step(dt_real)
            animacion_congelada = controller.pausa_animacion or controller.pausa_total
            dt_anim = 0.0 if animacion_congelada else dt_real

            if controller.problema == 1:
                factory_view.actualizar(controller.sim, dt_anim)
                factory_view.dibujar(screen, controller.sim)
            else:
                cluster_view.actualizar(controller.sim, dt_anim)
                cluster_view.dibujar(screen, controller.sim)

            if controller.pausa_animacion and not controller.pausa_total:
                _dibujar_cartel_pausa(screen, fonts, "ANIMACION EN PAUSA - EL MOTOR SIGUE CALCULANDO")
            elif controller.pausa_total:
                _dibujar_cartel_pausa(screen, fonts, "SIMULACION DETENIDA")

            hud.dibujar(screen, controller, clock.get_fps())

            if controller.terminado:
                _dibujar_panel_cierre(screen, fonts, controller)

        pygame.display.flip()

    pygame.quit()


def _dibujar_cartel_pausa(surface: pygame.Surface, fonts: dict, texto: str) -> None:
    """Cartel superior que distingue pausa de animacion de pausa total."""
    render = fonts["bold"].render(texto, True, (255, 255, 255))
    franja = pygame.Rect(0, 60, render.get_width() + 40, 30)
    pygame.draw.rect(surface, (80, 60, 10), franja)
    surface.blit(render, (franja.x + 20, franja.y + 6))
