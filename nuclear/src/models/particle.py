"""Modelos de particulas: neutrones libres y efectos visuales de fision."""

import math
import random
from typing import Tuple
from src.constants import (
    NeutronEnergy,
    V_FAST,
    V_THERMAL,
)


class Neutron:
    """Representa un neutron libre dentro del nucleo del reactor."""

    def __init__(
        self,
        x: float,
        y: float,
        energy: NeutronEnergy = NeutronEnergy.FAST,
        angle_rad: float = None,
        generation: int = 0,
    ):
        self.x = float(x)
        self.y = float(y)
        self.energy = energy
        self.generation = generation
        self.age = 0.0
        self.alive = True

        if angle_rad is None:
            angle_rad = random.uniform(0, 2 * math.pi)
        self.angle = angle_rad

        speed = V_FAST if self.energy == NeutronEnergy.FAST else V_THERMAL
        self.vx = speed * math.cos(self.angle)
        self.vy = speed * math.sin(self.angle)

    def update(self, dt: float):
        """Actualiza la posicion segun la velocidad vectorial."""
        if not self.alive:
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt

    def moderate(self):
        """Modera el neutron convirtiendolo de rapido a termico (colision elastica)."""
        if self.energy == NeutronEnergy.FAST:
            self.energy = NeutronEnergy.THERMAL
            # Desviacion angular estocastica por dispersion elastica
            self.angle += random.uniform(-math.pi / 3, math.pi / 3)
            self.vx = V_THERMAL * math.cos(self.angle)
            self.vy = V_THERMAL * math.sin(self.angle)

    def bounce(self, normal_x: float, normal_y: float):
        """Rebota el neutron contra una superficie reflectora (ej. reflector perimetral)."""
        # Proyeccion sobre la normal: v' = v - 2(v . n) n
        dot = self.vx * normal_x + self.vy * normal_y
        self.vx -= 2 * dot * normal_x
        self.vy -= 2 * dot * normal_y
        self.angle = math.atan2(self.vy, self.vx)


class FissionBurst:
    """Efecto visual transitorio de una fision nuclear ocurrida en el nucleo."""

    def __init__(self, x: float, y: float, energy_mev: float = 200.0):
        self.x = float(x)
        self.y = float(y)
        self.energy_mev = energy_mev
        self.radius = 3.0
        self.max_radius = 28.0
        self.lifetime = 0.30  # segundos
        self.age = 0.0
        self.alive = True

    def update(self, dt: float):
        """Evoluciona la onda expansiva y extincion del destello."""
        self.age += dt
        if self.age >= self.lifetime:
            self.alive = False
        else:
            progress = self.age / self.lifetime
            self.radius = 3.0 + (self.max_radius - 3.0) * progress

    @property
    def alpha(self) -> int:
        """Transparencia decreciente (255 -> 0)."""
        if not self.alive:
            return 0
        remaining = 1.0 - (self.age / self.lifetime)
        return max(0, min(255, int(255 * remaining)))
