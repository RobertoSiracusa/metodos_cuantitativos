"""
Punto de Entrada — Ejercicio 3, Parcial IV (Ubicacion de estaciones / Set Covering)
Universidad Jose Antonio Paez — Metodos Cuantitativos

Uso:
    python3 main.py                                  # problema del parcial (40 min, ida y vuelta)
    python3 main.py --sentido estacion_a_ciudad      # otro criterio de cobertura
    python3 main.py --limite 30                      # otro limite de tiempo
    python3 main.py --datos otra_tabla.json          # otra tabla de tiempos
"""
import argparse
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.set_covering import SENTIDOS, ModeloCubrimiento
from src.services.reporter import generar_reporte, guardar_reporte

DATOS_POR_DEFECTO = os.path.join(BASE_DIR, "datos", "tiempos.json")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Minimo de estaciones para cubrir todas las ciudades (set covering).")
    p.add_argument("--datos", default=DATOS_POR_DEFECTO, help="JSON con la tabla 'tiempos' (por defecto datos/tiempos.json)")
    p.add_argument("--limite", type=float, default=None, help="minutos maximos (por defecto el del JSON, 40)")
    p.add_argument("--sentido", choices=list(SENTIDOS), default="ida_vuelta", help="como se mide el limite")
    p.add_argument("--sin-exportar", action="store_true", help="no guardar el reporte en outputs/")
    args = p.parse_args(argv)

    try:
        with open(args.datos, encoding="utf-8") as f:
            d = json.load(f)
        limite = args.limite if args.limite is not None else d.get("limite", 40)
        modelo = ModeloCubrimiento(d["tiempos"], limite, args.sentido)
        resultado = modelo.resolver()
    except (OSError, KeyError, ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    texto = generar_reporte(modelo, resultado)
    print(texto)
    if not args.sin_exportar:
        ruta = guardar_reporte(texto, os.path.join(BASE_DIR, "outputs"))
        print(f"Reporte guardado en: {ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
