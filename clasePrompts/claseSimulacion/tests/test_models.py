"""Pruebas unitarias para las clases del modelo de datos."""

import pytest
from src.constants import Direction
from src.models.point import Point
from src.models.food import Food, FoodType
from src.models.snake import Snake
from src.models.stats import SimulationStats


def test_point_arithmetic_and_distance():
    p1 = Point(5, 5)
    p2 = Point(2, 3)

    p_add = p1 + p2
    assert p_add == Point(7, 8)

    p_sub = p1 - p2
    assert p_sub == Point(3, 2)

    assert p1.manhattan_distance(p2) == (abs(5 - 2) + abs(5 - 3)) == 5
    assert p1.is_inside_bounds(10, 10) is True
    assert Point(-1, 5).is_inside_bounds(10, 10) is False
    assert Point(5, 10).is_inside_bounds(10, 10) is False


def test_food_attributes_and_expiration():
    f_normal = Food(Point(3, 4), food_type=FoodType.NORMAL, spawn_time=1.0)
    assert f_normal.points == 10
    assert f_normal.growth_amount == 1
    assert f_normal.is_expired(100.0) is False

    f_bonus = Food(Point(7, 8), food_type=FoodType.BONUS, spawn_time=5.0, lifespan=10.0)
    assert f_bonus.points == 30
    assert f_bonus.growth_amount == 2
    assert f_bonus.is_expired(10.0) is False
    assert f_bonus.is_expired(15.0) is True
    assert f_bonus.time_remaining(12.0) == pytest.approx(3.0)


def test_snake_initialization():
    snake = Snake(initial_head=Point(10, 10), initial_length=3, initial_direction=Direction.RIGHT)
    assert snake.is_alive is True
    assert snake.head == Point(10, 10)
    assert snake.length == 3
    # Debe extenderse hacia la izquierda
    assert list(snake.body) == [Point(10, 10), Point(9, 10), Point(8, 10)]


def test_snake_movement_and_growth():
    snake = Snake(initial_head=Point(10, 10), initial_length=3, initial_direction=Direction.RIGHT)
    new_head, collision = snake.step(grid_width=20, grid_height=20)

    assert collision is False
    assert new_head == Point(11, 10)
    assert snake.head == Point(11, 10)
    assert snake.length == 3
    assert list(snake.body) == [Point(11, 10), Point(10, 10), Point(9, 10)]

    # Probar crecimiento
    snake.grow(amount=2)
    snake.step(grid_width=20, grid_height=20)
    assert snake.length == 4
    snake.step(grid_width=20, grid_height=20)
    assert snake.length == 5


def test_snake_wall_collision():
    snake = Snake(initial_head=Point(19, 5), initial_length=3, initial_direction=Direction.RIGHT)
    new_head, collision = snake.step(grid_width=20, grid_height=20)
    assert collision is True
    assert snake.is_alive is False
    assert "pared" in snake.death_reason.lower()


def test_snake_self_collision():
    # Crear serpiente en espiral que choque consigo misma
    snake = Snake(initial_head=Point(5, 5), initial_length=5, initial_direction=Direction.RIGHT)
    snake.set_direction(Direction.UP)
    snake.step(10, 10)
    snake.set_direction(Direction.LEFT)
    snake.step(10, 10)
    snake.set_direction(Direction.DOWN)
    _, collision = snake.step(10, 10)

    assert collision is True
    assert snake.is_alive is False
    assert "autocolision" in snake.death_reason.lower()


def test_direction_opposite_reversal_blocked():
    snake = Snake(initial_head=Point(5, 5), initial_direction=Direction.RIGHT)
    success = snake.set_direction(Direction.LEFT)
    assert success is False
    assert snake.buffered_direction is None


def test_simulation_stats():
    stats = SimulationStats()
    stats.record_step(sim_time=0.12, current_length=3)
    stats.record_step(sim_time=0.24, current_length=4)
    stats.record_food_eaten(points=10, is_bonus=False)
    stats.record_food_eaten(points=30, is_bonus=True)

    summary = stats.get_summary_dict()
    assert summary["pasos_totales"] == 2
    assert summary["puntos_acumulados"] == 40
    assert summary["alimentos_totales"] == 2
    assert summary["alimentos_normales"] == 1
    assert summary["alimentos_bonus"] == 1
    assert summary["longitud_maxima"] == 4
    assert summary["pasos_por_alimento"] == 1.0
