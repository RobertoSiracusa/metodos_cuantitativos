"""Agente autonomo basado en busqueda por anchura (BFS) y heuristica de supervivencia."""

from collections import deque
from typing import Dict, List, Optional, Set
from ..constants import Direction, GRID_HEIGHT, GRID_WIDTH
from ..models.point import Point
from ..models.snake import Snake


class SnakeAIAgent:
    """
    Agente de IA para el modo de simulacion autonoma.
    Utiliza BFS para encontrar la ruta mas corta hacia el alimento evitando colisiones.
    Si no hay ruta directa al alimento, busca el movimiento mas seguro con mayor espacio libre.
    """

    def __init__(self, grid_width: int = GRID_WIDTH, grid_height: int = GRID_HEIGHT):
        self.grid_width = grid_width
        self.grid_height = grid_height

    def decide_next_direction(
        self, snake: Snake, target_food_pos: Optional[Point]
    ) -> Direction:
        """Determina la direccion optima para el siguiente paso."""
        if not snake.is_alive:
            return snake.direction

        head = snake.head
        obstacles = snake.occupied_points

        # 1. Si hay comida disponible, intentar ruta BFS mas corta
        if target_food_pos is not None:
            path = self._bfs_shortest_path(head, target_food_pos, obstacles)
            if path and len(path) > 1:
                next_point = path[1]
                chosen_dir = self._point_to_direction(head, next_point)
                if chosen_dir and not chosen_dir.is_opposite(snake.direction):
                    return chosen_dir

        # 2. Heuristica de seguridad: buscar movimiento valido con mayor espacio navegable
        valid_moves = self._get_safe_moves(snake)
        if not valid_moves:
            # Sin movimientos seguros, mantener direccion actual
            return snake.direction

        # Evaluar espacio libre accesible desde cada movimiento candidato (inundacion/flood fill)
        best_dir = valid_moves[0]
        max_free_space = -1

        for candidate_dir in valid_moves:
            next_point = Point(head.x + candidate_dir.dx, head.y + candidate_dir.dy)
            free_space = self._count_accessible_spaces(next_point, obstacles)
            if free_space > max_free_space:
                max_free_space = free_space
                best_dir = candidate_dir

        return best_dir

    def _get_safe_moves(self, snake: Snake) -> List[Direction]:
        """Retorna las direcciones que no provocan colision inmediata."""
        head = snake.head
        obstacles = snake.occupied_points
        safe: List[Direction] = []

        for d in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
            if d.is_opposite(snake.direction):
                continue
            next_pt = Point(head.x + d.dx, head.y + d.dy)
            if next_pt.is_inside_bounds(self.grid_width, self.grid_height):
                if next_pt not in obstacles:
                    safe.append(d)
        return safe

    def _bfs_shortest_path(
        self, start: Point, goal: Point, obstacles: Set[Point]
    ) -> Optional[List[Point]]:
        """Busqueda por anchura para encontrar la ruta minima sin colisiones."""
        queue: deque[Point] = deque([start])
        visited: Set[Point] = {start}
        parent_map: Dict[Point, Point] = {}

        while queue:
            current = queue.popleft()
            if current == goal:
                # Reconstruir camino
                path = [goal]
                curr_node = goal
                while curr_node != start:
                    curr_node = parent_map[curr_node]
                    path.append(curr_node)
                path.reverse()
                return path

            for d in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
                neighbor = Point(current.x + d.dx, current.y + d.dy)
                if (
                    neighbor.is_inside_bounds(self.grid_width, self.grid_height)
                    and (neighbor not in obstacles or neighbor == goal)
                    and neighbor not in visited
                ):
                    visited.add(neighbor)
                    parent_map[neighbor] = current
                    queue.append(neighbor)
        return None

    def _count_accessible_spaces(self, start: Point, obstacles: Set[Point], limit: int = 50) -> int:
        """Cuenta celdas alcanzables (flood fill limitado) para evitar callejones sin salida."""
        queue: deque[Point] = deque([start])
        visited: Set[Point] = {start}
        count = 0

        while queue and count < limit:
            curr = queue.popleft()
            count += 1
            for d in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
                neighbor = Point(curr.x + d.dx, curr.y + d.dy)
                if (
                    neighbor.is_inside_bounds(self.grid_width, self.grid_height)
                    and neighbor not in obstacles
                    and neighbor not in visited
                ):
                    visited.add(neighbor)
                    queue.append(neighbor)
        return count

    @staticmethod
    def _point_to_direction(from_pt: Point, to_pt: Point) -> Optional[Direction]:
        dx = to_pt.x - from_pt.x
        dy = to_pt.y - from_pt.y
        for d in Direction:
            if d.dx == dx and d.dy == dy:
                return d
        return None
