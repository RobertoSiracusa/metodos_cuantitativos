"""
Ramificacion y Acotamiento (Branch and Bound) para Programacion Lineal Entera
Capa de Modelo Cuantitativo — Metodos Cuantitativos
Universidad Jose Antonio Paez

Resuelve:  Max Z = c.x   s.a.  A.x <= b ,  x >= 0 y enteras.
Cada nodo resuelve la relajacion lineal con SciPy (linprog / HiGHS). La
ramificacion, la poda y el arbol son propios.
"""

from dataclasses import dataclass, field
from math import floor
from typing import List, Optional, Tuple

from scipy.optimize import linprog

TOLERANCIA = 1e-6

Cota = Tuple[float, Optional[float]]  # (minimo, maximo) de una variable


@dataclass
class Nodo:
    """Un subproblema del arbol."""
    id: int
    cotas: List[Cota]
    restriccion: str                    # rama que lo genero, ej. "x1 <= 3"
    padre: Optional[int]
    x: Optional[List[float]] = None     # solucion de la relajacion (None si infactible)
    z: Optional[float] = None
    estado: str = ""                    # ENTERA, RAMIFICADO, PODADO, INFACTIBLE
    hijos: List[int] = field(default_factory=list)


@dataclass
class ResultadoBB:
    x_optimo: Optional[List[float]]
    z_optimo: Optional[float]
    nodos: List[Nodo]
    orden_exploracion: List[int]


class ModeloBranchAndBound:
    """
    Maximizacion entera por ramificacion y acotamiento.
    Regla de ramificacion: primera variable fraccionaria (en orden x1, x2, ...).
    Exploracion: en profundidad, primero la rama '<='.
    """

    def __init__(self, c: List[float], A: List[List[float]], b: List[float]):
        if len(A) != len(b):
            raise ValueError("A y b deben tener la misma cantidad de filas.")
        if any(len(fila) != len(c) for fila in A):
            raise ValueError("Cada fila de A debe tener tantos coeficientes como c.")
        self.c = [float(v) for v in c]
        self.A = [[float(v) for v in fila] for fila in A]
        self.b = [float(v) for v in b]
        self.n = len(c)

    def resolver_relajacion(self, cotas: List[Cota]) -> Tuple[Optional[List[float]], Optional[float]]:
        """Resuelve el PL relajado con las cotas dadas. Devuelve (x, Z) o (None, None)."""
        r = linprog([-v for v in self.c], A_ub=self.A, b_ub=self.b, bounds=cotas, method="highs")
        if r.status != 0:
            return None, None
        x = [0.0 if abs(v) < TOLERANCIA else float(v) for v in r.x]
        return x, float(-r.fun)

    @staticmethod
    def es_entero(v: float) -> bool:
        return abs(v - round(v)) <= TOLERANCIA

    def _crear_nodo(self, nodos: List[Nodo], cotas, restriccion, padre) -> Nodo:
        nodo = Nodo(id=len(nodos), cotas=cotas, restriccion=restriccion, padre=padre)
        nodo.x, nodo.z = self.resolver_relajacion(cotas)
        nodos.append(nodo)
        return nodo

    def resolver(self) -> ResultadoBB:
        nodos: List[Nodo] = []
        raiz = self._crear_nodo(nodos, [(0.0, None)] * self.n, "relajacion lineal", None)
        pila = [raiz.id]
        orden: List[int] = []
        mejor_x, mejor_z = None, None

        while pila:
            nodo = nodos[pila.pop()]
            orden.append(nodo.id)

            if nodo.x is None:
                nodo.estado = "INFACTIBLE"
                continue
            if mejor_z is not None and nodo.z <= mejor_z + TOLERANCIA:
                nodo.estado = f"PODADO (Z = {nodo.z:.2f} <= {mejor_z:.2f})"
                continue

            fraccionarias = [i for i, v in enumerate(nodo.x) if not self.es_entero(v)]
            if not fraccionarias:
                nodo.estado = "ENTERA (mejor solucion hasta ahora)"
                mejor_x = [float(round(v)) for v in nodo.x]
                mejor_z = nodo.z
                continue

            i = fraccionarias[0]
            piso = floor(nodo.x[i])
            nodo.estado = f"RAMIFICADO en x{i + 1} = {nodo.x[i]:.4f}"

            cotas_menor = list(nodo.cotas)
            cotas_menor[i] = (nodo.cotas[i][0], float(piso))
            cotas_mayor = list(nodo.cotas)
            cotas_mayor[i] = (float(piso + 1), nodo.cotas[i][1])

            h1 = self._crear_nodo(nodos, cotas_menor, f"x{i + 1} <= {piso}", nodo.id)
            h2 = self._crear_nodo(nodos, cotas_mayor, f"x{i + 1} >= {piso + 1}", nodo.id)
            nodo.hijos = [h1.id, h2.id]
            pila.extend([h2.id, h1.id])  # se explora primero la rama '<='

        return ResultadoBB(mejor_x, mejor_z, nodos, orden)
