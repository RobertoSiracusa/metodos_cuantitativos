"""Punto de entrada para la simulacion de estacion de servicio (SimPy + Pygame)."""

import argparse
import sys
from src.constants import DEFAULT_SERVERS, DEFAULT_LAMBDA, DEFAULT_MU
from src.engine.controller import StationController


def parse_args():
    parser = argparse.ArgumentParser(
        description="Simulacion de Estacion de Gasolina con Lineas de Espera (SimPy + Pygame) — Metodos Cuantitativos"
    )
    parser.add_argument(
        "--pumps",
        type=int,
        default=DEFAULT_SERVERS,
        help=f"Numero de servidores / bombas de gasolina (default: {DEFAULT_SERVERS})",
    )
    parser.add_argument(
        "--lamb",
        type=float,
        default=DEFAULT_LAMBDA,
        help=f"Tasa de arribos lambda (vehiculos por minuto) (default: {DEFAULT_LAMBDA})",
    )
    parser.add_argument(
        "--mu",
        type=float,
        default=DEFAULT_MU,
        help=f"Tasa de servicio mu por bomba (vehiculos por minuto) (default: {DEFAULT_MU})",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Multiplicador de velocidad de simulacion (ej. 1.0, 2.0, 5.0)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Ejecutar en modo sin ventana para pruebas y benchmarks cuantitativos",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Duracion maxima de ejecucion en segundos de tiempo simulado",
    )
    return parser.parse_args()


def print_banner(args):
    print("=" * 76)
    print("  UNIVERSIDAD JOSE ANTONIO PAEZ — FACULTAD DE INGENIERIA")
    print("  ESCUELA DE COMPUTACION — METODOS CUANTITATIVOS")
    print("  SIMULACION DE LINEA DE ESPERA EN ESTACION DE SERVICIO (SIMPY + PYGAME)")
    print("=" * 76)
    print(f"  Parametros iniciales: Bombas c={args.pumps} | lambda={args.lamb}/min | mu={args.mu}/min")
    print("  Controles interactivos:")
    print("    [ESPACIO]        : Pausar / Reanudar simulacion")
    print("    [1, 2, 3, 4]     : Ajustar velocidad (1x, 2x, 5x, 10x)")
    print("    [+] / [-]        : Modificar tasa de llegada lambda (+/- 0.5)")
    print("    [C]              : Despachar camion cisterna de reabastecimiento")
    print("    [R]              : Reiniciar simulacion")
    print("    [ESC]            : Finalizar y desplegar reporte analitico final")
    print("=" * 76)


def main():
    args = parse_args()

    if not args.headless:
        print_banner(args)
    else:
        print(f"[MODO HEADLESS] Iniciando simulacion M/M/{args.pumps} a maxima velocidad...")

    controller = StationController(
        headless=args.headless,
        speed_multiplier=args.speed,
        num_pumps=args.pumps,
        arrival_rate=args.lamb,
        service_rate=args.mu,
    )

    report = controller.run(max_sim_time=args.duration)

    print("\n" + "=" * 76)
    print("  REPORTE CUANTITATIVO COMPARATIVO (TEORIA M/M/c vs SIMULACION)")
    print("=" * 76)
    for k, v in report.items():
        print(f"  {k:35s}: {v}")
    print("=" * 76)


if __name__ == "__main__":
    main()
