"""Constantes fisicas, geometricas, visuales y operativas para la simulacion nuclear."""

from enum import Enum

# Resolucion y ventana grafica
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 768
FPS = 60

# Geometria del nucleo y vasija
CORE_CENTER_X = 440
CORE_CENTER_Y = 384
VESSEL_RADIUS = 310
CORE_ACTIVE_RADIUS = 250
REFLECTOR_THICKNESS = 35

# Parametros de la red de combustible (Lattice)
FUEL_GRID_ROWS = 9
FUEL_GRID_COLS = 9
FUEL_PITCH = 52  # Distancia entre centros de ensambles
PELLET_RADIUS = 16

# Barras de control (Canales intercalados)
CONTROL_ROD_COLUMNS = [1, 3, 5, 7]  # Columnas con barras de control
CONTROL_ROD_ROWS = [1, 3, 5, 7]
DEFAULT_ROD_INSERTION = 0.50  # 50% de insercion inicial
ROD_SPEED_PER_SEC = 0.25      # Velocidad de movimiento manual (25% por segundo)

# Parametros fisicos y nucleares
ENERGY_PER_FISSION_MEV = 200.0
JOULES_PER_MEV = 1.60218e-13
NU_PROMPT_MIN = 2
NU_PROMPT_MAX = 3
NU_PROMPT_AVG = 2.43
BETA_DELAYED = 0.0065  # Fraccion de neutrones retardados
LAMBDA_PRECURSOR = 0.15  # Tasa de decaimiento media de precursores (1/s)

# Velocidades y dinamica de neutrones en pantalla (pixels/segundo)
V_FAST = 320.0
V_THERMAL = 150.0
P_MODERATE = 0.12        # Probabilidad de moderacion (rapido -> termico) por segundo en agua
P_FISSION_U235 = 0.84    # Probabilidad de fisurar U-235 al impactar con neutron termico
P_CAPTURE_U235 = 0.16    # Captura radiativa sin fisura en U-235
P_CAPTURE_U238 = 0.18    # Captura resonante en U-238 (aumenta con temperatura)
P_ABSORB_ROD = 0.96      # Absorcion en barra de boro/cadmio
P_REFLECTOR_BOUNCE = 0.72 # Probabilidad de reflexion en el borde del nucleo
MAX_ACTIVE_NEUTRONS = 500 # Limite de poblacion activa en pantalla para fluidez

# Parametros termohidraulicos
T_AMBIENT = 25.0         # °C
T_INLET_COOLANT = 280.0  # °C Temperatura del refrigerante de entrada
T_NOMINAL_FUEL = 620.0   # °C Temperatura de operacion nominal
T_WARNING_FUEL = 1100.0  # °C Alarma de alta temperatura
T_MELTDOWN_FUEL = 1900.0 # °C Umbral de degradacion severa
HEAT_CAPACITY_CORE = 1200.0 # Capacidad calorifica normalizada
COOLING_COEFF_PUMPS_ON = 38.0  # Coeficiente de transferencia con bombas activas
COOLING_COEFF_PUMPS_OFF = 5.0  # Conveccion natural sin bombeo forzado
ALPHA_DOPPLER = 0.00030  # Coeficiente de reactividad por efecto Doppler negativo (/°C)

# Paleta de colores (Tema Cuartel de Control / Reactor Cherenkov)
COLOR_BG = (14, 18, 26)
COLOR_VESSEL_OUTER = (48, 54, 66)
COLOR_VESSEL_INNER = (75, 85, 102)
COLOR_REFLECTOR = (95, 108, 128)
COLOR_WATER_BASE = (16, 42, 68)
COLOR_CHERENKOV_MAX = (0, 210, 255)

COLOR_U235 = (46, 213, 115)       # Verde esmeralda energetico
COLOR_U238 = (62, 86, 75)         # Verde oliva opaco (fertil)
COLOR_CONTROL_ROD = (235, 77, 75) # Rojo cadmio
COLOR_ROD_GUIDE = (35, 40, 52)

COLOR_NEUTRON_FAST = (85, 230, 255)    # Azul cian
COLOR_NEUTRON_THERMAL = (255, 235, 90) # Amarillo radiante
COLOR_FISSION_FLASH = (255, 140, 40)   # Naranja incandescente
COLOR_ABSORPTION = (180, 90, 240)      # Violeta de captura

COLOR_PANEL_BG = (22, 28, 40)
COLOR_PANEL_BORDER = (42, 54, 76)
COLOR_PANEL_HEADER = (30, 38, 54)
COLOR_TEXT_LIGHT = (235, 242, 250)
COLOR_TEXT_MUTED = (140, 155, 178)

COLOR_STATE_SHUTDOWN = (110, 120, 135)
COLOR_STATE_SUBCRITICAL = (60, 160, 255)
COLOR_STATE_CRITICAL = (40, 215, 120)
COLOR_STATE_SUPERCRITICAL = (255, 195, 45)
COLOR_STATE_SCRAM = (240, 55, 65)


class ReactorState(Enum):
    """Estados operacionales del reactor nuclear."""
    SHUTDOWN = "APAGADO"
    SUBCRITICAL = "SUBCRITICO (k < 1.0)"
    CRITICAL = "CRITICO (k = 1.0)"
    SUPERCRITICAL = "SUPERCRITICO (k > 1.0)"
    PROMPT_CRITICAL = "PROMPT CRITICO (EXCURSION)"
    SCRAM = "PARADA DE EMERGENCIA (SCRAM)"


class NeutronEnergy(Enum):
    """Nivel de energia cinetica del neutron."""
    FAST = "RAPIDO"
    THERMAL = "TERMICO"
