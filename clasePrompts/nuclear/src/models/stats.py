"""Contabilidad de metricas estocasticas, telemetria e historial de variables de estado."""

from typing import List
from src.constants import T_INLET_COOLANT


class NuclearStats:
    """Registro cuantitativo de eventos nucleares y muestreo de series temporales."""

    def __init__(self):
        self.total_fissions = 0
        self.total_neutrons_born = 0
        self.total_absorbed_rods = 0
        self.total_captured_fuel = 0
        self.total_escaped = 0
        self.scram_events = 0

        # Metricas instantaneas
        self.active_neutrons = 0
        self.thermal_power_mw = 0.0
        self.k_eff = 1.00
        self.core_temperature = T_INLET_COOLANT
        self.fission_rate_per_sec = 0.0

        # Series temporales para graficos de instrumentacion (max 120 puntos)
        self.max_history_len = 120
        self.history_time: List[float] = []
        self.history_neutrons: List[int] = []
        self.history_keff: List[float] = []
        self.history_temperature: List[float] = []
        self.history_power: List[float] = []

    def record_sample(
        self,
        sim_time: float,
        active_neutrons: int,
        k_eff: float,
        temperature: float,
        power_mw: float,
    ):
        """Almacena una muestra para telemetria y graficos en tiempo real."""
        self.active_neutrons = active_neutrons
        self.k_eff = k_eff
        self.core_temperature = temperature
        self.thermal_power_mw = power_mw

        self.history_time.append(round(sim_time, 2))
        self.history_neutrons.append(active_neutrons)
        self.history_keff.append(round(k_eff, 4))
        self.history_temperature.append(round(temperature, 1))
        self.history_power.append(round(power_mw, 2))

        if len(self.history_time) > self.max_history_len:
            self.history_time.pop(0)
            self.history_neutrons.pop(0)
            self.history_keff.pop(0)
            self.history_temperature.pop(0)
            self.history_power.pop(0)

    def record_fission(self, num_neutrons_born: int):
        """Registra una fision individual."""
        self.total_fissions += 1
        self.total_neutrons_born += num_neutrons_born

    def record_rod_absorption(self):
        """Registra la absorcion de un neutron en barra de control."""
        self.total_absorbed_rods += 1

    def record_fuel_capture(self):
        """Registra la captura parasitaria o fertil en el combustible."""
        self.total_captured_fuel += 1

    def record_escape(self):
        """Registra un neutron que escapa de la vasija."""
        self.total_escaped += 1
