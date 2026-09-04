"""Pruebas unitarias para el motor estocastico de SimPy."""

import pytest
from src.simulation.reactor_sim import ReactorSimulation
from src.constants import ReactorState


def test_simulation_initialization():
    """Verifica la correcta inicializacion del entorno SimPy y neutrones fuente."""
    sim = ReactorSimulation(enrichment=0.20, initial_rod_insertion=0.50)
    assert sim.env.now == 0.0
    assert len(sim.core.neutrons) > 0
    assert sim.stats.total_fissions == 0


def test_simulation_step_advancement():
    """Verifica que step() avance el reloj de eventos discretos."""
    sim = ReactorSimulation(enrichment=0.20, initial_rod_insertion=0.40)
    assert sim.env.now == 0.0

    # Avanzar 0.5 segundos simulados
    sim.step(0.5)
    assert sim.env.now == pytest.approx(0.5)
    assert sim.current_sim_time == pytest.approx(0.5)


def test_source_injection_and_scram():
    """Verifica la inyeccion de neutrones adicionales y la reaccion al SCRAM."""
    sim = ReactorSimulation(enrichment=0.20, initial_rod_insertion=0.30)
    initial_neutrons = len(sim.core.neutrons)

    sim.inject_neutron_source(count=30)
    assert len(sim.core.neutrons) == initial_neutrons + 30

    # Disparar SCRAM
    sim.core.trigger_scram()
    assert sim.core.is_scrammed is True
    assert sim.core.state == ReactorState.SCRAM
    for rod in sim.core.control_rods:
        assert rod.insertion == 1.0


def test_telemetry_recording():
    """Verifica que el proceso de muestreo recolecte historial en NuclearStats."""
    sim = ReactorSimulation(enrichment=0.20, initial_rod_insertion=0.40)
    # Ejecutar suficiente tiempo para que el loop de muestreo registre muestras
    sim.step(1.0)
    assert len(sim.stats.history_time) > 0
    assert len(sim.stats.history_neutrons) > 0
    assert len(sim.stats.history_keff) > 0
    assert len(sim.stats.history_temperature) > 0
