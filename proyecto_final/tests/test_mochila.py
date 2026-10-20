"""Tests de Mochila (R2): mochila 0/1 tabular, con valores calculados a mano."""

from dataclasses import dataclass

import pytest

from src.core.programacion_dinamica.mochila import Mochila
from src.utils.validators import ErrorValidacion


@dataclass(frozen=True)
class _Item:
    """Item minimo (peso, valor) para probar el algoritmo de la mochila de forma aislada,
    sin las restricciones de dominio de Paquete (esas se prueban en test_entidades.py).
    """

    id: str
    requerimiento: int
    prioridad: int


def test_mochila_capacidad_10_selecciona_b_y_d():
    items = [
        _Item("A", 5, 10),
        _Item("B", 4, 40),
        _Item("C", 6, 30),
        _Item("D", 3, 50),
    ]
    resultado = Mochila(10).resolver(items)
    assert [p.id for p in resultado.seleccionados] == ["B", "D"]
    assert resultado.valor_total == 90
    assert resultado.peso_total == 7


def test_mochila_capacidad_cero_devuelve_vacio():
    items = [_Item("A", 5, 10), _Item("B", 4, 40)]
    resultado = Mochila(0).resolver(items)
    assert resultado.seleccionados == ()
    assert resultado.valor_total == 0
    assert resultado.peso_total == 0


def test_mochila_item_mas_pesado_que_capacidad_queda_excluido():
    items = [_Item("A", 10, 999), _Item("B", 2, 5)]
    resultado = Mochila(5).resolver(items)
    ids_seleccionados = [p.id for p in resultado.seleccionados]
    assert "A" not in ids_seleccionados
    assert "B" in ids_seleccionados


def test_mochila_lista_vacia_da_valor_cero():
    resultado = Mochila(10).resolver([])
    assert resultado.seleccionados == ()
    assert resultado.valor_total == 0
    assert resultado.peso_total == 0


def test_mochila_capacidad_negativa_lanza_error():
    with pytest.raises(ErrorValidacion):
        Mochila(-1)


def test_mochila_capacidad_no_entera_lanza_error():
    with pytest.raises(ErrorValidacion):
        Mochila(5.5)
