"""
Punto de Entrada - Ejercicio 2, Parcial V (Ruta mas corta por programacion dinamica)
Universidad Jose Antonio Paez - Metodos Cuantitativos

Uso:
    python3 main.py                              # problema del parcial (1 -> 13)
    python3 main.py --origen 2 --destino 9       # otro par de nodos
    python3 main.py --datos otro_grafo.json
    python3 main.py --sin-exportar
"""
import argparse
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path

from src.core.bellman_ford import BellmanFord
from src.core.etapas import RutaPorEtapas
from src.core.floyd_warshall import FloydWarshall
from src.core.grafo import Grafo
from src.services.reporter import generar_reporte, guardar_reporte

DATOS_POR_DEFECTO = os.path.join(BASE_DIR, "datos", "grafo.json")


def _verificar_scipy(grafo: Grafo, origen: int, destino: int) -> dict:
    """Corre scipy.sparse.csgraph.shortest_path con method='FW' y 'BF' y
    devuelve, por metodo, (distancia, ruta) entre origen y destino."""
    idx = {n: i for i, n in enumerate(grafo.nodos)}
    n = grafo.n
    filas, cols, pesos = [], [], []
    for u, v, p in grafo.arcos():
        filas.append(idx[u])
        cols.append(idx[v])
        pesos.append(p)
    matriz = csr_matrix((pesos, (filas, cols)), shape=(n, n))

    resultados = {}
    i, j = idx[origen], idx[destino]
    for metodo in ("FW", "BF"):
        D, pred = shortest_path(matriz, method=metodo, directed=False, return_predecessors=True)
        dist = D[i, j]
        if np.isinf(dist):
            resultados[metodo] = (float("inf"), None)
            continue
        camino_idx = [j]
        actual = j
        while actual != i:
            actual = pred[i, actual]
            camino_idx.append(actual)
        camino_idx.reverse()
        resultados[metodo] = (float(dist), [grafo.nodos[k] for k in camino_idx])
    return resultados


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Ruta mas corta (programacion dinamica, Floyd-Warshall, Bellman-Ford).")
    p.add_argument("--datos", default=DATOS_POR_DEFECTO, help="JSON con nodos, aristas y etapas")
    p.add_argument("--origen", type=int, default=None, help="nodo origen (por defecto el del JSON)")
    p.add_argument("--destino", type=int, default=None, help="nodo destino (por defecto el del JSON)")
    p.add_argument("--sin-exportar", action="store_true", help="no guardar el reporte en outputs/")
    args = p.parse_args(argv)

    try:
        with open(args.datos, encoding="utf-8") as f:
            d = json.load(f)

        grafo = Grafo(d["nodos"], d["aristas"])
        origen = args.origen if args.origen is not None else d["origen"]
        destino = args.destino if args.destino is not None else d["destino"]

        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos.")
        if origen not in grafo.nodos:
            raise ValueError(f"El nodo origen {origen} no existe en el grafo.")
        if destino not in grafo.nodos:
            raise ValueError(f"El nodo destino {destino} no existe en el grafo.")

        etapas_obj = RutaPorEtapas(grafo, d["etapas"])
        etapas_obj.recursion_adelante(origen)
        etapas_obj.recursion_atras(destino)

        floyd = FloydWarshall(grafo)
        floyd.resolver()

        bellman = BellmanFord(grafo)
        bellman.resolver(origen)

        scipy_res = _verificar_scipy(grafo, origen, destino)

        texto = generar_reporte(grafo, d, etapas_obj, floyd, bellman, scipy_res, origen, destino)
    except (OSError, KeyError, ValueError, RuntimeError, json.JSONDecodeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(texto)
    if not args.sin_exportar:
        ruta = guardar_reporte(texto, os.path.join(BASE_DIR, "outputs"))
        print(f"Reporte guardado en: {ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
