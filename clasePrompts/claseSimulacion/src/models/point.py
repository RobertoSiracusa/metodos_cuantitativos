"""Punto discreto en la cuadricula bidimensional."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Point:
    """Representa una coordenada entera (x, y) en la cuadricula discreta."""
    x: int
    y: int

    def __add__(self, other: object) -> "Point":
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        if isinstance(other, tuple) and len(other) == 2:
            return Point(self.x + other[0], self.y + other[1])
        return NotImplemented

    def __sub__(self, other: object) -> "Point":
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        if isinstance(other, tuple) and len(other) == 2:
            return Point(self.x - other[0], self.y - other[1])
        return NotImplemented

    def manhattan_distance(self, other: "Point") -> int:
        """Calcula la distancia Manhattan entre dos puntos."""
        return abs(self.x - other.x) + abs(self.y - other.y)

    def is_inside_bounds(self, width: int, height: int) -> bool:
        """Verifica si el punto se encuentra dentro de los limites de la cuadricula."""
        return 0 <= self.x < width and 0 <= self.y < height

    def to_pixels(self, cell_size: int) -> Tuple[int, int]:
        """Convierte la coordenada discreta a coordenadas de pixeles."""
        return (self.x * cell_size, self.y * cell_size)
