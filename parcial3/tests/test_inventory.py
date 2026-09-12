"""
Pruebas del inventario de procesadores y de la politica de reposicion (s, Q).

Cubre las tres cosas que pide el enunciado: que el pedido se dispare bajo el
umbral, que el lote entre despues del lead time, y que el contador de paradas
de linea funcione. Lo ultimo se ejercita con parametros ARTIFICIALES que si
agotan el stock: con los parametros oficiales el inventario nunca se vacia.
"""

import pytest

from src.core.factory_entities import InventarioProcesadores
from src.simulation.discrete_sim import FabricaSimulation
from src.utils.config import LEAD_TIME_MIN, LOTE_Q, STOCK_INICIAL, UMBRAL_CRITICO_S
from src.utils.validators import ValidacionError


# ----------------------------------------------------------------------
# Entidad de inventario aislada
# ----------------------------------------------------------------------

@pytest.fixture
def inventario():
    """Inventario con los parametros oficiales: 50 unidades, s = 10, Q = 50."""
    return InventarioProcesadores(
        nivel_inicial=STOCK_INICIAL,
        umbral_critico=UMBRAL_CRITICO_S,
        capacidad_lote=LOTE_Q,
    )


def test_estado_inicial(inventario):
    assert inventario.nivel == 50
    assert inventario.hay_stock
    assert not inventario.bajo_umbral
    assert not inventario.en_reposicion
    assert not inventario.necesita_reposicion()


def test_no_dispara_por_encima_del_umbral(inventario):
    """En el umbral exacto todavia no se dispara: la condicion es estrictamente menor."""
    for _ in range(40):
        inventario.consumir()
    assert inventario.nivel == 10
    assert not inventario.bajo_umbral
    assert not inventario.necesita_reposicion()


def test_dispara_por_debajo_del_umbral(inventario):
    for _ in range(41):
        inventario.consumir()
    assert inventario.nivel == 9
    assert inventario.bajo_umbral
    assert inventario.necesita_reposicion()


def test_un_solo_pedido_en_transito(inventario):
    for _ in range(41):
        inventario.consumir()
    inventario.registrar_pedido()
    assert inventario.en_reposicion
    assert not inventario.necesita_reposicion(), "no debe pedir dos veces lo mismo"
    with pytest.raises(ValidacionError, match="transito"):
        inventario.registrar_pedido()


def test_el_lote_entra_y_cierra_el_pedido(inventario):
    for _ in range(41):
        inventario.consumir()
    inventario.registrar_pedido()
    nivel = inventario.recibir_lote()
    assert nivel == 59
    assert inventario.lotes_recibidos == 1
    assert inventario.unidades_recibidas == 50
    assert not inventario.en_reposicion


def test_nivel_minimo_historico(inventario):
    for _ in range(45):
        inventario.consumir()
    inventario.recibir_lote()
    assert inventario.nivel_minimo == 5
    assert inventario.nivel == 55


def test_consumir_sin_stock_falla_fuerte():
    """Dejar el inventario en negativo produciria metricas mudas: debe lanzar."""
    inv = InventarioProcesadores(nivel_inicial=1, umbral_critico=0, capacidad_lote=5)
    inv.consumir()
    assert not inv.hay_stock
    with pytest.raises(ValidacionError, match="insuficiente"):
        inv.consumir()


def test_politica_inconsistente_se_rechaza():
    """Un lote Q que no supera el umbral s dejaria al sistema oscilando."""
    with pytest.raises(ValidacionError):
        InventarioProcesadores(nivel_inicial=50, umbral_critico=50, capacidad_lote=10)


# ----------------------------------------------------------------------
# Inventario dentro del motor de simulacion
# ----------------------------------------------------------------------

def test_ciclo_de_reposicion_dura_el_lead_time(metricas_p1):
    """El lote debe ingresar exactamente LEAD_TIME_MIN despues del disparo."""
    assert metricas_p1["ciclos_reposicion_observados"] >= 1
    assert metricas_p1["ciclo_reposicion_promedio_min"] == pytest.approx(LEAD_TIME_MIN, abs=1e-6)


def test_traza_registra_disparo_y_recepcion():
    sim = FabricaSimulation(semilla=2026)
    sim.ejecutar(8.0)
    lineas = sim.tracer.lineas
    disparos = [l for l in lineas if "DISPARO_REPOSICION" in l]
    recepciones = [l for l in lineas if "RECEPCION_LOTE" in l]
    assert disparos, "nunca se disparo una reposicion en 8 h"
    assert len(recepciones) == len(disparos)
    assert f"{LOTE_Q} procesadores" in recepciones[0]


def test_parametros_oficiales_no_producen_paradas(metricas_p1):
    """
    Resultado esperado del modelo, no un defecto: el umbral s = 10 cubre de sobra
    el consumo durante el lead time (~2.5 unidades), asi que el stock nunca llega
    a cero y la linea no se detiene.
    """
    assert metricas_p1["paradas_por_falta_stock"] == 0
    assert metricas_p1["ordenes_retrasadas_por_stock"] == 0
    assert metricas_p1["tiempo_linea_detenida_min"] == 0.0
    assert metricas_p1["eficiencia_reabastecimiento"] == pytest.approx(1.0)
    assert metricas_p1["stock_minimo"] > 0


# ----------------------------------------------------------------------
# Parametros artificiales que SI agotan el stock
# ----------------------------------------------------------------------

@pytest.fixture(scope="module")
def metricas_escasez():
    """
    Escenario artificial de desabastecimiento, solo para ejercitar el contador de
    paradas. Stock inicial minimo, lote chico y lead time largo frente al consumo.
    La estacion sigue siendo estable (lambda < mu) para que el modelo M/M/1 aplique.
    """
    sim = FabricaSimulation(
        lambda_ordenes_hora=20.0,
        media_ensamblaje_min=1.0,     # mu = 60 laptops/h, sistema estable
        stock_inicial=3,
        umbral_critico=1,
        lote_q=5,
        lead_time_min=60.0,           # el proveedor tarda mucho mas que el consumo
        semilla=2026,
    )
    return sim.ejecutar(6.0), sim


def test_escenario_artificial_detiene_la_linea(metricas_escasez):
    metricas, _ = metricas_escasez
    assert metricas["paradas_por_falta_stock"] >= 1
    assert metricas["ordenes_retrasadas_por_stock"] >= 1
    assert metricas["tiempo_linea_detenida_min"] > 0.0
    assert metricas["stock_minimo"] == 0


def test_escenario_artificial_baja_la_eficiencia(metricas_escasez):
    metricas, _ = metricas_escasez
    assert 0.0 <= metricas["eficiencia_reabastecimiento"] < 1.0
    # Coherencia de la definicion: 1 - tiempo_detenido / tiempo_total
    esperado = 1.0 - (metricas["tiempo_linea_detenida_min"] * 60.0) / metricas["tiempo_simulado_s"]
    assert metricas["eficiencia_reabastecimiento"] == pytest.approx(esperado, abs=1e-9)


def test_escenario_artificial_traza_parada_y_reanudacion(metricas_escasez):
    _, sim = metricas_escasez
    paradas = [l for l in sim.tracer.lineas if "PARADA_LINEA" in l]
    reanudaciones = [l for l in sim.tracer.lineas if "REANUDACION_LINEA" in l]
    assert paradas, "no se trazo ninguna parada de linea"
    # Cada parada se reanuda, salvo a lo sumo la ultima si la corrida corto antes
    assert len(paradas) - len(reanudaciones) in (0, 1)


def test_la_linea_queda_consistente_al_cierre(metricas_escasez):
    metricas, sim = metricas_escasez
    assert sim.linea_detenida == metricas["linea_detenida"]
    assert metricas["unidades_consumidas"] <= metricas["unidades_recibidas"] + 3
