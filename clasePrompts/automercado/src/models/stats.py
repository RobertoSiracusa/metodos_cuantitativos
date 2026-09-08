"""Colector y agregador de metricas cuantitativas de la simulacion del automercado."""

from typing import List
from src.constants import AVG_ITEM_PRICE


class SimulationStats:
    """Acumula estadisticas empiricas para contrastar con los modelos analiticos."""

    def __init__(self):
        self.total_arrivals = 0
        self.total_served = 0
        self.total_balked = 0

        self.total_wait_time_s = 0.0
        self.total_service_time_s = 0.0
        self.total_system_time_s = 0.0
        self.total_items_sold = 0

        # Muestreo temporal periodico para medias ponderadas en el tiempo
        self.queue_samples: List[int] = []
        self.system_samples: List[int] = []
        self.busy_server_samples: List[float] = []

    def record_arrival(self):
        self.total_arrivals += 1

    def record_balk(self):
        self.total_balked += 1

    def record_completed(self, wait_s: float, service_s: float, total_s: float, items: int):
        self.total_served += 1
        self.total_wait_time_s += max(0.0, wait_s)
        self.total_service_time_s += max(0.0, service_s)
        self.total_system_time_s += max(0.0, total_s)
        self.total_items_sold += max(0, items)

    def sample_state(self, queue_len: int, system_len: int, busy_servers: int, active_servers: int):
        self.queue_samples.append(queue_len)
        self.system_samples.append(system_len)
        if active_servers > 0:
            self.busy_server_samples.append(busy_servers / active_servers)
        else:
            self.busy_server_samples.append(0.0)

    @property
    def avg_wait_time_min(self) -> float:
        """Tiempo promedio de espera en cola (Wq empirico en minutos)."""
        if self.total_served == 0:
            return 0.0
        return (self.total_wait_time_s / self.total_served) / 60.0

    @property
    def avg_service_time_min(self) -> float:
        """Tiempo promedio de atencion en caja (1/mu empirico en minutos)."""
        if self.total_served == 0:
            return 0.0
        return (self.total_service_time_s / self.total_served) / 60.0

    @property
    def avg_system_time_min(self) -> float:
        """Tiempo promedio de permanencia en el automercado (W empirico en minutos)."""
        if self.total_served == 0:
            return 0.0
        return (self.total_system_time_s / self.total_served) / 60.0

    @property
    def avg_queue_length(self) -> float:
        """Promedio temporal de clientes en cola (Lq empirico)."""
        if not self.queue_samples:
            return 0.0
        return sum(self.queue_samples) / len(self.queue_samples)

    @property
    def avg_system_length(self) -> float:
        """Promedio temporal de clientes en el sistema (L empirico)."""
        if not self.system_samples:
            return 0.0
        return sum(self.system_samples) / len(self.system_samples)

    @property
    def empirical_rho(self) -> float:
        """Factor de utilizacion promedio empirico de las cajas registradoras."""
        if not self.busy_server_samples:
            return 0.0
        return sum(self.busy_server_samples) / len(self.busy_server_samples)

    @property
    def balk_rate(self) -> float:
        """Porcentaje de clientes rechazados por colas saturadas."""
        if self.total_arrivals == 0:
            return 0.0
        return (self.total_balked / self.total_arrivals) * 100.0

    @property
    def total_revenue(self) -> float:
        """Ingresos brutos estimados por ventas."""
        return self.total_items_sold * AVG_ITEM_PRICE
