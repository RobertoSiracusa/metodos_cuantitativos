"""Entidad de la serpiente en Programacion Orientada a Objetos."""

from collections import deque
from typing import Deque, List, Optional, Tuple
from ..constants import Direction
from .point import Point


class Snake:
    """Clase principal que encapsula la estructura y comportamiento de la serpiente."""

    def __init__(
        self,
        initial_head: Point = Point(12, 12),
        initial_length: int = 3,
        initial_direction: Direction = Direction.RIGHT,
    ):
        self.direction = initial_direction
        self.buffered_direction: Optional[Direction] = None
        self.is_alive = True
        self.death_reason: Optional[str] = None
        self.grow_pending = 0

        # Segmentos de la serpiente (head al frente en indice 0)
        self.body: Deque[Point] = deque()
        self._init_body(initial_head, initial_length, initial_direction)

    def _init_body(self, head: Point, length: int, direction: Direction) -> None:
        self.body.clear()
        self.body.append(head)
        # Construir cuerpo inicial en sentido contrario al movimiento
        opp_x = -direction.dx
        opp_y = -direction.dy
        for i in range(1, length):
            segment = Point(head.x + opp_x * i, head.y + opp_y * i)
            self.body.append(segment)

    @property
    def head(self) -> Point:
        """Retorna la coordenada de la cabeza."""
        return self.body[0]

    @property
    def length(self) -> int:
        """Longitud actual de la serpiente."""
        return len(self.body)

    @property
    def occupied_points(self) -> set[Point]:
        """Conjunto de puntos ocupados para busqueda rapida de colisiones."""
        return set(self.body)

    def set_direction(self, new_direction: Direction) -> bool:
        """
        Programa un cambio de direccion validando que no sea opuesta.
        Usa buffer para evitar colisiones por multiples pulsaciones rapidas.
        """
        if new_direction.is_opposite(self.direction):
            return False
        self.buffered_direction = new_direction
        return True

    def grow(self, amount: int = 1) -> None:
        """Incrementa el contador de crecimiento pendiente."""
        self.grow_pending += amount

    def step(self, grid_width: int, grid_height: int) -> Tuple[Point, bool]:
        """
        Ejecuta un paso discreto de movimiento.
        Retorna la nueva cabeza y si ocurrio una colision mortal.
        """
        if not self.is_alive:
            return self.head, False

        # Aplicar direccion en cola si existe
        if self.buffered_direction is not None:
            if not self.buffered_direction.is_opposite(self.direction):
                self.direction = self.buffered_direction
            self.buffered_direction = None

        new_head = Point(self.head.x + self.direction.dx, self.head.y + self.direction.dy)

        # 1. Chequeo de colision con limites de la pared
        if not new_head.is_inside_bounds(grid_width, grid_height):
            self.is_alive = False
            self.death_reason = f"Colision con pared en coordenada ({new_head.x}, {new_head.y})"
            return new_head, True

        # 2. Chequeo de colision con su propio cuerpo
        # Si la cola va a moverse en este turno (sin crecimiento pendiente), la cola no colisiona
        body_to_check = list(self.body)
        if self.grow_pending == 0 and len(body_to_check) > 0:
            body_to_check = body_to_check[:-1]

        if new_head in body_to_check:
            self.is_alive = False
            self.death_reason = f"Autocolision en segmento ({new_head.x}, {new_head.y})"
            return new_head, True

        # Avanzar: agregar nueva cabeza
        self.body.appendleft(new_head)

        # Manejar crecimiento o retiro de la cola
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

        return new_head, False

    def reset(
        self,
        initial_head: Point = Point(12, 12),
        initial_length: int = 3,
        initial_direction: Direction = Direction.RIGHT,
    ) -> None:
        """Reinicia la serpiente a su estado inicial."""
        self.direction = initial_direction
        self.buffered_direction = None
        self.is_alive = True
        self.death_reason = None
        self.grow_pending = 0
        self._init_body(initial_head, initial_length, initial_direction)
