"""
Validadores de los datos introducidos por el usuario y de los parametros cargados.

Regla del modulo: las funciones son puras y lanzan ValidacionError con un mensaje
accionable. Nunca imprimen ni piden datos por teclado. La capa de interfaz
(main.py) atrapa ValidacionError y reintenta, de modo que el usuario nunca ve un
traceback por una entrada invalida.
"""

from typing import Any, Iterable, Optional

from src.utils.config import HORAS_MAXIMO, HORAS_MINIMO


class ValidacionError(ValueError):
    """Entrada del usuario o parametro de configuracion fuera de contrato."""


def validar_horas(valor: Any) -> float:
    """
    Valida el periodo de simulacion expresado en horas.

    Acepta int, float o una cadena con el numero (coma o punto decimal).
    Rechaza None, cadena vacia, texto no numerico, cero, negativos, NaN,
    infinito y valores fuera del rango [HORAS_MINIMO, HORAS_MAXIMO].
    """
    if valor is None:
        raise ValidacionError("La duracion no puede estar vacia. Indique un numero de horas.")

    if isinstance(valor, bool):
        # bool es subclase de int en Python; aceptarlo seria un bug silencioso.
        raise ValidacionError(f"Duracion invalida: {valor!r}. Indique un numero de horas.")

    if isinstance(valor, str):
        texto = valor.strip().replace(",", ".")
        if not texto:
            raise ValidacionError("La duracion no puede estar vacia. Indique un numero de horas.")
    else:
        texto = valor

    try:
        horas = float(texto)
    except (TypeError, ValueError) as exc:
        raise ValidacionError(
            f"Duracion invalida: {valor!r}. Se esperaba un numero de horas, por ejemplo 8 o 8.5."
        ) from exc

    if horas != horas or horas in (float("inf"), float("-inf")):
        raise ValidacionError(f"Duracion invalida: {valor!r}. No se admiten NaN ni infinito.")

    if horas <= 0:
        raise ValidacionError(f"La duracion debe ser mayor a 0 horas. Recibido: {horas}.")

    if horas < HORAS_MINIMO:
        raise ValidacionError(
            f"La duracion minima admitida es {HORAS_MINIMO} horas. Recibido: {horas}."
        )

    if horas > HORAS_MAXIMO:
        raise ValidacionError(
            f"La duracion maxima admitida es {HORAS_MAXIMO} horas. Recibido: {horas}."
        )

    return horas


def parsear_horas_entrada(texto: Optional[str], defecto: float) -> float:
    """
    Interpreta lo que el usuario tecleo en el prompt de duracion.

    Un Enter vacio (cadena vacia o solo espacios) toma el valor por defecto.
    Cualquier otra entrada pasa por validar_horas.
    """
    if texto is None or not texto.strip():
        return validar_horas(defecto)
    return validar_horas(texto)


def validar_opcion_menu(texto: Optional[str], validas: Iterable[str]) -> str:
    """Valida que la opcion tecleada pertenezca al conjunto de opciones del menu."""
    opciones = [str(o) for o in validas]
    if texto is None:
        raise ValidacionError(f"Opcion vacia. Opciones validas: {', '.join(opciones)}.")
    limpio = texto.strip()
    if limpio not in opciones:
        raise ValidacionError(
            f"Opcion invalida: {texto!r}. Opciones validas: {', '.join(opciones)}."
        )
    return limpio


def validar_tasa(valor: Any, nombre: str = "Tasa") -> float:
    """Valida que una tasa (lambda o mu) sea un numero finito estrictamente positivo."""
    try:
        val = float(valor)
    except (TypeError, ValueError) as exc:
        raise ValidacionError(f"{nombre} debe ser numerica. Recibido: {valor!r}.") from exc
    # NaN e infinito pasan el float() pero envenenan cualquier formula posterior
    # sin lanzar nada: hay que atajarlos aca.
    if val != val or val in (float("inf"), float("-inf")):
        raise ValidacionError(f"{nombre} debe ser un numero finito. Recibido: {valor!r}.")
    if val <= 0:
        raise ValidacionError(f"{nombre} debe ser mayor a 0. Recibido: {val}.")
    return val


def _a_entero(valor: Any, nombre: str) -> int:
    """
    Convierte a entero atajando tambien OverflowError.

    int(float('inf')) lanza OverflowError, que NO es ValueError: sin este except
    el infinito se escapaba como traceback crudo hasta el usuario.
    """
    try:
        return int(valor)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValidacionError(f"{nombre} debe ser un entero. Recibido: {valor!r}.") from exc


def validar_entero_positivo(valor: Any, nombre: str = "Valor") -> int:
    """Valida que un parametro entero sea mayor o igual a 1."""
    val = _a_entero(valor, nombre)
    if val < 1:
        raise ValidacionError(f"{nombre} debe ser al menos 1. Recibido: {val}.")
    return val


def validar_entero_no_negativo(valor: Any, nombre: str = "Valor") -> int:
    """Valida que un parametro entero sea mayor o igual a 0."""
    val = _a_entero(valor, nombre)
    if val < 0:
        raise ValidacionError(f"{nombre} no puede ser negativo. Recibido: {val}.")
    return val


def validar_politica_inventario(umbral_s: int, lote_q: int, stock_inicial: int) -> None:
    """Valida la consistencia de la politica de inventario (s, Q)."""
    validar_entero_no_negativo(umbral_s, "Umbral critico s")
    validar_entero_positivo(lote_q, "Lote de reposicion Q")
    validar_entero_no_negativo(stock_inicial, "Stock inicial")
    if lote_q <= umbral_s:
        raise ValidacionError(
            f"El lote Q ({lote_q}) debe superar el umbral s ({umbral_s}); si no, "
            "una reposicion no alcanza para salir del umbral y el sistema oscila."
        )


def validar_rango_trafico(minimo: float, maximo: float) -> None:
    """Valida el rango de truncamiento de la distribucion de trafico."""
    if minimo >= maximo:
        raise ValidacionError(
            f"El limite inferior del trafico ({minimo}) debe ser menor al superior ({maximo})."
        )
    if minimo < 0:
        raise ValidacionError(f"El trafico no puede ser negativo. Recibido: {minimo}.")


def validar_sistema_estable(lamb: float, mu: float, servidores: int = 1) -> None:
    """
    Verifica la condicion de estabilidad de la cola: lambda < servidores * mu.

    Sin esta guarda, un M/M/1 con rho >= 1 da formulas cerradas negativas o
    infinitas y el reporte saldria con numeros sin sentido.
    """
    validar_tasa(lamb, "Tasa de llegada lambda")
    validar_tasa(mu, "Tasa de servicio mu")
    c = validar_entero_positivo(servidores, "Numero de servidores")
    if lamb >= c * mu:
        raise ValidacionError(
            f"Sistema inestable: lambda ({lamb}) debe ser menor que c*mu ({c * mu}). "
            "Con rho >= 1 la cola crece sin limite y las formulas cerradas no aplican."
        )


def _selfcheck() -> None:
    """Comprobaciones minimas del modulo, ejecutables sin pytest."""
    assert validar_horas(8) == 8.0
    assert validar_horas("8,5") == 8.5
    assert parsear_horas_entrada("", 8.0) == 8.0
    assert parsear_horas_entrada("   ", 8.0) == 8.0
    assert parsear_horas_entrada(None, 8.0) == 8.0
    assert parsear_horas_entrada("3", 8.0) == 3.0

    for invalido in (None, "", "   ", "ocho", -1, 0, "-4", "0", True):
        try:
            validar_horas(invalido)
        except ValidacionError:
            pass
        else:
            raise AssertionError(f"validar_horas acepto un valor invalido: {invalido!r}")

    # int(inf) lanza OverflowError, que no es ValueError: debe quedar convertido
    for invalido in (float("inf"), float("nan"), "x", None, 0, -1):
        try:
            validar_entero_positivo(invalido, "Servidores")
        except ValidacionError:
            pass
        else:
            raise AssertionError(f"validar_entero_positivo acepto {invalido!r}")

    for invalido in (float("inf"), float("nan"), 0, -1):
        try:
            validar_tasa(invalido, "lambda")
        except ValidacionError:
            pass
        else:
            raise AssertionError(f"validar_tasa acepto {invalido!r}")

    assert validar_opcion_menu(" 1 ", ["0", "1", "2"]) == "1"
    try:
        validar_opcion_menu("9", ["0", "1"])
    except ValidacionError:
        pass
    else:
        raise AssertionError("validar_opcion_menu acepto una opcion fuera del menu")

    validar_politica_inventario(10, 50, 50)
    try:
        validar_politica_inventario(50, 10, 50)
    except ValidacionError:
        pass
    else:
        raise AssertionError("validar_politica_inventario acepto Q <= s")

    validar_sistema_estable(10.0, 12.0, 1)
    try:
        validar_sistema_estable(12.0, 10.0, 1)
    except ValidacionError:
        pass
    else:
        raise AssertionError("validar_sistema_estable acepto un sistema inestable")

    print("selfcheck validators: OK")


if __name__ == "__main__":
    _selfcheck()
