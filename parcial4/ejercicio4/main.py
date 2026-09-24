"""
Punto de Entrada — Ejercicio 4, Parcial IV (Problema de la mochila 0/1)
Universidad Jose Antonio Paez — Metodos Cuantitativos

Uso:
    python3 main.py                         # problema del parcial (capacidad 50 kg)
    python3 main.py --capacidad 60          # otra capacidad
    python3 main.py --datos otros.json      # otros objetos
"""
import argparse
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.knapsack import ModeloMochila
from src.services.reporter import generar_reporte, guardar_reporte

DATOS_POR_DEFECTO = os.path.join(BASE_DIR, "datos", "objetos.json")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Problema de la mochila 0/1.")
    p.add_argument("--datos", default=DATOS_POR_DEFECTO, help="JSON con pesos, valores y capacidad")
    p.add_argument("--capacidad", type=int, default=None, help="capacidad en kg (por defecto la del JSON, 50)")
    p.add_argument("--sin-exportar", action="store_true", help="no guardar el reporte en outputs/")
    args = p.parse_args(argv)

    try:
        with open(args.datos, encoding="utf-8") as f:
            d = json.load(f)
        capacidad = args.capacidad if args.capacidad is not None else d["capacidad"]
        modelo = ModeloMochila(d["pesos"], d["valores"], capacidad)
        dp, ml, voraz = modelo.resolver_dp(), modelo.resolver_milp(), modelo.resolver_voraz()
    except (OSError, KeyError, ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    texto = generar_reporte(modelo, dp, ml, voraz)
    print(texto)
    if not args.sin_exportar:
        ruta = guardar_reporte(texto, os.path.join(BASE_DIR, "outputs"))
        print(f"Reporte guardado en: {ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
