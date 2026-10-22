"""Metricas de colas de la simulacion y comparacion con el modelo M/M/1 teorico (R6)."""

from __future__ import annotations

import math


class MetricasColas:
    """Acumula los tiempos de cada paquete y muestras periodicas del sistema.

    - Wq: espera en cola (llegada al servidor -> inicio del servicio).
    - W:  tiempo en el servidor (llegada al servidor -> fin del servicio).
    - Lq: largo medio de las colas, promedio de las muestras tomadas en cada tick.
    - Utilizacion: fraccion media de la capacidad de los servidores ocupada.
    """

    def __init__(self) -> None:
        self._llegadas: dict[str, float] = {}
        self._inicios: dict[str, float] = {}
        self._esperas: list[float] = []
        self._sistemas: list[float] = []
        self._muestras_lq: list[float] = []
        self._muestras_utilizacion: list[float] = []
        self._generados = 0
        self._perdidos: dict[str, int] = {}
        self._tiempo = 0.0

    def generado(self) -> None:
        self._generados += 1

    def llegada(self, paquete_id: str, t: float) -> None:
        self._llegadas[paquete_id] = t

    def inicio_servicio(self, paquete_id: str, t: float) -> None:
        self._inicios[paquete_id] = t
        self._esperas.append(t - self._llegadas[paquete_id])

    def fin_servicio(self, paquete_id: str, t: float) -> None:
        self._sistemas.append(t - self._llegadas.pop(paquete_id))
        self._inicios.pop(paquete_id, None)

    def perdido(self, motivo: str) -> None:
        self._perdidos[motivo] = self._perdidos.get(motivo, 0) + 1

    def muestrear(self, t: float, largo_colas: int, utilizacion: float) -> None:
        self._tiempo = t
        self._muestras_lq.append(largo_colas)
        self._muestras_utilizacion.append(utilizacion)

    def resumen(self) -> dict[str, float]:
        def promedio(valores: list[float]) -> float:
            return sum(valores) / len(valores) if valores else 0.0

        completados = len(self._sistemas)
        return {
            "generados": self._generados,
            "completados": completados,
            "perdidos": sum(self._perdidos.values()),
            "perdidos_sin_ruta": self._perdidos.get("sin_ruta", 0),
            "perdidos_sin_servidor": self._perdidos.get("sin_servidor", 0),
            "en_sistema": len(self._llegadas),
            "Wq": promedio(self._esperas),
            "W": promedio(self._sistemas),
            "Lq": promedio(self._muestras_lq),
            "utilizacion": promedio(self._muestras_utilizacion),
            "throughput": completados / self._tiempo if self._tiempo > 0 else 0.0,
        }

    @staticmethod
    def comparar_mm1(lam: float, mu: float) -> dict[str, float]:
        """Formulas de la cola M/M/1 con tasa de llegada `lam` y de servicio `mu`.

        rho = lam / mu,  Lq = rho^2 / (1 - rho),  Wq = rho / (mu - lam),  W = 1 / (mu - lam)
        Si rho >= 1 la cola no es estable y los tiempos son infinitos.
        """
        rho = lam / mu
        if rho >= 1:
            return {"rho": rho, "Lq": math.inf, "Wq": math.inf, "W": math.inf}
        return {"rho": rho, "Lq": rho**2 / (1 - rho), "Wq": rho / (mu - lam), "W": 1 / (mu - lam)}
