"""Pruebas unitarias para la red vial y algoritmos de ruta minima (Dijkstra y A*)."""

import pytest
from src.models.graph import TransportGraph
from src.models.pathfinding import PathFinder


@pytest.fixture
def default_network():
    """Retorna una instancia fresca del grafo vial predeterminado."""
    return TransportGraph.build_default_network()


def test_network_structure_and_connectivity(default_network):
    """Verifica que el grafo contenga todos los nodos y aristas viales conectadas."""
    assert len(default_network.nodes) == 12
    assert len(default_network.edges) >= 17

    val = default_network.get_node("VAL")
    assert val is not None
    assert val.name == "Valencia Central Hub"
    assert val.node_type == "HUB"

    ccs = default_network.get_node("CCS")
    assert ccs is not None
    assert ccs.node_type == "CITY"


def test_dijkstra_shortest_path(default_network):
    """Verifica el cálculo de la ruta más corta entre Valencia y Caracas."""
    result = PathFinder.dijkstra(default_network, "VAL", "CCS", cost_per_km=2.0)

    assert result.found is True
    assert len(result.nodes) >= 4
    assert result.nodes[0].id == "VAL"
    assert result.nodes[-1].id == "CCS"

    # La distancia optima por la Autopista Regional del Centro debe ser ~184 km
    # VAL -> GUA (22) -> MAR (46) -> VIC (34) -> TEQ (54) -> CCS (28) = 184 km
    assert 170.0 <= result.total_distance_km <= 195.0
    assert result.total_cost > 0.0
    assert result.total_time_hours > 0.0


def test_astar_equivalency_with_dijkstra(default_network):
    """
    Verifica que la heuristica admisible de A* converge exactamente al mismo
    costo y distancia minima global que el algoritmo de Dijkstra.
    """
    res_dijkstra = PathFinder.dijkstra(default_network, "PTO", "CCS", cost_per_km=2.10)
    res_astar = PathFinder.astar(default_network, "PTO", "CCS", cost_per_km=2.10)

    assert res_dijkstra.found is True
    assert res_astar.found is True

    # Ambas tecnicas deben coincidir en la distancia y costo optimo
    assert round(res_dijkstra.total_distance_km, 2) == round(res_astar.total_distance_km, 2)
    assert round(res_dijkstra.total_cost, 2) == round(res_astar.total_cost, 2)
    assert res_dijkstra.path_str == res_astar.path_str


def test_invalid_and_disconnected_paths(default_network):
    """Verifica el comportamiento seguro ante nodos inexistentes o caminos nulos."""
    res_invalid = PathFinder.dijkstra(default_network, "NON_EXISTENT", "CCS")
    assert res_invalid.found is False
    assert len(res_invalid.nodes) == 0

    # Mismo origen y destino
    res_same = PathFinder.dijkstra(default_network, "VAL", "VAL")
    assert res_same.found is True
    assert res_same.total_distance_km == 0.0
    assert len(res_same.nodes) == 1


def test_alternative_path_and_savings(default_network):
    """Verifica que la ruta alternativa sea mas larga y genere un ahorro positivo."""
    optimal = PathFinder.dijkstra(default_network, "VAL", "CCS", cost_per_km=2.10)
    alt = PathFinder.find_alternative_path(default_network, "VAL", "CCS", optimal, cost_per_km=2.10)

    assert alt is not None
    assert alt.found is True
    assert alt.path_str != optimal.path_str
    # La ruta alternativa debe tener mayor distancia o costo que la óptima
    assert alt.total_cost > optimal.total_cost
    assert alt.total_distance_km >= optimal.total_distance_km

    savings = alt.total_cost - optimal.total_cost
    assert savings > 0.0
