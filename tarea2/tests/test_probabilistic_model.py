import pytest
from src.core.probabilistic_model import ModeloProbabilistico, obtener_z, calcular_rop

def test_modelo_probabilistico_desayunos():
    # Caso 7 de la guia: Distribuidor de desayunos
    mod = ModeloProbabilistico(
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
    assert pytest.approx(mod.stock_seguridad, rel=1e-3) == 495.0 # Z = 1.65
    assert pytest.approx(mod.rop, rel=1e-3) == 1295.0
    assert pytest.approx(mod.costo_total_pedidos, rel=1e-3) == 1000.0
    assert pytest.approx(mod.costo_almacenaje_ciclo, rel=1e-3) == 1000.0
    assert pytest.approx(mod.costo_almacenaje_seguridad, rel=1e-3) == 990.0
    assert pytest.approx(mod.costo_operacional_total, rel=1e-3) == 2990.0

    reporte = mod.generar_reporte()
    assert "REPORTE DE INVENTARIO: MODELO PROBABILISTICO" in reporte
    assert "1000.00 unidades" in reporte

def test_obtener_z_metodos():
    z_tabla = obtener_z(0.95, metodo="tabla")
    assert z_tabla == 1.65

    z_exacto = obtener_z(0.95, metodo="exacto")
    assert pytest.approx(z_exacto, rel=1e-3) == 1.6449

    z_manual = obtener_z(0.95, metodo="manual", z_personalizado=1.96)
    assert z_manual == 1.96

def test_calcular_rop_directo():
    res = calcular_rop(
        demanda_promedio_diaria=200,
        desviacion_estandar_demanda=150,
        tiempo_entrega=4,
        nivel_servicio=0.95,
        metodo_z="tabla"
    )
    assert pytest.approx(res["ROP"], rel=1e-3) == 1295.0
    assert pytest.approx(res["Stock de seguridad"], rel=1e-3) == 495.0
