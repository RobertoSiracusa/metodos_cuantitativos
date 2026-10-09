"""
Bellman-Ford (un origen)
Capa de Modelo Cuantitativo - Metodos Cuantitativos
Universidad Jose Antonio Paez

Recurrencia (k = numero de arcos permitidos en el camino, de 1 a n-1):

    d_k(v) = min( d_(k-1)(v), min_u { d_(k-1)(u) + w(u,v) } )

Se relajan todos los arcos (el grafo no dirigido entra como arco en ambos
sentidos, en el orden de grafo.arcos(), deterministico) hasta n-1 veces,
cortando antes si una pasada completa no cambia nada. Se guarda el vector de
distancias al final de CADA pasada (para la tabla del reporte) y cuantas
pasadas hicieron falta. Una pasada extra, despues de la convergencia, detecta
ciclos negativos: si todavia relaja algo, el grafo no tiene solucion valida.
"""

from typing import Dict, List, Optional, Tuple

INF = float("inf")


class BellmanFord:
    def __init__(self, grafo):
        self.grafo = grafo
        self.historial: List[Dict[int, float]] = []
        self.iteraciones = 0
        self._dist: Dict[int, float] = {}
        self._pred: Dict[int, Optional[int]] = {}
        self._origen: Optional[int] = None

    def resolver(self, origen: int) -> Dict[int, float]:
        g = self.grafo
        if origen not in g.nodos:
            raise ValueError(f"El nodo origen {origen} no existe en el grafo.")

        dist: Dict[int, float] = {n: INF for n in g.nodos}
        pred: Dict[int, Optional[int]] = {n: None for n in g.nodos}
        dist[origen] = 0.0
        arcos = g.arcos()

        historial: List[Dict[int, float]] = []
        for _ in range(1, g.n):
            cambio = False
            for u, v, p in arcos:
                if dist[u] != INF and dist[u] + p < dist[v]:
                    dist[v] = dist[u] + p
                    pred[v] = u
                    cambio = True
            historial.append(dict(dist))
            if not cambio:
                break

        for u, v, p in arcos:
            if dist[u] != INF and dist[u] + p < dist[v]:
                raise RuntimeError("Se detecto un ciclo negativo: Bellman-Ford no converge.")

        self.historial = historial
        self.iteraciones = len(historial)
        self._dist, self._pred, self._origen = dist, pred, origen
        return dist

    def ruta(self, destino: int) -> Tuple[Optional[List[int]], float]:
        if destino not in self._pred:
            raise ValueError(f"El nodo destino {destino} no existe en el grafo.")
        if self._dist[destino] == INF:
            return None, INF
        camino = [destino]
        actual = destino
        while actual != self._origen:
            actual = self._pred[actual]
            camino.append(actual)
        camino.reverse()
        return camino, self._dist[destino]
