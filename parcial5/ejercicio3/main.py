"""
Punto de Entrada — Ejercicio 3, Parcial V (Problema de volumen de carga)
Universidad Jose Antonio Paez — Metodos Cuantitativos

Uso:
    python3 main.py                         # problema del parcial (capacidad 10 kg)
    python3 main.py --capacidad 14          # otra capacidad
    python3 main.py --datos otros.json      # otros productos
"""
import argparse
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.volumen_carga import VolumenCarga
from src.services.reporter import generar_reporte, guardar_reporte

DATOS_POR_DEFECTO = os.path.join(BASE_DIR, "datos", "productos.json")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Problema de volumen de carga (mochila 0/1 por etapas).")
    p.add_argument("--datos", default=DATOS_POR_DEFECTO, help="JSON con productos (nombre, peso, precio) y capacidad")
    p.add_argument("--capacidad", type=int, default=None, help="capacidad en kg (por defecto la del JSON, 10)")
    p.add_argument("--sin-exportar", action="store_true", help="no guardar el reporte en outputs/")
    args = p.parse_args(argv)

    try:
        with open(args.datos, encoding="utf-8") as f:
            d = json.load(f)
        capacidad = args.capacidad if args.capacidad is not None else d["capacidad"]
        nombres = [prod["nombre"] for prod in d["productos"]]
        pesos = [prod["peso"] for prod in d["productos"]]
        precios = [prod["precio"] for prod in d["productos"]]
        modelo = VolumenCarga(nombres, pesos, precios, capacidad)
        etapas = modelo.tablas_etapas()
        solucion = modelo.resolver()
        ml = modelo.resolver_milp()
        voraz = modelo.resolver_voraz()
        enumeracion = modelo.enumerar()
        alternativos = modelo.optimos_alternativos()
    except (OSError, KeyError, ValueError, RuntimeError, json.JSONDecodeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    texto = generar_reporte(modelo, etapas, solucion, ml, voraz, enumeracion, alternativos)
    print(texto)
    if not args.sin_exportar:
        ruta = guardar_reporte(texto, os.path.join(BASE_DIR, "outputs"))
        print(f"Reporte guardado en: {ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
