"""Entorno de simulacion por eventos discretos utilizando SimPy."""

import random
from typing import Callable, List, Optional
import simpy

from ..constants import (
    BONUS_FOOD_LIFESPAN,
    BONUS_FOOD_PROBABILITY,
    ControlMode,
    DEFAULT_STEP_INTERVAL,
    FOOD_EXPIRATION_CHECK_INTERVAL,
    GRID_HEIGHT,
    GRID_WIDTH,
    MIN_STEP_INTERVAL,
    SPEED_DECREMENT_PER_FOOD,
)
from ..models.food import Food, FoodType
from ..models.point import Point
from ..models.snake import Snake
from ..models.stats import SimulationStats
from .ai_agent import SnakeAIAgent


class SnakeSimulationEnvironment:
    """
    Controlador del modelo de simulacion con SimPy:
    - Modela el tiempo de avance de la serpiente como un proceso estocastico/discreto.
    - Modela la aparicion, ciclo de vida y expiracion de alimentos.
    - Recolecta periodicamente datos cuantitativos para analisis.
    """

    def __init__(
        self,
        grid_width: int = GRID_WIDTH,
        grid_height: int = GRID_HEIGHT,
        control_mode: ControlMode = ControlMode.MANUAL,
        base_step_interval: float = DEFAULT_STEP_INTERVAL,
        on_game_over_callback: Optional[Callable[[], None]] = None,
    ):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.control_mode = control_mode
        self.base_step_interval = base_step_interval
        self.current_step_interval = base_step_interval
        self.on_game_over_callback = on_game_over_callback

        self.ai_agent = SnakeAIAgent(grid_width, grid_height)
        self.stats = SimulationStats()
        self.foods: List[Food] = []

        # Instancia de SimPy
        self.env: simpy.Environment = simpy.Environment()
        self.snake = Snake(
            initial_head=Point(grid_width // 2, grid_height // 2),
            initial_length=3,
        )

        self._init_processes()

    def reset(self) -> None:
        """Reinicia el entorno de simulacion de SimPy y el estado de juego."""
        self.env = simpy.Environment()
        self.current_step_interval = self.base_step_interval
        self.foods.clear()
        self.snake.reset(
            initial_head=Point(self.grid_width // 2, self.grid_height // 2),
            initial_length=3,
        )
        self.stats.reset()
        self._init_processes()

    def _init_processes(self) -> None:
        """Registra los procesos concurrentes de SimPy."""
        # Generar comida inicial
        self._spawn_food(FoodType.NORMAL)

        # Iniciar procesos de SimPy
        self.env.process(self._snake_step_process())
        self.env.process(self._food_lifecycle_process())
        self.env.process(self._metrics_sampler_process())

    def _snake_step_process(self):
        """Proceso SimPy: temporizacion del movimiento discreto de la serpiente."""
        while self.snake.is_alive:
            # Si esta en modo IA, consultar al agente autonomo
            if self.control_mode == ControlMode.AUTO_AI:
                target_food = self._get_primary_target_food()
                next_dir = self.ai_agent.decide_next_direction(self.snake, target_food)
                self.snake.set_direction(next_dir)

            # Ejecutar el paso
            _, collision = self.snake.step(self.grid_width, self.grid_height)

            if collision:
                if self.on_game_over_callback:
                    self.on_game_over_callback()
                break

            # Registrar paso en metricas
            self.stats.record_step(self.env.now, self.snake.length)

            # Verificar si capturo algun alimento
            self._check_food_consumption()

            # Esperar el tiempo de retardo hasta el siguiente paso (evento SimPy)
            yield self.env.timeout(self.current_step_interval)

    def _food_lifecycle_process(self):
        """Proceso SimPy: gestiona el ciclo estocastico de aparicion y expiracion de alimentos."""
        while True:
            yield self.env.timeout(FOOD_EXPIRATION_CHECK_INTERVAL)

            # 1. Limpiar alimentos especiales expirados
            now = self.env.now
            active_foods = []
            for f in self.foods:
                if not f.is_expired(now):
                    active_foods.append(f)
            self.foods = active_foods

            # 2. Asegurar que siempre exista al menos un alimento normal
            has_normal = any(f.food_type == FoodType.NORMAL for f in self.foods)
            if not has_normal and self.snake.is_alive:
                self._spawn_food(FoodType.NORMAL)

            # 3. Probabilidad estocastica de aparicion de comida especial (Bonus)
            has_bonus = any(f.food_type == FoodType.BONUS for f in self.foods)
            if (
                not has_bonus
                and self.snake.is_alive
                and random.random() < BONUS_FOOD_PROBABILITY
            ):
                self._spawn_food(
                    FoodType.BONUS,
                    lifespan=BONUS_FOOD_LIFESPAN,
                )

    def _metrics_sampler_process(self):
        """Proceso SimPy: muestreo periodico de desempeno para analisis cuantitativo."""
        while True:
            yield self.env.timeout(1.0)
            if self.snake.is_alive:
                self.stats.sample_metrics(self.env.now)

    def _check_food_consumption(self) -> None:
        """Verifica si la cabeza alcanzo una unidad de comida."""
        head = self.snake.head
        remaining_foods = []

        for food in self.foods:
            if food.position == head:
                # Comida consumida
                self.snake.grow(food.growth_amount)
                self.stats.record_food_eaten(
                    points=food.points,
                    is_bonus=(food.food_type == FoodType.BONUS),
                )
                # Aceleracion gradual
                self.current_step_interval = max(
                    MIN_STEP_INTERVAL,
                    self.current_step_interval - SPEED_DECREMENT_PER_FOOD,
                )
            else:
                remaining_foods.append(food)

        self.foods = remaining_foods

        # Si se consumio la comida normal, reponerla de inmediato
        if not any(f.food_type == FoodType.NORMAL for f in self.foods) and self.snake.is_alive:
            self._spawn_food(FoodType.NORMAL)

    def _spawn_food(
        self,
        food_type: FoodType,
        lifespan: Optional[float] = None,
    ) -> Optional[Food]:
        """Ubica un nuevo alimento en una posicion desocupada aleatoria."""
        occupied = set(self.snake.occupied_points)
        for f in self.foods:
            occupied.add(f.position)

        available_points = [
            Point(x, y)
            for x in range(self.grid_width)
            for y in range(self.grid_height)
            if Point(x, y) not in occupied
        ]

        if not available_points:
            return None

        chosen_pos = random.choice(available_points)
        food = Food(
            position=chosen_pos,
            food_type=food_type,
            spawn_time=self.env.now,
            lifespan=lifespan,
        )
        self.foods.append(food)
        return food

    def _get_primary_target_food(self) -> Optional[Point]:
        """Determina la comida objetivo prioritaria (prioriza bonus si existe)."""
        if not self.foods:
            return None
        bonus = [f for f in self.foods if f.food_type == FoodType.BONUS]
        if bonus:
            return bonus[0].position
        return self.foods[0].position

    def advance_to(self, target_time: float) -> None:
        """Avanza los eventos de SimPy hasta target_time."""
        if target_time > self.env.now and self.snake.is_alive:
            try:
                self.env.run(until=target_time)
            except simpy.core.EmptySchedule:
                pass

    def toggle_control_mode(self) -> ControlMode:
        """Alterna entre control Manual y Simulacion IA."""
        if self.control_mode == ControlMode.MANUAL:
            self.control_mode = ControlMode.AUTO_AI
        else:
            self.control_mode = ControlMode.MANUAL
        return self.control_mode
