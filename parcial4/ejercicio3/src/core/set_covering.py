"""
Problema de Cubrimiento de Conjuntos (Set Covering) — Ubicacion de estaciones
Capa de Modelo Cuantitativo — Metodos Cuantitativos
Universidad Jose Antonio Paez

    Min Z = sum_j xj
    s.a. sum_j a_ij * xj >= 1   para cada ciudad i
         xj en {0, 1}

a_ij = 1 si una estacion en la ciudad j cubre a la ciudad i segun el limite de
tiempo y el sentido elegido. La tabla de tiempos puede no ser simetrica:
t[i][j] es el tiempo para ir de la ciudad i a la ciudad j.
"""

from dataclasses import dataclass
from itertools import combinations
from typing import List

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

SENTIDOS = {
    "ida_vuelta": "t(ciudad -> estacion) <= limite y t(estacion -> ciudad) <= limite",
    "ciudad_a_estacion": "t(ciudad -> estacion) <= limite",
    "estacion_a_ciudad": "t(estacion -> ciudad) <= limite",
}

MAX_CIUDADES_ENUMERACION = 20  # la enumeracion de optimos alternativos es exponencial


@dataclass
class ResultadoCobertura:
    estaciones: List[int]              # indices 0-based de las ciudades con estacion
    minimo: int
    cobertura: np.ndarray              # a_ij (n x n) de 0/1
    optimos_alternativos: List[List[int]]  # vacia si no se enumero


class ModeloCubrimiento:
    def __init__(self, tiempos: List[List[float]], limite: float = 40, sentido: str = "ida_vuelta"):
        t = np.array(tiempos, dtype=float)
        if t.ndim != 2 or t.shape[0] != t.shape[1]:
            raise ValueError("La tabla de tiempos debe ser cuadrada (n x n).")
        if sentido not in SENTIDOS:
            raise ValueError(f"Sentido invalido: {sentido}. Opciones: {', '.join(SENTIDOS)}")
        if limite < 0:
            raise ValueError("El limite de tiempo no puede ser negativo.")
        self.tiempos = t
        self.limite = float(limite)
        self.sentido = sentido
        self.n = t.shape[0]

    def matriz_cobertura(self) -> np.ndarray:
        """a[i][j] = 1 si la estacion en j cubre a la ciudad i."""
        ida = self.tiempos <= self.limite          # ciudad i -> estacion j
        vuelta = self.tiempos.T <= self.limite     # estacion j -> ciudad i
        if self.sentido == "ciudad_a_estacion":
            a = ida
        elif self.sentido == "estacion_a_ciudad":
            a = vuelta
        else:
            a = ida & vuelta
        return a.astype(int)

    def _cubre_todo(self, a: np.ndarray, estaciones) -> bool:
        return bool((a[:, list(estaciones)].sum(axis=1) >= 1).all())

    def resolver(self, enumerar_alternativos: bool = True) -> ResultadoCobertura:
        a = self.matriz_cobertura()
        sin_cobertura = [i + 1 for i in range(self.n) if a[i].sum() == 0]
        if sin_cobertura:
            raise ValueError(f"Ninguna estacion puede cubrir a las ciudades {sin_cobertura}: problema infactible.")

        r = milp(
            c=np.ones(self.n),
            constraints=LinearConstraint(a, lb=1, ub=np.inf),
            integrality=np.ones(self.n),
            bounds=Bounds(0, 1),
        )
        if r.status != 0:
            raise RuntimeError(f"El solver no encontro solucion: {r.message}")
        estaciones = [j for j in range(self.n) if r.x[j] > 0.5]
        minimo = len(estaciones)

        alternativos: List[List[int]] = []
        if enumerar_alternativos and self.n <= MAX_CIUDADES_ENUMERACION:
            alternativos = [list(c) for c in combinations(range(self.n), minimo) if self._cubre_todo(a, c)]
        return ResultadoCobertura(estaciones, minimo, a, alternativos)

    def existe_solucion_con(self, k: int) -> bool:
        """Comprueba por enumeracion si alguna combinacion de k estaciones cubre todo."""
        a = self.matriz_cobertura()
        return any(self._cubre_todo(a, c) for c in combinations(range(self.n), k))
