"""Red por etapas: routers, enlaces y clusteres de servidores (R1)."""

from __future__ import annotations

from src.core.network_entities import Enlace, Router, Servidor
from src.utils.validators import ErrorValidacion

CAPAS = ("gateway", "nucleo", "agregacion", "tor")


class Cluster:
    """Agrupa los servidores detras de un switch ToR; expone su demanda agregada (R5)."""

    def __init__(self, id: str, tor_id: str, servidores: list[Servidor]) -> None:
        self._id = id
        self._tor_id = tor_id
        self._servidores = tuple(servidores)
        self._energia_asignada = 0.0

    @property
    def id(self) -> str:
        return self._id

    @property
    def tor_id(self) -> str:
        return self._tor_id

    @property
    def servidores(self) -> tuple[Servidor, ...]:
        return self._servidores

    def demanda(self) -> float:
        """Carga total pendiente del cluster: en proceso + en cola, solo de servidores operativos.

        Es el `w_i` (demanda) que consume el reparto de energia por multiplicadores de
        Lagrange (R5): un servidor caido no aporta demanda porque no puede procesar nada.
        """
        total = 0.0
        for servidor in self._servidores:
            if servidor.esta_operativo:
                total += servidor.carga_actual
                total += sum(p.requerimiento for p in servidor.cola)
        return total

    @property
    def energia_asignada(self) -> float:
        return self._energia_asignada

    @energia_asignada.setter
    def energia_asignada(self, valor: float) -> None:
        if valor < 0:
            raise ErrorValidacion(
                f"energia_asignada de cluster {self._id} no puede ser negativa (recibido: {valor})"
            )
        self._energia_asignada = valor


class Red:
    """Grafo de la red organizado por etapas (gateway -> nucleo -> agregacion -> tor).

    Es la estructura que recorre RutaMasCorta (R1): `etapas()` agrupa los nodos por capa
    en el orden de CAPAS, y `vecinos()` / `enlace()` dan, para cada arco entre etapas
    consecutivas, el nodo destino y su costo actual.
    """

    def __init__(self, routers: list[Router], enlaces: list[Enlace], clusteres: list[Cluster]) -> None:
        self._routers: dict[str, Router] = {r.id: r for r in routers}
        self._enlaces: dict[tuple[str, str], Enlace] = {(e.origen_id, e.destino_id): e for e in enlaces}
        self._clusteres: dict[str, Cluster] = {c.id: c for c in clusteres}

        self._vecinos: dict[str, list[str]] = {}
        for enlace in enlaces:
            self._vecinos.setdefault(enlace.origen_id, []).append(enlace.destino_id)

        self._etapas: dict[str, list[str]] = {capa: [] for capa in CAPAS}
        for router in routers:
            self._etapas[router.capa].append(router.id)

    def nodo(self, id: str) -> Router | Servidor:
        """Busca un router o un servidor (de algun cluster) por id. KeyError si no existe."""
        if id in self._routers:
            return self._routers[id]
        for cluster in self._clusteres.values():
            for servidor in cluster.servidores:
                if servidor.id == id:
                    return servidor
        raise KeyError(f"no existe un nodo con id '{id}'")

    def enlace(self, origen_id: str, destino_id: str) -> Enlace:
        """Enlace dirigido de `origen_id` a `destino_id`. KeyError si no existe."""
        clave = (origen_id, destino_id)
        if clave not in self._enlaces:
            raise KeyError(f"no existe un enlace de '{origen_id}' a '{destino_id}'")
        return self._enlaces[clave]

    def vecinos(self, id: str) -> list[str]:
        """Destinos de los enlaces salientes de `id`, en el orden en que se agregaron."""
        return list(self._vecinos.get(id, []))

    def etapas(self) -> list[list[str]]:
        """Una lista de ids por capa, en el orden de CAPAS; dentro de cada capa, orden de insercion."""
        return [list(self._etapas[capa]) for capa in CAPAS]

    def etapa_de(self, id: str) -> int:
        """Indice (0-based) de la capa de `id`, segun el orden de CAPAS. KeyError si no existe."""
        router = self._routers[id]
        return CAPAS.index(router.capa)

    def nodos_operativos(self) -> list[Router]:
        """Routers de la red que no estan caidos."""
        return [r for r in self._routers.values() if r.esta_operativo]

    def cluster(self, id: str) -> Cluster:
        """Cluster por id. KeyError si no existe."""
        if id not in self._clusteres:
            raise KeyError(f"no existe un cluster con id '{id}'")
        return self._clusteres[id]

    @property
    def routers(self) -> tuple[Router, ...]:
        return tuple(self._routers.values())

    @property
    def enlaces(self) -> tuple[Enlace, ...]:
        return tuple(self._enlaces.values())

    @property
    def clusteres(self) -> tuple[Cluster, ...]:
        return tuple(self._clusteres.values())
