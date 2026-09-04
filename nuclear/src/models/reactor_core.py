"""Modelo fisico y geometrico del nucleo del reactor (vasija, combustible y barras)."""

import math
from typing import List, Optional
from src.constants import (
    CORE_CENTER_X,
    CORE_CENTER_Y,
    VESSEL_RADIUS,
    CORE_ACTIVE_RADIUS,
    FUEL_GRID_ROWS,
    FUEL_GRID_COLS,
    FUEL_PITCH,
    CONTROL_ROD_COLUMNS,
    CONTROL_ROD_ROWS,
    DEFAULT_ROD_INSERTION,
    T_INLET_COOLANT,
    T_WARNING_FUEL,
    T_MELTDOWN_FUEL,
    HEAT_CAPACITY_CORE,
    COOLING_COEFF_PUMPS_ON,
    COOLING_COEFF_PUMPS_OFF,
    ALPHA_DOPPLER,
    ReactorState,
)
from src.models.fuel_element import FuelAssembly
from src.models.control_rod import ControlRod
from src.models.particle import Neutron, FissionBurst


class ReactorCore:
    """Representa la estructura nuclear completa, su balance termico y estado cinetico."""

    def __init__(
        self,
        center_x: float = CORE_CENTER_X,
        center_y: float = CORE_CENTER_Y,
        vessel_radius: float = VESSEL_RADIUS,
        active_radius: float = CORE_ACTIVE_RADIUS,
        enrichment: float = 0.20,
        initial_rod_insertion: float = DEFAULT_ROD_INSERTION,
    ):
        self.center_x = float(center_x)
        self.center_y = float(center_y)
        self.vessel_radius = float(vessel_radius)
        self.active_radius = float(active_radius)
        self.enrichment = float(enrichment)

        # Componentes estructurales
        self.fuel_assemblies: List[FuelAssembly] = []
        self.control_rods: List[ControlRod] = []
        self.neutrons: List[Neutron] = []
        self.fission_bursts: List[FissionBurst] = []

        # Estado termohidraulico
        self.temperature = T_INLET_COOLANT
        self.coolant_pumps_active = True
        self.pump_speed = 1.0
        self.thermal_power_mw = 0.0

        # Estado operacional
        self.state = ReactorState.SHUTDOWN
        self.k_eff = 1.00
        self.is_scrammed = False

        self._build_lattice(initial_rod_insertion)

    def _build_lattice(self, initial_rod_insertion: float):
        """Construye la matriz geometrica de ensambles y canales de barras de control."""
        self.fuel_assemblies.clear()
        self.control_rods.clear()

        half_w = (FUEL_GRID_COLS - 1) * FUEL_PITCH / 2.0
        half_h = (FUEL_GRID_ROWS - 1) * FUEL_PITCH / 2.0

        rod_id_counter = 0

        for r in range(FUEL_GRID_ROWS):
            for c in range(FUEL_GRID_COLS):
                x = self.center_x - half_w + c * FUEL_PITCH
                y = self.center_y - half_h + r * FUEL_PITCH

                # Verificar si cae dentro del radio activo del nucleo
                dx = x - self.center_x
                dy = y - self.center_y
                dist_from_center = math.sqrt(dx * dx + dy * dy)

                if dist_from_center <= self.active_radius:
                    # Determinar si este nodo es un canal de barra de control
                    if r in CONTROL_ROD_ROWS and c in CONTROL_ROD_COLUMNS:
                        rod = ControlRod(
                            rod_id=rod_id_counter,
                            center_x=x,
                            center_y=y,
                            radius=16.0,
                            initial_insertion=initial_rod_insertion,
                        )
                        self.control_rods.append(rod)
                        rod_id_counter += 1
                    else:
                        # Ensamble de combustible
                        assembly = FuelAssembly(
                            grid_row=r,
                            grid_col=c,
                            center_x=x,
                            center_y=y,
                            enrichment=self.enrichment,
                        )
                        self.fuel_assemblies.append(assembly)

    def get_average_rod_insertion(self) -> float:
        """Calcula el porcentaje promedio de insercion de las barras de control (0.0 - 1.0)."""
        if not self.control_rods:
            return 0.0
        return sum(rod.insertion for rod in self.control_rods) / len(self.control_rods)

    def set_control_rods_insertion(self, insertion: float):
        """Ajusta de forma sincronizada todas las barras de control."""
        for rod in self.control_rods:
            rod.target_insertion = max(0.0, min(1.0, float(insertion)))

    def adjust_control_rods(self, delta: float):
        """Ajusta incrementalmente las barras de control."""
        for rod in self.control_rods:
            rod.adjust_insertion(delta)

    def trigger_scram(self):
        """Dispara el SCRAM de emergencia en todas las barras."""
        self.is_scrammed = True
        self.state = ReactorState.SCRAM
        for rod in self.control_rods:
            rod.trigger_scram()

    def reset_scram(self, reset_level: float = DEFAULT_ROD_INSERTION):
        """Restaura el control manual tras un SCRAM."""
        self.is_scrammed = False
        for rod in self.control_rods:
            rod.reset_scram(reset_level)

    def toggle_coolant_pumps(self):
        """Alterna el funcionamiento de las bombas principales de refrigeracion."""
        self.coolant_pumps_active = not self.coolant_pumps_active

    def calculate_keff(self) -> float:
        """
        Calcula el Factor de Multiplicacion Efectivo (k_eff) macroscopicamente
        usando la formula de los factores con reactividad de barras y Doppler.
        """
        # Factor infinito en funcion del enriquecimiento
        k_inf = 1.05 + (self.enrichment * 1.0)  # ej. 0.20 -> 1.25
        p_non_leakage = 0.94                    # Probabilidad de no escape

        # Reactividad negativa de barras de control
        rod_worth = 0.42
        avg_insertion = self.get_average_rod_insertion()
        rod_factor = 1.0 - (rod_worth * avg_insertion)

        # Realimentacion por efecto Doppler termico (disminuye reactividad si calienta)
        delta_t = max(0.0, self.temperature - T_INLET_COOLANT)
        doppler_factor = 1.0 - (ALPHA_DOPPLER * delta_t)

        k = k_inf * p_non_leakage * rod_factor * doppler_factor
        self.k_eff = max(0.0, k)
        return self.k_eff

    def update_thermal_hydraulics(self, dt: float, fissions_in_interval: int):
        """Modela la primera ley de la termodinamica en el nucleo del reactor."""
        # Generacion de calor proporcional a la tasa de fisuras
        heat_gen_rate = fissions_in_interval * 24.0  # MW normalizados
        self.thermal_power_mw = heat_gen_rate

        # Extraccion de calor por refrigerante
        cooling_coeff = COOLING_COEFF_PUMPS_ON if self.coolant_pumps_active else COOLING_COEFF_PUMPS_OFF
        cooling_rate = cooling_coeff * (self.temperature - T_INLET_COOLANT)

        # Balance diferencial de temperatura
        dt_temp = ((heat_gen_rate - cooling_rate) / HEAT_CAPACITY_CORE) * dt
        self.temperature = max(T_INLET_COOLANT, self.temperature + dt_temp)

        # Actualizar clasificacion del estado del reactor
        k = self.calculate_keff()

        if self.is_scrammed:
            self.state = ReactorState.SCRAM
        elif self.temperature >= T_WARNING_FUEL and k > 1.03:
            self.state = ReactorState.PROMPT_CRITICAL
        elif k > 1.01:
            self.state = ReactorState.SUPERCRITICAL
        elif 0.99 <= k <= 1.01:
            self.state = ReactorState.CRITICAL
        elif len(self.neutrons) == 0 and self.thermal_power_mw < 0.1:
            self.state = ReactorState.SHUTDOWN
        else:
            self.state = ReactorState.SUBCRITICAL
