"""
Punto de entrada del Parcial III - Simulacion.

Universidad Jose Antonio Paez - Facultad de Ingenieria
Escuela de Ingenieria en Computacion - Metodos Cuantitativos

Ofrece un menu de opciones para acceder a cada problema y una interfaz de linea
de comandos equivalente para correr sin interaccion.

Orden de ejecucion al terminar cada problema, tal como lo pide el enunciado:
    1. Escribir la traza analizable.
    2. Escribir el reporte .txt.
    3. Consultar la API de IA con las metricas.
    4. Mostrar por pantalla la conclusion y la recomendacion.
    5. Anexar la respuesta al final del reporte .txt.

El periodo de simulacion en horas se pide SIEMPRE antes de ejecutar, por teclado
o por el argumento --horas.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

# El proyecto se importa como paquete `src`, asi que la raiz debe estar en sys.path
# aunque se invoque main.py desde otro directorio.
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.services.ai_auditor import AIAuditorService
from src.services.conclusiones import contar_palabras, exportar_conclusiones
from src.services.reporter import ReportService
from src.services.tracer import TrazaEventos, TrazaSerie
from src.simulation.continuous_sim import CABECERA_TRAZA_P2, ClusterSimulation
from src.simulation.discrete_sim import FabricaSimulation
from src.utils.config import (
    ARCHIVO_REPORTE_P1,
    ARCHIVO_REPORTE_P2,
    ARCHIVO_TRAZA_P1,
    ARCHIVO_TRAZA_P2,
    HORAS_DEFECTO,
    SEMILLA_DEFECTO,
    asegurar_directorio_salidas,
)
from src.utils.validators import ValidacionError, parsear_horas_entrada, validar_opcion_menu

ANCHO = 62
SEPARADOR = "=" * ANCHO

BANNER = f"""{SEPARADOR}
  UNIVERSIDAD JOSE ANTONIO PAEZ - FACULTAD DE INGENIERIA
  ESCUELA DE INGENIERIA EN COMPUTACION
  PARCIAL III - SIMULACION
{SEPARADOR}
  [1] Problema 1: Fabrica de laptops (eventos discretos)
  [2] Problema 2: Cluster de servidores (simulacion continua)
  [3] Ejecutar ambos problemas
  [4] Animacion Pygame (bonus)
  [0] Salir
{SEPARADOR}"""

OPCIONES_MENU = ["0", "1", "2", "3", "4"]
MAX_REINTENTOS = 5

# Cache de metricas entre corridas. El archivo de conclusiones necesita los
# numeros de LOS DOS problemas; si el usuario corre uno solo, se guarda su mitad
# y las conclusiones se regeneran cuando la otra mitad ya existe en disco.
CACHE_METRICAS = {1: "metricas_problema1.json", 2: "metricas_problema2.json"}


# ----------------------------------------------------------------------
# Entrada de datos validada
# ----------------------------------------------------------------------

def solicitar_horas(defecto: float = HORAS_DEFECTO) -> float:
    """
    Pide por teclado el periodo de simulacion en horas, con reintento.

    Enter vacio toma el valor por defecto. Una entrada invalida muestra el motivo
    y vuelve a preguntar: el usuario nunca ve un traceback.
    """
    for intento in range(MAX_REINTENTOS):
        try:
            crudo = input(f"Duracion de la simulacion en horas [Enter = {defecto:g}]: ")
        except EOFError:
            print(f"Entrada no disponible. Se usa el valor por defecto: {defecto:g} horas.")
            return defecto
        try:
            return parsear_horas_entrada(crudo, defecto)
        except ValidacionError as exc:
            restantes = MAX_REINTENTOS - intento - 1
            print(f"  Dato invalido: {exc}")
            if restantes:
                print(f"  Intente de nuevo ({restantes} intento(s) restante(s)).")

    print(f"Demasiados intentos invalidos. Se usa el valor por defecto: {defecto:g} horas.")
    return defecto


def solicitar_opcion() -> str:
    """Pide una opcion del menu, con reintento y sin traceback ante entrada invalida."""
    while True:
        try:
            crudo = input("Seleccione una opcion: ")
        except EOFError:
            print("Entrada no disponible. Saliendo.")
            return "0"
        try:
            return validar_opcion_menu(crudo, OPCIONES_MENU)
        except ValidacionError as exc:
            print(f"  {exc}")


# ----------------------------------------------------------------------
# Cache de metricas entre corridas
# ----------------------------------------------------------------------

def _ruta_cache(problema: int) -> Path:
    """Ruta del archivo de cache de metricas de un problema."""
    return asegurar_directorio_salidas() / CACHE_METRICAS[problema]


def guardar_cache_metricas(problema: int, metricas: Dict) -> Path:
    """Persiste las metricas de un problema para poder cruzarlas mas tarde."""
    ruta = _ruta_cache(problema)
    ruta.write_text(json.dumps(metricas, indent=2, ensure_ascii=True), encoding="utf-8")
    return ruta


def cargar_cache_metricas(problema: int) -> Optional[Dict]:
    """Lee las metricas cacheadas de un problema, o None si no hay o estan rotas."""
    ruta = _ruta_cache(problema)
    if not ruta.is_file():
        return None
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Aviso: no se pudo leer la cache {ruta.name} ({exc}). Se ignora.")
        return None


# ----------------------------------------------------------------------
# Ejecucion de los problemas
# ----------------------------------------------------------------------

def ejecutar_problema1(
    horas: float, semilla: Optional[int] = SEMILLA_DEFECTO, sin_red: bool = False
) -> Dict:
    """
    Corre el Problema 1 de punta a punta y deja traza, reporte y respuesta de IA.
    """
    salidas = asegurar_directorio_salidas()
    print()
    print(SEPARADOR)
    print(f"PROBLEMA 1: FABRICA DE LAPTOPS - {horas:g} HORAS SIMULADAS")
    print(SEPARADOR)

    tracer = TrazaEventos("Problema 1: fabrica de laptops (eventos discretos)")
    sim = FabricaSimulation(semilla=semilla, tracer=tracer)
    metricas = sim.ejecutar(duracion_horas=horas)

    # 1. Traza analizable
    ruta_traza = tracer.guardar(salidas / ARCHIVO_TRAZA_P1)
    print(f"Traza de eventos escrita   : {ruta_traza}  ({len(tracer)} eventos)")

    # 2. Reporte de texto
    texto = ReportService.generar_texto_problema1(metricas)
    ruta_reporte = ReportService.exportar_reporte_txt(texto, salidas / ARCHIVO_REPORTE_P1)
    print(f"Reporte de texto escrito   : {ruta_reporte}")
    print()
    print(texto)

    # 3, 4 y 5. API de IA, impresion por pantalla y anexado al reporte
    AIAuditorService().ejecutar_auditoria(1, metricas, ruta_reporte, sin_red=sin_red)

    guardar_cache_metricas(1, metricas)
    return metricas


def ejecutar_problema2(
    horas: float, semilla: Optional[int] = SEMILLA_DEFECTO, sin_red: bool = False
) -> Dict:
    """
    Corre el Problema 2 de punta a punta y deja traza, reporte y respuesta de IA.
    """
    salidas = asegurar_directorio_salidas()
    print()
    print(SEPARADOR)
    print(f"PROBLEMA 2: CLUSTER DE SERVIDORES - {horas:g} HORAS SIMULADAS")
    print(SEPARADOR)

    tracer = TrazaSerie(CABECERA_TRAZA_P2)
    sim = ClusterSimulation(semilla=semilla, tracer=tracer)
    metricas = sim.ejecutar(duracion_horas=horas)

    # 1. Traza analizable
    ruta_traza = tracer.guardar(salidas / ARCHIVO_TRAZA_P2)
    print(f"Traza CSV escrita          : {ruta_traza}  ({len(tracer)} filas)")

    # 2. Reporte de texto
    texto = ReportService.generar_texto_problema2(metricas)
    ruta_reporte = ReportService.exportar_reporte_txt(texto, salidas / ARCHIVO_REPORTE_P2)
    print(f"Reporte de texto escrito   : {ruta_reporte}")
    print()
    print(texto)

    # 3, 4 y 5. API de IA, impresion por pantalla y anexado al reporte
    AIAuditorService().ejecutar_auditoria(2, metricas, ruta_reporte, sin_red=sin_red)

    guardar_cache_metricas(2, metricas)
    return metricas


def generar_conclusiones_si_es_posible(
    metricas_p1: Optional[Dict] = None, metricas_p2: Optional[Dict] = None
) -> Optional[Path]:
    """
    Escribe el .txt de conclusiones manuscritas si hay metricas de los dos problemas.

    Lo que falte se busca en la cache en disco, de modo que correr los problemas
    por separado igual termina produciendo el archivo.
    """
    m1 = metricas_p1 or cargar_cache_metricas(1)
    m2 = metricas_p2 or cargar_cache_metricas(2)
    if not m1 or not m2:
        faltante = "Problema 1" if not m1 else "Problema 2"
        print(
            f"Conclusiones manuscritas: pendientes. Falta correr el {faltante} "
            "para tener los numeros de los dos."
        )
        return None

    ruta = exportar_conclusiones(m1, m2)
    palabras = contar_palabras(ruta.read_text(encoding="utf-8"))
    print(f"Conclusiones manuscritas   : {ruta}  ({palabras} palabras, tope 200)")
    return ruta


def lanzar_gui(horas: float, semilla: Optional[int] = SEMILLA_DEFECTO) -> bool:
    """
    Punto de enganche de la capa grafica Pygame (bonus).

    El modulo grafico se entrega por separado. Cuando exista src/gui/app.py con
    una funcion `ejecutar_animacion(horas, semilla)`, esta funcion lo levanta sin
    que haya que tocar nada mas. Mientras tanto avisa y devuelve el control al menu.
    """
    try:
        from src.gui.app import ejecutar_animacion  # type: ignore[import-not-found]
    except ImportError:
        print()
        print("Modulo grafico no disponible en esta version")
        print()
        return False

    ejecutar_animacion(horas=horas, semilla=semilla)
    return True


# ----------------------------------------------------------------------
# Menu interactivo
# ----------------------------------------------------------------------

def mostrar_menu() -> None:
    """Imprime el menu de opciones."""
    print()
    print(BANNER)


def bucle_menu(semilla: Optional[int] = SEMILLA_DEFECTO, sin_red: bool = False) -> None:
    """Bucle principal del menu de opciones."""
    while True:
        mostrar_menu()
        opcion = solicitar_opcion()

        if opcion == "0":
            print("Fin del programa.")
            return

        if opcion == "4":
            horas = solicitar_horas()
            lanzar_gui(horas, semilla)
            continue

        # Las opciones 1, 2 y 3 piden la duracion ANTES de ejecutar
        horas = solicitar_horas()

        if opcion == "1":
            m1 = ejecutar_problema1(horas, semilla, sin_red)
            generar_conclusiones_si_es_posible(metricas_p1=m1)
        elif opcion == "2":
            m2 = ejecutar_problema2(horas, semilla, sin_red)
            generar_conclusiones_si_es_posible(metricas_p2=m2)
        elif opcion == "3":
            m1 = ejecutar_problema1(horas, semilla, sin_red)
            m2 = ejecutar_problema2(horas, semilla, sin_red)
            generar_conclusiones_si_es_posible(m1, m2)

        print()
        print("Corrida finalizada. Los archivos quedaron en el directorio outputs/.")


# ----------------------------------------------------------------------
# Interfaz de linea de comandos
# ----------------------------------------------------------------------

def construir_parser() -> argparse.ArgumentParser:
    """Define los argumentos de linea de comandos."""
    parser = argparse.ArgumentParser(
        prog="main.py",
        description=(
            "Parcial III de Metodos Cuantitativos: simulacion de una fabrica de "
            "laptops (eventos discretos) y de un cluster de servidores (continua)."
        ),
    )
    parser.add_argument(
        "--problema",
        choices=["1", "2", "ambos"],
        help="Problema a ejecutar sin pasar por el menu.",
    )
    parser.add_argument(
        "--horas",
        type=float,
        help=f"Periodo de simulacion en horas (por defecto {HORAS_DEFECTO:g}).",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Corre sin menu ni interaccion. Requiere --problema.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Lanza directamente la animacion Pygame (bonus).",
    )
    parser.add_argument(
        "--semilla",
        type=int,
        default=SEMILLA_DEFECTO,
        help=f"Semilla de reproducibilidad (por defecto {SEMILLA_DEFECTO}).",
    )
    parser.add_argument(
        "--sin-red",
        action="store_true",
        help="No consulta la API de IA; usa directamente el motor experto local.",
    )
    return parser


def resolver_horas(args: argparse.Namespace) -> Tuple[float, bool]:
    """
    Determina la duracion de la corrida a partir de los argumentos.

    Devuelve (horas, se_pidio_por_teclado). En modo headless nunca se pregunta:
    si no hay --horas se toma el valor por defecto.
    """
    if args.horas is not None:
        # validar_horas lanza ValidacionError, que el llamador convierte en un
        # mensaje limpio con codigo de salida 2.
        return parsear_horas_entrada(str(args.horas), HORAS_DEFECTO), False
    if args.headless:
        return HORAS_DEFECTO, False
    return solicitar_horas(), True


def main(argv: Optional[list] = None) -> int:
    """Punto de entrada. Devuelve el codigo de salida del proceso."""
    args = construir_parser().parse_args(argv)

    if args.headless and not args.problema and not args.gui:
        print("Error: --headless requiere --problema {1,2,ambos}.", file=sys.stderr)
        return 2

    try:
        if args.gui:
            horas, _ = resolver_horas(args)
            lanzar_gui(horas, args.semilla)
            return 0

        if args.problema:
            horas, _ = resolver_horas(args)
            print(BANNER)
            if args.problema in ("1", "ambos"):
                m1 = ejecutar_problema1(horas, args.semilla, args.sin_red)
            else:
                m1 = None
            if args.problema in ("2", "ambos"):
                m2 = ejecutar_problema2(horas, args.semilla, args.sin_red)
            else:
                m2 = None
            generar_conclusiones_si_es_posible(m1, m2)
            print()
            print("Corrida finalizada. Los archivos quedaron en el directorio outputs/.")
            return 0

        bucle_menu(args.semilla, args.sin_red)
        return 0

    except ValidacionError as exc:
        print(f"Error de validacion: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print()
        print("Ejecucion interrumpida por el usuario.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
