"""Clases base, estructuras de datos y validaciones para Programacion No Lineal."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ErrorValidacion(ValueError):
    """Excepcion lanzada ante parametros no validos en los modelos de optimizacion."""
    pass


def validar_numero(
    nombre: str,
    valor: Any,
    minimo: float | None = None,
    maximo: float | None = None,
    estricto_positivo: bool = False,
) -> float:
    """Valida que un valor sea numerico y cumpla con las cotas especificadas."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ErrorValidacion(
            f"El parametro '{nombre}' debe ser numerico (int o float), recibido: {valor!r} ({type(valor).__name__})"
        )
    val = float(valor)
    if estricto_positivo and val <= 0:
        raise ErrorValidacion(f"El parametro '{nombre}' debe ser estrictamente positivo (> 0), recibido: {val}")
    if minimo is not None and val < minimo:
        raise ErrorValidacion(f"El parametro '{nombre}' debe ser >= {minimo}, recibido: {val}")
    if maximo is not None and val > maximo:
        raise ErrorValidacion(f"El parametro '{nombre}' debe ser <= {maximo}, recibido: {val}")
    return val


@dataclass(frozen=True)
class ResultadoOptimizacion:
    """Contenedor inmutable del resultado de un modelo de optimizacion no lineal."""

    problema_id: int
    titulo: str
    variables_optimas: dict[str, float]
    valor_optimo: float
    tipo_optimo: str  # "minimo" o "maximo"
    metodo: str
    multiplicadores: dict[str, float] = field(default_factory=dict)
    convergencia: bool = True
    detalles: dict[str, Any] = field(default_factory=dict)
    conclusion: str = ""
