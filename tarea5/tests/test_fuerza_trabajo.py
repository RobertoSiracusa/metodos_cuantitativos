import pytest

from src.core.fuerza_trabajo import ModeloFuerzaTrabajoDP, PoliticaCostos
from src.services.reporter import formatear_resumen

DEMANDAS = [5, 7, 8, 4, 6]


@pytest.fixture
def modelo():
    politica = PoliticaCostos(
        costo_excedente_unitario=300.0,
        costo_fijo_contratacion=400.0,
        costo_variable_contratacion=200.0,
        costo_despido_unitario=0.0,
    )
    m = ModeloFuerzaTrabajoDP(requerimientos=DEMANDAS, politica=politica, fuerza_inicial=0)
    m.resolver()
    return m


# ---------------------------------------------------------------------------
# Rangos calculados (punto 3 de la adaptacion): deben reproducir los
# conjuntos de la guia de clase.
# ---------------------------------------------------------------------------

def test_rangos_calculados_reproducen_la_guia(modelo):
    assert modelo.etapas[1].alternativas == [5, 6, 7, 8]
    assert modelo.etapas[2].alternativas == [7, 8]
    assert modelo.etapas[3].alternativas == [8]
    assert modelo.etapas[4].alternativas == [4, 5, 6]
    assert modelo.etapas[5].alternativas == [6]

    assert modelo.etapas[1].estados_entrada == [0]
    assert modelo.etapas[2].estados_entrada == [5, 6, 7, 8]
    assert modelo.etapas[3].estados_entrada == [7, 8]
    assert modelo.etapas[4].estados_entrada == [8]
    assert modelo.etapas[5].estados_entrada == [4, 5, 6]


# ---------------------------------------------------------------------------
# Valores de f_i(x_{i-1}) verificados a mano.
# ---------------------------------------------------------------------------

def test_f5(modelo):
    e5 = modelo.etapas[5]
    assert e5.estados[4].costo_minimo == 800
    assert e5.estados[5].costo_minimo == 600
    assert e5.estados[6].costo_minimo == 0
    assert e5.estados[4].mejor_x_actual == 6
    assert e5.estados[5].mejor_x_actual == 6
    assert e5.estados[6].mejor_x_actual == 6


def test_f4(modelo):
    e4 = modelo.etapas[4]
    estado = e4.estados[8]
    assert estado.costo_minimo == 600
    assert estado.mejor_x_actual == 6
    costos_por_alternativa = {ev.x_actual: ev.costo_total for ev in estado.evaluaciones}
    assert costos_por_alternativa == {4: 800, 5: 900, 6: 600}


def test_f3(modelo):
    e3 = modelo.etapas[3]
    assert e3.estados[7].costo_minimo == 1200
    assert e3.estados[8].costo_minimo == 600
    assert e3.estados[7].mejor_x_actual == 8
    assert e3.estados[8].mejor_x_actual == 8


def test_f2(modelo):
    e2 = modelo.etapas[2]
    assert e2.estados[5].costo_minimo == 1900
    assert e2.estados[5].mejor_x_actual == 8
    assert e2.estados[6].costo_minimo == 1700
    assert e2.estados[6].mejor_x_actual == 8
    assert e2.estados[7].costo_minimo == 1200
    assert e2.estados[7].mejor_x_actual == 7
    assert e2.estados[8].costo_minimo == 900
    assert e2.estados[8].mejor_x_actual == 8


def test_f1(modelo):
    e1 = modelo.etapas[1]
    estado = e1.estados[0]
    assert estado.costo_minimo == 3300
    assert estado.mejor_x_actual == 5
    costos_por_alternativa = {ev.x_actual: ev.costo_total for ev in estado.evaluaciones}
    assert costos_por_alternativa == {5: 3300, 6: 3600, 7: 3600, 8: 3800}


def test_plan_optimo(modelo):
    plan = modelo.plan_optimo
    assert [p.fuerza_optima for p in plan] == [5, 8, 8, 6, 6]
    assert [p.costo_semana for p in plan] == [1400, 1300, 0, 600, 0]
    assert [p.costo_acumulado for p in plan] == [1400, 2700, 2700, 3300, 3300]
    assert plan[-1].costo_acumulado == 3300


# ---------------------------------------------------------------------------
# Casos chicos.
# ---------------------------------------------------------------------------

def test_caso_chico_una_semana():
    politica = PoliticaCostos(300.0, 400.0, 200.0, 0.0)
    m = ModeloFuerzaTrabajoDP(requerimientos=[3], politica=politica, fuerza_inicial=0)
    m.resolver()
    assert m.plan_optimo[-1].costo_acumulado == 1000


def test_caso_chico_dos_semanas():
    politica = PoliticaCostos(300.0, 400.0, 200.0, 0.0)
    m = ModeloFuerzaTrabajoDP(requerimientos=[2, 2], politica=politica, fuerza_inicial=0)
    m.resolver()
    assert m.plan_optimo[-1].costo_acumulado == 800


# ---------------------------------------------------------------------------
# Validaciones.
# ---------------------------------------------------------------------------

def test_demandas_vacias_lanza_valueerror():
    politica = PoliticaCostos()
    with pytest.raises(ValueError):
        ModeloFuerzaTrabajoDP(requerimientos=[], politica=politica, fuerza_inicial=0)


def test_demanda_negativa_lanza_valueerror():
    politica = PoliticaCostos()
    with pytest.raises(ValueError):
        ModeloFuerzaTrabajoDP(requerimientos=[5, -1, 8], politica=politica, fuerza_inicial=0)


def test_demanda_float_lanza_valueerror():
    politica = PoliticaCostos()
    with pytest.raises(ValueError):
        ModeloFuerzaTrabajoDP(requerimientos=[5, 1.5, 8], politica=politica, fuerza_inicial=0)


def test_demanda_bool_lanza_valueerror():
    politica = PoliticaCostos()
    with pytest.raises(ValueError):
        ModeloFuerzaTrabajoDP(requerimientos=[5, True, 8], politica=politica, fuerza_inicial=0)


def test_costo_negativo_lanza_valueerror():
    with pytest.raises(ValueError):
        PoliticaCostos(costo_excedente_unitario=-300.0)


def test_costo_bool_lanza_valueerror():
    with pytest.raises(ValueError):
        PoliticaCostos(costo_fijo_contratacion=True)


def test_fuerza_inicial_negativa_lanza_valueerror():
    politica = PoliticaCostos()
    with pytest.raises(ValueError):
        ModeloFuerzaTrabajoDP(requerimientos=DEMANDAS, politica=politica, fuerza_inicial=-1)


def test_fuerza_inicial_bool_lanza_valueerror():
    politica = PoliticaCostos()
    with pytest.raises(ValueError):
        ModeloFuerzaTrabajoDP(requerimientos=DEMANDAS, politica=politica, fuerza_inicial=True)


# ---------------------------------------------------------------------------
# Tabla resumen alineada: todas las filas (encabezado, separador y datos)
# deben tener el mismo largo.
# ---------------------------------------------------------------------------

def test_tabla_resumen_filas_mismo_largo(modelo):
    lineas = formatear_resumen(modelo).splitlines()
    largos = {len(l) for l in lineas}
    assert len(largos) == 1
