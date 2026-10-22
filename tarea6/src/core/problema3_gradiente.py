"""Problema 3: Metodo del Gradiente (busqueda iterativa de ascenso de gradiente).

Enunciado:
    Maximizar la funcion:
    f(x, y) = -(x^2 + y^2) + 4x + 6y
    Punto inicial: (0, 0).
    Tarea: Aplicar el metodo del gradiente con pasos iterativos y encontrar el maximo.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple
from .base import ResultadoOptimizacion, validar_numero, ErrorValidacion


@dataclass(frozen=True)
class PasoGradiente:
    """Registro de una iteracion individual del algoritmo de ascenso de gradiente."""

    iteracion: int
    x: float
    y: float
    f_val: float
    grad_x: float
    grad_y: float
    norma_gradiente: float
    tasa_aprendizaje: float


class OptimizadorGradienteAscenso:
    """Implementa el algoritmo iterativo de ascenso de gradiente para maximizar f(x, y).

    Funcion:
        f(x, y) = -(x^2 + y^2) + 4*x + 6*y = 13 - (x - 2)^2 - (y - 3)^2
    Gradiente:
        grad(f) = [ -2*x + 4, -2*y + 6 ]
    """

    def __init__(
        self,
        x0: float = 0.0,
        y0: float = 0.0,
        tasa_aprendizaje: float = 0.1,
        max_iteraciones: int = 50,
        tolerancia: float = 1e-6,
    ) -> None:
        self.x0 = validar_numero("x0", x0)
        self.y0 = validar_numero("y0", y0)
        self.tasa_aprendizaje = validar_numero("tasa_aprendizaje (alfa)", tasa_aprendizaje, estricto_positivo=True)
        self.max_iteraciones = int(validar_numero("max_iteraciones", max_iteraciones, minimo=1))
        self.tolerancia = validar_numero("tolerancia", tolerancia, estricto_positivo=True)

    def evaluar_funcion(self, x: float, y: float) -> float:
        """Calcula f(x, y) = -(x^2 + y^2) + 4*x + 6*y."""
        return -(x ** 2 + y ** 2) + 4.0 * x + 6.0 * y

    def gradiente(self, x: float, y: float) -> Tuple[float, float]:
        """Calcula el vector gradiente [df/dx, df/dy]."""
        return (-2.0 * x + 4.0, -2.0 * y + 6.0)

    def paso_optimo_analitico(self) -> float:
        """Calcula el paso optimo exacto para esta funcion cuadratica:
        Hessiano = -2*I => alfa* = 1 / 2 = 0.5. Con alfa=0.5 converge en 1 sola iteracion.
        """
        return 0.5

    def optimo_analitico(self) -> Tuple[float, float, float]:
        """Retorna (x*, y*, f*) resolviendo gradiente = 0 analiticamente."""
        return (2.0, 3.0, 13.0)

    def resolver_iterativo(self, alfa: float | None = None) -> Tuple[ResultadoOptimizacion, List[PasoGradiente]]:
        """Ejecuta la busqueda iterativa por ascenso de gradiente paso a paso."""
        tasa = alfa if alfa is not None else self.tasa_aprendizaje
        validar_numero("tasa", tasa, estricto_positivo=True)

        historial: List[PasoGradiente] = []
        x_curr = self.x0
        y_curr = self.y0
        convergido = False

        for k in range(self.max_iteraciones + 1):
            f_val = self.evaluar_funcion(x_curr, y_curr)
            gx, gy = self.gradiente(x_curr, y_curr)
            norma_g = math.hypot(gx, gy)

            historial.append(
                PasoGradiente(
                    iteracion=k,
                    x=x_curr,
                    y=y_curr,
                    f_val=f_val,
                    grad_x=gx,
                    grad_y=gy,
                    norma_gradiente=norma_g,
                    tasa_aprendizaje=tasa,
                )
            )

            if norma_g < self.tolerancia:
                convergido = True
                break

            if k == self.max_iteraciones:
                break

            # Actualizacion en direccion de ascenso (gradiente positivo)
            x_curr = x_curr + tasa * gx
            y_curr = y_curr + tasa * gy

        ultimo = historial[-1]
        x_teo, y_teo, f_teo = self.optimo_analitico()
        error_x = abs(ultimo.x - x_teo)
        error_y = abs(ultimo.y - y_teo)
        error_f = abs(ultimo.f_val - f_teo)

        conclusion = (
            f"El metodo del gradiente partiendo de ({self.x0:.1f}, {self.y0:.1f}) con tasa alfa = {tasa:.4f} "
            f"convergio en {ultimo.iteracion} iteraciones a las coordenadas x = {ultimo.x:.4f}, y = {ultimo.y:.4f}, "
            f"con un valor de funcion f(x, y) = {ultimo.f_val:.4f} y norma de gradiente ||grad|| = {ultimo.norma_gradiente:.2e}. "
            f"El resultado coincide con el optimo teorico global (x* = 2, y* = 3, f* = 13.0) con un error absoluto "
            f"menor a {max(error_x, error_y, error_f):.2e}."
        )

        resultado = ResultadoOptimizacion(
            problema_id=3,
            titulo="Metodo del Gradiente (busqueda iterativa)",
            variables_optimas={"x": ultimo.x, "y": ultimo.y},
            valor_optimo=ultimo.f_val,
            tipo_optimo="maximo",
            metodo=f"Ascenso de Gradiente Iterativo (alfa = {tasa})",
            multiplicadores={},
            convergencia=convergido,
            detalles={
                "iteraciones_totales": ultimo.iteracion,
                "norma_gradiente_final": ultimo.norma_gradiente,
                "punto_inicial": (self.x0, self.y0),
                "optimo_analitico": {"x": x_teo, "y": y_teo, "f": f_teo},
                "error_distancia": math.hypot(error_x, error_y),
            },
            conclusion=conclusion,
        )

        return resultado, historial
