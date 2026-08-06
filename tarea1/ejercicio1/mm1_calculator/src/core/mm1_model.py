from dataclasses import dataclass

from src.core.mmc_model import MMCModel
from src.utils.validators import validate_stable_system


@dataclass
class MM1Model(MMCModel):
    """Modelo M/M/1 para cálculos de teoría de colas."""

    servers: int = 1

    def __post_init__(self):
        super().__post_init__()
        validate_stable_system(self.lamb, self.mu, self.servers)

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
        # Tiempo promedio en el sistema
        return 1.0 / (self.mu - self.lamb)

    @property
    def wq(self) -> float:
        # Tiempo promedio en la cola
        return self.lamb / (self.mu * (self.mu - self.lamb))

    def prob_more_than(self, k: int) -> float:
        """P(n > k) para M/M/1: rho^(k+1)"""
        if k < 0:
            raise ValueError('k must be non-negative')
        return self.rho ** (k + 1)
