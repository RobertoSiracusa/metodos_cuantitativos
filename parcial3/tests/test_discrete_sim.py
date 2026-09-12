"""
Pruebas del motor de eventos discretos del Problema 1.

Verifica reproducibilidad con semilla fija, la Ley de Little con tolerancia amplia
(la corrida es estocastica), la ausencia de metricas negativas y el contrato que
la capa grafica va a consumir.
"""

import pytest

from src.core.factory_entities import Orden
from src.simulation.discrete_sim import FabricaSimulation


# ----------------------------------------------------------------------
# Reproducibilidad
# ----------------------------------------------------------------------

def test_corrida_reproducible_con_semilla_fija():
    a = FabricaSimulation(semilla=1234).ejecutar(4.0)
    b = FabricaSimulation(semilla=1234).ejecutar(4.0)
    assert a["ordenes_generadas"] == b["ordenes_generadas"]
    assert a["ordenes_completadas"] == b["ordenes_completadas"]
    assert a["wq_promedio_min"] == pytest.approx(b["wq_promedio_min"], abs=1e-12)
    assert a["l_promedio"] == pytest.approx(b["l_promedio"], abs=1e-12)


def test_semillas_distintas_dan_corridas_distintas():
    a = FabricaSimulation(semilla=1).ejecutar(4.0)
    b = FabricaSimulation(semilla=999).ejecutar(4.0)
    assert a["ordenes_generadas"] != b["ordenes_generadas"]


# ----------------------------------------------------------------------
# Coherencia de las metricas
# ----------------------------------------------------------------------

def test_ninguna_metrica_numerica_es_negativa(metricas_p1):
    for clave, valor in metricas_p1.items():
        if isinstance(valor, bool) or valor is None:
            continue
        if isinstance(valor, (int, float)):
            assert valor >= 0, f"metrica negativa: {clave} = {valor}"


def test_flujo_de_ordenes_es_consistente(metricas_p1):
    assert metricas_p1["ordenes_generadas"] > 0
    assert metricas_p1["ordenes_completadas"] > 0
    assert metricas_p1["ordenes_completadas"] <= metricas_p1["ordenes_generadas"]
    pendientes = metricas_p1["ordenes_generadas"] - metricas_p1["ordenes_completadas"]
    assert pendientes == metricas_p1["ordenes_en_sistema"]


def test_duracion_simulada_es_la_pedida(metricas_p1):
    assert metricas_p1["tiempo_simulado_horas"] == pytest.approx(8.0, abs=1e-9)
    assert metricas_p1["tiempo_simulado_s"] == pytest.approx(28800.0, abs=1e-6)


def test_ley_de_little(metricas_p1):
    """
    L debe aproximar lambda_efectivo * W. Es una corrida estocastica de 8 h con
    unas 80 ordenes, asi que la tolerancia es amplia a proposito: se pide que el
    numero no sea absurdo, no igualdad.
    """
    completadas = metricas_p1["ordenes_completadas"]
    horas = metricas_p1["tiempo_simulado_horas"]
    lambda_efectivo = completadas / horas
    w_horas = metricas_p1["w_promedio_horas"]
    little = lambda_efectivo * w_horas
    assert metricas_p1["l_promedio"] == pytest.approx(little, rel=0.35)


def test_little_para_la_cola(metricas_p1):
    """Lq ~ lambda_efectivo * Wq, con la misma tolerancia amplia."""
    lambda_efectivo = metricas_p1["ordenes_completadas"] / metricas_p1["tiempo_simulado_horas"]
    little_q = lambda_efectivo * metricas_p1["wq_promedio_horas"]
    assert metricas_p1["lq_promedio"] == pytest.approx(little_q, rel=0.40)


def test_wq_simulado_del_orden_del_teorico(metricas_p1):
    """El Wq simulado debe quedar en el orden de los 25 min teoricos."""
    assert metricas_p1["teorico_wq_min"] == pytest.approx(25.0, abs=1e-3)
    assert 10.0 < metricas_p1["wq_promedio_min"] < 50.0


def test_w_mayor_que_wq(metricas_p1):
    """El tiempo en el sistema incluye la espera mas el servicio."""
    assert metricas_p1["w_promedio_min"] > metricas_p1["wq_promedio_min"]
    assert metricas_p1["l_promedio"] >= metricas_p1["lq_promedio"]


def test_utilizacion_cercana_a_rho(metricas_p1):
    """La ocupacion observada de la estacion debe rondar rho = 0.833."""
    assert metricas_p1["utilizacion_estacion"] == pytest.approx(
        metricas_p1["teorico_rho"], abs=0.15
    )


def test_balance_de_inventario(metricas_p1):
    """Stock final = inicial + recibidas - consumidas."""
    esperado = (
        metricas_p1["stock_inicial"]
        + metricas_p1["unidades_recibidas"]
        - metricas_p1["unidades_consumidas"]
    )
    assert metricas_p1["stock_actual"] == esperado


def test_las_dos_lecturas_del_despacho_de_lote(metricas_p1):
    """El reporte debe traer las dos metricas etiquetadas, no una sola."""
    assert "ciclo_reposicion_promedio_min" in metricas_p1
    assert "despacho_lote_promedio_min" in metricas_p1
    assert metricas_p1["lotes_produccion_observados"] >= 1
    assert metricas_p1["despacho_lote_promedio_min"] > 0


# ----------------------------------------------------------------------
# Contrato consumido por la capa grafica
# ----------------------------------------------------------------------

def test_contrato_de_la_gui(sim_fabrica_corta):
    sim = sim_fabrica_corta
    assert sim.tiempo_actual == 0.0
    assert isinstance(sim.ordenes_en_cola, list)
    assert hasattr(sim.estacion, "ocupada")
    assert hasattr(sim.estacion, "orden_actual")
    assert hasattr(sim.inventario, "nivel")
    assert hasattr(sim.inventario, "capacidad_lote")
    assert hasattr(sim.inventario, "en_reposicion")
    assert sim.linea_detenida is False


def test_step_avanza_el_reloj_en_segundos(sim_fabrica_corta):
    sim = sim_fabrica_corta
    sim.step(600.0)
    assert sim.tiempo_actual == pytest.approx(600.0)
    sim.step(1800.0)
    assert sim.tiempo_actual == pytest.approx(1800.0)


def test_step_no_retrocede(sim_fabrica_corta):
    sim = sim_fabrica_corta
    sim.step(1000.0)
    sim.step(500.0)
    assert sim.tiempo_actual == pytest.approx(1000.0)


def test_obtener_metricas_funciona_a_mitad_de_corrida(sim_fabrica_corta):
    sim = sim_fabrica_corta
    sim.step(3600.0)
    parciales = sim.obtener_metricas()
    assert parciales["tiempo_simulado_horas"] == pytest.approx(1.0)
    assert parciales["ordenes_generadas"] >= 0
    sim.step(7200.0)
    finales = sim.obtener_metricas()
    assert finales["ordenes_generadas"] >= parciales["ordenes_generadas"]


def test_la_cola_y_la_estacion_son_coherentes(sim_fabrica_corta):
    sim = sim_fabrica_corta
    sim.step(7200.0)
    en_sistema = len(sim.ordenes_en_cola) + (1 if sim.estacion.ocupada else 0)
    assert sim.obtener_metricas()["ordenes_en_sistema"] == en_sistema
    if sim.estacion.ocupada:
        assert isinstance(sim.estacion.orden_actual, Orden)
    else:
        assert sim.estacion.orden_actual is None


def test_la_traza_registra_los_eventos_esperados():
    sim = FabricaSimulation(semilla=2026)
    sim.ejecutar(8.0)
    texto = "\n".join(sim.tracer.lineas)
    for evento in (
        "INICIO_SIMULACION",
        "LLEGADA_ORDEN",
        "INICIO_ENSAMBLAJE",
        "FIN_ENSAMBLAJE",
        "DISPARO_REPOSICION",
        "RECEPCION_LOTE",
        "FIN_SIMULACION",
    ):
        assert evento in texto, f"falta el evento {evento} en la traza"


def test_los_eventos_de_la_traza_estan_en_orden_cronologico():
    sim = FabricaSimulation(semilla=7)
    sim.ejecutar(4.0)
    marcas = [l[1:14] for l in sim.tracer.lineas]
    assert marcas == sorted(marcas), "la traza no esta ordenada en el tiempo"


def test_parametros_invalidos_se_rechazan():
    from src.utils.validators import ValidacionError

    with pytest.raises(ValidacionError):
        FabricaSimulation(lambda_ordenes_hora=0.0)
    with pytest.raises(ValidacionError):
        FabricaSimulation(media_ensamblaje_min=-5.0)
    with pytest.raises(ValidacionError):
        FabricaSimulation(lead_time_min=0.0)
