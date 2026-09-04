"""Renderizado cenital (top-down) del entorno fisico de la estacion de servicio."""

import pygame
from src.constants import (
    SIM_WIDTH,
    WINDOW_HEIGHT,
    COLOR_BG_ROAD,
    COLOR_CONCRETE,
    COLOR_CANOPY_ROOF,
    COLOR_CANOPY_EDGE,
    COLOR_ISLAND,
    COLOR_PUMP_BODY,
    COLOR_PUMP_FREE,
    COLOR_PUMP_BUSY,
    COLOR_PUMP_EMPTY,
    COLOR_LANE_WHITE,
    COLOR_LANE_YELLOW,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    PumpState,
    VehicleState,
    QUEUE_HEAD,
    EXIT_MERGE,
    EXIT_DESPAWN,
)
from src.view.car_drawer import CarDrawer


class StationView:
    """Gestiona el dibujo de la estacion, pistas, surtidores y vehiculos en transito."""

    def __init__(self, fonts: dict):
        self.fonts = fonts

    def update_and_render(self, surface: pygame.Surface, sim, dt: float):
        """
        Actualiza posiciones cinematicas y dibuja toda la estacion.
        surface: Lienzo Pygame de la ventana
        sim: Instancia de GasStationSimulation
        dt: Delta time en segundos reales
        """
        # 1. Asfalto de fondo de la calzada
        road_rect = pygame.Rect(0, 0, SIM_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(surface, COLOR_BG_ROAD, road_rect)

        # 2. Pista de concreto de la estacion de servicio
        station_rect = pygame.Rect(80, 110, 600, 520)
        pygame.draw.rect(surface, COLOR_CONCRETE, station_rect, border_radius=16)
        pygame.draw.rect(surface, (70, 78, 90), station_rect, width=2, border_radius=16)

        # 3. Lineas viales y demarcacion de carriles
        self._draw_road_markings(surface)

        # 4. Marquesina / Techo de la estacion (canopy transparente)
        canopy_rect = pygame.Rect(180, 140, 420, 460)
        canopy_surf = pygame.Surface((canopy_rect.width, canopy_rect.height), pygame.SRCALPHA)
        canopy_surf.fill((COLOR_CANOPY_ROOF[0], COLOR_CANOPY_ROOF[1], COLOR_CANOPY_ROOF[2], 80))
        surface.blit(canopy_surf, canopy_rect.topleft)
        pygame.draw.rect(surface, COLOR_CANOPY_EDGE, canopy_rect, width=2, border_radius=8)

        # Columnas de la marquesina
        columns = [(190, 150), (190, 580), (580, 150), (580, 580)]
        for col_x, col_y in columns:
            pygame.draw.circle(surface, (200, 205, 215), (col_x, col_y), 7)
            pygame.draw.circle(surface, (30, 40, 55), (col_x, col_y), 4)

        # Cartel marquesina
        title_lbl = self.fonts["bold"].render("ESTACION DE SERVICIO UJAP", True, (255, 255, 255))
        surface.blit(title_lbl, (240, 150))

        # 5. Tanque central subterraneo
        self._draw_fuel_tank(surface, sim.tank)

        # 6. Surtidores / Islas de bombas de gasolina
        self._draw_pumps(surface, sim.pumps)

        # 7. Actualizar y renderizar vehiculos
        self._update_and_draw_vehicles(surface, sim, dt)

    def _draw_road_markings(self, surface: pygame.Surface):
        """Demarcacion de lineas de aproximacion, cola y escape."""
        # Linea de espera en cola (flechas y rayas amarillas)
        for x in range(20, 260, 40):
            pygame.draw.line(surface, COLOR_LANE_YELLOW, (x, 370), (x + 20, 370), 2)

        # Entrada y Salida - textos de piso
        in_txt = self.fonts["small"].render("ENTRADA >>", True, (160, 175, 195))
        surface.blit(in_txt, (15, 345))

        out_txt = self.fonts["small"].render("SALIDA >>", True, (160, 175, 195))
        surface.blit(out_txt, (640, 345))

    def _draw_pumps(self, surface: pygame.Surface, pumps):
        """Dibuja las islas de bombas con su estado operativo y mangueras."""
        for pump in pumps:
            px, py = pump.x, pump.y

            # Isla de concreto protectora
            island_rect = pygame.Rect(px - 16, py - 40, 32, 80)
            pygame.draw.rect(surface, COLOR_ISLAND, island_rect, border_radius=6)
            pygame.draw.rect(surface, (100, 110, 125), island_rect, width=1, border_radius=6)

            # Rayas de seguridad en la isla
            pygame.draw.line(surface, COLOR_LANE_YELLOW, (px - 14, py - 32), (px + 14, py - 32), 2)
            pygame.draw.line(surface, COLOR_LANE_YELLOW, (px - 14, py + 32), (px + 14, py + 32), 2)

            # Cuerpo de la bomba
            pump_box = pygame.Rect(px - 10, py - 20, 20, 40)
            pygame.draw.rect(surface, COLOR_PUMP_BODY, pump_box, border_radius=4)

            # Luz LED de estado
            if pump.state == PumpState.FREE:
                led_color = COLOR_PUMP_FREE
            elif pump.state == PumpState.BUSY:
                led_color = COLOR_PUMP_BUSY
            else:
                led_color = COLOR_PUMP_EMPTY

            pygame.draw.circle(surface, led_color, (px, py - 10), 4)

            # Etiqueta de la bomba
            b_lbl = self.fonts["tiny"].render(f"B{pump.id}", True, COLOR_TEXT_MAIN)
            surface.blit(b_lbl, (px - 6, py + 2))

            # Manguera conectada al auto si esta surtiendo
            if pump.current_vehicle and pump.current_vehicle.state == VehicleState.FUELING:
                vx, vy = int(pump.current_vehicle.x), int(pump.current_vehicle.y)
                # Dibuja cable/manguera en arco curvo
                mid_x = (px + vx) // 2
                mid_y = min(py, vy) - 8
                pygame.draw.lines(surface, (20, 20, 25), False, [(px, py), (mid_x, mid_y), (vx - 10, vy)], 2)

    def _draw_fuel_tank(self, surface: pygame.Surface, tank):
        """Dibuja el indicador del tanque subterraneo en la zona superior de la estacion."""
        tx, ty = 480, 145
        tw, th = 110, 18

        # Contenedor del tanque
        pygame.draw.rect(surface, (25, 30, 40), (tx, ty, tw, th), border_radius=4)
        prog_w = int(tw * (tank.percent / 100.0))

        # Color segun nivel
        if tank.percent > 40:
            fill_col = (34, 197, 94)
        elif tank.percent > 20:
            fill_col = (234, 179, 8)
        else:
            fill_col = (239, 68, 68)

        pygame.draw.rect(surface, fill_col, (tx, ty, prog_w, th), border_radius=4)
        pygame.draw.rect(surface, (120, 130, 145), (tx, ty, tw, th), width=1, border_radius=4)

        lbl = self.fonts["tiny"].render(f"Tanque: {int(tank.level)}L ({int(tank.percent)}%)", True, (255, 255, 255))
        surface.blit(lbl, (tx, ty - 14))

        if tank.is_refilling:
            refill_lbl = self.fonts["tiny"].render("REABASTECIENDO...", True, (56, 189, 248))
            surface.blit(refill_lbl, (tx, ty + 20))

    def _update_and_draw_vehicles(self, surface: pygame.Surface, sim, dt: float):
        """Gestiona la cola ordenada, trayectorias y dibujo de todos los autos."""
        # 1. Asignar waypoints a vehiculos en cola
        slot_spacing = 56
        for idx, vehicle in enumerate(sim.vehicles_in_queue):
            target_x = QUEUE_HEAD[0] - idx * slot_spacing
            target_y = QUEUE_HEAD[1]
            vehicle.set_target(target_x, target_y, angle=0.0)

        # 2. Asignar waypoints a vehiculos activos dirigiendose a bombas
        for vehicle in sim.vehicles_active:
            if vehicle.assigned_pump_id:
                pump = next((p for p in sim.pumps if p.id == vehicle.assigned_pump_id), None)
                if pump:
                    # El auto se estaciona al lado izquierdo de la bomba
                    target_x = pump.x - 30
                    target_y = pump.y
                    if not vehicle.waypoints and (abs(vehicle.x - target_x) > 3 or abs(vehicle.y - target_y) > 3):
                        vehicle.set_target(target_x, target_y, angle=0.0)

        # 3. Asignar waypoints a vehiculos en salida
        for vehicle in sim.vehicles_departing:
            if not vehicle.waypoints:
                # Ruta de salida: avanzar hacia EXIT_MERGE y luego EXIT_DESPAWN
                if vehicle.x < EXIT_MERGE[0] - 10:
                    vehicle.add_waypoint(EXIT_MERGE[0], EXIT_MERGE[1], angle=0.0)
                vehicle.add_waypoint(EXIT_DESPAWN[0], EXIT_DESPAWN[1], angle=0.0)

        # 4. Actualizar movimiento y dibujar todos los vehiculos
        all_vehicles = sim.vehicles_in_queue + sim.vehicles_active + sim.vehicles_departing
        for vehicle in all_vehicles:
            vehicle.update_motion(dt)
            CarDrawer.draw_car(surface, vehicle, self.fonts["tiny"])
