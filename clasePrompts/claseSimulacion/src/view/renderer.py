"""Motor de renderizado y visualizacion con Pygame."""

import math
from typing import Optional
import pygame

from ..constants import (
    CELL_SIZE,
    COLOR_ACCENT_BLUE,
    COLOR_ACCENT_PURPLE,
    COLOR_BG_PLAY,
    COLOR_BG_SIDEBAR,
    COLOR_BORDER,
    COLOR_DANGER,
    COLOR_FOOD_BONUS,
    COLOR_FOOD_NORMAL,
    COLOR_GRID_LINE,
    COLOR_SNAKE_BODY,
    COLOR_SNAKE_EYE,
    COLOR_SNAKE_HEAD,
    COLOR_SNAKE_PUPIL,
    COLOR_SUCCESS,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_WARNING,
    ControlMode,
    Direction,
    GRID_HEIGHT,
    GRID_WIDTH,
    PLAY_HEIGHT,
    PLAY_WIDTH,
    SIDEBAR_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    GameState,
)
from ..models.food import Food, FoodType
from ..models.point import Point
from ..models.snake import Snake
from ..simulation.environment import SnakeSimulationEnvironment


class GameRenderer:
    """Encapsula todas las operaciones graficas sobre la superficie de Pygame."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        pygame.font.init()

        # Fuentes tipograficas
        self.font_title = pygame.font.SysFont("Helvetica, Arial, sans-serif", 18, bold=True)
        self.font_subtitle = pygame.font.SysFont("Helvetica, Arial, sans-serif", 13, bold=True)
        self.font_body = pygame.font.SysFont("Helvetica, Arial, sans-serif", 13)
        self.font_stat_val = pygame.font.SysFont("Helvetica, Arial, sans-serif", 16, bold=True)
        self.font_small = pygame.font.SysFont("Helvetica, Arial, sans-serif", 11)
        self.font_large = pygame.font.SysFont("Helvetica, Arial, sans-serif", 28, bold=True)

    def render(
        self,
        sim_env: SnakeSimulationEnvironment,
        game_state: GameState,
        speed_multiplier: float,
        fps: float,
    ) -> None:
        """Dibuja un fotograma completo: tablero, entidades y panel lateral."""
        # 1. Limpiar fondo
        self.screen.fill(COLOR_BG_PLAY)

        # 2. Dibujar cuadricula del area de juego
        self._draw_grid()

        # 3. Dibujar alimentos
        self._draw_foods(sim_env.foods, sim_env.env.now)

        # 4. Dibujar serpiente
        self._draw_snake(sim_env.snake)

        # 5. Dibujar linea divisoria
        pygame.draw.line(
            self.screen,
            COLOR_BORDER,
            (PLAY_WIDTH, 0),
            (PLAY_WIDTH, WINDOW_HEIGHT),
            2,
        )

        # 6. Dibujar panel lateral con metricas
        self._draw_sidebar(sim_env, game_state, speed_multiplier, fps)

        # 7. Superposicion segun estado (Pausa o Fin de juego)
        if game_state == GameState.PAUSED:
            self._draw_overlay("SIMULACION PAUSADA", "Presiona [ESPACIO] para reanudar", COLOR_WARNING)
        elif game_state == GameState.GAME_OVER:
            death_msg = sim_env.snake.death_reason or "Colision fatal"
            self._draw_overlay("FIN DE LA SIMULACION", f"{death_msg} - [R] Reiniciar", COLOR_DANGER)

    def _draw_grid(self) -> None:
        """Dibuja las lineas tenues de la cuadricula de juego."""
        for x in range(0, PLAY_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID_LINE, (x, 0), (x, PLAY_HEIGHT), 1)
        for y in range(0, PLAY_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID_LINE, (0, y), (PLAY_WIDTH, y), 1)

    def _draw_snake(self, snake: Snake) -> None:
        """Renderiza los segmentos y la cabeza de la serpiente con detalles vectoriales."""
        body = list(snake.body)
        if not body:
            return

        # Dibujar segmentos del cuerpo
        for i, segment in enumerate(body[1:], start=1):
            px, py = segment.to_pixels(CELL_SIZE)
            rect = pygame.Rect(px + 2, py + 2, CELL_SIZE - 4, CELL_SIZE - 4)

            # Efecto de degradado leve a lo largo del cuerpo
            decay = min(0.3, i * 0.005)
            r = int(COLOR_SNAKE_BODY[0] * (1.0 - decay))
            g = int(COLOR_SNAKE_BODY[1] * (1.0 - decay))
            b = int(COLOR_SNAKE_BODY[2] * (1.0 - decay))
            pygame.draw.rect(self.screen, (r, g, b), rect, border_radius=4)

        # Dibujar cabeza
        head = snake.head
        hx, hy = head.to_pixels(CELL_SIZE)
        head_rect = pygame.Rect(hx + 1, hy + 1, CELL_SIZE - 2, CELL_SIZE - 2)
        pygame.draw.rect(self.screen, COLOR_SNAKE_HEAD, head_rect, border_radius=6)

        # Ojos de la serpiente orientados segun la direccion
        self._draw_eyes(hx, hy, snake.direction)

    def _draw_eyes(self, hx: int, hy: int, direction: Direction) -> None:
        """Dibuja los ojos de la serpiente apuntando en la direccion de movimiento."""
        cx = hx + CELL_SIZE // 2
        cy = hy + CELL_SIZE // 2

        offset = 4
        eye_radius = 2.5
        pupil_radius = 1.2

        if direction == Direction.RIGHT:
            eye1 = (cx + 3, cy - offset)
            eye2 = (cx + 3, cy + offset)
            p_offset = (1, 0)
        elif direction == Direction.LEFT:
            eye1 = (cx - 3, cy - offset)
            eye2 = (cx - 3, cy + offset)
            p_offset = (-1, 0)
        elif direction == Direction.UP:
            eye1 = (cx - offset, cy - 3)
            eye2 = (cx + offset, cy - 3)
            p_offset = (0, -1)
        else:  # DOWN
            eye1 = (cx - offset, cy + 3)
            eye2 = (cx + offset, cy + 3)
            p_offset = (0, 1)

        for eye in (eye1, eye2):
            pygame.draw.circle(self.screen, COLOR_SNAKE_EYE, eye, eye_radius)
            pupil = (eye[0] + p_offset[0], eye[1] + p_offset[1])
            pygame.draw.circle(self.screen, COLOR_SNAKE_PUPIL, pupil, pupil_radius)

    def _draw_foods(self, foods: list[Food], current_sim_time: float) -> None:
        """Dibuja los alimentos con animacion de pulso para alimentos especiales."""
        for food in foods:
            px, py = food.position.to_pixels(CELL_SIZE)
            cx = px + CELL_SIZE // 2
            cy = py + CELL_SIZE // 2

            if food.food_type == FoodType.BONUS:
                # Efecto pulsante estocastico
                pulse = 1.0 + 0.2 * math.sin(current_sim_time * 8.0)
                radius = int((CELL_SIZE // 2 - 3) * pulse)
                pygame.draw.circle(self.screen, COLOR_FOOD_BONUS, (cx, cy), max(2, radius))
                pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), max(1, radius // 2))

                # Anillo de expiracion
                rem = food.time_remaining(current_sim_time)
                if food.lifespan and rem < 5.0:
                    pygame.draw.circle(self.screen, COLOR_DANGER, (cx, cy), CELL_SIZE // 2, 1)
            else:
                radius = CELL_SIZE // 2 - 4
                pygame.draw.circle(self.screen, COLOR_FOOD_NORMAL, (cx, cy), radius)
                # Brillo superior
                pygame.draw.circle(
                    self.screen,
                    (255, 200, 200),
                    (cx - radius // 3, cy - radius // 3),
                    radius // 3,
                )

    def _draw_sidebar(
        self,
        sim_env: SnakeSimulationEnvironment,
        game_state: GameState,
        speed_multiplier: float,
        fps: float,
    ) -> None:
        """Renderiza el panel lateral con metricas cuantitativas e informacion del modelo."""
        sidebar_rect = pygame.Rect(PLAY_WIDTH, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_BG_SIDEBAR, sidebar_rect)

        x_margin = PLAY_WIDTH + 18
        y = 16

        # Titulo de la materia y proyecto
        lbl_inst = self.font_small.render("UJAP - METODOS CUANTITATIVOS", True, COLOR_ACCENT_BLUE)
        self.screen.blit(lbl_inst, (x_margin, y))
        y += 18

        lbl_proj = self.font_title.render("Simulacion Snake", True, COLOR_TEXT_PRIMARY)
        self.screen.blit(lbl_proj, (x_margin, y))
        y += 24

        lbl_sub = self.font_small.render("Motor SimPy + Pygame (POO)", True, COLOR_TEXT_MUTED)
        self.screen.blit(lbl_sub, (x_margin, y))
        y += 20

        pygame.draw.line(self.screen, COLOR_BORDER, (x_margin, y), (WINDOW_WIDTH - 18, y), 1)
        y += 14

        # Estado y Modo
        mode_color = (
            COLOR_ACCENT_PURPLE
            if sim_env.control_mode == ControlMode.AUTO_AI
            else COLOR_SUCCESS
        )
        self._draw_key_value(x_margin, y, "MODO:", sim_env.control_mode.value, mode_color)
        y += 26

        state_str = game_state.name
        state_color = COLOR_SUCCESS if game_state == GameState.RUNNING else COLOR_WARNING
        if game_state == GameState.GAME_OVER:
            state_color = COLOR_DANGER
        self._draw_key_value(x_margin, y, "ESTADO:", state_str, state_color)
        y += 26

        pygame.draw.line(self.screen, COLOR_BORDER, (x_margin, y), (WINDOW_WIDTH - 18, y), 1)
        y += 14

        # Metricas Cuantitativas
        sec_hdr = self.font_subtitle.render("Metricas de Simulacion", True, COLOR_ACCENT_BLUE)
        self.screen.blit(sec_hdr, (x_margin, y))
        y += 22

        sim_time_str = f"{sim_env.env.now:.2f} s"
        self._draw_key_value(x_margin, y, "Reloj SimPy:", sim_time_str, COLOR_TEXT_PRIMARY)
        y += 22

        self._draw_key_value(x_margin, y, "Puntos:", str(sim_env.stats.score), COLOR_SUCCESS)
        y += 22

        self._draw_key_value(x_margin, y, "Longitud:", str(sim_env.snake.length), COLOR_TEXT_PRIMARY)
        y += 22

        self._draw_key_value(x_margin, y, "Alimentos Totales:", str(sim_env.stats.total_food_eaten), COLOR_TEXT_PRIMARY)
        y += 22

        bonus_str = f"{sim_env.stats.food_eaten_bonus} esp."
        self._draw_key_value(x_margin, y, "Bonus consumidos:", bonus_str, COLOR_FOOD_BONUS)
        y += 22

        self._draw_key_value(x_margin, y, "Pasos discretos:", str(sim_env.stats.total_steps), COLOR_TEXT_PRIMARY)
        y += 22

        eff = sim_env.stats.steps_per_food
        eff_str = f"{eff:.2f} p/alim" if eff < 9999 else "N/A"
        self._draw_key_value(x_margin, y, "Eficiencia (pasos):", eff_str, COLOR_TEXT_PRIMARY)
        y += 22

        interval_str = f"{sim_env.current_step_interval:.3f} s"
        self._draw_key_value(x_margin, y, "Intervalo paso:", interval_str, COLOR_TEXT_MUTED)
        y += 22

        fps_str = f"{fps:.0f} (vel: {speed_multiplier:.1f}x)"
        self._draw_key_value(x_margin, y, "FPS / Multiplicador:", fps_str, COLOR_TEXT_MUTED)
        y += 26

        pygame.draw.line(self.screen, COLOR_BORDER, (x_margin, y), (WINDOW_WIDTH - 18, y), 1)
        y += 14

        # Controles disponibles
        ctrl_hdr = self.font_subtitle.render("Controles", True, COLOR_ACCENT_BLUE)
        self.screen.blit(ctrl_hdr, (x_margin, y))
        y += 20

        controls = [
            ("[Flechas / WASD]", "Direccion serpiente"),
            ("[ESPACIO]", "Pausar / Reanudar"),
            ("[M]", "Alternar Manual / IA"),
            ("[1 / 2 / 3]", "Velocidad 1x, 2x, 4x"),
            ("[R]", "Reiniciar simulacion"),
        ]

        for key, desc in controls:
            k_surf = self.font_small.render(key, True, COLOR_ACCENT_BLUE)
            d_surf = self.font_small.render(desc, True, COLOR_TEXT_MUTED)
            self.screen.blit(k_surf, (x_margin, y))
            self.screen.blit(d_surf, (x_margin + 90, y))
            y += 18

    def _draw_key_value(
        self, x: int, y: int, label: str, value: str, val_color: tuple[int, int, int]
    ) -> None:
        lbl_surf = self.font_body.render(label, True, COLOR_TEXT_MUTED)
        val_surf = self.font_stat_val.render(value, True, val_color)
        self.screen.blit(lbl_surf, (x, y))
        self.screen.blit(val_surf, (x + 130, y - 1))

    def _draw_overlay(self, title: str, subtitle: str, color: tuple[int, int, int]) -> None:
        """Dibuja una marquesina de superposicion en el area de juego."""
        overlay = pygame.Surface((PLAY_WIDTH, PLAY_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 14, 23, 200))
        self.screen.blit(overlay, (0, 0))

        title_surf = self.font_large.render(title, True, color)
        sub_surf = self.font_subtitle.render(subtitle, True, COLOR_TEXT_PRIMARY)

        tx = (PLAY_WIDTH - title_surf.get_width()) // 2
        ty = PLAY_HEIGHT // 2 - 30
        sx = (PLAY_WIDTH - sub_surf.get_width()) // 2
        sy = ty + 45

        self.screen.blit(title_surf, (tx, ty))
        self.screen.blit(sub_surf, (sx, sy))
