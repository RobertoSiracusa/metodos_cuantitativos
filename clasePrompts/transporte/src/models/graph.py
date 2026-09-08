"""Estructura de datos para la red y grafo de transporte (POO)."""

import math
from typing import Dict, List, Optional, Tuple


class Node:
    """Vertice de la red de transporte (Centro logistico, ciudad o peaje)."""

    def __init__(
        self,
        node_id: str,
        name: str,
        x: float,
        y: float,
        node_type: str = "CITY",
        demand: float = 0.0,
        supply: float = 0.0,
    ):
        self.id = node_id
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.node_type = node_type.upper()  # 'HUB', 'CITY', 'CROSS'
        self.demand = float(demand)         # Demanda requerida en toneladas
        self.supply = float(supply)         # Capacidad de despacho en toneladas
        self.fulfilled_demand = 0.0

    @property
    def remaining_demand(self) -> float:
        """Demanda insatisfecha pendiente por recibir."""
        return max(0.0, self.demand - self.fulfilled_demand)

    def fulfill(self, amount: float):
        """Registra recepcion de mercancia en el nodo destino."""
        self.fulfilled_demand += amount

    def __repr__(self) -> str:
        return f"Node({self.id}, '{self.name}', type={self.node_type})"


class Edge:
    """Arista ponderada que modela un tramo vial entre dos nodos."""

    def __init__(
        self,
        source: Node,
        target: Node,
        distance_km: float,
        toll: float = 0.0,
        speed_limit_kmh: float = 80.0,
    ):
        self.source = source
        self.target = target
        self.distance_km = float(distance_km)
        self.toll = float(toll)
        self.speed_limit_kmh = float(speed_limit_kmh)
        self.pixel_length = math.hypot(target.x - source.x, target.y - source.y)

    def travel_time_hours(self, vehicle_speed_kmh: Optional[float] = None) -> float:
        """Calcula el tiempo de transito estimado en horas."""
        speed = min(vehicle_speed_kmh or self.speed_limit_kmh, self.speed_limit_kmh)
        return self.distance_km / max(speed, 1.0)

    def route_cost(self, cost_per_km: float) -> float:
        """Calcula el costo total del tramo (flete kilometrico + peaje)."""
        return (self.distance_km * cost_per_km) + self.toll

    def __repr__(self) -> str:
        return f"Edge({self.source.id} -> {self.target.id}, {self.distance_km}km)"


class TransportGraph:
    """Grafo de transporte multimodal ponderado para resolucion de redes."""

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.adj: Dict[str, List[Edge]] = {}

    def add_node(
        self,
        node_id: str,
        name: str,
        x: float,
        y: float,
        node_type: str = "CITY",
        demand: float = 0.0,
        supply: float = 0.0,
    ) -> Node:
        """Agrega un nodo a la red."""
        node = Node(node_id, name, x, y, node_type, demand, supply)
        self.nodes[node_id] = node
        if node_id not in self.adj:
            self.adj[node_id] = []
        return node

    def add_edge(
        self,
        u_id: str,
        v_id: str,
        distance_km: float,
        toll: float = 0.0,
        speed_limit_kmh: float = 80.0,
        bidirectional: bool = True,
    ) -> List[Edge]:
        """Agrega un tramo vial entre dos nodos existentes."""
        if u_id not in self.nodes or v_id not in self.nodes:
            raise KeyError(f"Nodos invalidos: {u_id} o {v_id} no existen en el grafo.")

        u_node = self.nodes[u_id]
        v_node = self.nodes[v_id]

        edge_forward = Edge(u_node, v_node, distance_km, toll, speed_limit_kmh)
        self.edges.append(edge_forward)
        self.adj[u_id].append(edge_forward)

        created = [edge_forward]
        if bidirectional:
            edge_backward = Edge(v_node, u_node, distance_km, toll, speed_limit_kmh)
            self.edges.append(edge_backward)
            self.adj[v_id].append(edge_backward)
            created.append(edge_backward)

        return created

    def get_node(self, node_id: str) -> Optional[Node]:
        """Obtiene un nodo por su identificador unico."""
        return self.nodes.get(node_id)

    def get_edge(self, u_id: str, v_id: str) -> Optional[Edge]:
        """Retorna la arista orientada entre dos nodos si existe."""
        if u_id in self.adj:
            for edge in self.adj[u_id]:
                if edge.target.id == v_id:
                    return edge
        return None

    def find_node_at_pos(self, x: float, y: float, radius: float = 24.0) -> Optional[Node]:
        """Busca si una coordenada de raton intersecta un nodo en pantalla."""
        for node in self.nodes.values():
            dist = math.hypot(node.x - x, node.y - y)
            if dist <= radius:
                return node
        return None

    @classmethod
    def build_default_network(cls) -> "TransportGraph":
        """Instancia la red de transporte predeterminada de constants."""
        from src.constants import NETWORK_NODES, NETWORK_EDGES

        graph = cls()
        for n in NETWORK_NODES:
            graph.add_node(
                node_id=n["id"],
                name=n["name"],
                x=n["x"],
                y=n["y"],
                node_type=n["type"],
                demand=n["demand"],
                supply=n["supply"],
            )

        for e in NETWORK_EDGES:
            graph.add_edge(
                u_id=e["u"],
                v_id=e["v"],
                distance_km=e["km"],
                toll=e["toll"],
                speed_limit_kmh=e["speed_limit"],
                bidirectional=True,
            )

        return graph
