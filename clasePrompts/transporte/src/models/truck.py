"""Modelo POO del camion de carga con cinemática 2D y máquina de estados."""

import math
from typing import List, Optional

from src.constants import (
    LOADING_TIME_SEC,
    UNLOADING_TIME_SEC,
    TruckState,
    TruckType,
)
from src.models.graph import Node
from src.models.order import TransportOrder
from src.models.pathfinding import PathResult


class Truck:
    """Entidad camion con cinemática continua, estados operacionales y capacidad."""

    def __init__(
        self,
        truck_id: int,
        name: str,
        truck_type: TruckType,
        initial_node: Node,
    ):
        self.id = truck_id
        self.name = name
        self.truck_type = truck_type
        self.capacity_tons = truck_type.capacity_tons
        self.cost_per_km = truck_type.cost_km
        self.speed_px = truck_type.speed_px

        self.state = TruckState.DISPONIBLE
        self.current_node = initial_node
        self.target_node: Optional[Node] = None

        # Posicion continua en pantalla
        self.x = initial_node.x
        self.y = initial_node.y
        self.angle = 0.0  # Grados de rotacion

        # Carga actual
        self.current_cargo_tons = 0.0
        self.current_order: Optional[TransportOrder] = None

        # Plan de navegacion
        self.navigation_queue: List[Node] = []
        self.reposition_target: Optional[Node] = None
        self.delivery_nodes: List[Node] = []
        self.current_segment_index = 0
        self.segment_progress = 0.0
        self.segment_total_dist = 0.0

        # Temporizadores de operaciones de carga/descarga
        self.timer = 0.0

        # Metricas acumuladas del vehiculo
        self.total_km_traveled = 0.0
        self.total_tons_delivered = 0.0
        self.trips_completed = 0
        self.total_cost_incurred = 0.0

    @property
    def is_available(self) -> bool:
        """Determina si el camion puede aceptar un nuevo servicio."""
        return self.state == TruckState.DISPONIBLE

    def assign_mission(
        self,
        order: TransportOrder,
        reposition_path: Optional[PathResult],
        delivery_path: PathResult,
    ):
        """Asigna una orden y programa el itinerario de viaje."""
        self.current_order = order
        self.delivery_nodes = list(delivery_path.nodes)

        # Si el camion ya esta en el origen del pedido
        if self.current_node.id == order.origin_id:
            self.state = TruckState.CARGANDO
            self.timer = LOADING_TIME_SEC
            self.navigation_queue = list(self.delivery_nodes)
            self.current_segment_index = 0
            self._setup_next_segment()
        else:
            # Debe viajar primero al origen a buscar la mercancia
            self.state = TruckState.EN_TRANSITO_ORIGEN
            self.navigation_queue = list(reposition_path.nodes) if reposition_path else [self.current_node]
            self.current_segment_index = 0
            self._setup_next_segment()

    def _setup_next_segment(self):
        """Configura el siguiente tramo entre dos nodos consecutivos."""
        if self.current_segment_index + 1 < len(self.navigation_queue):
            start_n = self.navigation_queue[self.current_segment_index]
            end_n = self.navigation_queue[self.current_segment_index + 1]
            self.target_node = end_n

            dx = end_n.x - start_n.x
            dy = end_n.y - start_n.y
            self.segment_total_dist = math.hypot(dx, dy)
            self.segment_progress = 0.0

            # Orientar hacia la meta en grados
            self.angle = math.degrees(math.atan2(dy, dx))
        else:
            self.target_node = None
            self.segment_total_dist = 0.0
            self.segment_progress = 0.0

    def update(self, dt: float, sim_time: float = 0.0):
        """Actualiza la cinemática, temporizadores y transiciones de estado."""
        if self.state == TruckState.DISPONIBLE:
            return

        if self.state == TruckState.CARGANDO:
            self.timer -= dt
            if self.timer <= 0:
                # Carga completada
                if self.current_order:
                    self.current_cargo_tons = self.current_order.cargo_tons
                    self.current_node.fulfill(0.0)  # Origen despacha
                self.state = TruckState.EN_RUTA
                self.navigation_queue = list(self.delivery_nodes)
                self.current_segment_index = 0
                self._setup_next_segment()
            return

        if self.state == TruckState.DESCARGANDO:
            self.timer -= dt
            if self.timer <= 0:
                # Descarga completada
                if self.current_order:
                    self.total_tons_delivered += self.current_cargo_tons
                    self.current_node.fulfill(self.current_cargo_tons)
                    self.current_order.mark_delivered(sim_time)
                    self.trips_completed += 1

                self.current_cargo_tons = 0.0
                self.current_order = None
                self.state = TruckState.DISPONIBLE
                self.target_node = None
            return

        # Movimiento continuo hacia el nodo objetivo
        if self.target_node is not None and self.segment_total_dist > 0:
            step_px = self.speed_px * dt
            self.segment_progress += step_px

            start_n = self.navigation_queue[self.current_segment_index]
            end_n = self.target_node

            t = min(1.0, self.segment_progress / self.segment_total_dist)
            self.x = start_n.x + (end_n.x - start_n.x) * t
            self.y = start_n.y + (end_n.y - start_n.y) * t

            # Registrar distancia proporcional en km
            km_advance = (step_px * 0.30)
            self.total_km_traveled += km_advance
            self.total_cost_incurred += km_advance * self.cost_per_km

            if t >= 1.0:
                # Llegada al nodo del tramo
                self.current_node = end_n
                self.x = end_n.x
                self.y = end_n.y
                self.current_segment_index += 1

                if self.current_segment_index + 1 < len(self.navigation_queue):
                    self._setup_next_segment()
                else:
                    # Fin del recorrido actual
                    self._on_navigation_finished()

    def _on_navigation_finished(self):
        """Maneja el arribo al destino final de la ruta programada."""
        if self.state == TruckState.EN_TRANSITO_ORIGEN:
            # Llego al origen del pedido -> Comenzar carga
            self.state = TruckState.CARGANDO
            self.timer = LOADING_TIME_SEC
            self.target_node = None
        elif self.state == TruckState.EN_RUTA:
            # Llego al cliente/destino final -> Comenzar descarga
            self.state = TruckState.DESCARGANDO
            self.timer = UNLOADING_TIME_SEC
            self.target_node = None
        else:
            self.state = TruckState.DISPONIBLE
            self.target_node = None

    def __repr__(self) -> str:
        return f"Truck({self.name}, {self.state.value}, cargo={self.current_cargo_tons}/{self.capacity_tons}t)"
