"""
test_simulacion.py
==============================================================================
Pruebas Unitarias y Validación Automatizada del Simulador de Redes
Facultad de Ingeniería - Universidad José Antonio Páez
==============================================================================
"""

import os
import sys
import unittest
import numpy as np

from hungarian_router import HungarianRouter, PENALIZACION_ENLACE_CAIDO
from red_simulacion import NetworkSimulation, RouterNode, Packet, PacketState
from gemini_client import GeminiNetworkAuditor, obtener_api_key


class TestSimuladorRedes(unittest.TestCase):

    def test_01_hungarian_router_cost_matrix(self):
        """Verifica el cálculo de la matriz C_ij = Latencia + alpha * Saturación."""
        router = HungarianRouter(alpha=50.0)
        enlaces = [
            {"latencia_ms": 10.0, "saturacion_nodo_destino": 0.20, "activo": True},   # Costo = 10 + 50*0.2 = 20.0
            {"latencia_ms": 15.0, "saturacion_nodo_destino": 0.80, "activo": True},   # Costo = 15 + 50*0.8 = 55.0
            {"latencia_ms": 5.0,  "saturacion_nodo_destino": 0.00, "activo": False},  # Caído = 1_000_000.0
        ]
        matriz = router.calcular_matriz_costos(num_flujos=2, enlaces_info=enlaces)

        self.assertEqual(matriz.shape, (2, 3))
        self.assertAlmostEqual(matriz[0, 0], 20.0)
        self.assertAlmostEqual(matriz[0, 1], 55.0)
        self.assertEqual(matriz[0, 2], PENALIZACION_ENLACE_CAIDO)

    def test_02_hungarian_assignment_resolution(self):
        """Verifica que el Algoritmo Húngaro asigna los flujos al menor costo y descarta enlaces caídos."""
        router = HungarianRouter(alpha=40.0)
        enlaces = [
            {"latencia_ms": 25.0, "saturacion_nodo_destino": 0.1, "activo": True},  # C = 29.0
            {"latencia_ms": 10.0, "saturacion_nodo_destino": 0.1, "activo": True},  # C = 14.0 (Mejor)
            {"latencia_ms": 5.0,  "saturacion_nodo_destino": 0.0, "activo": False}, # Caído
        ]
        res = router.resolver_asignacion(num_flujos=2, enlaces_info=enlaces)

        self.assertEqual(len(res.pares_asignados), 2)
        # El flujo que tome el enlace 1 debe tener costo 14.0
        enlaces_asignados = [e for _, e in res.pares_asignados]
        self.assertIn(1, enlaces_asignados)
        self.assertNotIn(2, enlaces_asignados)  # Enlace 2 está caído, no debe asignarse

    def test_03_simpy_network_simulation_run(self):
        """Ejecuta una corrida estocástica en SimPy durante 120 segundos simulados y valida métricas."""
        sim = NetworkSimulation(lam=15.0, mu=18.0, capacidad_s=50, umbral_s=10, lote_q=15)

        # Ejecutar 120 segundos de tiempo de simulación
        sim.env.run(until=120.0)
        metricas = sim.obtener_metricas_completas()

        self.assertGreaterEqual(metricas["tiempo_simulacion_s"], 120.0)
        self.assertGreater(metricas["paquetes_procesados"], 1000)
        self.assertGreater(metricas["promedio_paquetes_sistema_l"], 0.0)
        self.assertGreater(metricas["costo_almacenamiento_usd"], 0.0)
        self.assertGreater(metricas["costo_global_usd"], 0.0)

    def test_04_buffer_overflow_and_holding_costs(self):
        """Verifica que bajo tráfico excesivo (lambda >> mu) se producen descartes y costos de penalización."""
        sim_stress = NetworkSimulation(lam=80.0, mu=10.0, capacidad_s=15, umbral_s=5, lote_q=10)
        sim_stress.env.run(until=30.0)
        metricas = sim_stress.obtener_metricas_completas()

        self.assertGreater(metricas["paquetes_perdidos"], 0)
        self.assertGreater(metricas["tasa_perdida_pct"], 0.0)
        self.assertGreater(metricas["costo_penalizacion_usd"], 0.0)

    def test_05_export_report_txt_and_gemini_auditor(self):
        """Verifica que el archivo reporte_simulacion.txt se crea con el formato exacto requerido."""
        sim = NetworkSimulation(lam=15.0, mu=18.0, capacidad_s=50, umbral_s=10, lote_q=15)
        sim.env.run(until=120.0)
        metricas = sim.obtener_metricas_completas()

        auditor = GeminiNetworkAuditor()
        ruta_txt = "reporte_simulacion.txt"
        contenido = auditor.auditar_simulacion(metricas, ruta_txt)

        self.assertTrue(os.path.exists(ruta_txt))
        with open(ruta_txt, "r", encoding="utf-8") as f:
            texto = f.read()

        # Comprobar secciones obligatorias del PDF
        self.assertIn("REPORTE DE SIMULACIÓN DE RED", texto)
        self.assertIn("Tiempo Total de Simulación:", texto)
        self.assertIn("Tasa de Llegada (lambda):", texto)
        self.assertIn("Tasa de Servicio (mu):", texto)
        self.assertIn("Capacidad de Buffer (S):", texto)
        self.assertIn("Umbral Reabastecimiento (s):", texto)
        self.assertIn("METRICAS OBTENIDAS:", texto)
        self.assertIn("Paquetes Procesados:", texto)
        self.assertIn("Paquetes Perdidos (Overflow):", texto)
        self.assertIn("Tiempo Medio en Cola (Wq):", texto)
        self.assertIn("Promedio Paquetes en Sistema (L):", texto)
        self.assertIn("Costo Total de Almacenamiento:", texto)
        self.assertIn("Costo Total de Penalización (Ruptura):", texto)
        self.assertIn("Costo Global del Sistema:", texto)
        self.assertIn("ANÁLISIS AUTOMATIZADO Y RECOMENDACIONES", texto)


if __name__ == "__main__":
    unittest.main()
