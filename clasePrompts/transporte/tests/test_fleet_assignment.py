"""Pruebas unitarias para la asignacion de pedidos a la flota de camiones."""

import pytest
from src.constants import TruckState, TruckType
from src.models.fleet_manager import FleetManager
from src.models.graph import TransportGraph


@pytest.fixture
def fleet_mgr():
    """Retorna un gestor de flota inicializado con la red base."""
    graph = TransportGraph.build_default_network()
    return FleetManager(graph)


def test_fleet_initialization(fleet_mgr):
    """Verifica que la flota contenga los camiones iniciales y sus tipos correctos."""
    assert len(fleet_mgr.trucks) == 6

    truck_types = [t.truck_type for t in fleet_mgr.trucks]
    assert TruckType.LIGERO in truck_types
    assert TruckType.MEDIANO in truck_types
    assert TruckType.PESADO in truck_types

    # Todos deben arrancar disponibles
    for truck in fleet_mgr.trucks:
        assert truck.state == TruckState.DISPONIBLE
        assert truck.is_available is True
        assert truck.current_cargo_tons == 0.0


def test_order_creation_and_queue(fleet_mgr):
    """Verifica la creacion y encolamiento de ordenes."""
    order = fleet_mgr.create_order(origin_id="VAL", destination_id="CCS", cargo_tons=12.0)

    assert order.id == 1
    assert order.origin_id == "VAL"
    assert order.destination_id == "CCS"
    assert order.cargo_tons == 12.0
    assert order.status == "PENDIENTE"
    assert len(fleet_mgr.pending_orders) == 1


def test_capacity_constraint_rejection(fleet_mgr):
    """Verifica que no se asigne un camion ligero a un pedido de carga pesada."""
    # Deshabilitar camiones pesados y medianos para forzar solo camiones ligeros (capacidad 6t)
    for t in fleet_mgr.trucks:
        if t.truck_type != TruckType.LIGERO:
            t.state = TruckState.EN_RUTA

    # Pedido de 15 toneladas (excede las 6t de los camiones ligeros)
    heavy_order = fleet_mgr.create_order(origin_id="VAL", destination_id="CCS", cargo_tons=15.0)
    dispatch_res = fleet_mgr.dispatch_order(heavy_order)

    # Debe rechazar o retornar None por restriccion de capacidad
    assert dispatch_res is None
    assert heavy_order.status == "PENDIENTE"


def test_optimal_truck_selection(fleet_mgr):
    """
    Verifica que el algoritmo seleccione el camion disponible que minimice
    el costo combinado de reposicion + viaje cumpliendo la capacidad requerida.
    """
    order = fleet_mgr.create_order(origin_id="VAL", destination_id="GUA", cargo_tons=5.0)
    dispatch_res = fleet_mgr.dispatch_order(order)

    assert dispatch_res is not None
    chosen_truck, repos_path, deliv_path = dispatch_res

    # C-01 o C-03 estan en VAL (costo de reposicion = 0)
    # Como la carga es 5t, C-01 (Ligero) tiene menor costo por km ($1.25) que C-03 (Pesado, $3.40)
    assert chosen_truck.truck_type == TruckType.LIGERO
    assert chosen_truck.current_node.id == "VAL"
    assert order.status == "EN_PROCESO"
    assert order.assigned_truck_id == chosen_truck.id
