import math
import pytest
from src.core import (
    ModeloEOQClasico,
    ModeloProbabilistico,
    ModeloQuiebrePrecios,
    ModeloRestriccionesInventario,
    calcular_eoq_prob,
    calcular_rop,
    obtener_z,
    calcular_quiebre_precios,
    resolver_restricciones_lagrange
)
import src.core.probabilistic_model as mp
import src.core.discount_model as mq
import src.core.constrained_model as pr

# Test Modelo EOQ Clasico
def test_eoq_clasico_ramon():
    demanda = 500
    costo_pedido = 5000
    costo_mantenimiento = 25
    precio_unitario = 3700

    q_opt = mp.calcular_eoq(demanda, costo_pedido, costo_mantenimiento)
    assert pytest.approx(q_opt, rel=1e-3) == 447.21

    num_pedidos = demanda / q_opt
    assert pytest.approx(num_pedidos, rel=1e-3) == 1.118

    costo_pedidos = (demanda / q_opt) * costo_pedido
    costo_almacenaje = (q_opt / 2) * costo_mantenimiento
    costo_adquisicion = demanda * precio_unitario
    costo_total = costo_pedidos + costo_almacenaje + costo_adquisicion

    assert pytest.approx(costo_pedidos, rel=1e-3) == 5590.17
    assert pytest.approx(costo_almacenaje, rel=1e-3) == 5590.17
    assert pytest.approx(costo_total, rel=1e-3) == 1861180.34

def test_eoq_clasico_cls_company():
    demanda_anual = 27
    costo_pedido = 12000
    costo_mantenimiento_anual = 1500 * 12

    q_opt = mp.calcular_eoq(demanda_anual, costo_pedido, costo_mantenimiento_anual)
    assert q_opt == 6.0
    assert demanda_anual / q_opt == 4.5

def test_eoq_clasico_articulos_comprados():
    demanda = 1000
    costo_pedido = 5
    costo_almacenaje = 4
    
    q_opt = mp.calcular_eoq(demanda, costo_pedido, costo_almacenaje)
    assert q_opt == 50.0

# Test Modelo Probabilistico
def test_modelo_probabilistico_desayunos():
    mod = mp.ModeloProbabilistico(
        demanda_diaria=200,
        desviacion_estandar=150,
        tiempo_entrega=4,
        nivel_servicio=0.95,
        costo_pedido=20,
        precio_unitario=10,
        costo_mantenimiento_pct=20,
        dias_habiles=250,
        metodo_z="tabla"
    )
    mod.calcular()

    assert mod.demanda_anual == 50000.0
    assert mod.costo_almacenaje_anual == 2.0
    assert pytest.approx(mod.eoq, rel=1e-3) == 1000.0
    assert pytest.approx(mod.demanda_tiempo_entrega, rel=1e-3) == 800.0
    assert pytest.approx(mod.desv_tiempo_entrega, rel=1e-3) == 300.0
    assert pytest.approx(mod.stock_seguridad, rel=1e-3) == 495.0
    assert pytest.approx(mod.rop, rel=1e-3) == 1295.0
    assert pytest.approx(mod.costo_total_pedidos, rel=1e-3) == 1000.0
    assert pytest.approx(mod.costo_almacenaje_ciclo, rel=1e-3) == 1000.0
    assert pytest.approx(mod.costo_almacenaje_seguridad, rel=1e-3) == 990.0
    assert pytest.approx(mod.costo_operacional_total, rel=1e-3) == 2990.0

    reporte = mod.generar_reporte()
    assert "REPORTE DE INVENTARIO: MODELO PROBABILISTICO" in reporte
    assert "1000.00 unidades" in reporte

def test_modelo_probabilistico_z_exacto():
    mod = mp.ModeloProbabilistico(
        demanda_diaria=200,
        desviacion_estandar=150,
        tiempo_entrega=4,
        nivel_servicio=0.95,
        costo_pedido=20,
        precio_unitario=10,
        costo_mantenimiento_pct=20,
        dias_habiles=250,
        metodo_z="exacto"
    )
    mod.calcular()
    assert pytest.approx(mod.z, rel=1e-3) == 1.6449
    assert pytest.approx(mod.stock_seguridad, rel=1e-3) == 493.46

# Test Modelo de Quiebre de Precios
def test_modelo_quiebre_precios_guia():
    tramos = [
        (0, 999, 5.0),
        (1000, 1999, 4.8),
        (2000, float('inf'), 4.75)
    ]
    mod = mq.ModeloQuiebrePrecios(
        demanda_anual=5000,
        costo_pedido=49,
        costo_almacenamiento_porcentaje=20,
        tramos=tramos
    )
    mod.calcular()

    assert len(mod.resultados_tramos) == 3
    
    t1 = mod.resultados_tramos[0]
    assert pytest.approx(t1["eoq_calculado"], rel=1e-2) == 700.0
    assert pytest.approx(t1["cantidad_ajustada"], rel=1e-2) == 700.0
    assert pytest.approx(t1["costo_total"], rel=1e-2) == 25700.0
    assert t1["factible"] is True

    t2 = mod.resultados_tramos[1]
    assert pytest.approx(t2["eoq_calculado"], rel=1e-2) == 714.43
    assert pytest.approx(t2["cantidad_ajustada"], rel=1e-2) == 1000.0
    assert pytest.approx(t2["costo_total"], rel=1e-2) == 24725.0
    assert t2["factible"] is True

    t3 = mod.resultados_tramos[2]
    assert pytest.approx(t3["eoq_calculado"], rel=1e-2) == 718.18
    assert pytest.approx(t3["cantidad_ajustada"], rel=1e-2) == 2000.0
    assert pytest.approx(t3["costo_total"], rel=1e-2) == 24822.50
    assert t3["factible"] is True

    assert mod.optimo["tramo"] == 2
    assert pytest.approx(mod.optimo["cantidad"], rel=1e-2) == 1000.0
    assert pytest.approx(mod.optimo["costo_total"], rel=1e-2) == 24725.0

    reporte = mod.generar_reporte()
    assert "REPORTE DE INVENTARIO: QUIEBRE DE PRECIOS" in reporte
    assert "OPTIMO RECOMENDADO" in reporte

# Test Modelo Multi-Articulo con Restricciones
def test_modelo_restricciones_sin_activacion():
    mod = pr.ModeloRestriccionesInventario(
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

def test_modelo_restricciones_con_activacion_lagrange():
    mod = pr.ModeloRestriccionesInventario(
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
