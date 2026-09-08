"""Modelo de inventario continuo para el tanque central de combustible."""

from src.constants import TANK_CAPACITY, TANK_INITIAL


class FuelTank:
    """Tanque subterraneo central de combustible de la estacion."""

    def __init__(self, capacity: float = TANK_CAPACITY, initial_level: float = TANK_INITIAL):
        self.capacity = float(capacity)
        self.level = float(min(initial_level, capacity))
        self.is_refilling = False

    @property
    def percent(self) -> float:
        """Porcentaje de combustible disponible en el tanque (0.0 a 100.0)."""
        if self.capacity <= 0:
            return 0.0
        return (self.level / self.capacity) * 100.0

    @property
    def is_low(self) -> bool:
        """Indica si el combustible cayo por debajo del 20% de reserva."""
        return self.percent < 20.0

    def withdraw(self, amount: float) -> float:
        """
        Extrae combustible del tanque.
        amount: Litros solicitados.
        Devuelve la cantidad real despachada.
        """
        actual = min(amount, self.level)
        self.level -= actual
        return actual

    def refill(self, amount: float) -> float:
        """
        Abastece el tanque central con combustible de camion cisterna.
        Devuelve la cantidad neta ingresada.
        """
        available_space = self.capacity - self.level
        added = min(amount, available_space)
        self.level += added
        return added
