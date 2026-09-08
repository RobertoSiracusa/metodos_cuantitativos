"""Constantes, configuraciones graficas y parametros operacionales del automercado."""

from enum import Enum


class CustomerState(Enum):
    """Estados del ciclo de vida del cliente en el automercado."""
    ARRIVING = "Ingresando"
    SHOPPING = "Comprando"
    QUEUED = "En cola"
    AT_CHECKOUT = "En caja"
    SCANNING = "Escaneando"
    PAYING = "Pagando"
    DEPARTING = "Saliendo"
    BALKED = "Rechazado (Colas llenas)"


class CheckoutState(Enum):
    """Estado operativo de una caja registradora."""
    OPEN = "Libre"
    BUSY = "Atendiendo"
    CLOSED = "Cerrada"


class QueueMode(Enum):
    """Disciplina del sistema de colas implementado."""
    PARALLEL = "Colas Multiples (c x M/M/1)"
    SINGLE = "Cola Unica Central (M/M/c)"


# Dimensiones de la ventana y distribucion de pantalla
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 740
SIM_WIDTH = 900
HUD_WIDTH = WINDOW_WIDTH - SIM_WIDTH
FPS = 60

# Parametros analiticos y operacionales de teoria de colas
DEFAULT_REGISTERS = 4         # Numero de cajas abiertas por defecto (c)
MAX_REGISTERS = 5             # Capacidad maxima de cajas en layout
MIN_REGISTERS = 1
DEFAULT_LAMBDA = 5.0          # Tasa de arribos: clientes por minuto simulado
DEFAULT_MU = 1.5              # Tasa de servicio: clientes por minuto por caja
MAX_PARALLEL_QUEUE = 6        # Maximo de clientes en cola fisica por caja antes de balking
MAX_SINGLE_QUEUE = 24         # Maximo en cola unica antes de rechazo

# Parametros de compra y escaneo
MIN_ITEMS = 3
MAX_ITEMS = 25
AVG_ITEM_PRICE = 3.5          # Precio promedio referencial por articulo ($ o unidades monetarias)

# Posiciones fisicas de las cajas registradoras (x, y) en el lienzo del automercado
# 5 estaciones de cobro dispuestas en paralelo
CHECKOUT_POSITIONS = [
    (170, 480),  # Caja 1 (Express / Estandar)
    (330, 480),  # Caja 2
    (490, 480),  # Caja 3
    (650, 480),  # Caja 4
    (800, 480),  # Caja 5
]

# Waypoints y zonas clave de circulacion
SPAWN_POS = (-40, 80)
ENTRANCE_DOOR = (70, 80)
CART_STATION = (70, 140)

# Pasillos de gondolas (puntos de paso durante la compra)
AISLE_WAYPOINTS = [
    (250, 90),   # Pasillo 1: Frutas y Verduras
    (510, 90),   # Pasillo 2: Abarrotes y Granos
    (750, 90),   # Pasillo 3: Panaderia y Dulces
    (250, 210),  # Pasillo 4: Carnes y Embutidos
    (510, 210),  # Pasillo 5: Lacteos y Refrigerados
    (750, 210),  # Pasillo 6: Bebidas y Licores
]

# Zona previa a cajas (hall de decision)
CENTRAL_HALL_Y = 320
SINGLE_QUEUE_HEAD = (490, 360)

# Zona de salida
EXIT_TURNSTILES = (490, 660)
EXIT_DOOR = (840, 660)
EXIT_DESPAWN = (950, 660)

# Paleta de colores para el entorno top-down (Supermarket Fresh)
COLOR_FLOOR = (244, 246, 249)
COLOR_FLOOR_GRID = (226, 232, 240)
COLOR_WALL = (148, 163, 184)
COLOR_ENTRANCE = (56, 189, 248)

COLOR_SHELF_BODY = (203, 213, 225)
COLOR_SHELF_BORDER = (100, 116, 139)
COLOR_SHELF_GREEN = (34, 197, 94)
COLOR_SHELF_RED = (239, 68, 68)
COLOR_SHELF_BLUE = (59, 130, 246)
COLOR_SHELF_ORANGE = (249, 115, 22)
COLOR_SHELF_PURPLE = (168, 85, 247)
COLOR_SHELF_YELLOW = (234, 179, 8)

COLOR_REGISTER_BODY = (30, 41, 59)
COLOR_BELT = (15, 23, 42)
COLOR_SCANNER_OFF = (71, 85, 105)
COLOR_SCANNER_ON = (239, 68, 68)
COLOR_CASHIER_UNIFORM = (37, 99, 235)

COLOR_STATUS_FREE = (34, 197, 94)      # Verde
COLOR_STATUS_BUSY = (234, 179, 8)      # Amarillo
COLOR_STATUS_CLOSED = (239, 68, 68)    # Rojo

COLOR_STANCHION_POST = (71, 85, 105)
COLOR_STANCHION_BELT = (220, 38, 38)

# Colores de cliente y carrito
CART_FRAME_COLOR = (148, 163, 184)
CART_BASKET_COLOR = (203, 213, 225)
CUSTOMER_SKIN_TONES = [
    (253, 224, 197),
    (245, 195, 150),
    (218, 160, 109),
    (141, 85, 36),
]
CUSTOMER_SHIRT_COLORS = [
    (239, 68, 68),
    (59, 130, 246),
    (16, 185, 129),
    (234, 179, 8),
    (168, 85, 247),
    (236, 72, 153),
    (20, 184, 166),
    (249, 115, 22),
]
ITEM_COLORS = [
    (34, 197, 94),   # Manzana/Vegetal
    (239, 68, 68),   # Tomate/Carne
    (234, 179, 8),   # Platano/Cereal
    (59, 130, 246),  # Leche/Bebida
    (249, 115, 22),  # Pan/Naranja
    (168, 85, 247),  # Golosina/Snack
]

# Paleta del panel HUD (Dark Slate & Neon accents)
COLOR_HUD_BG = (18, 22, 30)
COLOR_HUD_CARD = (28, 34, 46)
COLOR_HUD_BORDER = (45, 55, 72)
COLOR_TEXT_MAIN = (248, 250, 252)
COLOR_TEXT_MUTED = (148, 163, 184)
COLOR_TEXT_ACCENT = (56, 189, 248)
COLOR_TEXT_EMERALD = (52, 211, 153)
COLOR_TEXT_WARN = (251, 191, 36)
