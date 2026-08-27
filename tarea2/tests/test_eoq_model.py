import pytest
from src.core.eoq_model import ModeloEOQClasico

def test_eoq_clasico_ramon():
    # Caso 1 de la guia: Ramon distribuidor de laptops Acer
    demanda = 500
    costo_pedido = 5000
    costo_mantenimiento = 25
    precio_unitario = 3700

    modelo = ModeloEOQClasico(
        demanda=demanda,
        costo_pedido=costo_pedido,
        costo_mantenimiento=costo_mantenimiento,
        precio_unitario=precio_unitario,
        es_mensual=False,
        i_porcentaje=0.68
    )
    modelo.calcular()

    assert pytest.approx(modelo.eoq, rel=1e-3) == 447.21
    assert pytest.approx(modelo.num_pedidos, rel=1e-3) == 1.118
    assert pytest.approx(modelo.frecuencia_meses, rel=1e-3) == 10.733
    assert pytest.approx(modelo.costo_pedido_anual, rel=1e-3) == 5590.17
    assert pytest.approx(modelo.costo_mantenimiento_anual, rel=1e-3) == 5590.17
    assert pytest.approx(modelo.costo_adquisicion_anual, rel=1e-3) == 1850000.0
    assert pytest.approx(modelo.costo_total_anual, rel=1e-3) == 1861180.34
    
    reporte = modelo.generar_reporte()
    assert "REPORTE DE INVENTARIO: MODELO EOQ CLASICO" in reporte
    assert "447.21 unidades" in reporte

def test_eoq_clasico_cls_company():
    # Caso 3 de la guia: CLS Computer Company
    modelo = ModeloEOQClasico(
        demanda=27,
        costo_pedido=12000,
        costo_mantenimiento=18000, # 1500 * 12
        es_mensual=False
    )
    modelo.calcular()
    assert modelo.eoq == 6.0
    assert modelo.num_pedidos == 4.5

def test_eoq_clasico_articulos_comprados():
    # Caso 6 de la guia: Articulos comprados
    modelo = ModeloEOQClasico(
        demanda=1000,
        costo_pedido=5,
        costo_mantenimiento=4,
        precio_unitario=20,
        es_mensual=False
    )
    modelo.calcular()
    assert modelo.eoq == 50.0
    assert modelo.costo_pedido_anual == 100.0
    assert modelo.costo_mantenimiento_anual == 100.0
