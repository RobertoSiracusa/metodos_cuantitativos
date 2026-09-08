"""Pruebas unitarias de modelos fisicos: particulas, combustible, barras y nucleo."""

import pytest
import math
from src.constants import (
    NeutronEnergy,
    V_FAST,
    V_THERMAL,
    T_INLET_COOLANT,
    ReactorState,
)
from src.models.particle import Neutron, FissionBurst
from src.models.fuel_element import FuelPellet, FuelAssembly
from src.models.control_rod import ControlRod
from src.models.reactor_core import ReactorCore


def test_neutron_lifecycle_and_moderation():
    """Verifica la cinematica y moderacion del neutron."""
    n = Neutron(x=100.0, y=100.0, energy=NeutronEnergy.FAST, angle_rad=0.0)
    assert n.energy == NeutronEnergy.FAST
    assert math.isclose(n.vx, V_FAST, rel_tol=1e-3)
    assert math.isclose(n.vy, 0.0, abs_tol=1e-3)

    # Actualizar posicion en 0.1s
    n.update(0.1)
    assert n.x > 100.0
    assert n.age == pytest.approx(0.1)

    # Moderar a neutron termico
    n.moderate()
    assert n.energy == NeutronEnergy.THERMAL
    current_speed = math.hypot(n.vx, n.vy)
    assert math.isclose(current_speed, V_THERMAL, rel_tol=1e-3)


def test_neutron_bounce():
    """Verifica el rebote elastico contra una normal reflectora."""
    n = Neutron(x=0, y=0, energy=NeutronEnergy.FAST, angle_rad=0.0)
    n.vx = 100.0
    n.vy = 0.0
    # Normal que apunta a la izquierda (-1, 0)
    n.bounce(-1.0, 0.0)
    assert n.vx == pytest.approx(-100.0)
    assert n.vy == pytest.approx(0.0)


def test_fuel_pellet_interaction():
    """Verifica la deteccion de colisiones e intensidad luminosa."""
    pellet = FuelPellet(x=50.0, y=50.0, is_u235=True, radius=10.0)
    assert pellet.contains_point(50.0, 50.0)
    assert pellet.contains_point(55.0, 50.0)
    assert not pellet.contains_point(80.0, 80.0)

    # Registro de fision
    pellet.record_fission()
    assert pellet.fissions_count == 1
    assert pellet.glow_intensity == 1.0

    pellet.cool_down(0.2)
    assert pellet.glow_intensity < 1.0


def test_control_rod_insertion_and_scram():
    """Verifica la mecanica de insercion, absorcion y SCRAM de barras de control."""
    rod = ControlRod(rod_id=1, center_x=200.0, center_y=200.0, radius=15.0, initial_insertion=0.5)
    assert rod.insertion == 0.5
    assert rod.target_insertion == 0.5

    # Ajuste incremental
    rod.adjust_insertion(0.2)
    assert rod.target_insertion == pytest.approx(0.7)

    # No debe superar 1.0
    rod.adjust_insertion(0.5)
    assert rod.target_insertion == 1.0

    # Activar SCRAM de emergencia
    rod.trigger_scram()
    assert rod.is_scrammed is True
    assert rod.insertion == 1.0
    assert rod.target_insertion == 1.0

    # Mientras este scrammed, no debe responder a ajustes
    rod.adjust_insertion(-0.3)
    assert rod.target_insertion == 1.0

    # Resetear scram
    rod.reset_scram(reset_level=0.4)
    assert rod.is_scrammed is False
    assert rod.target_insertion == 0.4


def test_reactor_core_lattice_and_keff():
    """Verifica la geometria del nucleo, k_eff y termohidraulica."""
    core = ReactorCore(enrichment=0.20, initial_rod_insertion=0.50)
    assert len(core.fuel_assemblies) > 0
    assert len(core.control_rods) > 0

    # Con barras a 50%, reactor debe ser subcritico (k < 1.0)
    k_initial = core.calculate_keff()
    assert k_initial < 1.0

    # Si se extraen totalmente las barras (0%), k_eff debe ser marcadamente mayor (supercritico)
    core.set_control_rods_insertion(0.0)
    for rod in core.control_rods:
        rod.insertion = 0.0
    k_withdrawn = core.calculate_keff()
    assert k_withdrawn > k_initial
    assert k_withdrawn > 1.0

    # Si se insertan al 100% (SCRAM), k_eff cae profundamente
    core.set_control_rods_insertion(1.0)
    for rod in core.control_rods:
        rod.insertion = 1.0
    k_scram = core.calculate_keff()
    assert k_scram < k_initial

    # Efecto Doppler: a mayor temperatura, menor reactividad
    core.temperature = 1200.0
    k_hot = core.calculate_keff()
    core.temperature = T_INLET_COOLANT
    k_cold = core.calculate_keff()
    assert k_hot < k_cold
