import os

class ReportService:
    """
    Servicio encargado de formatear, generar y persistir reportes de calculo en archivos .txt.
    """
    @staticmethod
    def guardar_reporte(reporte_texto: str, ruta_archivo: str) -> str:
        """Guarda el texto de reporte en la ruta especificada."""
        directorio = os.path.dirname(ruta_archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio, exist_ok=True)
            
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(reporte_texto)
        return ruta_archivo
