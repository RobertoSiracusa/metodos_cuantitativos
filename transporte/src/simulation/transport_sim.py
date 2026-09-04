"""Motor de simulacion cuantitativa de transporte y asignacion de rutas."""

from typing import Any, Dict, Optional

from src.constants import AUTO_ORDER_INTERVAL_SEC
from src.models.fleet_manager import FleetManager
from src.models.graph import Node, TransportGraph
from src.models.order import TransportOrder
from src.models.pathfinding import PathFinder, PathResult


class TransportSimulation:
    """Motor central que gestiona el tiempo simulado, generacion de demanda y flujo de flota."""

    def __init__(self, algorithm: str = "dijkstra", auto_mode: bool = False):
        self.graph = TransportGraph.build_default_network()
        self.fleet_manager = FleetManager(self.graph)
        self.algorithm = algorithm
        self.auto_mode = auto_mode

        self.sim_time = 0.0
        self.order_timer = 2.0  # Primer pedido automatico temprano

        # Seleccion interactiva de nodos por el usuario
        self.selected_origin: Optional[Node] = self.graph.get_node("VAL")
        self.selected_dest: Optional[Node] = self.graph.get_node("CCS")

        # Calculo de ruta previa entre seleccion actual
        self.preview_path: Optional[PathResult] = None
        self.preview_alt_path: Optional[PathResult] = None
        self.update_preview_path()

    def select_node(self, node: Node):
        """Maneja la seleccion interactiva de origen y destino por clic del usuario."""
        if self.selected_origin is None or (self.selected_origin is not None and self.selected_dest is not None):
            self.selected_origin = node
            self.selected_dest = None
            self.preview_path = None
            self.preview_alt_path = None
        elif self.selected_dest is None and node.id != self.selected_origin.id:
            self.selected_dest = node
            self.update_preview_path()

    def update_preview_path(self):
        """Recalcula la ruta optima y la alternativa entre el origen y destino seleccionados."""
        if not self.selected_origin or not self.selected_dest:
            self.preview_path = None
            self.preview_alt_path = None
            return

        finder_fn = PathFinder.astar if self.algorithm.lower() in ["astar", "a*"] else PathFinder.dijkstra
        self.preview_path = finder_fn(
            self.graph,
            self.selected_origin.id,
            self.selected_dest.id,
            cost_per_km=2.10,  # Costo referencial de camion mediano
        )

        if self.preview_path.found:
            self.preview_alt_path = PathFinder.find_alternative_path(
                self.graph,
                self.selected_origin.id,
                self.selected_dest.id,
                self.preview_path,
                cost_per_km=2.10,
            )
        else:
            self.preview_alt_path = None

    def toggle_algorithm(self):
        """Alterna entre Dijkstra y A*."""
        self.algorithm = "astar" if self.algorithm.lower() == "dijkstra" else "dijkstra"
        self.update_preview_path()

    def toggle_auto_mode(self):
        """Activa o desactiva la generacion estocastica continua de pedidos."""
        self.auto_mode = not self.auto_mode

    def dispatch_selected_route(self, cargo_tons: float = 12.0) -> Optional[TransportOrder]:
        """Despacha un nuevo camion para la ruta seleccionada manualmente."""
        if not self.selected_origin or not self.selected_dest:
            return None

        order = self.fleet_manager.create_order(
            origin_id=self.selected_origin.id,
            destination_id=self.selected_dest.id,
            cargo_tons=cargo_tons,
            priority=1,
            sim_time=self.sim_time,
        )
        self.fleet_manager.dispatch_order(order, algorithm=self.algorithm, sim_time=self.sim_time)
        return order

    def step(self, dt: float):
        """Avanza la simulacion en un delta de tiempo dt."""
        self.sim_time += dt

        # Generador automatico de pedidos si auto_mode esta encendido
        if self.auto_mode:
            self.order_timer -= dt
            if self.order_timer <= 0:
                new_order = self.fleet_manager.generate_random_order(sim_time=self.sim_time)
                if new_order:
                    self.fleet_manager.dispatch_order(new_order, algorithm=self.algorithm, sim_time=self.sim_time)
                self.order_timer = AUTO_ORDER_INTERVAL_SEC

        # Despachar ordenes pendientes si hay camiones que se liberaron
        self.fleet_manager.process_pending_orders(algorithm=self.algorithm, sim_time=self.sim_time)

        # Actualizar cinemática de flota
        self.fleet_manager.update(dt, sim_time=self.sim_time)

    def get_metrics(self) -> Dict[str, Any]:
        """Retorna el compendio de metricas globales de la simulacion."""
        summary = self.fleet_manager.get_fleet_summary()
        summary["tiempo_simulado_seg"] = round(self.sim_time, 1)
        summary["algoritmo_activo"] = self.algorithm.upper()
        summary["modo_automatico"] = "Activo" if self.auto_mode else "Manual"
        return summary
