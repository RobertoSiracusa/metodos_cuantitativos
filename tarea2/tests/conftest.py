import sys
import os

# Anadir el directorio raiz de tarea2 al sys.path para ejecucion de tests
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
