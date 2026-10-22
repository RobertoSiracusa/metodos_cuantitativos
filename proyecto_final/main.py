"""Punto de entrada del simulador.

    python main.py                  dashboard Pygame (simulacion en vivo)
    python main.py --headless       simulacion SimPy sin ventana, imprime el resumen
    python main.py --modulo m1      modulo 1 solo: ruta mas corta + mochila
    python main.py --modulo m2      modulo 2 solo: termico, gradiente y Lagrange
"""

from __future__ import annotations

import argparse
import math
import sys
from typing import TYPE_CHECKING

from src.core.no_lineal.base import EntradaOptimizacion
from src.core.programacion_dinamica.mochila import Mochila
from src.core.programacion_dinamica.ruta_mas_corta import RutaMasCorta
from src.utils.config import Configuracion
from src.utils.validators import ErrorValidacion, Validador

if TYPE_CHECKING:
    from src.simulation.motor_simpy import MotorSimulacion


def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simulador de optimizacion para redes de centros de datos")
    parser.add_argument("--modulo", choices=["m1", "m2"], default=None, help="Modulo a ejecutar")
    parser.add_argument("--escenario", default=None, help="Ruta a un escenario JSON (default: el escenario por defecto)")
    parser.add_argument("--cluster", default="C1", help="Id del cluster a usar en el modulo m1 (default: C1)")
    parser.add_argument(
        "--fallar",
        action="append",
        default=[],
        metavar="NODO",
        help="Id de un nodo a marcar como caido antes de resolver (repetible)",
    )
    parser.add_argument("--headless", action="store_true", help="Corre la simulacion SimPy sin ventana")
    parser.add_argument("--semilla", type=int, default=42, help="Semilla aleatoria de la simulacion (default: 42)")
    parser.add_argument("--duracion", type=float, default=None, help="Duracion de la simulacion (default: la del escenario)")
    parser.add_argument("--reporte", action="store_true", help="Con --headless: genera el reporte PDF al terminar")
    parser.add_argument("--sin-ia", action="store_true", help="No llama a la API de IA en el reporte")
    parser.add_argument("--captura", default=None, metavar="PNG", help="Guarda una imagen del dashboard sin abrir la ventana")
    parser.add_argument("--tiempo-captura", type=float, default=120.0, help="Instante de la captura (default: 120)")
    parser.add_argument("--carga", type=float, default=60.0, help="Carga Q en %% para el gradiente del modulo m2 (default: 60)")
    parser.add_argument("--iteraciones", type=_entero_positivo, default=50, help="Iteraciones del gradiente en m2 (default: 50)")
    return parser


def _entero_positivo(texto: str) -> int:
    try:
        return int(Validador.validar_rango("--iteraciones", texto, minimo=1, maximo=100000, entero=True))
    except ErrorValidacion as e:
        raise argparse.ArgumentTypeError(str(e)) from None


def _formatear_costo(costo: float) -> str:
    return "inf" if math.isinf(costo) else f"{costo:.4f}"


def _cargar_configuracion(args: argparse.Namespace) -> Configuracion:
    return Configuracion.desde_archivo(args.escenario) if args.escenario else Configuracion.por_defecto()


def _crear_motor(args: argparse.Namespace) -> "MotorSimulacion":
    from src.simulation.motor_simpy import MotorSimulacion  # import diferido: m1 y m2 no necesitan SimPy

    configuracion = _cargar_configuracion(args)
    if args.duracion is not None:
        datos = configuracion.datos
        datos["parametros"].setdefault("simulacion", {})["duracion"] = Validador.validar_rango(
            "--duracion", args.duracion, minimo=1, maximo=100000
        )
        configuracion = Configuracion(datos)
    return MotorSimulacion(configuracion, semilla=args.semilla)


def _generador_reporte(motor: "MotorSimulacion", sin_ia: bool):
    """Devuelve una funcion estado -> ruta del PDF (la usan --reporte y la tecla P de la GUI)."""
    from src.services.ia import ProveedorSinConexion, crear_proveedor
    from src.services.reporte_pdf import GeneradorReportePDF

    proveedor = ProveedorSinConexion("se pidio --sin-ia") if sin_ia else crear_proveedor()
    generador = GeneradorReportePDF(proveedor)
    contexto = lambda: {"parametros": motor.parametros, "mm1": motor.comparacion_mm1()}  # noqa: E731
    return lambda estado: generador.generar(estado, contexto=contexto())


def _ejecutar_headless(args: argparse.Namespace) -> None:
    motor = _crear_motor(args)
    motor.suscribir(lambda e: print(f"[t={e.tiempo:7.2f}] {e.tipo:<11} {e.mensaje}") if e.tipo != "cambio_ruta" else None)
    motor.avanzar(motor.duracion)
    estado = motor.estado()

    print()
    print(f"Resumen de la simulacion (duracion {motor.duracion}, semilla {args.semilla}):")
    for clave, valor in estado.metricas.items():
        print(f"  {clave:<22}{valor:.4f}" if isinstance(valor, float) else f"  {clave:<22}{valor}")
    print("Eventos:", estado.conteo_eventos)
    print("M/M/1 de referencia por servidor:", {k: round(v, 4) for k, v in motor.comparacion_mm1().items()})
    print(f"Temperatura final {estado.temperatura:.2f} C con carga {estado.carga:.2f} %  |  ventilador v = {estado.velocidad:.4f}")
    print("Energia por cluster:", {k: round(v, 2) for k, v in estado.energia_clusteres.items()}, f"lambda = {estado.lambda_:.4f}")
    print("Rutas finales:", {k: " -> ".join(v) or "sin ruta" for k, v in estado.rutas.items()})
    if args.reporte:
        print(f"Reporte PDF guardado en {_generador_reporte(motor, args.sin_ia)(estado)}")


def _ejecutar_modulo_m1(args: argparse.Namespace) -> None:
    configuracion = _cargar_configuracion(args)
    red = configuracion.construir_red()

    for nodo_id in args.fallar:
        try:
            nodo = red.nodo(nodo_id)
        except KeyError:
            raise ErrorValidacion(f"el nodo a fallar '{nodo_id}' no existe") from None
        nodo.fallar()

    cluster = red.cluster(args.cluster)
    origen = next(r.id for r in red.routers if r.capa == "gateway")
    destino = cluster.tor_id

    modelo_ruta = RutaMasCorta(red)
    resultado_ruta = modelo_ruta.resolver(origen, destino)

    print("Tabla de programacion dinamica (ruta mas corta):")
    print(f"{'etapa':<6}{'nodo':<8}{'f':<12}{'siguiente':<10}")
    for etapa in sorted(modelo_ruta.tabla):
        for nodo_id, (f, siguiente) in modelo_ruta.tabla[etapa].items():
            print(f"{etapa:<6}{nodo_id:<8}{_formatear_costo(f):<12}{siguiente or '-':<10}")
    print()

    if resultado_ruta.existe:
        camino = " -> ".join(resultado_ruta.camino)
        print(f"Ruta {origen} -> {destino}: {camino} (costo {resultado_ruta.costo:.4f})")
    else:
        print(f"Ruta {origen} -> {destino}: no existe")
    print()

    primer_servidor = cluster.servidores[0]
    paquetes_cluster = [p for p in configuracion.construir_paquetes() if p.destino_cluster == cluster.id]

    modelo_mochila = Mochila(primer_servidor.capacidad)
    resultado_mochila = modelo_mochila.resolver(paquetes_cluster)

    print(f"Mochila para cluster {cluster.id} (capacidad {primer_servidor.capacidad}):")
    ids_seleccionados = ", ".join(p.id for p in resultado_mochila.seleccionados) or "(ninguno)"
    print(f"Seleccionados: {ids_seleccionados}")
    print(f"Valor total: {resultado_mochila.valor_total}")
    print(f"Peso total: {resultado_mochila.peso_total}")


def _ejecutar_modulo_m2(args: argparse.Namespace) -> None:
    q = Validador.validar_rango("--carga", args.carga, minimo=0, maximo=100)
    configuracion = _cargar_configuracion(args)

    termico = configuracion.construir_modelo_termico()
    print("Modelo termico T(c) (R3):")
    for punto in termico.puntos_estacionarios():
        print(f"  {punto.tipo:<7} local en c = {punto.carga:.2f} %  ->  T = {punto.temperatura:.2f} C")
    inflexion = termico.punto_inflexion()
    print(f"  inflexion en c = {inflexion:.2f} %" if inflexion is not None else "  sin inflexion en el dominio")
    umbral = termico.carga_umbral()
    print(f"  T >= {termico.t_max} C desde c = {umbral:.2f} %" if umbral is not None else f"  T nunca llega a {termico.t_max} C")
    critico = termico.punto_critico()
    print(f"  punto critico de enfriamiento de emergencia: c = {critico:.2f} %" if critico is not None else "  sin punto critico")
    print()

    gradiente = configuracion.construir_gradiente()
    print(f"Gradiente de enfriamiento con carga Q = {q} % (R4):")
    print(f"{'iter':<6}{'v':<10}{'E(v)':<12}{'E_prima(v)':<12}")
    for i in range(1, args.iteraciones + 1):
        valores = gradiente.actualizar(EntradaOptimizacion(float(i), carga=q)).valores
        if i <= 5 or i % 10 == 0 or i == args.iteraciones:
            print(f"{i:<6}{valores['velocidad']:<10.4f}{valores['energia']:<12.4f}{valores['gradiente']:<12.4f}")
    print(f"  optimo analitico v* = {gradiente.optimo_analitico(q):.4f}")
    print()

    demandas: dict[str, float] = {c["id"]: 0.0 for c in configuracion.datos["clusteres"]}
    for paquete in configuracion.construir_paquetes():
        demandas[paquete.destino_cluster] += paquete.requerimiento
    lagrange = configuracion.construir_lagrange()
    resultado = lagrange.resolver(demandas, lagrange.e_max)
    print(f"Reparto de energia con Lagrange, E_max = {lagrange.e_max} (R5):")
    for cid, energia in resultado.asignacion.items():
        print(f"  {cid}: demanda {demandas[cid]:>6.1f}  ->  E = {energia:.4f}")
    print(f"  lambda = {resultado.lambda_:.4f}   rendimiento R = {resultado.rendimiento:.4f}")
    print(f"  suma E = {sum(resultado.asignacion.values()):.4f}")


def _ejecutar_gui(args: argparse.Namespace) -> None:
    from src.gui.app import AplicacionPygame  # import diferido: m1, m2 y --headless no necesitan pygame

    motor = _crear_motor(args)
    aplicacion = AplicacionPygame(motor, _generador_reporte(motor, args.sin_ia))
    if args.captura:
        ruta = aplicacion.capturar(args.captura, Validador.validar_rango("--tiempo-captura", args.tiempo_captura, minimo=0))
        print(f"Captura guardada en {ruta}")
    else:
        aplicacion.ejecutar()


def main(argv: list[str] | None = None) -> int:
    parser = _construir_parser()
    args = parser.parse_args(argv)

    try:
        if args.modulo == "m1":
            _ejecutar_modulo_m1(args)
        elif args.modulo == "m2":
            _ejecutar_modulo_m2(args)
        elif args.headless:
            _ejecutar_headless(args)
        else:
            _ejecutar_gui(args)
    except ErrorValidacion as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
