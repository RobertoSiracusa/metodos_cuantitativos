"""Pruebas unitarias para la entidad Customer y su cinematica top-down."""

import pytest
from src.constants import CustomerState
from src.models.customer import Customer


def test_customer_creation_and_attributes():
    """Verifica atributos iniciales, asignacion de items y colores."""
    c = Customer(customer_id=1, arrival_time=10.0, initial_pos=(50, 50), num_items=12)
    assert c.id == 1
    assert c.arrival_time == 10.0
    assert c.num_items == 12
    assert c.items_remaining == 12
    assert c.state == CustomerState.ARRIVING
    assert len(c.item_colors) == 12
    assert (c.x, c.y) == (50.0, 50.0)


def test_customer_motion_interpolation():
    """Verifica desplazamiento hacia waypoints y rotacion angular."""
    c = Customer(customer_id=2, arrival_time=0.0, initial_pos=(0, 0))
    c.speed = 100.0  # 100 px/s

    # Moverse hacia (100, 0)
    c.set_target(100.0, 0.0, angle=0.0)
    assert len(c.waypoints) == 1

    # Actualizar dt = 0.5 s -> debe avanzar 50 px en x
    c.update_motion(0.5)
    assert round(c.x, 1) == 50.0
    assert round(c.y, 1) == 0.0

    # Actualizar dt = 0.6 s -> debe alcanzar el objetivo (100, 0)
    c.update_motion(0.6)
    assert round(c.x, 1) == 100.0
    assert round(c.y, 1) == 0.0
    assert len(c.waypoints) == 0


def test_customer_duration_metrics():
    """Verifica calculo de tiempos operacionales (espera, servicio, permanencia)."""
    c = Customer(customer_id=3, arrival_time=5.0, initial_pos=(0, 0))
    c.queue_join_time = 10.0
    c.service_start_time = 25.0
    c.departure_time = 40.0

    # Espera en cola = 25 - 10 = 15 s
    assert c.wait_time == 15.0
    # Duracion del servicio = 40 - 25 = 15 s
    assert c.service_duration == 15.0
    # Tiempo total en sistema = 40 - 5 = 35 s
    assert c.total_system_time == 35.0
