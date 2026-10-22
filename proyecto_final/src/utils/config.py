"""Carga y validacion de un escenario (JSON) y construccion de los objetos de dominio (P7)."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from src.core.network_entities import Enlace, Paquete, Router, Servidor
from src.core.no_lineal.gradiente_enfriamiento import GradienteEnfriamiento
from src.core.no_lineal.lagrange_energia import AsignadorLagrange
from src.core.no_lineal.modelo_termico import ModeloTermico
from src.core.red import Cluster, Red
from src.utils.validators import ErrorValidacion, Validador

_RUTA_ESCENARIO_DEFAULT = Path(__file__).resolve().parent.parent.parent / "data" / "escenario_default.json"


class Configuracion:
    """Escenario validado (topologia, clusteres y paquetes de prueba) listo para usarse.

    Guarda los datos crudos ya validados y construye objetos de dominio NUEVOS en cada
    llamada a `construir_red()` / `construir_paquetes()`, para que distintas corridas
    (o distintos tests) nunca comparten estado mutable por accidente.
    """

    def __init__(self, datos: dict) -> None:
        self._datos = datos

    @classmethod
    def desde_archivo(cls, ruta: str | Path) -> "Configuracion":
        """Carga un escenario desde un archivo JSON. ErrorValidacion si no existe o es invalido."""
        ruta = Path(ruta)
        try:
            texto = ruta.read_text(encoding="utf-8")
        except OSError as e:
            raise ErrorValidacion(f"no se pudo leer el archivo de escenario '{ruta}': {e}") from None

        try:
            datos = json.loads(texto)
        except json.JSONDecodeError as e:
            raise ErrorValidacion(f"el archivo de escenario '{ruta}' tiene JSON invalido: {e}") from None

        Validador.validar_escenario(datos)
        return cls(datos)

    @classmethod
    def por_defecto(cls) -> "Configuracion":
        """Carga el escenario por defecto empaquetado con el proyecto (P7)."""
        return cls.desde_archivo(_RUTA_ESCENARIO_DEFAULT)

    @property
    def datos(self) -> dict:
        """Copia profunda de los datos crudos del escenario."""
        return copy.deepcopy(self._datos)

    def construir_red(self) -> Red:
        """Construye una Red nueva (routers, enlaces y clusteres nuevos) desde el escenario."""
        routers = [
            Router(
                id=nodo["id"],
                capa=nodo["capa"],
                latencia_procesamiento=nodo["latencia_procesamiento"],
                posicion=tuple(nodo["posicion"]),
            )
            for nodo in self._datos["nodos"]
        ]

        enlaces = [
            Enlace(
                origen_id=enlace["origen"],
                destino_id=enlace["destino"],
                latencia_base=enlace["latencia"],
                capacidad=enlace["capacidad"],
            )
            for enlace in self._datos["enlaces"]
        ]

        clusteres = []
        for cluster in self._datos["clusteres"]:
            servidores = [
                Servidor(
                    id=servidor["id"],
                    capacidad=servidor["capacidad"],
                    tasa_servicio=servidor["tasa_servicio"],
                    posicion=tuple(servidor["posicion"]),
                )
                for servidor in cluster["servidores"]
            ]
            clusteres.append(Cluster(id=cluster["id"], tor_id=cluster["tor"], servidores=servidores))

        return Red(routers=routers, enlaces=enlaces, clusteres=clusteres)

    def parametros(self, seccion: str) -> dict:
        """Copia de una seccion de `parametros` del escenario ({} si no esta definida)."""
        return dict(self._datos["parametros"].get(seccion, {}))

    def construir_modelo_termico(self) -> ModeloTermico:
        return self._construir(ModeloTermico, "termico")

    def construir_gradiente(self) -> GradienteEnfriamiento:
        return self._construir(GradienteEnfriamiento, "gradiente")

    def construir_lagrange(self) -> AsignadorLagrange:
        return self._construir(AsignadorLagrange, "lagrange")

    def _construir(self, clase: type, seccion: str):
        """Crea `clase` con los parametros de la seccion; una clave desconocida es un error de validacion."""
        try:
            return clase(**self.parametros(seccion))
        except TypeError as e:
            raise ErrorValidacion(f"parametros.{seccion} tiene una clave invalida: {e}") from None

    def construir_paquetes(self) -> list[Paquete]:
        """Construye la lista de paquetes de prueba (objetos nuevos) desde el escenario."""
        return [
            Paquete(
                id=p["id"],
                requerimiento=p["requerimiento"],
                prioridad=p["prioridad"],
                destino_cluster=p["destino_cluster"],
            )
            for p in self._datos["paquetes_prueba"]
        ]
