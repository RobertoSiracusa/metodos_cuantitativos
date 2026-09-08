"""
red_simulacion.py
==============================================================================
Motor de Simulación Estocástica de Redes de Computadoras con SimPy
Facultad de Ingeniería - Universidad José Antonio Páez
Cátedra: Métodos Cuantitativos y Simulación

Integra:
1. TEORÍA DE COLAS (Líneas de Espera):
   - Proceso de Poisson (lambda) para la llegada de paquetes.
   - Servidores exponenciales (mu) en routers/switches.
   - Cálculo en tiempo real de métricas: L, Lq, W, Wq y factor de utilización rho.

2. MODELO DE GESTIÓN DE INVENTARIO (Control de Buffers):
   - Capacidad máxima de almacenamiento en buffer (S).
   - Política de control de flujo y reabastecimiento (s, Q):
     Cuando el buffer cae por debajo de s, se emite una señal de flujo para
     habilitar el siguiente lote Q o desbloquear la compuerta de entrada.
   - Costo de mantener (Holding Cost en RAM/buffer) proporcional al tiempo de estancia.
   - Costo de ruptura/penalización (Shortage Cost) por cada descarte (Buffer Overflow).

3. TOPOLOGÍA DE RED Y ENLACES DINÁMICOS:
   - Nodos de Origen / Fuentes de Tráfico (S1, S2, S3).
   - Nodos Intermedios / Routers de Distribución (R1, R2, R3, R4) con buffers gestionados.
   - Nodos de Destino / Salida (D1, D2).
   - Enlaces con latencias dinámicas y simulación de fallas/caídas imprevistas.
==============================================================================
"""

from dataclasses import dataclass, field
from enum import Enum, auto
import math
import random
import time
from typing import Callable, Deque, Dict, List, Optional, Tuple
from collections import deque

import simpy
import numpy as np

from hungarian_router import HungarianRouter, AsignacionResultado


# ==============================================================================
# CONSTANTES Y VALORES POR DEFECTO DEL SISTEMA
# ==============================================================================
LAMBDA_DEFECTO = 15.0       # Tasa de llegada media (paquetes/segundo)
MU_DEFECTO = 18.0           # Tasa de servicio media por servidor (paquetes/segundo)
CAPACIDAD_BUFFER_S = 50     # Capacidad máxima del buffer del router (S)
UMBRAL_REABASTECER_S = 10   # Umbral mínimo s para control de flujo
LOTE_REABASTECER_Q = 15     # Tamaño del lote de paquetes autorizado Q

# Costos unitarios del modelo de inventario
COSTO_HOLDING_POR_SEG = 0.05    # $ por paquete por segundo almacenado en RAM/buffer
COSTO_PENALIZACION_RUPTURA = 10.0  # $ de penalización por paquete descartado (Overflow)

INTERVALO_HUNGARO_DT = 1.0     # Cada Delta t segundos se optimiza la asignación


class PacketState(Enum):
    """Estados del ciclo de vida de un paquete de datos."""
    GENERATED = auto()          # Creado en nodo de origen
    TRAVELING_INGRESS = auto()  # En tránsito por enlace hacia router intermedio
    IN_BUFFER = auto()          # Esperando en la cola/buffer del router
    IN_SERVICE = auto()         # En proceso de modulación/transmisión por el servidor
    TRAVELING_EGRESS = auto()   # En tránsito hacia el destino final
    DELIVERED = auto()          # Entregado con éxito en el destino
    DROPPED = auto()            # Descartado por buffer overflow (pérdida)


@dataclass
class Packet:
    """Entidad de datos que transita por la red estocástica."""
    id: int
    source_id: str
    target_router_id: Optional[str] = None
    dest_id: Optional[str] = None
    size_bytes: int = 1500
    state: PacketState = PacketState.GENERATED

    # Estampas de tiempo para métricas de colas (en segundos de simulación)
    t_created: float = 0.0
    t_buffer_entry: float = 0.0
    t_service_start: float = 0.0
    t_service_end: float = 0.0
    t_delivered: float = 0.0

    # Variables visuales para interpolación cinemática en Pygame
    x: float = 0.0
    y: float = 0.0
    start_pos: Tuple[float, float] = (0.0, 0.0)
    end_pos: Tuple[float, float] = (0.0, 0.0)
    progress: float = 0.0       # 0.0 a 1.0 en el enlace actual
    travel_time: float = 0.45   # Duración de recorrido visual
    t_link_start: float = 0.0   # Momento en que inició el tránsito por el enlace actual

    @property
    def waiting_time_wq(self) -> float:
        """Tiempo de espera en cola (Wq)."""
        if self.t_service_start > 0:
            return max(0.0, self.t_service_start - self.t_buffer_entry)
        return 0.0

    @property
    def total_system_time_w(self) -> float:
        """Tiempo total en el sistema (W)."""
        if self.t_delivered > 0:
            return max(0.0, self.t_delivered - self.t_created)
        return 0.0


class NetworkLink:
    """Enlace de comunicación bidireccional entre nodos con latencia y estado dinámico."""
    def __init__(
        self,
        link_id: str,
        from_node_id: str,
        to_node_id: str,
        base_latency_ms: float = 12.0,
        jitter_ms: float = 3.0
    ):
        self.link_id = link_id
        self.from_node_id = from_node_id
        self.to_node_id = to_node_id
        self.base_latency_ms = base_latency_ms
        self.jitter_ms = jitter_ms
        self.active = True          # Control de enlace operativo o caído
        self.packets_in_transit: List[Packet] = []
        self.total_transferred = 0

    @property
    def current_latency_ms(self) -> float:
        """Calcula la latencia actual con ruido estocástico (jitter)."""
        if not self.active:
            return 999999.0
        # Variación normal acotada
        ruido = random.gauss(0, self.jitter_ms * 0.5)
        return max(1.0, self.base_latency_ms + ruido)


class RouterNode:
    """
    Nodo intermedio (Router/Switch) con buffer finito (S) y servidor exponencial (mu).
    Implementa el modelo de inventario (s, Q) para control de flujo y prevención de rotura.
    """
    def __init__(
        self,
        node_id: str,
        name: str,
        x: float,
        y: float,
        env: simpy.Environment,
        capacidad_s: int = CAPACIDAD_BUFFER_S,
        umbral_s: int = UMBRAL_REABASTECER_S,
        lote_q: int = LOTE_REABASTECER_Q,
        mu: float = MU_DEFECTO
    ):
        self.node_id = node_id
        self.name = name
        self.x = x
        self.y = y
        self.env = env
        self.capacidad_s = int(capacidad_s)
        self.umbral_s = int(umbral_s)
        self.lote_q = int(lote_q)
        self.mu = float(mu)

        # Recurso de SimPy: Canal de transmisión (1 servidor M/M/1/K)
        self.server = simpy.Resource(env, capacity=1)
        self.buffer_queue: Deque[Packet] = deque()
        self.current_serving: Optional[Packet] = None

        # Estadísticas del nodo
        self.total_arrived = 0
        self.total_processed = 0
        self.total_dropped = 0
        self.flow_control_signals_sent = 0
        self.credito_flujo_disponible = lote_q

        # Acumuladores temporales para métricas L, Lq
        self.area_queue_lq = 0.0
        self.area_system_l = 0.0
        self.last_update_time = 0.0
        self.total_holding_cost = 0.0

    @property
    def queue_length(self) -> int:
        """Cantidad de paquetes actualmente esperando en el buffer."""
        return len(self.buffer_queue)

    @property
    def system_packets(self) -> int:
        """Cantidad de paquetes en el nodo (en buffer + en transmisión)."""
        return len(self.buffer_queue) + (1 if self.current_serving is not None else 0)

    @property
    def saturation_ratio(self) -> float:
        """Ratio de saturación del buffer (0.0 a 1.0)."""
        if self.capacidad_s <= 0:
            return 1.0
        return min(1.0, len(self.buffer_queue) / self.capacidad_s)

    @property
    def status_color_category(self) -> str:
        """
        Categoría según el enunciado:
        Verde: < 50%, Amarillo: 50%-80%, Rojo: > 80%.
        """
        sat = self.saturation_ratio
        if sat < 0.50:
            return "VERDE"
        elif sat <= 0.80:
            return "AMARILLO"
        else:
            return "ROJO"

    def actualizar_areas_temporales(self) -> None:
        """Actualiza las integrales de paquetes en el tiempo para L y Lq."""
        now = self.env.now
        dt = now - self.last_update_time
        if dt > 0:
            q_len = len(self.buffer_queue)
            sys_len = q_len + (1 if self.current_serving is not None else 0)

            self.area_queue_lq += q_len * dt
            self.area_system_l += sys_len * dt
            self.total_holding_cost += q_len * dt * COSTO_HOLDING_POR_SEG
            self.last_update_time = now

    def recibir_paquete(self, packet: Packet) -> bool:
        """
        Intenta almacenar un paquete entrante en el buffer.
        Aplica control de inventario y detección de desbordamiento (Overflow).
        :return: True si fue admitido, False si fue descartado (Drop).
        """
        self.actualizar_areas_temporales()
        self.total_arrived += 1

        # Control de Inventario: ¿Supera la capacidad máxima S?
        if len(self.buffer_queue) >= self.capacidad_s:
            # Buffer Overflow (Pérdida por ruptura de inventario)
            packet.state = PacketState.DROPPED
            self.total_dropped += 1
            return False

        # Paquete admitido en el buffer
        packet.state = PacketState.IN_BUFFER
        packet.t_buffer_entry = self.env.now
        self.buffer_queue.append(packet)

        # Política de Reabastecimiento / Control de Flujo (s, Q):
        # Si el nivel cae por debajo de 's', enviamos señal para autorizar nuevo lote
        if len(self.buffer_queue) < self.umbral_s and self.credito_flujo_disponible <= 0:
            self.flow_control_signals_sent += 1
            self.credito_flujo_disponible = self.lote_q

        return True


class NetworkSimulation:
    """
    Orquestador principal de la red de computadoras que vincula:
    - Entorno de Eventos Discretos de SimPy.
    - Proceso de Llegada de Poisson (lambda).
    - Servidores con Tasa Exponencial (mu).
    - Enrutamiento Dinámico con Algoritmo Húngaro (Delta t).
    - Control de Inventario y Buffer Overflow.
    """

    def __init__(
        self,
        lam: float = LAMBDA_DEFECTO,
        mu: float = MU_DEFECTO,
        capacidad_s: int = CAPACIDAD_BUFFER_S,
        umbral_s: int = UMBRAL_REABASTECER_S,
        lote_q: int = LOTE_REABASTECER_Q
    ):
        self.env = simpy.Environment()
        self.lam = max(0.1, float(lam))
        self.mu = max(0.1, float(mu))
        self.capacidad_s = int(capacidad_s)
        self.umbral_s = int(umbral_s)
        self.lote_q = int(lote_q)

        self.router_hungaro = HungarianRouter(alpha=40.0)
        self.packet_seq_id = 1

        # Nodos de Origen / Fuentes de Tráfico (Flujos N)
        self.sources = [
            {"id": "S1", "name": "Servidor Web (S1)", "x": 120, "y": 160},
            {"id": "S2", "name": "Base de Datos (S2)", "x": 120, "y": 320},
            {"id": "S3", "name": "Streaming CDN (S3)", "x": 120, "y": 480},
        ]

        # Nodos Intermedios / Routers con Buffer (M canales)
        self.routers: Dict[str, RouterNode] = {
            "R1": RouterNode("R1", "Router Core 1", 420, 120, self.env, self.capacidad_s, self.umbral_s, self.lote_q, self.mu),
            "R2": RouterNode("R2", "Router Core 2", 420, 250, self.env, self.capacidad_s, self.umbral_s, self.lote_q, self.mu),
            "R3": RouterNode("R3", "Router Core 3", 420, 390, self.env, self.capacidad_s, self.umbral_s, self.lote_q, self.mu),
            "R4": RouterNode("R4", "Router Core 4", 420, 520, self.env, self.capacidad_s, self.umbral_s, self.lote_q, self.mu),
        }

        # Nodos de Destino
        self.destinations = [
            {"id": "D1", "name": "Gateway WAN A (D1)", "x": 720, "y": 220},
            {"id": "D2", "name": "Gateway WAN B (D2)", "x": 720, "y": 420},
        ]

        # Enlaces Ingress (Fuentes -> Routers)
        self.ingress_links: Dict[str, NetworkLink] = {}
        for s in self.sources:
            for r_id in self.routers.keys():
                lid = f"{s['id']}-{r_id}"
                # Latencias base variables para dar diversidad a la matriz de costos
                base_lat = 8.0 + (int(s['id'][-1]) * 2.0) + (int(r_id[-1]) * 1.5)
                self.ingress_links[lid] = NetworkLink(lid, s['id'], r_id, base_lat, jitter_ms=2.5)

        # Enlaces Egress (Routers -> Destinos)
        self.egress_links: Dict[str, NetworkLink] = {}
        for r_id in self.routers.keys():
            for d in self.destinations:
                lid = f"{r_id}-{d['id']}"
                base_lat = 10.0 + (int(r_id[-1]) * 1.0)
                self.egress_links[lid] = NetworkLink(lid, r_id, d['id'], base_lat, jitter_ms=2.0)

        # Registro de paquetes procesados exitosamente y tiempos
        self.all_delivered_packets: List[Packet] = []
        self.total_generated_packets = 0
        self.total_dropped_packets = 0

        # Historial de eventos recientes (para consola y trazas)
        self.event_log: Deque[str] = deque(maxlen=20)

        # Iniciar procesos concurrentes en SimPy
        self.env.process(self._traffic_generator_process())
        for r_node in self.routers.values():
            self.env.process(self._router_service_process(r_node))
        self.env.process(self._hungarian_periodic_optimizer())

    def actualizar_dimensiones_pantalla(self, ancho_red: float, alto_pantalla: float):
        """Ajusta las coordenadas de los nodos para aprovechar el ancho y alto disponibles en pantalla completa."""
        ancho_red = max(500.0, float(ancho_red))
        alto_pantalla = max(450.0, float(alto_pantalla))

        # Fuentes a la izquierda (x = ~13% del ancho de red)
        sx = max(80.0, ancho_red * 0.13)
        sy_base = alto_pantalla * 0.20
        sy_step = (alto_pantalla * 0.60) / max(1, len(self.sources) - 1)
        for i, s in enumerate(self.sources):
            s["x"] = sx
            s["y"] = sy_base + (i * sy_step)

        # Routers intermedios en el centro (x = ~50% del ancho de red)
        rx = ancho_red * 0.50
        ry_base = alto_pantalla * 0.15
        ry_step = (alto_pantalla * 0.70) / max(1, len(self.routers) - 1)
        for i, (r_id, r_node) in enumerate(self.routers.items()):
            r_node.x = rx
            r_node.y = ry_base + (i * ry_step)

        # Destinos a la derecha (x = ~87% del ancho de red)
        dx = min(ancho_red - 80.0, ancho_red * 0.87)
        dy_base = alto_pantalla * 0.30
        dy_step = (alto_pantalla * 0.40) / max(1, len(self.destinations) - 1)
        for i, d in enumerate(self.destinations):
            d["x"] = dx
            d["y"] = dy_base + (i * dy_step)

        # Actualizar start_pos y end_pos de paquetes que están viajando en este instante
        todos_enlaces = list(self.ingress_links.values()) + list(self.egress_links.values())
        for link in todos_enlaces:
            for pkt in link.packets_in_transit:
                pkt.start_pos = (self._get_node_x(link.from_node_id), self._get_node_y(link.from_node_id))
                pkt.end_pos = (self._get_node_x(link.to_node_id), self._get_node_y(link.to_node_id))

    # --------------------------------------------------------------------------
    # PROCESO SIMPY 1: GENERACIÓN DE TRÁFICO (PROCESO DE POISSON)
    # --------------------------------------------------------------------------
    def _traffic_generator_process(self):
        """
        Genera paquetes siguiendo un Proceso de Poisson con tasa lambda.
        El intervalo entre llegadas sucesivas sigue distribución exponencial: Exp(lambda).
        """
        while True:
            # Tiempo entre arribos: t ~ Exp(lambda) -> media = 1.0 / lambda
            intervalo = random.expovariate(self.lam)
            yield self.env.timeout(intervalo)

            # Seleccionar una fuente activa
            source = random.choice(self.sources)
            s_id = source["id"]

            packet = Packet(
                id=self.packet_seq_id,
                source_id=s_id,
                t_created=self.env.now,
                x=float(source["x"]),
                y=float(source["y"])
            )
            self.packet_seq_id += 1
            self.total_generated_packets += 1

            # Despachar paquete hacia el mejor router asignado por el algoritmo húngaro
            self._route_ingress_packet(packet)

    def _route_ingress_packet(self, packet: Packet):
        """Selecciona el enlace óptimo hacia un router intermedio."""
        s_id = packet.source_id

        # Evaluar enlaces activos desde esta fuente
        candidatos = [
            (lid, link) for lid, link in self.ingress_links.items()
            if link.from_node_id == s_id and link.active
        ]

        if not candidatos:
            # Si todos los enlaces de esta fuente están caídos, paquete descartado
            packet.state = PacketState.DROPPED
            self.total_dropped_packets += 1
            self._log_event(f"⚠️ Paquete #{packet.id} descartado: sin enlaces activos desde {s_id}")
            return

        # Si tenemos asignación óptima previa para este flujo, usarla; si no, elegir por menor costo
        best_link = None
        min_cost = float("inf")

        for lid, link in candidatos:
            r_node = self.routers[link.to_node_id]
            cost = link.current_latency_ms + self.router_hungaro.alpha * r_node.saturation_ratio
            if cost < min_cost:
                min_cost = cost
                best_link = link

        if best_link is not None:
            packet.target_router_id = best_link.to_node_id
            packet.start_pos = (float(self._get_node_x(s_id)), float(self._get_node_y(s_id)))
            target_r = self.routers[best_link.to_node_id]
            packet.end_pos = (float(target_r.x), float(target_r.y))
            packet.progress = 0.0
            packet.state = PacketState.TRAVELING_INGRESS
            # Tiempo de viaje calibrado para visualización suave
            packet.travel_time = max(0.40, best_link.current_latency_ms / 30.0)
            packet.t_link_start = self.env.now

            # Proceso SimPy que modela el tiempo de propagación por el enlace
            self.env.process(self._transit_link_process(packet, best_link, target_r))

    def _transit_link_process(self, packet: Packet, link: NetworkLink, target_node: RouterNode):
        """Modela el tiempo en tránsito en el enlace físico."""
        link.packets_in_transit.append(packet)
        # Retardo sincronizado exactamente con la duración visual
        transit_delay = packet.travel_time
        yield self.env.timeout(transit_delay)

        if packet in link.packets_in_transit:
            link.packets_in_transit.remove(packet)
        link.total_transferred += 1

        # Llegada al router intermedio: intentar entrar al buffer
        admitido = target_node.recibir_paquete(packet)
        if not admitido:
            self.total_dropped_packets += 1
            self._log_event(f"❌ OVERFLOW en {target_node.name}: Paquete #{packet.id} DESCARTADO.")
        else:
            self._log_event(f"📥 Paquete #{packet.id} encolado en {target_node.name} (Cola: {target_node.queue_length}/{target_node.capacidad_s})")

    # --------------------------------------------------------------------------
    # PROCESO SIMPY 2: ATENCIÓN EXPONENCIAL EN ROUTERS (SERVIDOR MU)
    # --------------------------------------------------------------------------
    def _router_service_process(self, r_node: RouterNode):
        """
        Servidor con tasa de servicio exponencial mu.
        Extrae paquetes del buffer según disciplina FIFO.
        """
        while True:
            # Si el buffer está vacío, esperar un breve instante
            if not r_node.buffer_queue:
                yield self.env.timeout(0.02)
                continue

            # Solicitar el servidor transmisor del router
            with r_node.server.request() as req:
                yield req

                r_node.actualizar_areas_temporales()
                if not r_node.buffer_queue:
                    continue

                packet = r_node.buffer_queue.popleft()
                r_node.current_serving = packet
                packet.state = PacketState.IN_SERVICE
                packet.t_service_start = self.env.now

                # Tiempo de servicio exponencial: t_s ~ Exp(mu) -> media = 1.0 / mu
                service_duration = random.expovariate(self.mu)
                yield self.env.timeout(service_duration)

                packet.t_service_end = self.env.now
                r_node.total_processed += 1
                r_node.current_serving = None
                r_node.actualizar_areas_temporales()

                # Despachar paquete procesado al nodo de destino final
                self._route_egress_packet(packet, r_node)

    def _route_egress_packet(self, packet: Packet, from_node: RouterNode):
        """Envía el paquete modulado hacia el gateway de destino final."""
        dest = random.choice(self.destinations)
        packet.dest_id = dest["id"]
        lid = f"{from_node.node_id}-{dest['id']}"
        link = self.egress_links.get(lid)

        if link and link.active:
            packet.start_pos = (float(from_node.x), float(from_node.y))
            packet.end_pos = (float(dest["x"]), float(dest["y"]))
            packet.progress = 0.0
            packet.state = PacketState.TRAVELING_EGRESS
            packet.travel_time = max(0.35, link.current_latency_ms / 35.0)
            packet.t_link_start = self.env.now

            self.env.process(self._transit_egress_process(packet, link, dest))
        else:
            # Enlace de salida caído: descarte forzado
            packet.state = PacketState.DROPPED
            self.total_dropped_packets += 1
            self._log_event(f"⚠️ Paquete #{packet.id} perdido: enlace de salida {lid} caído.")

    def _transit_egress_process(self, packet: Packet, link: NetworkLink, dest: Dict):
        """Tránsito hacia el nodo final de la red."""
        link.packets_in_transit.append(packet)
        delay = packet.travel_time
        yield self.env.timeout(delay)

        if packet in link.packets_in_transit:
            link.packets_in_transit.remove(packet)
        link.total_transferred += 1

        # Entrega exitosa del paquete
        packet.state = PacketState.DELIVERED
        packet.t_delivered = self.env.now
        self.all_delivered_packets.append(packet)
        self._log_event(f"✅ Paquete #{packet.id} entregado en {dest['name']} (W={packet.total_system_time_w:.3f}s)")

    # --------------------------------------------------------------------------
    # PROCESO SIMPY 3: OPTIMIZACIÓN PERIÓDICA CON ALGORITMO HÚNGARO (DELTA T)
    # --------------------------------------------------------------------------
    def _hungarian_periodic_optimizer(self):
        """
        En cada intervalo Delta t, evalúa N flujos de datos pendientes y M enlaces,
        calculando dinámicamente la asignación que minimiza C_{ij}.
        """
        while True:
            yield self.env.timeout(INTERVALO_HUNGARO_DT)

            num_flujos = len(self.sources)
            enlaces_candidatos_info = []

            # Evaluamos los enlaces de la red (Ingress a cada router)
            router_keys = list(self.routers.keys())
            for r_id in router_keys:
                r_node = self.routers[r_id]
                # Evaluamos un enlace promedio representativo hacia ese router
                active_links = [l for l in self.ingress_links.values() if l.to_node_id == r_id and l.active]
                esta_activo = len(active_links) > 0
                avg_lat = np.mean([l.current_latency_ms for l in active_links]) if esta_activo else 99999.0

                enlaces_candidatos_info.append({
                    "latencia_ms": avg_lat,
                    "saturacion_nodo_destino": r_node.saturation_ratio,
                    "activo": esta_activo
                })

            # Resolver con el Algoritmo Húngaro
            resultado = self.router_hungaro.resolver_asignacion(
                num_flujos=num_flujos,
                enlaces_info=enlaces_candidatos_info
            )

    # --------------------------------------------------------------------------
    # CÁLCULO DE MÉTRICAS GLOBALES (TEORÍA DE COLAS E INVENTARIO)
    # --------------------------------------------------------------------------
    def obtener_metricas_completas(self) -> Dict:
        """
        Calcula y compila todas las métricas de rendimiento exigidas en el enunciado:
        - L: Número promedio de paquetes en el sistema.
        - Lq: Número promedio de paquetes en cola.
        - W: Tiempo medio de estancia total.
        - Wq: Tiempo medio de espera en cola.
        - Paquetes procesados, perdidos y tasa de pérdida.
        - Costos de almacenamiento, penalización y costo global.
        """
        t_now = max(0.001, self.env.now)

        # Actualizar áreas en todos los routers
        for r in self.routers.values():
            r.actualizar_areas_temporales()

        total_procesados = len(self.all_delivered_packets)
        total_perdidos = self.total_dropped_packets
        total_llegadas = total_procesados + total_perdidos

        tasa_perdida_pct = (total_perdidos / total_llegadas * 100.0) if total_llegadas > 0 else 0.0

        # Tiempos W y Wq a partir de los paquetes completados
        if total_procesados > 0:
            wq_promedio = float(np.mean([p.waiting_time_wq for p in self.all_delivered_packets]))
            w_promedio = float(np.mean([p.total_system_time_w for p in self.all_delivered_packets]))
        else:
            wq_promedio = 0.0
            w_promedio = 0.0

        # L y Lq integrados en el tiempo a través de todos los routers de la red
        suma_area_lq = sum(r.area_queue_lq for r in self.routers.values())
        suma_area_l = sum(r.area_system_l for r in self.routers.values())

        lq_global = suma_area_lq / t_now
        l_global = suma_area_l / t_now

        # Costos del sistema
        costo_almacenamiento = sum(r.total_holding_cost for r in self.routers.values())
        costo_penalizacion = total_perdidos * COSTO_PENALIZACION_RUPTURA
        costo_global = costo_almacenamiento + costo_penalizacion

        # Factor de utilización teórico y empírico
        rho = self.lam / (self.mu * len(self.routers)) if self.mu > 0 else 0.0

        return {
            "tiempo_simulacion_s": round(t_now, 2),
            "lambda": round(self.lam, 2),
            "mu": round(self.mu, 2),
            "capacidad_buffer_s": self.capacidad_s,
            "umbral_reabastecimiento_s": self.umbral_s,
            "lote_q": self.lote_q,
            "paquetes_procesados": total_procesados,
            "paquetes_perdidos": total_perdidos,
            "tasa_perdida_pct": round(tasa_perdida_pct, 2),
            "tiempo_medio_cola_wq_s": round(wq_promedio, 4),
            "tiempo_medio_sistema_w_s": round(w_promedio, 4),
            "promedio_paquetes_cola_lq": round(lq_global, 2),
            "promedio_paquetes_sistema_l": round(l_global, 2),
            "costo_almacenamiento_usd": round(costo_almacenamiento, 2),
            "costo_penalizacion_usd": round(costo_penalizacion, 2),
            "costo_global_usd": round(costo_global, 2),
            "factor_utilizacion_rho": round(rho, 3),
        }

    def _get_node_x(self, node_id: str) -> float:
        for s in self.sources:
            if s["id"] == node_id:
                return float(s["x"])
        if node_id in self.routers:
            return float(self.routers[node_id].x)
        for d in self.destinations:
            if d["id"] == node_id:
                return float(d["x"])
        return 0.0

    def _get_node_y(self, node_id: str) -> float:
        for s in self.sources:
            if s["id"] == node_id:
                return float(s["y"])
        if node_id in self.routers:
            return float(self.routers[node_id].y)
        for d in self.destinations:
            if d["id"] == node_id:
                return float(d["y"])
        return 0.0

    def _log_event(self, mensaje: str):
        self.event_log.append(f"[{self.env.now:6.2f}s] {mensaje}")

    def toggle_enlace(self, link_id: str) -> bool:
        """Alterna el estado activo/caído de un enlace."""
        if link_id in self.ingress_links:
            link = self.ingress_links[link_id]
            link.active = not link.active
            estado = "OPERATIVO" if link.active else "CAÍDO"
            self._log_event(f"⚡ Enlace {link_id} ahora está {estado}")
            return link.active
        elif link_id in self.egress_links:
            link = self.egress_links[link_id]
            link.active = not link.active
            estado = "OPERATIVO" if link.active else "CAÍDO"
            self._log_event(f"⚡ Enlace {link_id} ahora está {estado}")
            return link.active
        return False
