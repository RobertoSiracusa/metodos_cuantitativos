"""Constantes, configuraciones graficas y parametros operacionales de la estacion."""

from enum import Enum


class VehicleState(Enum):
    """Estados del ciclo de vida de un vehiculo en la estacion."""
    ARRIVING = "Llegando"
    QUEUED = "En cola"
    MOVING_TO_PUMP = "Hacia bomba"
    FUELING = "Surtidor"
    PAYING = "Pagando"
    DEPARTING = "Saliendo"
    BALKED = "Rechazado (Cola llena)"


class PumpState(Enum):
    """Estado operativo de un surtidor / bomba de gasolina."""
    FREE = "Libre"
    BUSY = "Ocupado"
    OUT_OF_FUEL = "Sin combustible"


# Dimensiones de la ventana
WINDOW_WIDTH = 1260
WINDOW_HEIGHT = 740
SIM_WIDTH = 880
HUD_WIDTH = WINDOW_WIDTH - SIM_WIDTH
FPS = 60

# Parametros de la teoria de colas (M/M/c)
DEFAULT_SERVERS = 3          # Numero de bombas (c)
DEFAULT_LAMBDA = 4.0         # Tasa de llegada: vehiculos por minuto simulado
DEFAULT_MU = 1.8             # Tasa de servicio: vehiculos por minuto por bomba
MAX_QUEUE_CAPACITY = 8       # Capacidad maxima en cola fisica antes de rechazar

# Combustible y almacenamiento
TANK_CAPACITY = 3000.0       # Capacidad del tanque central (litros)
TANK_INITIAL = 2200.0        # Nivel inicial (litros)
MIN_FUEL_REQ = 20.0          # Minimo litros solicitados por vehiculo
MAX_FUEL_REQ = 50.0          # Maximo litros solicitados por vehiculo
PUMP_FLOW_RATE = 2.0         # Litros por segundo simulado
TANKER_RELOAD_AMOUNT = 1500.0 # Litros que descarga la cisterna

# Geometria de la estacion (coordenadas top-down en SIM_WIDTH x WINDOW_HEIGHT)
# Puntos de las 3 bombas (Islas centrales)
PUMP_POSITIONS = [
    (380, 220),  # Bomba 1
    (380, 370),  # Bomba 2
    (380, 520),  # Bomba 3
]

# Waypoints de la calzada
ENTRY_SPAWN = (-60, 370)     # Origen de vehiculos en calle de acceso
QUEUE_START = (120, 370)     # Inicio de cola
QUEUE_HEAD = (260, 370)      # Cabeza de cola antes de bifurcar a bombas
EXIT_MERGE = (540, 370)      # Punto de salida unificado
EXIT_DESPAWN = (940, 370)    # Fin de la via de salida

# Paleta de colores (tema Dark Asphalt & Industrial)
COLOR_BG_ROAD = (36, 40, 48)
COLOR_CONCRETE = (55, 62, 74)
COLOR_CANOPY_ROOF = (70, 78, 92)
COLOR_CANOPY_EDGE = (239, 68, 68)     # Rojo corporativo en marquesina
COLOR_ISLAND = (180, 186, 198)
COLOR_PUMP_BODY = (30, 41, 59)
COLOR_PUMP_FREE = (34, 197, 94)       # Verde esmeralda
COLOR_PUMP_BUSY = (234, 179, 8)       # Amarillo ámbar
COLOR_PUMP_EMPTY = (239, 68, 68)      # Rojo alerta

COLOR_LANE_WHITE = (240, 243, 246)
COLOR_LANE_YELLOW = (250, 204, 21)
COLOR_TEXT_MAIN = (248, 250, 252)
COLOR_TEXT_MUTED = (148, 163, 184)
COLOR_TEXT_ACCENT = (56, 189, 248)    # Cyan

COLOR_HUD_BG = (18, 22, 30)
COLOR_HUD_CARD = (28, 34, 46)
COLOR_HUD_BORDER = (45, 55, 72)

# Colores aleatorios de carroceria para variedad visual
CAR_COLORS = [
    (220, 38, 38),   # Rojo
    (37, 99, 235),   # Azul
    (245, 158, 11),  # Ámbar
    (16, 185, 129),  # Verde
    (139, 92, 246),  # Púrpura
    (244, 244, 245), # Blanco plata
    (71, 85, 105),   # Gris oscuro
    (236, 72, 153),  # Rosa
    (20, 184, 166),  # Turquesa
]
