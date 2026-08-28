"""
Modulo de Vistas de la Interfaz Grafica.
"""
from src.gui.views.eoq_view import EOQClasicoFrame
from src.gui.views.probabilistic_view import ProbabilisticoFrame
from src.gui.views.discount_view import DescuentosTramosFrame
from src.gui.views.constrained_view import RestriccionesFrame

__all__ = [
    "EOQClasicoFrame",
    "ProbabilisticoFrame",
    "DescuentosTramosFrame",
    "RestriccionesFrame"
]
