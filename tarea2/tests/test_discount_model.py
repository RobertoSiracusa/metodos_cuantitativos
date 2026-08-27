import pytest
from src.core.discount_model import ModeloQuiebrePrecios, calcular_quiebre_precios

def test_modelo_quiebre_precios_guia():
    # Caso 4 de la guia: Descuentos por volumen
    tramos = [
        (0, 999, 5.0),
        (1000, 1999, 4.8),
        (2000, float('inf'), 4.75)
    ]
    mod = ModeloQuiebrePrecios(
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
