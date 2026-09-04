"""Pruebas unitarias para el entorno de simulacion SimPy y el agente autonomo."""

from src.constants import ControlMode, Direction
from src.models.point import Point
from src.models.snake import Snake
from src.simulation.ai_agent import SnakeAIAgent
from src.simulation.environment import SnakeSimulationEnvironment


def test_simpy_environment_advancement():
    env = SnakeSimulationEnvironment(
        grid_width=15,
        grid_height=15,
        control_mode=ControlMode.MANUAL,
        base_step_interval=0.1,
    )

    assert env.env.now == 0.0
    assert env.snake.is_alive is True
    assert len(env.foods) >= 1

    # Avanzar 0.5 segundos en SimPy (equivalente a 5 pasos)
    env.advance_to(0.55)
    assert env.env.now >= 0.5
    assert env.stats.total_steps >= 4


def test_ai_agent_shortest_path_to_food():
    agent = SnakeAIAgent(grid_width=10, grid_height=10)
    snake = Snake(initial_head=Point(2, 2), initial_length=3, initial_direction=Direction.RIGHT)

    # Comida a la derecha
    food_pos = Point(5, 2)
    direction = agent.decide_next_direction(snake, food_pos)
    assert direction == Direction.RIGHT

    # Comida hacia abajo
    food_pos_down = Point(2, 6)
    # Cambiamos direccion actual hacia abajo para permitir giro
    snake.direction = Direction.DOWN
    direction_down = agent.decide_next_direction(snake, food_pos_down)
    assert direction_down == Direction.DOWN


def test_simulation_reset():
    env = SnakeSimulationEnvironment(grid_width=15, grid_height=15)
    env.advance_to(1.0)
    assert env.env.now >= 1.0

    env.reset()
    assert env.env.now == 0.0
    assert env.stats.total_steps == 0
    assert env.snake.length == 3
    assert env.snake.is_alive is True
