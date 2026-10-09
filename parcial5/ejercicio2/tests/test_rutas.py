import json
import os

import pytest
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path

from src.core.bellman_ford import BellmanFord
from src.core.etapas import RutaPorEtapas
from src.core.floyd_warshall import FloydWarshall
from src.core.grafo import Grafo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(BASE_DIR, "datos", "grafo.json")

F_ESPERADO = {1: 0, 2: 100, 3: 50, 4: 40, 5: 150, 6: 140, 7: 270, 8: 280, 9: 240, 10: 330, 11: 340, 12: 390, 13: 430}
G_ESPERADO = {13: 0, 12: 100, 10: 100, 11: 150, 7: 160, 8: 170, 9: 250, 5: 280, 6: 320, 2: 380, 3: 380, 4: 400, 1: 430}
RUTA_ESPERADA = [1, 3, 5, 7, 10, 13]
COSTO_ESPERADO = 430


@pytest.fixture
def datos():
    with open(DATOS, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def grafo(datos):
    return Grafo(datos["nodos"], datos["aristas"])


@pytest.fixture
def etapas(grafo, datos):
    return RutaPorEtapas(grafo, datos["etapas"])


# ---------------------------------------------------------------------------
# Recursion hacia adelante
# ---------------------------------------------------------------------------
def test_recursion_adelante_valores(etapas):
    filas = etapas.recursion_adelante(1)
    f = {fila.nodo: fila.valor for fila in filas}
    assert f == F_ESPERADO


def test_ruta_adelante(etapas):
    etapas.recursion_adelante(1)
    ruta, costo = etapas.ruta_adelante(13)
    assert ruta == RUTA_ESPERADA
    assert costo == COSTO_ESPERADO


# ---------------------------------------------------------------------------
# Recursion hacia atras
# ---------------------------------------------------------------------------
def test_recursion_atras_valores(etapas):
    filas = etapas.recursion_atras(13)
    g = {fila.nodo: fila.valor for fila in filas}
    assert g == G_ESPERADO


def test_recursion_atras_mejoras_internas(etapas):
    filas = etapas.recursion_atras(13)
    g = {fila.nodo: fila for fila in filas}
    # 6 mejora via 5 (relajacion interna de la etapa [5, 6])
    assert g[6].decision == 5
    # 4 mejora via 3 (relajacion interna de la etapa [2, 3, 4])
    assert g[4].decision == 3


def test_ruta_atras(etapas):
    etapas.recursion_atras(13)
    ruta, costo = etapas.ruta_atras(1)
    assert ruta == RUTA_ESPERADA
    assert costo == COSTO_ESPERADO


# ---------------------------------------------------------------------------
# Floyd-Warshall
# ---------------------------------------------------------------------------
def test_floyd_warshall_simetrica_y_diagonal(grafo):
    fw = FloydWarshall(grafo)
    D = fw.resolver()
    n = grafo.n
    for i in range(n):
        assert D[i][i] == 0
        for j in range(n):
            assert D[i][j] == D[j][i]


def test_floyd_warshall_fila_nodo_1_coincide_con_f(grafo, datos):
    fw = FloydWarshall(grafo)
    fw.resolver()
    idx = {n: i for i, n in enumerate(grafo.nodos)}
    for nodo, valor in F_ESPERADO.items():
        assert fw._D[idx[1]][idx[nodo]] == valor


def test_floyd_warshall_ruta_1_13(grafo):
    fw = FloydWarshall(grafo)
    fw.resolver()
    ruta, costo = fw.ruta(1, 13)
    assert ruta == RUTA_ESPERADA
    assert costo == COSTO_ESPERADO


# ---------------------------------------------------------------------------
# Bellman-Ford
# ---------------------------------------------------------------------------
def test_bellman_ford_desde_1_coincide_con_f(grafo):
    bf = BellmanFord(grafo)
    dist = bf.resolver(1)
    assert dist == F_ESPERADO


def test_bellman_ford_desde_13_coincide_con_g(grafo):
    bf = BellmanFord(grafo)
    dist = bf.resolver(13)
    assert dist == G_ESPERADO


def test_bellman_ford_ruta_1_13(grafo):
    bf = BellmanFord(grafo)
    bf.resolver(1)
    ruta, costo = bf.ruta(13)
    assert ruta == RUTA_ESPERADA
    assert costo == COSTO_ESPERADO


# ---------------------------------------------------------------------------
# Coincidencia con scipy
# ---------------------------------------------------------------------------
def test_coincide_con_scipy(grafo):
    idx = {n: i for i, n in enumerate(grafo.nodos)}
    filas, cols, pesos = [], [], []
    for u, v, p in grafo.arcos():
        filas.append(idx[u])
        cols.append(idx[v])
        pesos.append(p)
    matriz = csr_matrix((pesos, (filas, cols)), shape=(grafo.n, grafo.n))
    for metodo in ("FW", "BF"):
        D = shortest_path(matriz, method=metodo, directed=False)
        assert D[idx[1]][idx[13]] == COSTO_ESPERADO


# ---------------------------------------------------------------------------
# Validaciones del grafo
# ---------------------------------------------------------------------------
def test_arista_a_nodo_inexistente():
    with pytest.raises(ValueError):
        Grafo([1, 2, 3], [[1, 99, 10]])


def test_peso_cero_o_negativo():
    with pytest.raises(ValueError):
        Grafo([1, 2], [[1, 2, 0]])
    with pytest.raises(ValueError):
        Grafo([1, 2], [[1, 2, -5]])


def test_arista_duplicada():
    with pytest.raises(ValueError):
        Grafo([1, 2], [[1, 2, 10], [2, 1, 10]])


def test_lazo():
    with pytest.raises(ValueError):
        Grafo([1, 2], [[1, 1, 10]])


# ---------------------------------------------------------------------------
# Validaciones de etapas
# ---------------------------------------------------------------------------
def test_etapas_que_no_particionan(grafo):
    with pytest.raises(ValueError):
        RutaPorEtapas(grafo, [[1], [2, 3, 4], [5, 6], [7, 8, 9], [10, 11], [12]])  # falta el 13


def test_arista_que_salta_etapas(grafo):
    # con este agrupamiento, la arista (2, 5) conecta la etapa 0 con la etapa 2:
    # salto no consecutivo.
    etapas_malas = [[1, 2], [3, 4], [5, 6], [7, 8, 9], [10, 11], [12, 13]]
    with pytest.raises(ValueError):
        RutaPorEtapas(grafo, etapas_malas)
