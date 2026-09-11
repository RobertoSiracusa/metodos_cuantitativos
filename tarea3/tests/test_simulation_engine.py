"""
Pruebas Unitarias para el Motor de Simulacion Estocastica (SimPy)
"""

import pytest
from src.services.simulation_service import NetworkSimulation


def test_simulacion_estocastica_120s():
    sim = NetworkSimulation(lam=15.0, mu=18.0, capacidad_s=50, umbral_s=10, lote_q=15)
    sim.env.run(until=120.0)

    m = sim.obtener_metricas_completas()
    assert m["tiempo_simulacion_s"] >= 120.0
    assert m["paquetes_procesados"] > 1000
    assert m["tiempo_medio_cola_wq_s"] >= 0.0
    assert m["promedio_paquetes_sistema_l"] > 0.0
    assert m["costo_global_usd"] > 0.0


def test_conmutacion_enlace_falla():
    sim = NetworkSimulation(lam=10.0, mu=15.0)
    # Probar corte de enlace S1-R1
    estado_ini = sim.ingress_links["S1-R1"].active
    assert estado_ini is True

    estado_nuevo = sim.toggle_enlace("S1-R1")
    assert estado_nuevo is False
    assert sim.ingress_links["S1-R1"].active is False

    # Restaurar enlace
    sim.toggle_enlace("S1-R1")
    assert sim.ingress_links["S1-R1"].active is True


def test_estres_y_desbordamiento_buffer():
    # Sobrecargar el sistema: lambda muy alta (100 paq/s), capacidad diminuta (S=3)
    sim = NetworkSimulation(lam=100.0, mu=5.0, capacidad_s=3, umbral_s=1, lote_q=2)
    sim.env.run(until=20.0)

    m = sim.obtener_metricas_completas()
    assert m["paquetes_perdidos"] > 0
    assert m["tasa_perdida_pct"] > 0.0
    assert m["costo_penalizacion_usd"] > 0.0
