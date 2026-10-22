"""Metodo del gradiente para ajustar la velocidad de los ventiladores en tiempo real (R4)."""

from __future__ import annotations

from src.core.no_lineal.base import EntradaOptimizacion, Optimizador
from src.utils.validators import ErrorValidacion, Validador


class GradienteEnfriamiento(Optimizador):
    """Minimiza el consumo de refrigeracion E(v) con un paso de gradiente por tick.

        E(v)  = a v^3 + b Q / v
        E'(v) = 3a v^2 - b Q / v^2
        v <- v - alfa * E'(v),  acotado a [v_min, v_max]

    `a v^3` es la potencia del ventilador (ley de afinidad: crece con el cubo de la
    velocidad) y `b Q / v` penaliza el calor Q que no se extrae (a menor velocidad, mas
    calor queda en la sala). Q es la carga actual de los servidores (%).

    Igualando E'(v) = 0 se obtiene el optimo analitico v* = (b Q / 3a)^(1/4), que sirve
    para comprobar que el metodo iterativo converge al valor correcto.
    """

    def __init__(
        self,
        a: float = 1.0,
        b: float = 0.05,
        alfa: float = 0.05,
        v_inicial: float = 0.3,
        v_min: float = 0.1,
        v_max: float = 2.0,
    ) -> None:
        super().__init__()
        self._a = Validador.validar_rango("a", a, minimo=1e-9)
        self._b = Validador.validar_rango("b", b, minimo=1e-9)
        self._alfa = Validador.validar_rango("alfa", alfa, minimo=1e-9)
        self._v_min = Validador.validar_rango("v_min", v_min, minimo=1e-9)
        self._v_max = Validador.validar_rango("v_max", v_max, minimo=1e-9)
        if self._v_min >= self._v_max:
            raise ErrorValidacion(f"v_min ({v_min}) debe ser menor que v_max ({v_max})")
        self._v = Validador.validar_rango("v_inicial", v_inicial, minimo=self._v_min, maximo=self._v_max)

    @property
    def velocidad_actual(self) -> float:
        return self._v

    def energia(self, v: float, q: float) -> float:
        return self._a * v**3 + self._b * q / v

    def gradiente(self, v: float, q: float) -> float:
        return 3 * self._a * v**2 - self._b * q / v**2

    def optimo_analitico(self, q: float) -> float:
        """v* = (b Q / 3a)^(1/4), recortado al intervalo [v_min, v_max]."""
        v = (self._b * max(q, 0.0) / (3 * self._a)) ** 0.25
        return min(max(v, self._v_min), self._v_max)

    def _paso(self, entrada: EntradaOptimizacion) -> dict[str, float]:
        q = Validador.validar_rango("carga", entrada.carga, minimo=0)
        g = self.gradiente(self._v, q)
        self._v = min(max(self._v - self._alfa * g, self._v_min), self._v_max)
        return {
            "velocidad": self._v,
            "energia": self.energia(self._v, q),
            "gradiente": g,
            "velocidad_optima": self.optimo_analitico(q),
        }
