"""
Servicio de reportes — Ejercicio 4 (Problema de la mochila)
Formatea el modelo, la solucion optima, los optimos alternativos y la
comparacion con la heuristica voraz, y los guarda en outputs/.
"""

import os

from src.core.knapsack import ModeloMochila, SolucionMochila


def _n(v: float) -> str:
    return f"{v:g}"


def _objetos(s: SolucionMochila) -> str:
    return ", ".join(str(i + 1) for i in s.objetos) or "ninguno"


def formatear_modelo(m: ModeloMochila) -> str:
    lineas = [
        "MODELO",
        "------",
        "xi = 1 si el objeto i entra en la mochila, 0 si no",
        "Max Z = " + " + ".join(f"{_n(v)}x{i + 1}" for i, v in enumerate(m.valores)),
        "s.a.",
        "  " + " + ".join(f"{w}x{i + 1}" for i, w in enumerate(m.pesos)) + f" <= {m.capacidad}",
        "  xi en {0, 1}",
        "",
        "Objeto  Peso  Valor  Valor/kg",
    ]
    for i in range(m.n):
        lineas.append(f"  {i + 1:>4}  {m.pesos[i]:>4}  {_n(m.valores[i]):>5}  {m.valores[i] / m.pesos[i]:>8.2f}")
    return "\n".join(lineas)


def formatear_resultado(m: ModeloMochila, dp: SolucionMochila, ml: SolucionMochila, voraz: SolucionMochila) -> str:
    x = ["1" if i in dp.objetos else "0" for i in range(m.n)]
    lineas = [
        "RESULTADO",
        "---------",
        f"Programacion dinamica: objetos {_objetos(dp)} | peso {_n(dp.peso)} kg | valor ${_n(dp.valor)}",
        "  x = (" + ", ".join(x) + ")",
        f"Verificacion milp:     objetos {_objetos(ml)} | peso {_n(ml.peso)} kg | valor ${_n(ml.valor)}",
        f"Coinciden en valor: {'SI' if abs(dp.valor - ml.valor) < 1e-9 else 'NO'}",
    ]
    alternativos = m.optimos_alternativos(dp.valor)
    if alternativos:
        lineas += ["", f"Combinaciones que alcanzan ${_n(dp.valor)}: {len(alternativos)}"]
        for s in alternativos:
            libre = m.capacidad - s.peso
            lineas.append(f"  objetos {_objetos(s):<10} peso {_n(s.peso)} kg (libres {_n(libre)} kg)")
        lineas.append(f"Recomendada (mismo valor, menor peso): objetos {_objetos(alternativos[0])}")
    lineas += [
        "",
        f"Heuristica voraz (mayor valor/kg): objetos {_objetos(voraz)} | peso {_n(voraz.peso)} kg | valor ${_n(voraz.valor)}",
        f"Diferencia contra el optimo: ${_n(dp.valor - voraz.valor)}",
    ]
    return "\n".join(lineas)


def generar_reporte(m, dp, ml, voraz) -> str:
    partes = [
        "EJERCICIO 4 - PROBLEMA DE LA MOCHILA\n" + "=" * 36,
        formatear_modelo(m),
        formatear_resultado(m, dp, ml, voraz),
    ]
    return "\n\n".join(partes) + "\n"


def guardar_reporte(texto: str, carpeta: str, nombre: str = "reporte_ejercicio4.txt") -> str:
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)
    return ruta
