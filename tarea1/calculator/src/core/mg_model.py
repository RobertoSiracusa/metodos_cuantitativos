from dataclasses import dataclass
from math import factorial

from src.core.mmc_model import MMCModel


@dataclass
class MGCModel(MMCModel):
    """Modelo M/G/c: llegadas Poisson, servicio con distribución general.

    `sigma` es la desviación estándar del tiempo de servicio (en unidades de
    tiempo, no de tasa). Con sigma = 1/mu se recupera M/M/c; con sigma = 0 se
    recupera M/D/c (servicio determinístico).
    """

    sigma: float = 0.0

    # Erlang-C (pw) asume servicio exponencial: no aplica a servicio general
    supports_pw = False

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.sigma, (int, float)):
            raise TypeError('sigma must be a number')
        if self.sigma < 0:
            raise ValueError('sigma must be non-negative')

    @property
    def scv(self) -> float:
        """Coeficiente de variación al cuadrado del tiempo de servicio."""
        return (self.sigma * self.mu) ** 2

    @property
    def lq(self) -> float:
        if self.servers == 1:
            # Pollaczek-Khinchine (exacto para M/G/1)
            return ((self.lamb ** 2) * (self.sigma ** 2) + self.rho ** 2) / (2.0 * (1.0 - self.rho))
        # ponytail: Allen-Cunneen. Aproximación, no fórmula cerrada exacta;
        # M/G/c no la tiene. Error típico < 5% con rho alto.
        return MMCModel.lq.fget(self) * (1.0 + self.scv) / 2.0

    @property
    def p0(self) -> float:
        if self.servers == 1:
            return 1.0 - self.rho
        return MMCModel.p0.fget(self)

    @property
    def is_exact(self) -> bool:
        return self.servers == 1

    def _lq_step_g1(self):
        """Paso de Lq para el caso M/G/1 (Pollaczek-Khinchine exacto)."""
        lamb, sigma, rho, lq = self.lamb, self.sigma, self.rho, self.lq
        return (
            'Numero esperado en cola (Lq)',
            'Lq = (lambda^2 * sigma^2 + rho^2) / (2 * (1 - rho))',
            f'Lq = ({lamb:.4f}^2 * {sigma:.4f}^2 + {rho:.4f}^2) / (2 * (1 - {rho:.4f}))',
            f'Lq = {lq:.6f}',
        )

    def _lq_step_gc(self, mmc_lq):
        """Paso de Lq para el caso M/G/c (aproximacion Allen-Cunneen)."""
        scv, lq = self.scv, self.lq
        return (
            'Numero esperado en cola (Lq)',
            'Lq = Lq(M/M/c) * (1 + Cs^2) / 2',
            f'Lq = {mmc_lq:.4f} * (1 + {scv:.4f}) / 2',
            f'Lq = {lq:.6f}',
        )

    def steps(self) -> list:
        """Desarrollo paso a paso. M/G/1: rho,P0,Lq,L,Wq,W. M/G/c: rho,a,Cs^2,P0,Lq(M/M/c),Lq,L,Wq,W."""
        lamb, mu, rho, p0, l, wq, w = (
            self.lamb, self.mu, self.rho, self.p0, self.l, self.wq, self.w
        )

        if self.servers == 1:
            return [
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
                self._lq_step_g1(),
                (
                    'Numero esperado en sistema (L)',
                    'L = Lq + rho',
                    f'L = {self.lq:.4f} + {rho:.4f}',
                    f'L = {l:.6f}',
                ),
                (
                    'Tiempo promedio en cola (Wq)',
                    'Wq = Lq / lambda',
                    f'Wq = {self.lq:.4f} / {lamb:.4f}',
                    f'Wq = {wq:.6f}',
                ),
                (
                    'Tiempo promedio en sistema (W)',
                    'W = Wq + 1/mu',
                    f'W = {wq:.4f} + 1/{mu:.4f}',
                    f'W = {w:.6f}',
                ),
            ]

        c = self.servers
        a, sigma, scv = self.a, self.sigma, self.scv
        mmc = MMCModel(lamb=lamb, mu=mu, servers=c)
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
                'Coeficiente de variacion al cuadrado (Cs^2)',
                'Cs^2 = (sigma * mu)^2',
                f'Cs^2 = ({sigma:.4f} * {mu:.4f})^2',
                f'Cs^2 = {scv:.6f}',
            ),
            (
                'Probabilidad de sistema vacio (P0)',
                'P0 = [ sum_{n=0}^{c-1} a^n/n! + (a^c/c!) * (1/(1-rho)) ]^-1',
                f'P0 = [ {summation:.4f} + {tail:.4f} ]^-1',
                f'P0 = {p0:.6f}',
            ),
            (
                'Numero esperado en cola equivalente M/M/c (Lq(M/M/c))',
                'Lq(M/M/c) = (P0 * a^c * rho) / (c! * (1-rho)^2)',
                f'Lq(M/M/c) = ({p0:.4f} * {a:.4f}^{c} * {rho:.4f}) / ({factorial(c)} * (1-{rho:.4f})^2)',
                f'Lq(M/M/c) = {mmc.lq:.6f}',
            ),
            self._lq_step_gc(mmc.lq),
            (
                'Numero esperado en sistema (L)',
                'L = Lq + a',
                f'L = {self.lq:.4f} + {a:.4f}',
                f'L = {l:.6f}',
            ),
            (
                'Tiempo promedio en cola (Wq)',
                'Wq = Lq / lambda',
                f'Wq = {self.lq:.4f} / {lamb:.4f}',
                f'Wq = {wq:.6f}',
            ),
            (
                'Tiempo promedio en sistema (W)',
                'W = Wq + 1/mu',
                f'W = {wq:.4f} + 1/{mu:.4f}',
                f'W = {w:.6f}',
            ),
        ]

    def steps_note(self):
        if self.servers > 1:
            return 'Nota: M/G/c no tiene formula cerrada exacta. Se usa la aproximacion de Allen-Cunneen.'
        return None


@dataclass
class MG1Model(MGCModel):
    """M/G/1 exacto (Pollaczek-Khinchine)."""

    servers: int = 1


@dataclass
class MDCModel(MGCModel):
    """M/D/c: servicio determinístico (sigma = 0)."""

    sigma: float = 0.0

    def __post_init__(self):
        self.sigma = 0.0
        super().__post_init__()

    def _lq_step_gc(self, mmc_lq):
        """M/D/c: Cs^2 = 0, por lo que Lq = Lq(M/M/c) / 2."""
        lq = self.lq
        return (
            'Numero esperado en cola (Lq)',
            'Lq = Lq(M/M/c) / 2',
            f'Lq = {mmc_lq:.4f} / 2',
            f'Lq = {lq:.6f}',
        )


@dataclass
class MD1Model(MDCModel):
    """M/D/1: caso exacto, Lq = rho^2 / (2(1-rho))."""

    servers: int = 1

    def _lq_step_g1(self):
        """M/D/1: caso sigma = 0 de P-K, Lq = rho^2 / (2(1-rho))."""
        rho, lq = self.rho, self.lq
        return (
            'Numero esperado en cola (Lq)',
            'Lq = rho^2 / (2 * (1 - rho))',
            f'Lq = {rho:.4f}^2 / (2 * (1 - {rho:.4f}))  [P-K con sigma = 0]',
            f'Lq = {lq:.6f}',
        )
