"""
Punto de Entrada Principal — Simulador Dinamico de Redes de Computadoras
Arquitectura Top-Down Modular POO
Universidad Jose Antonio Paez — Facultad de Ingenieria
Catedra: Metodos Cuantitativos y Simulacion
"""

import argparse
import os
import sys
from pathlib import Path

# Asegurar que el directorio raiz del proyecto este en sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.utils.config import (
    LAMBDA_DEFECTO,
    MU_DEFECTO,
    CAPACIDAD_BUFFER_S,
    UMBRAL_REABASTECER_S,
    LOTE_REABASTECER_Q,
    OUTPUTS_DIR,
)
from src.core.queuing_model import ModeloColasRed
from src.core.inventory_model import ModeloInventarioBuffer
from src.core.hungarian_model import ModeloAsignacionHungaro
from src.services.simulation_service import NetworkSimulation
from src.services.reporter import ReportService
from src.services.ai_auditor import AIAuditorService
from src.services.docx_service import DocxReportService


def ejecutar_modo_headless(
    duracion_s: float = 120.0,
    lamb: float = LAMBDA_DEFECTO,
    mu: float = MU_DEFECTO,
    capacidad_s: int = CAPACIDAD_BUFFER_S,
    umbral_s: int = UMBRAL_REABASTECER_S,
    lote_q: int = LOTE_REABASTECER_Q,
    exportar: bool = True,
) -> None:
    """
    Ejecuta una corrida estocastica completa en modo por lotes/consola sin requerir interfaz grafica.
    Ideal para auditorias automatizadas, servidores remotos o pruebas cuantitativas.
    """
    print("=" * 65)
    print("SIMULADOR DINAMICO DE REDES — MODO POR LOTES / CONSOLA")
    print("=" * 65)
    print(f"Parametros: lambda={lamb} paq/s, mu={mu} paq/s, S={capacidad_s}, s={umbral_s}, Q={lote_q}")
    print(f"Ejecutando simulacion estocastica por {duracion_s} segundos simulados...")

    sim = NetworkSimulation(
        lam=lamb,
        mu=mu,
        capacidad_s=capacidad_s,
        umbral_s=umbral_s,
        lote_q=lote_q,
    )

    # Avanzar entorno SimPy hasta el tiempo objetivo
    sim.env.run(until=duracion_s)

    metricas = sim.obtener_metricas_completas()
    reporte_txt = ReportService.generar_texto_reporte(metricas)

    print("\n" + reporte_txt)

    if exportar:
        ruta_txt = OUTPUTS_DIR / "reporte_simulacion.txt"
        ReportService.exportar_reporte_txt(metricas, ruta_txt)
        print(f"\nReporte estructurado guardado en: {ruta_txt}")

        ruta_log = sim.exportar_eventos_log(OUTPUTS_DIR / "eventos_desempeno.log")
        print(f"Registro de eventos de desempeno guardado en: {ruta_log}")

        auditor = AIAuditorService()
        diag = auditor.ejecutar_auditoria_completa(metricas, ruta_txt)

        ruta_docx = OUTPUTS_DIR / "Informe_Tecnico_Simulador_Redes.docx"
        DocxReportService.compilar_informe_docx(
            metricas=metricas,
            diagnostico_ia=diag,
            destino_docx=ruta_docx,
        )
        print(f"Informe Tecnico Word generado en: {ruta_docx}")


def main():
    parser = argparse.ArgumentParser(
        description="Simulador Dinamico de Redes de Computadoras (Metodos Cuantitativos - UJAP)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Ejecuta la simulacion en modo consola/lotes sin abrir la ventana grafica Pygame.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=120.0,
        help="Duracion de la simulacion en segundos para modo headless. Default: 120.0 s.",
    )
    parser.add_argument(
        "--lambda",
        dest="lamb",
        type=float,
        default=LAMBDA_DEFECTO,
        help=f"Tasa de llegada Poisson (paquetes/segundo). Default: {LAMBDA_DEFECTO}",
    )
    parser.add_argument(
        "--mu",
        type=float,
        default=MU_DEFECTO,
        help=f"Tasa de servicio exponencial por router (paquetes/segundo). Default: {MU_DEFECTO}",
    )
    parser.add_argument(
        "--capacidad-s",
        type=int,
        default=CAPACIDAD_BUFFER_S,
        help=f"Capacidad maxima S del buffer. Default: {CAPACIDAD_BUFFER_S}",
    )
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="En modo headless, desactiva la generacion de archivos de salida .txt y .docx",
    )

    args = parser.parse_args()

    if args.headless:
        ejecutar_modo_headless(
            duracion_s=args.duration,
            lamb=args.lamb,
            mu=args.mu,
            capacidad_s=args.capacidad_s,
            exportar=not args.no_export,
        )
    else:
        # Lanzamiento interactivo de la interfaz grafica Pygame
        try:
            from src.gui.app import SimulatorApp
            app = SimulatorApp()
            app.run()
        except Exception as ex:
            es_error_display = any(k in str(ex).lower() for k in ("display", "video", "driver", "window"))
            if es_error_display:
                print(f"No fue posible inicializar la ventana grafica ({ex}).")
                print("Ejecutando en modo headless alternativo...")
                ejecutar_modo_headless(
                    duracion_s=args.duration,
                    lamb=args.lamb,
                    mu=args.mu,
                    capacidad_s=args.capacidad_s,
                    exportar=True,
                )
            else:
                import traceback
                print(f"Error critico al ejecutar la interfaz grafica: {ex}")
                traceback.print_exc()
                sys.exit(1)


if __name__ == "__main__":
    main()
