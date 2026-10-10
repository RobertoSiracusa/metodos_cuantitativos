"""
Punto de Entrada - Tarea 5, Metodos Cuantitativos
(Modelo de tamano de la fuerza de trabajo, Programacion Dinamica)
Universidad Jose Antonio Paez - Metodos Cuantitativos

Uso:
    python3 main.py                                # problema de la tarea (demandas 5,7,8,4,6)
    python3 main.py --demandas "5,7,8,4,6"          # otras demandas
    python3 main.py --inicial 2                     # otra fuerza inicial x0
    python3 main.py --excedente 300 --fijo 400 --variable 200 --despido 0
    python3 main.py --datos otros.json
    python3 main.py --sin-exportar                  # no guardar el reporte en outputs/
"""
import argparse
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.fuerza_trabajo import ModeloFuerzaTrabajoDP, PoliticaCostos
from src.services.reporter import generar_reporte, guardar_reporte

DATOS_POR_DEFECTO = os.path.join(BASE_DIR, "datos", "fuerza_trabajo.json")


def _parsear_demandas(texto: str):
    """Convierte 'a,b,c' en una lista de enteros; levanta ValueError con un mensaje claro si falla."""
    partes = [p.strip() for p in texto.split(",")]
    try:
        return [int(p) for p in partes]
    except ValueError:
        raise ValueError(
            f"--demandas debe ser una lista de enteros separados por coma, se recibio: {texto!r}"
        )


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Modelo de tamano de la fuerza de trabajo (programacion dinamica por etapas)."
    )
    p.add_argument("--datos", default=DATOS_POR_DEFECTO, help="JSON con demandas y costos")
    p.add_argument("--demandas", default=None, help="demandas separadas por coma, ej: 5,7,8,4,6")
    p.add_argument("--inicial", type=int, default=None, help="fuerza de trabajo inicial x0")
    p.add_argument("--excedente", type=float, default=None, help="costo por trabajador excedente por semana")
    p.add_argument("--fijo", type=float, default=None, help="costo fijo de contratacion")
    p.add_argument("--variable", type=float, default=None, help="costo variable de contratacion por trabajador")
    p.add_argument("--despido", type=float, default=None, help="costo de despido por trabajador")
    p.add_argument("--sin-exportar", action="store_true", help="no guardar el reporte en outputs/")
    args = p.parse_args(argv)

    try:
        with open(args.datos, encoding="utf-8") as f:
            d = json.load(f)

        demandas = _parsear_demandas(args.demandas) if args.demandas is not None else d["demandas"]
        fuerza_inicial = args.inicial if args.inicial is not None else d["fuerza_inicial"]

        politica = PoliticaCostos(
            costo_excedente_unitario=args.excedente if args.excedente is not None else d["costo_excedente"],
            costo_fijo_contratacion=args.fijo if args.fijo is not None else d["costo_fijo_contratacion"],
            costo_variable_contratacion=args.variable if args.variable is not None else d["costo_variable_contratacion"],
            costo_despido_unitario=args.despido if args.despido is not None else d["costo_despido"],
        )
        modelo = ModeloFuerzaTrabajoDP(
            requerimientos=demandas,
            politica=politica,
            fuerza_inicial=fuerza_inicial,
        )
        modelo.resolver()
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    texto = generar_reporte(modelo)
    print(texto)
    if not args.sin_exportar:
        ruta = guardar_reporte(texto, os.path.join(BASE_DIR, "outputs"))
        print(f"Reporte guardado en: {ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
