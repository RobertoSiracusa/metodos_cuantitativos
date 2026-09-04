"""Motor de simulacion por eventos discretos SimPy para la estacion de servicio."""

import random
from typing import List, Optional, Dict
import simpy

from src.constants import (
    VehicleState,
    PumpState,
    DEFAULT_SERVERS,
    DEFAULT_LAMBDA,
    DEFAULT_MU,
    MAX_QUEUE_CAPACITY,
    MIN_FUEL_REQ,
    MAX_FUEL_REQ,
    TANK_CAPACITY,
    TANK_INITIAL,
    TANKER_RELOAD_AMOUNT,
    PUMP_POSITIONS,
    ENTRY_SPAWN,
    QUEUE_HEAD,
    EXIT_MERGE,
    EXIT_DESPAWN,
)
from src.models.vehicle import Vehicle
from src.models.pump import FuelPump
from src.models.tank import FuelTank
from src.models.stats import SimulationStats
from src.models.queue_model import MMCAnalytical


class GasStationSimulation:
    """Orquestador de procesos estocasticos concurrentes en SimPy."""

    def __init__(
        self,
        num_pumps: int = DEFAULT_SERVERS,
        arrival_rate_per_min: float = DEFAULT_LAMBDA,
        service_rate_per_min: float = DEFAULT_MU,
        max_queue: int = MAX_QUEUE_CAPACITY,
    ):
        self.num_pumps = num_pumps
        self.lamb = arrival_rate_per_min
        self.mu = service_rate_per_min
        self.max_queue = max_queue

        # Entorno SimPy
        self.env = simpy.Environment()
        self.pump_resource = simpy.Resource(self.env, capacity=self.num_pumps)

        # Entidades del dominio
        self.tank = FuelTank(TANK_CAPACITY, TANK_INITIAL)
        self.pumps: List[FuelPump] = [
            FuelPump(pump_id=i + 1, position=PUMP_POSITIONS[i])
            for i in range(min(num_pumps, len(PUMP_POSITIONS)))
        ]
        self.stats = SimulationStats()

        # Colecciones activas para renderizado visual
        self.vehicles_in_queue: List[Vehicle] = []
        self.vehicles_active: List[Vehicle] = []  # En transito o en bomba
        self.vehicles_departing: List[Vehicle] = []

        self.next_vehicle_id = 1
        self.is_running = True

        # Iniciar procesos concurrentes
        self.env.process(self._arrival_process())
        self.env.process(self._metrics_sampler_process())

    @property
    def current_sim_time(self) -> float:
        """Tiempo actual del reloj SimPy en segundos."""
        return self.env.now

    @property
    def analytical_model(self) -> MMCAnalytical:
        """Calculadora analitica teorica con los parametros actuales."""
        return MMCAnalytical(lamb=self.lamb, mu=self.mu, c=self.num_pumps)

    def set_arrival_rate(self, new_lambda: float):
        """Ajusta dinamicamente la tasa de llegada (vehiculos/minuto)."""
        self.lamb = max(0.5, min(12.0, new_lambda))

    def set_service_rate(self, new_mu: float):
        """Ajusta dinamicamente la tasa de servicio (vehiculos/minuto por bomba)."""
        self.mu = max(0.5, min(6.0, new_mu))

    def trigger_tanker_truck(self):
        """Despacha un camion cisterna para reabastecer el tanque."""
        if not self.tank.is_refilling:
            self.tank.is_refilling = True
            self.env.process(self._tanker_process())

    def _arrival_process(self):
        """Generador de Poisson para arribos estocasticos de vehiculos."""
        while self.is_running:
            # Intervalo exponencial entre llegadas (lambda vehiculos/min -> seg = 60 / lambda)
            lamb_per_sec = self.lamb / 60.0
            inter_arrival = random.expovariate(lamb_per_sec)
            yield self.env.timeout(inter_arrival)

            # Verificar si la cola fisica alcanzo la capacidad maxima
            if len(self.vehicles_in_queue) >= self.max_queue:
                self.stats.record_arrival()
                self.stats.record_balk()
                continue

            # Crear nuevo vehiculo
            fuel_req = random.uniform(MIN_FUEL_REQ, MAX_FUEL_REQ)
            vehicle = Vehicle(
                vehicle_id=self.next_vehicle_id,
                arrival_time=self.env.now,
                fuel_requested=fuel_req,
                initial_pos=ENTRY_SPAWN,
            )
            self.next_vehicle_id += 1
            self.stats.record_arrival()

            # Lanzar proceso de atencion del vehiculo
            self.env.process(self._vehicle_lifecycle_process(vehicle))

    def _vehicle_lifecycle_process(self, vehicle: Vehicle):
        """Ciclo de vida de un vehiculo: llegada -> cola -> servicio -> salida."""
        self.vehicles_in_queue.append(vehicle)
        vehicle.state = VehicleState.QUEUED

        # Solicitar atencion en una de las bombas disponibles
        req = self.pump_resource.request()
        yield req

        # Bomba asignada
        self.vehicles_in_queue.remove(vehicle)
        vehicle.service_start_time = self.env.now

        # Asignar a un surtidor libre fisico
        assigned_pump = self._find_free_pump()
        if not assigned_pump:
            assigned_pump = self.pumps[0]

        assigned_pump.assign_vehicle(vehicle)
        self.vehicles_active.append(vehicle)
        vehicle.state = VehicleState.MOVING_TO_PUMP

        # Traslado hacia la bomba (tiempo de desplazamiento)
        yield self.env.timeout(2.5)

        # Inicio de recarga
        vehicle.state = VehicleState.FUELING

        # Duracion del servicio: modelada exponencialmente segun mu (o normal)
        # Media = 60 / mu segundos
        mean_service_s = 60.0 / self.mu
        # Asegurar un minimo de 4 segundos y variabilidad estocastica
        actual_service_s = max(4.0, random.expovariate(1.0 / mean_service_s))

        # Despachar combustible del tanque central progresivamente
        dispensed = self.tank.withdraw(vehicle.fuel_requested)
        vehicle.fuel_dispensed = dispensed

        yield self.env.timeout(actual_service_s * 0.8)

        # Transaccion de pago
        vehicle.state = VehicleState.PAYING
        yield self.env.timeout(actual_service_s * 0.2)

        # Liberar recurso de SimPy y bomba fisica
        self.pump_resource.release(req)
        assigned_pump.release_vehicle()

        # Salida del vehiculo
        vehicle.state = VehicleState.DEPARTING
        vehicle.departure_time = self.env.now

        self.vehicles_active.remove(vehicle)
        self.vehicles_departing.append(vehicle)

        # Registrar metricas cuantitativas
        self.stats.record_completed(
            wait_s=vehicle.wait_time,
            service_s=vehicle.service_duration,
            total_s=vehicle.total_system_time,
        )

        # Esperar a que el vehiculo abandone la vista antes de eliminarlo
        yield self.env.timeout(3.5)
        if vehicle in self.vehicles_departing:
            self.vehicles_departing.remove(vehicle)

    def _tanker_process(self):
        """Proceso de arribo y descarga de camion cisterna."""
        self.tank.is_refilling = True
        # Tiempo de viaje del camion
        yield self.env.timeout(8.0)
        # Descarga
        self.tank.refill(TANKER_RELOAD_AMOUNT)
        yield self.env.timeout(4.0)
        self.tank.is_refilling = False

    def _metrics_sampler_process(self):
        """Muestreo temporal periodico para calcular promedios de colas."""
        while self.is_running:
            yield self.env.timeout(1.0)
            q_len = len(self.vehicles_in_queue)
            sys_len = q_len + len(self.vehicles_active)
            self.stats.sample_state(q_len, sys_len)

            # Reabastecimiento automatico de emergencia si cae de 15%
            if self.tank.percent < 15.0 and not self.tank.is_refilling:
                self.trigger_tanker_truck()

    def _find_free_pump(self) -> Optional[FuelPump]:
        """Busca el primer surtidor fisico desocupado."""
        for pump in self.pumps:
            if pump.is_free:
                return pump
        return None

    def step(self, target_time: float):
        """Avanza el reloj de SimPy de forma determinista hasta target_time."""
        if target_time > self.env.now:
            self.env.run(until=target_time)
