"""Modulo para la recoleccion y calculo de metricas cuantitativas de simulacion."""

from typing import Dict, Any, List


class SimulationStats:
    """
    Rastrea metricas cuantitativas de desempeno:
    - Tiempo de supervivencia (reloj SimPy vs tiempo real)
    - Tasa de ingesta de alimentos
    - Eficiencia de pasos por unidad de alimento
    - Puntuacion y longitud alcanzada
    """

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self.sim_start_time: float = 0.0
        self.current_sim_time: float = 0.0
        self.total_steps: int = 0
        self.food_eaten_normal: int = 0
        self.food_eaten_bonus: int = 0
        self.total_food_eaten: int = 0
        self.score: int = 0
        self.max_length: int = 3
        self.history_samples: List[Dict[str, Any]] = []

    def record_step(self, sim_time: float, current_length: int) -> None:
        """Registra un paso de avance de la simulacion."""
        self.total_steps += 1
        self.current_sim_time = sim_time
        if current_length > self.max_length:
            self.max_length = current_length

    def record_food_eaten(self, points: int, is_bonus: bool) -> None:
        """Registra la ingesta de alimento."""
        self.score += points
        self.total_food_eaten += 1
        if is_bonus:
            self.food_eaten_bonus += 1
        else:
            self.food_eaten_normal += 1

    def sample_metrics(self, sim_time: float) -> None:
        """Toma una muestra instantanea para analisis cuantitativo."""
        sample = {
            "sim_time": round(sim_time, 2),
            "steps": self.total_steps,
            "score": self.score,
            "food_total": self.total_food_eaten,
            "efficiency": round(self.steps_per_food, 2),
        }
        self.history_samples.append(sample)

    @property
    def survival_time(self) -> float:
        """Tiempo de supervivencia en segundos simulados."""
        return max(0.0, self.current_sim_time - self.sim_start_time)

    @property
    def steps_per_food(self) -> float:
        """Eficiencia: pasos promedio requeridos para capturar un alimento."""
        if self.total_food_eaten == 0:
            return float(self.total_steps)
        return self.total_steps / self.total_food_eaten

    def get_summary_dict(self) -> Dict[str, Any]:
        """Genera un diccionario resumen con las metricas consolidadas."""
        return {
            "tiempo_simulado_seg": round(self.survival_time, 2),
            "pasos_totales": self.total_steps,
            "puntos_acumulados": self.score,
            "alimentos_totales": self.total_food_eaten,
            "alimentos_normales": self.food_eaten_normal,
            "alimentos_bonus": self.food_eaten_bonus,
            "longitud_maxima": self.max_length,
            "pasos_por_alimento": round(self.steps_per_food, 2),
        }
