"""Tests de Validador y ErrorValidacion (P6)."""

import copy
import math

import pytest

from src.utils.config import Configuracion
from src.utils.validators import ErrorValidacion, Validador


def test_escenario_por_defecto_es_valido():
    configuracion = Configuracion.por_defecto()
    # si Configuracion.por_defecto() no lanzo, el escenario ya es valido; se revalida
    # explicitamente para dejar la intencion clara en el test.
    Validador.validar_escenario(configuracion.datos)


def test_escenario_con_dos_errores_junta_ambos_en_una_sola_excepcion():
    datos = copy.deepcopy(Configuracion.por_defecto().datos)

    # error 1: el primer enlace (GW->N1) ahora salta directo a agregacion
    datos["enlaces"][0]["destino"] = "A1"

    # error 2: un paquete de prueba con prioridad fuera de 1..10
    datos["paquetes_prueba"][0]["prioridad"] = 11

    with pytest.raises(ErrorValidacion) as exc_info:
        Validador.validar_escenario(datos)

    mensaje = str(exc_info.value)
    assert "A1" in mensaje
    assert "prioridad" in mensaje
    assert mensaje.count("\n") >= 1


def test_desde_archivo_con_json_invalido_lanza_error_validacion(tmp_path):
    archivo = tmp_path / "escenario_invalido.json"
    archivo.write_text("{ esto no es json valido ", encoding="utf-8")

    with pytest.raises(ErrorValidacion):
        Configuracion.desde_archivo(archivo)


def test_desde_archivo_inexistente_lanza_error_validacion(tmp_path):
    archivo = tmp_path / "no_existe.json"
    with pytest.raises(ErrorValidacion):
        Configuracion.desde_archivo(archivo)


class TestValidarRango:
    def test_rechaza_bool(self):
        with pytest.raises(ErrorValidacion):
            Validador.validar_rango("x", True, minimo=0, maximo=10)

    def test_rechaza_string_no_numerica(self):
        with pytest.raises(ErrorValidacion):
            Validador.validar_rango("x", "abc", minimo=0, maximo=10)

    def test_rechaza_nan(self):
        with pytest.raises(ErrorValidacion):
            Validador.validar_rango("x", math.nan, minimo=0, maximo=10)

    def test_rechaza_inf(self):
        with pytest.raises(ErrorValidacion):
            Validador.validar_rango("x", math.inf, minimo=0, maximo=10)

    def test_rechaza_none(self):
        with pytest.raises(ErrorValidacion):
            Validador.validar_rango("x", None, minimo=0, maximo=10)

    def test_acepta_valor_en_rango_y_convierte_a_entero(self):
        resultado = Validador.validar_rango("x", 5.0, minimo=0, maximo=10, entero=True)
        assert resultado == 5
        assert isinstance(resultado, int)

    def test_rechaza_fuera_de_rango(self):
        with pytest.raises(ErrorValidacion):
            Validador.validar_rango("x", 15, minimo=0, maximo=10)
