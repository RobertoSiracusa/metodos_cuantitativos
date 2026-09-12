"""
Pruebas de los validadores de entrada del usuario.

El contrato es que toda entrada invalida produzca un ValidacionError controlado
con mensaje accionable, NUNCA un traceback crudo que llegue al usuario. La capa
de interfaz atrapa esa excepcion y reintenta.
"""

import pytest

from src.utils.config import HORAS_DEFECTO, HORAS_MAXIMO, HORAS_MINIMO
from src.utils.validators import (
    ValidacionError,
    parsear_horas_entrada,
    validar_entero_no_negativo,
    validar_entero_positivo,
    validar_horas,
    validar_opcion_menu,
    validar_politica_inventario,
    validar_rango_trafico,
    validar_sistema_estable,
    validar_tasa,
)


# ----------------------------------------------------------------------
# Duracion de la simulacion
# ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "entrada,esperado",
    [
        (8, 8.0),
        (8.5, 8.5),
        ("8", 8.0),
        ("8.5", 8.5),
        ("8,5", 8.5),
        ("  12  ", 12.0),
        (0.5, 0.5),
        (HORAS_MAXIMO, HORAS_MAXIMO),
    ],
    ids=["int", "float", "str_int", "str_float", "coma_decimal", "espacios", "media_hora", "tope"],
)
def test_horas_validas(entrada, esperado):
    assert validar_horas(entrada) == pytest.approx(esperado)


@pytest.mark.parametrize(
    "entrada",
    [None, "", "   ", "ocho", "8 horas", "abc", -1, -0.5, 0, "0", "-4", [], {}, True, False],
    ids=[
        "None", "vacio", "espacios", "texto", "texto_mixto", "letras",
        "negativo_int", "negativo_float", "cero", "cero_str", "negativo_str",
        "lista", "dict", "True", "False",
    ],
)
def test_horas_invalidas_lanzan_validacion_error(entrada):
    """Todas se rechazan con ValidacionError, no con un traceback crudo."""
    with pytest.raises(ValidacionError):
        validar_horas(entrada)


def test_horas_invalidas_traen_mensaje_accionable():
    with pytest.raises(ValidacionError) as exc:
        validar_horas("ocho")
    assert "numero de horas" in str(exc.value)

    with pytest.raises(ValidacionError) as exc:
        validar_horas(-3)
    assert "mayor a 0" in str(exc.value)


def test_horas_fuera_de_rango():
    with pytest.raises(ValidacionError, match="minima"):
        validar_horas(HORAS_MINIMO / 2.0)
    with pytest.raises(ValidacionError, match="maxima"):
        validar_horas(HORAS_MAXIMO + 1.0)


@pytest.mark.parametrize("entrada", ["nan", "inf", "-inf"], ids=["nan", "inf", "menos_inf"])
def test_nan_e_infinito_se_rechazan(entrada):
    with pytest.raises(ValidacionError):
        validar_horas(entrada)


@pytest.mark.parametrize("vacio", [None, "", "   ", "\t", "\n"])
def test_enter_vacio_toma_el_valor_por_defecto(vacio):
    assert parsear_horas_entrada(vacio, HORAS_DEFECTO) == HORAS_DEFECTO


def test_entrada_no_vacia_se_valida():
    assert parsear_horas_entrada("3", HORAS_DEFECTO) == 3.0
    with pytest.raises(ValidacionError):
        parsear_horas_entrada("cero", HORAS_DEFECTO)


# ----------------------------------------------------------------------
# Opciones del menu
# ----------------------------------------------------------------------

@pytest.mark.parametrize("entrada", ["0", "1", "2", "3", "4", " 1 ", "\t2\n"])
def test_opciones_validas_del_menu(entrada):
    assert validar_opcion_menu(entrada, ["0", "1", "2", "3", "4"]) == entrada.strip()


@pytest.mark.parametrize("entrada", [None, "", "   ", "9", "a", "1.0", "01", "uno"])
def test_opciones_invalidas_del_menu(entrada):
    with pytest.raises(ValidacionError):
        validar_opcion_menu(entrada, ["0", "1", "2", "3", "4"])


def test_el_mensaje_del_menu_lista_las_opciones():
    with pytest.raises(ValidacionError) as exc:
        validar_opcion_menu("9", ["0", "1"])
    assert "0, 1" in str(exc.value)


# ----------------------------------------------------------------------
# Parametros del modelo
# ----------------------------------------------------------------------

@pytest.mark.parametrize("valor", [0, -1, -0.5, "x", None])
def test_tasas_invalidas(valor):
    with pytest.raises(ValidacionError):
        validar_tasa(valor, "lambda")


def test_tasa_valida():
    assert validar_tasa(10.0, "lambda") == 10.0
    assert validar_tasa("12", "mu") == 12.0


@pytest.mark.parametrize("valor", [0, -1, "x", None, 1.5e400])
def test_enteros_positivos_invalidos(valor):
    with pytest.raises(ValidacionError):
        validar_entero_positivo(valor, "Servidores")


def test_entero_no_negativo_acepta_cero():
    assert validar_entero_no_negativo(0, "Stock") == 0
    with pytest.raises(ValidacionError):
        validar_entero_no_negativo(-1, "Stock")


def test_politica_de_inventario_valida():
    validar_politica_inventario(10, 50, 50)


@pytest.mark.parametrize(
    "s,q,stock",
    [(-1, 50, 50), (10, 0, 50), (10, -5, 50), (50, 10, 50), (10, 10, 50), (10, 50, -1)],
    ids=["s_negativo", "q_cero", "q_negativo", "q_menor_que_s", "q_igual_a_s", "stock_negativo"],
)
def test_politica_de_inventario_invalida(s, q, stock):
    with pytest.raises(ValidacionError):
        validar_politica_inventario(s, q, stock)


def test_rango_de_trafico():
    validar_rango_trafico(1.0, 5.0)
    with pytest.raises(ValidacionError):
        validar_rango_trafico(5.0, 1.0)
    with pytest.raises(ValidacionError):
        validar_rango_trafico(3.0, 3.0)
    with pytest.raises(ValidacionError):
        validar_rango_trafico(-1.0, 5.0)


def test_estabilidad_del_sistema():
    validar_sistema_estable(10.0, 12.0, 1)
    validar_sistema_estable(20.0, 12.0, 2)
    with pytest.raises(ValidacionError, match="inestable"):
        validar_sistema_estable(12.0, 12.0, 1)
    with pytest.raises(ValidacionError, match="inestable"):
        validar_sistema_estable(15.0, 12.0, 1)


def test_validacion_error_es_un_value_error():
    """Permite atraparlo con except ValueError en codigo de terceros."""
    assert issubclass(ValidacionError, ValueError)
