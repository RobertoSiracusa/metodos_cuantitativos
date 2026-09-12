"""
Modelo M/M/1 analitico: formulas cerradas de teoria de colas.

Sirve de contraste teorico para la simulacion de eventos discretos del
Problema 1. Con lambda = 10 ordenes/h y mu = 12 laptops/h los valores esperados
son rho = 0.833333, P0 = 0.166667, L = 5.0, Lq = 4.166667, W = 0.5 h (30 min)
y Wq = 0.416667 h (25 min).
"""

from dataclasses import dataclass
from typing import Dict

from src.utils.validators import ValidacionError, validar_sistema_estable


@dataclass
class ModeloMM1:
    """
    Cola M/M/1: llegadas Poisson, servicio exponencial, un solo servidor,
    disciplina FIFO y capacidad infinita.

    lamb y mu deben expresarse en la MISMA unidad de tiempo. En este proyecto
    se usan unidades por hora.
    """

    lamb: float
    mu: float
    servidores: int = 1

    def __post_init__(self) -> None:
        # Validacion al borde: un sistema inestable produce L y W negativos,
        # que es peor que fallar de una.
        validar_sistema_estable(self.lamb, self.mu, self.servidores)

    @property
    def rho(self) -> float:
        """Factor de utilizacion del servidor: rho = lambda / mu."""
        return self.lamb / self.mu

    @property
    def p0(self) -> float:
        """Probabilidad de sistema vacio: P0 = 1 - rho."""
        return 1.0 - self.rho

    @property
    def l(self) -> float:
        """Numero esperado de ordenes en el sistema: L = rho / (1 - rho)."""
        return self.rho / (1.0 - self.rho)

    @property
    def lq(self) -> float:
        """Numero esperado de ordenes en cola: Lq = rho^2 / (1 - rho)."""
        return (self.rho ** 2) / (1.0 - self.rho)

    @property
    def w(self) -> float:
        """Tiempo promedio en el sistema: W = 1 / (mu - lambda)."""
        return 1.0 / (self.mu - self.lamb)

    @property
    def wq(self) -> float:
        """Tiempo promedio en cola: Wq = lambda / (mu * (mu - lambda))."""
        return self.lamb / (self.mu * (self.mu - self.lamb))

    def probabilidad_n(self, n: int) -> float:
        """Probabilidad de encontrar exactamente n ordenes: Pn = (1 - rho) * rho^n."""
        if n < 0:
            raise ValidacionError(f"n debe ser mayor o igual a 0. Recibido: {n}.")
        return (1.0 - self.rho) * (self.rho ** n)

    def probabilidad_mas_de(self, k: int) -> float:
        """Probabilidad de que haya mas de k ordenes: P(n > k) = rho^(k+1)."""
        if k < 0:
            raise ValidacionError(f"k debe ser mayor o igual a 0. Recibido: {k}.")
        return self.rho ** (k + 1)

    def resumen(self) -> Dict[str, float]:
        """Diccionario con todos los indicadores cerrados, listo para el reporte."""
        return {
            "lambda": self.lamb,
            "mu": self.mu,
            "rho": self.rho,
            "p0": self.p0,
            "l": self.l,
            "lq": self.lq,
            "w_horas": self.w,
            "wq_horas": self.wq,
            "w_min": self.w * 60.0,
            "wq_min": self.wq * 60.0,
        }

    def pasos_desarrollados(self) -> list:
        """Desarrollo paso a paso de cada formula, para el reporte impreso."""
        return [
            ("Factor de utilizacion", "rho = lambda / mu",
             f"rho = {self.lamb:.4f} / {self.mu:.4f}", f"rho = {self.rho:.6f}"),
            ("Probabilidad de sistema vacio", "P0 = 1 - rho",
             f"P0 = 1 - {self.rho:.6f}", f"P0 = {self.p0:.6f}"),
            ("Ordenes esperadas en el sistema", "L = rho / (1 - rho)",
             f"L = {self.rho:.6f} / (1 - {self.rho:.6f})", f"L = {self.l:.6f}"),
            ("Ordenes esperadas en cola", "Lq = rho^2 / (1 - rho)",
             f"Lq = {self.rho:.6f}^2 / (1 - {self.rho:.6f})", f"Lq = {self.lq:.6f}"),
            ("Tiempo promedio en el sistema", "W = 1 / (mu - lambda)",
             f"W = 1 / ({self.mu:.4f} - {self.lamb:.4f})",
             f"W = {self.w:.6f} h = {self.w * 60.0:.4f} min"),
            ("Tiempo promedio en cola", "Wq = lambda / (mu * (mu - lambda))",
             f"Wq = {self.lamb:.4f} / ({self.mu:.4f} * ({self.mu:.4f} - {self.lamb:.4f}))",
             f"Wq = {self.wq:.6f} h = {self.wq * 60.0:.4f} min"),
        ]


def _selfcheck() -> None:
    """Contrasta el modelo contra los valores cerrados del enunciado."""
    m = ModeloMM1(lamb=10.0, mu=12.0)
    assert abs(m.rho - 0.833333) < 1e-6, m.rho
    assert abs(m.p0 - 0.166667) < 1e-6, m.p0
    assert abs(m.l - 5.0) < 1e-9, m.l
    assert abs(m.lq - 4.166667) < 1e-6, m.lq
    assert abs(m.w - 0.5) < 1e-9, m.w
    assert abs(m.wq - 0.416667) < 1e-6, m.wq
    assert abs(m.w * 60.0 - 30.0) < 1e-9
    assert abs(m.wq * 60.0 - 25.0) < 1e-4
    # Ley de Little: L = lambda * W  y  Lq = lambda * Wq
    assert abs(m.l - m.lamb * m.w) < 1e-9
    assert abs(m.lq - m.lamb * m.wq) < 1e-9
    # La distribucion de estado debe sumar 1 al truncarla lejos
    total = sum(m.probabilidad_n(n) for n in range(0, 400))
    assert abs(total - 1.0) < 1e-6, total
    print("selfcheck mm1_analytical: OK")


if __name__ == "__main__":
    _selfcheck()
