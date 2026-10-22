"""Punto de Entrada - Tarea 6, Metodos Cuantitativos
Programacion No Lineal (Modelos de Optimizacion Clásica y Numérica)
Universidad Jose Antonio Paez - Facultad de Ingenieria

Uso:
    python3 main.py                        # Resuelve todos los problemas (1 al 5) y exporta
    python3 main.py --problema 1           # Ejecuta solo el problema 1
    python3 main.py --problema 3 --alfa 0.2  # Problema 3 con tasa de aprendizaje personalizada
    python3 main.py --sin-exportar         # Ejecuta sin guardar el reporte en outputs/
    python3 main.py --datos ruta.json      # Carga configuraciones desde archivo externo
"""

from __future__ import annotations

import argparse
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.base import ErrorValidacion
from src.core.problema1_sin_restricciones import OptimizadorSinRestricciones
from src.core.problema2_lagrange import OptimizadorLagrangeRectangulo
from src.core.problema3_gradiente import OptimizadorGradienteAscenso
from src.core.problema4_kkt import OptimizadorKKTMultiplesRestricciones
from src.core.problema5_cilindro import OptimizadorCilindroFisico
from src.services.reporter import (
    formatear_problema_1,
    formatear_problema_2,
    formatear_problema_3,
    formatear_problema_4,
    formatear_problema_5,
    generar_reporte_completo,
    guardar_reporte,
)

DATOS_POR_DEFECTO = os.path.join(BASE_DIR, "datos", "problemas.json")


def _cargar_configuracion(ruta: str) -> dict:
    if not os.path.exists(ruta):
        return {}
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Tarea 6 - Programacion No Lineal (Calculo Multivariable, Lagrange, Gradiente, KKT y Modelado Fisico)."
    )
    parser.add_argument(
        "--problema",
        type=int,
        choices=[1, 2, 3, 4, 5],
        default=None,
        help="Numero del problema a ejecutar (1 a 5). Si no se especifica, resuelve todos.",
    )
    parser.add_argument("--datos", default=DATOS_POR_DEFECTO, help="Ruta al JSON de configuracion.")
    parser.add_argument("--sin-exportar", action="store_true", help="No genera archivo en outputs/.")

    # Parametros especificos opcionales
    parser.add_argument("--perimetro", type=float, default=None, help="Perimetro para el problema 2.")
    parser.add_argument("--alfa", type=float, default=None, help="Tasa de aprendizaje para el gradiente (problema 3).")
    parser.add_argument("--iteraciones", type=int, default=None, help="Iteraciones max para el gradiente (problema 3).")
    parser.add_argument("--capacidad", type=float, default=None, help="Capacidad maxima para el problema 4.")
    parser.add_argument("--volumen", type=float, default=None, help="Volumen del cilindro para el problema 5.")

    args = parser.parse_args(argv)

    try:
        config = _cargar_configuracion(args.datos)

        # Instanciacion de modelos con parametros de config o CLI
        c1 = config.get("problema1", {})
        opt1 = OptimizadorSinRestricciones(
            a=c1.get("coef_x2", 1.0),
            b=c1.get("coef_y2", 1.0),
            c=c1.get("coef_x", -4.0),
            d=c1.get("coef_y", -6.0),
            e=c1.get("constante", 20.0),
        )

        c2 = config.get("problema2", {})
        perim = args.perimetro if args.perimetro is not None else c2.get("perimetro", 40.0)
        opt2 = OptimizadorLagrangeRectangulo(perimetro=perim)

        c3 = config.get("problema3", {})
        tasa = args.alfa if args.alfa is not None else c3.get("tasa_aprendizaje", 0.1)
        max_it = args.iteraciones if args.iteraciones is not None else c3.get("max_iter", 50)
        opt3 = OptimizadorGradienteAscenso(
            x0=c3.get("x0", 0.0),
            y0=c3.get("y0", 0.0),
            tasa_aprendizaje=tasa,
            max_iteraciones=max_it,
            tolerancia=c3.get("tolerancia", 1e-6),
        )

        c4 = config.get("problema4", {})
        cap = args.capacidad if args.capacidad is not None else c4.get("capacidad_maxima", 40.0)
        opt4 = OptimizadorKKTMultiplesRestricciones(
            coef_x=c4.get("coef_x", 5.0),
            coef_y=c4.get("coef_y", 8.0),
            coef_x2=c4.get("coef_x2", -0.1),
            coef_y2=c4.get("coef_y2", -0.2),
            capacidad_maxima=cap,
        )

        c5 = config.get("problema5", {})
        vol = args.volumen if args.volumen is not None else c5.get("volumen", 500.0)
        opt5 = OptimizadorCilindroFisico(volumen=vol, cerrado=c5.get("cerrado", True))

        # Resolucion segun seleccion
        if args.problema == 1:
            res1 = opt1.resolver()
            texto = formatear_problema_1(res1)
        elif args.problema == 2:
            res2 = opt2.resolver()
            texto = formatear_problema_2(res2)
        elif args.problema == 3:
            res3, hist3 = opt3.resolver_iterativo()
            texto = formatear_problema_3(res3, hist3)
        elif args.problema == 4:
            res4 = opt4.resolver()
            texto = formatear_problema_4(res4)
        elif args.problema == 5:
            res5 = opt5.resolver()
            texto = formatear_problema_5(res5)
        else:
            # Ejecutar todos
            res1 = opt1.resolver()
            res2 = opt2.resolver()
            res3, hist3 = opt3.resolver_iterativo()
            res4 = opt4.resolver()
            res5 = opt5.resolver()
            texto = generar_reporte_completo(res1, res2, res3, hist3, res4, res5)

        print(texto)

        if not args.sin_exportar:
            directorio_salidas = os.path.join(BASE_DIR, "outputs")
            nombre = f"reporte_problema_{args.problema}.txt" if args.problema else "reporte_tarea6.txt"
            ruta = guardar_reporte(texto, directorio_salidas, nombre)
            print(f"\n[OK] Reporte exportado exitosamente en: {ruta}")

    except (ErrorValidacion, KeyError, ValueError, OSError) as e:
        print(f"Error en la ejecucion: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
