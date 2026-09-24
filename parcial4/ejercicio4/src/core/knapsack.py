"""
Problema de la Mochila 0/1 (Knapsack)
Capa de Modelo Cuantitativo — Metodos Cuantitativos
Universidad Jose Antonio Paez

    Max Z = sum_i vi * xi
    s.a. sum_i wi * xi <= W
         xi en {0, 1}

Se resuelve por programacion dinamica (propia) y se verifica con scipy.milp.
Tambien se calcula la solucion voraz (mejor valor por kg) para comparar.
"""

from dataclasses import dataclass
from itertools import combinations
from typing import List

from scipy.optimize import Bounds, LinearConstraint, milp

MAX_OBJETOS_ENUMERACION = 20


@dataclass
class SolucionMochila:
    objetos: List[int]     # indices 0-based
    valor: float
    peso: float


class ModeloMochila:
    def __init__(self, pesos: List[int], valores: List[float], capacidad: int):
        if len(pesos) != len(valores) or not pesos:
            raise ValueError("pesos y valores deben tener el mismo largo (y no estar vacios).")
        if any(int(w) != w or w <= 0 for w in pesos) or int(capacidad) != capacidad or capacidad < 0:
            raise ValueError("Los pesos deben ser enteros positivos y la capacidad un entero >= 0.")
        self.pesos = [int(w) for w in pesos]
        self.valores = [float(v) for v in valores]
        self.capacidad = int(capacidad)
        self.n = len(pesos)

    def _solucion(self, objetos) -> SolucionMochila:
        objetos = sorted(objetos)
        return SolucionMochila(
            objetos,
            sum(self.valores[i] for i in objetos),
            sum(self.pesos[i] for i in objetos),
        )

    def tabla_dp(self) -> List[List[float]]:
        """F[i][c] = mejor valor usando los primeros i objetos con capacidad c."""
        W = self.capacidad
        F = [[0.0] * (W + 1) for _ in range(self.n + 1)]
        for i in range(1, self.n + 1):
            w, v = self.pesos[i - 1], self.valores[i - 1]
            for c in range(W + 1):
                F[i][c] = F[i - 1][c]
                if w <= c and F[i - 1][c - w] + v > F[i][c]:
                    F[i][c] = F[i - 1][c - w] + v
        return F

    def resolver_dp(self) -> SolucionMochila:
        F = self.tabla_dp()
        c, objetos = self.capacidad, []
        for i in range(self.n, 0, -1):
            if F[i][c] != F[i - 1][c]:       # el objeto i entro
                objetos.append(i - 1)
                c -= self.pesos[i - 1]
        return self._solucion(objetos)

    def resolver_milp(self) -> SolucionMochila:
        r = milp(
            c=[-v for v in self.valores],
            constraints=LinearConstraint([self.pesos], ub=self.capacidad),
            integrality=[1] * self.n,
            bounds=Bounds(0, 1),
        )
        if r.status != 0:
            raise RuntimeError(f"El solver no encontro solucion: {r.message}")
        return self._solucion([i for i in range(self.n) if r.x[i] > 0.5])

    def resolver_voraz(self) -> SolucionMochila:
        """Heuristica: agrega objetos por mayor valor/peso mientras quepan."""
        orden = sorted(range(self.n), key=lambda i: self.valores[i] / self.pesos[i], reverse=True)
        objetos, peso = [], 0
        for i in orden:
            if peso + self.pesos[i] <= self.capacidad:
                objetos.append(i)
                peso += self.pesos[i]
        return self._solucion(objetos)

    def optimos_alternativos(self, valor_optimo: float) -> List[SolucionMochila]:
        """Todas las combinaciones que alcanzan el valor optimo (enumeracion)."""
        if self.n > MAX_OBJETOS_ENUMERACION:
            return []
        res = []
        for k in range(self.n + 1):
            for comb in combinations(range(self.n), k):
                s = self._solucion(comb)
                if s.peso <= self.capacidad and abs(s.valor - valor_optimo) < 1e-9:
                    res.append(s)
        return sorted(res, key=lambda s: s.peso)
