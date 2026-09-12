"""
Entidades del dominio del Problema 1: fabrica de laptops.

Modelo de objetos puro, sin dependencia de SimPy. El motor de eventos discretos
(src/simulation/discrete_sim.py) orquesta estas entidades; aca vive el estado y
las reglas de negocio, que asi se pueden testear sin levantar un entorno de
simulacion.

Unidad de tiempo interna: SEGUNDOS simulados, igual que el reloj de SimPy.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from src.utils.validators import (
    ValidacionError,
    validar_entero_no_negativo,
    validar_entero_positivo,
    validar_politica_inventario,
)


@dataclass
class Orden:
    """
    Orden de produccion de una laptop.

    Recorre el ciclo llegada -> cola -> (posible espera por falta de stock) ->
    ensamblaje -> despacho. Todos los sellos de tiempo estan en segundos
    simulados; None significa que esa etapa todavia no ocurrio.
    """

    id_orden: int
    tiempo_llegada: float
    tiempo_inicio_ensamblaje: Optional[float] = None
    tiempo_fin_ensamblaje: Optional[float] = None
    tiempo_bloqueo_stock: float = 0.0
    retrasada_por_stock: bool = False

    def __post_init__(self) -> None:
        if self.id_orden < 1:
            raise ValidacionError(f"El id de la orden debe ser positivo. Recibido: {self.id_orden}.")
        if self.tiempo_llegada < 0:
            raise ValidacionError(
                f"El tiempo de llegada no puede ser negativo. Recibido: {self.tiempo_llegada}."
            )

    @property
    def completada(self) -> bool:
        """True cuando la laptop ya salio de la estacion."""
        return self.tiempo_fin_ensamblaje is not None

    @property
    def espera_en_cola_s(self) -> Optional[float]:
        """
        Wq de esta orden: tiempo desde que llego hasta que tomo la estacion.
        No incluye el bloqueo posterior por falta de procesadores.
        """
        if self.tiempo_inicio_ensamblaje is None:
            return None
        return self.tiempo_inicio_ensamblaje - self.tiempo_llegada

    @property
    def tiempo_en_sistema_s(self) -> Optional[float]:
        """W de esta orden: tiempo total desde la llegada hasta el despacho."""
        if self.tiempo_fin_ensamblaje is None:
            return None
        return self.tiempo_fin_ensamblaje - self.tiempo_llegada

    @property
    def duracion_ensamblaje_s(self) -> Optional[float]:
        """Tiempo de ocupacion efectiva de la estacion, bloqueo incluido."""
        if self.tiempo_fin_ensamblaje is None or self.tiempo_inicio_ensamblaje is None:
            return None
        return self.tiempo_fin_ensamblaje - self.tiempo_inicio_ensamblaje


class EstacionEnsamblaje:
    """
    Estacion de ensamblaje unica (c = 1). Expone el estado que la capa grafica
    necesita leer en cualquier frame: si esta ocupada y que orden esta montada.
    """

    def __init__(self, id_estacion: int = 1) -> None:
        self.id_estacion = validar_entero_positivo(id_estacion, "Id de estacion")
        self.ocupada: bool = False
        self.orden_actual: Optional[Orden] = None
        self.laptops_ensambladas: int = 0
        self.tiempo_ocupada_s: float = 0.0

    @property
    def libre(self) -> bool:
        """True si no hay ninguna orden montada."""
        return not self.ocupada

    def montar(self, orden: Orden) -> None:
        """Monta una orden en la estacion."""
        if self.ocupada:
            raise ValidacionError(
                f"La estacion {self.id_estacion} ya esta ocupada por la orden "
                f"{self.orden_actual.id_orden if self.orden_actual else 'desconocida'}."
            )
        self.ocupada = True
        self.orden_actual = orden

    def liberar(self, duracion_s: float) -> None:
        """Desmonta la orden actual y acumula el tiempo de ocupacion."""
        if not self.ocupada:
            raise ValidacionError(f"La estacion {self.id_estacion} ya estaba libre.")
        if duracion_s < 0:
            raise ValidacionError(f"La duracion no puede ser negativa: {duracion_s}.")
        self.ocupada = False
        self.orden_actual = None
        self.laptops_ensambladas += 1
        self.tiempo_ocupada_s += duracion_s

    def utilizacion(self, tiempo_total_s: float) -> float:
        """Fraccion del tiempo simulado en que la estacion estuvo ocupada."""
        if tiempo_total_s <= 0:
            return 0.0
        return self.tiempo_ocupada_s / tiempo_total_s

    def __repr__(self) -> str:
        estado = "ocupada" if self.ocupada else "libre"
        return f"EstacionEnsamblaje(id={self.id_estacion}, {estado}, ensambladas={self.laptops_ensambladas})"


class InventarioProcesadores:
    """
    Inventario de procesadores de gama alta con politica de revision continua (s, Q).

    Cuando el nivel cae por DEBAJO del umbral critico s se dispara un pedido de Q
    unidades, que el proveedor entrega tras el lead time. No hay capacidad maxima
    declarada en el enunciado, asi que el inventario no rechaza lotes.
    """

    def __init__(
        self,
        nivel_inicial: int,
        umbral_critico: int,
        capacidad_lote: int,
        consumo_por_laptop: int = 1,
    ) -> None:
        validar_politica_inventario(umbral_critico, capacidad_lote, nivel_inicial)
        self.nivel: int = validar_entero_no_negativo(nivel_inicial, "Stock inicial")
        self.umbral_critico: int = umbral_critico
        self.capacidad_lote: int = capacidad_lote
        self.consumo_por_laptop: int = validar_entero_positivo(
            consumo_por_laptop, "Consumo por laptop"
        )
        self.en_reposicion: bool = False

        # Contadores historicos
        self.nivel_minimo: int = self.nivel
        self.unidades_consumidas: int = 0
        self.unidades_recibidas: int = 0
        self.pedidos_disparados: int = 0
        self.lotes_recibidos: int = 0

    @property
    def hay_stock(self) -> bool:
        """True si alcanza para ensamblar al menos una laptop mas."""
        return self.nivel >= self.consumo_por_laptop

    @property
    def bajo_umbral(self) -> bool:
        """True si el nivel cayo por debajo del umbral critico s."""
        return self.nivel < self.umbral_critico

    def necesita_reposicion(self) -> bool:
        """True si corresponde disparar un pedido y no hay uno ya en camino."""
        return self.bajo_umbral and not self.en_reposicion

    def consumir(self, unidades: Optional[int] = None) -> int:
        """
        Descuenta los procesadores que consume una laptop.

        Falla fuerte si no hay stock: consumir en negativo produciria un inventario
        imposible y metricas mudas. El motor debe consultar hay_stock antes.
        """
        cantidad = self.consumo_por_laptop if unidades is None else validar_entero_positivo(
            unidades, "Unidades a consumir"
        )
        if self.nivel < cantidad:
            raise ValidacionError(
                f"Stock insuficiente: nivel={self.nivel}, se pidieron {cantidad} unidades."
            )
        self.nivel -= cantidad
        self.unidades_consumidas += cantidad
        self.nivel_minimo = min(self.nivel_minimo, self.nivel)
        return self.nivel

    def registrar_pedido(self) -> None:
        """Marca que hay un pedido de reposicion en transito."""
        if self.en_reposicion:
            raise ValidacionError("Ya hay un pedido de reposicion en transito.")
        self.en_reposicion = True
        self.pedidos_disparados += 1

    def recibir_lote(self, unidades: Optional[int] = None) -> int:
        """Ingresa el lote entregado por el proveedor y cierra el pedido en transito."""
        cantidad = self.capacidad_lote if unidades is None else validar_entero_positivo(
            unidades, "Unidades del lote"
        )
        self.nivel += cantidad
        self.unidades_recibidas += cantidad
        self.lotes_recibidos += 1
        self.en_reposicion = False
        return self.nivel

    def __repr__(self) -> str:
        return (
            f"InventarioProcesadores(nivel={self.nivel}, s={self.umbral_critico}, "
            f"Q={self.capacidad_lote}, en_reposicion={self.en_reposicion})"
        )


class EstadisticasFabrica:
    """
    Acumulador de metricas del Problema 1.

    L y Lq se estiman por muestreo temporal a intervalo fijo (media temporal),
    no por promedio de eventos: es la definicion correcta del promedio de una
    cola en el tiempo.
    """

    def __init__(self) -> None:
        self.ordenes_generadas: int = 0
        self.ordenes_completadas: int = 0
        self.esperas_cola_s: List[float] = []
        self.tiempos_sistema_s: List[float] = []

        # Muestreo temporal de L y Lq
        self.muestras_cola: int = 0
        self.suma_cola: float = 0.0
        self.suma_sistema: float = 0.0

        # Inventario y paradas de linea
        self.paradas_por_falta_stock: int = 0
        self.ordenes_retrasadas_por_stock: int = 0
        self.tiempo_linea_detenida_s: float = 0.0

        # Ciclos de reposicion: disparo del pedido -> ingreso del lote
        self.ciclos_reposicion_s: List[float] = []

        # Despacho de lotes de produccion: marcas de tiempo cada N laptops
        self.tiempos_despacho_lote_s: List[float] = []

    def registrar_llegada(self) -> None:
        """Contabiliza una orden que entro al sistema."""
        self.ordenes_generadas += 1

    def registrar_completada(self, espera_cola_s: float, tiempo_sistema_s: float) -> None:
        """Contabiliza una laptop terminada con sus tiempos."""
        if espera_cola_s < 0 or tiempo_sistema_s < 0:
            raise ValidacionError(
                f"Tiempos negativos al cerrar una orden: Wq={espera_cola_s}, W={tiempo_sistema_s}."
            )
        self.ordenes_completadas += 1
        self.esperas_cola_s.append(espera_cola_s)
        self.tiempos_sistema_s.append(tiempo_sistema_s)

    def muestrear_estado(self, en_cola: int, en_sistema: int) -> None:
        """Toma una muestra temporal del largo de la cola y del sistema."""
        self.muestras_cola += 1
        self.suma_cola += en_cola
        self.suma_sistema += en_sistema

    @property
    def wq_promedio_s(self) -> float:
        """Tiempo de espera promedio en cola, en segundos."""
        if not self.esperas_cola_s:
            return 0.0
        return sum(self.esperas_cola_s) / len(self.esperas_cola_s)

    @property
    def w_promedio_s(self) -> float:
        """Tiempo promedio en el sistema, en segundos."""
        if not self.tiempos_sistema_s:
            return 0.0
        return sum(self.tiempos_sistema_s) / len(self.tiempos_sistema_s)

    @property
    def lq_promedio(self) -> float:
        """Numero promedio de ordenes en cola (media temporal)."""
        if self.muestras_cola == 0:
            return 0.0
        return self.suma_cola / self.muestras_cola

    @property
    def l_promedio(self) -> float:
        """Numero promedio de ordenes en el sistema (media temporal)."""
        if self.muestras_cola == 0:
            return 0.0
        return self.suma_sistema / self.muestras_cola

    @property
    def ciclo_reposicion_promedio_s(self) -> float:
        """Promedio del ciclo de reposicion de componentes, en segundos."""
        if not self.ciclos_reposicion_s:
            return 0.0
        return sum(self.ciclos_reposicion_s) / len(self.ciclos_reposicion_s)

    @property
    def despacho_lote_promedio_s(self) -> float:
        """Promedio del tiempo en completar un lote de produccion, en segundos."""
        if not self.tiempos_despacho_lote_s:
            return 0.0
        return sum(self.tiempos_despacho_lote_s) / len(self.tiempos_despacho_lote_s)

    def eficiencia_reabastecimiento(self, tiempo_total_s: float) -> float:
        """
        Eficiencia del reabastecimiento, definida como la fraccion del tiempo
        simulado en que la linea NO estuvo detenida por falta de procesadores:

            eficiencia = 1 - (tiempo_linea_detenida / tiempo_total)

        Vale 1.0 (100%) cuando el inventario nunca dejo sin material a la estacion.
        """
        if tiempo_total_s <= 0:
            return 1.0
        return max(0.0, 1.0 - self.tiempo_linea_detenida_s / tiempo_total_s)


def _selfcheck() -> None:
    """Comprobaciones minimas de las entidades del Problema 1."""
    orden = Orden(id_orden=1, tiempo_llegada=100.0)
    assert orden.espera_en_cola_s is None
    orden.tiempo_inicio_ensamblaje = 160.0
    orden.tiempo_fin_ensamblaje = 460.0
    assert orden.espera_en_cola_s == 60.0
    assert orden.tiempo_en_sistema_s == 360.0
    assert orden.duracion_ensamblaje_s == 300.0
    assert orden.completada

    est = EstacionEnsamblaje()
    assert est.libre and not est.ocupada
    est.montar(orden)
    assert est.ocupada and est.orden_actual is orden
    est.liberar(300.0)
    assert est.libre and est.laptops_ensambladas == 1
    assert abs(est.utilizacion(600.0) - 0.5) < 1e-9

    inv = InventarioProcesadores(nivel_inicial=50, umbral_critico=10, capacidad_lote=50)
    assert inv.hay_stock and not inv.bajo_umbral
    for _ in range(41):
        inv.consumir()
    assert inv.nivel == 9 and inv.bajo_umbral and inv.necesita_reposicion()
    inv.registrar_pedido()
    assert inv.en_reposicion and not inv.necesita_reposicion()
    inv.recibir_lote()
    assert inv.nivel == 59 and not inv.en_reposicion and inv.lotes_recibidos == 1
    assert inv.nivel_minimo == 9

    vacio = InventarioProcesadores(nivel_inicial=0, umbral_critico=0, capacidad_lote=5)
    assert not vacio.hay_stock
    try:
        vacio.consumir()
    except ValidacionError:
        pass
    else:
        raise AssertionError("consumir() permitio dejar el inventario en negativo")

    stats = EstadisticasFabrica()
    stats.registrar_llegada()
    stats.registrar_completada(60.0, 360.0)
    stats.muestrear_estado(2, 3)
    stats.muestrear_estado(0, 1)
    assert stats.wq_promedio_s == 60.0
    assert stats.lq_promedio == 1.0 and stats.l_promedio == 2.0
    assert stats.eficiencia_reabastecimiento(1000.0) == 1.0
    stats.tiempo_linea_detenida_s = 250.0
    assert abs(stats.eficiencia_reabastecimiento(1000.0) - 0.75) < 1e-9

    print("selfcheck factory_entities: OK")


if __name__ == "__main__":
    _selfcheck()
