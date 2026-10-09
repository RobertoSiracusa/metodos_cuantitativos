"""
Floyd-Warshall (todos los pares)
Capa de Modelo Cuantitativo - Metodos Cuantitativos
Universidad Jose Antonio Paez

Recurrencia (k = nodo intermedio permitido, de 0 a n-1 en orden):

    D_k[i][j] = min( D_(k-1)[i][j], D_(k-1)[i][k] + D_(k-1)[k][j] )

D_0 es la matriz de pesos directos (inf si no hay arista, 0 en la diagonal).
Se guarda ademas la matriz de "siguiente nodo" P para reconstruir rutas en
O(n) y, por nodo intermedio k, cuantas celdas (i, j) mejoraron (para mostrar
cuanto aporta cada nodo como paso intermedio).
"""

from typing import List, Optional, Tuple

INF = float("inf")


class FloydWarshall:
    def __init__(self, grafo):
        self.grafo = grafo
        self._D: Optional[List[List[float]]] = None
        self._P: Optional[List[List[Optional[int]]]] = None
        self._idx = {n: i for i, n in enumerate(grafo.nodos)}
        self.mejoras_por_k: List[Tuple[int, int]] = []  # (nodo_k, celdas_mejoradas)

    def resolver(self) -> List[List[float]]:
        g = self.grafo
        n = g.n
        nodos = g.nodos
        idx = self._idx

        D = [[INF] * n for _ in range(n)]
        P: List[List[Optional[int]]] = [[None] * n for _ in range(n)]
        for i in range(n):
            D[i][i] = 0.0
            P[i][i] = nodos[i]
        for u, v, p in g.arcos():
            i, j = idx[u], idx[v]
            if p < D[i][j]:
                D[i][j] = p
                P[i][j] = v

        mejoras = []
        for k in range(n):
            cuenta = 0
            for i in range(n):
                dik = D[i][k]
                if dik == INF:
                    continue
                fila_k = D[k]
                for j in range(n):
                    nuevo = dik + fila_k[j]
                    if nuevo < D[i][j]:
                        D[i][j] = nuevo
                        P[i][j] = P[i][k]
                        cuenta += 1
            mejoras.append((nodos[k], cuenta))

        self._D, self._P = D, P
        self.mejoras_por_k = mejoras
        return D

    def ruta(self, i: int, j: int) -> Tuple[Optional[List[int]], float]:
        if self._D is None:
            self.resolver()
        idx = self._idx
        if i not in idx or j not in idx:
            raise ValueError(f"Nodo inexistente en Floyd-Warshall: {i if i not in idx else j}")
        ii, jj = idx[i], idx[j]
        if self._D[ii][jj] == INF:
            return None, INF
        camino = [i]
        actual = i
        while actual != j:
            actual = self._P[idx[actual]][jj]
            camino.append(actual)
        return camino, self._D[ii][jj]
