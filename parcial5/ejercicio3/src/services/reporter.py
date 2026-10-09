"""
Servicio de reportes — Ejercicio 3 (Problema de volumen de carga)
Formatea el modelo, las tablas de cada etapa, la tabla resumen, la
reconstruccion de la solucion, el resultado, la enumeracion completa y la
comparacion con la heuristica voraz, y los guarda en outputs/.
"""

import os

from src.core.volumen_carga import Combinacion, SolucionCarga, VolumenCarga


def _n(v: float) -> str:
    return f"{v:g}"


def _g(v) -> str:
    return "-" if v is None else _n(v)


def _productos(m: VolumenCarga, s) -> str:
    return ", ".join(m.nombres[i] for i in s.productos) or "ninguno"


def formatear_modelo(m: VolumenCarga) -> str:
    lineas = [
        "MODELO",
        "------",
        "mi = 1 si el producto i entra en la carga, 0 si no",
        "Max Z = " + " + ".join(f"{_n(p)}m{i + 1}" for i, p in enumerate(m.precios)),
        "s.a.",
        "  " + " + ".join(f"{w}m{i + 1}" for i, w in enumerate(m.pesos)) + f" <= {m.capacidad}",
        "  mi en {0, 1}",
        "",
        "Producto                      Peso  Precio  Precio/kg",
    ]
    for i in range(m.n):
        etiqueta = f"{i + 1} {m.nombres[i]}"
        lineas.append(
            f"  {etiqueta:<28} {m.pesos[i]:>4}  {_n(m.precios[i]):>6}  {m.precios[i] / m.pesos[i]:>8.2f}"
        )
    return "\n".join(lineas)


def formatear_etapas(m: VolumenCarga, etapas) -> str:
    bloques = ["TABLAS POR ETAPA", "-----------------"]
    for i, filas in enumerate(etapas):
        nombre, peso, precio = m.nombres[i], m.pesos[i], m.precios[i]
        bloques.append("")
        bloques.append(f"Etapa {i + 1} - {nombre} (peso {peso} kg, precio ${_n(precio)})")
        bloques.append(f"f_{i + 1}(y) = max{{ f_{i}(y) , {_n(precio)} + f_{i}(y - {peso}) }}")
        bloques.append("")
        bloques.append("   y  m=0    m=1    f_i(y)  m_i*")
        for fila in filas:
            bloques.append(
                f"  {fila.y:>2}  {_n(fila.sin_producto):>5}  {_g(fila.con_producto):>5}  "
                f"{_n(fila.f):>6}  {fila.decision:>4}"
            )
    return "\n".join(bloques)


def formatear_resumen(m: VolumenCarga, etapas) -> str:
    W = m.capacidad
    filas_f = [[0.0] * (W + 1)] + [[fila.f for fila in e] for e in etapas]
    lineas = ["TABLA RESUMEN", "-------------"]
    lineas.append("        " + "".join(f"{y:>6}" for y in range(W + 1)) + "   <- y")
    for i, fila in enumerate(filas_f):
        lineas.append(f"f_{i:<4}  " + "".join(f"{_n(v):>6}" for v in fila))
    return "\n".join(lineas)


def formatear_reconstruccion(m: VolumenCarga, etapas) -> str:
    lineas = ["RECONSTRUCCION", "--------------"]
    y = m.capacidad
    for i in range(m.n - 1, -1, -1):
        nombre, peso, precio = m.nombres[i], m.pesos[i], m.precios[i]
        fila = etapas[i][y]
        if fila.decision == 1:
            lineas.append(
                f"Etapa {i + 1} ({nombre}): f_{i + 1}({y}) = {_n(precio)} + f_{i}({y - peso}) = "
                f"{_n(fila.f)} -> m{i + 1} = 1, y = {y - peso}"
            )
            y -= peso
        else:
            lineas.append(
                f"Etapa {i + 1} ({nombre}): f_{i + 1}({y}) = f_{i}({y}) = "
                f"{_n(fila.f)} -> m{i + 1} = 0, y = {y}"
            )
    return "\n".join(lineas)


def formatear_resultado(m: VolumenCarga, solucion: SolucionCarga, ml: SolucionCarga, alternativos) -> str:
    x = ["1" if i in solucion.productos else "0" for i in range(m.n)]
    lineas = [
        "RESULTADO",
        "---------",
        f"Programacion dinamica: productos {_productos(m, solucion)}",
        f"  peso {_n(solucion.peso)} kg | precio ${_n(solucion.valor)} | libre {_n(solucion.libre)} kg",
        "  m = (" + ", ".join(x) + ")",
        f"Verificacion milp:     productos {_productos(m, ml)} | peso {_n(ml.peso)} kg | precio ${_n(ml.valor)}",
        f"Coinciden en valor: {'SI' if abs(solucion.valor - ml.valor) < 1e-9 else 'NO'}",
    ]
    if alternativos:
        lineas += ["", f"Combinaciones optimas (precio ${_n(solucion.valor)}): {len(alternativos)}"]
        for c in alternativos:
            libre = m.capacidad - c.peso
            lineas.append(f"  productos {_productos(m, c):<45} peso {_n(c.peso)} kg (libres {_n(libre)} kg)")
    return "\n".join(lineas)


def formatear_enumeracion(m: VolumenCarga, enumeracion) -> str:
    lineas = ["ENUMERACION COMPLETA", "---------------------"]
    ordenada = sorted(enumeracion, key=lambda c: (-c.valor, c.peso))
    ancho = max(len(_productos(m, c)) for c in ordenada)
    for c in ordenada:
        estado = "FACTIBLE" if c.factible else "EXCEDE"
        lineas.append(
            f"  {_productos(m, c):<{ancho}}  peso {_n(c.peso):>3} kg  precio ${_n(c.valor):>4}  {estado}"
        )
    return "\n".join(lineas)


def formatear_comparacion_voraz(m: VolumenCarga, solucion: SolucionCarga, voraz: SolucionCarga) -> str:
    diferencia = solucion.valor - voraz.valor
    lineas = [
        "COMPARACION CON HEURISTICA VORAZ",
        "---------------------------------",
        f"Heuristica voraz (mayor precio/kg): productos {_productos(m, voraz)}",
        f"  peso {_n(voraz.peso)} kg | precio ${_n(voraz.valor)}",
        f"Diferencia contra el optimo: ${_n(diferencia)}",
    ]
    return "\n".join(lineas)


def generar_reporte(m, etapas, solucion, ml, voraz, enumeracion, alternativos) -> str:
    partes = [
        "EJERCICIO 3 - PROBLEMA DE VOLUMEN DE CARGA\n" + "=" * 43,
        formatear_modelo(m),
        formatear_etapas(m, etapas),
        formatear_resumen(m, etapas),
        formatear_reconstruccion(m, etapas),
        formatear_resultado(m, solucion, ml, alternativos),
        formatear_enumeracion(m, enumeracion),
        formatear_comparacion_voraz(m, solucion, voraz),
    ]
    return "\n\n".join(partes) + "\n"


def guardar_reporte(texto: str, carpeta: str, nombre: str = "reporte_ejercicio3.txt") -> str:
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)
    return ruta
