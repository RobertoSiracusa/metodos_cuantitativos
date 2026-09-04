"""Modelo de orden de transporte y despacho de carga."""

from typing import Optional


class TransportOrder:
    """Representa un pedido de carga que debe transportarse entre un origen y un destino."""

    def __init__(
        self,
        order_id: int,
        origin_id: str,
        destination_id: str,
        cargo_tons: float,
        priority: int = 2,
        created_at: float = 0.0,
    ):
        self.id = order_id
        self.origin_id = origin_id
        self.destination_id = destination_id
        self.cargo_tons = float(cargo_tons)
        self.priority = priority
        self.created_at = float(created_at)

        self.status = "PENDIENTE"  # "PENDIENTE", "EN_PROCESO", "ENTREGADO"
        self.assigned_truck_id: Optional[int] = None
        self.optimal_distance_km: float = 0.0
        self.optimal_cost: float = 0.0
        self.alt_cost: float = 0.0
        self.savings: float = 0.0
        self.delivered_at: Optional[float] = None

    def mark_assigned(self, truck_id: int, opt_distance: float, opt_cost: float, alt_cost: float = 0.0):
        """Asigna el camion y registra las metricas de costo estimadas."""
        self.status = "EN_PROCESO"
        self.assigned_truck_id = truck_id
        self.optimal_distance_km = opt_distance
        self.optimal_cost = opt_cost
        self.alt_cost = max(alt_cost, opt_cost)
        self.savings = max(0.0, self.alt_cost - self.optimal_cost)

    def mark_delivered(self, completion_time: float):
        """Marca la orden como satisfecha en el destino."""
        self.status = "ENTREGADO"
        self.delivered_at = completion_time

    def __repr__(self) -> str:
        return f"Order(#{self.id}: {self.origin_id} -> {self.destination_id}, {self.cargo_tons}t, {self.status})"
