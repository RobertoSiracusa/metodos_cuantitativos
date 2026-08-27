import os
import pytest
from src.services.reporter import ReportService

def test_guardar_reporte(tmp_path):
    archivo_destino = tmp_path / "reportes" / "test_report.txt"
    texto = "Reporte de prueba"
    
    ruta_guardada = ReportService.guardar_reporte(texto, str(archivo_destino))
    
    assert os.path.exists(ruta_guardada)
    with open(ruta_guardada, "r", encoding="utf-8") as f:
        contenido = f.read()
    assert contenido == texto
