from dataclasses import dataclass
from math import factorial

from src.utils.validators import validate_positive_rate, validate_servers, validate_stable_system


@dataclass
class MMCModel:
    """Modelo M/M/c para cálculos de teoría de colas."""

    lamb: float
    mu: float
    servers: int = 1

    def __post_init__(self):
        validate_positive_rate(self.lamb, 'lambda')
        validate_positive_rate(self.mu, 'mu')
        validate_servers(self.servers)
        validate_stable_system(self.lamb, self.mu, self.servers)

    @property
    def rho(self) -> float:
        return self.lamb / (self.servers * self.mu)

    @property
    def a(self) -> float:
        return self.lamb / self.mu

    @property
    def p0(self) -> float:
        summation = sum((self.a ** n) / factorial(n) for n in range(self.servers))
        tail = (self.a ** self.servers) / factorial(self.servers) * (1.0 / (1.0 - self.rho))
        return 1.0 / (summation + tail)

    @property
    def lq(self) -> float:
        numerator = self.p0 * (self.a ** self.servers) * self.rho
        denominator = factorial(self.servers) * ((1.0 - self.rho) ** 2)
        return numerator / denominator

    @property
    def wq(self) -> float:
        return self.lq / self.lamb

    @property
    def w(self) -> float:
        return self.wq + (1.0 / self.mu)

    @property
    def l(self) -> float:
        return self.lq + (self.lamb / self.mu)

    @property
    def pw(self) -> float:
        return ((self.a ** self.servers) / factorial(self.servers)) * (1.0 / (1.0 - self.rho)) * self.p0
