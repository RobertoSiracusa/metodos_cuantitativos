"""Reparto del presupuesto electrico entre clusteres con multiplicadores de Lagrange (R5)."""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.core.no_lineal.base import EntradaOptimizacion, Optimizador
from src.utils.validators import ErrorValidacion, Validador


@dataclass(frozen=True)
class ResultadoLagrange:
    """Energia asignada a cada cluster, el multiplicador lambda y el rendimiento total R."""

    asignacion: dict[str, float]
    lambda_: float
    rendimiento: float


class AsignadorLagrange(Optimizador):
    """Maximiza R(E_1..E_n) = sum w_i ln(1 + E_i)  sujeto a  sum E_i = E_max,  E_i >= 0.

    Lagrangiano: L = sum w_i ln(1 + E_i) - lambda (sum E_i - E_max)
        dL/dE_i = w_i / (1 + E_i) - lambda = 0   ->  E_i = w_i / lambda - 1
        sum E_i = E_max                           ->  lambda = sum w_i / (E_max + n)

    Si algun E_i sale negativo (cluster con poca demanda) se fija E_i = 0 y se vuelve a
    resolver con los clusteres restantes: es la condicion de holgura complementaria de
    KKT. Quitar un cluster asi solo hace crecer lambda, asi que los ya excluidos nunca
    vuelven a ser positivos y el ciclo termina en a lo sumo n vueltas.

    w_i es la demanda actual de cada cluster, que actualiza el motor SimPy en cada tick.
    """

    def __init__(self, e_max: float = 100.0) -> None:
        super().__init__()
        self._e_max = Validador.validar_rango("e_max", e_max, minimo=0)
        self._lambda = 0.0

    @property
    def e_max(self) -> float:
        return self._e_max

    @property
    def lambda_actual(self) -> float:
        return self._lambda

    @staticmethod
    def resolver(demandas: dict[str, float], e_max: float) -> ResultadoLagrange:
        """Resuelve el reparto para unas demandas dadas (metodo puro, sin estado)."""
        if not demandas:
            raise ErrorValidacion("se necesita al menos un cluster para repartir la energia")
        e_max = Validador.validar_rango("e_max", e_max, minimo=0)
        pesos = {cid: Validador.validar_rango(f"demanda de {cid}", w, minimo=0) for cid, w in demandas.items()}

        if sum(pesos.values()) == 0:
            # sin demanda el rendimiento es 0 para cualquier reparto: se divide en partes iguales
            parte = e_max / len(pesos)
            return ResultadoLagrange({cid: parte for cid in pesos}, 0.0, 0.0)

        activos = {cid for cid, w in pesos.items() if w > 0}
        while True:
            lam = sum(pesos[c] for c in activos) / (e_max + len(activos))
            negativos = {c for c in activos if pesos[c] / lam - 1 < 0}
            if not negativos:
                break
            activos -= negativos

        asignacion = {cid: (pesos[cid] / lam - 1 if cid in activos else 0.0) for cid in pesos}
        rendimiento = sum(w * math.log(1 + asignacion[cid]) for cid, w in pesos.items())
        return ResultadoLagrange(asignacion, lam, rendimiento)

    def _paso(self, entrada: EntradaOptimizacion) -> dict[str, float]:
        resultado = self.resolver(entrada.demandas, self._e_max)
        self._lambda = resultado.lambda_
        valores = {"lambda": resultado.lambda_, "rendimiento": resultado.rendimiento}
        valores.update({f"E_{cid}": e for cid, e in resultado.asignacion.items()})
        return valores
