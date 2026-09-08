"""Gestion de flota, asignacion de rutas y cola de ordenes logisticas."""

import random
from typing import Dict, List, Optional, Tuple

from src.constants import INITIAL_FLEET_CONFIG
from src.models.graph import TransportGraph
from src.models.order import TransportOrder
from src.models.pathfinding import PathFinder, PathResult
from src.models.truck import Truck


class FleetManager:
    """Administrador de la flota de camiones y despacho optimizado de pedidos."""

    def __init__(self, graph: TransportGraph):
        self.graph = graph
        self.trucks: List[Truck] = []
        self.pending_orders: List[TransportOrder] = []
        self.completed_orders: List[TransportOrder] = []
        self.order_counter = 1

        self._init_fleet()

    def _init_fleet(self):
        """Inicializa los camiones segun la configuracion base."""
        for cfg in INITIAL_FLEET_CONFIG:
            init_node = self.graph.get_node(cfg["initial_node"])
            if not init_node:
                init_node = list(self.graph.nodes.values())[0]

            truck = Truck(
                truck_id=cfg["id"],
                name=cfg["name"],
                truck_type=cfg["type"],
                initial_node=init_node,
            )
            self.trucks.append(truck)

    def create_order(
        self,
        origin_id: str,
        destination_id: str,
        cargo_tons: float,
        priority: int = 2,
        sim_time: float = 0.0,
    ) -> TransportOrder:
        """Crea y encola una nueva solicitud de transporte."""
        order = TransportOrder(
            order_id=self.order_counter,
            origin_id=origin_id,
            destination_id=destination_id,
            cargo_tons=cargo_tons,
            priority=priority,
            created_at=sim_time,
        )
        self.order_counter += 1
        self.pending_orders.append(order)
        return order

    def dispatch_order(
        self,
        order: TransportOrder,
        algorithm: str = "dijkstra",
        sim_time: float = 0.0,
    ) -> Optional[Tuple[Truck, PathResult, PathResult]]:
        """
        Asigna el camion mas optimo disponible para cumplir la orden.
        Criterio cuantitativo de asignacion:
          Minimizar Costo Total = Costo_reposicion(camion -> origen) + Costo_viaje(origen -> destino).
          Sujeto a: Capacidad_camion >= Demanda_orden.
        """
        eligible_trucks = [t for t in self.trucks if t.is_available and t.capacity_tons >= order.cargo_tons]

        if not eligible_trucks:
            return None

        finder_fn = PathFinder.astar if algorithm.lower() in ["astar", "a*"] else PathFinder.dijkstra

        best_truck: Optional[Truck] = None
        best_total_cost = float("inf")
        best_reposition_path: Optional[PathResult] = None
        best_delivery_path: Optional[PathResult] = None
        best_alt_cost = 0.0

        for truck in eligible_trucks:
            # 1. Ruta de reposicion si el camion no esta en el origen
            if truck.current_node.id != order.origin_id:
                reposition_path = finder_fn(
                    self.graph,
                    truck.current_node.id,
                    order.origin_id,
                    cost_per_km=truck.cost_per_km,
                )
                if not reposition_path.found:
                    continue
                repos_cost = reposition_path.total_cost
            else:
                reposition_path = PathResult(
                    found=True,
                    nodes=[truck.current_node],
                    edges=[],
                    total_distance_km=0.0,
                    total_cost=0.0,
                    algorithm_used=algorithm,
                )
                repos_cost = 0.0

            # 2. Ruta optima de entrega desde origen hasta destino
            delivery_path = finder_fn(
                self.graph,
                order.origin_id,
                order.destination_id,
                cost_per_km=truck.cost_per_km,
            )
            if not delivery_path.found:
                continue

            deliv_cost = delivery_path.total_cost
            total_eval_cost = repos_cost + deliv_cost

            # 3. Evaluar alternativa suboptima para calculo de ahorro
            alt_path = PathFinder.find_alternative_path(
                self.graph,
                order.origin_id,
                order.destination_id,
                delivery_path,
                cost_per_km=truck.cost_per_km,
            )
            alt_cost = alt_path.total_cost if alt_path and alt_path.found else deliv_cost * 1.35

            if total_eval_cost < best_total_cost:
                best_total_cost = total_eval_cost
                best_truck = truck
                best_reposition_path = reposition_path
                best_delivery_path = delivery_path
                best_alt_cost = alt_cost

        if best_truck and best_delivery_path:
            # Asignar mision al camion elegido
            best_truck.assign_mission(order, best_reposition_path, best_delivery_path)
            order.mark_assigned(
                truck_id=best_truck.id,
                opt_distance=best_delivery_path.total_distance_km,
                opt_cost=best_delivery_path.total_cost,
                alt_cost=best_alt_cost,
            )
            if order in self.pending_orders:
                self.pending_orders.remove(order)
            return best_truck, best_reposition_path, best_delivery_path

        return None

    def process_pending_orders(self, algorithm: str = "dijkstra", sim_time: float = 0.0) -> int:
        """Intenta despachar las ordenes pendientes en cola."""
        dispatched_count = 0
        for order in list(self.pending_orders):
            res = self.dispatch_order(order, algorithm=algorithm, sim_time=sim_time)
            if res is not None:
                dispatched_count += 1
        return dispatched_count

    def generate_random_order(self, sim_time: float = 0.0) -> Optional[TransportOrder]:
        """Genera estocasticamente una orden de transporte entre dos nodos validos."""
        nodes = list(self.graph.nodes.values())
        if len(nodes) < 2:
            return None

        # Preferir orígenes con oferta o tipo HUB
        hubs = [n for n in nodes if n.node_type == "HUB" or n.supply > 0]
        cities = [n for n in nodes if n.node_type == "CITY"]

        origin = random.choice(hubs if hubs else nodes)
        possible_destinations = [n for n in (cities if cities else nodes) if n.id != origin.id]
        if not possible_destinations:
            return None
        destination = random.choice(possible_destinations)

        # Carga aleatoria coherente con capacidades de la flota (3 a 25 toneladas)
        cargo = round(random.uniform(4.0, 24.0), 1)

        return self.create_order(
            origin_id=origin.id,
            destination_id=destination.id,
            cargo_tons=cargo,
            priority=random.choice([1, 2]),
            sim_time=sim_time,
        )

    def update(self, dt: float, sim_time: float = 0.0):
        """Actualiza el movimiento y estado de todos los camiones."""
        for truck in self.trucks:
            prev_order = truck.current_order
            truck.update(dt, sim_time=sim_time)
            # Detectar ordenes recien entregadas
            if prev_order and prev_order.status == "ENTREGADO" and prev_order not in self.completed_orders:
                self.completed_orders.append(prev_order)

    def get_fleet_summary(self) -> Dict[str, any]:
        """Resumen analitico cuantitativo de la flota."""
        total_km = sum(t.total_km_traveled for t in self.trucks)
        total_tons = sum(t.total_tons_delivered for t in self.trucks)
        total_trips = sum(t.trips_completed for t in self.trucks)
        total_cost = sum(t.total_cost_incurred for t in self.trucks)
        total_savings = sum(o.savings for o in self.completed_orders)

        available_count = sum(1 for t in self.trucks if t.is_available)

        return {
            "total_camiones": len(self.trucks),
            "camiones_disponibles": available_count,
            "camiones_en_servicio": len(self.trucks) - available_count,
            "ordenes_entregadas": len(self.completed_orders),
            "ordenes_pendientes": len(self.pending_orders),
            "toneladas_entregadas": round(total_tons, 2),
            "kilometros_totales": round(total_km, 2),
            "costo_total_operativo": round(total_cost, 2),
            "ahorro_total_optimizacion": round(total_savings, 2),
        }
