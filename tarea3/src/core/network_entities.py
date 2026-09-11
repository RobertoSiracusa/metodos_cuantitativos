"""
Entidades de Red: Paquetes, Enlaces y Routers
Capa de Modelo Cuantitativo — Metodos Cuantitativos
"""

from collections import deque
from dataclasses import dataclass
from enum import Enum, auto
import random
from typing import Deque, List, Optional, Tuple
import simpy

from src.utils.config import (
    CAPACIDAD_BUFFER_S,
    UMBRAL_REABASTECER_S,
    LOTE_REABASTECER_Q,
    MU_DEFECTO,
    COSTO_HOLDING_POR_SEG,
)


class PacketState(Enum):
    """Estados en el ciclo de vida de un paquete de datos."""
    GENERATED = auto()          # Creado en fuente de origen
    TRAVELING_INGRESS = auto()  # En transito por enlace hacia router
    IN_BUFFER = auto()          # En cola de espera del buffer
    IN_SERVICE = auto()         # Siendo procesado por el servidor
    TRAVELING_EGRESS = auto()   # En transito hacia destino final
    DELIVERED = auto()          # Entregado exitosamente
    DROPPED = auto()            # Descartado por buffer overflow


@dataclass
class Packet:
    """Entidad de datos que transita por la red estocastica."""
    id: int
    source_id: str
    target_router_id: Optional[str] = None
    dest_id: Optional[str] = None
    size_bytes: int = 1500
    state: PacketState = PacketState.GENERATED

    # Tiempos de simulacion (segundos)
    t_created: float = 0.0
    t_buffer_entry: float = 0.0
    t_service_start: float = 0.0
    t_service_end: float = 0.0
    t_delivered: float = 0.0

    # Variables para sincronizacion y visualizacion
    x: float = 0.0
    y: float = 0.0
    start_pos: Tuple[float, float] = (0.0, 0.0)
    end_pos: Tuple[float, float] = (0.0, 0.0)
    progress: float = 0.0
    travel_time: float = 0.45
    t_link_start: float = 0.0

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
    """Enlace de comunicacion con retardo dinamico (latencia + jitter) y control de fallas."""

    def __init__(
        self,
        link_id: str,
        from_node_id: str,
        to_node_id: str,
        base_latency_ms: float = 12.0,
        jitter_ms: float = 3.0,
    ):
        self.link_id = link_id
        self.from_node_id = from_node_id
        self.to_node_id = to_node_id
        self.base_latency_ms = base_latency_ms
        self.jitter_ms = jitter_ms
        self.active = True
        self.packets_in_transit: List[Packet] = []
        self.total_transferred = 0

    @property
    def current_latency_ms(self) -> float:
        """Calcula la latencia actual considerando fluctuacion estocastica."""
        if not self.active:
            return 999999.0
        ruido = random.gauss(0, self.jitter_ms * 0.5)
        return max(1.0, self.base_latency_ms + ruido)


class RouterNode:
    """
    Nodo intermedio (Router/Switch) con buffer finito (S) y servidor exponencial (mu).
    Implementa la politica de inventario (s, Q) para control de flujo y prevencion de rotura.
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
        mu: float = MU_DEFECTO,
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

        # Servidor de atencion SimPy (canal de transmision unico M/M/1/K)
        self.server = simpy.Resource(env, capacity=1)
        self.buffer_queue: Deque[Packet] = deque()
        self.current_serving: Optional[Packet] = None

        # Contadores de eventos
        self.total_arrived = 0
        self.total_processed = 0
        self.total_dropped = 0
        self.flow_control_signals_sent = 0
        self.credito_flujo_disponible = lote_q

        # Integrales temporales para metricas de colas e inventario
        self.area_queue_lq = 0.0
        self.area_system_l = 0.0
        self.last_update_time = 0.0
        self.total_holding_cost = 0.0

    @property
    def queue_length(self) -> int:
        """Cantidad de paquetes actualmente en buffer de cola."""
        return len(self.buffer_queue)

    @property
    def system_packets(self) -> int:
        """Cantidad de paquetes en el nodo (en buffer + en servidor)."""
        return len(self.buffer_queue) + (1 if self.current_serving is not None else 0)

    @property
    def saturation_ratio(self) -> float:
        """Grado de saturacion del buffer (0.0 a 1.0)."""
        if self.capacidad_s <= 0:
            return 1.0
        return min(1.0, len(self.buffer_queue) / self.capacidad_s)

    @property
    def status_color_category(self) -> str:
        """
        Categoria segun la especificacion del enunciado:
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
        """Actualiza las integrales de paquetes en el tiempo para L, Lq y holding cost."""
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
        Evalua la admision de un paquete al buffer segun la capacidad S.
        Aplica control de inventario y detecta Buffer Overflow.
        Retorna True si fue admitido, False si fue descartado.
        """
        self.actualizar_areas_temporales()
        self.total_arrived += 1

        # Control de capacidad maxima S
        if len(self.buffer_queue) >= self.capacidad_s:
            packet.state = PacketState.DROPPED
            self.total_dropped += 1
            return False

        packet.state = PacketState.IN_BUFFER
        packet.t_buffer_entry = self.env.now
        self.buffer_queue.append(packet)

        # Politica de reabastecimiento (s, Q):
        # Cuando el buffer cae por debajo de 's', emite senal para liberar siguiente lote
        if len(self.buffer_queue) < self.umbral_s and self.credito_flujo_disponible <= 0:
            self.flow_control_signals_sent += 1
            self.credito_flujo_disponible = self.lote_q

        return True
