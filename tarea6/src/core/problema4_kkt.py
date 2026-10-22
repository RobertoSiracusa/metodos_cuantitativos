"""Problema 4: Programacion No Lineal con multiples restricciones (Condiciones KKT).

Enunciado:
    Maximizar la ganancia:
    G(x, y) = 5x + 8y - 0.1x^2 - 0.2y^2
    Restricciones:
    x + y <= 40
    x >= 0
    y >= 0
"""

from __future__ import annotations

from typing import Dict, Tuple
from .base import ResultadoOptimizacion, validar_numero, ErrorValidacion


class OptimizadorKKTMultiplesRestricciones:
    """Modela y resuelve el problema de maximizacion de ganancia con restricciones de desigualdad.

    Funcion objetivo:
        G(x, y) = c_x*x + c_y*y + q_x*x^2 + q_y*y^2
        (Con q_x = -0.1, q_y = -0.2 < 0, funcion estrictamente concava)
    Restricciones:
        g1(x, y) = x + y - B <= 0  (con B = 40)
        g2(x, y) = -x <= 0
        g3(x, y) = -y <= 0
    """

    def __init__(
        self,
        coef_x: float = 5.0,
        coef_y: float = 8.0,
        coef_x2: float = -0.1,
        coef_y2: float = -0.2,
        capacidad_maxima: float = 40.0,
    ) -> None:
        self.coef_x = validar_numero("coef_x", coef_x)
        self.coef_y = validar_numero("coef_y", coef_y)
        self.coef_x2 = validar_numero("coef_x2", coef_x2)
        self.coef_y2 = validar_numero("coef_y2", coef_y2)
        self.capacidad_maxima = validar_numero("capacidad_maxima (B)", capacidad_maxima, estricto_positivo=True)

        if self.coef_x2 >= 0 or self.coef_y2 >= 0:
            raise ErrorValidacion("Los coeficientes cuadraticos deben ser negativos para garantizar concavidad.")

    def evaluar_ganancia(self, x: float, y: float) -> float:
        """Calcula G(x, y) = 5x + 8y - 0.1x^2 - 0.2y^2."""
        return self.coef_x * x + self.coef_y * y + self.coef_x2 * (x ** 2) + self.coef_y2 * (y ** 2)

    def gradiente(self, x: float, y: float) -> Tuple[float, float]:
        """Calcula el vector gradiente [dG/dx, dG/dy]."""
        return (self.coef_x + 2 * self.coef_x2 * x, self.coef_y + 2 * self.coef_y2 * y)

    def optimo_no_restringido(self) -> Tuple[float, float, float]:
        """Encuentra el maximo sin restricciones (dG/dx = 0, dG/dy = 0)."""
        x_nr = -self.coef_x / (2 * self.coef_x2)  # -5 / (-0.2) = 25
        y_nr = -self.coef_y / (2 * self.coef_y2)  # -8 / (-0.4) = 20
        g_nr = self.evaluar_ganancia(x_nr, y_nr)
        return (x_nr, y_nr, g_nr)

    def resolver(self) -> ResultadoOptimizacion:
        """Resuelve el sistema KKT examinando la activacion de restricciones."""
        x_nr, y_nr, g_nr = self.optimo_no_restringido()
        suma_nr = x_nr + y_nr

        # Verificacion de factibilidad del optimo no restringido:
        if suma_nr <= self.capacidad_maxima and x_nr >= 0 and y_nr >= 0:
            # La restriccion no esta activa, el maximo es el punto interior
            x_opt, y_opt = x_nr, y_nr
            mu1, mu2, mu3 = 0.0, 0.0, 0.0
            restriccion_activa = "Ninguna (optimo en el interior de la region)"
        else:
            # La restriccion de capacidad x + y <= B esta activa con igualdad: x + y = B => y = B - x
            # dL/dx = coef_x + 2*coef_x2*x - mu1 = 0 => mu1 = coef_x + 2*coef_x2*x
            # dL/dy = coef_y + 2*coef_y2*y - mu1 = 0 => mu1 = coef_y + 2*coef_y2*(B - x)
            # coef_x + 2*coef_x2*x = coef_y + 2*coef_y2*B - 2*coef_y2*x
            # 2*(coef_x2 + coef_y2)*x = coef_y - coef_x + 2*coef_y2*B
            # x* = (coef_y - coef_x + 2*coef_y2*B) / (2*(coef_y2 - coef_x2)) pero evaluemos con signos correctos:
            # dG/dx = 5 - 0.2x; dG/dy = 8 - 0.4y
            # 5 - 0.2x = 8 - 0.4(B - x) = 8 - 0.4B + 0.4x
            # 5 - 8 + 0.4B = 0.4x + 0.2x = 0.6x
            # x* = (5 - 8 + 0.4*40) / 0.6 = (-3 + 16) / 0.6 = 13 / 0.6 = 65/3
            # Formalizamos para cualquier parametro:
            # (2*self.coef_x2 - 2*self.coef_y2)*x = self.coef_y - self.coef_x + 2*self.coef_y2*self.capacidad_maxima
            # dG/dx - dG/dy = 0 en frontera:
            # (coef_x + 2*coef_x2*x) = (coef_y + 2*coef_y2*(self.capacidad_maxima - x))
            # x * (2*coef_x2 + 2*coef_y2_negativo) ...
            denominador = (2 * self.coef_x2) - (2 * self.coef_y2)  # 2*(-0.1) - 2*(-0.2) = -0.2 + 0.4 = 0.2? Wait!
            # Vamos paso por paso con algebra precisa:
            # 5 + 2*(-0.1)*x = 8 + 2*(-0.2)*(40 - x)
            # 5 - 0.2x = 8 - 0.4*40 + 0.4x
            # 5 - 0.2x = 8 - 16 + 0.4x = -8 + 0.4x
            # 13 = 0.6x  =>  x = 13 / 0.6 = 65 / 3
            # En variables generales:
            # coef_x + 2*coef_x2*x = coef_y + 2*coef_y2*B - 2*coef_y2*x
            # x * (2*coef_x2 - 2*coef_y2) ?? No: pasamos -2*coef_y2*x restando:
            # 2*coef_x2*x - (-2*coef_y2*x) ...
            # 2*coef_x2*x - 2*coef_y2*x NO, en el lado derecho es: + 2*coef_y2*(B - x) = 2*coef_y2*B - 2*coef_y2*x.
            # Pasando a la izquierda: x * (2*coef_x2 + 2*coef_y2) ??
            # Verifiquemos coef_x2 = -0.1, coef_y2 = -0.2:
            # 2*(-0.1)*x - (-2*(-0.2)*x) = -0.2x - 0.4x = -0.6x.
            # Y al lado derecho: coef_y - coef_x + 2*coef_y2*B = 8 - 5 + 2*(-0.2)*40 = 3 - 16 = -13.
            # -0.6x = -13  =>  x = 13 / 0.6 = 65/3.
            numerador = self.coef_y - self.coef_x + 2 * self.coef_y2 * self.capacidad_maxima
            denominador = 2 * self.coef_x2 - 2 * (-self.coef_y2)  # = 2*coef_x2 + 2*coef_y2
            # 2*(-0.1) + 2*(-0.2) = -0.6. Perfecto!
            denominador_correcto = 2 * (self.coef_x2 + self.coef_y2)
            x_opt = numerador / denominador_correcto
            y_opt = self.capacidad_maxima - x_opt

            mu1 = self.coef_x + 2 * self.coef_x2 * x_opt
            mu2 = 0.0
            mu3 = 0.0
            restriccion_activa = f"x + y = {self.capacidad_maxima:.1f} (frontera activa)"

        ganancia_max = self.evaluar_ganancia(x_opt, y_opt)

        conclusion = (
            f"El optimo sin restricciones se ubica en ({x_nr:.2f}, {y_nr:.2f}) con una suma de {suma_nr:.2f} > {self.capacidad_maxima:.2f}, "
            f"lo cual es infactible. En consecuencia, la restriccion de capacidad conjunta x + y <= {self.capacidad_maxima:.1f} "
            f"se activa plenamente en el optimo. "
            f"Resolviendo el sistema Karush-Kuhn-Tucker (KKT), las cantidades optimas a producir son "
            f"x* = {x_opt:.4f} (65/3) e y* = {y_opt:.4f} (55/3), generando una ganancia maxima de {ganancia_max:.4f} "
            f"(845/6 = 140.8333 unidades monetarias). "
            f"El multiplicador de Lagrange asociado a la capacidad es mu1 = {mu1:.4f} (2/3 > 0), el cual representa el "
            f"precio sombra de la restriccion: un aumento de 1 unidad en la capacidad conjunta incrementara la ganancia "
            f"maxima en aproximadamente {mu1:.4f} unidades monetarias."
        )

        return ResultadoOptimizacion(
            problema_id=4,
            titulo="Problema con multiples restricciones (KKT)",
            variables_optimas={"x": x_opt, "y": y_opt},
            valor_optimo=ganancia_max,
            tipo_optimo="maximo",
            metodo="Condiciones Karush-Kuhn-Tucker (KKT)",
            multiplicadores={"mu_capacidad (mu1)": mu1, "mu_no_neg_x (mu2)": mu2, "mu_no_neg_y (mu3)": mu3},
            convergencia=True,
            detalles={
                "restriccion_activa": restriccion_activa,
                "optimo_sin_restricciones": {"x": x_nr, "y": y_nr, "ganancia": g_nr, "suma": suma_nr},
                "holgura_capacidad": self.capacidad_maxima - (x_opt + y_opt),
                "fraccion_exacta_x": "65/3",
                "fraccion_exacta_y": "55/3",
                "fraccion_exacta_ganancia": "845/6",
                "fraccion_exacta_mu1": "2/3",
                "sensibilidad_dG_dB": mu1,
            },
            conclusion=conclusion,
        )
