from dataclasses import dataclass
from typing import Union
from src.utils.validators import validate_positive_rate, validate_stable_system


@dataclass
class MM1Model:
    """Modelo M/M/1 para cálculos de teoría de colas."""
    lamb: float
    mu: float

    def __post_init__(self):
        validate_positive_rate(self.lamb, 'lambda')
        validate_positive_rate(self.mu, 'mu')
        validate_stable_system(self.lamb, self.mu)

    @property
    def rho(self) -> float:
        return self.lamb / self.mu

    @property
    def p0(self) -> float:
        # Probabilidad de servidor ocioso
        return 1.0 - self.rho

    @property
    def l(self) -> float:
        # Número esperado en el sistema
        return self.rho / (1.0 - self.rho)

    @property
    def lq(self) -> float:
        # Número esperado en la cola
        return (self.rho ** 2) / (1.0 - self.rho)

    @property
    def w(self) -> float:
        # Tiempo promedio en el sistema (minutos)
        return 1.0 / (self.mu - self.lamb)

    @property
    def wq(self) -> float:
        # Tiempo promedio en la cola (minutos)
        return self.lamb / (self.mu * (self.mu - self.lamb))

    def prob_more_than(self, k: int) -> float:
        """P(n > k) para M/M/1: rho^(k+1)"""
        if k < 0:
            raise ValueError('k must be non-negative')
        return self.rho ** (k + 1)
