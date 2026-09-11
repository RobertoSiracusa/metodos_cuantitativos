"""
Servicio de Simulacion Estocastica de Redes con SimPy
Capa de Servicios — Metodos Cuantitativos
Universidad Jose Antonio Paez
"""

from collections import deque
from pathlib import Path
import random
from typing import Deque, Dict, List, Optional, Tuple, Union
import numpy as np
import simpy

from src.core.network_entities import Packet, PacketState, NetworkLink, RouterNode
from src.core.hungarian_model import ModeloAsignacionHungaro, AsignacionResultado
from src.utils.config import (
    LAMBDA_DEFECTO,
    MU_DEFECTO,
    CAPACIDAD_BUFFER_S,
    UMBRAL_REABASTECER_S,
    LOTE_REABASTECER_Q,
    ALPHA_DEFECTO,
    INTERVALO_HUNGARO_DT,
    COSTO_HOLDING_POR_SEG,
    COSTO_PENALIZACION_RUPTURA,
    OUTPUTS_DIR,
)


class NetworkSimulation:
    """
    Orquestador de simulacion estocastica de eventos discretos.
    Integra:
    - Teoria de Colas: llegadas Poisson (lambda) y atencion exponencial (mu).
    - Modelos de Inventario: buffers con capacidad finita S y control de flujo (s, Q).
    - Asignacion Optima: Algoritmo Hungaro para enrutamiento dinamico.
    """

    def __init__(
        self,
        lam: float = LAMBDA_DEFECTO,
        mu: float = MU_DEFECTO,
        capacidad_s: int = CAPACIDAD_BUFFER_S,
        umbral_s: int = UMBRAL_REABASTECER_S,
        lote_q: int = LOTE_REABASTECER_Q,
        alpha: float = ALPHA_DEFECTO,
    ):
        self.env = simpy.Environment()
        self.lam = max(0.1, float(lam))
        self.mu = max(0.1, float(mu))
        self.capacidad_s = int(capacidad_s)
        self.umbral_s = int(umbral_s)
        self.lote_q = int(lote_q)

        self.router_hungaro = ModeloAsignacionHungaro(alpha=alpha)
        self.packet_seq_id = 1

        # Fuentes de trafico N (servidores de aplicacion)
        self.sources = [
            {"id": "S1", "name": "Servidor Web (S1)", "x": 120.0, "y": 160.0},
            {"id": "S2", "name": "Base de Datos (S2)", "x": 120.0, "y": 320.0},
            {"id": "S3", "name": "Streaming CDN (S3)", "x": 120.0, "y": 480.0},
        ]

        # Routers intermedios M con buffers finitos
        self.routers: Dict[str, RouterNode] = {
            "R1": RouterNode("R1", "Router Core 1", 420.0, 120.0, self.env, self.capacidad_s, self.umbral_s, self.lote_q, self.mu),
            "R2": RouterNode("R2", "Router Core 2", 420.0, 250.0, self.env, self.capacidad_s, self.umbral_s, self.lote_q, self.mu),
            "R3": RouterNode("R3", "Router Core 3", 420.0, 390.0, self.env, self.capacidad_s, self.umbral_s, self.lote_q, self.mu),
            "R4": RouterNode("R4", "Router Core 4", 420.0, 520.0, self.env, self.capacidad_s, self.umbral_s, self.lote_q, self.mu),
        }

        # Destinos finales de salida
        self.destinations = [
            {"id": "D1", "name": "Gateway WAN A (D1)", "x": 720.0, "y": 220.0},
            {"id": "D2", "name": "Gateway WAN B (D2)", "x": 720.0, "y": 420.0},
        ]

        # Enlaces Ingress (Fuentes -> Routers)
        self.ingress_links: Dict[str, NetworkLink] = {}
        for s in self.sources:
            for r_id in self.routers.keys():
                lid = f"{s['id']}-{r_id}"
                base_lat = 8.0 + (int(s['id'][-1]) * 2.0) + (int(r_id[-1]) * 1.5)
                self.ingress_links[lid] = NetworkLink(lid, s['id'], r_id, base_lat, jitter_ms=2.5)

        # Enlaces Egress (Routers -> Destinos)
        self.egress_links: Dict[str, NetworkLink] = {}
        for r_id in self.routers.keys():
            for d in self.destinations:
                lid = f"{r_id}-{d['id']}"
                base_lat = 10.0 + (int(r_id[-1]) * 1.0)
                self.egress_links[lid] = NetworkLink(lid, r_id, d['id'], base_lat, jitter_ms=2.0)

        # Contabilidad y registro de paquetes
        self.all_delivered_packets: List[Packet] = []
        self.total_generated_packets = 0
        self.total_dropped_packets = 0
        self.event_log: Deque[str] = deque(maxlen=25)
        self.historial_completo_eventos: List[str] = []

        # Iniciar procesos concurrentes en SimPy
        self.env.process(self._traffic_generator_process())
        for r_node in self.routers.values():
            self.env.process(self._router_service_process(r_node))
        self.env.process(self._hungarian_periodic_optimizer())

    def actualizar_dimensiones_pantalla(self, ancho_red: float, alto_pantalla: float) -> None:
        """Adapta las coordenadas de nodos segun la resolucion grafica de pantalla."""
        ancho_red = max(500.0, float(ancho_red))
        alto_pantalla = max(450.0, float(alto_pantalla))

        # Posicionamiento de fuentes (izquierda)
        sx = max(80.0, ancho_red * 0.13)
        sy_base = alto_pantalla * 0.20
        sy_step = (alto_pantalla * 0.60) / max(1, len(self.sources) - 1)
        for i, s in enumerate(self.sources):
            s["x"] = sx
            s["y"] = sy_base + (i * sy_step)

        # Posicionamiento de routers core (centro)
        rx = ancho_red * 0.50
        ry_base = alto_pantalla * 0.15
        ry_step = (alto_pantalla * 0.70) / max(1, len(self.routers) - 1)
        for i, (r_id, r_node) in enumerate(self.routers.items()):
            r_node.x = rx
            r_node.y = ry_base + (i * ry_step)

        # Posicionamiento de gateways WAN (derecha)
        dx = min(ancho_red - 80.0, ancho_red * 0.87)
        dy_base = alto_pantalla * 0.30
        dy_step = (alto_pantalla * 0.40) / max(1, len(self.destinations) - 1)
        for i, d in enumerate(self.destinations):
            d["x"] = dx
            d["y"] = dy_base + (i * dy_step)

        # Actualizar posiciones cinemáticas de paquetes en transito
        todos_enlaces = list(self.ingress_links.values()) + list(self.egress_links.values())
        for link in todos_enlaces:
            for pkt in link.packets_in_transit:
                pkt.start_pos = (self._get_node_x(link.from_node_id), self._get_node_y(link.from_node_id))
                pkt.end_pos = (self._get_node_x(link.to_node_id), self._get_node_y(link.to_node_id))

    def _traffic_generator_process(self):
        """Genera trafico de paquetes siguiendo un Proceso de Poisson (Exp(lambda))."""
        while True:
            intervalo = random.expovariate(self.lam)
            yield self.env.timeout(intervalo)

            source = random.choice(self.sources)
            s_id = source["id"]

            packet = Packet(
                id=self.packet_seq_id,
                source_id=s_id,
                t_created=self.env.now,
                x=float(source["x"]),
                y=float(source["y"]),
            )
            self.packet_seq_id += 1
            self.total_generated_packets += 1

            self._route_ingress_packet(packet)

    def _route_ingress_packet(self, packet: Packet):
        """Despacha el paquete entrante por el enlace asignado u optimo."""
        s_id = packet.source_id
        candidatos = [
            (lid, link) for lid, link in self.ingress_links.items()
            if link.from_node_id == s_id and link.active
        ]

        if not candidatos:
            packet.state = PacketState.DROPPED
            self.total_dropped_packets += 1
            self._log_event(f"Paquete #{packet.id} descartado: sin enlaces operativos desde {s_id}")
            return

        best_link = None
        min_cost = float("inf")

        for lid, link in candidatos:
            r_node = self.routers[link.to_node_id]
            cost = link.current_latency_ms + (self.router_hungaro.alpha * r_node.saturation_ratio)
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
            packet.travel_time = max(0.40, best_link.current_latency_ms / 30.0)
            packet.t_link_start = self.env.now

            self.env.process(self._transit_link_process(packet, best_link, target_r))

    def _transit_link_process(self, packet: Packet, link: NetworkLink, target_node: RouterNode):
        """Modela la propagacion del paquete por el medio fisico."""
        link.packets_in_transit.append(packet)
        transit_delay = packet.travel_time
        yield self.env.timeout(transit_delay)

        if packet in link.packets_in_transit:
            link.packets_in_transit.remove(packet)
        link.total_transferred += 1

        admitido = target_node.recibir_paquete(packet)
        if not admitido:
            self.total_dropped_packets += 1
            self._log_event(f"OVERFLOW en {target_node.name}: Paquete #{packet.id} descartado.")
        else:
            self._log_event(f"Paquete #{packet.id} encolado en {target_node.name} (Cola: {target_node.queue_length}/{target_node.capacidad_s})")

    def _router_service_process(self, r_node: RouterNode):
        """Servidor de modulacion y conmutacion con tasa exponencial mu."""
        while True:
            if not r_node.buffer_queue:
                yield self.env.timeout(0.02)
                continue

            with r_node.server.request() as req:
                yield req

                r_node.actualizar_areas_temporales()
                if not r_node.buffer_queue:
                    continue

                packet = r_node.buffer_queue.popleft()
                r_node.current_serving = packet
                packet.state = PacketState.IN_SERVICE
                packet.t_service_start = self.env.now

                service_duration = random.expovariate(self.mu)
                yield self.env.timeout(service_duration)

                packet.t_service_end = self.env.now
                r_node.total_processed += 1
                r_node.current_serving = None
                r_node.actualizar_areas_temporales()

                self._route_egress_packet(packet, r_node)

    def _route_egress_packet(self, packet: Packet, from_node: RouterNode):
        """Encamina el paquete atendido hacia el destino final WAN."""
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
            packet.state = PacketState.DROPPED
            self.total_dropped_packets += 1
            self._log_event(f"Paquete #{packet.id} perdido: enlace de salida {lid} inactivo.")

    def _transit_egress_process(self, packet: Packet, link: NetworkLink, dest: Dict):
        """Tránsito hacia el nodo final."""
        link.packets_in_transit.append(packet)
        yield self.env.timeout(packet.travel_time)

        if packet in link.packets_in_transit:
            link.packets_in_transit.remove(packet)
        link.total_transferred += 1

        packet.state = PacketState.DELIVERED
        packet.t_delivered = self.env.now
        self.all_delivered_packets.append(packet)
        self._log_event(f"Paquete #{packet.id} entregado en {dest['name']} (W={packet.total_system_time_w:.3f}s)")

    def _hungarian_periodic_optimizer(self):
        """Ejecuta periodicamente la optimizacion de enrutamiento con el Algoritmo Hungaro."""
        while True:
            yield self.env.timeout(INTERVALO_HUNGARO_DT)

            num_flujos = len(self.sources)
            enlaces_candidatos_info = []

            for r_id in self.routers.keys():
                r_node = self.routers[r_id]
                active_links = [l for l in self.ingress_links.values() if l.to_node_id == r_id and l.active]
                esta_activo = len(active_links) > 0
                avg_lat = float(np.mean([l.current_latency_ms for l in active_links])) if esta_activo else 99999.0

                enlaces_candidatos_info.append({
                    "latencia_ms": avg_lat,
                    "saturacion_nodo_destino": r_node.saturation_ratio,
                    "activo": esta_activo,
                })

            self.router_hungaro.resolver_asignacion(
                num_flujos=num_flujos,
                enlaces_info=enlaces_candidatos_info,
            )

    def obtener_metricas_completas(self) -> Dict:
        """Calcula y compila todas las metricas de rendimiento exigidas por el enunciado."""
        t_now = max(0.001, self.env.now)

        for r in self.routers.values():
            r.actualizar_areas_temporales()

        total_procesados = len(self.all_delivered_packets)
        total_perdidos = self.total_dropped_packets
        total_llegadas = total_procesados + total_perdidos

        tasa_perdida_pct = (total_perdidos / total_llegadas * 100.0) if total_llegadas > 0 else 0.0

        if total_procesados > 0:
            wq_promedio = float(np.mean([p.waiting_time_wq for p in self.all_delivered_packets]))
            w_promedio = float(np.mean([p.total_system_time_w for p in self.all_delivered_packets]))
        else:
            wq_promedio = 0.0
            w_promedio = 0.0

        suma_area_lq = sum(r.area_queue_lq for r in self.routers.values())
        suma_area_l = sum(r.area_system_l for r in self.routers.values())

        lq_global = suma_area_lq / t_now
        l_global = suma_area_l / t_now

        costo_almacenamiento = sum(r.total_holding_cost for r in self.routers.values())
        costo_penalizacion = total_perdidos * COSTO_PENALIZACION_RUPTURA
        costo_global = costo_almacenamiento + costo_penalizacion

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

    def _log_event(self, mensaje: str, categoria: str = "EVENTO") -> None:
        stamp = f"[{self.env.now:6.2f}s]"
        self.event_log.append(f"{stamp} {mensaje}")
        self.historial_completo_eventos.append(f"{stamp} [{categoria:16s}] {mensaje}")

    def exportar_eventos_log(self, destino: Union[str, Path] = "eventos_desempeno.log") -> Path:
        """Exporta el registro cronologico completo de eventos de desempeno de la red."""
        ruta_p = Path(destino)
        if not ruta_p.is_absolute() and len(ruta_p.parts) == 1:
            ruta_p = OUTPUTS_DIR / ruta_p.name
        ruta_p.parent.mkdir(parents=True, exist_ok=True)

        lineas = [
            "=" * 75,
            "REGISTRO CRONOLOGICO DE EVENTOS DE DESEMPENO — SIMULADOR DE RED",
            "=" * 75,
            f"Tiempo de Simulacion: {self.env.now:.2f} s",
            f"Parametros: lambda={self.lam} paq/s, mu={self.mu} paq/s, S={self.capacidad_s}, s={self.umbral_s}, Q={self.lote_q}",
            f"Total Eventos Registrados: {len(self.historial_completo_eventos)}",
            "-" * 75,
        ]
        with open(ruta_p, "w", encoding="utf-8") as f:
            f.write("\n".join(lineas) + "\n")
            for ev in self.historial_completo_eventos:
                f.write(ev + "\n")
            f.write("=" * 75 + "\n")
        return ruta_p

    def toggle_enlace(self, link_id: str) -> bool:
        """Alterna el estado operativo/caido de un enlace."""
        if link_id in self.ingress_links:
            link = self.ingress_links[link_id]
            link.active = not link.active
            estado = "OPERATIVO" if link.active else "CAIDO"
            self._log_event(f"Enlace {link_id} ahora esta {estado}", categoria="ENLACE_ESTADO")
            return link.active
        elif link_id in self.egress_links:
            link = self.egress_links[link_id]
            link.active = not link.active
            estado = "OPERATIVO" if link.active else "CAIDO"
            self._log_event(f"Enlace {link_id} ahora esta {estado}", categoria="ENLACE_ESTADO")
            return link.active
        return False
