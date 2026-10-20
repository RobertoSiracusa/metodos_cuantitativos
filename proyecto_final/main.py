"""Punto de entrada del simulador.

Fase F1: solo esta disponible --modulo m1 (ruta mas corta + mochila sobre datos
estaticos). Los demas modos (--modulo m2, GUI, SimPy) se agregan en fases posteriores.
"""

from __future__ import annotations

import argparse
import math
import sys

from src.core.programacion_dinamica.mochila import Mochila
from src.core.programacion_dinamica.ruta_mas_corta import RutaMasCorta
from src.utils.config import Configuracion
from src.utils.validators import ErrorValidacion


def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simulador de optimizacion para redes de centros de datos")
    parser.add_argument("--modulo", choices=["m1", "m2"], default=None, help="Modulo a ejecutar")
    parser.add_argument("--escenario", default=None, help="Ruta a un escenario JSON (default: el escenario por defecto)")
    parser.add_argument("--cluster", default="C1", help="Id del cluster a usar en el modulo m1 (default: C1)")
    parser.add_argument(
        "--fallar",
        action="append",
        default=[],
        metavar="NODO",
        help="Id de un nodo a marcar como caido antes de resolver (repetible)",
    )
    return parser


def _formatear_costo(costo: float) -> str:
    return "inf" if math.isinf(costo) else f"{costo:.4f}"


def _ejecutar_modulo_m1(args: argparse.Namespace) -> None:
    configuracion = Configuracion.desde_archivo(args.escenario) if args.escenario else Configuracion.por_defecto()
    red = configuracion.construir_red()

    for nodo_id in args.fallar:
        try:
            nodo = red.nodo(nodo_id)
        except KeyError:
            raise ErrorValidacion(f"el nodo a fallar '{nodo_id}' no existe") from None
        nodo.fallar()

    cluster = red.cluster(args.cluster)
    origen = next(r.id for r in red.routers if r.capa == "gateway")
    destino = cluster.tor_id

    modelo_ruta = RutaMasCorta(red)
    resultado_ruta = modelo_ruta.resolver(origen, destino)

    print("Tabla de programacion dinamica (ruta mas corta):")
    print(f"{'etapa':<6}{'nodo':<8}{'f':<12}{'siguiente':<10}")
    for etapa in sorted(modelo_ruta.tabla):
        for nodo_id, (f, siguiente) in modelo_ruta.tabla[etapa].items():
            print(f"{etapa:<6}{nodo_id:<8}{_formatear_costo(f):<12}{siguiente or '-':<10}")
    print()

    if resultado_ruta.existe:
        camino = " -> ".join(resultado_ruta.camino)
        print(f"Ruta {origen} -> {destino}: {camino} (costo {resultado_ruta.costo:.4f})")
    else:
        print(f"Ruta {origen} -> {destino}: no existe")
    print()

    primer_servidor = cluster.servidores[0]
    paquetes_cluster = [p for p in configuracion.construir_paquetes() if p.destino_cluster == cluster.id]

    modelo_mochila = Mochila(primer_servidor.capacidad)
    resultado_mochila = modelo_mochila.resolver(paquetes_cluster)

    print(f"Mochila para cluster {cluster.id} (capacidad {primer_servidor.capacidad}):")
    ids_seleccionados = ", ".join(p.id for p in resultado_mochila.seleccionados) or "(ninguno)"
    print(f"Seleccionados: {ids_seleccionados}")
    print(f"Valor total: {resultado_mochila.valor_total}")
    print(f"Peso total: {resultado_mochila.peso_total}")


def _ejecutar_modulo_m2() -> None:
    print("El modulo m2 (optimizacion no lineal: termico, gradiente, Lagrange) llega en fases posteriores (F2/F4).")


def main(argv: list[str] | None = None) -> int:
    parser = _construir_parser()
    args = parser.parse_args(argv)

    try:
        if args.modulo == "m1":
            _ejecutar_modulo_m1(args)
        else:
            _ejecutar_modulo_m2()
    except ErrorValidacion as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
