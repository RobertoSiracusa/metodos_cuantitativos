"""Entidades basicas de la red: nodos, enlaces y paquetes (R1, R2, R6)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.utils.validators import Validador


class CapacidadExcedidaError(ValueError):
    """Se lanza cuando una asignacion a un Servidor superaria su capacidad libre."""


@dataclass(frozen=True)
class Paquete:
    """Tarea en transito por la red.

    Es el item del modelo de mochila (R2): `requerimiento` es el peso (unidades de
    RAM/CPU que consume en el servidor destino) y `prioridad` es el valor que aporta
    si se selecciona. Es inmutable: el Servidor administra su estado (en cola o en
    proceso); el Paquete en si nunca cambia.
    """

    id: str
    requerimiento: int
    prioridad: int
    destino_cluster: str
    t_creacion: float = 0.0

    def __post_init__(self) -> None:
        Validador.validar_rango(f"paquete {self.id}.requerimiento", self.requerimiento, minimo=1, entero=True)
        Validador.validar_rango(f"paquete {self.id}.prioridad", self.prioridad, minimo=1, maximo=10, entero=True)
        Validador.validar_rango(f"paquete {self.id}.t_creacion", self.t_creacion, minimo=0)


class Nodo(ABC):
    """Nodo generico de la red: identidad, posicion y estado operativo/caido.

    Es la base comun de Router y Servidor (herencia): fallar()/reparar() y la propiedad
    esta_operativo viven una sola vez aqui. Cada subclase solo define como calcula
    tiempo_servicio (metodo abstracto), que es lo unico que cambia entre un router
    (latencia fija de procesamiento) y un servidor (tiempo proporcional a la carga del
    paquete).
    """

    def __init__(self, id: str, posicion: tuple[float, float]) -> None:
        self._id = id
        self._posicion = posicion
        self._operativo = True

    @property
    def id(self) -> str:
        return self._id

    @property
    def posicion(self) -> tuple[float, float]:
        return self._posicion

    @property
    def esta_operativo(self) -> bool:
        return self._operativo

    def fallar(self) -> None:
        """Marca el nodo como caido: deja de participar en rutas y en el procesamiento."""
        self._operativo = False

    def reparar(self) -> None:
        """Restaura el nodo a estado operativo."""
        self._operativo = True

    @abstractmethod
    def tiempo_servicio(self, paquete: Paquete) -> float:
        """Tiempo que tarda este nodo en procesar `paquete` (unidades de latencia del escenario)."""
        raise NotImplementedError

    def __repr__(self) -> str:
        estado = "operativo" if self._operativo else "caido"
        return f"{type(self).__name__}(id={self._id!r}, estado={estado})"


class Router(Nodo):
    """Nodo intermedio que reenvia paquetes sin encolarlos: su costo de procesamiento es fijo."""

    def __init__(self, id: str, capa: str, latencia_procesamiento: float, posicion: tuple[float, float]) -> None:
        super().__init__(id, posicion)
        self._capa = capa
        self._latencia_procesamiento = latencia_procesamiento

    @property
    def capa(self) -> str:
        return self._capa

    def tiempo_servicio(self, paquete: Paquete) -> float:
        return self._latencia_procesamiento


class Servidor(Nodo):
    """Nodo de computo: mantiene una cola de espera y procesa paquetes dentro de su capacidad.

    `tiempo_servicio` devuelve la MEDIA del tiempo de procesamiento
    (requerimiento / tasa_servicio). Muestrear una duracion exponencial con esa media
    para cada paquete en la simulacion es responsabilidad del motor SimPy (F3), no de
    esta clase: aqui solo vive el valor esperado.
    """

    def __init__(self, id: str, capacidad: int, tasa_servicio: float, posicion: tuple[float, float]) -> None:
        super().__init__(id, posicion)
        self._capacidad = capacidad
        self._tasa_servicio = tasa_servicio
        self._cola: list[Paquete] = []
        self._en_proceso: dict[str, Paquete] = {}

    @property
    def capacidad(self) -> int:
        return self._capacidad

    @property
    def tasa_servicio(self) -> float:
        return self._tasa_servicio

    @property
    def cola(self) -> tuple[Paquete, ...]:
        return tuple(self._cola)

    @property
    def en_proceso(self) -> tuple[Paquete, ...]:
        return tuple(self._en_proceso.values())

    @property
    def carga_actual(self) -> int:
        """Suma de requerimientos de los paquetes actualmente en proceso (no en cola)."""
        return sum(p.requerimiento for p in self._en_proceso.values())

    @property
    def capacidad_libre(self) -> int:
        return self._capacidad - self.carga_actual

    def encolar(self, paquete: Paquete) -> None:
        """Agrega un paquete al final de la cola de espera."""
        self._cola.append(paquete)

    def asignar(self, paquetes: list[Paquete]) -> None:
        """Mueve `paquetes` de la cola a "en proceso", de forma atomica.

        Si algun paquete no esta en la cola no mueve nada y lanza ValueError. Si la suma
        de requerimientos excede la capacidad libre actual tampoco mueve nada y lanza
        CapacidadExcedidaError: la operacion es todo-o-nada, nunca deja al servidor en
        un estado parcialmente actualizado.
        """
        for p in paquetes:
            if p not in self._cola:
                raise ValueError(f"el paquete {p.id} no esta en la cola del servidor {self.id}")

        suma_requerimientos = sum(p.requerimiento for p in paquetes)
        if suma_requerimientos > self.capacidad_libre:
            raise CapacidadExcedidaError(
                f"servidor {self.id}: se intento asignar {suma_requerimientos} unidades "
                f"pero la capacidad libre es {self.capacidad_libre}"
            )

        for p in paquetes:
            self._cola.remove(p)
            self._en_proceso[p.id] = p

    def liberar(self, paquete_id: str) -> None:
        """Quita un paquete de "en proceso" porque ya termino su servicio. KeyError si no estaba."""
        if paquete_id not in self._en_proceso:
            raise KeyError(f"el paquete {paquete_id} no esta en proceso en el servidor {self.id}")
        del self._en_proceso[paquete_id]

    def tiempo_servicio(self, paquete: Paquete) -> float:
        return paquete.requerimiento / self._tasa_servicio


class Enlace:
    """Conexion dirigida entre dos nodos; su latencia efectiva crece con la congestion.

    `costo_actual` aplica el factor de congestion de una cola M/M/1: el tiempo de espera
    en ese modelo es proporcional a 1 / (1 - rho), con rho la utilizacion (ocupacion) del
    enlace. Por eso el costo final es `latencia_base * (1 + rho / (1 - rho))`: a baja
    ocupacion el costo es casi la latencia base, y crece sin cota a medida que rho se
    acerca a 1 (de ahi que `ocupacion` se tope en 0.95: evita dividir por cero y modela
    la saturacion del enlace).
    """

    def __init__(self, origen_id: str, destino_id: str, latencia_base: float, capacidad: int = 10) -> None:
        self._origen_id = origen_id
        self._destino_id = destino_id
        self._latencia_base = latencia_base
        self._capacidad = capacidad
        self._en_transito: set[str] = set()

    @property
    def origen_id(self) -> str:
        return self._origen_id

    @property
    def destino_id(self) -> str:
        return self._destino_id

    @property
    def latencia_base(self) -> float:
        return self._latencia_base

    @property
    def capacidad(self) -> int:
        return self._capacidad

    @property
    def ocupacion(self) -> float:
        return min(len(self._en_transito) / self._capacidad, 0.95)

    def entrar(self, paquete: Paquete) -> None:
        """Registra que `paquete` entro en transito por este enlace."""
        self._en_transito.add(paquete.id)

    def salir(self, paquete: Paquete) -> None:
        """Quita a `paquete` del transito. KeyError si no estaba en transito."""
        if paquete.id not in self._en_transito:
            raise KeyError(f"el paquete {paquete.id} no esta en transito por este enlace")
        self._en_transito.remove(paquete.id)

    def costo_actual(self) -> float:
        """Costo efectivo = latencia_base * (1 + rho / (1 - rho)), con rho = ocupacion."""
        rho = self.ocupacion
        return self._latencia_base * (1 + rho / (1 - rho))
