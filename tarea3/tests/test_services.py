"""
Pruebas Unitarias para los Servicios de Exportacion y Auditoria
"""

import os
from pathlib import Path
import pytest

from src.services.reporter import ReportService
from src.services.ai_auditor import AIAuditorService
from src.services.docx_service import DocxReportService


def test_exportacion_reporte_txt(tmp_path):
    metricas = {
        "tiempo_simulacion_s": 120.0,
        "lambda": 15.0,
        "mu": 18.0,
        "capacidad_buffer_s": 50,
        "umbral_reabastecimiento_s": 10,
        "paquetes_procesados": 1750,
        "paquetes_perdidos": 42,
        "tasa_perdida_pct": 2.40,
        "tiempo_medio_cola_wq_s": 0.1200,
        "promedio_paquetes_sistema_l": 4.25,
        "costo_almacenamiento_usd": 125.40,
        "costo_penalizacion_usd": 420.00,
        "costo_global_usd": 545.40,
    }

    destino = tmp_path / "test_reporte.txt"
    out_path = ReportService.exportar_reporte_txt(metricas, destino)

    assert out_path.exists()
    contenido = out_path.read_text(encoding="utf-8")
    assert "REPORTE DE SIMULACIÓN DE RED" in contenido
    assert "Tasa de Llegada (lambda): 15.0 paquetes/s" in contenido
    assert "Costo Global del Sistema: $545.40" in contenido


def test_auditoria_local_contingencia(tmp_path):
    metricas = {
        "tiempo_simulacion_s": 120.0,
        "lambda": 15.0,
        "mu": 18.0,
        "capacidad_buffer_s": 50,
        "umbral_reabastecimiento_s": 10,
        "paquetes_procesados": 1800,
        "paquetes_perdidos": 0,
        "tasa_perdida_pct": 0.0,
        "tiempo_medio_cola_wq_s": 0.0450,
        "promedio_paquetes_sistema_l": 0.95,
        "costo_almacenamiento_usd": 4.50,
        "costo_penalizacion_usd": 0.00,
        "costo_global_usd": 4.50,
    }

    destino = tmp_path / "reporte_auditoria.txt"
    auditor = AIAuditorService(api_key="CLAVE_DE_PRUEBA_INEXISTENTE")
    diag = auditor.ejecutar_auditoria_completa(metricas, destino)

    assert "DIAGNOSTICO DE EFICIENCIA Y TEORIA DE COLAS" in diag
    assert "TRES (3) RECOMENDACIONES DE OPTIMIZACION" in diag
    assert destino.exists()
    texto_final = destino.read_text(encoding="utf-8")
    assert "RESPUESTA DE LA API" in texto_final


def test_generacion_docx_informe(tmp_path):
    metricas = {
        "tiempo_simulacion_s": 120.0,
        "lambda": 15.0,
        "mu": 18.0,
        "capacidad_buffer_s": 50,
        "umbral_reabastecimiento_s": 10,
        "paquetes_procesados": 1780,
        "paquetes_perdidos": 10,
        "tasa_perdida_pct": 0.56,
        "tiempo_medio_cola_wq_s": 0.0520,
        "promedio_paquetes_sistema_l": 1.10,
        "promedio_paquetes_cola_lq": 0.35,
        "costo_almacenamiento_usd": 6.20,
        "costo_penalizacion_usd": 100.00,
        "costo_global_usd": 106.20,
    }
    diag = "Diagnostico de prueba para informe tecnico formal."
    destino = tmp_path / "Informe_Tecnico_Test.docx"

    out_docx = DocxReportService.compilar_informe_docx(
        metricas=metricas,
        diagnostico_ia=diag,
        destino_docx=destino,
    )

    assert out_docx.exists()
    assert out_docx.stat().st_size > 1000
