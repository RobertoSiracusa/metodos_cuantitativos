"""
PROBLEMA 2 - Motor de simulacion continua del cluster de servidores.

Integra el balance termico de primer orden con Runge-Kutta de cuarto orden y
paso de 1 segundo simulado, acoplado al modelo de rendimiento con thermal
throttling.

DECISION DE MODELADO - RETENCION DE ORDEN CERO DEL TRAFICO:
el trafico se re-sortea cada 60 s y se mantiene constante dentro de cada minuto.
Un sorteo por segundo convertiria la demanda en ruido blanco: el filtro pasabajos
que impone la inercia termica (tau = 120 s) promediaria todo y la temperatura
quedaria clavada en el equilibrio medio, borrando justamente la variabilidad que
el enunciado pide medir. Un escalon por minuto si representa una demanda real.

La traza CSV se muestrea una vez por minuto simulado, no una vez por paso: una
corrida de 8 h produce 480 filas analizables en lugar de 28.800 inservibles.

Igual que el motor discreto, el reloj corre en SEGUNDOS simulados.
"""

from collections import deque
from statistics import mean, pstdev
from typing import Deque, Dict, List, Optional

from src.core.thermal_model import ModeloTermico, eficiencia_termica, gb_a_tb, hay_throttling
from src.core.traffic_model import GeneradorTrafico
from src.services.tracer import TrazaSerie
from src.utils.config import (
    C_TERMICA,
    H_DISIP,
    HISTORIAL_MAX_PUNTOS,
    INTERVALO_RESORTEO_S,
    INTERVALO_TRAZA_P2_S,
    K_CARGA_W,
    EFICIENCIA_BASE,
    P_IDLE_W,
    PASO_INTEGRACION_S,
    SEMILLA_DEFECTO,
    T_AMB_C,
    TEMP_DISENO_C,
    TEMP_INICIAL_C,
    TRAFICO_DESV_GBPS,
    TRAFICO_MAX_GBPS,
    TRAFICO_MEDIA_GBPS,
    TRAFICO_MIN_GBPS,
)
from src.utils.validators import ValidacionError

CABECERA_TRAZA_P2 = [
    "t_horas",
    "trafico_gbps",
    "temp_c",
    "eficiencia",
    "throughput_gbps",
    "tb_acumulados",
]


class ClusterSimulation:
    """
    Simulacion continua del comportamiento termico y de rendimiento del cluster.

    Contrato publico que consume la capa grafica:
      - step(target_time)      avanza la integracion hasta ese instante
      - tiempo_actual          tiempo simulado actual, en segundos
      - obtener_metricas()     metricas consolidadas en cualquier momento
      - temperatura_actual, trafico_actual, eficiencia_actual, throughput_actual
      - tb_acumulados
      - historial_temp         ventana acotada para dibujar el oscilograma
    """

    def __init__(
        self,
        temp_inicial_c: float = TEMP_INICIAL_C,
        t_amb_c: float = T_AMB_C,
        h_disip: float = H_DISIP,
        p_idle_w: float = P_IDLE_W,
        k_carga_w: float = K_CARGA_W,
        c_termica: float = C_TERMICA,
        trafico_media: float = TRAFICO_MEDIA_GBPS,
        trafico_desv: float = TRAFICO_DESV_GBPS,
        trafico_min: float = TRAFICO_MIN_GBPS,
        trafico_max: float = TRAFICO_MAX_GBPS,
        paso_s: float = PASO_INTEGRACION_S,
        intervalo_resorteo_s: float = INTERVALO_RESORTEO_S,
        intervalo_traza_s: float = INTERVALO_TRAZA_P2_S,
        semilla: Optional[int] = SEMILLA_DEFECTO,
        tracer: Optional[TrazaSerie] = None,
    ) -> None:
        if paso_s <= 0:
            raise ValidacionError(f"El paso de integracion debe ser positivo: {paso_s}.")
        if intervalo_resorteo_s < paso_s:
            raise ValidacionError(
                f"El intervalo de resorteo ({intervalo_resorteo_s} s) no puede ser menor "
                f"que el paso de integracion ({paso_s} s)."
            )

        self.modelo = ModeloTermico(
            t_amb_c=t_amb_c,
            h_disip=h_disip,
            p_idle_w=p_idle_w,
            k_carga_w=k_carga_w,
            c_termica=c_termica,
        )
        self.generador = GeneradorTrafico(
            media=trafico_media,
            desviacion=trafico_desv,
            minimo=trafico_min,
            maximo=trafico_max,
            semilla=semilla,
        )

        self.paso_s = float(paso_s)
        self.intervalo_resorteo_s = float(intervalo_resorteo_s)
        self.intervalo_traza_s = float(intervalo_traza_s)
        self.semilla = semilla
        self.temp_inicial_c = float(temp_inicial_c)

        self.tracer = tracer if tracer is not None else TrazaSerie(CABECERA_TRAZA_P2)

        # --- Estado observable por la capa grafica ---
        self._t: float = 0.0
        self.temperatura_actual: float = float(temp_inicial_c)
        self.trafico_actual: float = self.generador.muestrear()
        self.eficiencia_actual: float = eficiencia_termica(self.temperatura_actual)
        self.throughput_actual: float = self.trafico_actual * self.eficiencia_actual
        self.historial_temp: Deque[float] = deque(maxlen=HISTORIAL_MAX_PUNTOS)
        self.historial_temp.append(self.temperatura_actual)

        # --- Acumuladores integrales ---
        self._gb_acumulados: float = 0.0
        self._suma_eta_dt: float = 0.0
        self._suma_trafico_dt: float = 0.0
        self._suma_throughput_dt: float = 0.0
        self._segundos_throttling: float = 0.0

        # --- Muestras de temperatura para media, desviacion, minimo y maximo ---
        self._muestras_temp: List[float] = [self.temperatura_actual]

        # --- Relojes auxiliares ---
        self._seg_desde_resorteo: float = 0.0
        self._seg_desde_traza: float = 0.0

    # ------------------------------------------------------------------
    # Contrato consumido por la capa grafica
    # ------------------------------------------------------------------

    @property
    def tiempo_actual(self) -> float:
        """Tiempo simulado actual, en segundos."""
        return self._t

    @property
    def tiempo_actual_horas(self) -> float:
        """Tiempo simulado actual, en horas."""
        return self._t / 3600.0

    @property
    def tb_acumulados(self) -> float:
        """Datos totales procesados hasta el momento, en Terabytes."""
        return gb_a_tb(self._gb_acumulados)

    @property
    def gb_acumulados(self) -> float:
        """Datos totales procesados hasta el momento, en Gigabits."""
        return self._gb_acumulados

    @property
    def throttling_activo(self) -> bool:
        """True si en este instante la temperatura supera la de diseno."""
        return hay_throttling(self.temperatura_actual)

    @property
    def temperatura_equilibrio_actual(self) -> float:
        """Temperatura hacia la que tiende el sistema con el trafico vigente."""
        return self.modelo.temperatura_equilibrio(self.trafico_actual)

    def step(self, target_time: float) -> None:
        """
        Avanza la integracion hasta target_time (segundos simulados).

        Da pasos completos de paso_s mientras quepan; el motor nunca retrocede ni
        da pasos parciales, para que la serie temporal quede en una grilla regular.
        """
        if target_time <= self._t:
            return
        # Tolerancia contra el error de acumulacion en punto flotante del reloj.
        tolerancia = self.paso_s * 1e-9
        while self._t + self.paso_s <= target_time + tolerancia:
            self._avanzar_un_paso()

    def ejecutar(self, duracion_horas: float) -> Dict:
        """Corre la simulacion completa por N horas y devuelve las metricas."""
        self.step(duracion_horas * 3600.0)
        return self.obtener_metricas()

    # ------------------------------------------------------------------
    # Nucleo de la integracion
    # ------------------------------------------------------------------

    def _avanzar_un_paso(self) -> None:
        """Un paso de RK4 de paso_s segundos, con sus acumuladores y su traza."""
        dt = self.paso_s
        trafico = self.trafico_actual          # retencion de orden cero en el intervalo
        temp_ini = self.temperatura_actual
        temp_fin = self.modelo.paso_rk4(temp_ini, trafico, dt)

        # Estado representativo del intervalo: temperatura media del paso. Con
        # dt = 1 s y tau = 120 s la diferencia contra los extremos es marginal,
        # pero la regla del punto medio hace insesgados los acumuladores.
        temp_media = 0.5 * (temp_ini + temp_fin)
        eta = eficiencia_termica(temp_media)
        throughput = trafico * eta

        self._gb_acumulados += throughput * dt      # Gbps * s = Gb
        self._suma_eta_dt += eta * dt
        self._suma_trafico_dt += trafico * dt
        self._suma_throughput_dt += throughput * dt
        if hay_throttling(temp_media):
            self._segundos_throttling += dt

        # Avanzar el estado publico
        self.temperatura_actual = temp_fin
        self._t += dt
        self._muestras_temp.append(temp_fin)
        self.historial_temp.append(temp_fin)
        self.eficiencia_actual = eficiencia_termica(temp_fin)
        self.throughput_actual = trafico * self.eficiencia_actual

        # Re-sorteo del trafico con retencion de orden cero
        self._seg_desde_resorteo += dt
        if self._seg_desde_resorteo >= self.intervalo_resorteo_s - 1e-9:
            self._seg_desde_resorteo = 0.0
            self.trafico_actual = self.generador.muestrear()
            self.throughput_actual = self.trafico_actual * self.eficiencia_actual

        # Muestreo de la traza CSV
        self._seg_desde_traza += dt
        if self._seg_desde_traza >= self.intervalo_traza_s - 1e-9:
            self._seg_desde_traza = 0.0
            self._registrar_traza()

    def _registrar_traza(self) -> None:
        """Anota una fila de la serie temporal en la traza CSV."""
        self.tracer.registrar(
            [
                self._t / 3600.0,
                self.trafico_actual,
                self.temperatura_actual,
                self.eficiencia_actual,
                self.throughput_actual,
                self.tb_acumulados,
            ]
        )

    # ------------------------------------------------------------------
    # Metricas
    # ------------------------------------------------------------------

    def obtener_metricas(self) -> Dict:
        """
        Metricas consolidadas. Se puede llamar en cualquier momento de la corrida,
        no solamente al final.
        """
        total_s = self._t
        muestras = self._muestras_temp

        temp_media = mean(muestras) if muestras else self.temperatura_actual
        temp_desv = pstdev(muestras) if len(muestras) > 1 else 0.0
        temp_min = min(muestras) if muestras else self.temperatura_actual
        temp_max = max(muestras) if muestras else self.temperatura_actual

        if total_s > 0:
            eta_global = self._suma_eta_dt / total_s
            trafico_medio = self._suma_trafico_dt / total_s
            throughput_medio = self._suma_throughput_dt / total_s
            pct_throttling = self._segundos_throttling / total_s * 100.0
        else:
            eta_global = self.eficiencia_actual
            trafico_medio = self.trafico_actual
            throughput_medio = self.throughput_actual
            pct_throttling = 0.0

        # Dos perdidas distintas que NO hay que confundir:
        #
        # (a) Perdida TOTAL contra el trafico ofrecido. Incluye los 10 puntos de
        #     ineficiencia base que el sistema tiene aunque este frio, porque
        #     eta vale 0.90 incluso a 70 C o menos. No es culpa del throttling.
        #
        # (b) Perdida atribuible AL THROTTLING: cuanto cae eta respecto de su
        #     valor nominal de 0.90. Es la unica que el enfriamiento puede
        #     recuperar. Confundirlas infla la cifra por un factor de ~4.
        perdida_total_pct = 0.0
        if trafico_medio > 0:
            perdida_total_pct = (1.0 - throughput_medio / trafico_medio) * 100.0

        perdida_throttling_pct = 0.0
        if EFICIENCIA_BASE > 0:
            perdida_throttling_pct = (
                (EFICIENCIA_BASE - eta_global) / EFICIENCIA_BASE * 100.0
            )

        return {
            "problema": 2,
            "titulo": "Cluster de servidores - simulacion continua",
            # Parametros de entrada
            "tiempo_simulado_s": total_s,
            "tiempo_simulado_horas": total_s / 3600.0,
            "semilla": self.semilla,
            "paso_integracion_s": self.paso_s,
            "intervalo_resorteo_s": self.intervalo_resorteo_s,
            "temp_inicial_c": self.temp_inicial_c,
            "temp_ambiente_c": self.modelo.t_amb_c,
            "temp_diseno_c": TEMP_DISENO_C,
            "h_disip": self.modelo.h_disip,
            "p_idle_w": self.modelo.p_idle_w,
            "k_carga_w": self.modelo.k_carga_w,
            "c_termica": self.modelo.c_termica,
            "tau_s": self.modelo.tau_s,
            "trafico_media_nominal": self.generador.media,
            "trafico_desv_nominal": self.generador.desviacion,
            "trafico_min_gbps": self.generador.minimo,
            "trafico_max_gbps": self.generador.maximo,
            # Datos procesados
            "gb_procesados": self._gb_acumulados,
            "gb_procesados_bytes": self._gb_acumulados / 8.0,
            "tb_procesados": self.tb_acumulados,
            # Variabilidad de la temperatura
            "temp_media_c": temp_media,
            "temp_desviacion_c": temp_desv,
            "temp_min_c": temp_min,
            "temp_max_c": temp_max,
            "temp_actual_c": self.temperatura_actual,
            "temp_equilibrio_media_c": self.modelo.temperatura_equilibrio(self.generador.media),
            # Eficiencia y rendimiento
            "eficiencia_global": eta_global,
            "eficiencia_global_pct": eta_global * 100.0,
            "trafico_medio_gbps": trafico_medio,
            "throughput_medio_gbps": throughput_medio,
            "perdida_total_pct": perdida_total_pct,
            "perdida_por_throttling_pct": perdida_throttling_pct,
            "pct_tiempo_throttling": pct_throttling,
            "segundos_throttling": self._segundos_throttling,
            "muestras_temperatura": len(muestras),
            "filas_traza": len(self.tracer),
            "tasa_rechazo_trafico": self.generador.tasa_rechazo,
        }


def _selfcheck() -> None:
    """Corrida corta reproducible con asserts de coherencia fisica."""
    sim = ClusterSimulation(semilla=SEMILLA_DEFECTO)
    metricas = sim.ejecutar(duracion_horas=8.0)

    assert abs(metricas["tiempo_simulado_horas"] - 8.0) < 1e-9
    assert metricas["filas_traza"] == 480, metricas["filas_traza"]
    assert metricas["muestras_temperatura"] == 28801, metricas["muestras_temperatura"]

    # La temperatura media debe rondar el equilibrio nominal de 70 C
    assert 66.0 < metricas["temp_media_c"] < 74.0, metricas["temp_media_c"]
    # Y quedar acotada por los equilibrios extremos con trafico 1 y 5 Gbps
    assert metricas["temp_min_c"] >= 52.0 - 1e-6, metricas["temp_min_c"]
    assert metricas["temp_max_c"] <= 88.0 + 1e-6, metricas["temp_max_c"]

    # El throttling debe activarse parte del tiempo, no siempre ni nunca
    assert 0.0 < metricas["pct_tiempo_throttling"] < 100.0, metricas["pct_tiempo_throttling"]
    assert 0.30 <= metricas["eficiencia_global"] <= 0.90
    assert metricas["tb_procesados"] > 0.0

    # Coherencia: throughput medio = trafico medio por eficiencia, aproximadamente
    assert metricas["throughput_medio_gbps"] <= metricas["trafico_medio_gbps"] + 1e-9

    # Reproducibilidad
    otra = ClusterSimulation(semilla=SEMILLA_DEFECTO).ejecutar(8.0)
    assert abs(otra["tb_procesados"] - metricas["tb_procesados"]) < 1e-12

    print(
        "selfcheck continuous_sim: OK "
        f"(T media={metricas['temp_media_c']:.2f} C, "
        f"throttling={metricas['pct_tiempo_throttling']:.2f}%, "
        f"TB={metricas['tb_procesados']:.4f})"
    )


if __name__ == "__main__":
    _selfcheck()
