"""Modelos matematicos cuantitativos de teoria de colas para el automercado.

Implementa los modelos analiticos exactos:
1. M/M/c: Sistema multi-servidor con cola unica compartida (disciplina bancaria/centralizada).
2. c x M/M/1: Sistema de multiples servidores con colas individuales paralelas independientes.
Permite contrastar ambas disciplinas teoricas contra los datos empiricos de la simulacion.
"""

from math import factorial
from typing import Dict, Any


class MMCAnalytical:
    """Calculadora cuantitativa analitica para el sistema de colas M/M/c (Kendall)."""

    def __init__(self, lamb: float, mu: float, c: int):
        """
        lamb: Tasa global de arribos (clientes por unidad de tiempo, ej. min).
        mu: Tasa de servicio por caja (clientes por unidad de tiempo).
        c: Cantidad de cajas registradoras activas en paralelo.
        """
        self.lamb = float(lamb)
        self.mu = float(mu)
        self.c = int(c)

    @property
    def a(self) -> float:
        """Intensidad de trafico ofrecida (Erlangs): a = lambda / mu."""
        return self.lamb / self.mu if self.mu > 0 else 0.0

    @property
    def rho(self) -> float:
        """Factor de utilizacion promedio por servidor: rho = lambda / (c * mu)."""
        if self.c <= 0 or self.mu <= 0:
            return 0.0
        return self.lamb / (self.c * self.mu)

    @property
    def is_stable(self) -> bool:
        """Condicion estocastica de estabilidad en estado estacionario (rho < 1)."""
        return self.rho < 1.0

    @property
    def p0(self) -> float:
        """Probabilidad de que todo el automercado este desocupado (sin clientes)."""
        if not self.is_stable:
            return 0.0
        summation = sum((self.a ** n) / factorial(n) for n in range(self.c))
        tail = ((self.a ** self.c) / factorial(self.c)) * (1.0 / (1.0 - self.rho))
        total = summation + tail
        return 1.0 / total if total > 0 else 0.0

    @property
    def lq(self) -> float:
        """Numero esperado de clientes esperando en cola unica (Lq)."""
        if not self.is_stable:
            return float("inf")
        numerator = self.p0 * (self.a ** self.c) * self.rho
        denominator = factorial(self.c) * ((1.0 - self.rho) ** 2)
        return numerator / denominator if denominator > 0 else 0.0

    @property
    def wq(self) -> float:
        """Tiempo promedio esperado en cola antes de ser atendido: Wq = Lq / lambda."""
        if not self.is_stable or self.lamb <= 0:
            return float("inf")
        return self.lq / self.lamb

    @property
    def w(self) -> float:
        """Tiempo promedio total de permanencia en el sistema: W = Wq + 1/mu."""
        if not self.is_stable or self.mu <= 0:
            return float("inf")
        return self.wq + (1.0 / self.mu)

    @property
    def l(self) -> float:
        """Numero promedio de clientes en el sistema (cola + siendo atendidos): L = lambda * W."""
        if not self.is_stable:
            return float("inf")
        return self.lq + self.a

    @property
    def pw(self) -> float:
        """Probabilidad de espera de Erlang-C (probabilidad de encontrar todas las cajas ocupadas)."""
        if not self.is_stable:
            return 1.0
        return ((self.a ** self.c) / factorial(self.c)) * (1.0 / (1.0 - self.rho)) * self.p0

    def get_summary(self) -> Dict[str, Any]:
        """Devuelve diccionario consolidado de metricas teoricas M/M/c."""
        stable = self.is_stable
        return {
            "disciplina": "Cola Unica M/M/c",
            "lambda": self.lamb,
            "mu": self.mu,
            "c": self.c,
            "rho": self.rho,
            "is_stable": stable,
            "P0": self.p0 if stable else 0.0,
            "Lq": self.lq if stable else -1.0,
            "L": self.l if stable else -1.0,
            "Wq": self.wq if stable else -1.0,
            "W": self.w if stable else -1.0,
            "Pw": self.pw if stable else 1.0,
        }


class ParallelMM1Analytical:
    """Calculadora analitica para red de c colas independientes M/M/1 en paralelo."""

    def __init__(self, lamb: float, mu: float, c: int):
        self.lamb = float(lamb)
        self.mu = float(mu)
        self.c = int(c)

    @property
    def lambda_per_queue(self) -> float:
        """Tasa media de arribos que recibe cada caja individual en equilibrio."""
        return self.lamb / self.c if self.c > 0 else 0.0

    @property
    def rho(self) -> float:
        """Utilizacion por caja: rho = (lambda / c) / mu."""
        if self.c <= 0 or self.mu <= 0:
            return 0.0
        return self.lambda_per_queue / self.mu

    @property
    def is_stable(self) -> bool:
        return self.rho < 1.0

    @property
    def p0(self) -> float:
        """Probabilidad de que todas las c cajas esten simultaneamente vacias."""
        if not self.is_stable:
            return 0.0
        # Probabilidad de vacio en cada cola independiente = (1 - rho)
        return (1.0 - self.rho) ** self.c

    @property
    def lq_single(self) -> float:
        """Clientes en cola en una sola caja individual."""
        if not self.is_stable:
            return float("inf")
        return (self.rho ** 2) / (1.0 - self.rho)

    @property
    def lq(self) -> float:
        """Total de clientes esperando en cola sumando todas las cajas."""
        if not self.is_stable:
            return float("inf")
        return self.c * self.lq_single

    @property
    def wq(self) -> float:
        """Tiempo promedio de espera en cola por cliente: Wq = Lq_total / lambda."""
        if not self.is_stable or self.mu <= 0:
            return float("inf")
        return self.rho / (self.mu * (1.0 - self.rho))

    @property
    def w(self) -> float:
        """Tiempo total promedio en el sistema: W = Wq + 1/mu."""
        if not self.is_stable or self.mu <= 0:
            return float("inf")
        return 1.0 / (self.mu * (1.0 - self.rho))

    @property
    def l(self) -> float:
        """Total de clientes en el sistema a traves de todas las cajas."""
        if not self.is_stable:
            return float("inf")
        return self.c * (self.rho / (1.0 - self.rho))

    def get_summary(self) -> Dict[str, Any]:
        """Devuelve diccionario consolidado de metricas teoricas c x M/M/1."""
        stable = self.is_stable
        return {
            "disciplina": "Colas Paralelas c x M/M/1",
            "lambda": self.lamb,
            "mu": self.mu,
            "c": self.c,
            "rho": self.rho,
            "is_stable": stable,
            "P0": self.p0 if stable else 0.0,
            "Lq": self.lq if stable else -1.0,
            "L": self.l if stable else -1.0,
            "Wq": self.wq if stable else -1.0,
            "W": self.w if stable else -1.0,
            "Pw": self.rho if stable else 1.0,
        }
