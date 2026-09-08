"""Pruebas de la simulacion estocastica de eventos discretos SimPy."""

import pytest
from src.simulation.gas_station_sim import GasStationSimulation
from src.constants import PumpState, VehicleState


def test_simulation_initial_state():
    """Verifica el estado inicial de los recursos y tanques."""
    sim = GasStationSimulation(num_pumps=3, arrival_rate_per_min=3.0, service_rate_per_min=2.0)

    assert len(sim.pumps) == 3
    for pump in sim.pumps:
        assert pump.is_free is True
        assert pump.state == PumpState.FREE

    assert sim.tank.level > 0
    assert sim.tank.percent > 50.0
    assert len(sim.vehicles_in_queue) == 0


def test_simulation_step_progress():
    """Verifica que el entorno SimPy avance el tiempo deterministamente."""
    sim = GasStationSimulation(num_pumps=3, arrival_rate_per_min=6.0, service_rate_per_min=3.0)

    sim.step(15.0)
    assert sim.current_sim_time >= 15.0
    assert sim.stats.total_arrivals > 0


def test_tank_consumption_and_refill():
    """Comprueba las extracciones y recargas sobre el tanque central."""
    sim = GasStationSimulation(num_pumps=3)
    initial_fuel = sim.tank.level

    dispensed = sim.tank.withdraw(100.0)
    assert dispensed == 100.0
    assert sim.tank.level == initial_fuel - 100.0

    refilled = sim.tank.refill(50.0)
    assert refilled == 50.0
    assert sim.tank.level == initial_fuel - 50.0


def test_tanker_truck_trigger():
    """Verifica la invocacion del camion cisterna."""
    sim = GasStationSimulation(num_pumps=3)
    sim.tank.withdraw(1500.0)
    prev_level = sim.tank.level

    sim.trigger_tanker_truck()
    assert sim.tank.is_refilling is True

    # Avanzar tiempo suficiente para que el camion llegue y descargue
    sim.step(sim.current_sim_time + 15.0)
    assert sim.tank.is_refilling is False
    assert sim.tank.level > prev_level
