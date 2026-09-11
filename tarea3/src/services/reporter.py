"""
Servicio de Generacion y Exportacion de Reportes (.txt)
Capa de Servicios — Metodos Cuantitativos
Universidad Jose Antonio Paez
"""

from pathlib import Path
from typing import Dict, Union

from src.utils.config import OUTPUTS_DIR


class ReportService:
    """
    Servicio encargado de compilar y persistir los reportes estructurados de texto plano
    segun el formato oficial solicitado en el enunciado de la practica.
    """

    @staticmethod
    def generar_texto_reporte(metricas: Dict) -> str:
        """
        Construye la representacion en texto plano de las metricas obtenidas.
        Sigue de manera estricta la estructura fijada por el profesor.
        """
        lineas = [
            "==================================================",
            "REPORTE DE SIMULACIÓN DE RED",
            "==================================================",
            f"Tiempo Total de Simulación: {metricas.get('tiempo_simulacion_s', 0.0)} s",
            f"Tasa de Llegada (lambda): {metricas.get('lambda', 0.0):.1f} paquetes/s",
            f"Tasa de Servicio (mu): {metricas.get('mu', 0.0):.1f} paquetes/s",
            f"Capacidad de Buffer (S): {metricas.get('capacidad_buffer_s', 50)} paquetes",
            f"Umbral Reabastecimiento (s): {metricas.get('umbral_reabastecimiento_s', 10)} paquetes",
            "",
            "METRICAS OBTENIDAS:",
            f"- Paquetes Procesados: {metricas.get('paquetes_procesados', 0)}",
            f"- Paquetes Perdidos (Overflow): {metricas.get('paquetes_perdidos', 0)}",
            f"- Tasa de Pérdida: {metricas.get('tasa_perdida_pct', 0.0):.2f}%",
            f"- Tiempo Medio en Cola (Wq): {metricas.get('tiempo_medio_cola_wq_s', 0.0):.4f} s",
            f"- Promedio Paquetes en Sistema (L): {metricas.get('promedio_paquetes_sistema_l', 0.0):.2f}",
            f"- Costo Total de Almacenamiento: ${metricas.get('costo_almacenamiento_usd', 0.0):.2f}",
            f"- Costo Total de Penalización (Ruptura): ${metricas.get('costo_penalizacion_usd', 0.0):.2f}",
            f"- Costo Global del Sistema: ${metricas.get('costo_global_usd', 0.0):.2f}",
            "==================================================",
        ]
        return "\n".join(lineas)

    @classmethod
    def exportar_reporte_txt(
        cls,
        metricas: Dict,
        destino: Union[str, Path] = "reporte_simulacion.txt",
    ) -> Path:
        """
        Exporta el reporte a un archivo .txt plano.
        Si la ruta es relativa y simple, la guarda en OUTPUTS_DIR o en la ruta indicada.
        """
        ruta = Path(destino)
        if not ruta.is_absolute() and len(ruta.parts) == 1:
            ruta = OUTPUTS_DIR / ruta.name

        ruta.parent.mkdir(parents=True, exist_ok=True)
        contenido = cls.generar_texto_reporte(metricas)

        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido + "\n")

        return ruta

    @classmethod
    def anexar_seccion(cls, ruta: Union[str, Path], titulo: str, contenido: str) -> None:
        """Anexa un bloque de analisis adicional al final del archivo de texto."""
        ruta_p = Path(ruta)
        bloque = (
            "\n\n==================================================\n"
            f"{titulo.upper()}\n"
            "==================================================\n"
            f"{contenido.strip()}\n"
            "==================================================\n"
        )
        with open(ruta_p, "a", encoding="utf-8") as f:
            f.write(bloque)
