"""
Punto de Entrada Principal — Calculadora de Teoria de Inventarios
Arquitectura Top-Down Modular.
"""
import sys
import os

# Asegurar que el directorio base este en sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.eoq_model import ModeloEOQClasico
from src.core.probabilistic_model import ModeloProbabilistico
from src.core.discount_model import ModeloQuiebrePrecios
from src.core.constrained_model import ModeloRestriccionesInventario
from src.gui.app import Application

def main():
    """Lanza la aplicacion con interfaz grafica."""
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()
