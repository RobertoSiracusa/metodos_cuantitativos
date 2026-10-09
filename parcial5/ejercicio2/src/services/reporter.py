"""
Servicio de reportes - Ejercicio 2 (Ruta mas corta)
Formatea el grafo, las dos recursiones por etapas (adelante y atras),
Bellman-Ford, Floyd-Warshall y la verificacion con scipy, y los guarda en
outputs/. Formato ASCII (sin tildes), igual que el Ejercicio 4.
"""

import os

INF = float("inf")


def _n(v: float) -> str:
    if v == INF:
        return "inf"
    return f"{v:g}"


def _ruta_txt(ruta):
    return " -> ".join(str(n) for n in ruta) if ruta else None


# ---------------------------------------------------------------------------
# 1. Datos
# ---------------------------------------------------------------------------
def formatear_datos(grafo, datos) -> str:
    lineas = [
        "EJERCICIO 2 - RUTA MAS CORTA (PROGRAMACION DINAMICA)",
        "=" * 52,
        "",
        datos.get("descripcion", ""),
        f"Origen (oficina anterior): {datos['origen']}   Destino (oficina nueva): {datos['destino']}",
        "",
        "Aristas (no dirigidas):",
    ]
    for u, v, p in grafo.aristas:
        lineas.append(f"  {u:>2} - {v:<2} : {_n(p)}")
    lineas.append("")
    lineas.append("Etapas:")
    for s, etapa in enumerate(datos["etapas"]):
        lineas.append(f"  Etapa {s}: {etapa}")
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# 2 y 3. Recursion por etapas (adelante / atras)
# ---------------------------------------------------------------------------
def _marca_min(fila) -> set:
    """Indices (0-based) de los candidatos que coinciden con la decision final."""
    marcados = set()
    for i, (desde, _, _, total) in enumerate(fila.candidatos):
        if desde == fila.decision and abs(total - fila.valor) < 1e-9:
            marcados.add(i)
            break
    return marcados


def _formatear_filas(filas, letra: str) -> str:
    lineas = []
    etapa_actual = None
    for fila in filas:
        if fila.etapa != etapa_actual:
            if etapa_actual is not None:
                lineas.append("")
            etapa_actual = fila.etapa
            lineas.append(f"Etapa {etapa_actual}:")
        lineas.append(f"  nodo {fila.nodo}:")
        marcados = _marca_min(fila)
        for i, (desde, valor_desde, dist, total) in enumerate(fila.candidatos):
            marca = "  <- min" if i in marcados else ""
            lineas.append(f"    via {desde}: {_n(valor_desde)} + {_n(dist)} = {_n(total)}{marca}")
        decision_txt = str(fila.decision) if fila.decision is not None else "-"
        lineas.append(f"    {letra}({fila.nodo}) = {_n(fila.valor)}   decision: {decision_txt}")
    return "\n".join(lineas)


def formatear_adelante(etapas_obj, origen: int, destino: int) -> str:
    titulo = f"RECURSION HACIA ADELANTE (desde el nodo {origen})"
    filas = etapas_obj.recursion_adelante(origen)
    ruta, costo = etapas_obj.ruta_adelante(destino)
    lineas = [
        titulo,
        "-" * len(titulo),
        "f_s(j) = min_i { f_(s-1)(i) + d(i,j) }   (mas relajacion interna de la etapa)",
        "",
        _formatear_filas(filas, "f"),
        "",
    ]
    if ruta:
        lineas.append(f"Ruta (adelante) {origen} -> {destino}: {_ruta_txt(ruta)}")
        lineas.append(f"Costo total: {_n(costo)}")
    else:
        lineas.append(
            f"No aplica: la recursion hacia adelante no alcanza al nodo {destino} "
            f"respetando el orden de las etapas."
        )
    return "\n".join(lineas)


def formatear_atras(etapas_obj, origen: int, destino: int) -> str:
    titulo = f"RECURSION HACIA ATRAS (desde el nodo {destino})"
    filas = etapas_obj.recursion_atras(destino)
    ruta, costo = etapas_obj.ruta_atras(origen)
    lineas = [
        titulo,
        "-" * len(titulo),
        "g_s(i) = min_j { d(i,j) + g_(s+1)(j) }   (mas relajacion interna de la etapa)",
        "",
        _formatear_filas(filas, "g"),
        "",
    ]
    if ruta:
        lineas.append(f"Ruta (atras) {origen} -> {destino}: {_ruta_txt(ruta)}")
        lineas.append(f"Costo total: {_n(costo)}")
    else:
        lineas.append(
            f"No aplica: la recursion hacia atras no alcanza al nodo {origen} "
            f"respetando el orden de las etapas."
        )
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# 4. Bellman-Ford
# ---------------------------------------------------------------------------
def formatear_bellman(grafo, bellman, origen: int, destino: int) -> str:
    titulo = f"BELLMAN-FORD (origen {origen})"
    nodos = grafo.nodos
    ancho = max(6, max(len(str(n)) for n in nodos) + 2)
    encabezado = "Iteracion".ljust(11) + "".join(f"{n:>{ancho}}" for n in nodos)
    lineas = [titulo, "-" * len(titulo), "d_k(v) = min( d_(k-1)(v), min_u { d_(k-1)(u) + w(u,v) } )", "", encabezado]
    for k, fila in enumerate(bellman.historial, start=1):
        valores = "".join(f"{_n(fila[n]):>{ancho}}" for n in nodos)
        lineas.append(f"{k:<11}{valores}")
    lineas.append("")
    lineas.append(f"Iteraciones hasta converger: {bellman.iteraciones}")
    ruta, costo = bellman.ruta(destino)
    lineas.append("")
    if ruta:
        lineas.append(f"Ruta: {_ruta_txt(ruta)}")
        lineas.append(f"Costo total: {_n(costo)}")
    else:
        lineas.append(f"No hay ruta de {origen} a {destino}.")
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# 5. Floyd-Warshall
# ---------------------------------------------------------------------------
def formatear_floyd(grafo, floyd, origen: int, destino: int) -> str:
    titulo = "FLOYD-WARSHALL"
    nodos = grafo.nodos
    D = floyd._D
    ancho = max(6, max(len(str(n)) for n in nodos) + 2)
    lineas = [
        titulo,
        "-" * len(titulo),
        "D_k[i][j] = min( D_(k-1)[i][j], D_(k-1)[i][k] + D_(k-1)[k][j] )",
        "",
        "Matriz de distancias final (D):",
        "".ljust(6) + "".join(f"{n:>{ancho}}" for n in nodos),
    ]
    for i, ni in enumerate(nodos):
        fila = "".join(f"{_n(D[i][j]):>{ancho}}" for j in range(len(nodos)))
        lineas.append(f"{ni:>6}{fila}")
    lineas.append("")
    lineas.append("Celdas (i, j) mejoradas por cada nodo intermedio k:")
    for nodo_k, cuenta in floyd.mejoras_por_k:
        lineas.append(f"  k={nodo_k}: {cuenta} celdas")
    ruta, costo = floyd.ruta(origen, destino)
    lineas.append("")
    if ruta:
        lineas.append(f"Ruta {origen} -> {destino}: {_ruta_txt(ruta)}")
        lineas.append(f"Costo total: {_n(costo)}")
    else:
        lineas.append(f"No hay ruta de {origen} a {destino}.")
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# 6. Verificacion (scipy)
# ---------------------------------------------------------------------------
def formatear_verificacion(etapas_obj, floyd, bellman, scipy_res, origen: int, destino: int) -> str:
    titulo = "VERIFICACION"
    dist_fw_scipy, ruta_fw_scipy = scipy_res["FW"]
    dist_bf_scipy, ruta_bf_scipy = scipy_res["BF"]
    coinciden_scipy = abs(dist_fw_scipy - dist_bf_scipy) < 1e-9

    ruta_etapas, costo_etapas = etapas_obj.ruta_adelante(destino)
    ruta_fw, costo_fw = floyd.ruta(origen, destino)
    ruta_bf, costo_bf = bellman.ruta(destino)

    filas = [
        ("Etapas (DP)", costo_etapas, ruta_etapas),
        ("Floyd-Warshall", costo_fw, ruta_fw),
        ("Bellman-Ford", costo_bf, ruta_bf),
        ("scipy (FW/BF)", dist_fw_scipy, ruta_fw_scipy),
    ]

    lineas = [
        titulo,
        "-" * len(titulo),
        f"scipy Floyd-Warshall: D[{origen}][{destino}] = {_n(dist_fw_scipy)}   ruta: {_ruta_txt(ruta_fw_scipy) or '-'}",
        f"scipy Bellman-Ford:   D[{origen}][{destino}] = {_n(dist_bf_scipy)}   ruta: {_ruta_txt(ruta_bf_scipy) or '-'}",
        f"scipy FW y BF dan el mismo D[{origen}][{destino}]: {'SI' if coinciden_scipy else 'NO'}",
        "",
        f"{'Metodo':<16} | {'Distancia ' + str(origen) + '->' + str(destino):>18} | Ruta",
    ]
    valores_costo = [c for _, c, _ in filas]
    todos_coinciden = all(abs(c - valores_costo[0]) < 1e-9 for c in valores_costo)
    for nombre, costo, ruta in filas:
        lineas.append(f"{nombre:<16} | {_n(costo):>18} | {_ruta_txt(ruta) or '-'}")
    lineas.append("")
    lineas.append(f"Coinciden: {'SI' if todos_coinciden else 'NO'}")
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# 7. Complejidad
# ---------------------------------------------------------------------------
def formatear_complejidad(grafo, bellman) -> str:
    titulo = "COMPLEJIDAD"
    n = grafo.n
    m_no_dirigidas = len(grafo.aristas)
    m_arcos = len(grafo.arcos())
    lineas = [
        titulo,
        "-" * len(titulo),
        f"n = {n} nodos, m = {m_no_dirigidas} aristas no dirigidas ({m_arcos} arcos dirigidos)",
        f"Floyd-Warshall: O(n^3) = {n}^3 = {n ** 3} operaciones basicas",
        f"Bellman-Ford:   O(n*m) = {n}*{m_arcos} = {n * m_arcos} en el peor caso; "
        f"esta corrida convergio en {bellman.iteraciones} iteraciones "
        f"({bellman.iteraciones * m_arcos} relajaciones reales)",
        "Floyd-Warshall conviene cuando se necesitan TODOS los pares de distancias; "
        "Bellman-Ford conviene para un solo origen y, a diferencia de Dijkstra, "
        "admite pesos negativos en grafos dirigidos (aqui no aplica: el grafo es "
        "no dirigido y los pesos son todos > 0).",
    ]
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
def generar_reporte(grafo, datos, etapas_obj, floyd, bellman, scipy_res, origen: int, destino: int) -> str:
    partes = [
        formatear_datos(grafo, datos),
        formatear_adelante(etapas_obj, origen, destino),
        formatear_atras(etapas_obj, origen, destino),
        formatear_bellman(grafo, bellman, origen, destino),
        formatear_floyd(grafo, floyd, origen, destino),
        formatear_verificacion(etapas_obj, floyd, bellman, scipy_res, origen, destino),
        formatear_complejidad(grafo, bellman),
    ]
    return "\n\n".join(partes) + "\n"


def guardar_reporte(texto: str, carpeta: str, nombre: str = "reporte_ejercicio2.txt") -> str:
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)
    return ruta
