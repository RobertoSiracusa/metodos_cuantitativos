"""Ruta mas corta (menor latencia) entre nodos de una red por etapas (R1)."""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.core.programacion_dinamica.base import ModeloProgramacionDinamica
from src.core.red import Red
from src.utils.validators import ErrorValidacion

TablaRutas = dict[int, dict[str, tuple[float, "str | None"]]]


@dataclass(frozen=True)
class ResultadoRuta:
    """Resultado de resolver la ruta mas corta: el camino de nodos y su costo total."""

    camino: tuple[str, ...]
    costo: float

    @property
    def existe(self) -> bool:
        """True si el costo es finito, es decir, si hay un camino que une origen y destino."""
        return math.isfinite(self.costo)


class RutaMasCorta(ModeloProgramacionDinamica):
    """Ruta de menor costo entre dos nodos de una red por etapas (problema de la diligencia).

    Recursion hacia atras, etapa por etapa, desde el destino hasta el origen:

        f_k(s) = min_{x en la etapa k+1} { c(s, x) + f_{k+1}(x) }
        f(destino) = 0
        f(s) = infinito, para cualquier otro nodo s de la etapa del destino

    `c(s, x)` es el costo actual del enlace (latencia base mas congestion, ver
    `Enlace.costo_actual`). Un nodo caido -- sea origen, destino o intermedio -- tiene
    f = infinito y por lo tanto nunca puede formar parte de una ruta optima: es el
    principio de optimalidad de Bellman aplicado capa por capa.
    """

    def __init__(self, red: Red) -> None:
        super().__init__()
        self._red = red
        self._origen: str | None = None
        self._destino: str | None = None
        self._etapa_origen: int = 0
        self._etapa_destino: int = 0

    def _preparar(self, origen: str, destino: str) -> None:
        try:
            etapa_origen = self._red.etapa_de(origen)
        except KeyError:
            raise ErrorValidacion(f"el nodo origen '{origen}' no existe") from None
        try:
            etapa_destino = self._red.etapa_de(destino)
        except KeyError:
            raise ErrorValidacion(f"el nodo destino '{destino}' no existe") from None

        if etapa_origen >= etapa_destino:
            raise ErrorValidacion(
                f"el origen '{origen}' (etapa {etapa_origen}) debe estar en una etapa "
                f"estrictamente anterior a la del destino '{destino}' (etapa {etapa_destino})"
            )

        self._origen = origen
        self._destino = destino
        self._etapa_origen = etapa_origen
        self._etapa_destino = etapa_destino

    def _construir_tabla(self) -> TablaRutas:
        etapas = self._red.etapas()
        tabla: TablaRutas = {self._etapa_destino: {}}

        for nodo_id in etapas[self._etapa_destino]:
            nodo = self._red.nodo(nodo_id)
            if nodo_id == self._destino and nodo.esta_operativo:
                tabla[self._etapa_destino][nodo_id] = (0.0, None)
            else:
                tabla[self._etapa_destino][nodo_id] = (math.inf, None)

        for k in range(self._etapa_destino - 1, self._etapa_origen - 1, -1):
            tabla[k] = {}
            for nodo_id in etapas[k]:
                nodo = self._red.nodo(nodo_id)
                if not nodo.esta_operativo:
                    tabla[k][nodo_id] = (math.inf, None)
                    continue

                mejor_costo = math.inf
                mejor_siguiente: str | None = None
                for vecino in self._red.vecinos(nodo_id):
                    f_vecino, _ = tabla[k + 1][vecino]
                    costo_total = self._red.enlace(nodo_id, vecino).costo_actual() + f_vecino
                    if costo_total < mejor_costo:
                        mejor_costo = costo_total
                        mejor_siguiente = vecino
                tabla[k][nodo_id] = (mejor_costo, mejor_siguiente)

        return tabla

    def _reconstruir(self) -> ResultadoRuta:
        f_origen, _ = self._tabla[self._etapa_origen][self._origen]
        if not math.isfinite(f_origen):
            return ResultadoRuta((), math.inf)

        camino = [self._origen]
        actual = self._origen
        etapa_actual = self._etapa_origen
        while actual != self._destino:
            _, siguiente = self._tabla[etapa_actual][actual]
            camino.append(siguiente)
            actual = siguiente
            etapa_actual += 1
        return ResultadoRuta(tuple(camino), f_origen)
