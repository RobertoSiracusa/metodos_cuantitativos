"""Problema 5: Problema de dimensionamiento optimo de cilindro (aplicacion fisica).

Enunciado:
    Se disena un cilindro de volumen fijo V = 500 cm^3. Se quiere minimizar el area superficial.
"""

from __future__ import annotations

import math
from typing import Tuple
from .base import ResultadoOptimizacion, validar_numero, ErrorValidacion


class OptimizadorCilindroFisico:
    """Modela y optimiza las dimensiones de un cilindro para minimizar su area superficial
    manteniendo un volumen constante.

    Formula general para cilindro cerrado (con 2 tapas circulares):
        Volumen: V = pi * r^2 * h
        Area:    A(r, h) = 2*pi*r^2 + 2*pi*r*h

    Sustituyendo h = V / (pi * r^2):
        A(r) = 2*pi*r^2 + (2*V) / r
    """

    def __init__(self, volumen: float = 500.0, cerrado: bool = True) -> None:
        self.volumen = validar_numero("volumen (V)", volumen, estricto_positivo=True)
        if not isinstance(cerrado, bool):
            raise ErrorValidacion("El parametro 'cerrado' debe ser booleano (True o False).")
        self.cerrado = cerrado

    def evaluar_area(self, r: float, h: float) -> float:
        """Calcula el area superficial total dadas las dimensiones r y h."""
        validar_numero("radio (r)", r, estricto_positivo=True)
        validar_numero("altura (h)", h, estricto_positivo=True)
        area_bases = (2.0 if self.cerrado else 1.0) * math.pi * (r ** 2)
        area_lateral = 2.0 * math.pi * r * h
        return area_bases + area_lateral

    def evaluar_volumen(self, r: float, h: float) -> float:
        """Calcula el volumen V = pi * r^2 * h."""
        return math.pi * (r ** 2) * h

    def derivadas_unidimensionales(self, r: float) -> Tuple[float, float]:
        """Calcula A'(r) y A''(r) en funcion del radio r para h = V / (pi * r^2)."""
        validar_numero("radio (r)", r, estricto_positivo=True)
        factor_base = 4.0 if self.cerrado else 2.0
        # A'(r) = factor_base * pi * r - (2 * V) / r^2
        d1 = factor_base * math.pi * r - (2.0 * self.volumen) / (r ** 2)
        # A''(r) = factor_base * pi + (4 * V) / r^3
        d2 = factor_base * math.pi + (4.0 * self.volumen) / (r ** 3)
        return (d1, d2)

    def resolver(self) -> ResultadoOptimizacion:
        """Resuelve analiticamente el problema de dimensionamiento optimo."""
        if self.cerrado:
            # Cilindro con dos tapas:
            # A'(r) = 4*pi*r - 2V/r^2 = 0 => 4*pi*r^3 = 2V => r^3 = V / (2*pi)
            r_opt = (self.volumen / (2.0 * math.pi)) ** (1.0 / 3.0)
            # h* = V / (pi * r^2) = 2 * r* (la altura es igual al diametro)
            h_opt = 2.0 * r_opt
            # Multiplicador de Lagrange: dL/dh = 2*pi*r - lambda*pi*r^2 = 0 => lambda = 2 / r
            lambda_opt = 2.0 / r_opt
            proporcion = "h = 2r (altura igual al diametro)"
            tipo_cilindro = "Cilindro cerrado (con 2 tapas circulares)"
        else:
            # Cilindro abierto (sin tapa superior):
            # A'(r) = 2*pi*r - 2V/r^2 = 0 => 2*pi*r^3 = 2V => r^3 = V / pi
            r_opt = (self.volumen / math.pi) ** (1.0 / 3.0)
            # h* = V / (pi * r^2) = r* (la altura es igual al radio)
            h_opt = r_opt
            lambda_opt = 1.0 / r_opt
            proporcion = "h = r (altura igual al radio)"
            tipo_cilindro = "Cilindro abierto (sin tapa superior)"

        area_min = self.evaluar_area(r_opt, h_opt)
        d1, d2 = self.derivadas_unidimensionales(r_opt)

        conclusion = (
            f"Para un volumen fijo de V = {self.volumen:.2f} cm^3 ({tipo_cilindro}), el diseno que minimiza el area "
            f"superficial requiere una relacion geometrica de {proporcion}. "
            f"Las dimensiones optimas son radio r* = {r_opt:.4f} cm y altura h* = {h_opt:.4f} cm "
            f"(diametro d* = {2*r_opt:.4f} cm), resultando en un area superficial minima de {area_min:.4f} cm^2. "
            f"La segunda derivada A''(r*) = {d2:.4f} > 0 ratifica matematicamente un minimo global estricto. "
            f"El multiplicador de Lagrange lambda* = {lambda_opt:.4f} cm^(-1) representa la sensibilidad marginal: "
            f"un aumento de 1 cm^3 en el volumen requerido expandira el area minima en aproximadamente {lambda_opt:.4f} cm^2."
        )

        return ResultadoOptimizacion(
            problema_id=5,
            titulo="Problema de volumen minimo (aplicacion fisica - dimensionamiento de cilindro)",
            variables_optimas={"radio_r": r_opt, "altura_h": h_opt},
            valor_optimo=area_min,
            tipo_optimo="minimo",
            metodo="Calculo diferencial y Multiplicadores de Lagrange (Analitico)",
            multiplicadores={"lambda_volumen": lambda_opt},
            convergencia=True,
            detalles={
                "tipo_cilindro": tipo_cilindro,
                "relacion_geometrica": proporcion,
                "diametro": 2.0 * r_opt,
                "volumen_verificado": self.evaluar_volumen(r_opt, h_opt),
                "segunda_derivada": d2,
                "sensibilidad_dA_dV": lambda_opt,
                "formula_radio": "cbrt(V / (2*pi))" if self.cerrado else "cbrt(V / pi)",
            },
            conclusion=conclusion,
        )
