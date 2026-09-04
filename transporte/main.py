"""Punto de entrada para la simulacion de transporte y optimizacion de rutas (Pygame)."""

import argparse
import sys
from src.engine.controller import TransportController


def parse_args():
    parser = argparse.ArgumentParser(
        description="Optimizacion de Redes de Transporte & Asignacion de Flota en Pygame — Metodos Cuantitativos"
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        choices=["dijkstra", "astar"],
        default="dijkstra",
        help="Algoritmo de camino minimo inicial ('dijkstra' o 'astar') (default: dijkstra)",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Multiplicador de velocidad de simulacion (ej. 1.0, 2.0, 5.0)",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Iniciar en modo de generacion y despacho automatico continuo de pedidos",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Ejecutar en modo sin ventana para benchmarks, analisis cuantitativo y tests",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Duracion maxima en segundos de tiempo simulado (util en modo headless)",
    )
    parser.add_argument(
        "--origin",
        type=str,
        default="VAL",
        help="Codigo de nodo de origen inicial (ej. VAL, PTO, MAR) (default: VAL)",
    )
    parser.add_argument(
        "--dest",
        type=str,
        default="CCS",
        help="Codigo de nodo de destino inicial (ej. CCS, GUA, CAG) (default: CCS)",
    )
    parser.add_argument(
        "--cargo",
        type=float,
        default=14.0,
        help="Carga inicial en toneladas a despachar en la ruta seleccionada (default: 14.0)",
    )
    return parser.parse_args()


def print_banner(args):
    print("=" * 76)
    print("  UNIVERSIDAD JOSE ANTONIO PAEZ — FACULTAD DE INGENIERIA")
    print("  ESCUELA DE COMPUTACION — METODOS CUANTITATIVOS")
    print("  SISTEMA DE ASIGNACION DE FLOTA & RUTAS OPTIMAS (PYGAME + GRAFOS)")
    print("=" * 76)
    print(f"  Configuracion: Algoritmo={args.algorithm.upper()} | Vel={args.speed}x | Modo={'AUTO' if args.auto else 'MANUAL'}")
    print(f"  Ruta inicial seleccionada: [{args.origin}] -> [{args.dest}] ({args.cargo}t)")
    print("  Controles interactivos:")
    print("    [CLIC EN NODO]   : Seleccionar Origen y Destino en la red vial")
    print("    [D]              : Despachar pedido con camion mas optimo")
    print("    [A]              : Alternar despacho automatico continuo (ON/OFF)")
    print("    [T]              : Alternar algoritmo de ruta (Dijkstra <-> A*)")
    print("    [1, 2, 3, 4]     : Ajustar velocidad de simulacion (1x, 2x, 5x, 10x)")
    print("    [ESPACIO]        : Pausar / Reanudar simulacion")
    print("    [R]              : Reiniciar simulacion")
    print("    [ESC]            : Salir y desplegar reporte analitico final")
    print("=" * 76)


def main():
    args = parse_args()

    if not args.headless:
        print_banner(args)
    else:
        print(f"[MODO HEADLESS] Ejecutando optimizacion cuantitativa ({args.algorithm.upper()})...")

    controller = TransportController(
        headless=args.headless,
        speed_multiplier=args.speed,
        algorithm=args.algorithm,
        auto_mode=args.auto,
    )

    # Configurar seleccion inicial si fue especificada
    orig_node = controller.sim.graph.get_node(args.origin.upper())
    dest_node = controller.sim.graph.get_node(args.dest.upper())
    if orig_node and dest_node and orig_node.id != dest_node.id:
        controller.sim.selected_origin = orig_node
        controller.sim.selected_dest = dest_node
        controller.sim.update_preview_path()

    report = controller.run(max_sim_time=args.duration)

    print("\n" + "=" * 76)
    print("  REPORTE LOGISTICO CUANTITATIVO FINAL")
    print("=" * 76)
    for k, v in report.items():
        print(f"  {k:35s}: {v}")
    print("=" * 76)


if __name__ == "__main__":
    main()
