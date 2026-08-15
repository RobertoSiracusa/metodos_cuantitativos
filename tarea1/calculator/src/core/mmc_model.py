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

    def steps(self) -> list:
        """Desarrollo paso a paso: rho, a, P0, Lq, L, Wq, W, Pw."""
        lamb, mu, c = self.lamb, self.mu, self.servers
        rho, a, p0, lq, l, wq, w, pw = (
            self.rho, self.a, self.p0, self.lq, self.l, self.wq, self.w, self.pw
        )
        summation = sum((a ** n) / factorial(n) for n in range(c))
        tail = (a ** c) / factorial(c) * (1.0 / (1.0 - rho))
        return [
            (
                'Factor de utilizacion (rho)',
                'rho = lambda / (c * mu)',
                f'rho = {lamb:.4f} / ({c} * {mu:.4f})',
                f'rho = {rho:.6f}',
            ),
            (
                'Intensidad de trafico (a)',
                'a = lambda / mu',
                f'a = {lamb:.4f} / {mu:.4f}',
                f'a = {a:.6f}',
            ),
            (
                'Probabilidad de sistema vacio (P0)',
                'P0 = [ sum_{n=0}^{c-1} a^n/n! + (a^c/c!) * (1/(1-rho)) ]^-1',
                f'P0 = [ {summation:.4f} + {tail:.4f} ]^-1',
                f'P0 = {p0:.6f}',
            ),
            (
                'Numero esperado en cola (Lq)',
                'Lq = (P0 * a^c * rho) / (c! * (1-rho)^2)',
                f'Lq = ({p0:.4f} * {a:.4f}^{c} * {rho:.4f}) / ({factorial(c)} * (1-{rho:.4f})^2)',
                f'Lq = {lq:.6f}',
            ),
            (
                'Numero esperado en sistema (L)',
                'L = Lq + a',
                f'L = {lq:.4f} + {a:.4f}',
                f'L = {l:.6f}',
            ),
            (
                'Tiempo promedio en cola (Wq)',
                'Wq = Lq / lambda',
                f'Wq = {lq:.4f} / {lamb:.4f}',
                f'Wq = {wq:.6f}',
            ),
            (
                'Tiempo promedio en sistema (W)',
                'W = Wq + 1/mu',
                f'W = {wq:.4f} + 1/{mu:.4f}',
                f'W = {w:.6f}',
            ),
            (
                'Probabilidad de esperar (Pw)',
                'Pw = (a^c/c!) * (1/(1-rho)) * P0',
                f'Pw = ({a:.4f}^{c}/{factorial(c)}) * (1/(1-{rho:.4f})) * {p0:.4f}',
                f'Pw = {pw:.6f}',
            ),
        ]

    def steps_note(self):
        return None
