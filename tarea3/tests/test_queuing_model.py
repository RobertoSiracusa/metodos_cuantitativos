"""
Pruebas Unitarias para el Modelo de Teoria de Colas (M/M/1/K)
"""

import pytest
from src.core.queuing_model import ModeloColasRed


def test_modelo_colas_calculo_teorico():
    modelo = ModeloColasRed(lamb=15.0, mu=18.0, capacidad_k=50, servidores_paralelos=4)
    modelo.calcular_teorico()

    # Cada router recibe 15.0 / 4 = 3.75 paq/s; mu = 18.0 -> rho = 3.75 / 18.0 = 0.2083
    assert pytest.approx(modelo.rho, rel=1e-3) == 0.2083
    assert modelo.p0 > 0.70  # Con baja utilizacion, P0 debe ser alta (> 75%)
    assert modelo.prob_bloqueo_pk < 1e-6  # Probabilidad de desborde casi nula
    assert modelo.l_teorico < 1.0
    assert modelo.wq_teorico < 0.05

    reporte = modelo.generar_reporte()
    assert "REPORTE DE TEORIA DE COLAS" in reporte
    assert "Factor de Utilizacion por Router (rho): 0.2083" in reporte


def test_verificacion_ley_little():
    modelo = ModeloColasRed(lamb=10.0, mu=12.0, capacidad_k=20, servidores_paralelos=2)
    # L = lambda * W
    cumple, err = modelo.verificar_ley_little(l_observado=1.5, w_observado=0.3, tasa_efectiva=5.0)
    assert cumple is True
    assert err == 0.0
