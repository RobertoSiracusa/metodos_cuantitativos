"""Modelos de elementos combustibles nucleares (U-235 y U-238)."""

import math
import random
from typing import List, Optional
from src.constants import PELLET_RADIUS, T_INLET_COOLANT


class FuelPellet:
    """Pastilla individual de combustible dentro de un ensamble."""

    def __init__(self, x: float, y: float, is_u235: bool, radius: float = PELLET_RADIUS):
        self.x = float(x)
        self.y = float(y)
        self.is_u235 = is_u235
        self.radius = float(radius)
        self.fissions_count = 0
        self.glow_intensity = 0.0

    def contains_point(self, px: float, py: float) -> bool:
        """Determina si un punto (ej. posicion de un neutron) impacta con la pastilla."""
        dx = px - self.x
        dy = py - self.y
        return (dx * dx + dy * dy) <= (self.radius * self.radius)

    def record_fission(self):
        """Registra una fision en esta pastilla y activa brillo termico."""
        self.fissions_count += 1
        self.glow_intensity = 1.0

    def cool_down(self, dt: float):
        """Disipa el resplandor visual con el paso del tiempo."""
        if self.glow_intensity > 0.0:
            self.glow_intensity = max(0.0, self.glow_intensity - dt * 2.5)


class FuelAssembly:
    """Ensamble o elemento combustible que agrupa pastillas de uranio."""

    def __init__(
        self,
        grid_row: int,
        grid_col: int,
        center_x: float,
        center_y: float,
        enrichment: float = 0.20,
    ):
        self.grid_row = grid_row
        self.grid_col = grid_col
        self.center_x = float(center_x)
        self.center_y = float(center_y)
        self.enrichment = float(enrichment)
        self.temperature = T_INLET_COOLANT
        self.total_fissions = 0

        # Crear micro-arreglo de 4 pastillas por ensamble
        self.pellets: List[FuelPellet] = []
        offset = PELLET_RADIUS * 0.75
        positions = [
            (self.center_x - offset, self.center_y - offset),
            (self.center_x + offset, self.center_y - offset),
            (self.center_x - offset, self.center_y + offset),
            (self.center_x + offset, self.center_y + offset),
        ]

        for px, py in positions:
            # Seleccionar U-235 segun la fraccion de enriquecimiento
            is_u235 = random.random() < self.enrichment
            self.pellets.append(FuelPellet(px, py, is_u235=is_u235, radius=PELLET_RADIUS * 0.7))

    def check_interaction(self, nx: float, ny: float) -> Optional[FuelPellet]:
        """Retorna la pastilla impactada si un neutron colisiona con el ensamble."""
        for pellet in self.pellets:
            if pellet.contains_point(nx, ny):
                return pellet
        return None

    def update(self, dt: float):
        """Actualiza el enfriamiento visual de las pastillas."""
        for pellet in self.pellets:
            pellet.cool_down(dt)
