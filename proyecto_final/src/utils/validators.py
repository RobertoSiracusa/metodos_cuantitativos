"""Validacion de datos de entrada: argumentos de linea de comandos y escenarios cargados (P6).

Este modulo no depende de ninguna otra parte del proyecto (ni core, ni simulation, ni gui),
asi que puede ser importado por cualquiera sin crear dependencias circulares.
"""

from __future__ import annotations

import math
from typing import Any

CAPAS_VALIDAS = ("gateway", "nucleo", "agregacion", "tor")
SECCIONES_PARAMETROS = ("termico", "gradiente", "lagrange", "simulacion")


class ErrorValidacion(ValueError):
    """Excepcion de dominio para datos invalidos: argumentos de comando o escenario cargado."""


class Validador:
    """Validaciones estaticas y reutilizables de rango, identificadores y escenario completo."""

    @staticmethod
    def validar_rango(
        nombre: str,
        valor: Any,
        minimo: float | None = None,
        maximo: float | None = None,
        entero: bool = False,
    ) -> int | float:
        """Valida que `valor` sea numerico, finito y este dentro de [minimo, maximo].

        Rechaza explicitamente None, bool (en Python bool es subclase de int, pero no es
        un numero de dominio aqui), cadenas no convertibles a numero y los valores no
        finitos (NaN, +-inf). Devuelve el valor convertido: int si entero=True, float en
        caso contrario. minimo y maximo son inclusive.
        """
        numero = Validador._a_numero_finito(nombre, valor)
        if entero:
            if not float(numero).is_integer():
                raise ErrorValidacion(f"{nombre} debe ser un numero entero (recibido: {valor!r})")
            numero = int(numero)
        if (minimo is not None and numero < minimo) or (maximo is not None and numero > maximo):
            raise ErrorValidacion(Validador._mensaje_fuera_de_rango(nombre, valor, minimo, maximo))
        return numero

    @staticmethod
    def validar_id(nombre: str, valor: Any) -> str:
        """Valida que `valor` sea una cadena no vacia y sin ningun espacio en blanco."""
        if not isinstance(valor, str) or valor == "" or any(c.isspace() for c in valor):
            raise ErrorValidacion(
                f"{nombre} debe ser un identificador no vacio y sin espacios (recibido: {valor!r})"
            )
        return valor

    @staticmethod
    def validar_escenario(datos: dict) -> None:
        """Valida la estructura completa de un escenario y junta TODOS los errores hallados.

        A diferencia de validar_rango/validar_id (que fallan en el primer problema), este
        metodo recorre nodos, enlaces, clusteres y paquetes de prueba acumulando cada
        inconsistencia en una lista y, al final, lanza UNA sola ErrorValidacion con un
        mensaje por linea. Asi el usuario corrige todo el escenario de una vez.
        """
        if not isinstance(datos, dict):
            raise ErrorValidacion(f"el escenario debe ser un objeto JSON (recibido: {type(datos).__name__})")

        errores: list[str] = []
        claves_requeridas = ("nodos", "enlaces", "clusteres", "paquetes_prueba", "parametros")
        for clave in claves_requeridas:
            if clave not in datos:
                errores.append(f"falta la clave requerida '{clave}' en el escenario")
        if errores:
            # sin las claves base no hay nada mas que se pueda inspeccionar de forma segura
            raise ErrorValidacion("\n".join(errores))

        Validador._validar_parametros(datos["parametros"], errores)

        ids_nodos = Validador._validar_nodos(datos["nodos"], errores)
        Validador._validar_enlaces(datos["enlaces"], ids_nodos, errores)
        ids_clusteres = Validador._validar_clusteres(datos["clusteres"], ids_nodos, errores)
        Validador._validar_paquetes_prueba(datos["paquetes_prueba"], ids_clusteres, errores)

        if errores:
            raise ErrorValidacion("\n".join(errores))

    # ------------------------------------------------------------------
    # Helpers internos de validar_escenario (no forman parte de la API publica)
    # ------------------------------------------------------------------

    @staticmethod
    def _validar_nodos(nodos: Any, errores: list[str]) -> dict[str, str]:
        ids_nodos: dict[str, str] = {}
        gateways = 0
        if not isinstance(nodos, list):
            errores.append(f"nodos debe ser una lista (recibido: {type(nodos).__name__})")
            return ids_nodos
        for i, nodo in enumerate(nodos):
            prefijo = f"nodo[{i}]"
            if not isinstance(nodo, dict):
                errores.append(f"{prefijo} debe ser un objeto (recibido: {type(nodo).__name__})")
                continue

            nid = Validador._id_o_none(f"{prefijo}.id", nodo.get("id"), errores)
            if nid is not None:
                if nid in ids_nodos:
                    errores.append(f"id de nodo duplicado: '{nid}'")
                else:
                    ids_nodos[nid] = nodo.get("capa")

            capa = nodo.get("capa")
            if capa not in CAPAS_VALIDAS:
                errores.append(f"{prefijo} ({nid}).capa invalida: {capa!r}, debe ser una de {CAPAS_VALIDAS}")
            elif capa == "gateway":
                gateways += 1

            Validador._validar_positivo(f"{prefijo} ({nid}).latencia_procesamiento", nodo.get("latencia_procesamiento"), errores)
            Validador._validar_posicion_2d(f"{prefijo} ({nid}).posicion", nodo.get("posicion"), errores)

        if gateways != 1:
            errores.append(f"debe haber exactamente un nodo gateway (encontrados: {gateways})")
        return ids_nodos

    @staticmethod
    def _validar_enlaces(enlaces: Any, ids_nodos: dict[str, str], errores: list[str]) -> None:
        if not isinstance(enlaces, list):
            errores.append(f"enlaces debe ser una lista (recibido: {type(enlaces).__name__})")
            return
        vistos: set[tuple[Any, Any]] = set()
        for i, enlace in enumerate(enlaces):
            prefijo = f"enlace[{i}]"
            if not isinstance(enlace, dict):
                errores.append(f"{prefijo} debe ser un objeto (recibido: {type(enlace).__name__})")
                continue

            origen = enlace.get("origen")
            destino = enlace.get("destino")
            if origen not in ids_nodos:
                errores.append(f"{prefijo}.origen '{origen}' no existe entre los nodos")
            if destino not in ids_nodos:
                errores.append(f"{prefijo}.destino '{destino}' no existe entre los nodos")

            if origen in ids_nodos and destino in ids_nodos:
                capa_origen = ids_nodos[origen]
                capa_destino = ids_nodos[destino]
                if capa_origen in CAPAS_VALIDAS and capa_destino in CAPAS_VALIDAS:
                    idx_origen = CAPAS_VALIDAS.index(capa_origen)
                    idx_destino = CAPAS_VALIDAS.index(capa_destino)
                    if idx_destino != idx_origen + 1:
                        errores.append(
                            f"{prefijo} ({origen}->{destino}) debe ir de la capa '{capa_origen}' a la "
                            f"capa siguiente, pero destino esta en '{capa_destino}'"
                        )
                par = (origen, destino)
                if par in vistos:
                    errores.append(f"{prefijo} ({origen}->{destino}) es un enlace duplicado")
                else:
                    vistos.add(par)

            Validador._validar_positivo(f"{prefijo}.latencia", enlace.get("latencia"), errores)
            try:
                Validador.validar_rango(f"{prefijo}.capacidad", enlace.get("capacidad"), minimo=1, entero=True)
            except ErrorValidacion as e:
                errores.append(str(e))

    @staticmethod
    def _validar_clusteres(clusteres: Any, ids_nodos: dict[str, str], errores: list[str]) -> set[str]:
        ids_clusteres: set[str] = set()
        if not isinstance(clusteres, list):
            errores.append(f"clusteres debe ser una lista (recibido: {type(clusteres).__name__})")
            return ids_clusteres
        ids_servidores: set[str] = set()
        for i, cluster in enumerate(clusteres):
            prefijo = f"cluster[{i}]"
            if not isinstance(cluster, dict):
                errores.append(f"{prefijo} debe ser un objeto (recibido: {type(cluster).__name__})")
                continue

            cid = Validador._id_o_none(f"{prefijo}.id", cluster.get("id"), errores)
            if cid is not None:
                if cid in ids_clusteres:
                    errores.append(f"id de cluster duplicado: '{cid}'")
                else:
                    ids_clusteres.add(cid)

            tor = cluster.get("tor")
            if tor not in ids_nodos:
                errores.append(f"{prefijo} ({cid}).tor '{tor}' no existe entre los nodos")
            elif ids_nodos[tor] != "tor":
                errores.append(f"{prefijo} ({cid}).tor '{tor}' debe ser un nodo de capa 'tor'")

            servidores = cluster.get("servidores")
            if not isinstance(servidores, list) or len(servidores) < 1:
                errores.append(f"{prefijo} ({cid}) debe tener al menos un servidor")
                servidores = []

            for j, servidor in enumerate(servidores):
                prefijo_s = f"{prefijo}.servidor[{j}]"
                if not isinstance(servidor, dict):
                    errores.append(f"{prefijo_s} debe ser un objeto (recibido: {type(servidor).__name__})")
                    continue

                sid = Validador._id_o_none(f"{prefijo_s}.id", servidor.get("id"), errores)
                if sid is not None:
                    if sid in ids_nodos:
                        errores.append(f"id de servidor '{sid}' coincide con un id de nodo")
                    elif sid in ids_servidores:
                        errores.append(f"id de servidor duplicado: '{sid}'")
                    else:
                        ids_servidores.add(sid)

                try:
                    Validador.validar_rango(
                        f"{prefijo_s} ({sid}).capacidad", servidor.get("capacidad"), minimo=1, maximo=1024, entero=True
                    )
                except ErrorValidacion as e:
                    errores.append(str(e))

                Validador._validar_positivo(f"{prefijo_s} ({sid}).tasa_servicio", servidor.get("tasa_servicio"), errores)
                Validador._validar_posicion_2d(f"{prefijo_s} ({sid}).posicion", servidor.get("posicion"), errores)

        return ids_clusteres

    @staticmethod
    def _validar_paquetes_prueba(paquetes: Any, ids_clusteres: set[str], errores: list[str]) -> None:
        if not isinstance(paquetes, list):
            errores.append(f"paquetes_prueba debe ser una lista (recibido: {type(paquetes).__name__})")
            return
        ids_paquetes: set[str] = set()
        for i, paquete in enumerate(paquetes):
            prefijo = f"paquete_prueba[{i}]"
            if not isinstance(paquete, dict):
                errores.append(f"{prefijo} debe ser un objeto (recibido: {type(paquete).__name__})")
                continue

            pid = Validador._id_o_none(f"{prefijo}.id", paquete.get("id"), errores)
            if pid is not None:
                if pid in ids_paquetes:
                    errores.append(f"id de paquete de prueba duplicado: '{pid}'")
                else:
                    ids_paquetes.add(pid)

            try:
                Validador.validar_rango(
                    f"{prefijo} ({pid}).requerimiento", paquete.get("requerimiento"), minimo=1, maximo=1024, entero=True
                )
            except ErrorValidacion as e:
                errores.append(str(e))

            try:
                Validador.validar_rango(
                    f"{prefijo} ({pid}).prioridad", paquete.get("prioridad"), minimo=1, maximo=10, entero=True
                )
            except ErrorValidacion as e:
                errores.append(str(e))

            destino_cluster = paquete.get("destino_cluster")
            if destino_cluster not in ids_clusteres:
                errores.append(f"{prefijo} ({pid}).destino_cluster '{destino_cluster}' no existe entre los clusteres")

    @staticmethod
    def _validar_parametros(parametros: Any, errores: list[str]) -> None:
        """Cada seccion conocida debe ser un objeto de numeros finitos; los rangos finos los
        valida el constructor de cada modelo al recibirlos."""
        if not isinstance(parametros, dict):
            errores.append(f"parametros debe ser un objeto (recibido: {type(parametros).__name__})")
            return
        for seccion, valores in parametros.items():
            if seccion not in SECCIONES_PARAMETROS:
                errores.append(f"parametros.{seccion} no es una seccion valida, debe ser una de {SECCIONES_PARAMETROS}")
                continue
            if not isinstance(valores, dict):
                errores.append(f"parametros.{seccion} debe ser un objeto (recibido: {type(valores).__name__})")
                continue
            for clave, valor in valores.items():
                try:
                    Validador.validar_rango(f"parametros.{seccion}.{clave}", valor)
                except ErrorValidacion as e:
                    errores.append(str(e))

    @staticmethod
    def _id_o_none(nombre: str, valor: Any, errores: list[str]) -> str | None:
        try:
            return Validador.validar_id(nombre, valor)
        except ErrorValidacion as e:
            errores.append(str(e))
            return None

    @staticmethod
    def _validar_positivo(nombre: str, valor: Any, errores: list[str]) -> None:
        """Valida que `valor` sea un numero estrictamente mayor a 0."""
        try:
            numero = Validador.validar_rango(nombre, valor, minimo=0)
            if numero == 0:
                errores.append(f"{nombre} debe ser mayor a 0 (recibido: {valor})")
        except ErrorValidacion as e:
            errores.append(str(e))

    @staticmethod
    def _validar_posicion_2d(nombre: str, valor: Any, errores: list[str]) -> None:
        if (
            not isinstance(valor, (list, tuple))
            or len(valor) != 2
            or not all(isinstance(c, (int, float)) and not isinstance(c, bool) for c in valor)
        ):
            errores.append(f"{nombre} debe ser una lista de 2 numeros (recibido: {valor!r})")

    @staticmethod
    def _a_numero_finito(nombre: str, valor: Any) -> float:
        if valor is None or isinstance(valor, bool):
            raise ErrorValidacion(f"{nombre} debe ser un numero (recibido: {valor!r})")
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            raise ErrorValidacion(f"{nombre} debe ser un numero (recibido: {valor!r})") from None
        if math.isnan(numero) or math.isinf(numero):
            raise ErrorValidacion(f"{nombre} debe ser un numero finito (recibido: {valor!r})")
        return numero

    @staticmethod
    def _mensaje_fuera_de_rango(nombre: str, valor: Any, minimo: float | None, maximo: float | None) -> str:
        if minimo is not None and maximo is not None:
            return f"{nombre} debe estar entre {minimo} y {maximo} (recibido: {valor})"
        if minimo is not None:
            return f"{nombre} debe estar entre {minimo} y infinito (recibido: {valor})"
        if maximo is not None:
            return f"{nombre} debe estar entre -infinito y {maximo} (recibido: {valor})"
        return f"{nombre} fuera de rango (recibido: {valor})"
