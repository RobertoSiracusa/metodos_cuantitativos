"""Punto de entrada principal para la simulacion de reaccion nuclear (SimPy + Pygame)."""

import argparse
import sys
from src.constants import DEFAULT_ROD_INSERTION
from src.engine.controller import NuclearController


def parse_args():
    parser = argparse.ArgumentParser(
        description="Simulacion de Reaccion Nuclear y Dinamica de Reactor (SimPy + Pygame) — Metodos Cuantitativos"
    )
    parser.add_argument(
        "--rods",
        type=float,
        default=DEFAULT_ROD_INSERTION,
        help=f"Nivel inicial de insercion de barras de control (0.0 a 1.0, default: {DEFAULT_ROD_INSERTION})",
    )
    parser.add_argument(
        "--enrichment",
        type=float,
        default=0.20,
        help="Fraccion de enriquecimiento de Uranio-235 (ej. 0.05 para comercial, 0.20 para investigacion)",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Multiplicador de velocidad de simulacion (ej. 1.0, 2.0, 4.0)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Ejecutar en modo sin ventana grafica para pruebas cuantitativas y CI",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Duracion maxima en segundos de tiempo simulado",
    )
    return parser.parse_args()


def print_banner(args):
    print("=" * 78)
    print("  UNIVERSIDAD JOSE ANTONIO PAEZ — FACULTAD DE INGENIERIA")
    print("  ESCUELA DE COMPUTACION — METODOS CUANTITATIVOS")
    print("  SIMULACION DE REACCION NUCLEAR EN CADENA Y REACTOR (SIMPY + PYGAME)")
    print("=" * 78)
    print(f"  Parametros iniciales: Enriquecimiento U-235={args.enrichment*100:.1f}% | Barras={args.rods*100:.1f}%")
    print("  Controles del operador de reactor:")
    print("    [ESPACIO]        : Inyectar pulso de neutrones fuente (Cf-252)")
    print("    [ARRIBA/ABAJO]   : Extraer / Insertar barras de control (+/- reactividad)")
    print("    [S]              : SCRAM de Emergencia (caida gravitacional al 100%)")
    print("    [B]              : Alternar bombas principales de refrigeracion")
    print("    [P]              : Pausar / Reanudar simulacion")
    print("    [1, 2, 3, 4]     : Velocidad temporal (1x, 2x, 4x, 8x)")
    print("    [R]              : Reiniciar nucleo a combustible fresco")
    print("    [ESC]            : Salir y desplegar reporte cuantitativo final")
    print("=" * 78)


def main():
    args = parse_args()

    if not args.headless:
        print_banner(args)
    else:
        print(f"[MODO HEADLESS] Iniciando simulacion nuclear (Enriquecimiento: {args.enrichment*100:.1f}%)...")

    controller = NuclearController(
        headless=args.headless,
        speed_multiplier=args.speed,
        enrichment=args.enrichment,
        initial_rod_insertion=args.rods,
    )

    report = controller.run(max_sim_time=args.duration)

    print("\n" + "=" * 78)
    print("  REPORTE CUANTITATIVO DE OPERACION DEL REACTOR NUCLEAR")
    print("=" * 78)
    for k, v in report.items():
        print(f"  {k:38s}: {v}")
    print("=" * 78)


if __name__ == "__main__":
    main()
