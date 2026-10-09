"""
Problema de Volumen de Carga (mochila 0/1 resuelta por etapas)
Capa de Modelo Cuantitativo — Metodos Cuantitativos
Universidad Jose Antonio Paez

    Max Z = sum_i ri * mi
    s.a. sum_i wi * mi <= W
         mi en {0, 1}

Se resuelve por programacion dinamica (propia), etapa por etapa, con una etapa
por producto i = 1..n (en el orden del JSON) y estado y = capacidad disponible
(0..W):

    f_0(y) = 0
    f_i(y) = max{ f_{i-1}(y) ,                      (mi = 0, no se lleva)
                  ri + f_{i-1}(y - wi)  si wi <= y } (mi = 1, se lleva)

En caso de empate entre mi = 0 y mi = 1, se elige mi = 0 (no llevarlo). Se
verifica el optimo con scipy.milp y se compara contra una heuristica voraz
(mayor precio/kg) y contra la enumeracion completa de las 2**n combinaciones.
"""

from dataclasses import dataclass
from itertools import combinations
from typing import List, Optional

from scipy.optimize import Bounds, LinearConstraint, milp

MAX_PRODUCTOS_ENUMERACION = 20


@dataclass
class FilaEtapa:
    y: int
    sin_producto: float            # f_{i-1}(y)                    -> valor si mi = 0
    con_producto: Optional[float]  # ri + f_{i-1}(y - wi), o None si wi > y (no entra)
    f: float                       # f_i(y) = max(sin_producto, con_producto)
    decision: int                  # mi* en {0, 1} para este y


@dataclass
class SolucionCarga:
    productos: List[int]   # indices 0-based de los productos que se llevan
    peso: int
    valor: float
    libre: int              # capacidad - peso


@dataclass
class Combinacion:
    productos: List[int]
    peso: int
    valor: float
    factible: bool


class VolumenCarga:
    def __init__(self, nombres: List[str], pesos: List[int], precios: List[float], capacidad: int):
        if not (len(nombres) == len(pesos) == len(precios)):
            raise ValueError("nombres, pesos y precios deben tener el mismo largo.")
        if not nombres:
            raise ValueError("Debe haber al menos un producto.")
        if any(not str(nom).strip() for nom in nombres):
            raise ValueError("Los nombres de los productos no pueden ser vacios.")
        if any(isinstance(w, bool) or int(w) != w or w <= 0 for w in pesos):
            raise ValueError("Los pesos deben ser enteros positivos (sin bool, sin decimales).")
        if any(isinstance(p, bool) or p < 0 for p in precios):
            raise ValueError("Los precios deben ser numericos y no negativos.")
        if isinstance(capacidad, bool) or int(capacidad) != capacidad or capacidad < 0:
            raise ValueError("La capacidad debe ser un entero mayor o igual a 0 (sin bool, sin decimales).")

        self.nombres = [str(nom) for nom in nombres]
        self.pesos = [int(w) for w in pesos]
        self.precios = [float(p) for p in precios]
        self.capacidad = int(capacidad)
        self.n = len(nombres)

    def tablas_etapas(self) -> List[List[FilaEtapa]]:
        """
        Arma, etapa por etapa, la tabla de programacion dinamica del modelo:

            f_0(y) = 0
            f_i(y) = max{ f_{i-1}(y) , ri + f_{i-1}(y - wi)  si wi <= y }

        Devuelve una lista de n etapas (una por producto, en el orden del JSON);
        cada etapa es una lista de FilaEtapa para y = 0..capacidad.
        """
        W = self.capacidad
        f_prev = [0.0] * (W + 1)  # f_0
        etapas = []
        for i in range(self.n):
            w, r = self.pesos[i], self.precios[i]
            f_actual = [0.0] * (W + 1)
            filas = []
            for y in range(W + 1):
                sin_producto = f_prev[y]
                con_producto = r + f_prev[y - w] if w <= y else None
                if con_producto is not None and con_producto > sin_producto:
                    f_val, decision = con_producto, 1
                else:
                    f_val, decision = sin_producto, 0
                f_actual[y] = f_val
                filas.append(FilaEtapa(y, sin_producto, con_producto, f_val, decision))
            etapas.append(filas)
            f_prev = f_actual
        return etapas

    def resolver(self) -> SolucionCarga:
        """Reconstruccion hacia atras desde y = capacidad en la etapa n."""
        etapas = self.tablas_etapas()
        y = self.capacidad
        productos = []
        for i in range(self.n - 1, -1, -1):
            fila = etapas[i][y]
            if fila.decision == 1:
                productos.append(i)
                y -= self.pesos[i]
        productos.reverse()
        valor = etapas[-1][self.capacidad].f
        peso = sum(self.pesos[i] for i in productos)
        return SolucionCarga(productos, peso, valor, self.capacidad - peso)

    def resolver_milp(self) -> SolucionCarga:
        """Verificacion del optimo con scipy.optimize.milp (variables binarias)."""
        r = milp(
            c=[-p for p in self.precios],
            constraints=LinearConstraint([self.pesos], ub=self.capacidad),
            integrality=[1] * self.n,
            bounds=Bounds(0, 1),
        )
        if r.status != 0:
            raise RuntimeError(f"El solver no encontro solucion: {r.message}")
        productos = [i for i in range(self.n) if r.x[i] > 0.5]
        peso = sum(self.pesos[i] for i in productos)
        valor = sum(self.precios[i] for i in productos)
        return SolucionCarga(productos, peso, valor, self.capacidad - peso)

    def resolver_voraz(self) -> SolucionCarga:
        """Heuristica: agrega productos por mayor precio/kg mientras quepan."""
        orden = sorted(range(self.n), key=lambda i: self.precios[i] / self.pesos[i], reverse=True)
        productos, peso = [], 0
        for i in orden:
            if peso + self.pesos[i] <= self.capacidad:
                productos.append(i)
                peso += self.pesos[i]
        productos.sort()
        valor = sum(self.precios[i] for i in productos)
        return SolucionCarga(productos, peso, valor, self.capacidad - peso)

    def enumerar(self) -> List[Combinacion]:
        """Enumera las 2**n combinaciones posibles (maximo 20 productos)."""
        if self.n > MAX_PRODUCTOS_ENUMERACION:
            raise ValueError(f"enumerar() soporta hasta {MAX_PRODUCTOS_ENUMERACION} productos.")
        combinaciones = []
        for k in range(self.n + 1):
            for comb in combinations(range(self.n), k):
                peso = sum(self.pesos[i] for i in comb)
                valor = sum(self.precios[i] for i in comb)
                combinaciones.append(Combinacion(list(comb), peso, valor, peso <= self.capacidad))
        return combinaciones

    def optimos_alternativos(self) -> List[Combinacion]:
        """Combinaciones factibles (de enumerar()) que alcanzan el valor de resolver()."""
        valor_optimo = self.resolver().valor
        return [
            c for c in self.enumerar()
            if c.factible and abs(c.valor - valor_optimo) < 1e-9
        ]
