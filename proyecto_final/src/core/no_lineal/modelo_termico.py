"""Modelo termico carga -> temperatura y su analisis por derivadas (R3)."""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.utils.validators import ErrorValidacion, Validador


@dataclass(frozen=True)
class PuntoEstacionario:
    """Punto donde T'(c) = 0, clasificado con el signo de T''(c)."""

    carga: float
    temperatura: float
    tipo: str  # "maximo", "minimo" o "silla"


class ModeloTermico:
    """Temperatura de un servidor en funcion de su carga c (en %, dominio [0, 100]).

        T(c)   = a c^3 + b c^2 + k c + d
        T'(c)  = 3a c^2 + 2b c + k
        T''(c) = 6a c + 2b

    Con los coeficientes por defecto (a=0.0002, b=-0.03, k=1.26, d=30):
        T'(c) = 0.0006 (c - 30)(c - 70)  -> estacionarios en c=30 y c=70
        T''(c) = 0.0012 (c - 50)         -> inflexion en c=50
    Lectura fisica: la temperatura sube hasta un maximo local (30 %), baja cuando los
    ventiladores entran en regimen (minimo local en 70 %) y despues se dispara.

    Todo se calcula analiticamente (formula de la cuadratica sobre T'), sin librerias
    simbolicas, para que la derivacion se vea en el codigo.
    """

    DOMINIO = (0.0, 100.0)

    def __init__(
        self,
        a: float = 0.0002,
        b: float = -0.03,
        k: float = 1.26,
        d: float = 30.0,
        t_max: float = 50.0,
    ) -> None:
        self._a = Validador.validar_rango("a", a)
        if self._a == 0:
            raise ErrorValidacion("a no puede ser 0: el modelo termico debe ser cubico")
        self._b = Validador.validar_rango("b", b)
        self._k = Validador.validar_rango("k", k)
        self._d = Validador.validar_rango("d", d)
        self._t_max = Validador.validar_rango("t_max", t_max)

    @property
    def t_max(self) -> float:
        return self._t_max

    def temperatura(self, c: float) -> float:
        return self._a * c**3 + self._b * c**2 + self._k * c + self._d

    def derivada(self, c: float) -> float:
        return 3 * self._a * c**2 + 2 * self._b * c + self._k

    def segunda_derivada(self, c: float) -> float:
        return 6 * self._a * c + 2 * self._b

    def puntos_estacionarios(self) -> list[PuntoEstacionario]:
        """Raices de T'(c) = 0 dentro del dominio, clasificadas por el criterio de la 2da derivada.

        T'(c) = A c^2 + B c + C con A = 3a, B = 2b, C = k  ->  c = (-B +- sqrt(B^2 - 4AC)) / 2A
        """
        A, B, C = 3 * self._a, 2 * self._b, self._k
        discriminante = B * B - 4 * A * C
        if discriminante < 0:
            return []
        raiz = math.sqrt(discriminante)
        candidatos = sorted({(-B - raiz) / (2 * A), (-B + raiz) / (2 * A)})

        puntos = []
        for c in candidatos:
            if not self.DOMINIO[0] <= c <= self.DOMINIO[1]:
                continue
            curvatura = self.segunda_derivada(c)
            tipo = "maximo" if curvatura < 0 else "minimo" if curvatura > 0 else "silla"
            puntos.append(PuntoEstacionario(c, self.temperatura(c), tipo))
        return puntos

    def punto_inflexion(self) -> float | None:
        """T''(c) = 0  ->  c = -b / (3a). None si cae fuera del dominio."""
        c = -self._b / (3 * self._a)
        return c if self.DOMINIO[0] <= c <= self.DOMINIO[1] else None

    def carga_umbral(self, paso: float = 0.01) -> float | None:
        """Primera carga del dominio con T(c) >= t_max (barrido fino), o None si nunca se alcanza."""
        c = self.DOMINIO[0]
        while c <= self.DOMINIO[1]:
            if self.temperatura(c) >= self._t_max:
                return round(c, 6)
            c += paso
        return None

    def punto_critico(self) -> float | None:
        """Carga de enfriamiento de emergencia (decision D3).

        Es el menor entre el punto de inflexion (desde ahi la temperatura empieza a
        acelerarse) y la primera carga donde T(c) alcanza t_max. None si no hay ninguno.
        """
        candidatos = [c for c in (self.punto_inflexion(), self.carga_umbral()) if c is not None]
        return min(candidatos) if candidatos else None
