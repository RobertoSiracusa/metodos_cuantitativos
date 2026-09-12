"""
Tests headless de la capa grafica Pygame (Pregunta Bonus).

Se fija SDL_VIDEODRIVER=dummy como las dos primeras lineas del modulo, ANTES
de importar pygame o cualquier modulo de src/gui/ que lo importe de forma
transitiva. Ninguno de estos tests abre una ventana real ni se cuelga: solo
se usa pygame.Surface() en memoria y pygame.event.post() para simular
teclado, nunca un bucle de eventos bloqueante.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys
from pathlib import Path

import pygame
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.gui import app, cluster_view, controller, factory_view, hud, input_handler, styles
from src.simulation.continuous_sim import ClusterSimulation
from src.simulation.discrete_sim import FabricaSimulation

SEMILLA_TEST = 2026


@pytest.fixture(scope="session", autouse=True)
def _pygame_headless():
    """Inicializa Pygame una unica vez para toda la sesion, en modo dummy."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


@pytest.fixture(scope="session")
def fonts():
    return styles.cargar_fuentes()


@pytest.fixture
def sim_fabrica_con_estado():
    """Motor de fabrica con algo de historia: cola, estacion e inventario en uso."""
    sim = FabricaSimulation(semilla=SEMILLA_TEST)
    sim.step(300.0)  # 5 min simulados, alcanza para tener ordenes en curso
    return sim


@pytest.fixture
def sim_cluster_con_estado():
    """Motor de cluster con algo de historia: temperatura e historial poblados."""
    sim = ClusterSimulation(semilla=SEMILLA_TEST)
    sim.step(600.0)  # 10 min simulados
    return sim


# --------------------------------------------------------------------------
# 1. Los siete modulos importan sin efectos colaterales
# --------------------------------------------------------------------------

def test_los_siete_modulos_importan_sin_efectos_colaterales():
    """Basta con que ya se hayan importado arriba sin excepcion; se verifica
    ademas que expongan lo minimo esperado de su API publica."""
    assert hasattr(app, "ejecutar_animacion")
    assert hasattr(app, "AppState")
    assert hasattr(controller, "SimController")
    assert hasattr(input_handler, "InputHandler")
    assert hasattr(hud, "Hud")
    assert hasattr(factory_view, "FactoryView")
    assert hasattr(cluster_view, "ClusterView")
    # Importar no debe haber inicializado nada por su cuenta
    assert pygame.get_init()  # lo hizo el fixture de sesion, no un import


# --------------------------------------------------------------------------
# 2. Interpolacion de color por temperatura
# --------------------------------------------------------------------------

def test_color_por_temperatura_ancla_fria_y_calida():
    assert styles.color_por_temperatura(50.0) == styles.COLOR_TEMP_FRIO
    assert styles.color_por_temperatura(90.0) == styles.COLOR_TEMP_CALIENTE


def test_color_por_temperatura_es_monotona_en_rojo():
    anterior = styles.color_por_temperatura(30.0)[0]
    t = 30.0
    while t <= 110.0:
        actual = styles.color_por_temperatura(t)[0]
        assert actual >= anterior - 1e-9, f"componente rojo no monotono en T={t}"
        anterior = actual
        t += 1.0


def test_color_por_temperatura_satura_fuera_de_rango_sin_lanzar():
    assert styles.color_por_temperatura(-100.0) == styles.COLOR_TEMP_FRIO
    assert styles.color_por_temperatura(1000.0) == styles.COLOR_TEMP_CALIENTE


# --------------------------------------------------------------------------
# 3. El controlador se construye para cada problema y step avanza el motor
# --------------------------------------------------------------------------

def test_controller_problema_1_construye_fabrica_y_step_avanza():
    c = controller.SimController(problema=1, horas=1.0, semilla=SEMILLA_TEST)
    assert isinstance(c.sim, FabricaSimulation)
    t0 = c.sim.tiempo_actual
    c.step(dt_real_s=1.0)
    assert c.sim.tiempo_actual > t0


def test_controller_problema_2_construye_cluster_y_step_avanza():
    c = controller.SimController(problema=2, horas=1.0, semilla=SEMILLA_TEST)
    assert isinstance(c.sim, ClusterSimulation)
    t0 = c.sim.tiempo_actual
    c.step(dt_real_s=1.0)
    assert c.sim.tiempo_actual > t0


# --------------------------------------------------------------------------
# 4 y 5. La letra chica: pausa de animacion NO detiene el motor; pausa total SI
# --------------------------------------------------------------------------

def test_espacio_pausa_animacion_pero_el_motor_sigue_avanzando():
    c = controller.SimController(problema=1, horas=2.0, semilla=SEMILLA_TEST)
    estado = app.AppState(horas=2.0, semilla=SEMILLA_TEST)
    estado.controller = c
    estado.pantalla = "vista"

    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    input_handler.InputHandler.procesar_eventos(estado)
    assert c.pausa_animacion is True
    assert c.pausa_total is False

    antes = c.sim.tiempo_actual
    for _ in range(10):
        c.step(dt_real_s=0.05)
    assert c.sim.tiempo_actual > antes, "el motor no avanzo con la animacion en pausa"


def test_p_congela_el_motor_por_completo():
    c = controller.SimController(problema=1, horas=2.0, semilla=SEMILLA_TEST)
    estado = app.AppState(horas=2.0, semilla=SEMILLA_TEST)
    estado.controller = c
    estado.pantalla = "vista"

    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))
    input_handler.InputHandler.procesar_eventos(estado)
    assert c.pausa_total is True

    congelado = c.sim.tiempo_actual
    for _ in range(10):
        c.step(dt_real_s=0.05)
    assert c.sim.tiempo_actual == congelado, "P no congelo el motor"


# --------------------------------------------------------------------------
# 6. Las teclas 1-4 fijan la escala de tiempo esperada
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "tecla, escala_esperada",
    [
        (pygame.K_1, 60.0),
        (pygame.K_2, 300.0),
        (pygame.K_3, 900.0),
        (pygame.K_4, 3600.0),
    ],
)
def test_teclas_1_a_4_fijan_la_escala_de_tiempo(tecla, escala_esperada):
    c = controller.SimController(problema=1, horas=1.0, semilla=SEMILLA_TEST)
    estado = app.AppState(horas=1.0, semilla=SEMILLA_TEST)
    estado.controller = c
    estado.pantalla = "vista"

    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=tecla))
    input_handler.InputHandler.procesar_eventos(estado)
    assert c.escala_tiempo == escala_esperada


# --------------------------------------------------------------------------
# 7. Renderizado de un frame de cada vista sobre una Surface fuera de pantalla
# --------------------------------------------------------------------------

def test_render_frame_vista_fabrica_sin_excepcion(fonts, sim_fabrica_con_estado):
    surface = pygame.Surface((styles.ANCHO_VENTANA, styles.ALTO_VENTANA))
    vista = factory_view.FactoryView(fonts)
    vista.actualizar(sim_fabrica_con_estado, dt_anim=0.5)
    vista.dibujar(surface, sim_fabrica_con_estado)  # no debe lanzar


def test_render_frame_vista_fabrica_con_alarma_y_reposicion(fonts, sim_fabrica_con_estado):
    """Fuerza las dos ramas de alarma/parpadeo del Problema 1 (linea detenida,
    inventario en reposicion) para que tambien queden cubiertas por el render."""
    surface = pygame.Surface((styles.ANCHO_VENTANA, styles.ALTO_VENTANA))
    sim_fabrica_con_estado.linea_detenida = True
    sim_fabrica_con_estado.inventario.en_reposicion = True
    vista = factory_view.FactoryView(fonts)
    vista.actualizar(sim_fabrica_con_estado, dt_anim=0.5)
    vista.dibujar(surface, sim_fabrica_con_estado)


def test_render_frame_vista_cluster_sin_excepcion(fonts, sim_cluster_con_estado):
    surface = pygame.Surface((styles.ANCHO_VENTANA, styles.ALTO_VENTANA))
    vista = cluster_view.ClusterView(fonts)
    vista.actualizar(sim_cluster_con_estado, dt_anim=0.5)
    vista.dibujar(surface, sim_cluster_con_estado)  # no debe lanzar


def test_render_hud_fabrica_y_cluster_sin_excepcion(
    fonts, sim_fabrica_con_estado, sim_cluster_con_estado
):
    surface = pygame.Surface((styles.ANCHO_VENTANA, styles.ALTO_VENTANA))
    tablero = hud.Hud(fonts)

    c1 = controller.SimController(problema=1, horas=1.0, semilla=SEMILLA_TEST)
    c1.sim = sim_fabrica_con_estado
    tablero.dibujar(surface, c1, fps=60.0)

    c2 = controller.SimController(problema=2, horas=1.0, semilla=SEMILLA_TEST)
    c2.sim = sim_cluster_con_estado
    tablero.dibujar(surface, c2, fps=60.0)


def test_render_selector_y_panel_cierre_sin_excepcion(fonts):
    surface = pygame.Surface((styles.ANCHO_VENTANA, styles.ALTO_VENTANA))
    estado = app.AppState(horas=1.0, semilla=SEMILLA_TEST)
    app._dibujar_selector(surface, fonts, estado)

    c = controller.SimController(problema=1, horas=0.001, semilla=SEMILLA_TEST)
    c.step(dt_real_s=100.0)
    app._dibujar_panel_cierre(surface, fonts, c)


# --------------------------------------------------------------------------
# Selector: primero se elige, despues se visualiza solo lo elegido
# --------------------------------------------------------------------------

def test_selector_es_la_pantalla_inicial_y_elige_una_sola_vista():
    estado = app.AppState(horas=1.0, semilla=SEMILLA_TEST)
    assert estado.pantalla == "selector"
    assert estado.controller is None

    estado.ir_a_vista(problema=2)
    assert estado.pantalla == "vista"
    assert estado.controller is not None
    assert estado.controller.problema == 2

    estado.ir_a_selector()
    assert estado.pantalla == "selector"
    assert estado.controller is None


def test_esc_desde_selector_termina_la_aplicacion():
    estado = app.AppState(horas=1.0, semilla=SEMILLA_TEST)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    seguir = input_handler.InputHandler.procesar_eventos(estado)
    assert seguir is False


def test_esc_desde_vista_vuelve_al_selector_sin_salir():
    estado = app.AppState(horas=1.0, semilla=SEMILLA_TEST)
    estado.ir_a_vista(problema=1)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    seguir = input_handler.InputHandler.procesar_eventos(estado)
    assert seguir is True
    assert estado.pantalla == "selector"


def test_r_reinicia_la_vista_actual():
    estado = app.AppState(horas=1.0, semilla=SEMILLA_TEST)
    estado.ir_a_vista(problema=1)
    estado.controller.step(dt_real_s=5.0)
    assert estado.controller.sim.tiempo_actual > 0.0

    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
    input_handler.InputHandler.procesar_eventos(estado)
    assert estado.controller.sim.tiempo_actual == 0.0
