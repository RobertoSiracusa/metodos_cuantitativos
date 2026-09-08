"""Modelo matematico analitico M/M/c para comparacion con la simulacion SimPy."""

from math import factorial
from typing import Dict, Any, Optional


class MMCAnalytical:
    """Calculadora teorica analitica para el sistema de colas M/M/c (Kendall)."""

    def __init__(self, lamb: float, mu: float, c: int):
        """
        Inicializa parametros de tasas y servidores.
        lamb: Tasa de llegada (vehiculos/unidad de tiempo)
        mu: Tasa de servicio por servidor (vehiculos/unidad de tiempo)
        c: Cantidad de servidores paralelos (bombas)
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
        """Determina si el sistema alcanza estado estable estocastico (rho < 1)."""
        return self.rho < 1.0

    @property
    def p0(self) -> float:
        """Probabilidad de que el sistema este completamente vacio."""
        if not self.is_stable:
            return 0.0
        summation = sum((self.a ** n) / factorial(n) for n in range(self.c))
        tail = ((self.a ** self.c) / factorial(self.c)) * (1.0 / (1.0 - self.rho))
        total = summation + tail
        return 1.0 / total if total > 0 else 0.0

    @property
    def lq(self) -> float:
        """Numero promedio esperado de vehiculos esperando en la cola."""
        if not self.is_stable:
            return float('inf')
        numerator = self.p0 * (self.a ** self.c) * self.rho
        denominator = factorial(self.c) * ((1.0 - self.rho) ** 2)
        return numerator / denominator if denominator > 0 else 0.0

    @property
    def wq(self) -> float:
        """Tiempo promedio esperado en cola (espera): Wq = Lq / lambda."""
        if not self.is_stable or self.lamb <= 0:
            return float('inf')
        return self.lq / self.lamb

    @property
    def w(self) -> float:
        """Tiempo promedio esperado en todo el sistema (espera + servicio): W = Wq + 1/mu."""
        if not self.is_stable or self.mu <= 0:
            return float('inf')
        return self.wq + (1.0 / self.mu)

    @property
    def l(self) -> float:
        """Numero promedio esperado de vehiculos en el sistema (cola + bombas): L = lambda * W."""
        if not self.is_stable:
            return float('inf')
        return self.lq + self.a

    @property
    def pw(self) -> float:
        """Probabilidad de demora de Erlang-C (probabilidad de que deba esperar en cola)."""
        if not self.is_stable:
            return 1.0
        return ((self.a ** self.c) / factorial(self.c)) * (1.0 / (1.0 - self.rho)) * self.p0

    def get_summary(self) -> Dict[str, Any]:
        """Devuelve diccionario consolidado con todas las metricas analiticas."""
        stable = self.is_stable
        return {
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
