"""Modelo de barra de control de absorcion neutronica (Boro / Cadmio)."""

import math
from src.constants import (
    DEFAULT_ROD_INSERTION,
    ROD_SPEED_PER_SEC,
    P_ABSORB_ROD,
)


class ControlRod:
    """Barra de control que regula o extingue la reaccion en cadena."""

    def __init__(
        self,
        rod_id: int,
        center_x: float,
        center_y: float,
        radius: float = 14.0,
        initial_insertion: float = DEFAULT_ROD_INSERTION,
    ):
        self.rod_id = rod_id
        self.center_x = float(center_x)
        self.center_y = float(center_y)
        self.radius = float(radius)
        self.insertion = float(initial_insertion)  # 0.0 (fuera) a 1.0 (totalmente insertada)
        self.target_insertion = float(initial_insertion)
        self.is_scrammed = False
        self.absorbed_neutrons = 0

    def adjust_insertion(self, delta: float):
        """Ajusta el objetivo de insercion de la barra."""
        if self.is_scrammed:
            return
        self.target_insertion = max(0.0, min(1.0, self.target_insertion + delta))

    def trigger_scram(self):
        """Dispara el SCRAM de emergencia (caida inmediata por gravedad al 100%)."""
        self.is_scrammed = True
        self.target_insertion = 1.0
        self.insertion = 1.0

    def reset_scram(self, reset_level: float = DEFAULT_ROD_INSERTION):
        """Restaura el control manual tras un SCRAM."""
        self.is_scrammed = False
        self.target_insertion = float(reset_level)

    def update(self, dt: float):
        """Desplaza suavemente la barra hacia su posicion objetivo."""
        if self.insertion < self.target_insertion:
            speed = 1.8 if self.is_scrammed else ROD_SPEED_PER_SEC
            self.insertion = min(self.target_insertion, self.insertion + speed * dt)
        elif self.insertion > self.target_insertion:
            self.insertion = max(self.target_insertion, self.insertion - ROD_SPEED_PER_SEC * dt)

    def can_absorb_at(self, px: float, py: float) -> bool:
        """
        Determina si un neutron cae dentro de la seccion eficaz de absorcion de la barra.
        La probabilidad efectiva de captura es proporcional al nivel de insercion.
        """
        if self.insertion <= 0.01:
            return False

        dx = px - self.center_x
        dy = py - self.center_y
        dist_sq = dx * dx + dy * dy
        effective_radius = self.radius * (0.3 + 0.7 * self.insertion)

        return dist_sq <= (effective_radius * effective_radius)

    def record_absorption(self):
        """Contabiliza un neutron capturado."""
        self.absorbed_neutrons += 1
