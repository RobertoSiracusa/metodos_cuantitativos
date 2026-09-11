"""
Modelo de Gestion de Inventario (Control de Buffers y Costos)
Capa de Modelo Cuantitativo — Metodos Cuantitativos
Universidad Jose Antonio Paez
"""

from typing import Dict, Optional
from src.utils.config import (
    CAPACIDAD_BUFFER_S,
    UMBRAL_REABASTECER_S,
    LOTE_REABASTECER_Q,
    COSTO_HOLDING_POR_SEG,
    COSTO_PENALIZACION_RUPTURA,
)


class ModeloInventarioBuffer:
    """
    Encapsula el modelado cuantitativo de gestion de inventarios aplicado
    al almacenamiento de paquetes en buffers de routers.
    
    Implementa:
    - Politica de control de flujo (s, Q).
    - Capacidad maxima de almacenamiento (S).
    - Costo de mantener (Holding Cost en RAM) y costo de ruptura (Shortage / Overflow).
    """

    def __init__(
        self,
        capacidad_s: int = CAPACIDAD_BUFFER_S,
        umbral_s: int = UMBRAL_REABASTECER_S,
        lote_q: int = LOTE_REABASTECER_Q,
        costo_holding_por_seg: float = COSTO_HOLDING_POR_SEG,
        costo_ruptura: float = COSTO_PENALIZACION_RUPTURA,
    ):
        self.capacidad_s = int(capacidad_s)
        self.umbral_s = int(umbral_s)
        self.lote_q = int(lote_q)
        self.costo_holding_por_seg = float(costo_holding_por_seg)
        self.costo_ruptura = float(costo_ruptura)

        # Resultados acumulados
        self.costo_almacenamiento_total = 0.0
        self.costo_penalizacion_total = 0.0
        self.costo_global = 0.0
        self.total_paquetes_perdidos = 0
        self.total_paquetes_procesados = 0

    def registrar_desempeno(
        self,
        costo_almacenamiento: float,
        paquetes_perdidos: int,
        paquetes_procesados: int,
    ) -> None:
        """Registra los resultados provenientes de la ejecucion de la simulacion."""
        self.costo_almacenamiento_total = round(float(costo_almacenamiento), 2)
        self.total_paquetes_perdidos = int(paquetes_perdidos)
        self.total_paquetes_procesados = int(paquetes_procesados)
        self.costo_penalizacion_total = round(self.total_paquetes_perdidos * self.costo_ruptura, 2)
        self.costo_global = round(self.costo_almacenamiento_total + self.costo_penalizacion_total, 2)

    def evaluar_salud_inventario(self) -> Dict[str, str]:
        """Evalua cualitativamente el impacto financiero y de servicio del buffer."""
        total_llegadas = self.total_paquetes_procesados + self.total_paquetes_perdidos
        tasa_perdida = (self.total_paquetes_perdidos / total_llegadas * 100.0) if total_llegadas > 0 else 0.0

        if tasa_perdida == 0.0:
            nivel = "OPTIMO"
            diagnostico = (
                f"Excelente retencion de inventario (0.00% de ruptura). La capacidad S={self.capacidad_s} "
                "amortigua completamente las oscilaciones de demanda estocastica."
            )
        elif tasa_perdida < 5.0:
            nivel = "MODERADO"
            diagnostico = (
                f"Nivel de ruptura aceptable ({tasa_perdida:.2f}% de descarte). Compromiso economico balanceado "
                "entre retencion en buffer y costos de almacenamiento."
            )
        else:
            nivel = "CRITICO"
            diagnostico = (
                f"Saturacion severa del inventario ({tasa_perdida:.2f}% de descarte). El costo de ruptura domina "
                f"la operacion con ${self.costo_penalizacion_total:.2f} en penalizaciones."
            )

        return {
            "nivel": nivel,
            "tasa_perdida": f"{tasa_perdida:.2f}%",
            "diagnostico": diagnostico,
        }

    def generar_reporte(self) -> str:
        """Genera reporte estructurado de los costos de inventario."""
        evaluacion = self.evaluar_salud_inventario()
        pct_alm = (self.costo_almacenamiento_total / self.costo_global * 100.0) if self.costo_global > 0 else 0.0
        pct_rup = (self.costo_penalizacion_total / self.costo_global * 100.0) if self.costo_global > 0 else 0.0

        rep = (
            "==================================================\n"
            "   REPORTE DE GESTION DE INVENTARIO EN BUFFERS\n"
            "==================================================\n"
            "Parametros de Politica de Inventario:\n"
            f" - Capacidad Maxima del Buffer (S): {self.capacidad_s} paquetes\n"
            f" - Umbral Minimo de Control de Flujo (s): {self.umbral_s} paquetes\n"
            f" - Lote de Autorizacion de Entrada (Q): {self.lote_q} paquetes\n"
            f" - Costo Unitario de Almacenamiento (Ch): ${self.costo_holding_por_seg:.2f}/paq/s\n"
            f" - Costo Unitario de Ruptura (Cs): ${self.costo_ruptura:.2f}/descarte\n\n"
            "Resultados de Costos del Sistema:\n"
            f" - Costo Total de Almacenamiento: ${self.costo_almacenamiento_total:.2f} ({pct_alm:.1f}%)\n"
            f" - Costo Total de Penalizacion (Ruptura): ${self.costo_penalizacion_total:.2f} ({pct_rup:.1f}%)\n"
            f" - Costo Global del Sistema: ${self.costo_global:.2f}\n\n"
            f"Diagnostico de Politica: [{evaluacion['nivel']}]\n"
            f"{evaluacion['diagnostico']}\n"
            "==================================================\n"
        )
        return rep
