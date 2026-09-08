"""Entidad Cliente y logica cinematica para navegacion top-down con carrito."""

import math
import random
from typing import Optional, List, Tuple
from src.constants import (
    CustomerState,
    CUSTOMER_SKIN_TONES,
    CUSTOMER_SHIRT_COLORS,
    ITEM_COLORS,
    MIN_ITEMS,
    MAX_ITEMS,
)


class Customer:
    """Representa a un cliente con carrito de compras en el automercado."""

    def __init__(
        self,
        customer_id: int,
        arrival_time: float,
        initial_pos: Tuple[float, float],
        num_items: Optional[int] = None,
    ):
        self.id = customer_id
        self.arrival_time = arrival_time
        self.state = CustomerState.ARRIVING

        # Cantidad y variedad cromatica de articulos en el carrito
        if num_items is not None:
            self.num_items = max(1, num_items)
        else:
            self.num_items = random.randint(MIN_ITEMS, MAX_ITEMS)

        self.items_scanned = 0
        self.item_colors = [random.choice(ITEM_COLORS) for _ in range(self.num_items)]

        # Timers operacionales para calculo de metricas cuantitativas (segundos simulados)
        self.queue_join_time: Optional[float] = None
        self.service_start_time: Optional[float] = None
        self.departure_time: Optional[float] = None
        self.assigned_checkout_id: Optional[int] = None

        # Posicion y orientacion cinematica (x, y, angulo en grados)
        self.x, self.y = float(initial_pos[0]), float(initial_pos[1])
        self.angle = 90.0  # 90 grados = hacia abajo (+y)
        self.waypoints: List[Tuple[float, float, float]] = []
        self.speed = 190.0  # Pixeles por segundo

        # Apariencia visual aleatoria pero determinista segun ID
        rng = random.Random(customer_id * 37)
        self.skin_color = rng.choice(CUSTOMER_SKIN_TONES)
        self.shirt_color = rng.choice(CUSTOMER_SHIRT_COLORS)
        self.hair_color = rng.choice([(40, 25, 20), (80, 50, 30), (190, 160, 100), (30, 30, 30)])

    @property
    def wait_time(self) -> float:
        """Tiempo de espera transcurrido en la cola antes de ser atendido."""
        if self.service_start_time is None or self.queue_join_time is None:
            return 0.0
        return max(0.0, self.service_start_time - self.queue_join_time)

    @property
    def service_duration(self) -> float:
        """Tiempo total de atencion en caja (escaneo y pago)."""
        if self.service_start_time is None or self.departure_time is None:
            return 0.0
        return max(0.0, self.departure_time - self.service_start_time)

    @property
    def total_system_time(self) -> float:
        """Tiempo total de permanencia en el sistema (arribo a salida)."""
        if self.departure_time is None:
            return 0.0
        return max(0.0, self.departure_time - self.arrival_time)

    @property
    def items_remaining(self) -> int:
        """Articulos pendientes por escanear."""
        return max(0, self.num_items - self.items_scanned)

    def set_target(self, x: float, y: float, angle: float = 90.0):
        """Asigna un destino directo a la trayectoria."""
        self.waypoints = [(float(x), float(y), float(angle))]

    def add_waypoint(self, x: float, y: float, angle: float = 90.0):
        """Agrega un punto de paso secuencial."""
        self.waypoints.append((float(x), float(y), float(angle)))

    def clear_waypoints(self):
        """Vacia los puntos de paso pendientes."""
        self.waypoints.clear()

    def update_motion(self, dt: float):
        """
        Actualiza suavemente la posicion y angulo hacia el proximo waypoint.
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
            self.x = target_x
            self.y = target_y
            self.angle = target_angle
            self.waypoints.pop(0)
        else:
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step

            move_angle = math.degrees(math.atan2(dy, dx))
            angle_diff = (move_angle - self.angle + 180) % 360 - 180
            self.angle += angle_diff * min(1.0, 10.0 * dt)
