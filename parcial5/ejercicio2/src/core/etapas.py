"""
Ruta por Etapas (Programacion Dinamica hacia adelante y hacia atras)
Capa de Modelo Cuantitativo - Metodos Cuantitativos
Universidad Jose Antonio Paez

Recurrencias (para que se puedan copiar a la hoja de examen):

    hacia adelante:  f_s(j) = min_i { f_(s-1)(i) + d(i,j) }
    hacia atras:     g_s(i) = min_j { d(i,j) + g_(s+1)(j) }

donde i recorre los vecinos de j (o j los vecinos de i) que caen en la etapa
inmediatamente anterior (o siguiente). Ademas del salto entre etapas
consecutivas, el grafo tiene aristas entre nodos de la MISMA etapa
(3-4, 5-6, 7-8, 8-9, 12-13), asi que despues de evaluar los vecinos de la
etapa adyacente se relajan las aristas internas de la etapa, en ambos
sentidos, repitiendo hasta que ninguna mejore (punto fijo). Cada mejora,
venga del paso entre etapas o de la relajacion interna, se guarda como un
candidato mas en la fila del nodo. En los empates se queda el primer
candidato evaluado (comparacion estricta <).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

INF = float("inf")


@dataclass
class FilaEtapa:
    etapa: int
    nodo: int
    candidatos: List[Tuple[int, float, float, float]]  # (desde, valor_desde, distancia, total)
    valor: float
    decision: Optional[int]


class RutaPorEtapas:
    def __init__(self, grafo, etapas: List[List[int]]):
        self.grafo = grafo
        self.etapas = [list(e) for e in etapas]

        todos = [nodo for etapa in self.etapas for nodo in etapa]
        if sorted(todos) != sorted(grafo.nodos) or len(set(todos)) != len(todos):
            raise ValueError("Las etapas no son una particion de los nodos del grafo.")

        self._etapa_de: Dict[int, int] = {}
        for s, etapa in enumerate(self.etapas):
            for nodo in etapa:
                self._etapa_de[nodo] = s

        for u, v, _ in grafo.aristas:
            su, sv = self._etapa_de[u], self._etapa_de[v]
            if abs(su - sv) > 1:
                raise ValueError(
                    f"La arista ({u}, {v}) salta etapas no consecutivas ({su} y {sv})."
                )

        self._f: Dict[int, float] = {}
        self._decision_fwd: Dict[int, Optional[int]] = {}
        self._filas_fwd: List[FilaEtapa] = []
        self._origen: Optional[int] = None

        self._g: Dict[int, float] = {}
        self._decision_bwd: Dict[int, Optional[int]] = {}
        self._filas_bwd: List[FilaEtapa] = []
        self._destino: Optional[int] = None

    def _internos(self, s: int) -> List[Tuple[int, int, float]]:
        """Aristas internas de la etapa s, en ambos sentidos, orden de aparicion en el JSON."""
        nodos_etapa = set(self.etapas[s])
        arcos = []
        for u, v, p in self.grafo.aristas:
            if u in nodos_etapa and v in nodos_etapa:
                arcos.append((u, v, p))
                arcos.append((v, u, p))
        return arcos

    @staticmethod
    def _relajar_internos(internos, valores, decision, candidatos_por_nodo):
        cambio = True
        while cambio:
            cambio = False
            for i, j, p in internos:
                if valores[i] == INF:
                    continue
                total = valores[i] + p
                if total < valores[j]:
                    valores[j] = total
                    decision[j] = i
                    candidatos_por_nodo[j].append((i, valores[i], p, total))
                    cambio = True

    # ------------------------------------------------------------------
    # Recursion hacia adelante: f_s(j) = min_i { f_(s-1)(i) + d(i,j) }
    # ------------------------------------------------------------------
    def recursion_adelante(self, origen: int) -> List[FilaEtapa]:
        if origen not in self._etapa_de:
            raise ValueError(f"El nodo origen {origen} no existe en el grafo.")
        s0 = self._etapa_de[origen]

        f: Dict[int, float] = {n: INF for n in self.grafo.nodos}
        decision: Dict[int, Optional[int]] = {n: None for n in self.grafo.nodos}
        candidatos: Dict[int, List[Tuple[int, float, float, float]]] = {n: [] for n in self.grafo.nodos}
        f[origen] = 0.0

        filas: List[FilaEtapa] = []

        # Etapa del origen: tambien se relaja internamente (b).
        self._relajar_internos(self._internos(s0), f, decision, candidatos)
        for nodo in self.etapas[s0]:
            filas.append(FilaEtapa(s0, nodo, list(candidatos[nodo]), f[nodo], decision[nodo]))

        for s in range(s0 + 1, len(self.etapas)):
            for j in self.etapas[s]:
                for i in self.grafo.vecinos(j):
                    if self._etapa_de.get(i) != s - 1 or f[i] == INF:
                        continue
                    p = self.grafo.peso(i, j)
                    total = f[i] + p
                    candidatos[j].append((i, f[i], p, total))
                    if total < f[j]:
                        f[j] = total
                        decision[j] = i
            self._relajar_internos(self._internos(s), f, decision, candidatos)
            for j in self.etapas[s]:
                filas.append(FilaEtapa(s, j, list(candidatos[j]), f[j], decision[j]))

        self._f, self._decision_fwd, self._filas_fwd, self._origen = f, decision, filas, origen
        return filas

    def ruta_adelante(self, destino: int) -> Tuple[Optional[List[int]], float]:
        """Reconstruye el camino origen -> ... -> destino a partir de f/decision.

        Devuelve (None, inf) si recursion_adelante no llego a `destino` (por
        ejemplo porque su etapa queda antes que la del origen).
        """
        if self._origen is None:
            raise RuntimeError("Hay que llamar recursion_adelante(origen) antes de ruta_adelante.")
        if destino not in self._f or self._f[destino] == INF:
            return None, INF
        camino = [destino]
        actual = destino
        while actual != self._origen:
            anterior = self._decision_fwd.get(actual)
            if anterior is None:
                return None, INF
            camino.append(anterior)
            actual = anterior
        camino.reverse()
        return camino, self._f[destino]

    # ------------------------------------------------------------------
    # Recursion hacia atras: g_s(i) = min_j { d(i,j) + g_(s+1)(j) }
    # ------------------------------------------------------------------
    def recursion_atras(self, destino: int) -> List[FilaEtapa]:
        if destino not in self._etapa_de:
            raise ValueError(f"El nodo destino {destino} no existe en el grafo.")
        sD = self._etapa_de[destino]

        g: Dict[int, float] = {n: INF for n in self.grafo.nodos}
        decision: Dict[int, Optional[int]] = {n: None for n in self.grafo.nodos}
        candidatos: Dict[int, List[Tuple[int, float, float, float]]] = {n: [] for n in self.grafo.nodos}
        g[destino] = 0.0

        filas: List[FilaEtapa] = []

        # Etapa del destino: solo relajacion interna (asi 12 obtiene g=100 via 13).
        self._relajar_internos(self._internos(sD), g, decision, candidatos)
        for nodo in self.etapas[sD]:
            filas.append(FilaEtapa(sD, nodo, list(candidatos[nodo]), g[nodo], decision[nodo]))

        for s in range(sD - 1, -1, -1):
            for i in self.etapas[s]:
                for j in self.grafo.vecinos(i):
                    if self._etapa_de.get(j) != s + 1 or g[j] == INF:
                        continue
                    p = self.grafo.peso(i, j)
                    total = p + g[j]
                    candidatos[i].append((j, g[j], p, total))
                    if total < g[i]:
                        g[i] = total
                        decision[i] = j
            self._relajar_internos(self._internos(s), g, decision, candidatos)
            for i in self.etapas[s]:
                filas.append(FilaEtapa(s, i, list(candidatos[i]), g[i], decision[i]))

        self._g, self._decision_bwd, self._filas_bwd, self._destino = g, decision, filas, destino
        return filas

    def ruta_atras(self, origen: int) -> Tuple[Optional[List[int]], float]:
        """Reconstruye el camino origen -> ... -> destino a partir de g/decision.

        Devuelve (None, inf) si recursion_atras no llego a `origen`.
        """
        if self._destino is None:
            raise RuntimeError("Hay que llamar recursion_atras(destino) antes de ruta_atras.")
        if origen not in self._g or self._g[origen] == INF:
            return None, INF
        camino = [origen]
        actual = origen
        while actual != self._destino:
            siguiente = self._decision_bwd.get(actual)
            if siguiente is None:
                return None, INF
            camino.append(siguiente)
            actual = siguiente
        return camino, self._g[origen]
