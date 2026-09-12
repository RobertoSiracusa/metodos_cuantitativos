"""
Paleta visual, geometria de ventana y utilidades de color de la capa grafica.

Mantiene el mismo lenguaje visual (tema oscuro tipo "dashboard industrial") que
clasePrompts/estacion, para que los tres proyectos Pygame del alumno se vean
coherentes entre si.
"""

from typing import Dict, Tuple

Color = Tuple[int, int, int]

# --------------------------------------------------------------------------
# Ventana y layout
# --------------------------------------------------------------------------
ANCHO_VENTANA = 1280
ALTO_VENTANA = 720
FPS = 60

ANCHO_PLANTA = 830                    # Zona de dibujo de la simulacion
ANCHO_HUD = ANCHO_VENTANA - ANCHO_PLANTA  # Panel lateral de telemetria

# --------------------------------------------------------------------------
# Escalas de tiempo disponibles (segundos simulados por segundo real)
# --------------------------------------------------------------------------
ESCALAS_TIEMPO: Dict[int, float] = {1: 60.0, 2: 300.0, 3: 900.0, 4: 3600.0}
ESCALA_DEFECTO = ESCALAS_TIEMPO[2]

# --------------------------------------------------------------------------
# Paleta (tema Dark Dashboard, coherente con clasePrompts/estacion)
# --------------------------------------------------------------------------
COLOR_FONDO_PLANTA: Color = (30, 34, 42)
COLOR_PANEL_HUD: Color = (18, 22, 30)
COLOR_TARJETA: Color = (28, 34, 46)
COLOR_BORDE: Color = (45, 55, 72)

COLOR_TEXTO_PRINCIPAL: Color = (248, 250, 252)
COLOR_TEXTO_MUTED: Color = (148, 163, 184)
COLOR_TEXTO_ACENTO: Color = (56, 189, 248)

COLOR_OK: Color = (34, 197, 94)        # Verde: libre / normal
COLOR_ALERTA: Color = (234, 179, 8)    # Ambar: advertencia
COLOR_CRITICO: Color = (239, 68, 68)   # Rojo: ocupado / critico

COLOR_CAJA_ORDEN: Color = (56, 130, 246)
COLOR_ESTACION_BORDE: Color = (200, 210, 224)


def cargar_fuentes() -> Dict[str, "pygame.font.Font"]:  # noqa: F821
    """
    Crea el set de tipografias usado por todas las vistas.

    Import de pygame local a la funcion: este modulo debe poder importarse
    (para testear color_temperatura, por ejemplo) sin que pygame ya este
    inicializado.
    """
    import pygame

    familia = "Helvetica,Arial,sans-serif"
    return {
        "titulo": pygame.font.SysFont(familia, 26, bold=True),
        "subtitulo": pygame.font.SysFont(familia, 16),
        "bold": pygame.font.SysFont(familia, 14, bold=True),
        "normal": pygame.font.SysFont(familia, 13),
        "chico": pygame.font.SysFont(familia, 12),
    }


def _lerp(a: float, b: float, t: float) -> float:
    """Interpolacion lineal simple, t se satura a [0, 1] antes de aplicarse."""
    t = max(0.0, min(1.0, t))
    return a + (b - a) * t


def _lerp_color(c_frio: Color, c_calido: Color, t: float) -> Color:
    return (
        round(_lerp(c_frio[0], c_calido[0], t)),
        round(_lerp(c_frio[1], c_calido[1], t)),
        round(_lerp(c_frio[2], c_calido[2], t)),
    )


# Anclas de la interpolacion termica, pedidas explicitamente por el enunciado:
# azul en la parte fria, rojo critico en la parte caliente, con un punto medio
# amarillo alrededor de los 70 C (temperatura de diseno / umbral de throttling).
TEMP_ANCLA_FRIA_C = 50.0
TEMP_ANCLA_MEDIA_C = 70.0
TEMP_ANCLA_CALIDA_C = 90.0

COLOR_TEMP_FRIO: Color = (37, 99, 235)       # Azul
COLOR_TEMP_MEDIO: Color = (234, 179, 8)      # Amarillo/ambar
COLOR_TEMP_CALIENTE: Color = (239, 68, 68)   # Rojo critico

# Nota de diseno: el componente rojo de las tres anclas (37 -> 234 -> 239) es
# estrictamente no decreciente a proposito, para que la interpolacion completa
# (frio -> medio -> caliente) sea monotona en R en todo el rango, no solo en
# cada tramo por separado. Es lo que valida el selfcheck de abajo.


def color_por_temperatura(temperatura_c: float) -> Color:
    """
    Interpola el color del cuerpo del servidor segun la temperatura.

    Azul a TEMP_ANCLA_FRIA_C (50 C), amarillo en TEMP_ANCLA_MEDIA_C (70 C, el
    umbral de throttling) y rojo critico en TEMP_ANCLA_CALIDA_C (90 C). Fuera
    de ese rango la funcion satura en el color extremo correspondiente, nunca
    lanza excepcion.
    """
    if temperatura_c <= TEMP_ANCLA_FRIA_C:
        return COLOR_TEMP_FRIO
    if temperatura_c >= TEMP_ANCLA_CALIDA_C:
        return COLOR_TEMP_CALIENTE
    if temperatura_c <= TEMP_ANCLA_MEDIA_C:
        t = (temperatura_c - TEMP_ANCLA_FRIA_C) / (TEMP_ANCLA_MEDIA_C - TEMP_ANCLA_FRIA_C)
        return _lerp_color(COLOR_TEMP_FRIO, COLOR_TEMP_MEDIO, t)
    t = (temperatura_c - TEMP_ANCLA_MEDIA_C) / (TEMP_ANCLA_CALIDA_C - TEMP_ANCLA_MEDIA_C)
    return _lerp_color(COLOR_TEMP_MEDIO, COLOR_TEMP_CALIENTE, t)


def color_inventario(nivel: int, capacidad_lote: int, umbral_critico: int) -> Color:
    """Verde por encima del umbral, ambar cerca, rojo bajo el umbral critico."""
    if nivel < umbral_critico:
        return COLOR_CRITICO
    margen = max(1, capacidad_lote - umbral_critico)
    if (nivel - umbral_critico) < 0.25 * margen:
        return COLOR_ALERTA
    return COLOR_OK


def _selfcheck() -> None:
    """Verifica la interpolacion de color por temperatura sin abrir pygame."""
    # Ancla fria: tira a azul
    frio = color_por_temperatura(50.0)
    assert frio == COLOR_TEMP_FRIO

    # Ancla caliente: tira a rojo
    caliente = color_por_temperatura(90.0)
    assert caliente == COLOR_TEMP_CALIENTE

    # Saturacion fuera de rango, sin excepcion
    assert color_por_temperatura(-40.0) == COLOR_TEMP_FRIO
    assert color_por_temperatura(500.0) == COLOR_TEMP_CALIENTE

    # Monotonia del componente rojo en todo el rango de interes
    anterior = color_por_temperatura(40.0)[0]
    for decimo in range(400, 1000):
        t = decimo / 10.0
        actual = color_por_temperatura(t)[0]
        assert actual >= anterior - 1e-9, f"componente rojo no monotono en T={t}"
        anterior = actual

    # Inventario
    assert color_inventario(50, 50, 10) == COLOR_OK
    assert color_inventario(9, 50, 10) == COLOR_CRITICO
    assert color_inventario(11, 50, 10) == COLOR_ALERTA

    print("selfcheck styles: OK")


if __name__ == "__main__":
    _selfcheck()
