"""Mochila 0/1 (volumen-carga): maximiza el valor de las tareas sin exceder una capacidad (R2)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from src.core.network_entities import Paquete
from src.core.programacion_dinamica.base import ModeloProgramacionDinamica
from src.utils.validators import Validador


@dataclass(frozen=True)
class ResultadoMochila:
    """Resultado de resolver la mochila: los paquetes elegidos y sus totales."""

    seleccionados: tuple[Paquete, ...]
    valor_total: int
    peso_total: int


class Mochila(ModeloProgramacionDinamica):
    """Mochila 0/1: elige que paquetes procesar en una ventana de despacho de un servidor
    sin exceder su capacidad (R2).

    Cada paquete i tiene peso `w_i` (requerimiento) y valor `v_i` (prioridad). La tabla
    tabular acumula, para cada prefijo de i paquetes y cada capacidad w disponible, el
    mejor valor alcanzable:

        V[i][w] = V[i-1][w]                              si w_i > w  (no entra)
        V[i][w] = max(V[i-1][w], V[i-1][w - w_i] + v_i)   si w_i <= w

    con V[0][w] = 0 para todo w. La solucion optima es V[n][capacidad]; se reconstruye
    recorriendo la tabla hacia atras: si V[i][w] == V[i-1][w] el paquete i NO formo parte
    de la solucion optima encontrada (ante un empate se prefiere no incluirlo).
    """

    def __init__(self, capacidad: int) -> None:
        super().__init__()
        self._capacidad = Validador.validar_rango("capacidad", capacidad, minimo=0, entero=True)
        self._paquetes: tuple[Paquete, ...] = ()

    def _preparar(self, paquetes: Sequence[Paquete]) -> None:
        self._paquetes = tuple(paquetes)

    def _construir_tabla(self) -> list[list[int]]:
        n = len(self._paquetes)
        capacidad = self._capacidad
        tabla = [[0] * (capacidad + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            paquete = self._paquetes[i - 1]
            peso = paquete.requerimiento
            valor = paquete.prioridad
            for w in range(capacidad + 1):
                mejor_sin_item = tabla[i - 1][w]
                if peso <= w:
                    mejor_con_item = tabla[i - 1][w - peso] + valor
                    tabla[i][w] = max(mejor_sin_item, mejor_con_item)
                else:
                    tabla[i][w] = mejor_sin_item

        return tabla

    def _reconstruir(self) -> ResultadoMochila:
        n = len(self._paquetes)
        w = self._capacidad
        incluidos: set[int] = set()

        for i in range(n, 0, -1):
            if self._tabla[i][w] != self._tabla[i - 1][w]:
                incluidos.add(i - 1)
                w -= self._paquetes[i - 1].requerimiento

        seleccionados = tuple(self._paquetes[i] for i in range(n) if i in incluidos)
        valor_total = sum(p.prioridad for p in seleccionados)
        peso_total = sum(p.requerimiento for p in seleccionados)
        return ResultadoMochila(seleccionados, valor_total, peso_total)
