"""Renderizado del nucleo del reactor, vasija, barras y fenomenos cuanticos."""

import math
import pygame
from typing import Dict
from src.constants import (
    CORE_CENTER_X,
    CORE_CENTER_Y,
    VESSEL_RADIUS,
    CORE_ACTIVE_RADIUS,
    REFLECTOR_THICKNESS,
    COLOR_VESSEL_OUTER,
    COLOR_VESSEL_INNER,
    COLOR_REFLECTOR,
    COLOR_WATER_BASE,
    COLOR_CHERENKOV_MAX,
    COLOR_U235,
    COLOR_U238,
    COLOR_CONTROL_ROD,
    COLOR_ROD_GUIDE,
    COLOR_NEUTRON_FAST,
    COLOR_NEUTRON_THERMAL,
    COLOR_FISSION_FLASH,
    NeutronEnergy,
)
from src.simulation.reactor_sim import ReactorSimulation


class CoreView:
    """Renderiza la camara del reactor y la cinematica de particulas."""

    def __init__(self, fonts: Dict[str, pygame.font.Font]):
        self.fonts = fonts
        # Superficie translucida reutilizable para el resplandor Cherenkov
        self.cherenkov_surf = pygame.Surface((VESSEL_RADIUS * 2, VESSEL_RADIUS * 2), pygame.SRCALPHA)

    def render(self, surface: pygame.Surface, sim: ReactorSimulation, dt: float):
        """Dibuja el estado visual completo de la camara del reactor."""
        cx, cy = CORE_CENTER_X, CORE_CENTER_Y
        core = sim.core

        # 1. Blindaje biologico de hormigon (anillo exterior)
        pygame.draw.circle(surface, COLOR_VESSEL_OUTER, (cx, cy), VESSEL_RADIUS + 24)
        pygame.draw.circle(surface, (30, 35, 45), (cx, cy), VESSEL_RADIUS + 24, width=3)

        # 2. Vasija de presion de acero inoxidable
        pygame.draw.circle(surface, COLOR_VESSEL_INNER, (cx, cy), VESSEL_RADIUS)
        pygame.draw.circle(surface, (120, 135, 155), (cx, cy), VESSEL_RADIUS, width=4)

        # 3. Reflector perimetral de neutrones (berilio / agua pesada)
        pygame.draw.circle(surface, COLOR_REFLECTOR, (cx, cy), CORE_ACTIVE_RADIUS + REFLECTOR_THICKNESS)

        # 4. Piscina de agua / moderador base
        pygame.draw.circle(surface, COLOR_WATER_BASE, (cx, cy), CORE_ACTIVE_RADIUS)

        # 5. Efecto de Radiacion Cherenkov (brillo azul proporcional a potencia)
        power_ratio = min(1.0, core.thermal_power_mw / 120.0)
        if power_ratio > 0.02:
            self.cherenkov_surf.fill((0, 0, 0, 0))
            alpha_glow = int(140 * power_ratio)
            color_with_alpha = (*COLOR_CHERENKOV_MAX, alpha_glow)
            pygame.draw.circle(
                self.cherenkov_surf,
                color_with_alpha,
                (VESSEL_RADIUS, VESSEL_RADIUS),
                CORE_ACTIVE_RADIUS - 10,
            )
            surface.blit(
                self.cherenkov_surf,
                (cx - VESSEL_RADIUS, cy - VESSEL_RADIUS),
                special_flags=pygame.BLEND_RGBA_ADD,
            )

        # 6. Ensambles de combustible
        for assembly in core.fuel_assemblies:
            # Marco del ensamble
            box_rect = pygame.Rect(
                assembly.center_x - 22,
                assembly.center_y - 22,
                44,
                44,
            )
            pygame.draw.rect(surface, (25, 32, 44), box_rect, border_radius=4)
            pygame.draw.rect(surface, (45, 58, 78), box_rect, width=1, border_radius=4)

            # Pastillas individuales dentro del ensamble
            for pellet in assembly.pellets:
                base_color = COLOR_U235 if pellet.is_u235 else COLOR_U238
                # Si hubo fision reciente, sobreiluminar con naranja
                if pellet.glow_intensity > 0.05:
                    r = int(base_color[0] + (255 - base_color[0]) * pellet.glow_intensity)
                    g = int(base_color[1] * (1.0 - 0.5 * pellet.glow_intensity))
                    b = int(base_color[2] * (1.0 - 0.5 * pellet.glow_intensity))
                    draw_color = (min(255, r), min(255, g), min(255, b))
                else:
                    draw_color = base_color

                pygame.draw.circle(
                    surface,
                    draw_color,
                    (int(pellet.x), int(pellet.y)),
                    int(pellet.radius),
                )
                pygame.draw.circle(
                    surface,
                    (20, 25, 35),
                    (int(pellet.x), int(pellet.y)),
                    int(pellet.radius),
                    width=1,
                )

        # 7. Canales y barras de control
        for rod in core.control_rods:
            rx, ry = int(rod.center_x), int(rod.center_y)
            # Tubo guia exterior
            pygame.draw.circle(surface, COLOR_ROD_GUIDE, (rx, ry), int(rod.radius + 3))
            pygame.draw.circle(surface, (70, 80, 98), (rx, ry), int(rod.radius + 3), width=2)

            # Barra de boro/cadmio (el radio visual y opacidad dependen de insercion)
            fill_r = max(3, int(rod.radius * (0.3 + 0.7 * rod.insertion)))
            rod_color = COLOR_CONTROL_ROD if not rod.is_scrammed else (255, 30, 30)
            pygame.draw.circle(surface, rod_color, (rx, ry), fill_r)

            # Detalle mecanico central
            pygame.draw.line(surface, (255, 200, 200), (rx - 4, ry), (rx + 4, ry), 2)
            pygame.draw.line(surface, (255, 200, 200), (rx, ry - 4), (rx, ry + 4), 2)

        # 8. Destellos de fision nuclear transitorios
        for burst in core.fission_bursts:
            if burst.alive:
                alpha = burst.alpha
                burst_color = (*COLOR_FISSION_FLASH, min(220, alpha))
                # Circulo expansivo
                flash_surf = pygame.Surface((int(burst.radius * 2 + 4), int(burst.radius * 2 + 4)), pygame.SRCALPHA)
                pygame.draw.circle(
                    flash_surf,
                    burst_color,
                    (int(burst.radius + 2), int(burst.radius + 2)),
                    int(burst.radius),
                    width=max(1, int(3 * (1.0 - burst.age / burst.lifetime))),
                )
                surface.blit(
                    flash_surf,
                    (int(burst.x - burst.radius - 2), int(burst.y - burst.radius - 2)),
                    special_flags=pygame.BLEND_RGBA_ADD,
                )

        # 9. Neutrones libres activos en el espacio del nucleo
        for n in core.neutrons:
            color = COLOR_NEUTRON_FAST if n.energy == NeutronEnergy.FAST else COLOR_NEUTRON_THERMAL
            nx, ny = int(n.x), int(n.y)

            # Estela / vector de velocidad
            trail_len = 8 if n.energy == NeutronEnergy.FAST else 4
            trail_x = int(n.x - (n.vx / (math.hypot(n.vx, n.vy) + 1e-5)) * trail_len)
            trail_y = int(n.y - (n.vy / (math.hypot(n.vx, n.vy) + 1e-5)) * trail_len)
            pygame.draw.line(surface, (*color, 120), (trail_x, trail_y), (nx, ny), 1)

            # Nucleo del neutron
            rad = 3 if n.energy == NeutronEnergy.THERMAL else 2
            pygame.draw.circle(surface, color, (nx, ny), rad)
