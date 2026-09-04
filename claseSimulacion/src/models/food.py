"""Modelo de comida y elementos consumibles en la simulacion."""

from enum import Enum
from typing import Optional
from .point import Point


class FoodType(Enum):
    """Tipos de comida con diferentes valores y dinamicas de expiracion."""
    NORMAL = "NORMAL"
    BONUS = "BONUS"


class Food:
    """Representa una unidad de alimento en la cuadricula discreta."""

    def __init__(
        self,
        position: Point,
        food_type: FoodType = FoodType.NORMAL,
        spawn_time: float = 0.0,
        lifespan: Optional[float] = None,
    ):
        self.position = position
        self.food_type = food_type
        self.spawn_time = spawn_time
        self.lifespan = lifespan

        if food_type == FoodType.BONUS:
            self.points = 30
            self.growth_amount = 2
        else:
            self.points = 10
            self.growth_amount = 1

    def is_expired(self, current_sim_time: float) -> bool:
        """Determina si la comida ha caducado segun el reloj de simulacion."""
        if self.lifespan is None:
            return False
        return (current_sim_time - self.spawn_time) >= self.lifespan

    def time_remaining(self, current_sim_time: float) -> float:
        """Tiempo restante antes de expirar (en segundos simulados)."""
        if self.lifespan is None:
            return float("inf")
        return max(0.0, self.lifespan - (current_sim_time - self.spawn_time))
