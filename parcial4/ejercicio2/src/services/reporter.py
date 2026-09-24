"""
Servicio de reportes — Ejercicio 2 (Ramificacion y Acotamiento)
Formatea el modelo, los nodos y el arbol, y los guarda en outputs/.
"""

import os
from typing import List

from src.core.branch_and_bound import ModeloBranchAndBound, ResultadoBB


def _num(v: float) -> str:
    return f"{v:.0f}" if abs(v - round(v)) < 1e-9 else f"{v:.4f}".rstrip("0")


def formatear_modelo(m: ModeloBranchAndBound) -> str:
    def expr(coefs: List[float]) -> str:
        return " + ".join(f"{'' if a == 1 else _num(a)}x{i + 1}" for i, a in enumerate(coefs) if a != 0)

    lineas = ["MODELO", "------", f"Max Z = {expr(m.c)}", "s.a."]
    lineas += [f"  {expr(fila)} <= {_num(bi)}" for fila, bi in zip(m.A, m.b)]
    variables = ", ".join(f"x{i + 1}" for i in range(m.n))
    lineas.append(f"  {variables} >= 0 y enteras")
    return "\n".join(lineas)


def formatear_nodos(res: ResultadoBB) -> str:
    lineas = ["NODOS (en orden de exploracion)", "-------------------------------"]
    for nid in res.orden_exploracion:
        n = res.nodos[nid]
        if n.x is None:
            sol = "infactible"
        else:
            sol = "x = (" + ", ".join(_num(v) for v in n.x) + f")  Z = {_num(n.z)}"
        lineas.append(f"P{n.id:<2} [{n.restriccion}]  {sol}  -> {n.estado}")
    return "\n".join(lineas)


def formatear_arbol(res: ResultadoBB) -> str:
    lineas = ["ARBOL", "-----"]

    def dibujar(nid: int, prefijo: str, ultimo: bool, raiz: bool):
        n = res.nodos[nid]
        sol = "infactible" if n.x is None else "(" + ", ".join(_num(v) for v in n.x) + f") Z={_num(n.z)}"
        etiqueta = f"P{n.id} {sol}" if raiz else f"[{n.restriccion}] P{n.id} {sol}"
        marca = "" if raiz else ("`-- " if ultimo else "|-- ")
        lineas.append(f"{prefijo}{marca}{etiqueta}  {n.estado}")
        nuevo = prefijo if raiz else prefijo + ("    " if ultimo else "|   ")
        for k, h in enumerate(n.hijos):
            dibujar(h, nuevo, k == len(n.hijos) - 1, False)

    dibujar(0, "", True, True)
    return "\n".join(lineas)


def formatear_resultado(res: ResultadoBB) -> str:
    if res.x_optimo is None:
        return "RESULTADO\n---------\nEl problema no tiene solucion entera factible."
    xs = " ; ".join(f"x{i + 1} = {_num(v)}" for i, v in enumerate(res.x_optimo))
    return f"RESULTADO\n---------\n{xs} ; Z optimo = {_num(res.z_optimo)}"


def generar_reporte(m: ModeloBranchAndBound, res: ResultadoBB) -> str:
    partes = [
        "EJERCICIO 2 - RAMIFICACION Y ACOTAMIENTO\n" + "=" * 40,
        formatear_modelo(m),
        formatear_nodos(res),
        formatear_arbol(res),
        formatear_resultado(res),
    ]
    return "\n\n".join(partes) + "\n"


def guardar_reporte(texto: str, carpeta: str, nombre: str = "reporte_ejercicio2.txt") -> str:
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)
    return ruta
