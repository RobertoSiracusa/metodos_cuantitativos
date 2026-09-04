"""Motor de simulacion por eventos discretos SimPy para el automercado."""

import random
from typing import List, Dict, Optional
import simpy

from src.constants import (
    CustomerState,
    CheckoutState,
    QueueMode,
    DEFAULT_REGISTERS,
    MAX_REGISTERS,
    MIN_REGISTERS,
    DEFAULT_LAMBDA,
    DEFAULT_MU,
    MAX_PARALLEL_QUEUE,
    MAX_SINGLE_QUEUE,
    CHECKOUT_POSITIONS,
    SPAWN_POS,
    ENTRANCE_DOOR,
    CART_STATION,
    AISLE_WAYPOINTS,
    CENTRAL_HALL_Y,
    SINGLE_QUEUE_HEAD,
    EXIT_TURNSTILES,
    EXIT_DOOR,
    EXIT_DESPAWN,
)
from src.models.customer import Customer
from src.models.checkout import CheckoutCounter
from src.models.stats import SimulationStats
from src.models.queue_model import MMCAnalytical, ParallelMM1Analytical


class MarketSimulation:
    """Orquestador de procesos estocasticos concurrentes en SimPy para el automercado."""

    def __init__(
        self,
        num_registers: int = DEFAULT_REGISTERS,
        arrival_rate_per_min: float = DEFAULT_LAMBDA,
        service_rate_per_min: float = DEFAULT_MU,
        queue_mode: QueueMode = QueueMode.PARALLEL,
    ):
        self.num_registers = max(MIN_REGISTERS, min(MAX_REGISTERS, num_registers))
        self.lamb = float(arrival_rate_per_min)
        self.mu = float(service_rate_per_min)
        self.queue_mode = queue_mode

        # Entorno SimPy
        self.env = simpy.Environment()

        # Estaciones de cobro (cajas registradoras) y sus recursos
        self.checkouts: List[CheckoutCounter] = []
        self.checkout_resources: Dict[int, simpy.Resource] = {}
        for i in range(MAX_REGISTERS):
            is_active = i < self.num_registers
            counter = CheckoutCounter(
                counter_id=i + 1,
                position=CHECKOUT_POSITIONS[i],
                is_express=(i == 0),  # Caja 1 express para compras rapidas
                is_active=is_active,
            )
            self.checkouts.append(counter)
            self.checkout_resources[counter.id] = simpy.Resource(self.env, capacity=1)

        # Recurso compartido para el modelo de Cola Unica M/M/c
        self.single_queue_resource = simpy.Resource(self.env, capacity=self.num_registers)

        # Estadisticas
        self.stats = SimulationStats()

        # Colecciones activas de clientes para visualizacion grafica
        self.customers_in_store: List[Customer] = []
        self.single_queue: List[Customer] = []
        self.parallel_queues: Dict[int, List[Customer]] = {c.id: [] for c in self.checkouts}
        self.customers_at_checkout: List[Customer] = []
        self.customers_departing: List[Customer] = []

        self.next_customer_id = 1
        self.is_running = True

        # Iniciar procesos concurrentes
        self.env.process(self._arrival_process())
        self.env.process(self._metrics_sampler_process())

    @property
    def current_sim_time(self) -> float:
        """Tiempo actual del reloj SimPy en segundos."""
        return self.env.now

    @property
    def active_registers_count(self) -> int:
        """Numero de cajas actualmente habilitadas."""
        return sum(1 for c in self.checkouts if c.is_active)

    @property
    def analytical_mmc(self) -> MMCAnalytical:
        """Modelo analitico teorico M/M/c."""
        return MMCAnalytical(lamb=self.lamb, mu=self.mu, c=self.active_registers_count)

    @property
    def analytical_parallel(self) -> ParallelMM1Analytical:
        """Modelo analitico teorico para c colas paralelas c x M/M/1."""
        return ParallelMM1Analytical(lamb=self.lamb, mu=self.mu, c=self.active_registers_count)

    @property
    def current_analytical_model(self):
        """Devuelve el modelo analitico correspondiente a la disciplina activa."""
        if self.queue_mode == QueueMode.SINGLE:
            return self.analytical_mmc
        return self.analytical_parallel

    def set_arrival_rate(self, new_lambda: float):
        """Modifica la tasa de arribos lambda (clientes por minuto)."""
        self.lamb = max(0.5, min(16.0, round(new_lambda, 1)))

    def set_service_rate(self, new_mu: float):
        """Modifica la tasa de atencion mu por caja (clientes por minuto)."""
        self.mu = max(0.5, min(8.0, round(new_mu, 1)))

    def toggle_queue_mode(self):
        """Alterna entre Cola Unica (M/M/c) y Colas Paralelas (c x M/M/1)."""
        if self.queue_mode == QueueMode.PARALLEL:
            self.queue_mode = QueueMode.SINGLE
        else:
            self.queue_mode = QueueMode.PARALLEL

    def open_next_register(self) -> bool:
        """Habilita una caja registradora adicional si hay disponibles."""
        for counter in self.checkouts:
            if not counter.is_active:
                counter.open_counter()
                self.num_registers = self.active_registers_count
                return True
        return False

    def close_last_register(self) -> bool:
        """Cierra la ultima caja activa (manteniendo al menos 1 caja abierta)."""
        if self.active_registers_count <= MIN_REGISTERS:
            return False

        for counter in reversed(self.checkouts):
            if counter.is_active:
                counter.close_counter()
                self.num_registers = self.active_registers_count
                return True
        return False

    def _arrival_process(self):
        """Generador Poisson de arribos estocasticos de clientes."""
        while self.is_running:
            lamb_per_sec = self.lamb / 60.0
            inter_arrival = random.expovariate(lamb_per_sec)
            yield self.env.timeout(inter_arrival)

            # Validar capacidad de cola antes de aceptar el ingreso
            if self._is_queue_saturated():
                self.stats.record_arrival()
                self.stats.record_balk()
                continue

            customer = Customer(
                customer_id=self.next_customer_id,
                arrival_time=self.env.now,
                initial_pos=SPAWN_POS,
            )
            self.next_customer_id += 1
            self.stats.record_arrival()
            self.customers_in_store.append(customer)

            self.env.process(self._customer_lifecycle(customer))

    def _is_queue_saturated(self) -> bool:
        """Verifica si las colas fisicas superan el limite tolerable."""
        if self.queue_mode == QueueMode.SINGLE:
            return len(self.single_queue) >= MAX_SINGLE_QUEUE

        active_counters = [c for c in self.checkouts if c.is_active]
        if not active_counters:
            return True
        # Rechazo si todas las colas individuales alcanzaron su tope
        return all(len(self.parallel_queues[c.id]) >= MAX_PARALLEL_QUEUE for c in active_counters)

    def _customer_lifecycle(self, customer: Customer):
        """Ciclo completo: ingreso -> paseo de compras -> cola -> caja -> salida."""
        # 1. Ingreso a la tienda
        customer.state = CustomerState.ARRIVING
        customer.set_target(ENTRANCE_DOOR[0], ENTRANCE_DOOR[1], angle=0.0)
        yield self.env.timeout(1.2)

        # 2. Tomar carrito en la estacion
        customer.add_waypoint(CART_STATION[0], CART_STATION[1], angle=90.0)
        yield self.env.timeout(0.8)

        # 3. Recorrido por pasillos de gondolas (compras)
        customer.state = CustomerState.SHOPPING
        aisle1 = random.choice(AISLE_WAYPOINTS)
        aisle2 = random.choice(AISLE_WAYPOINTS)
        customer.add_waypoint(aisle1[0], aisle1[1], angle=0.0)
        customer.add_waypoint(aisle2[0], aisle2[1], angle=90.0)
        customer.add_waypoint(aisle2[0], CENTRAL_HALL_Y, angle=90.0)

        # Duracion de compra segun cantidad de items
        shopping_time = 2.0 + (customer.num_items * 0.12)
        yield self.env.timeout(shopping_time)

        # 4. Entrada al sistema de colas
        customer.state = CustomerState.QUEUED
        customer.queue_join_time = self.env.now

        if self.queue_mode == QueueMode.SINGLE:
            yield from self._handle_single_queue_service(customer)
        else:
            yield from self._handle_parallel_queue_service(customer)

    def _handle_single_queue_service(self, customer: Customer):
        """Atencion bajo disciplina de Cola Unica Centralizada (M/M/c)."""
        self.single_queue.append(customer)
        self._update_single_queue_positions()

        # Esperar hasta que alguna caja activa se desocupe
        assigned_counter = None
        while assigned_counter is None and self.is_running:
            # Buscar caja libre entre las activas
            for counter in self.checkouts:
                if counter.is_free:
                    assigned_counter = counter
                    break
            if assigned_counter is None:
                yield self.env.timeout(0.2)

        # Avanzar a la caja asignada
        if customer in self.single_queue:
            self.single_queue.remove(customer)
        self._update_single_queue_positions()

        resource = self.checkout_resources[assigned_counter.id]
        with resource.request() as req:
            yield req
            yield from self._serve_customer_at_counter(customer, assigned_counter)

    def _handle_parallel_queue_service(self, customer: Customer):
        """Atencion bajo disciplina de Colas Paralelas (c x M/M/1) con seleccion de cola mas corta."""
        # Elegir la caja activa con la cola mas corta
        target_counter = self._select_shortest_queue_counter(customer)
        counter_id = target_counter.id

        self.parallel_queues[counter_id].append(customer)
        self._update_parallel_queue_positions(counter_id)

        resource = self.checkout_resources[counter_id]
        with resource.request() as req:
            yield req

            # Retirar de la cola de espera
            if customer in self.parallel_queues[counter_id]:
                self.parallel_queues[counter_id].remove(customer)
            self._update_parallel_queue_positions(counter_id)

            yield from self._serve_customer_at_counter(customer, target_counter)

    def _select_shortest_queue_counter(self, customer: Customer) -> CheckoutCounter:
        """Selecciona la caja registradora activa con menor fila de espera."""
        active_counters = [c for c in self.checkouts if c.is_active]
        if not active_counters:
            return self.checkouts[0]

        # Priorizar caja express si el cliente tiene <= 10 articulos
        if customer.num_items <= 10:
            express_counters = [c for c in active_counters if c.is_express]
            if express_counters:
                best_express = min(express_counters, key=lambda c: len(self.parallel_queues[c.id]))
                if len(self.parallel_queues[best_express.id]) < 4:
                    return best_express

        # Seleccionar la cola mas corta
        return min(active_counters, key=lambda c: len(self.parallel_queues[c.id]))

    def _serve_customer_at_counter(self, customer: Customer, counter: CheckoutCounter):
        """Proceso de atencion, escaneo de articulos, pago y despacho en la caja."""
        counter.assign_customer(customer)
        self.customers_at_checkout.append(customer)

        customer.state = CustomerState.AT_CHECKOUT
        customer.service_start_time = self.env.now

        # Desplazamiento visual al puesto de atencion frente a la cinta
        customer.set_target(counter.x - 15, counter.y, angle=90.0)
        yield self.env.timeout(1.0)

        # Tiempo de servicio exponencial estocastico segun parametro mu
        # Duracion promedio = 60 / mu segundos
        mean_service_s = 60.0 / max(0.1, self.mu)
        actual_service_s = max(3.5, random.expovariate(1.0 / mean_service_s))

        # Fase de escaneo progresivo de articulos (80% del tiempo)
        customer.state = CustomerState.SCANNING
        scan_time = actual_service_s * 0.75
        steps = min(customer.num_items, 10)
        for step in range(steps):
            customer.items_scanned = int((step + 1) * (customer.num_items / steps))
            yield self.env.timeout(scan_time / steps)

        # Fase de pago (25% del tiempo restante)
        customer.state = CustomerState.PAYING
        yield self.env.timeout(actual_service_s * 0.25)

        # Liberacion de caja
        counter.release_customer()
        if customer in self.customers_at_checkout:
            self.customers_at_checkout.remove(customer)

        # Registro de metricas cuantitativas
        customer.state = CustomerState.DEPARTING
        customer.departure_time = self.env.now

        self.stats.record_completed(
            wait_s=customer.wait_time,
            service_s=customer.service_duration,
            total_s=customer.total_system_time,
            items=customer.num_items,
        )

        # Trayectoria de salida hacia los molinetes
        self.customers_departing.append(customer)
        customer.set_target(customer.x - 15, EXIT_TURNSTILES[1] - 30, angle=90.0)
        customer.add_waypoint(EXIT_DOOR[0], EXIT_DOOR[1], angle=0.0)
        customer.add_waypoint(EXIT_DESPAWN[0], EXIT_DESPAWN[1], angle=0.0)

        yield self.env.timeout(3.5)

        if customer in self.customers_departing:
            self.customers_departing.remove(customer)
        if customer in self.customers_in_store:
            self.customers_in_store.remove(customer)

    def _update_single_queue_positions(self):
        """Calcula las coordenadas de cada cliente en la fila unica central."""
        head_x, head_y = SINGLE_QUEUE_HEAD
        for i, customer in enumerate(self.single_queue):
            # Fila vertical serpenteante
            target_x = head_x
            target_y = max(240, head_y - (i * 26))
            customer.set_target(target_x, target_y, angle=90.0)

    def _update_parallel_queue_positions(self, counter_id: int):
        """Calcula las posiciones lineales de la cola de una caja especifica."""
        counter = next((c for c in self.checkouts if c.id == counter_id), None)
        if not counter:
            return

        cx, cy = counter.x, counter.y
        queue = self.parallel_queues[counter_id]
        for i, customer in enumerate(queue):
            target_x = cx - 15
            target_y = max(250, (cy - 50) - (i * 26))
            customer.set_target(target_x, target_y, angle=90.0)

    def _metrics_sampler_process(self):
        """Muestreo periodico para calcular promedios ponderados en el tiempo."""
        while self.is_running:
            yield self.env.timeout(1.0)
            if self.queue_mode == QueueMode.SINGLE:
                q_len = len(self.single_queue)
            else:
                q_len = sum(len(q) for q in self.parallel_queues.values())

            active_cnt = self.active_registers_count
            busy_cnt = sum(1 for c in self.checkouts if c.is_active and c.state == CheckoutState.BUSY)
            sys_len = q_len + len(self.customers_at_checkout)

            self.stats.sample_state(
                queue_len=q_len,
                system_len=sys_len,
                busy_servers=busy_cnt,
                active_servers=active_cnt,
            )

    def step(self, target_time: float):
        """Avanza el reloj de SimPy de forma determinista hasta target_time."""
        if target_time > self.env.now:
            self.env.run(until=target_time)
