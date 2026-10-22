"""Problema 1: Optimizacion sin restricciones mediante calculo multivariable y derivadas parciales.

Enunciado:
    Una empresa produce un articulo cuya funcion de costo depende de dos variables:
    C(x, y) = x^2 + y^2 - 4x - 6y + 20
    Tarea: Encontrar los valores de x e y que minimizan el costo.
"""

from __future__ import annotations

from typing import Tuple
from .base import ResultadoOptimizacion, validar_numero, ErrorValidacion


class OptimizadorSinRestricciones:
    """Modela y resuelve el problema de minimizacion de costos sin restricciones.

    Representa la funcion cuadratica general:
        C(x, y) = a*x^2 + b*y^2 + c*x + d*y + e
    """

    def __init__(
        self,
        a: float = 1.0,
        b: float = 1.0,
        c: float = -4.0,
        d: float = -6.0,
        e: float = 20.0,
    ) -> None:
        self.a = validar_numero("coef_x2 (a)", a)
        self.b = validar_numero("coef_y2 (b)", b)
        self.c = validar_numero("coef_x (c)", c)
        self.d = validar_numero("coef_y (d)", d)
        self.e = validar_numero("constante (e)", e)

        if self.a == 0 or self.b == 0:
            raise ErrorValidacion("Los coeficientes cuadraticos 'a' y 'b' no pueden ser cero en este modelo.")

    def evaluar_costo(self, x: float, y: float) -> float:
        """Calcula el costo C(x, y)."""
        return self.a * (x ** 2) + self.b * (y ** 2) + self.c * x + self.d * y + self.e

    def gradiente(self, x: float, y: float) -> Tuple[float, float]:
        """Calcula el vector gradiente [dC/dx, dC/dy]."""
        return (2 * self.a * x + self.c, 2 * self.b * y + self.d)

    def matriz_hessiana(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Retorna la matriz Hessiana H = [[d2C/dx2, d2C/dxdy], [d2C/dydx, d2C/dy2]]."""
        return ((2 * self.a, 0.0), (0.0, 2 * self.b))

    def resolver(self) -> ResultadoOptimizacion:
        """Encuentra el punto critico analiticamente y clasifica la concavidad/convexidad mediante el Hessiano."""
        # Condicion Necesaria de Primer Orden (CPO): gradiente = (0, 0)
        # 2*a*x + c = 0  =>  x* = -c / (2*a)
        # 2*b*y + d = 0  =>  y* = -d / (2*b)
        x_opt = -self.c / (2 * self.a)
        y_opt = -self.d / (2 * self.b)
        costo_min = self.evaluar_costo(x_opt, y_opt)

        # Condicion Suficiente de Segundo Orden (CSO): Matriz Hessiana
        # H = [[2a, 0], [0, 2b]]
        d1 = 2 * self.a
        det_h = (2 * self.a) * (2 * self.b)

        if d1 > 0 and det_h > 0:
            clasificacion = "minimo global estricto"
            tipo = "minimo"
        elif d1 < 0 and det_h > 0:
            clasificacion = "maximo global estricto"
            tipo = "maximo"
        elif det_h < 0:
            clasificacion = "punto de silla (saddle point)"
            tipo = "indefinido"
        else:
            clasificacion = "criterio no concluyente (det(H) = 0)"
            tipo = "indefinido"

        conclusion = (
            f"Para minimizar el costo operativo, la empresa debe establecer los niveles de produccion en "
            f"x = {x_opt:.4f} e y = {y_opt:.4f}, alcanzando un costo minimo de {costo_min:.4f} unidades monetarias. "
            f"La matriz Hessiana es definida positiva (D1 = {d1:.2f} > 0, det(H) = {det_h:.2f} > 0), "
            f"lo que certifica analiticamente que el punto critico es un {clasificacion}."
        )

        return ResultadoOptimizacion(
            problema_id=1,
            titulo="Problema sin restricciones (derivadas parciales)",
            variables_optimas={"x": x_opt, "y": y_opt},
            valor_optimo=costo_min,
            tipo_optimo=tipo,
            metodo="Derivadas parciales y criterio de la matriz Hessiana (Analitico)",
            multiplicadores={},
            convergencia=True,
            detalles={
                "d1_hessiano": d1,
                "det_hessiano": det_h,
                "clasificacion_punto": clasificacion,
                "gradiente_en_optimo": self.gradiente(x_opt, y_opt),
                "forma_canonica": f"(x - {x_opt:.2f})^2 + (y - {y_opt:.2f})^2 + {costo_min:.2f}",
            },
            conclusion=conclusion,
        )
