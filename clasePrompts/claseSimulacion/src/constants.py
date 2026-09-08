"""Constantes globales para la simulacion y visualizacion de Snake."""

from enum import Enum, auto


class Direction(Enum):
    """Direcciones de movimiento en la cuadricula discreta."""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def dx(self) -> int:
        return self.value[0]

    @property
    def dy(self) -> int:
        return self.value[1]

    def is_opposite(self, other: "Direction") -> bool:
        """Verifica si otra direccion es opuesta (invalida para giro inmediato)."""
        return (self.dx + other.dx == 0) and (self.dy + other.dy == 0)


class GameState(Enum):
    """Estados del ciclo de vida del juego/simulador."""
    MENU = auto()
    RUNNING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


class ControlMode(Enum):
    """Modo de control de la serpiente."""
    MANUAL = "MANUAL (JUGADOR)"
    AUTO_AI = "AUTO (SIMULACION IA)"


# Dimensiones de la ventana y de la cuadricula
CELL_SIZE = 24  # Pixeles por celda
GRID_WIDTH = 25  # Columnas en el area de juego (600px)
GRID_HEIGHT = 25  # Filas en el area de juego (600px)

PLAY_WIDTH = GRID_WIDTH * CELL_SIZE  # 600px
PLAY_HEIGHT = GRID_HEIGHT * CELL_SIZE  # 600px
SIDEBAR_WIDTH = 280  # Ancho del panel lateral de metricas

WINDOW_WIDTH = PLAY_WIDTH + SIDEBAR_WIDTH  # 880px
WINDOW_HEIGHT = PLAY_HEIGHT  # 600px

# Parametros de simulacion discreta (en segundos de tiempo de simulacion)
DEFAULT_STEP_INTERVAL = 0.12  # Intervalo base entre avances
MIN_STEP_INTERVAL = 0.04  # Limite minimo de velocidad
SPEED_DECREMENT_PER_FOOD = 0.002  # Aceleracion progresiva al comer
BONUS_FOOD_PROBABILITY = 0.25  # Probabilidad de generar comida especial
BONUS_FOOD_LIFESPAN = 12.0  # Duracion en segundos simulados de la comida especial
FOOD_EXPIRATION_CHECK_INTERVAL = 1.0  # Frecuencia de chequeo de comida

# Paleta de colores tematica cuantitativa (Dark Slate & Neon accents)
COLOR_BG_PLAY = (16, 22, 34)
COLOR_BG_SIDEBAR = (10, 14, 23)
COLOR_GRID_LINE = (24, 33, 50)
COLOR_BORDER = (40, 56, 84)

# Serpiente
COLOR_SNAKE_HEAD = (46, 204, 113)
COLOR_SNAKE_BODY = (39, 174, 96)
COLOR_SNAKE_EYE = (236, 240, 241)
COLOR_SNAKE_PUPIL = (24, 33, 50)

# Comida
COLOR_FOOD_NORMAL = (231, 76, 60)
COLOR_FOOD_BONUS = (241, 196, 15)
COLOR_FOOD_PULSE = (255, 235, 150)

# Textos e indicadores
COLOR_TEXT_PRIMARY = (245, 247, 250)
COLOR_TEXT_MUTED = (140, 155, 178)
COLOR_ACCENT_BLUE = (52, 152, 219)
COLOR_ACCENT_PURPLE = (155, 89, 182)
COLOR_DANGER = (231, 76, 60)
COLOR_SUCCESS = (46, 204, 113)
COLOR_WARNING = (243, 156, 18)
