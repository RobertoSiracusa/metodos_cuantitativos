"""Entidad de vehiculo y logica cinematica para visualizacion top-down."""

import math
from typing import Optional, List, Tuple
from src.constants import VehicleState, CAR_COLORS


class Vehicle:
    """Representa un automovil que ingresa, espera en cola y es surtido en la estacion."""

    def __init__(
        self,
        vehicle_id: int,
        arrival_time: float,
        fuel_requested: float,
        initial_pos: Tuple[float, float],
        color: Optional[Tuple[int, int, int]] = None,
    ):
        self.id = vehicle_id
        self.arrival_time = arrival_time
        self.fuel_requested = fuel_requested
        self.fuel_dispensed = 0.0
        self.state = VehicleState.ARRIVING

        # Timers para calculo de metricas cuantitativas (segundos simulados)
        self.service_start_time: Optional[float] = None
        self.departure_time: Optional[float] = None
        self.assigned_pump_id: Optional[int] = None

        # Posicion y orientacion cinematica (x, y, angulo en grados)
        self.x, self.y = float(initial_pos[0]), float(initial_pos[1])
        self.angle = 0.0  # 0 grados = hacia la derecha (+x)

        # Cola de navegacion por waypoints: [(x, y, angulo_deseado), ...]
        self.waypoints: List[Tuple[float, float, float]] = []
        self.speed = 220.0  # Pixeles por segundo

        # Color aleatorio o predefinido
        if color:
            self.color = color
        else:
            self.color = CAR_COLORS[vehicle_id % len(CAR_COLORS)]

    @property
    def wait_time(self) -> float:
        """Tiempo que paso esperando en cola antes de acceder a la bomba."""
        if self.service_start_time is None:
            return 0.0
        return max(0.0, self.service_start_time - self.arrival_time)

    @property
    def service_duration(self) -> float:
        """Tiempo de servicio (recarga de combustible + transaccion)."""
        if self.service_start_time is None or self.departure_time is None:
            return 0.0
        return max(0.0, self.departure_time - self.service_start_time)

    @property
    def total_system_time(self) -> float:
        """Tiempo total de permanencia en la estacion (W)."""
        if self.departure_time is None:
            return 0.0
        return max(0.0, self.departure_time - self.arrival_time)

    def set_target(self, x: float, y: float, angle: float = 0.0):
        """Asigna un objetivo directo de desplazamiento."""
        self.waypoints = [(float(x), float(y), float(angle))]

    def add_waypoint(self, x: float, y: float, angle: float = 0.0):
        """Agrega un punto de paso a la trayectoria."""
        self.waypoints.append((float(x), float(y), float(angle)))

    def clear_waypoints(self):
        """Limpia los puntos de paso pendientes."""
        self.waypoints.clear()

    def update_motion(self, dt: float):
        """
        Actualiza suavemente la posicion y angulo del vehiculo en el lienzo hacia el proximo waypoint.
        dt: Delta de tiempo real en segundos.
        """
        if not self.waypoints:
            return

        target_x, target_y, target_angle = self.waypoints[0]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        step = self.speed * dt

        if dist <= step or dist < 2.0:
            # Llegada al waypoint actual
            self.x = target_x
            self.y = target_y
            self.angle = target_angle
            self.waypoints.pop(0)
        else:
            # Desplazamiento lineal
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step

            # Suavizado de giro angular
            move_angle = math.degrees(math.atan2(dy, dx))
            angle_diff = (move_angle - self.angle + 180) % 360 - 180
            self.angle += angle_diff * min(1.0, 10.0 * dt)
