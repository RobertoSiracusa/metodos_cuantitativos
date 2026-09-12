"""
Modelo termico y de rendimiento del Problema 2 (cluster de servidores).

Balance termico de primer orden:

    C * dT/dt = P_idle + k * trafico - h * (T - T_amb)

    C       capacidad termica del cluster           [J/C]
    P_idle  potencia disipada en reposo             [W]
    k       potencia adicional por Gbps de trafico  [W/Gbps]
    h       coeficiente de disipacion del circuito
            de refrigeracion liquida                [W/C]
    T_amb   temperatura ambiente del datacenter     [C]

Con trafico constante la EDO es lineal y tiene solucion cerrada:

    T_eq  = T_amb + (P_idle + k * trafico) / h
    tau   = C / h
    T(t)  = T_eq + (T0 - T_eq) * exp(-t / tau)

Esa solucion cerrada es la que valida al integrador RK4 en los tests.

La calibracion del enunciado (P_idle=360, k=180, h=20, T_amb=25) deja el
equilibrio con trafico medio de 3 Gbps en 70.0 C exactos, que es la temperatura
de diseno. Con 1 Gbps baja a 52 C y con 5 Gbps sube a 88 C.
"""

import math
from dataclasses import dataclass

from src.utils.config import (
    C_TERMICA,
    EFICIENCIA_BASE,
    EFICIENCIA_MINIMA,
    H_DISIP,
    K_CARGA_W,
    P_IDLE_W,
    PENALIZACION_POR_GRADO,
    T_AMB_C,
    TEMP_DISENO_C,
)
from src.utils.validators import ValidacionError


def eficiencia_termica(
    temperatura_c: float,
    temp_diseno: float = TEMP_DISENO_C,
    eficiencia_base: float = EFICIENCIA_BASE,
    penalizacion_por_grado: float = PENALIZACION_POR_GRADO,
    eficiencia_minima: float = EFICIENCIA_MINIMA,
) -> float:
    """
    Eficiencia del cluster con thermal throttling.

        eta(T) = 0.90                                si T <= 70
        eta(T) = max(0.30, 0.90 - 0.02 * (T - 70))   si T > 70

    Es continua en T = 70, no creciente en todo el dominio, y esta acotada al
    intervalo [0.30, 0.90].
    """
    if temperatura_c <= temp_diseno:
        return eficiencia_base
    caida = penalizacion_por_grado * (temperatura_c - temp_diseno)
    return max(eficiencia_minima, eficiencia_base - caida)


def hay_throttling(temperatura_c: float, temp_diseno: float = TEMP_DISENO_C) -> bool:
    """True si la temperatura supera la de diseno y el cluster esta limitado."""
    return temperatura_c > temp_diseno


def throughput_gbps(trafico_gbps: float, temperatura_c: float) -> float:
    """Rendimiento efectivamente entregado: trafico admitido por la eficiencia."""
    return trafico_gbps * eficiencia_termica(temperatura_c)


def gb_a_tb(gigabits: float) -> float:
    """Convierte Gigabits a Terabytes: Gb / 8 -> GB, GB / 1000 -> TB."""
    return gigabits / 8.0 / 1000.0


@dataclass
class ModeloTermico:
    """
    Balance termico del cluster, con integrador Runge-Kutta de cuarto orden.

    Las unidades de tiempo son SEGUNDOS, coherentes con C en J/C y h en W/C.
    """

    t_amb_c: float = T_AMB_C
    h_disip: float = H_DISIP
    p_idle_w: float = P_IDLE_W
    k_carga_w: float = K_CARGA_W
    c_termica: float = C_TERMICA

    def __post_init__(self) -> None:
        if self.h_disip <= 0:
            raise ValidacionError(
                f"El coeficiente de disipacion h debe ser positivo. Recibido: {self.h_disip}."
            )
        if self.c_termica <= 0:
            raise ValidacionError(
                f"La capacidad termica C debe ser positiva. Recibido: {self.c_termica}."
            )

    @property
    def tau_s(self) -> float:
        """Constante de tiempo del sistema de primer orden: tau = C / h."""
        return self.c_termica / self.h_disip

    def potencia_disipada_w(self, trafico_gbps: float) -> float:
        """Potencia total generada: reposo mas la parte proporcional al trafico."""
        return self.p_idle_w + self.k_carga_w * trafico_gbps

    def derivada(self, temperatura_c: float, trafico_gbps: float) -> float:
        """
        dT/dt en C/s.

            dT/dt = (P_idle + k * trafico - h * (T - T_amb)) / C
        """
        generado = self.potencia_disipada_w(trafico_gbps)
        evacuado = self.h_disip * (temperatura_c - self.t_amb_c)
        return (generado - evacuado) / self.c_termica

    def temperatura_equilibrio(self, trafico_gbps: float) -> float:
        """
        Temperatura de regimen permanente con trafico constante:

            T_eq = T_amb + (P_idle + k * trafico) / h
        """
        return self.t_amb_c + self.potencia_disipada_w(trafico_gbps) / self.h_disip

    def solucion_analitica(
        self, temp_inicial_c: float, trafico_gbps: float, tiempo_s: float
    ) -> float:
        """
        Solucion cerrada de la EDO lineal con forzante constante:

            T(t) = T_eq + (T0 - T_eq) * exp(-t / tau)

        Se usa para validar el integrador numerico, no dentro de la simulacion.
        """
        if tiempo_s < 0:
            raise ValidacionError(f"El tiempo no puede ser negativo: {tiempo_s}.")
        t_eq = self.temperatura_equilibrio(trafico_gbps)
        return t_eq + (temp_inicial_c - t_eq) * math.exp(-tiempo_s / self.tau_s)

    def paso_rk4(self, temperatura_c: float, trafico_gbps: float, dt_s: float) -> float:
        """
        Un paso de Runge-Kutta de cuarto orden.

        El trafico se mantiene constante durante todo el paso (retencion de orden
        cero), lo que es consistente con el re-sorteo cada 60 s del motor: la
        demanda es un escalon por minuto, no ruido por segundo.
        """
        if dt_s <= 0:
            raise ValidacionError(f"El paso de integracion debe ser positivo: {dt_s}.")

        k1 = self.derivada(temperatura_c, trafico_gbps)
        k2 = self.derivada(temperatura_c + 0.5 * dt_s * k1, trafico_gbps)
        k3 = self.derivada(temperatura_c + 0.5 * dt_s * k2, trafico_gbps)
        k4 = self.derivada(temperatura_c + dt_s * k3, trafico_gbps)
        return temperatura_c + (dt_s / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

    def integrar(
        self, temp_inicial_c: float, trafico_gbps: float, duracion_s: float, dt_s: float = 1.0
    ) -> float:
        """Integra la EDO con RK4 durante duracion_s con trafico constante."""
        if duracion_s < 0:
            raise ValidacionError(f"La duracion no puede ser negativa: {duracion_s}.")
        temp = float(temp_inicial_c)
        pasos = int(round(duracion_s / dt_s))
        for _ in range(pasos):
            temp = self.paso_rk4(temp, trafico_gbps, dt_s)
        return temp


def _selfcheck() -> None:
    """Verifica equilibrios, throttling y exactitud del RK4."""
    modelo = ModeloTermico()

    # Equilibrios del enunciado
    assert abs(modelo.temperatura_equilibrio(3.0) - 70.0) < 1e-9
    assert abs(modelo.temperatura_equilibrio(1.0) - 52.0) < 1e-9
    assert abs(modelo.temperatura_equilibrio(5.0) - 88.0) < 1e-9
    assert abs(modelo.tau_s - 120.0) < 1e-9

    # En el equilibrio la derivada se anula
    assert abs(modelo.derivada(70.0, 3.0)) < 1e-12

    # RK4 contra la solucion cerrada: error por debajo de 1e-9 C
    for trafico in (1.0, 3.0, 5.0):
        for t0 in (25.0, 70.0, 95.0):
            for horizonte in (60.0, 300.0, 1800.0):
                num = modelo.integrar(t0, trafico, horizonte, dt_s=1.0)
                exacta = modelo.solucion_analitica(t0, trafico, horizonte)
                assert abs(num - exacta) < 1e-9, (trafico, t0, horizonte, num, exacta)

    # Convergencia al equilibrio con trafico constante 3 Gbps
    assert abs(modelo.integrar(25.0, 3.0, 3600.0) - 70.0) < 1e-6

    # Eficiencia: meseta, caida lineal y piso
    assert eficiencia_termica(25.0) == 0.90
    assert eficiencia_termica(70.0) == 0.90
    assert abs(eficiencia_termica(80.0) - 0.70) < 1e-12
    assert abs(eficiencia_termica(88.0) - 0.54) < 1e-12
    assert eficiencia_termica(200.0) == 0.30
    anterior = 1.0
    for grados in range(0, 200):
        actual = eficiencia_termica(float(grados))
        assert actual <= anterior + 1e-12, f"eta crecio en T={grados}"
        assert 0.30 <= actual <= 0.90
        anterior = actual

    assert not hay_throttling(70.0)
    assert hay_throttling(70.1)
    assert abs(throughput_gbps(5.0, 88.0) - 2.7) < 1e-12
    assert abs(gb_a_tb(8000.0) - 1.0) < 1e-12

    print("selfcheck thermal_model: OK")


if __name__ == "__main__":
    _selfcheck()
