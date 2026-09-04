"""Modelo para la entidad Bomba / Surtidor de gasolina."""

from typing import Optional, Tuple
from src.constants import PumpState
from src.models.vehicle import Vehicle


class FuelPump:
    """Entidad que representa un surtidor de combustible individual."""

    def __init__(self, pump_id: int, position: Tuple[int, int]):
        self.id = pump_id
        self.x, self.y = position
        self.state = PumpState.FREE
        self.current_vehicle: Optional[Vehicle] = None

        # Metricas acumuladas de la bomba
        self.total_vehicles_served = 0
        self.total_liters_dispensed = 0.0
        self.total_busy_time = 0.0

    @property
    def is_free(self) -> bool:
        """Determina si la bomba esta disponible para atender un nuevo vehiculo."""
        return self.state == PumpState.FREE

    def assign_vehicle(self, vehicle: Vehicle):
        """Asigna un vehiculo al surtidor e inicia la atencion."""
        self.current_vehicle = vehicle
        self.state = PumpState.BUSY
        vehicle.assigned_pump_id = self.id

    def release_vehicle(self):
        """Libera la bomba tras culminar la recarga y cobro."""
        if self.current_vehicle:
            self.total_vehicles_served += 1
            self.total_liters_dispensed += self.current_vehicle.fuel_dispensed
        self.current_vehicle = None
        self.state = PumpState.FREE
