"""
Configuracion Global y Parametros del Sistema
Universidad Jose Antonio Paez — Metodos Cuantitativos
"""

import os
from pathlib import Path
from typing import Dict

# Directorios base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Valores por defecto para Teoria de Colas
LAMBDA_DEFECTO = 15.0       # Tasa de llegada media (paquetes/segundo)
MU_DEFECTO = 18.0           # Tasa de servicio media por servidor (paquetes/segundo)

# Valores por defecto para Modelos de Inventario en Buffers
CAPACIDAD_BUFFER_S = 50     # Capacidad maxima de buffer por router (S)
UMBRAL_REABASTECER_S = 10   # Umbral minimo de reabastecimiento (s)
LOTE_REABASTECER_Q = 15     # Tamano de lote de liberacion (Q)
COSTO_HOLDING_POR_SEG = 0.05    # USD por paquete por segundo en buffer
COSTO_PENALIZACION_RUPTURA = 10.0  # USD por paquete perdido por desborde

# Parametros para Algoritmo Hungaro
ALPHA_DEFECTO = 40.0        # Ponderacion de saturacion de buffer vs latencia (ms)
INTERVALO_HUNGARO_DT = 1.0  # Intervalo de optimizacion Delta t (segundos)
PENALIZACION_ENLACE_CAIDO = 1_000_000.0  # Costo prohibitivo para enlace caido

# Prompt Oficial para la API de IA segun el enunciado
PROMPT_OFICIAL = (
    "Analiza los siguientes resultados de desempeno de un simulador de red basado en teoria "
    "de colas e inventario. Evalua la tasa de perdida de paquetes, tiempos de espera y costos, "
    "e indica conclusiones detalladas y 3 recomendaciones de optimizacion."
)


def cargar_variables_entorno() -> Dict[str, str]:
    """Carga credenciales desde .env si existe o lee las variables de entorno del sistema."""
    config = {
        "gemini": os.environ.get("GEMINI_API_KEY", "").strip(),
        "openai": os.environ.get("OPENAI_API_KEY", "").strip(),
        "local": os.environ.get("LOCAL_API_URL", os.environ.get("OLLAMA_URL", "")).strip(),
    }

    rutas_env = [
        BASE_DIR / ".env",
        Path.cwd() / ".env",
    ]

    for ruta in rutas_env:
        if ruta.exists():
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    for linea in f:
                        linea = linea.strip()
                        if not linea or linea.startswith("#"):
                            continue
                        if linea.startswith("GEMINI_API_KEY=") and not config["gemini"]:
                            config["gemini"] = linea.split("=", 1)[1].strip().strip('"').strip("'")
                        elif linea.startswith("OPENAI_API_KEY=") and not config["openai"]:
                            config["openai"] = linea.split("=", 1)[1].strip().strip('"').strip("'")
                        elif (linea.startswith("LOCAL_API_URL=") or linea.startswith("OLLAMA_URL=")) and not config["local"]:
                            config["local"] = linea.split("=", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass

    return config
