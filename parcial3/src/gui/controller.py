"""
Controlador de sincronizacion: reloj real de Pygame <-> motor de simulacion.

Patron tomado de clasePrompts/estacion/src/engine/controller.py (mismo repo,
solo lectura), adaptado a los dos motores de este parcial y a la distincion
entre "pausar la animacion" y "pausar la simulacion" que pide el enunciado.

DISTINCION CLAVE (letra chica del enunciado, es lo que se pregunta en la
defensa): pausar o reanudar la animacion NO debe detener el calculo logico.

  - `pausa_animacion` (tecla ESPACIO): congela unicamente el estado VISUAL
    (sprites interpolados, parpadeos). El motor sigue recibiendo step() en
    cada frame exactamente igual, y el HUD sigue leyendo datos frescos.
  - `pausa_total` (tecla P): es el extra que si detiene todo, incluido el
    motor. Sirve para congelar la pantalla por completo.

Ninguna de las dos vistas guarda una copia paralela del estado de dominio:
leen `self.sim` en cada frame. Este controlador es el UNICO lugar donde se
decide cuanto avanza el reloj simulado.
"""

from typing import Optional, Union

from src.gui.styles import ESCALA_DEFECTO, ESCALAS_TIEMPO
from src.simulation.continuous_sim import ClusterSimulation
from src.simulation.discrete_sim import FabricaSimulation

Motor = Union[FabricaSimulation, ClusterSimulation]

PROBLEMA_FABRICA = 1
PROBLEMA_CLUSTER = 2


class SimController:
    """
    Envuelve un motor de simulacion (Problema 1 o 2) y sincroniza su reloj
    con el tiempo real de Pygame, sin nunca copiar su estado de dominio.
    """

    def __init__(
        self,
        problema: int,
        horas: float,
        semilla: Optional[int],
        escala_tiempo: float = ESCALA_DEFECTO,
    ) -> None:
        if problema not in (PROBLEMA_FABRICA, PROBLEMA_CLUSTER):
            raise ValueError(f"Problema invalido: {problema}. Debe ser 1 o 2.")
        if horas <= 0:
            raise ValueError(f"Las horas simuladas deben ser positivas: {horas}.")

        self.problema = problema
        self.horas = float(horas)
        self.semilla = semilla
        self.escala_tiempo = float(escala_tiempo)

        self.pausa_animacion: bool = False
        self.pausa_total: bool = False

        self.tiempo_objetivo_s: float = self.horas * 3600.0
        self.sim: Motor = self._crear_motor()

    def _crear_motor(self) -> Motor:
        """Instancia el motor del problema seleccionado con la semilla recibida."""
        if self.problema == PROBLEMA_FABRICA:
            return FabricaSimulation(semilla=self.semilla)
        return ClusterSimulation(semilla=self.semilla)

    def reiniciar(self) -> None:
        """Recrea el motor desde cero, con la misma semilla y parametros."""
        self.sim = self._crear_motor()
        self.pausa_animacion = False
        self.pausa_total = False

    def fijar_escala(self, nivel: int) -> None:
        """Aplica la escala de tiempo asociada a una tecla 1-4."""
        if nivel not in ESCALAS_TIEMPO:
            raise ValueError(f"Nivel de escala invalido: {nivel}. Debe ser 1, 2, 3 o 4.")
        self.escala_tiempo = ESCALAS_TIEMPO[nivel]

    @property
    def terminado(self) -> bool:
        """True cuando el motor ya alcanzo las horas objetivo de la corrida."""
        return self.sim.tiempo_actual >= self.tiempo_objetivo_s

    @property
    def progreso(self) -> float:
        """Fraccion [0, 1] del tiempo objetivo ya simulado."""
        if self.tiempo_objetivo_s <= 0:
            return 1.0
        return min(1.0, self.sim.tiempo_actual / self.tiempo_objetivo_s)

    def step(self, dt_real_s: float) -> None:
        """
        Avanza el motor segun el tiempo real transcurrido y la escala vigente.

        `pausa_total` es la UNICA condicion que detiene esta llamada. La
        pausa de animacion (`pausa_animacion`) es exclusivamente visual y no
        se consulta aca: el motor avanza igual.
        """
        if self.pausa_total or self.terminado:
            return
        objetivo = self.sim.tiempo_actual + dt_real_s * self.escala_tiempo
        objetivo = min(objetivo, self.tiempo_objetivo_s)
        self.sim.step(objetivo)


def _selfcheck() -> None:
    """Verifica la sincronizacion y la distincion pausa-animacion / pausa-total."""
    c1 = SimController(problema=1, horas=1.0, semilla=2026)
    assert isinstance(c1.sim, FabricaSimulation)
    t0 = c1.sim.tiempo_actual
    c1.step(dt_real_s=1.0)
    assert c1.sim.tiempo_actual > t0

    c2 = SimController(problema=2, horas=1.0, semilla=2026)
    assert isinstance(c2.sim, ClusterSimulation)
    t0 = c2.sim.tiempo_actual
    c2.step(dt_real_s=1.0)
    assert c2.sim.tiempo_actual > t0

    # Pausa de animacion: el motor DEBE seguir avanzando.
    c1.pausa_animacion = True
    antes = c1.sim.tiempo_actual
    for _ in range(5):
        c1.step(dt_real_s=0.1)
    assert c1.sim.tiempo_actual > antes, "el motor no avanzo con la animacion en pausa"

    # Pausa total: el motor NO debe avanzar.
    c1.pausa_total = True
    congelado = c1.sim.tiempo_actual
    for _ in range(5):
        c1.step(dt_real_s=0.1)
    assert c1.sim.tiempo_actual == congelado, "pausa_total no congelo el motor"

    # Escalas de tiempo
    c1.fijar_escala(1)
    assert c1.escala_tiempo == 60.0
    c1.fijar_escala(4)
    assert c1.escala_tiempo == 3600.0
    try:
        c1.fijar_escala(9)
    except ValueError:
        pass
    else:
        raise AssertionError("fijar_escala acepto un nivel invalido")

    # Reinicio
    c1.pausa_total = False
    c1.step(dt_real_s=1.0)
    c1.reiniciar()
    assert c1.sim.tiempo_actual == 0.0
    assert not c1.pausa_total and not c1.pausa_animacion

    # Terminado / progreso. 10 s exactos: multiplo del paso de integracion (1 s)
    # del motor continuo, que avanza en grilla y no da pasos parciales.
    c3 = SimController(problema=2, horas=10.0 / 3600.0, semilla=2026)
    c3.step(dt_real_s=100.0)  # de sobra para cubrir el objetivo
    assert c3.terminado
    assert c3.progreso == 1.0

    print("selfcheck controller: OK")


if __name__ == "__main__":
    _selfcheck()
