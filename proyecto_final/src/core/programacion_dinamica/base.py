"""Esqueleto comun (Template Method) para los modelos de programacion dinamica (R1, R2)."""

from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from typing import Any


class ModeloProgramacionDinamica(ABC):
    """Template Method para resolver un problema de programacion dinamica.

    `resolver()` fija el orden de los pasos: preparar los datos de entrada, construir la
    tabla de sub-soluciones y reconstruir la solucion final a partir de esa tabla. Cada
    subclase concreta (RutaMasCorta, Mochila) solo completa `_preparar`,
    `_construir_tabla` y `_reconstruir`; el algoritmo general no cambia.

    Esto plasma el principio de optimalidad de Bellman: `_construir_tabla` guarda, para
    cada subproblema, el valor optimo asumiendo que todos los subproblemas mas pequenos
    ya fueron resueltos de forma optima, y `_reconstruir` recorre esa tabla una sola vez
    hacia la solucion global, sin volver a resolver ningun subproblema.
    """

    def __init__(self) -> None:
        self._tabla: Any | None = None

    def resolver(self, *args: Any, **kwargs: Any) -> Any:
        """Ejecuta el Template Method completo y devuelve la solucion reconstruida."""
        self._preparar(*args, **kwargs)
        self._tabla = self._construir_tabla()
        return self._reconstruir()

    @abstractmethod
    def _preparar(self, *args: Any, **kwargs: Any) -> None:
        """Valida y guarda los datos de entrada propios del problema concreto."""
        raise NotImplementedError

    @abstractmethod
    def _construir_tabla(self) -> Any:
        """Llena la tabla de sub-soluciones optimas (la programacion dinamica en si)."""
        raise NotImplementedError

    @abstractmethod
    def _reconstruir(self) -> Any:
        """Recorre la tabla ya construida para armar la solucion final."""
        raise NotImplementedError

    @property
    def tabla(self) -> Any | None:
        """Copia profunda de la tabla de la ultima resolucion, o None si nunca se resolvio.

        Se devuelve una copia (no la tabla interna) para que modificarla desde afuera no
        afecte el estado del modelo.
        """
        if self._tabla is None:
            return None
        return copy.deepcopy(self._tabla)
