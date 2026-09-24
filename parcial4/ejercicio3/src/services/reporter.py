"""
Servicio de reportes — Ejercicio 3 (Cubrimiento de conjuntos)
Formatea el modelo, la solucion y la cobertura, y los guarda en outputs/.
"""

import os

from src.core.set_covering import SENTIDOS, ModeloCubrimiento, ResultadoCobertura


def formatear_modelo(m: ModeloCubrimiento, a) -> str:
    lineas = [
        "MODELO",
        "------",
        "xj = 1 si se construye una estacion en la ciudad j, 0 si no",
        f"Criterio de cobertura ({m.sentido}): {SENTIDOS[m.sentido]}, limite = {m.limite:g} min",
        "",
        "Min Z = " + " + ".join(f"x{j + 1}" for j in range(m.n)),
        "s.a.",
    ]
    for i in range(m.n):
        suma = " + ".join(f"x{j + 1}" for j in range(m.n) if a[i, j])
        lineas.append(f"  Ciudad {i + 1:>2}: {suma} >= 1")
    lineas.append("  xj en {0, 1}")
    return "\n".join(lineas)


def formatear_resultado(m: ModeloCubrimiento, res: ResultadoCobertura) -> str:
    a = res.cobertura
    nombres = ", ".join(str(j + 1) for j in res.estaciones)
    lineas = ["RESULTADO", "---------", f"Minimo de estaciones: {res.minimo}", f"Ubicacion: ciudades {nombres}", ""]
    lineas.append("Estacion -> ciudades que cubre")
    for j in res.estaciones:
        cubre = ", ".join(str(i + 1) for i in range(m.n) if a[i, j])
        lineas.append(f"  {j + 1:>2} -> {cubre}")
    lineas += ["", "Ciudad -> estacion asignada (la mas cercana ida + vuelta)"]
    for i in range(m.n):
        j = min((j for j in res.estaciones if a[i, j]), key=lambda j: m.tiempos[i, j] + m.tiempos[j, i])
        lineas.append(f"  {i + 1:>2} -> {j + 1:>2}  (ida {m.tiempos[i, j]:g} min, vuelta {m.tiempos[j, i]:g} min)")
    if res.optimos_alternativos:
        lineas += ["", f"Combinaciones optimas de {res.minimo} estaciones: {len(res.optimos_alternativos)}"]
        for c in res.optimos_alternativos:
            lineas.append("  {" + ", ".join(str(j + 1) for j in c) + "}")
    if res.minimo > 1:
        con_menos = m.existe_solucion_con(res.minimo - 1)
        lineas += ["", f"Con {res.minimo - 1} estaciones {'SI' if con_menos else 'NO'} se cubren todas las ciudades."]
    return "\n".join(lineas)


def generar_reporte(m: ModeloCubrimiento, res: ResultadoCobertura) -> str:
    partes = [
        "EJERCICIO 3 - UBICACION DE ESTACIONES (CUBRIMIENTO DE CONJUNTOS)\n" + "=" * 64,
        formatear_modelo(m, res.cobertura),
        formatear_resultado(m, res),
    ]
    return "\n\n".join(partes) + "\n"


def guardar_reporte(texto: str, carpeta: str, nombre: str = "reporte_ejercicio3.txt") -> str:
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)
    return ruta
