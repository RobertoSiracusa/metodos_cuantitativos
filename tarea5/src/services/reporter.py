"""
Servicio de reportes - Tarea 5 (Modelo de tamano de la fuerza de trabajo)
Formatea, en texto, las tablas de cada etapa (semana) y el resumen de la
politica optima del modelo, y guarda el reporte completo en outputs/.
El modelo (src/core/fuerza_trabajo.py) no imprime ni escribe nada: solo
calcula.
"""

import os


def formatear_etapa(etapa) -> str:
    """
    Genera, para una etapa (semana), la tabla en texto con el detalle de
    cada alternativa evaluada en la celda exc+contr+futuro=total, y
    reproduce la estructura de la tabla de la clase teorica.
    """
    lineas = []
    lineas.append("=" * 80)
    lineas.append(
        f"  ETAPA {etapa.semana} (SEMANA {etapa.semana}) | Requerimiento minimo: b_{etapa.semana} = {etapa.b_requerido}"
    )
    lineas.append(f"  Alternativas evaluadas: x_{etapa.semana} in {etapa.alternativas}")
    lineas.append(
        f"  Ecuacion: f_{etapa.semana}(x_{etapa.semana - 1}) = min {{ C_1(x_{etapa.semana} - {etapa.b_requerido}) "
        f"+ C_2(x_{etapa.semana} - x_{etapa.semana - 1}) + f_{etapa.semana + 1}(x_{etapa.semana}) }}"
    )
    lineas.append("-" * 80)

    headers = [f"x_{etapa.semana}={alt}" for alt in etapa.alternativas]
    col_width = 24
    header_str = (
        f"{'x_' + str(etapa.semana - 1):^8} | "
        + " | ".join(f"{h:^{col_width}}" for h in headers)
        + f" | {'f_' + str(etapa.semana) + '(x)':^12} | {'x_' + str(etapa.semana) + '*':^8}"
    )
    lineas.append(header_str)
    lineas.append("-" * len(header_str))

    for x_prev in etapa.estados_entrada:
        estado = etapa.estados[x_prev]
        celdas = []
        for alt in etapa.alternativas:
            ev = next((e for e in estado.evaluaciones if e.x_actual == alt), None)
            if ev:
                # Detalle: Exceso + Transicion + Futuro = Total
                celda_texto = (
                    f"{int(ev.costo_excedente):>3}+{int(ev.costo_transicion):>4}"
                    f"+{int(ev.costo_futuro):>4}={int(ev.costo_total):>4}"
                )
            else:
                celda_texto = "-"
            celdas.append(f"{celda_texto:^{col_width}}")

        f_opt = f"${int(estado.costo_minimo)}"
        x_opt = f"{estado.mejor_x_actual}"
        fila_str = f"{x_prev:^8} | " + " | ".join(celdas) + f" | {f_opt:^12} | {x_opt:^8}"
        lineas.append(fila_str)

    lineas.append("-" * 80)
    lineas.append("  Leyenda celda: [C_excedente + C_contratacion + f_futuro = Costo_Total]\n")
    return "\n".join(lineas)


def formatear_resumen(modelo) -> str:
    """
    Tabla resumen de la politica optima, con columnas alineadas:
    - El ancho de "Decision tomada" se calcula a partir del largo real de
      las decisiones (y del encabezado), en vez de un ancho fijo que corta
      el texto mas largo o deja huecos de sobra.
    - Las columnas de costo usan formato "$N" alineado a la derecha, sin el
      espacio entre el "$" y el numero.
    """
    decisiones = [p.accion_decision for p in modelo.plan_optimo]
    ancho_decision = max([len("Decision tomada")] + [len(d) for d in decisiones])

    costos_sem = [f"${int(p.costo_semana)}" for p in modelo.plan_optimo]
    costos_acum = [f"${int(p.costo_acumulado)}" for p in modelo.plan_optimo]
    ancho_costo_sem = max([len("Costo Sem ($)")] + [len(c) for c in costos_sem])
    ancho_costo_acum = max([len("Costo Acum ($)")] + [len(c) for c in costos_acum])

    lineas = []
    encabezado = (
        f"{'Semana':^8} | {'Min Req':^9} | {'Personal Real':^15} | "
        f"{'Decision tomada':^{ancho_decision}} | {'Costo Sem ($)':^{ancho_costo_sem}} | "
        f"{'Costo Acum ($)':^{ancho_costo_acum}}"
    )
    lineas.append(encabezado)
    lineas.append("-" * len(encabezado))

    for p, c_sem, c_acum in zip(modelo.plan_optimo, costos_sem, costos_acum):
        lineas.append(
            f"{p.semana:^8} | {p.req_minimo:^9} | {p.fuerza_optima:^15} | "
            f"{p.accion_decision:<{ancho_decision}} | {c_sem:>{ancho_costo_sem}} | {c_acum:>{ancho_costo_acum}}"
        )
    return "\n".join(lineas)


def generar_reporte(modelo) -> str:
    """
    Genera el reporte completo: encabezado (universidad, materia y titulo),
    datos del problema, ecuacion de Bellman, tablas etapa por etapa (de la
    semana 5 a la 1) con el detalle exc+contr+futuro=total, resumen de la
    politica optima, costo total minimo y autores.
    """
    lineas = []
    lineas.append("=" * 80)
    lineas.append("UNIVERSIDAD JOSE ANTONIO PAEZ")
    lineas.append("FACULTAD DE INGENIERIA - ESCUELA DE INGENIERIA EN COMPUTACION")
    lineas.append("METODOS CUANTITATIVOS / INVESTIGACION DE OPERACIONES II")
    lineas.append("")
    lineas.append("TAREA 5 - MODELO DE TAMANO DE LA FUERZA DE TRABAJO")
    lineas.append("=" * 80)
    lineas.append("")

    lineas.append("1. DATOS DEL PROBLEMA:")
    lineas.append(f"   - Duracion del proyecto: {modelo.n_semanas} semanas.")
    lineas.append(f"   - Requerimientos minimos de personal: {modelo.requerimientos}")
    lineas.append(f"   - Fuerza laboral inicial: {modelo.fuerza_inicial} trabajadores.")
    lineas.append("   - Estructura de costos:")
    lineas.append(
        f"     * Costo por mano de obra excedente: ${int(modelo.politica.costo_excedente_unitario)} por trabajador/semana."
    )
    lineas.append(
        f"     * Costo de contratacion: ${int(modelo.politica.costo_fijo_contratacion)} (fijo) + "
        f"${int(modelo.politica.costo_variable_contratacion)} por trabajador."
    )
    lineas.append(f"     * Costo por despido: ${int(modelo.politica.costo_despido_unitario)}.")
    lineas.append("")
    lineas.append("2. ECUACION RECURSIVA DE BELLMAN (Recursividad hacia atras):")
    lineas.append("   f_i(x_{i-1}) = min { C_1(x_i - b_i) + C_2(x_i - x_{i-1}) + f_{i+1}(x_i) }")
    lineas.append("   con condicion de frontera: f_{n+1}(x_n) = 0")
    lineas.append("")
    lineas.append("=" * 80)
    lineas.append("              RESOLUCION PASO POR PASO (DE ETAPA 5 A ETAPA 1)")
    lineas.append("=" * 80)
    lineas.append("")

    for semana in range(modelo.n_semanas, 0, -1):
        lineas.append(formatear_etapa(modelo.etapas[semana]))

    resumen_texto = formatear_resumen(modelo)
    ancho_tabla = max(len(l) for l in resumen_texto.splitlines())

    lineas.append("=" * 80)
    lineas.append("                    RESUMEN DE LA POLITICA OPTIMA FINAL")
    lineas.append("=" * 80)
    lineas.append(resumen_texto)

    costo_total = modelo.plan_optimo[-1].costo_acumulado if modelo.plan_optimo else 0.0
    lineas.append("=" * ancho_tabla)
    lineas.append(f"  >>> COSTO TOTAL MINIMO DE MANO DE OBRA PARA EL PROYECTO: ${int(costo_total)} USD <<<")
    lineas.append("=" * 80)
    lineas.append("")
    lineas.append("Autores: Roberto Siracusa (C.I. 30.195.953), Ignacio Acena (C.I. 31.352.123)")
    lineas.append("")
    return "\n".join(lineas)


def guardar_reporte(texto: str, carpeta: str, nombre: str = "salidas_fuerza_trabajo.txt") -> str:
    """Guarda el texto del reporte en carpeta/nombre, creando la carpeta si no existe."""
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)
    return ruta
