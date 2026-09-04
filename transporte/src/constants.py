"""Constantes, configuraciones graficas y parametros operacionales de transporte."""

from enum import Enum


class TruckState(Enum):
    """Estados del ciclo de vida operativo de un camion."""
    DISPONIBLE = "Disponible"
    ASIGNADO = "Asignado"
    EN_TRANSITO_ORIGEN = "Hacia origen"
    CARGANDO = "Cargando"
    EN_RUTA = "En ruta optima"
    DESCARGANDO = "Descargando"
    RETORNANDO = "Retornando"


class TruckType(Enum):
    """Categorias de camiones con capacidades y costos por kilometro."""
    LIGERO = ("Camion Ligero (350)", 6.0, 160.0, 1.25, (56, 189, 248))      # Capacidad 6t, 160 px/s, $1.25/km, Cyan
    MEDIANO = ("Camion Mediano (750)", 14.0, 130.0, 2.10, (251, 191, 36))   # Capacidad 14t, 130 px/s, $2.10/km, Ambar
    PESADO = ("Gandola Chuto (Tractor)", 28.0, 100.0, 3.40, (168, 85, 247)) # Capacidad 28t, 100 px/s, $3.40/km, Purpura

    def __init__(self, label: str, capacity_tons: float, speed_px: float, cost_km: float, color: tuple):
        self.label = label
        self.capacity_tons = capacity_tons
        self.speed_px = speed_px
        self.cost_km = cost_km
        self.color = color


class PathAlgorithm(Enum):
    """Algoritmos de optimizacion de rutas en redes."""
    DIJKSTRA = "Dijkstra (Exacto)"
    ASTAR = "A* (Heuristico Admisible)"


# Dimensiones de la ventana y distribucion de pantalla
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 740
SIM_WIDTH = 890
HUD_WIDTH = WINDOW_WIDTH - SIM_WIDTH
FPS = 60

# Parametros operacionales de la simulacion
DEFAULT_SPEED = 1.0
AUTO_ORDER_INTERVAL_SEC = 5.5
LOADING_TIME_SEC = 1.2
UNLOADING_TIME_SEC = 1.4

# Paleta de colores tematica (Dark Asphalt, Slate & Neon Routing)
COLOR_BG = (18, 22, 30)
COLOR_GRID = (28, 34, 46)

# Carreteras y vias
COLOR_ROAD_BG = (35, 41, 52)
COLOR_ROAD_BORDER = (55, 65, 81)
COLOR_ROAD_DASH = (100, 116, 139)
COLOR_ROAD_LABEL_BG = (22, 27, 34)

# Resaltado de rutas cuantitativas
COLOR_ROUTE_OPTIMAL = (6, 182, 212)       # Cyan Neon para la ruta mas corta
COLOR_ROUTE_OPTIMAL_GLOW = (6, 182, 212, 60)
COLOR_ROUTE_ALT = (244, 63, 94)           # Rosa/Rojo para ruta alternativa o suboptima
COLOR_ROUTE_TRANSIT = (234, 179, 8)       # Amarillo ambar para ruta de camiones en viaje

# Nodos del grafo
COLOR_NODE_HUB = (59, 130, 246)          # Azul brillante para Hub / Centro de Distribucion
COLOR_NODE_CITY = (16, 185, 129)         # Verde esmeralda para Ciudades y Destinos
COLOR_NODE_CROSS = (107, 114, 128)       # Gris para Peajes e Intersecciones
COLOR_NODE_SELECTED_ORIGIN = (56, 189, 248) # Halo Cyan
COLOR_NODE_SELECTED_DEST = (52, 211, 153)   # Halo Verde Neón

# Tipografia y textos
COLOR_TEXT_MAIN = (248, 250, 252)
COLOR_TEXT_MUTED = (148, 163, 184)
COLOR_TEXT_ACCENT = (56, 189, 248)
COLOR_TEXT_SUCCESS = (52, 211, 153)
COLOR_TEXT_WARNING = (251, 191, 36)
COLOR_TEXT_DANGER = (248, 113, 113)

# Panel HUD
COLOR_HUD_BG = (13, 17, 23)
COLOR_HUD_CARD = (22, 27, 34)
COLOR_HUD_BORDER = (48, 54, 61)
COLOR_HUD_DIVIDER = (33, 38, 45)

# Definicion del grafo logistico base (Red Centro-Norte-Llanos)
# Nodos: id, nombre, x, y, tipo, demanda inicial (ton), oferta inicial (ton)
NETWORK_NODES = [
    {"id": "VAL", "name": "Valencia Central Hub", "x": 130, "y": 370, "type": "HUB", "demand": 0.0, "supply": 120.0},
    {"id": "PTO", "name": "Puerto Cabello (Maritimo)", "x": 220, "y": 140, "type": "HUB", "demand": 0.0, "supply": 200.0},
    {"id": "GUA", "name": "Guacara Industrial", "x": 280, "y": 350, "type": "CITY", "demand": 25.0, "supply": 30.0},
    {"id": "MAR", "name": "Maracay Hub Fabril", "x": 420, "y": 320, "type": "HUB", "demand": 40.0, "supply": 80.0},
    {"id": "CAG", "name": "Cagua Agroindustrial", "x": 470, "y": 450, "type": "CITY", "demand": 35.0, "supply": 15.0},
    {"id": "VIC", "name": "La Victoria Peaje", "x": 570, "y": 330, "type": "CROSS", "demand": 10.0, "supply": 0.0},
    {"id": "SJC", "name": "San Juan de los Morros", "x": 410, "y": 600, "type": "CITY", "demand": 45.0, "supply": 20.0},
    {"id": "VLL", "name": "Valle de la Pascua", "x": 690, "y": 600, "type": "CITY", "demand": 50.0, "supply": 25.0},
    {"id": "CHA", "name": "Charallave Valles Tuy", "x": 700, "y": 440, "type": "CITY", "demand": 30.0, "supply": 10.0},
    {"id": "TEQ", "name": "Los Teques Altos", "x": 690, "y": 280, "type": "CITY", "demand": 20.0, "supply": 0.0},
    {"id": "CCS", "name": "Caracas Capital", "x": 800, "y": 160, "type": "CITY", "demand": 95.0, "supply": 0.0},
    {"id": "GTR", "name": "Guatire / Guarenas", "x": 810, "y": 360, "type": "HUB", "demand": 30.0, "supply": 40.0},
]

# Aristas: u, v, distancia_km, costo_peaje_fijo ($), limite_velocidad_kmh
NETWORK_EDGES = [
    {"u": "PTO", "v": "VAL", "km": 55.0, "toll": 5.0, "speed_limit": 80.0},
    {"u": "PTO", "v": "MAR", "km": 115.0, "toll": 8.0, "speed_limit": 70.0},
    {"u": "VAL", "v": "GUA", "km": 22.0, "toll": 2.0, "speed_limit": 90.0},
    {"u": "GUA", "v": "MAR", "km": 46.0, "toll": 3.0, "speed_limit": 90.0},
    {"u": "MAR", "v": "CAG", "km": 24.0, "toll": 1.5, "speed_limit": 80.0},
    {"u": "MAR", "v": "VIC", "km": 34.0, "toll": 3.0, "speed_limit": 90.0},
    {"u": "CAG", "v": "VIC", "km": 28.0, "toll": 2.0, "speed_limit": 75.0},
    {"u": "CAG", "v": "SJC", "km": 48.0, "toll": 2.5, "speed_limit": 70.0},
    {"u": "SJC", "v": "VLL", "km": 160.0, "toll": 4.0, "speed_limit": 80.0},
    {"u": "VIC", "v": "TEQ", "km": 54.0, "toll": 4.0, "speed_limit": 85.0},
    {"u": "VIC", "v": "CHA", "km": 68.0, "toll": 3.5, "speed_limit": 75.0},
    {"u": "TEQ", "v": "CCS", "km": 28.0, "toll": 2.0, "speed_limit": 70.0},
    {"u": "CHA", "v": "CCS", "km": 44.0, "toll": 3.0, "speed_limit": 80.0},
    {"u": "CHA", "v": "GTR", "km": 56.0, "toll": 3.0, "speed_limit": 75.0},
    {"u": "CCS", "v": "GTR", "km": 36.0, "toll": 2.5, "speed_limit": 80.0},
    {"u": "CHA", "v": "VLL", "km": 175.0, "toll": 5.0, "speed_limit": 80.0},
    {"u": "VLL", "v": "GTR", "km": 190.0, "toll": 6.0, "speed_limit": 75.0},
]

# Configuracion inicial de la flota de camiones
INITIAL_FLEET_CONFIG = [
    {"id": 1, "name": "Camion C-01", "type": TruckType.LIGERO, "initial_node": "VAL"},
    {"id": 2, "name": "Camion C-02", "type": TruckType.MEDIANO, "initial_node": "PTO"},
    {"id": 3, "name": "Camion C-03", "type": TruckType.PESADO, "initial_node": "VAL"},
    {"id": 4, "name": "Camion C-04", "type": TruckType.MEDIANO, "initial_node": "MAR"},
    {"id": 5, "name": "Camion C-05", "type": TruckType.PESADO, "initial_node": "PTO"},
    {"id": 6, "name": "Camion C-06", "type": TruckType.LIGERO, "initial_node": "GTR"},
]
