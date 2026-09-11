"""
Pruebas Unitarias para el Algoritmo Hungaro (SciPy y Kuhn-Munkres Nativo)
"""

import pytest
import numpy as np
from src.core.hungarian_model import ModeloAsignacionHungaro
from src.utils.config import PENALIZACION_ENLACE_CAIDO


def test_matriz_costos_hungaro():
    router = ModeloAsignacionHungaro(alpha=50.0)
    enlaces = [
        {"latencia_ms": 10.0, "saturacion_nodo_destino": 0.20, "activo": True},   # 10 + 50*0.2 = 20.0
        {"latencia_ms": 15.0, "saturacion_nodo_destino": 0.80, "activo": True},   # 15 + 50*0.8 = 55.0
        {"latencia_ms": 5.0,  "saturacion_nodo_destino": 0.00, "activo": False},  # Caido = 1_000_000.0
    ]
    matriz = router.calcular_matriz_costos(num_flujos=2, enlaces_info=enlaces)

    assert matriz.shape == (2, 3)
    assert pytest.approx(matriz[0, 0]) == 20.0
    assert pytest.approx(matriz[0, 1]) == 55.0
    assert matriz[0, 2] == PENALIZACION_ENLACE_CAIDO


def test_resolucion_scipy_y_nativo():
    router = ModeloAsignacionHungaro(alpha=40.0)
    enlaces = [
        {"latencia_ms": 25.0, "saturacion_nodo_destino": 0.1, "activo": True},   # 25 + 4 = 29.0
        {"latencia_ms": 10.0, "saturacion_nodo_destino": 0.1, "activo": True},   # 10 + 4 = 14.0 (Optimo)
        {"latencia_ms": 5.0,  "saturacion_nodo_destino": 0.0, "activo": False},  # Caido
    ]

    # 1. Resolucion regular (SciPy si disponible)
    res = router.resolver_asignacion(num_flujos=2, enlaces_info=enlaces)
    assert len(res.pares_asignados) == 2
    enlaces_asignados = [e for _, e in res.pares_asignados]
    assert 1 in enlaces_asignados
    assert 0 in enlaces_asignados
    assert 2 not in enlaces_asignados  # Enlace caido descartado
    assert pytest.approx(res.costo_total) == 43.0

    # 2. Resolucion forzando Kuhn-Munkres nativo (prueba del motor de contingencia)
    res_nativo = router.resolver_asignacion(num_flujos=2, enlaces_info=enlaces, forzar_nativo=True)
    assert len(res_nativo.pares_asignados) == 2
    enlaces_nativo = [e for _, e in res_nativo.pares_asignados]
    assert 1 in enlaces_nativo
    assert 0 in enlaces_nativo
    assert 2 not in enlaces_nativo
    assert pytest.approx(res_nativo.costo_total) == 43.0
