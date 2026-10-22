"""Problema 2: Metodo de los Multiplicadores de Lagrange con restriccion de igualdad.

Enunciado:
    Se quiere disenar un rectangulo de maxima area, pero con un perimetro fijo de 40 unidades.
    A(x, y) = x * y
    Restriccion: 2x + 2y = 40
    Tarea: Usar el metodo de Lagrange para encontrar las dimensiones optimas.
"""

from __future__ import annotations

from typing import Tuple
from .base import ResultadoOptimizacion, validar_numero, ErrorValidacion


class OptimizadorLagrangeRectangulo:
    """Modela y resuelve el problema de maximizacion de area rectangular con perimetro fijo.

    Funcion objetivo:
        A(x, y) = x * y
    Restriccion:
        g(x, y) = 2*x + 2*y - P = 0
    Lagrangiano:
        L(x, y, lambda_) = x*y - lambda_ * (2*x + 2*y - P)
    """

    def __init__(self, perimetro: float = 40.0) -> None:
        self.perimetro = validar_numero("perimetro (P)", perimetro, estricto_positivo=True)

    def evaluar_area(self, x: float, y: float) -> float:
        """Calcula el area A(x, y) = x * y."""
        return x * y

    def evaluar_restriccion(self, x: float, y: float) -> float:
        """Evalua 2*x + 2*y."""
        return 2 * x + 2 * y

    def hessiano_orlado(self) -> Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]:
        """Construye y retorna la matriz del Hessiano Orlado H_bar:
        H_bar = [
            [0,     dg/dx,  dg/dy],
            [dg/dx, d2L/dx2, d2L/dxdy],
            [dg/dy, d2L/dydx, d2L/dy2]
        ]
        Para este problema:
            dg/dx = 2, dg/dy = 2
            d2L/dx2 = 0, d2L/dy2 = 0, d2L/dxdy = 1
        """
        return (
            (0.0, 2.0, 2.0),
            (2.0, 0.0, 1.0),
            (2.0, 1.0, 0.0),
        )

    def determinante_hessiano_orlado(self) -> float:
        """Calcula el determinante del Hessiano Orlado:
        det(H_bar) = 0 - 2*(0 - 2) + 2*(2 - 0) = 4 + 4 = 8.
        Como det(H_bar) > 0 para n=2 variables y m=1 restriccion, garantiza un maximo local.
        """
        return 8.0

    def resolver(self) -> ResultadoOptimizacion:
        """Resuelve el sistema de Lagrange analiticamente y valida la solucion de segundo orden."""
        # Sistema de Lagrange:
        # dL/dx = y - 2*lambda = 0  => y = 2*lambda
        # dL/dy = x - 2*lambda = 0  => x = 2*lambda
        # dL/dlambda = -(2*x + 2*y - P) = 0 => 2(2*lambda) + 2(2*lambda) = P => 8*lambda = P
        lambda_opt = self.perimetro / 8.0
        x_opt = 2.0 * lambda_opt  # P / 4
        y_opt = 2.0 * lambda_opt  # P / 4
        area_max = self.evaluar_area(x_opt, y_opt)  # (P / 4)^2 = P^2 / 16

        det_h_bar = self.determinante_hessiano_orlado()

        conclusion = (
            f"El diseno geometrico que maximiza el area con un perimetro fijo de {self.perimetro:.2f} unidades "
            f"corresponde a una configuracion cuadrada perfecta de lados x = {x_opt:.4f} unidades e y = {y_opt:.4f} unidades, "
            f"alcanzando un area maxima de {area_max:.4f} unidades cuadradas. "
            f"El determinante del Hessiano Orlado es det(H_bar) = {det_h_bar:.2f} > 0, certificando un maximo restringido estricto. "
            f"El multiplicador de Lagrange lambda* = {lambda_opt:.4f} representa el valor marginal (precio sombra): "
            f"un incremento de 1 unidad en el perimetro disponible aumenta el area maxima en aproximadamente {lambda_opt:.4f} unidades cuadradas."
        )

        return ResultadoOptimizacion(
            problema_id=2,
            titulo="Metodo de Lagrange (restriccion de igualdad)",
            variables_optimas={"x": x_opt, "y": y_opt},
            valor_optimo=area_max,
            tipo_optimo="maximo",
            metodo="Multiplicadores de Lagrange y criterio del Hessiano Orlado (Analitico)",
            multiplicadores={"lambda": lambda_opt},
            convergencia=True,
            detalles={
                "geometria": "Cuadrado (x = y)",
                "perimetro_verificado": self.evaluar_restriccion(x_opt, y_opt),
                "det_hessiano_orlado": det_h_bar,
                "sensibilidad_dA_dP": lambda_opt,
                "formula_analitica_area": f"(P/4)^2 = ({self.perimetro}/4)^2 = {area_max:.4f}",
            },
            conclusion=conclusion,
        )
