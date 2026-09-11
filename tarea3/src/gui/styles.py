"""
Estilos, Constantes y Paleta de Colores (Slate 900 & Neon)
Capa de Presentacion — Metodos Cuantitativos
Universidad Jose Antonio Paez
"""

from typing import Tuple

# Dimensiones base por defecto
SCREEN_WIDTH = 1260
SCREEN_HEIGHT = 740
NET_VIEW_WIDTH = 850
HUD_WIDTH = SCREEN_WIDTH - NET_VIEW_WIDTH

# Paleta de Colores Principal (Slate 900)
COLOR_BG = (15, 23, 42)              # Fondo principal (Slate 900)
COLOR_NET_GRID = (24, 34, 53)        # Rejilla suave de topologia
COLOR_HUD_BG = (18, 28, 48)          # Fondo del panel lateral HUD
COLOR_CARD_BG = (30, 41, 59)         # Tarjetas de telemetria (Slate 800)
COLOR_CARD_BORDER = (51, 65, 85)     # Bordes de tarjetas (Slate 700)

# Colores de Texto de Alto Contraste
COLOR_TEXT_WHITE = (255, 255, 255)   # Blanco puro
COLOR_TEXT_MUTED = (226, 232, 240)   # Slate 200 (legibilidad maxima)
COLOR_TEXT_DIM = (160, 174, 192)     # Slate 400 secundario
COLOR_TEXT_CYAN = (103, 232, 249)    # Cian 300 luminoso
COLOR_TEXT_GOLD = (253, 224, 71)     # Oro 300

# Estados de Saturacion del Buffer exigidos por el enunciado:
# Verde < 50%, Amarillo 50%-80%, Rojo > 80%
COLOR_BUF_GREEN = (74, 222, 128)     # Verde esmeralda vivo (< 50%)
COLOR_BUF_YELLOW = (250, 204, 21)    # Amarillo ambar (50% - 80%)
COLOR_BUF_RED = (248, 113, 113)      # Rojo coral (> 80%)

# Colores de Nodos y Enlaces
COLOR_SOURCE_NODE = (56, 189, 248)   # Nodos de origen (Cian)
COLOR_DEST_NODE = (192, 132, 252)    # Nodos de destino (Purpura)
COLOR_LINK_ACTIVE = (80, 95, 120)    # Enlaces operativos
COLOR_LINK_HIGHLIGHT = (56, 189, 248)# Enlace con transmision activa
COLOR_LINK_BROKEN = (248, 113, 113)  # Enlace caido / inactivo

# Insignias de Telemetria (Badges)
BADGE_GREEN_BG = (20, 83, 45)
BADGE_GREEN_TXT = (187, 247, 208)
BADGE_YELLOW_BG = (113, 63, 18)
BADGE_YELLOW_TXT = (254, 240, 138)
BADGE_RED_BG = (127, 29, 29)
BADGE_RED_TXT = (254, 202, 202)
BADGE_BLUE_BG = (30, 58, 138)
BADGE_BLUE_TXT = (219, 234, 254)
