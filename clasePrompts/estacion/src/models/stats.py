"""Recoleccion y agregacion cuantitativa de metricas de la simulacion."""

from typing import List, Dict, Any


class SimulationStats:
    """Registrador en tiempo real de tiempos de espera, servicio y tamanos de cola."""

    def __init__(self):
        self.total_arrivals = 0
        self.total_served = 0
        self.total_balked = 0   # Rechazados por cola llena

        # Listas de tiempos en segundos simulados
        self.wait_times: List[float] = []       # Wq
        self.service_times: List[float] = []    # S
        self.system_times: List[float] = []     # W

        # Muestreo continuo de la longitud de cola Lq y sistema L
        self.queue_samples: List[int] = []
        self.system_samples: List[int] = []

    def record_arrival(self):
        self.total_arrivals += 1

    def record_balk(self):
        self.total_balked += 1

    def record_completed(self, wait_s: float, service_s: float, total_s: float):
        """Registra la culminacion exitosa de un vehiculo."""
        self.total_served += 1
        self.wait_times.append(wait_s)
        self.service_times.append(service_s)
        self.system_times.append(total_s)

    def sample_state(self, current_queue_len: int, current_system_len: int):
        """Toma una muestra del estado instantaneo para calcular promedios temporales."""
        self.queue_samples.append(current_queue_len)
        self.system_samples.append(current_system_len)

    @property
    def avg_wait_time_min(self) -> float:
        """Tiempo promedio de espera en cola (Wq) en minutos."""
        if not self.wait_times:
            return 0.0
        return (sum(self.wait_times) / len(self.wait_times)) / 60.0

    @property
    def avg_service_time_min(self) -> float:
        """Tiempo promedio de servicio (1/mu) en minutos."""
        if not self.service_times:
            return 0.0
        return (sum(self.service_times) / len(self.service_times)) / 60.0

    @property
    def avg_system_time_min(self) -> float:
        """Tiempo promedio total en el sistema (W) en minutos."""
        if not self.system_times:
            return 0.0
        return (sum(self.system_times) / len(self.system_times)) / 60.0

    @property
    def avg_queue_length(self) -> float:
        """Longitud promedio observada de la cola (Lq)."""
        if not self.queue_samples:
            return 0.0
        return sum(self.queue_samples) / len(self.queue_samples)

    @property
    def avg_system_length(self) -> float:
        """Numero promedio observado de clientes en el sistema (L)."""
        if not self.system_samples:
            return 0.0
        return sum(self.system_samples) / len(self.system_samples)

    def get_summary(self) -> Dict[str, Any]:
        """Resumen de metricas empíricas de la simulacion."""
        return {
            "arribos_totales": self.total_arrivals,
            "vehiculos_atendidos": self.total_served,
            "vehiculos_rechazados": self.total_balked,
            "Wq_sim_min": round(self.avg_wait_time_min, 3),
            "W_sim_min": round(self.avg_system_time_min, 3),
            "1_sobre_mu_sim_min": round(self.avg_service_time_min, 3),
            "Lq_sim": round(self.avg_queue_length, 2),
            "L_sim": round(self.avg_system_length, 2),
        }
