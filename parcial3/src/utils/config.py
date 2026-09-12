"""
Configuracion global y parametros por defecto del Parcial III.

Universidad Jose Antonio Paez - Facultad de Ingenieria
Escuela de Ingenieria en Computacion - Metodos Cuantitativos

Todos los valores por defecto salen del enunciado. Los dos supuestos propios
(no fijados por el enunciado) estan marcados de forma explicita como SUPUESTO.
El usuario puede sobreescribir la duracion de la corrida por teclado o por CLI.
"""

import os
from pathlib import Path
from typing import Dict

# --------------------------------------------------------------------------
# Directorios base del proyecto
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"

# Nombres canonicos de los artefactos generados
ARCHIVO_TRAZA_P1 = "traza_problema1.log"
ARCHIVO_TRAZA_P2 = "traza_problema2.csv"
ARCHIVO_REPORTE_P1 = "reporte_problema1.txt"
ARCHIVO_REPORTE_P2 = "reporte_problema2.txt"
ARCHIVO_CONCLUSIONES = "conclusiones_manuscritas.txt"

# --------------------------------------------------------------------------
# Duracion de la simulacion (comun a los dos problemas)
# --------------------------------------------------------------------------
HORAS_DEFECTO = 8.0          # Periodo de simulacion por defecto, en horas
HORAS_MINIMO = 0.01          # Cota inferior aceptada al validar la entrada
HORAS_MAXIMO = 720.0         # Cota superior: 30 dias simulados

# --------------------------------------------------------------------------
# PROBLEMA 1 - Fabrica de laptops (eventos discretos, M/M/1 con inventario)
# --------------------------------------------------------------------------
LAMBDA_ORDENES_HORA = 10.0   # Llegadas Poisson: 10 ordenes por hora
MEDIA_ENSAMBLAJE_MIN = 5.0   # Servicio exponencial: media de 5 min por laptop
SERVIDORES = 1               # Estacion de ensamblaje unica -> sistema M/M/1
UMBRAL_CRITICO_S = 10        # Umbral critico (s): dispara la reposicion
LEAD_TIME_MIN = 15.0         # Lead time del proveedor, en minutos
LOTE_Q = 50                  # Tamano del lote de reposicion (Q), en unidades
STOCK_INICIAL = 50           # SUPUESTO PROPIO: el enunciado no fija el stock inicial
CONSUMO_POR_LAPTOP = 1       # SUPUESTO PROPIO: 1 procesador por laptop ensamblada
LOTE_PRODUCCION = 50         # Tamano del lote de produccion para medir el despacho

# Tasa de servicio derivada: 60 min/h dividido entre la media de ensamblaje.
# Con 5 min/laptop resulta mu = 12 laptops/hora.
MU_ENSAMBLAJE_HORA = 60.0 / MEDIA_ENSAMBLAJE_MIN

# Intervalo de muestreo temporal de L y Lq dentro del motor SimPy (segundos)
INTERVALO_MUESTREO_P1_S = 1.0

# --------------------------------------------------------------------------
# PROBLEMA 2 - Cluster de servidores (simulacion continua, EDO + RK4)
# --------------------------------------------------------------------------
# Distribucion del trafico entrante: Normal(3, 1) truncada al rango [1, 5] Gbps
TRAFICO_MEDIA_GBPS = 3.0
TRAFICO_DESV_GBPS = 1.0
TRAFICO_MIN_GBPS = 1.0
TRAFICO_MAX_GBPS = 5.0

# Constantes del balance termico:  C * dT/dt = P_idle + k * trafico - h * (T - T_amb)
# Estan calibradas para que el equilibrio con trafico medio (3 Gbps) caiga en 70 C
# exactos, que es la temperatura de diseno declarada en el enunciado.
T_AMB_C = 25.0               # Temperatura ambiente del datacenter, en grados Celsius
H_DISIP = 20.0               # Coeficiente de disipacion (refrigeracion liquida), en W/C
P_IDLE_W = 360.0             # Potencia disipada en reposo, en W
K_CARGA_W = 180.0            # Potencia adicional por Gbps de trafico, en W/Gbps
C_TERMICA = 2400.0           # Capacidad termica del cluster, en J/C

# Constante de tiempo del sistema de primer orden: tau = C / h = 120 s
TAU_TERMICA_S = C_TERMICA / H_DISIP

# Temperatura inicial de la corrida. Se arranca en el equilibrio nominal (70 C)
# para que las metricas de variabilidad midan la respuesta al trafico y no el
# transitorio de encendido, que es un artefacto de arranque.
TEMP_INICIAL_C = 70.0

# Thermal throttling: la eficiencia es 90% hasta la temperatura de diseno y cae
# 2 puntos porcentuales por cada grado por encima, con un piso de 30%.
TEMP_DISENO_C = 70.0
EFICIENCIA_BASE = 0.90
PENALIZACION_POR_GRADO = 0.02
EFICIENCIA_MINIMA = 0.30

# Integracion numerica y muestreo
PASO_INTEGRACION_S = 1.0     # Paso de RK4: 1 segundo simulado
INTERVALO_RESORTEO_S = 60.0  # El trafico se re-sortea cada 60 s (retencion de orden cero)
INTERVALO_TRAZA_P2_S = 60.0  # Muestreo de la traza CSV: 1 fila por minuto simulado
HISTORIAL_MAX_PUNTOS = 300   # Ventana acotada de temperatura para el oscilograma de la GUI

# --------------------------------------------------------------------------
# Semillas por defecto (reproducibilidad de las corridas de entrega)
# --------------------------------------------------------------------------
SEMILLA_DEFECTO = 2026

# --------------------------------------------------------------------------
# Valores teoricos M/M/1 con lambda = 10 y mu = 12 (contraste del reporte)
# --------------------------------------------------------------------------
TEORICO_MM1 = {
    "rho": 0.833333,
    "p0": 0.166667,
    "l": 5.0,
    "lq": 4.166667,
    "w_horas": 0.5,
    "wq_horas": 0.416667,
    "w_min": 30.0,
    "wq_min": 25.0,
}

# --------------------------------------------------------------------------
# Prompts para la API de IA (uno por problema)
# --------------------------------------------------------------------------
PROMPT_PROBLEMA_1 = (
    "Actua como auditor cuantitativo experto en teoria de colas e inventarios. "
    "Analiza el siguiente reporte de una simulacion de eventos discretos de una fabrica "
    "de laptops con una unica estacion de ensamblaje (sistema M/M/1) y una politica de "
    "inventario (s, Q) para los procesadores. Responde en texto plano, sin markdown y sin "
    "emojis, en espanol, con esta estructura:\n"
    "1. Conclusion sobre el desempeno de la linea de ensamblaje y la teoria de colas.\n"
    "2. Conclusion sobre la politica de inventario y el reabastecimiento.\n"
    "3. Tres recomendaciones concretas de optimizacion, priorizadas."
)

PROMPT_PROBLEMA_2 = (
    "Actua como auditor experto en eficiencia energetica y termica de centros de datos. "
    "Analiza el siguiente reporte de una simulacion continua del comportamiento termico y "
    "de rendimiento de un cluster de servidores, resuelta con Runge-Kutta de cuarto orden. "
    "Responde en texto plano, sin markdown y sin emojis, en espanol, con esta estructura:\n"
    "1. Conclusion sobre el comportamiento termico y la estabilidad del equilibrio.\n"
    "2. Conclusion sobre el impacto del thermal throttling en el rendimiento entregado.\n"
    "3. Tres recomendaciones concretas de optimizacion, priorizadas."
)


def asegurar_directorio_salidas() -> Path:
    """Crea el directorio de salidas si no existe y devuelve su ruta."""
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUTS_DIR


def cargar_variables_entorno() -> Dict[str, str]:
    """
    Carga las credenciales de las APIs de IA en cascada.

    Orden de precedencia (gana el primero que aporte un valor no vacio):
      1. Variables de entorno del sistema.
      2. parcial3/.env
      3. metodos_cuantitativos/.env  (raiz del repositorio, compartido entre proyectos)
      4. .env del directorio de trabajo actual y de su padre.

    Nunca lanza excepcion: si no hay ninguna clave, el llamador cae al motor
    experto local de respaldo.
    """
    config = {
        "gemini": os.environ.get("GEMINI_API_KEY", "").strip(),
        "openai": os.environ.get("OPENAI_API_KEY", "").strip(),
        "local": os.environ.get("LOCAL_API_URL", os.environ.get("OLLAMA_URL", "")).strip(),
    }

    claves = {
        "GEMINI_API_KEY": "gemini",
        "OPENAI_API_KEY": "openai",
        "LOCAL_API_URL": "local",
        "OLLAMA_URL": "local",
    }

    rutas_env = [
        BASE_DIR / ".env",
        BASE_DIR.parent / ".env",
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
    ]

    for ruta in rutas_env:
        if not ruta.is_file():
            continue
        try:
            texto = ruta.read_text(encoding="utf-8")
        except OSError:
            # Un .env ilegible no debe tumbar la simulacion: se ignora esa ruta
            # y se sigue con la siguiente de la cascada.
            continue
        for linea in texto.splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            nombre, _, valor = linea.partition("=")
            destino = claves.get(nombre.strip())
            if destino and not config[destino]:
                config[destino] = valor.strip().strip('"').strip("'")

    return config
