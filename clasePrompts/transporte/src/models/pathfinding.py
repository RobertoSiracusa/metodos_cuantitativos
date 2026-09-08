"""Algoritmos de optimizacion de rutas: Dijkstra y A* (A-Star)."""

import heapq
import math
from typing import Dict, List, Optional, Tuple

from src.models.graph import Edge, Node, TransportGraph


class PathResult:
    """Resultado cuantitativo de la optimizacion de ruta."""

    def __init__(
        self,
        found: bool,
        nodes: List[Node],
        edges: List[Edge],
        total_distance_km: float = 0.0,
        total_cost: float = 0.0,
        total_time_hours: float = 0.0,
        visited_count: int = 0,
        algorithm_used: str = "Dijkstra",
    ):
        self.found = found
        self.nodes = nodes
        self.edges = edges
        self.total_distance_km = float(total_distance_km)
        self.total_cost = float(total_cost)
        self.total_time_hours = float(total_time_hours)
        self.visited_count = visited_count
        self.algorithm_used = algorithm_used

    @property
    def path_str(self) -> str:
        """Representacion textual en secuencia de nodos."""
        if not self.nodes:
            return "Sin ruta"
        return " -> ".join(n.id for n in self.nodes)

    def __repr__(self) -> str:
        return f"PathResult({self.path_str}, {self.total_distance_km:.1f}km, ${self.total_cost:.2f})"


class PathFinder:
    """Motor de busqueda y optimizacion de caminos minimos en redes de transporte."""

    @staticmethod
    def dijkstra(
        graph: TransportGraph,
        start_id: str,
        target_id: str,
        cost_per_km: float = 2.0,
        criterion: str = "distance",  # "distance" o "cost"
    ) -> PathResult:
        """
        Calcula la ruta mas corta / de menor costo entre start_id y target_id usando Dijkstra.
        Garantiza optimalidad global en grafos con pesos no negativos.
        """
        if start_id not in graph.nodes or target_id not in graph.nodes:
            return PathResult(found=False, nodes=[], edges=[], algorithm_used="Dijkstra")

        if start_id == target_id:
            node = graph.nodes[start_id]
            return PathResult(
                found=True,
                nodes=[node],
                edges=[],
                total_distance_km=0.0,
                total_cost=0.0,
                total_time_hours=0.0,
                visited_count=1,
                algorithm_used="Dijkstra",
            )

        # Distancias minimas acumuladas desde el origen
        best_weight: Dict[str, float] = {nid: float("inf") for nid in graph.nodes}
        best_weight[start_id] = 0.0

        # Predecesores para reconstruccion
        previous_node: Dict[str, Optional[str]] = {nid: None for nid in graph.nodes}
        previous_edge: Dict[str, Optional[Edge]] = {nid: None for nid in graph.nodes}

        # Cola de prioridad: (peso_acumulado, contador_orden, node_id)
        pq: List[Tuple[float, int, str]] = []
        counter = 0
        heapq.heappush(pq, (0.0, counter, start_id))

        visited_nodes = set()

        while pq:
            curr_weight, _, curr_id = heapq.heappop(pq)

            if curr_id in visited_nodes:
                continue
            visited_nodes.add(curr_id)

            if curr_id == target_id:
                break

            for edge in graph.adj.get(curr_id, []):
                neighbor = edge.target
                nid = neighbor.id
                if nid in visited_nodes:
                    continue

                step_weight = edge.distance_km if criterion == "distance" else edge.route_cost(cost_per_km)
                tentative = curr_weight + step_weight

                if tentative < best_weight[nid]:
                    best_weight[nid] = tentative
                    previous_node[nid] = curr_id
                    previous_edge[nid] = edge
                    counter += 1
                    heapq.heappush(pq, (tentative, counter, nid))

        if best_weight[target_id] == float("inf"):
            return PathResult(
                found=False,
                nodes=[],
                edges=[],
                visited_count=len(visited_nodes),
                algorithm_used="Dijkstra",
            )

        # Reconstruir camino
        path_nodes: List[Node] = []
        path_edges: List[Edge] = []
        curr = target_id
        while curr is not None:
            path_nodes.append(graph.nodes[curr])
            edge = previous_edge[curr]
            if edge:
                path_edges.append(edge)
            curr = previous_node[curr]

        path_nodes.reverse()
        path_edges.reverse()

        tot_dist = sum(e.distance_km for e in path_edges)
        tot_cost = sum(e.route_cost(cost_per_km) for e in path_edges)
        tot_time = sum(e.travel_time_hours() for e in path_edges)

        return PathResult(
            found=True,
            nodes=path_nodes,
            edges=path_edges,
            total_distance_km=tot_dist,
            total_cost=tot_cost,
            total_time_hours=tot_time,
            visited_count=len(visited_nodes),
            algorithm_used="Dijkstra",
        )

    @staticmethod
    def astar(
        graph: TransportGraph,
        start_id: str,
        target_id: str,
        cost_per_km: float = 2.0,
        criterion: str = "distance",
    ) -> PathResult:
        """
        Busqueda heuristica A* para encontrar la ruta optima.
        Heuristica h(n) admisible y consistente: distancia euclidiana escalada a km.
        """
        if start_id not in graph.nodes or target_id not in graph.nodes:
            return PathResult(found=False, nodes=[], edges=[], algorithm_used="A*")

        if start_id == target_id:
            node = graph.nodes[start_id]
            return PathResult(
                found=True,
                nodes=[node],
                edges=[],
                total_distance_km=0.0,
                total_cost=0.0,
                total_time_hours=0.0,
                visited_count=1,
                algorithm_used="A*",
            )

        target_node = graph.nodes[target_id]

        def heuristic(node: Node) -> float:
            # Distancia euclidiana en pixeles convertida a kilometros referenciales
            pix_dist = math.hypot(target_node.x - node.x, target_node.y - node.y)
            # Factor de escala conservador: 1 pixel ~ 0.35 km
            km_est = pix_dist * 0.30
            if criterion == "cost":
                return km_est * cost_per_km
            return km_est

        g_score: Dict[str, float] = {nid: float("inf") for nid in graph.nodes}
        g_score[start_id] = 0.0

        f_score: Dict[str, float] = {nid: float("inf") for nid in graph.nodes}
        f_score[start_id] = heuristic(graph.nodes[start_id])

        previous_node: Dict[str, Optional[str]] = {nid: None for nid in graph.nodes}
        previous_edge: Dict[str, Optional[Edge]] = {nid: None for nid in graph.nodes}

        open_set: List[Tuple[float, float, int, str]] = []
        counter = 0
        heapq.heappush(open_set, (f_score[start_id], 0.0, counter, start_id))

        closed_set = set()

        while open_set:
            _, current_g, _, curr_id = heapq.heappop(open_set)

            if curr_id in closed_set:
                continue
            closed_set.add(curr_id)

            if curr_id == target_id:
                break

            for edge in graph.adj.get(curr_id, []):
                neighbor = edge.target
                nid = neighbor.id
                if nid in closed_set:
                    continue

                step_weight = edge.distance_km if criterion == "distance" else edge.route_cost(cost_per_km)
                tentative_g = current_g + step_weight

                if tentative_g < g_score[nid]:
                    g_score[nid] = tentative_g
                    f = tentative_g + heuristic(neighbor)
                    f_score[nid] = f
                    previous_node[nid] = curr_id
                    previous_edge[nid] = edge
                    counter += 1
                    heapq.heappush(open_set, (f, tentative_g, counter, nid))

        if g_score[target_id] == float("inf"):
            return PathResult(
                found=False,
                nodes=[],
                edges=[],
                visited_count=len(closed_set),
                algorithm_used="A*",
            )

        # Reconstruccion de la ruta
        path_nodes: List[Node] = []
        path_edges: List[Edge] = []
        curr = target_id
        while curr is not None:
            path_nodes.append(graph.nodes[curr])
            edge = previous_edge[curr]
            if edge:
                path_edges.append(edge)
            curr = previous_node[curr]

        path_nodes.reverse()
        path_edges.reverse()

        tot_dist = sum(e.distance_km for e in path_edges)
        tot_cost = sum(e.route_cost(cost_per_km) for e in path_edges)
        tot_time = sum(e.travel_time_hours() for e in path_edges)

        return PathResult(
            found=True,
            nodes=path_nodes,
            edges=path_edges,
            total_distance_km=tot_dist,
            total_cost=tot_cost,
            total_time_hours=tot_time,
            visited_count=len(closed_set),
            algorithm_used="A*",
        )

    @staticmethod
    def find_alternative_path(
        graph: TransportGraph,
        start_id: str,
        target_id: str,
        optimal_path: PathResult,
        cost_per_km: float = 2.0,
    ) -> Optional[PathResult]:
        """
        Calcula una ruta alternativa secundaria (suboptima o de respaldo)
        penalizando las aristas criticas de la ruta optima. Permite contrastar
        el ahorro cuantitativo obtenido gracias al algoritmo de optimizacion.
        """
        if not optimal_path.found or len(optimal_path.edges) == 0:
            return None

        # Identificar la arista principal a penalizar (la de mayor distancia)
        critical_edge = max(optimal_path.edges, key=lambda e: e.distance_km)

        # Clonar temporalmente pesos o penalizar
        original_dist = critical_edge.distance_km
        critical_edge.distance_km *= 4.0  # Penalizacion de paso

        # Buscar ruta con Dijkstra
        alt_result = PathFinder.dijkstra(graph, start_id, target_id, cost_per_km=cost_per_km)

        # Restaurar peso original
        critical_edge.distance_km = original_dist

        # Si encontramos una ruta y no es exactamente identica, recalculamos metricas reales
        if alt_result.found and alt_result.path_str != optimal_path.path_str:
            real_dist = sum(e.distance_km for e in alt_result.edges)
            real_cost = sum(e.route_cost(cost_per_km) for e in alt_result.edges)
            real_time = sum(e.travel_time_hours() for e in alt_result.edges)
            alt_result.total_distance_km = real_dist
            alt_result.total_cost = real_cost
            alt_result.total_time_hours = real_time
            alt_result.algorithm_used = "Alternativa (Suboptima)"
            return alt_result

        return None
