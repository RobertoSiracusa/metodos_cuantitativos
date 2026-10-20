"""Tests de RutaMasCorta (R1) sobre el escenario por defecto, con valores calculados a mano."""

import math

import pytest

from src.core.network_entities import Paquete
from src.core.programacion_dinamica.ruta_mas_corta import RutaMasCorta
from src.utils.config import Configuracion
from src.utils.validators import ErrorValidacion


@pytest.fixture
def red():
    return Configuracion.por_defecto().construir_red()


def test_ruta_basica_gw_a_t1(red):
    resultado = RutaMasCorta(red).resolver("GW", "T1")
    assert resultado.camino == ("GW", "N1", "A2", "T1")
    assert resultado.costo == pytest.approx(7.0)
    assert resultado.existe


def test_ruta_con_congestion_en_a2_t1(red):
    enlace = red.enlace("A2", "T1")
    for i in range(5):
        enlace.entrar(Paquete(id=f"CONG{i}", requerimiento=1, prioridad=1, destino_cluster="C1"))

    assert enlace.ocupacion == pytest.approx(0.5)
    assert enlace.costo_actual() == pytest.approx(6.0)

    resultado = RutaMasCorta(red).resolver("GW", "T1")
    assert resultado.camino == ("GW", "N1", "A1", "T1")
    assert resultado.costo == pytest.approx(8.0)


def test_ruta_con_falla_de_n1(red):
    red.nodo("N1").fallar()
    resultado = RutaMasCorta(red).resolver("GW", "T1")
    assert resultado.camino == ("GW", "N2", "A2", "T1")
    assert resultado.costo == pytest.approx(9.0)


def test_ruta_sin_solucion_cuando_caen_a1_y_a2(red):
    red.nodo("A1").fallar()
    red.nodo("A2").fallar()
    resultado = RutaMasCorta(red).resolver("GW", "T1")
    assert resultado.existe is False
    assert resultado.camino == ()
    assert math.isinf(resultado.costo)


def test_origen_en_etapa_no_anterior_a_destino_lanza_error(red):
    modelo = RutaMasCorta(red)
    with pytest.raises(ErrorValidacion):
        modelo.resolver("T1", "GW")
    with pytest.raises(ErrorValidacion):
        modelo.resolver("N1", "N2")


def test_id_inexistente_lanza_error(red):
    modelo = RutaMasCorta(red)
    with pytest.raises(ErrorValidacion):
        modelo.resolver("GW", "NO_EXISTE")
    with pytest.raises(ErrorValidacion):
        modelo.resolver("NO_EXISTE", "T1")


def test_tabla_none_antes_de_resolver_y_es_copia(red):
    modelo = RutaMasCorta(red)
    assert modelo.tabla is None

    modelo.resolver("GW", "T1")
    tabla = modelo.tabla
    assert tabla is not None

    etapa_0 = next(iter(tabla))
    nodo_cualquiera = next(iter(tabla[etapa_0]))
    tabla[etapa_0][nodo_cualquiera] = (999.0, "MODIFICADO")

    tabla_de_nuevo = modelo.tabla
    assert tabla_de_nuevo[etapa_0][nodo_cualquiera] != (999.0, "MODIFICADO")
