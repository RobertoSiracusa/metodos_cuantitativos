"""Punto de entrada principal para la simulacion del juego Snake (SimPy + Pygame)."""

import argparse
import sys
from src.constants import ControlMode
from src.engine.controller import GameController


def parse_args():
    parser = argparse.ArgumentParser(
        description="Simulacion del juego Snake con SimPy y Pygame (POO) - Metodos Cuantitativos"
    )
    parser.add_argument(
        "--mode",
        choices=["manual", "auto"],
        default="manual",
        help="Modo de control inicial: 'manual' (jugador) o 'auto' (agente IA)",
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
        help="Ejecutar en modo sin ventana para recoleccion rapida de datos y pruebas",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Duracion maxima en segundos de tiempo simulado",
    )
    return parser.parse_args()


def print_banner():
    print("=" * 70)
    print("  UNIVERSIDAD JOSE ANTONIO PAEZ - FACULTAD DE INGENIERIA")
    print("  ESCUELA DE COMPUTACION - METODOS CUANTITATIVOS")
    print("  SIMULACION DE SISTEMA DISCRETO: JUEGO SNAKE (SIMPY + PYGAME)")
    print("=" * 70)
    print("  Controles en pantalla:")
    print("    [Flechas / WASD] : Control manual de direccion")
    print("    [ESPACIO]        : Pausar / Reanudar simulacion")
    print("    [M]              : Alternar modo (Manual / Auto IA)")
    print("    [1, 2, 3]        : Velocidad (1x, 2x, 4x)")
    print("    [R]              : Reiniciar simulacion")
    print("    [ESC]            : Salir")
    print("=" * 70)


def main():
    args = parse_args()

    mode = ControlMode.AUTO_AI if args.mode == "auto" else ControlMode.MANUAL

    if not args.headless:
        print_banner()
    else:
        print("[MODO HEADLESS] Iniciando simulacion cuantitativa automatizada...")

    controller = GameController(
        headless=args.headless,
        control_mode=mode,
        speed_multiplier=args.speed,
    )

    summary = controller.run(max_sim_time=args.duration)

    print("\n" + "=" * 70)
    print("  REPORTE CUANTITATIVO DE LA SESION DE SIMULACION")
    print("=" * 70)
    for k, v in summary.items():
        print(f"  {k:30s}: {v}")
    print("=" * 70)


if __name__ == "__main__":
    main()
