"""Pruebas unitarias para el motor de eventos discretos SimPy del automercado."""

import pytest
from src.constants import QueueMode, CheckoutState
from src.simulation.market_sim import MarketSimulation


def test_simulation_initial_state():
    """Verifica la inicializacion de cajas y estado del simulador."""
    sim = MarketSimulation(
        num_registers=3,
        arrival_rate_per_min=6.0,
        service_rate_per_min=2.5,
        queue_mode=QueueMode.PARALLEL,
    )

    assert sim.current_sim_time == 0.0
    assert sim.active_registers_count == 3
    assert len(sim.checkouts) == 5
    assert sim.lamb == 6.0
    assert sim.mu == 2.5
    assert sim.queue_mode == QueueMode.PARALLEL


def test_simulation_step_progress():
    """Verifica que el entorno SimPy avance y procese arribos estocasticos."""
    sim = MarketSimulation(
        num_registers=4,
        arrival_rate_per_min=12.0,  # Llegadas rapidas para garantizar arribos
        service_rate_per_min=3.0,
    )

    # Avanzar 30 segundos simulados
    sim.step(30.0)
    assert sim.current_sim_time >= 30.0
    assert sim.stats.total_arrivals > 0


def test_toggle_queue_mode():
    """Verifica el cambio dinamico entre cola unica y colas paralelas."""
    sim = MarketSimulation(queue_mode=QueueMode.PARALLEL)
    assert sim.queue_mode == QueueMode.PARALLEL

    sim.toggle_queue_mode()
    assert sim.queue_mode == QueueMode.SINGLE

    sim.toggle_queue_mode()
    assert sim.queue_mode == QueueMode.PARALLEL


def test_open_close_registers():
    """Verifica habilitacion y deshabilitacion dinamica de cajas registradoras."""
    sim = MarketSimulation(num_registers=2)
    assert sim.active_registers_count == 2

    # Abrir una caja mas
    opened = sim.open_next_register()
    assert opened is True
    assert sim.active_registers_count == 3

    # Cerrar una caja
    closed = sim.close_last_register()
    assert closed is True
    assert sim.active_registers_count == 2
