"""Motor de simulacion discreta en SimPy para la dinamica nuclear y termohidraulica."""

import math
import random
from typing import List, Optional
import simpy

from src.constants import (
    CORE_CENTER_X,
    CORE_CENTER_Y,
    NeutronEnergy,
    NU_PROMPT_MIN,
    NU_PROMPT_MAX,
    BETA_DELAYED,
    LAMBDA_PRECURSOR,
    P_MODERATE,
    P_FISSION_U235,
    P_CAPTURE_U235,
    P_CAPTURE_U238,
    P_ABSORB_ROD,
    P_REFLECTOR_BOUNCE,
    MAX_ACTIVE_NEUTRONS,
    DEFAULT_ROD_INSERTION,
)
from src.models.particle import Neutron, FissionBurst
from src.models.reactor_core import ReactorCore
from src.models.stats import NuclearStats


class ReactorSimulation:
    """Orquesta los procesos estocasticos concurrentes del reactor en SimPy."""

    def __init__(
        self,
        enrichment: float = 0.20,
        initial_rod_insertion: float = DEFAULT_ROD_INSERTION,
    ):
        self.enrichment = float(enrichment)
        self.initial_rod_insertion = float(initial_rod_insertion)

        self.env = simpy.Environment()
        self.core = ReactorCore(
            enrichment=self.enrichment,
            initial_rod_insertion=self.initial_rod_insertion,
        )
        self.stats = NuclearStats()

        self.current_sim_time = 0.0
        self.recent_fissions = 0

        # Iniciar procesos concurrentes en el entorno SimPy
        self.env.process(self._cycle_process())
        self.env.process(self._thermal_hydraulics_process())
        self.env.process(self._telemetry_sampling_process())

        # Inyeccion inicial de neutrones para arrancar el sistema
        self.inject_neutron_source(count=20)

    def inject_neutron_source(self, count: int = 15):
        """Inyecta un pulso de neutrones fuente en el centro del reactor (ej. emisor Cf-252)."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, 50.0)
            nx = self.core.center_x + dist * math.cos(angle)
            ny = self.core.center_y + dist * math.sin(angle)

            neutron = Neutron(
                x=nx,
                y=ny,
                energy=NeutronEnergy.FAST,
                generation=0,
            )
            self.core.neutrons.append(neutron)

    def _delayed_neutron_precursor(self, x: float, y: float):
        """Proceso SimPy que modela el decaimiento de un precursor de neutrones retardados."""
        delay = random.expovariate(LAMBDA_PRECURSOR)
        yield self.env.timeout(delay)

        if len(self.core.neutrons) < MAX_ACTIVE_NEUTRONS:
            dn = Neutron(
                x=x,
                y=y,
                energy=NeutronEnergy.THERMAL,
                generation=0,
            )
            self.core.neutrons.append(dn)

    def _cycle_process(self):
        """Proceso discreto de transporte neutrónico, interacciones y colisiones."""
        dt = 0.04  # 40ms por intervalo de transporte
        while True:
            yield self.env.timeout(dt)

            fissions_in_step = 0
            surviving_neutrons: List[Neutron] = []
            newborn_neutrons: List[Neutron] = []

            # 1. Actualizar barras de control
            for rod in self.core.control_rods:
                rod.update(dt)

            # 2. Actualizar efectos visuales
            for assembly in self.core.fuel_assemblies:
                assembly.update(dt)

            for burst in self.core.fission_bursts:
                burst.update(dt)
            self.core.fission_bursts = [b for b in self.core.fission_bursts if b.alive]

            # 3. Procesar cada neutrón libre
            for n in self.core.neutrons:
                n.update(dt)

                # Comprobar moderación en agua (rápido -> térmico)
                if n.energy == NeutronEnergy.FAST and random.random() < (P_MODERATE * dt * 8.0):
                    n.moderate()

                # Comprobar absorción en barras de control
                absorbed_in_rod = False
                for rod in self.core.control_rods:
                    if rod.can_absorb_at(n.x, n.y):
                        if random.random() < P_ABSORB_ROD:
                            rod.record_absorption()
                            self.stats.record_rod_absorption()
                            absorbed_in_rod = True
                            break
                if absorbed_in_rod:
                    continue

                # Comprobar colisión con combustible
                hit_fuel = False
                for assembly in self.core.fuel_assemblies:
                    pellet = assembly.check_interaction(n.x, n.y)
                    if pellet:
                        hit_fuel = True
                        if pellet.is_u235:
                            # Uranio-235: Fisión o captura radiativa
                            if n.energy == NeutronEnergy.THERMAL:
                                p_fiss = P_FISSION_U235
                            else:
                                p_fiss = P_FISSION_U235 * 0.35  # Sección eficaz menor para rápidos

                            if random.random() < p_fiss:
                                # ¡FISION NUCLEAR!
                                fissions_in_step += 1
                                pellet.record_fission()
                                self.core.fission_bursts.append(FissionBurst(n.x, n.y))

                                # Neutrones prontos emitidos (2 o 3)
                                num_born = random.randint(NU_PROMPT_MIN, NU_PROMPT_MAX)
                                self.stats.record_fission(num_born)

                                for _ in range(num_born):
                                    if len(surviving_neutrons) + len(newborn_neutrons) < MAX_ACTIVE_NEUTRONS:
                                        new_n = Neutron(
                                            x=n.x,
                                            y=n.y,
                                            energy=NeutronEnergy.FAST,
                                            generation=n.generation + 1,
                                        )
                                        newborn_neutrons.append(new_n)

                                # Probabilidad de producir un precursor retardado
                                if random.random() < BETA_DELAYED:
                                    self.env.process(self._delayed_neutron_precursor(n.x, n.y))
                            else:
                                # Captura radiativa sin fisión
                                self.stats.record_fuel_capture()
                        else:
                            # Uranio-238: Captura fértil (aumenta con temperatura / Doppler)
                            self.stats.record_fuel_capture()
                        break  # Termina interacción con este neutrón

                if hit_fuel:
                    continue

                # Comprobar borde del núcleo y reflector
                dx = n.x - self.core.center_x
                dy = n.y - self.core.center_y
                dist = math.sqrt(dx * dx + dy * dy)

                if dist > self.core.active_radius:
                    if dist <= self.core.vessel_radius:
                        # Zona del reflector perimetral
                        if random.random() < P_REFLECTOR_BOUNCE:
                            # Rebote elástico hacia el interior
                            nx_norm = -dx / dist
                            ny_norm = -dy / dist
                            n.bounce(nx_norm, ny_norm)
                            surviving_neutrons.append(n)
                        else:
                            self.stats.record_escape()
                    else:
                        # Escapa de la vasija
                        self.stats.record_escape()
                else:
                    surviving_neutrons.append(n)

            # Actualizar lista de neutrones vivos
            total_neutrons = surviving_neutrons + newborn_neutrons
            if len(total_neutrons) > MAX_ACTIVE_NEUTRONS:
                total_neutrons = total_neutrons[-MAX_ACTIVE_NEUTRONS:]
            self.core.neutrons = total_neutrons
            self.recent_fissions += fissions_in_step

    def _thermal_hydraulics_process(self):
        """Proceso SimPy que modela el balance de calor y temperatura del núcleo."""
        dt = 0.10
        while True:
            yield self.env.timeout(dt)
            self.core.update_thermal_hydraulics(dt, self.recent_fissions)
            self.stats.fission_rate_per_sec = (self.recent_fissions / dt)
            self.recent_fissions = 0

    def _telemetry_sampling_process(self):
        """Muestreo periódico de telemetría e instrumentación."""
        dt = 0.20
        while True:
            yield self.env.timeout(dt)
            self.stats.record_sample(
                sim_time=self.env.now,
                active_neutrons=len(self.core.neutrons),
                k_eff=self.core.k_eff,
                temperature=self.core.temperature,
                power_mw=self.core.thermal_power_mw,
            )

    def step(self, target_sim_time: float):
        """Avanza el reloj de eventos de SimPy hasta el tiempo objetivo."""
        if target_sim_time > self.env.now:
            self.env.run(until=target_sim_time)
            self.current_sim_time = self.env.now
