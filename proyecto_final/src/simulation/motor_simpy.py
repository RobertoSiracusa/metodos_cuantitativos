"""Motor de simulacion SimPy que integra el modulo 1 (DP) y el modulo 2 (no lineal) (R6)."""

from __future__ import annotations

import random
from collections import Counter, deque
from dataclasses import dataclass
from typing import Callable

import simpy

from src.core.network_entities import Paquete, Servidor
from src.core.no_lineal.base import EntradaOptimizacion, Optimizador
from src.core.programacion_dinamica.mochila import Mochila
from src.core.programacion_dinamica.ruta_mas_corta import RutaMasCorta
from src.simulation.metricas import MetricasColas
from src.utils.config import Configuracion
from src.utils.validators import ErrorValidacion, Validador

PARAMETROS_SIMULACION = {
    "duracion": 300.0,
    "tasa_llegada": 4.0,  # paquetes por unidad de tiempo (Poisson)
    "ventana_despacho": 1.0,  # cada cuanto cada servidor corre la mochila sobre su cola
    "paso_control": 1.0,  # cada cuanto corren el gradiente y Lagrange
    "mtbf": 200.0,  # tiempo medio entre fallas de un nodo
    "mttr": 15.0,  # tiempo medio de reparacion
    "escala_latencia": 0.2,  # convierte el costo de un enlace en tiempo de transito
    "requerimiento_max": 8,  # requerimiento de cada paquete ~ U{1..requerimiento_max}
}


@dataclass(frozen=True)
class Evento:
    """Algo notable que paso en la simulacion: cambio de ruta, falla, reparacion, emergencia."""

    tiempo: float
    tipo: str
    mensaje: str


@dataclass(frozen=True)
class EstadoSimulacion:
    """Foto del sistema en un instante. La GUI y el PDF solo leen esto; nunca tocan el motor.

    Todos los contenedores son copias armadas en `MotorSimulacion.estado()`, asi que
    modificarlos no altera la simulacion.
    """

    tiempo: float
    posiciones: dict[str, tuple[float, float]]
    capas: dict[str, str]
    clusteres: dict[str, tuple[str, ...]]  # cluster -> ids de servidores
    tor_de_cluster: dict[str, str]
    operativos: dict[str, bool]
    ocupacion_enlaces: dict[tuple[str, str], float]
    rutas: dict[str, tuple[str, ...]]  # cluster -> ruta optima actual (vacia si no hay)
    en_transito: tuple[tuple[str, str, str, float], ...]  # (paquete, origen, destino, progreso 0-1)
    colas: dict[str, int]
    carga_servidores: dict[str, float]  # % de capacidad ocupada
    carga: float
    temperatura: float
    punto_critico: float | None
    curva_termica: tuple[tuple[float, float], ...]  # (carga, T(carga)) de 0 a 100 %
    puntos_estacionarios: tuple[tuple[float, float, str], ...]  # (carga, T, tipo)
    punto_inflexion: float | None
    emergencia: bool
    velocidad: float
    lambda_: float
    energia_clusteres: dict[str, float]
    ultimas_mochilas: dict[str, dict]  # servidor -> ultima decision de la mochila (R2)
    eventos: tuple[Evento, ...]  # los ultimos 200
    conteo_eventos: dict[str, int]  # total por tipo desde el inicio
    metricas: dict[str, float]
    series_gradiente: dict[str, list[float]]
    series_lagrange: dict[str, list[float]]
    series_termico: dict[str, list[float]]


class MotorSimulacion:
    """Procesos SimPy: llegadas Poisson, transito por la ruta optima, despacho con mochila,
    servicio exponencial, fallas/reparaciones de nodos y un lazo de control no lineal.

    Integracion de modulos:
      - M1: cada paquete pide a RutaMasCorta la ruta GW -> ToR de su cluster con los
        costos de congestion del momento; cada servidor elige que tareas atender con Mochila.
      - M2: en cada tick de control, ModeloTermico da la temperatura para la carga actual y
        cada Optimizador (gradiente, Lagrange) da un paso (polimorfismo).
    Patron Observer: `suscribir(fn)` recibe cada Evento (cambio de ruta, falla, emergencia).
    """

    def __init__(self, configuracion: Configuracion, semilla: int | None = None) -> None:
        self._p = dict(PARAMETROS_SIMULACION)
        for clave, valor in configuracion.parametros("simulacion").items():
            if clave not in self._p:
                raise ErrorValidacion(f"parametros.simulacion.{clave} no es un parametro conocido")
            self._p[clave] = valor
        for clave in ("duracion", "tasa_llegada", "ventana_despacho", "paso_control", "mtbf", "mttr", "escala_latencia"):
            Validador.validar_rango(f"parametros.simulacion.{clave}", self._p[clave], minimo=1e-9)
        Validador.validar_rango("parametros.simulacion.requerimiento_max", self._p["requerimiento_max"], minimo=1, entero=True)

        self._rng = random.Random(semilla)
        self._env = simpy.Environment()
        self._red = configuracion.construir_red()
        self._modelo_ruta = RutaMasCorta(self._red)
        self._termico = configuracion.construir_modelo_termico()
        self._gradiente = configuracion.construir_gradiente()
        self._lagrange = configuracion.construir_lagrange()
        self._optimizadores: list[Optimizador] = [self._gradiente, self._lagrange]
        self._punto_critico = self._termico.punto_critico()
        self._curva_termica = tuple((float(c), self._termico.temperatura(c)) for c in range(0, 101))
        self._puntos_estacionarios = tuple((p.carga, p.temperatura, p.tipo) for p in self._termico.puntos_estacionarios())
        self._metricas = MetricasColas()

        self._gateway = next(r.id for r in self._red.routers if r.capa == "gateway")
        self._servidores: list[Servidor] = [s for c in self._red.clusteres for s in c.servidores]
        self._observadores: list[Callable[[Evento], None]] = []
        self._eventos: deque[Evento] = deque(maxlen=200)
        self._conteo_eventos: Counter[str] = Counter()
        self._rutas: dict[str, tuple[str, ...]] = {}
        self._en_transito: dict[str, tuple[str, str, float, float]] = {}
        self._carga = 0.0
        self._emergencia = False
        self._serie_termico: dict[str, list[float]] = {"tiempo": [], "carga": [], "temperatura": []}
        self._contador = 0
        self._ultimas_mochilas: dict[str, dict] = {}

        for cluster in self._red.clusteres:
            self._rutas[cluster.id] = self._calcular_ruta(cluster.id)
        self._env.process(self._llegadas())
        self._env.process(self._control())
        for servidor in self._servidores:
            self._env.process(self._despachador(servidor))
        for nodo in [*self._red.routers, *self._servidores]:
            if nodo.id != self._gateway:
                self._env.process(self._fallas(nodo))

    # ------------------------------------------------------------------ API publica

    @property
    def tiempo(self) -> float:
        return self._env.now

    @property
    def duracion(self) -> float:
        return float(self._p["duracion"])

    @property
    def parametros(self) -> dict:
        return dict(self._p)

    def suscribir(self, observador: Callable[[Evento], None]) -> None:
        """Registra una funcion que se llama con cada Evento nuevo (patron Observer)."""
        self._observadores.append(observador)

    def avanzar(self, hasta: float) -> None:
        """Corre la simulacion hasta el instante `hasta` (no hace nada si ya paso)."""
        if hasta > self._env.now:
            self._env.run(until=hasta)

    def comparacion_mm1(self) -> dict[str, float]:
        """M/M/1 de referencia (aproximada) para un servidor promedio.

        lambda_s = lambda / #servidores. Como un servidor atiende en paralelo unas
        capacidad / E[req] tareas, cada una con tasa tasa_servicio / E[req], se toma
        mu_s = (capacidad / E[req]) * (tasa_servicio / E[req]) como su tasa de salida a plena carga.
        """
        n = len(self._servidores)
        req_medio = (1 + self._p["requerimiento_max"]) / 2
        mu = sum((s.capacidad / req_medio) * (s.tasa_servicio / req_medio) for s in self._servidores) / n
        return MetricasColas.comparar_mm1(self._p["tasa_llegada"] / n, mu)

    def estado(self) -> EstadoSimulacion:
        ahora = self._env.now
        en_transito = tuple(
            (pid, a, b, min(max((ahora - t0) / dur, 0.0), 1.0) if dur > 0 else 1.0)
            for pid, (a, b, t0, dur) in self._en_transito.items()
        )
        nodos = [*self._red.routers, *self._servidores]
        return EstadoSimulacion(
            tiempo=ahora,
            posiciones={n.id: n.posicion for n in nodos},
            capas={**{r.id: r.capa for r in self._red.routers}, **{s.id: "servidor" for s in self._servidores}},
            clusteres={c.id: tuple(s.id for s in c.servidores) for c in self._red.clusteres},
            tor_de_cluster={c.id: c.tor_id for c in self._red.clusteres},
            operativos={n.id: n.esta_operativo for n in nodos},
            ocupacion_enlaces={(e.origen_id, e.destino_id): e.ocupacion for e in self._red.enlaces},
            rutas=dict(self._rutas),
            en_transito=en_transito,
            colas={s.id: len(s.cola) for s in self._servidores},
            carga_servidores={s.id: 100 * s.carga_actual / s.capacidad for s in self._servidores},
            carga=self._carga,
            temperatura=self._termico.temperatura(self._carga),
            punto_critico=self._punto_critico,
            curva_termica=self._curva_termica,
            puntos_estacionarios=self._puntos_estacionarios,
            punto_inflexion=self._termico.punto_inflexion(),
            emergencia=self._emergencia,
            velocidad=self._gradiente.velocidad_actual,
            lambda_=self._lagrange.lambda_actual,
            energia_clusteres={c.id: c.energia_asignada for c in self._red.clusteres},
            ultimas_mochilas={k: dict(v) for k, v in self._ultimas_mochilas.items()},
            eventos=tuple(self._eventos),
            conteo_eventos=dict(self._conteo_eventos),
            metricas=self._metricas.resumen(),
            series_gradiente=self._gradiente.series_para_grafico(),
            series_lagrange=self._lagrange.series_para_grafico(),
            series_termico={k: list(v) for k, v in self._serie_termico.items()},
        )

    # ------------------------------------------------------------------ procesos SimPy

    def _llegadas(self):
        """Llegadas Poisson al gateway: tiempo entre arribos ~ Exponencial(tasa_llegada)."""
        clusteres = [c.id for c in self._red.clusteres]
        while True:
            yield self._env.timeout(self._rng.expovariate(self._p["tasa_llegada"]))
            self._contador += 1
            paquete = Paquete(
                id=f"P{self._contador}",
                requerimiento=self._rng.randint(1, int(self._p["requerimiento_max"])),
                prioridad=self._rng.randint(1, 10),
                destino_cluster=self._rng.choice(clusteres),
                t_creacion=self._env.now,
            )
            self._metricas.generado()
            self._env.process(self._viajar(paquete))

    def _viajar(self, paquete: Paquete):
        """Recorre la ruta optima del momento salto por salto y se encola en un servidor."""
        ruta = self._actualizar_ruta(paquete.destino_cluster)
        if not ruta:
            self._metricas.perdido("sin_ruta")
            return

        for origen, destino in zip(ruta, ruta[1:]):
            enlace = self._red.enlace(origen, destino)
            duracion = self._p["escala_latencia"] * (
                enlace.costo_actual() + self._red.nodo(origen).tiempo_servicio(paquete)
            )
            enlace.entrar(paquete)
            self._en_transito[paquete.id] = (origen, destino, self._env.now, duracion)
            yield self._env.timeout(duracion)
            enlace.salir(paquete)
            del self._en_transito[paquete.id]

        candidatos = [s for s in self._red.cluster(paquete.destino_cluster).servidores if s.esta_operativo]
        if not candidatos:
            self._metricas.perdido("sin_servidor")
            return
        servidor = min(candidatos, key=lambda s: (sum(p.requerimiento for p in s.cola) + s.carga_actual))
        servidor.encolar(paquete)
        self._metricas.llegada(paquete.id, self._env.now)

    def _despachador(self, servidor: Servidor):
        """Ventana de despacho: la mochila elige que tareas de la cola entran en la capacidad libre (R2)."""
        while True:
            yield self._env.timeout(self._p["ventana_despacho"])
            if not servidor.esta_operativo or not servidor.cola or servidor.capacidad_libre == 0:
                continue
            capacidad_libre = servidor.capacidad_libre
            en_cola = len(servidor.cola)
            resultado = Mochila(capacidad_libre).resolver(servidor.cola)
            self._ultimas_mochilas[servidor.id] = {
                "tiempo": self._env.now,
                "capacidad_libre": capacidad_libre,
                "en_cola": en_cola,
                "seleccionados": [p.id for p in resultado.seleccionados],
                "valor": resultado.valor_total,
                "peso": resultado.peso_total,
            }
            if not resultado.seleccionados:
                continue
            servidor.asignar(list(resultado.seleccionados))
            for paquete in resultado.seleccionados:
                self._metricas.inicio_servicio(paquete.id, self._env.now)
                self._env.process(self._servir(servidor, paquete))

    def _servir(self, servidor: Servidor, paquete: Paquete):
        """Tiempo de servicio ~ Exponencial con media requerimiento / tasa_servicio."""
        yield self._env.timeout(self._rng.expovariate(1 / servidor.tiempo_servicio(paquete)))
        servidor.liberar(paquete.id)
        self._metricas.fin_servicio(paquete.id, self._env.now)

    def _fallas(self, nodo):
        """Ciclo falla/reparacion con tiempos exponenciales (MTBF / MTTR)."""
        while True:
            yield self._env.timeout(self._rng.expovariate(1 / self._p["mtbf"]))
            nodo.fallar()
            self._emitir("falla", f"cae el nodo {nodo.id}")
            yield self._env.timeout(self._rng.expovariate(1 / self._p["mttr"]))
            nodo.reparar()
            self._emitir("reparacion", f"se repara el nodo {nodo.id}")

    def _control(self):
        """Lazo de control: modelo termico + un paso de cada optimizador del modulo 2."""
        while True:
            yield self._env.timeout(self._p["paso_control"])
            ahora = self._env.now
            operativos = [s for s in self._servidores if s.esta_operativo]
            capacidad = sum(s.capacidad for s in operativos)
            self._carga = 100 * sum(s.carga_actual for s in operativos) / capacidad if capacidad else 0.0

            entrada = EntradaOptimizacion(ahora, self._carga, {c.id: c.demanda() for c in self._red.clusteres})
            for optimizador in self._optimizadores:
                optimizador.actualizar(entrada)
            for cluster in self._red.clusteres:
                cluster.energia_asignada = self._lagrange.historial[-1].valores[f"E_{cluster.id}"]

            temperatura = self._termico.temperatura(self._carga)
            self._serie_termico["tiempo"].append(ahora)
            self._serie_termico["carga"].append(self._carga)
            self._serie_termico["temperatura"].append(temperatura)

            en_emergencia = self._punto_critico is not None and self._carga >= self._punto_critico
            if en_emergencia and not self._emergencia:
                self._emitir("emergencia", f"carga {self._carga:.1f} % >= critico {self._punto_critico:.1f} % (T = {temperatura:.1f} C)")
            elif self._emergencia and not en_emergencia:
                self._emitir("normal", f"carga {self._carga:.1f} %: fin de la emergencia termica")
            self._emergencia = en_emergencia

            for cluster in self._red.clusteres:
                self._actualizar_ruta(cluster.id)
            self._metricas.muestrear(
                ahora,
                sum(len(s.cola) for s in self._servidores),
                self._carga / 100,
            )

    # ------------------------------------------------------------------ auxiliares

    def _calcular_ruta(self, cluster_id: str) -> tuple[str, ...]:
        resultado = self._modelo_ruta.resolver(self._gateway, self._red.cluster(cluster_id).tor_id)
        return resultado.camino if resultado.existe else ()

    def _actualizar_ruta(self, cluster_id: str) -> tuple[str, ...]:
        """Recalcula la ruta optima con los costos actuales; si cambio, emite un evento (R9)."""
        nueva = self._calcular_ruta(cluster_id)
        anterior = self._rutas.get(cluster_id)
        if nueva != anterior:
            self._rutas[cluster_id] = nueva
            destino = " -> ".join(nueva) if nueva else "sin ruta"
            self._emitir("cambio_ruta", f"{cluster_id}: {destino}")
        return nueva

    def _emitir(self, tipo: str, mensaje: str) -> None:
        evento = Evento(self._env.now, tipo, mensaje)
        self._eventos.append(evento)
        self._conteo_eventos[evento.tipo] += 1
        for observador in self._observadores:
            observador(evento)
