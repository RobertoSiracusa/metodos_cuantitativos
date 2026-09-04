"""Punto de entrada para la simulacion de automercado y lineas de espera (SimPy + Pygame)."""

import argparse
import sys
from src.constants import (
    DEFAULT_REGISTERS,
    DEFAULT_LAMBDA,
    DEFAULT_MU,
    QueueMode,
)
from src.engine.controller import MarketController


def parse_args():
    parser = argparse.ArgumentParser(
        description="Simulacion de Automercado con Modelos de Lineas de Espera (SimPy + Pygame) — Metodos Cuantitativos"
    )
    parser.add_argument(
        "--registers",
        "-c",
        type=int,
        default=DEFAULT_REGISTERS,
        help=f"Numero de cajas registradoras abiertas (default: {DEFAULT_REGISTERS})",
    )
    parser.add_argument(
        "--lamb",
        "-l",
        type=float,
        default=DEFAULT_LAMBDA,
        help=f"Tasa de arribos lambda (clientes por minuto) (default: {DEFAULT_LAMBDA})",
    )
    parser.add_argument(
        "--mu",
        "-m",
        type=float,
        default=DEFAULT_MU,
        help=f"Tasa de servicio mu por caja (clientes por minuto) (default: {DEFAULT_MU})",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Multiplicador inicial de velocidad de simulacion (ej. 1.0, 2.0, 5.0)",
    )
    parser.add_argument(
        "--queue-mode",
        choices=["parallel", "single"],
        default="parallel",
        help="Disciplina de cola inicial: 'parallel' (colas por caja) o 'single' (cola unica central M/M/c)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Ejecutar en modo sin ventana grafica para analisis cuantitativo y benchmarks",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Duracion maxima en segundos de tiempo simulado",
    )
    return parser.parse_args()


def print_banner(args, queue_mode_val):
    print("=" * 78)
    print("  UNIVERSIDAD JOSE ANTONIO PAEZ — FACULTAD DE INGENIERIA")
    print("  ESCUELA DE COMPUTACION — METODOS CUANTITATIVOS")
    print("  SIMULACION DE AUTOMERCADO Y MODELOS DE LINEAS DE ESPERA (SIMPY + PYGAME)")
    print("=" * 78)
    print(f"  Parametros: Cajas c={args.registers} | lambda={args.lamb}/min | mu={args.mu}/min")
    print(f"  Disciplina de cola inicial: {queue_mode_val.value}")
    print("  Controles interactivos en ejecucion:")
    print("    [ESPACIO]        : Pausar / Reanudar simulacion")
    print("    [1, 2, 3, 4]     : Velocidad (1x, 2x, 5x, 10x)")
    print("    [+] / [-]        : Ajustar tasa de llegada lambda (+/- 0.5)")
    print("    [A] / [Z]        : Abrir / Cerrar cajas registradoras")
    print("    [M]              : Alternar entre Cola Unica (M/M/c) y Colas Paralelas")
    print("    [R]              : Reiniciar simulacion")
    print("    [ESC]            : Finalizar sesion y generar reporte cuantitativo")
    print("=" * 78)


def main():
    args = parse_args()
    queue_mode = QueueMode.SINGLE if args.queue_mode == "single" else QueueMode.PARALLEL

    if not args.headless:
        print_banner(args, queue_mode)
    else:
        print(f"[MODO HEADLESS] Simulando automercado con c={args.registers} cajas ({queue_mode.value})...")

    controller = MarketController(
        headless=args.headless,
        speed_multiplier=args.speed,
        num_registers=args.registers,
        arrival_rate=args.lamb,
        service_rate=args.mu,
        queue_mode=queue_mode,
    )

    report = controller.run(max_sim_time=args.duration)

    print("\n" + "=" * 78)
    print("  REPORTE CUANTITATIVO COMPARATIVO (TEORIA vs SIMULACION SIMPY)")
    print("=" * 78)
    for k, v in report.items():
        print(f"  {k:35s}: {v}")
    print("=" * 78)


if __name__ == "__main__":
    main()
