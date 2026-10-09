"""
Grafo no dirigido
Capa de Modelo Cuantitativo - Metodos Cuantitativos
Universidad Jose Antonio Paez

Representa el grafo por lista de adyacencia a partir de nodos y aristas
[u, v, peso]. En un grafo no dirigido un peso negativo equivale a decir que
ir y volver por la misma arista "ahorra" costo: eso es, por definicion, un
ciclo negativo, y los metodos de camino minimo (Floyd-Warshall, Bellman-Ford)
no convergen a una respuesta valida. Por eso se exige peso > 0 al construir
el grafo.
"""

from typing import Dict, List, Tuple


class Grafo:
    def __init__(self, nodos: List[int], aristas: List[List[float]]):
        if not nodos:
            raise ValueError("La lista de nodos no puede estar vacia.")
        if any(not isinstance(n, int) for n in nodos):
            raise ValueError("Todos los nodos deben ser enteros.")
        if len(set(nodos)) != len(nodos):
            raise ValueError("Los nodos no pueden repetirse.")

        self.nodos = list(nodos)
        self.n = len(self.nodos)
        indice = set(self.nodos)

        vistas = set()
        self._vecinos: Dict[int, List[Tuple[int, float]]] = {n: [] for n in self.nodos}
        aristas_norm = []
        for arista in aristas:
            if len(arista) != 3:
                raise ValueError(f"Arista mal formada (se esperan u, v, peso): {arista}")
            u, v, peso = arista
            if u not in indice or v not in indice:
                raise ValueError(f"La arista ({u}, {v}) referencia un nodo que no existe.")
            if u == v:
                raise ValueError(f"La arista ({u}, {v}) es un lazo (u == v); no esta permitido.")
            if not isinstance(peso, (int, float)) or isinstance(peso, bool) or peso <= 0:
                raise ValueError(
                    f"La arista ({u}, {v}) tiene peso {peso}: debe ser numerico y > 0 "
                    "(en un grafo no dirigido un peso negativo es un ciclo negativo)."
                )
            clave = frozenset((u, v))
            if clave in vistas:
                raise ValueError(f"Arista duplicada entre {u} y {v}.")
            vistas.add(clave)

            peso = float(peso)
            aristas_norm.append((u, v, peso))
            self._vecinos[u].append((v, peso))
            self._vecinos[v].append((u, peso))

        self.aristas: List[Tuple[int, int, float]] = aristas_norm

    def peso(self, u: int, v: int) -> float:
        for w, p in self._vecinos.get(u, []):
            if w == v:
                return p
        return float("inf")

    def vecinos(self, u: int) -> List[int]:
        """Vecinos de u, en el orden en que aparecen las aristas en el JSON."""
        return [w for w, _ in self._vecinos.get(u, [])]

    def arcos(self) -> List[Tuple[int, int, float]]:
        """Cada arista no dirigida como dos arcos (u, v, peso) y (v, u, peso)."""
        arcos = []
        for u, v, p in self.aristas:
            arcos.append((u, v, p))
            arcos.append((v, u, p))
        return arcos
