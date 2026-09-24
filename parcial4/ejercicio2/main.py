"""
Punto de Entrada — Ejercicio 2, Parcial IV (Ramificacion y Acotamiento)
Universidad Jose Antonio Paez — Metodos Cuantitativos

Uso:
    python3 main.py                          # resuelve el problema del parcial
    python3 main.py --datos otro.json        # resuelve otro problema de maximizacion
    python3 main.py --sin-exportar           # no escribe outputs/
"""
import argparse
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.branch_and_bound import ModeloBranchAndBound
from src.services.reporter import generar_reporte, guardar_reporte

DATOS_POR_DEFECTO = os.path.join(BASE_DIR, "datos", "problema.json")


def cargar_datos(ruta: str) -> ModeloBranchAndBound:
    with open(ruta, encoding="utf-8") as f:
        d = json.load(f)
    return ModeloBranchAndBound(d["c"], d["A"], d["b"])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Ramificacion y acotamiento para PL entera (maximizacion, <=).")
    p.add_argument("--datos", default=DATOS_POR_DEFECTO, help="JSON con c, A y b (por defecto datos/problema.json)")
    p.add_argument("--sin-exportar", action="store_true", help="no guardar el reporte en outputs/")
    args = p.parse_args(argv)

    try:
        modelo = cargar_datos(args.datos)
    except (OSError, KeyError, ValueError) as e:
        print(f"Error al leer los datos: {e}", file=sys.stderr)
        return 1

    resultado = modelo.resolver()
    texto = generar_reporte(modelo, resultado)
    print(texto)
    if not args.sin_exportar:
        ruta = guardar_reporte(texto, os.path.join(BASE_DIR, "outputs"))
        print(f"Reporte guardado en: {ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
