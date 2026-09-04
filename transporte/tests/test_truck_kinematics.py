"""Pruebas unitarias para la cinemática de camiones y transiciones de estado."""

import pytest
from src.constants import TruckState, TruckType
from src.models.graph import TransportGraph
from src.models.order import TransportOrder
from src.models.pathfinding import PathFinder
from src.models.truck import Truck


@pytest.fixture
def test_setup():
    """Configura un entorno reducido de prueba con un camion y una ruta directa."""
    graph = TransportGraph.build_default_network()
    val_node = graph.get_node("VAL")
    truck = Truck(truck_id=99, name="Test Truck", truck_type=TruckType.MEDIANO, initial_node=val_node)
    order = TransportOrder(order_id=10, origin_id="VAL", destination_id="GUA", cargo_tons=10.0)
    deliv_path = PathFinder.dijkstra(graph, "VAL", "GUA")
    return truck, order, deliv_path


def test_truck_loading_and_route_transition(test_setup):
    """Verifica que el camion inicie en CARGANDO y luego pase a EN_RUTA."""
    truck, order, deliv_path = test_setup

    truck.assign_mission(order, reposition_path=None, delivery_path=deliv_path)

    # Debe iniciar cargando en el origen
    assert truck.state == TruckState.CARGANDO
    assert truck.timer > 0.0

    # Simular transcurso del tiempo de carga
    truck.update(dt=truck.timer + 0.1)

    # Debe haber cargado la mercancia y pasar a EN_RUTA
    assert truck.state == TruckState.EN_RUTA
    assert truck.current_cargo_tons == 10.0
    assert truck.target_node is not None
    assert truck.target_node.id == "GUA"


def test_truck_motion_and_delivery_completion(test_setup):
    """Verifica que el camion avance en pantalla y complete la descarga al llegar."""
    truck, order, deliv_path = test_setup

    truck.assign_mission(order, reposition_path=None, delivery_path=deliv_path)
    # Pasar de carga a ruta
    truck.update(dt=truck.timer + 0.1)

    initial_x = truck.x
    initial_y = truck.y

    # Simular avance del movimiento durante varios pasos
    truck.update(dt=0.5)

    assert (truck.x != initial_x) or (truck.y != initial_y)
    assert truck.total_km_traveled > 0.0

    # Simular tiempo suficiente para llegar a GUA (distancia es ~150px a 130px/s)
    for _ in range(50):
        truck.update(dt=0.1)
        if truck.state == TruckState.DESCARGANDO:
            break

    assert truck.state == TruckState.DESCARGANDO

    # Completar tiempo de descarga
    truck.update(dt=truck.timer + 0.1)

    # Camion debe quedar libre, con orden entregada y mercancia descargada
    assert truck.state == TruckState.DISPONIBLE
    assert truck.current_cargo_tons == 0.0
    assert truck.trips_completed == 1
    assert truck.total_tons_delivered == 10.0
    assert order.status == "ENTREGADO"
