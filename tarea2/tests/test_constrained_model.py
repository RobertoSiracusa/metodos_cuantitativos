import pytest
from src.core.constrained_model import ModeloRestriccionesInventario, calcular_lambda_aproximado

def test_modelo_restricciones_sin_activacion():
    # Caso 8 de la guia: 3 articulos con holgura
    mod = ModeloRestriccionesInventario(
        articulos=['A', 'B', 'C'],
        demandas=[100, 150, 200],
        costos_pedido=[20, 25, 30],
        costos_almacenamiento=[2, 3, 4],
        capacidad_total=500,
        presupuesto=1000,
        demandas_diarias=[5, 6, 7],
        tiempos_entrega=[2, 3, 4],
        metodo="Multiplicadores de Lagrange (Exacto)"
    )
    mod.calcular()

    assert pytest.approx(mod.resultados_articulos['A']['cantidad_pedir'], rel=1e-2) == 44.72
    assert pytest.approx(mod.resultados_articulos['B']['cantidad_pedir'], rel=1e-2) == 50.00
    assert pytest.approx(mod.resultados_articulos['C']['cantidad_pedir'], rel=1e-2) == 54.77

    assert mod.resultados_articulos['A']['rop'] == 10.0
    assert mod.resultados_articulos['B']['rop'] == 18.0
    assert mod.resultados_articulos['C']['rop'] == 28.0

    assert pytest.approx(mod.espacio_utilizado, rel=1e-2) == 149.49
    assert pytest.approx(mod.costo_total, rel=1e-2) == 458.53
    assert mod.lambda_calculado == 0.0

    reporte = mod.generar_reporte()
    assert "REPORTE DE INVENTARIO: MULTI-ARTICULO CON REST." in reporte
    assert "Diagnostico de Restricciones y Holguras" in reporte

def test_modelo_restricciones_con_activacion_lagrange():
    mod = ModeloRestriccionesInventario(
        articulos=['A', 'B', 'C'],
        demandas=[100, 150, 200],
        costos_pedido=[20, 25, 30],
        costos_almacenamiento=[2, 3, 4],
        capacidad_total=100,
        presupuesto=1000,
        demandas_diarias=[5, 6, 7],
        tiempos_entrega=[2, 3, 4],
        metodo="Multiplicadores de Lagrange (Exacto)"
    )
    mod.calcular()

    assert mod.lambda_calculado > 0.0
    assert pytest.approx(mod.espacio_utilizado, abs=0.1) == 100.0
    assert mod.costo_total > 458.53

def test_lambda_aproximado():
    l_aprox = calcular_lambda_aproximado(
        demandas=[100, 150, 200],
        costos_pedido=[20, 25, 30],
        costos_almacenamiento=[2, 3, 4],
        areas=[1.0, 1.0, 1.0],
        capacidad_total=100
    )
    assert l_aprox > 0.0
