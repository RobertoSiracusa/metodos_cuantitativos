"""Interfaz comun de los optimizadores no lineales que se actualizan en cada tick (R4, R5)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class EntradaOptimizacion:
    """Lo que un optimizador necesita saber del sistema en un instante.

    Se define aqui (y no en simulation/) para que core/ no dependa del motor SimPy: el
    motor arma esta entrada en cada tick y se la pasa a todos los optimizadores por igual.

    - `tiempo`: instante de simulacion.
    - `carga`: carga promedio de los servidores, en % (0-100). Es el calor Q del gradiente.
    - `demandas`: demanda actual de cada cluster (w_i de Lagrange).
    """

    tiempo: float
    carga: float
    demandas: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class ResultadoOptimizacion:
    """Valores calculados por un optimizador en un tick: nombre de la serie -> valor."""

    tiempo: float
    valores: dict[str, float]


class Optimizador(ABC):
    """Base de GradienteEnfriamiento y AsignadorLagrange (polimorfismo en el motor).

    El motor hace `for opt in optimizadores: opt.actualizar(entrada)` sin conocer la clase
    concreta. Cada resultado se guarda en `historial`, que la GUI y el PDF usan para graficar.
    """

    def __init__(self) -> None:
        self._historial: list[ResultadoOptimizacion] = []

    def actualizar(self, entrada: EntradaOptimizacion) -> ResultadoOptimizacion:
        """Ejecuta un paso del optimizador y lo registra en el historial (Template Method)."""
        resultado = ResultadoOptimizacion(entrada.tiempo, self._paso(entrada))
        self._historial.append(resultado)
        return resultado

    @abstractmethod
    def _paso(self, entrada: EntradaOptimizacion) -> dict[str, float]:
        """Calcula los valores del tick actual."""
        raise NotImplementedError

    @property
    def historial(self) -> tuple[ResultadoOptimizacion, ...]:
        return tuple(self._historial)

    def series_para_grafico(self) -> dict[str, list[float]]:
        """Historial en columnas: {'tiempo': [...], '<serie>': [...]} listo para graficar."""
        series: dict[str, list[float]] = {"tiempo": []}
        for r in self._historial:
            series["tiempo"].append(r.tiempo)
            for nombre, valor in r.valores.items():
                series.setdefault(nombre, []).append(valor)
        return series
