"""Pruebas para el modelo cinematico y ciclo de vida de los vehiculos."""

from src.models.vehicle import Vehicle
from src.constants import VehicleState


def test_vehicle_motion_interpolation():
    """Verifica el movimiento suave hacia los waypoints."""
    v = Vehicle(vehicle_id=1, arrival_time=0.0, fuel_requested=30.0, initial_pos=(0, 0))

    v.set_target(100.0, 0.0, angle=0.0)
    assert len(v.waypoints) == 1

    # Actualizar con delta time
    v.update_motion(0.2)  # speed = 220 px/s -> avanza ~44 px
    assert v.x > 30.0
    assert v.x < 100.0

    # Actualizar tiempo suficiente para alcanzar el objetivo
    v.update_motion(1.0)
    assert v.x == 100.0
    assert len(v.waypoints) == 0


def test_vehicle_duration_metrics():
    """Verifica el calculo de tiempos de espera y servicio."""
    v = Vehicle(vehicle_id=1, arrival_time=10.0, fuel_requested=40.0, initial_pos=(0, 0))

    assert v.wait_time == 0.0

    v.service_start_time = 15.0
    assert v.wait_time == 5.0

    v.departure_time = 25.0
    assert v.service_duration == 10.0
    assert v.total_system_time == 15.0
