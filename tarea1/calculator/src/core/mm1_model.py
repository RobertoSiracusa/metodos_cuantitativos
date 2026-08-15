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

    def steps(self, k=None) -> list:
        """Desarrollo paso a paso: rho, P0, L, Lq, W, Wq y P(n>k) si se pide k."""
        lamb, mu = self.lamb, self.mu
        rho, p0, l, lq, w, wq = self.rho, self.p0, self.l, self.lq, self.w, self.wq
        result = [
            (
                'Factor de utilizacion (rho)',
                'rho = lambda / mu',
                f'rho = {lamb:.4f} / {mu:.4f}',
                f'rho = {rho:.6f}',
            ),
            (
                'Probabilidad de sistema vacio (P0)',
                'P0 = 1 - rho',
                f'P0 = 1 - {rho:.4f}',
                f'P0 = {p0:.6f}',
            ),
            (
                'Numero esperado en sistema (L)',
                'L = rho / (1 - rho)',
                f'L = {rho:.4f} / (1 - {rho:.4f})',
                f'L = {l:.6f}',
            ),
            (
                'Numero esperado en cola (Lq)',
                'Lq = rho^2 / (1 - rho)',
                f'Lq = {rho:.4f}^2 / (1 - {rho:.4f})',
                f'Lq = {lq:.6f}',
            ),
            (
                'Tiempo promedio en sistema (W)',
                'W = 1 / (mu - lambda)',
                f'W = 1 / ({mu:.4f} - {lamb:.4f})',
                f'W = {w:.6f}',
            ),
            (
                'Tiempo promedio en cola (Wq)',
                'Wq = lambda / (mu * (mu - lambda))',
                f'Wq = {lamb:.4f} / ({mu:.4f} * ({mu:.4f} - {lamb:.4f}))',
                f'Wq = {wq:.6f}',
            ),
        ]
        if k is not None:
            value = self.prob_more_than(k)
            result.append((
                f'Probabilidad de mas de {k} clientes (P(n>{k}))',
                'P(n > k) = rho^(k+1)',
                f'P(n > {k}) = {rho:.4f}^{k + 1}',
                f'P(n > {k}) = {value:.6f}',
            ))
        return result

    def steps_note(self):
        return None
