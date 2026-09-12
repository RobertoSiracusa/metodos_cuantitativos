"""
PROBLEMA 1 - Motor de simulacion por eventos discretos (SimPy).

Fabrica de laptops con una unica estacion de ensamblaje y un inventario de
procesadores de gama alta con politica de revision continua (s, Q).

  - Las ordenes llegan segun un proceso de Poisson de tasa lambda.
  - El ensamblaje es exponencial de media MEDIA_ENSAMBLAJE_MIN.
  - Con un solo servidor el sistema es una cola M/M/1.
  - Cuando el stock cae por debajo del umbral critico s se dispara un pedido de
    Q unidades que el proveedor entrega tras el lead time.
  - Si el stock llega a cero, la orden montada bloquea la estacion y la linea
    queda detenida hasta que entre el lote.

El reloj de SimPy corre en SEGUNDOS simulados, igual que el motor continuo del
Problema 2, para que la capa grafica pueda avanzar los dos con el mismo reloj.

NOTA SOBRE LOS PARAMETROS OFICIALES: con lambda=10 ordenes/h, lead time de 15 min
y umbral s=10, durante una reposicion se consumen unas 2.5 unidades, muy por
debajo del umbral. El stock por lo tanto NUNCA llega a cero y las paradas de
linea dan 0. Es el resultado correcto del modelo: el inventario esta
sobredimensionado y el cuello de botella real es la estacion (rho = 0.833).
El codigo implementa igual la parada de linea, que se ejercita en los tests con
parametros artificiales que si agotan el stock.
"""

import random
from typing import Dict, List, Optional

import simpy

from src.core.factory_entities import (
    EstacionEnsamblaje,
    EstadisticasFabrica,
    InventarioProcesadores,
    Orden,
)
from src.core.mm1_analytical import ModeloMM1
from src.services.tracer import TrazaEventos
from src.utils.config import (
    CONSUMO_POR_LAPTOP,
    INTERVALO_MUESTREO_P1_S,
    LAMBDA_ORDENES_HORA,
    LEAD_TIME_MIN,
    LOTE_PRODUCCION,
    LOTE_Q,
    MEDIA_ENSAMBLAJE_MIN,
    SEMILLA_DEFECTO,
    SERVIDORES,
    STOCK_INICIAL,
    UMBRAL_CRITICO_S,
)
from src.utils.validators import validar_entero_positivo, validar_tasa


class FabricaSimulation:
    """
    Orquestador de los procesos estocasticos concurrentes de la fabrica.

    Contrato publico que consume la capa grafica:
      - step(target_time)      avanza el reloj simulado hasta ese instante
      - tiempo_actual          tiempo simulado actual, en segundos
      - obtener_metricas()     metricas consolidadas en cualquier momento
      - ordenes_en_cola        lista de ordenes esperando estacion
      - estacion               .ocupada / .orden_actual
      - inventario             .nivel / .capacidad_lote / .en_reposicion
      - linea_detenida         True mientras falte stock
    """

    def __init__(
        self,
        lambda_ordenes_hora: float = LAMBDA_ORDENES_HORA,
        media_ensamblaje_min: float = MEDIA_ENSAMBLAJE_MIN,
        servidores: int = SERVIDORES,
        stock_inicial: int = STOCK_INICIAL,
        umbral_critico: int = UMBRAL_CRITICO_S,
        lote_q: int = LOTE_Q,
        lead_time_min: float = LEAD_TIME_MIN,
        consumo_por_laptop: int = CONSUMO_POR_LAPTOP,
        lote_produccion: int = LOTE_PRODUCCION,
        semilla: Optional[int] = SEMILLA_DEFECTO,
        tracer: Optional[TrazaEventos] = None,
    ) -> None:
        # --- Validacion de parametros al borde ---
        self.lambda_ordenes_hora = validar_tasa(lambda_ordenes_hora, "Tasa de llegada lambda")
        self.media_ensamblaje_min = validar_tasa(media_ensamblaje_min, "Media de ensamblaje")
        self.servidores = validar_entero_positivo(servidores, "Servidores")
        self.lead_time_min = validar_tasa(lead_time_min, "Lead time")
        self.lote_produccion = validar_entero_positivo(lote_produccion, "Lote de produccion")

        # Tasa de servicio derivada, en laptops por hora
        self.mu_hora = 60.0 / self.media_ensamblaje_min

        # Conversion a segundos, unidad interna del reloj
        self.lambda_por_segundo = self.lambda_ordenes_hora / 3600.0
        self.media_ensamblaje_s = self.media_ensamblaje_min * 60.0
        self.lead_time_s = self.lead_time_min * 60.0

        # --- Entorno SimPy y recursos ---
        self.env = simpy.Environment()
        self._recurso_estacion = simpy.Resource(self.env, capacity=self.servidores)
        self._rng = random.Random(semilla)
        self.semilla = semilla

        # --- Entidades del dominio ---
        self.estacion = EstacionEnsamblaje(id_estacion=1)
        self.inventario = InventarioProcesadores(
            nivel_inicial=stock_inicial,
            umbral_critico=umbral_critico,
            capacidad_lote=lote_q,
            consumo_por_laptop=consumo_por_laptop,
        )
        self.estadisticas = EstadisticasFabrica()
        # El inventario muta su nivel durante la corrida; el valor declarado se
        # guarda aparte para poder reportarlo tal cual se configuro.
        self.stock_inicial = self.inventario.nivel

        # --- Estado observable por la capa grafica ---
        self.ordenes_en_cola: List[Orden] = []
        self.ordenes_completadas: List[Orden] = []
        self.linea_detenida: bool = False

        # --- Traza de eventos ---
        self.tracer = tracer if tracer is not None else TrazaEventos(
            "Problema 1: fabrica de laptops (eventos discretos)"
        )

        # --- Estado interno ---
        self._siguiente_id: int = 1
        self._tiempo_servicio_s: float = 0.0
        self._laptops_desde_ultimo_lote: int = 0
        self._inicio_lote_produccion_s: float = 0.0
        # Evento que despierta a la orden bloqueada cuando entra un lote.
        self._evento_stock = self.env.event()

        self.tracer.registrar(
            0.0,
            "inicio_simulacion",
            f"lambda={self.lambda_ordenes_hora:.2f} ord/h | mu={self.mu_hora:.2f} laptops/h | "
            f"stock inicial={self.inventario.nivel} | s={self.inventario.umbral_critico} | "
            f"Q={self.inventario.capacidad_lote} | lead time={self.lead_time_min:.1f} min",
        )

        # --- Procesos concurrentes ---
        self.env.process(self._proceso_llegadas())
        self.env.process(self._proceso_muestreo())

    # ------------------------------------------------------------------
    # Contrato consumido por la capa grafica
    # ------------------------------------------------------------------

    @property
    def tiempo_actual(self) -> float:
        """Tiempo simulado actual, en segundos."""
        return float(self.env.now)

    @property
    def tiempo_actual_horas(self) -> float:
        """Tiempo simulado actual, en horas."""
        return self.tiempo_actual / 3600.0

    @property
    def modelo_analitico(self) -> ModeloMM1:
        """Modelo M/M/1 cerrado con los parametros vigentes, para contrastar."""
        return ModeloMM1(lamb=self.lambda_ordenes_hora, mu=self.mu_hora, servidores=self.servidores)

    def step(self, target_time: float) -> None:
        """
        Avanza el reloj de SimPy hasta target_time (segundos simulados).

        Si target_time ya paso, no hace nada: el motor nunca retrocede.
        """
        if target_time > self.env.now:
            self.env.run(until=target_time)

    def ejecutar(self, duracion_horas: float) -> Dict:
        """Corre la simulacion completa por N horas y devuelve las metricas."""
        objetivo_s = duracion_horas * 3600.0
        self.step(objetivo_s)
        self.tracer.registrar(
            self.tiempo_actual,
            "fin_simulacion",
            f"ordenes generadas={self.estadisticas.ordenes_generadas} | "
            f"laptops completadas={self.estadisticas.ordenes_completadas}",
        )
        return self.obtener_metricas()

    # ------------------------------------------------------------------
    # Procesos SimPy
    # ------------------------------------------------------------------

    def _proceso_llegadas(self):
        """Proceso de Poisson: intervalos entre llegadas exponenciales."""
        while True:
            intervalo = self._rng.expovariate(self.lambda_por_segundo)
            yield self.env.timeout(intervalo)

            orden = Orden(id_orden=self._siguiente_id, tiempo_llegada=self.env.now)
            self._siguiente_id += 1
            self.estadisticas.registrar_llegada()
            self.tracer.registrar(
                self.env.now,
                "llegada_orden",
                f"Orden #{orden.id_orden} | en cola: {len(self.ordenes_en_cola)} | "
                f"stock: {self.inventario.nivel}",
            )
            self.env.process(self._proceso_orden(orden))

    def _proceso_orden(self, orden: Orden):
        """Ciclo de vida de una orden: cola -> estacion -> (bloqueo) -> despacho."""
        self.ordenes_en_cola.append(orden)

        # Espera por la estacion de ensamblaje
        solicitud = self._recurso_estacion.request()
        yield solicitud

        self.ordenes_en_cola.remove(orden)
        orden.tiempo_inicio_ensamblaje = self.env.now
        self.estacion.montar(orden)
        self.tracer.registrar(
            self.env.now,
            "inicio_ensamblaje",
            f"Orden #{orden.id_orden} | espera en cola: "
            f"{(orden.espera_en_cola_s or 0.0) / 60.0:.2f} min",
        )

        # Bloqueo por falta de procesadores: la estacion queda tomada y la linea parada
        if not self.inventario.hay_stock:
            yield from self._esperar_stock(orden)

        # Consumo de procesadores y evaluacion del umbral critico
        self.inventario.consumir()
        self._disparar_reposicion_si_corresponde()

        # Ensamblaje: duracion exponencial de media MEDIA_ENSAMBLAJE_MIN
        duracion = self._rng.expovariate(1.0 / self.media_ensamblaje_s)
        yield self.env.timeout(duracion)
        self._tiempo_servicio_s += duracion

        # Despacho de la laptop
        orden.tiempo_fin_ensamblaje = self.env.now
        self.estacion.liberar(self.env.now - (orden.tiempo_inicio_ensamblaje or self.env.now))
        self._recurso_estacion.release(solicitud)

        self.estadisticas.registrar_completada(
            espera_cola_s=orden.espera_en_cola_s or 0.0,
            tiempo_sistema_s=orden.tiempo_en_sistema_s or 0.0,
        )
        self.ordenes_completadas.append(orden)
        self.tracer.registrar(
            self.env.now,
            "fin_ensamblaje",
            f"Orden #{orden.id_orden} | ensamblaje: {duracion / 60.0:.2f} min | "
            f"total en sistema: {(orden.tiempo_en_sistema_s or 0.0) / 60.0:.2f} min | "
            f"stock: {self.inventario.nivel}",
        )
        self._registrar_lote_produccion()

    def _esperar_stock(self, orden: Orden):
        """
        Detiene la linea hasta que entre un lote de procesadores.

        Con un solo servidor solo puede haber una orden bloqueada a la vez, asi
        que el acumulado de tiempo detenido no se solapa.
        """
        inicio_parada = self.env.now
        self.linea_detenida = True
        orden.retrasada_por_stock = True
        self.estadisticas.paradas_por_falta_stock += 1
        self.estadisticas.ordenes_retrasadas_por_stock += 1
        self.tracer.registrar(
            self.env.now,
            "parada_linea",
            f"Orden #{orden.id_orden} bloqueada | stock: {self.inventario.nivel} | "
            f"parada numero {self.estadisticas.paradas_por_falta_stock}",
        )

        while not self.inventario.hay_stock:
            # Garantiza que haya un pedido en camino aunque el umbral no se haya
            # cruzado por el camino normal (caso borde: stock inicial ya en cero).
            self._disparar_reposicion_si_corresponde(forzar=True)
            yield self._evento_stock

        detenido = self.env.now - inicio_parada
        orden.tiempo_bloqueo_stock = detenido
        self.estadisticas.tiempo_linea_detenida_s += detenido
        self.linea_detenida = False
        self.tracer.registrar(
            self.env.now,
            "reanudacion_linea",
            f"Orden #{orden.id_orden} reanudada | detenida {detenido / 60.0:.2f} min | "
            f"stock: {self.inventario.nivel}",
        )

    def _proceso_reposicion(self, tiempo_disparo: float):
        """Pedido al proveedor: entrega Q unidades tras el lead time."""
        yield self.env.timeout(self.lead_time_s)
        self.inventario.recibir_lote()
        ciclo = self.env.now - tiempo_disparo
        self.estadisticas.ciclos_reposicion_s.append(ciclo)
        self.tracer.registrar(
            self.env.now,
            "recepcion_lote",
            f"Ingresan {self.inventario.capacidad_lote} procesadores | "
            f"stock: {self.inventario.nivel} | ciclo de reposicion: {ciclo / 60.0:.2f} min",
        )
        self._despertar_esperas_de_stock()

    def _proceso_muestreo(self):
        """Muestreo temporal periodico de L y Lq (media en el tiempo, no por evento)."""
        while True:
            yield self.env.timeout(INTERVALO_MUESTREO_P1_S)
            en_cola = len(self.ordenes_en_cola)
            en_sistema = en_cola + (1 if self.estacion.ocupada else 0)
            self.estadisticas.muestrear_estado(en_cola, en_sistema)

    # ------------------------------------------------------------------
    # Auxiliares internos
    # ------------------------------------------------------------------

    def _disparar_reposicion_si_corresponde(self, forzar: bool = False) -> bool:
        """
        Dispara un pedido si el nivel cayo bajo el umbral critico y no hay otro
        en transito. Devuelve True si efectivamente se lanzo el pedido.
        """
        if self.inventario.en_reposicion:
            return False
        if not (self.inventario.necesita_reposicion() or forzar):
            return False

        self.inventario.registrar_pedido()
        self.tracer.registrar(
            self.env.now,
            "disparo_reposicion",
            f"stock {self.inventario.nivel} por debajo del umbral "
            f"s={self.inventario.umbral_critico} | pedido de "
            f"{self.inventario.capacidad_lote} unidades | lead time {self.lead_time_min:.1f} min",
        )
        self.env.process(self._proceso_reposicion(self.env.now))
        return True

    def _despertar_esperas_de_stock(self) -> None:
        """Libera a las ordenes bloqueadas y renueva el evento para futuras esperas."""
        evento = self._evento_stock
        self._evento_stock = self.env.event()
        if not evento.triggered:
            evento.succeed()

    def _registrar_lote_produccion(self) -> None:
        """Mide el tiempo en completar cada lote de LOTE_PRODUCCION laptops."""
        self._laptops_desde_ultimo_lote += 1
        if self._laptops_desde_ultimo_lote < self.lote_produccion:
            return
        transcurrido = self.env.now - self._inicio_lote_produccion_s
        self.estadisticas.tiempos_despacho_lote_s.append(transcurrido)
        self.tracer.registrar(
            self.env.now,
            "despacho_lote",
            f"Lote de {self.lote_produccion} laptops completado en "
            f"{transcurrido / 60.0:.2f} min",
        )
        self._laptops_desde_ultimo_lote = 0
        self._inicio_lote_produccion_s = self.env.now

    # ------------------------------------------------------------------
    # Metricas
    # ------------------------------------------------------------------

    def obtener_metricas(self) -> Dict:
        """
        Metricas consolidadas. Se puede llamar en cualquier momento de la corrida,
        no solamente al final.
        """
        stats = self.estadisticas
        total_s = self.tiempo_actual
        teorico = self.modelo_analitico.resumen()

        return {
            "problema": 1,
            "titulo": "Fabrica de laptops - simulacion de eventos discretos",
            # Parametros de entrada
            "tiempo_simulado_s": total_s,
            "tiempo_simulado_horas": total_s / 3600.0,
            "semilla": self.semilla,
            "lambda_ordenes_hora": self.lambda_ordenes_hora,
            "mu_laptops_hora": self.mu_hora,
            "media_ensamblaje_min": self.media_ensamblaje_min,
            "servidores": self.servidores,
            "stock_inicial": self.stock_inicial,
            "umbral_critico_s": self.inventario.umbral_critico,
            "lote_q": self.inventario.capacidad_lote,
            "lead_time_min": self.lead_time_min,
            "consumo_por_laptop": self.inventario.consumo_por_laptop,
            "lote_produccion": self.lote_produccion,
            # Resultados de flujo
            "ordenes_generadas": stats.ordenes_generadas,
            "ordenes_completadas": stats.ordenes_completadas,
            "ordenes_en_cola": len(self.ordenes_en_cola),
            "ordenes_en_sistema": len(self.ordenes_en_cola) + (1 if self.estacion.ocupada else 0),
            # Metricas de cola simuladas
            "wq_promedio_min": stats.wq_promedio_s / 60.0,
            "w_promedio_min": stats.w_promedio_s / 60.0,
            "wq_promedio_horas": stats.wq_promedio_s / 3600.0,
            "w_promedio_horas": stats.w_promedio_s / 3600.0,
            "lq_promedio": stats.lq_promedio,
            "l_promedio": stats.l_promedio,
            "utilizacion_estacion": self.estacion.utilizacion(total_s),
            "utilizacion_estacion_pct": self.estacion.utilizacion(total_s) * 100.0,
            "tiempo_servicio_efectivo_s": self._tiempo_servicio_s,
            # Las dos lecturas de "tiempo total que toma despachar un lote"
            "ciclo_reposicion_promedio_min": stats.ciclo_reposicion_promedio_s / 60.0,
            "ciclos_reposicion_observados": len(stats.ciclos_reposicion_s),
            "despacho_lote_promedio_min": stats.despacho_lote_promedio_s / 60.0,
            "lotes_produccion_observados": len(stats.tiempos_despacho_lote_s),
            # Inventario
            "paradas_por_falta_stock": stats.paradas_por_falta_stock,
            "ordenes_retrasadas_por_stock": stats.ordenes_retrasadas_por_stock,
            "tiempo_linea_detenida_min": stats.tiempo_linea_detenida_s / 60.0,
            "eficiencia_reabastecimiento": stats.eficiencia_reabastecimiento(total_s),
            "eficiencia_reabastecimiento_pct": stats.eficiencia_reabastecimiento(total_s) * 100.0,
            "stock_actual": self.inventario.nivel,
            "stock_minimo": self.inventario.nivel_minimo,
            "pedidos_disparados": self.inventario.pedidos_disparados,
            "lotes_recibidos": self.inventario.lotes_recibidos,
            "unidades_consumidas": self.inventario.unidades_consumidas,
            "unidades_recibidas": self.inventario.unidades_recibidas,
            "linea_detenida": self.linea_detenida,
            # Contraste teorico M/M/1
            "teorico_rho": teorico["rho"],
            "teorico_p0": teorico["p0"],
            "teorico_l": teorico["l"],
            "teorico_lq": teorico["lq"],
            "teorico_w_min": teorico["w_min"],
            "teorico_wq_min": teorico["wq_min"],
        }


def _selfcheck() -> None:
    """Corrida corta reproducible con asserts de coherencia."""
    sim = FabricaSimulation(semilla=SEMILLA_DEFECTO)
    metricas = sim.ejecutar(duracion_horas=8.0)

    assert metricas["ordenes_generadas"] > 0
    assert metricas["ordenes_completadas"] > 0
    assert metricas["ordenes_completadas"] <= metricas["ordenes_generadas"]
    for clave, valor in metricas.items():
        if isinstance(valor, (int, float)) and not isinstance(valor, bool):
            assert valor >= 0 or clave in (), f"metrica negativa: {clave}={valor}"

    # Con los parametros oficiales el inventario nunca se agota
    assert metricas["paradas_por_falta_stock"] == 0, metricas["paradas_por_falta_stock"]
    assert abs(metricas["eficiencia_reabastecimiento"] - 1.0) < 1e-12

    # Reproducibilidad con la misma semilla
    otra = FabricaSimulation(semilla=SEMILLA_DEFECTO).ejecutar(8.0)
    assert otra["ordenes_generadas"] == metricas["ordenes_generadas"]
    assert abs(otra["wq_promedio_min"] - metricas["wq_promedio_min"]) < 1e-9

    print(
        "selfcheck discrete_sim: OK "
        f"(ordenes={metricas['ordenes_generadas']}, "
        f"Wq={metricas['wq_promedio_min']:.2f} min vs teorico 25.00 min, "
        f"paradas={metricas['paradas_por_falta_stock']})"
    )


if __name__ == "__main__":
    _selfcheck()
