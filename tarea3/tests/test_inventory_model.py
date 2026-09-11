"""
Pruebas Unitarias para el Modelo de Gestion de Inventario (Buffers)
"""

import pytest
from src.core.inventory_model import ModeloInventarioBuffer


def test_inventario_costos_y_salud():
    inv = ModeloInventarioBuffer(
        capacidad_s=50,
        umbral_s=10,
        lote_q=15,
        costo_holding_por_seg=0.05,
        costo_ruptura=10.0,
    )

    inv.registrar_desempeno(costo_almacenamiento=125.40, paquetes_perdidos=42, paquetes_procesados=1750)

    assert inv.costo_almacenamiento_total == 125.40
    assert inv.costo_penalizacion_total == 420.00
    assert inv.costo_global == 545.40

    salud = inv.evaluar_salud_inventario()
    assert salud["nivel"] == "MODERADO"
    assert "2.34%" in salud["tasa_perdida"] or "2.35%" in salud["tasa_perdida"]

    reporte = inv.generar_reporte()
    assert "REPORTE DE GESTION DE INVENTARIO" in reporte
    assert "$545.40" in reporte
