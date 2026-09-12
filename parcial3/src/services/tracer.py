"""
Servicio de trazas analizables.

El enunciado pide "generar salidas en trazas que puedan ser analizadas". Se
producen dos formatos, uno por problema:

  - TrazaEventos  -> .log de una linea por evento discreto (Problema 1).
  - TrazaSerie    -> .csv de series temporales muestreadas (Problema 2).

Las dos clases acumulan en memoria y escriben al cerrar. El volumen es chico por
diseno (cientos de lineas, no decenas de miles), porque la traza del Problema 2
se muestrea cada 60 s aunque el integrador avance de a 1 s.
"""

from pathlib import Path
from typing import Iterable, List, Sequence, Union

from src.utils.validators import ValidacionError


def formatear_tiempo(segundos: float) -> str:
    """
    Formatea un tiempo simulado en HH:MM:SS.mmm.

    Se usa el tiempo SIMULADO, no el de reloj de pared: dos corridas con la misma
    semilla producen exactamente los mismos sellos de tiempo, que es lo que hace
    a la traza analizable y comparable.
    """
    if segundos < 0:
        raise ValidacionError(f"El tiempo simulado no puede ser negativo: {segundos}.")
    total_ms = int(round(segundos * 1000.0))
    horas, resto = divmod(total_ms, 3_600_000)
    minutos, resto = divmod(resto, 60_000)
    segs, ms = divmod(resto, 1000)
    return f"{horas:02d}:{minutos:02d}:{segs:02d}.{ms:03d}"


class TrazaEventos:
    """Traza de eventos discretos: una linea por evento, en orden cronologico."""

    SEPARADOR = " | "

    def __init__(self, titulo: str) -> None:
        self.titulo = titulo
        self.lineas: List[str] = []

    def registrar(self, tiempo_s: float, tipo_evento: str, detalle: str = "") -> str:
        """
        Anota un evento. Devuelve la linea generada para poder inspeccionarla.

        Formato: [HH:MM:SS.mmm] TIPO_EVENTO | detalle
        """
        if not tipo_evento or not tipo_evento.strip():
            raise ValidacionError("El tipo de evento no puede estar vacio.")
        marca = formatear_tiempo(tiempo_s)
        tipo = tipo_evento.strip().upper()
        linea = f"[{marca}] {tipo:<22}"
        if detalle:
            linea += f"{self.SEPARADOR}{detalle.strip()}"
        self.lineas.append(linea)
        return linea

    def contar(self, tipo_evento: str) -> int:
        """Cuenta las lineas de un tipo de evento (util para tests y auditoria)."""
        clave = tipo_evento.strip().upper()
        return sum(1 for l in self.lineas if f"] {clave:<22}" in l or f"] {clave} " in l)

    def cabecera(self) -> List[str]:
        """Bloque de encabezado del archivo de traza."""
        return [
            "=" * 78,
            f"TRAZA DE EVENTOS - {self.titulo.upper()}",
            "Formato: [tiempo simulado HH:MM:SS.mmm] TIPO_EVENTO | detalle",
            "=" * 78,
        ]

    def guardar(self, destino: Union[str, Path]) -> Path:
        """Escribe la traza completa en disco y devuelve la ruta final."""
        ruta = Path(destino)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        contenido = "\n".join(self.cabecera() + self.lineas)
        ruta.write_text(contenido + "\n", encoding="utf-8")
        return ruta

    def __len__(self) -> int:
        return len(self.lineas)


class TrazaSerie:
    """Traza de series temporales en CSV, apta para graficar o cargar en una hoja."""

    def __init__(self, cabecera: Sequence[str], decimales: int = 6) -> None:
        if not cabecera:
            raise ValidacionError("La traza CSV necesita al menos una columna.")
        self.cabecera: List[str] = [str(c) for c in cabecera]
        self.decimales = decimales
        self.filas: List[List[str]] = []

    def registrar(self, valores: Iterable) -> List[str]:
        """
        Anota una fila. Valida el ancho contra la cabecera para que un cambio de
        columnas no genere un CSV desalineado que despues nadie puede leer.
        """
        crudos = list(valores)
        if len(crudos) != len(self.cabecera):
            raise ValidacionError(
                f"La fila tiene {len(crudos)} valores y la cabecera {len(self.cabecera)} columnas."
            )
        fila = [self._formatear(v) for v in crudos]
        self.filas.append(fila)
        return fila

    def _formatear(self, valor) -> str:
        """Los flotantes salen con precision fija; el resto, como texto."""
        if isinstance(valor, bool):
            return "1" if valor else "0"
        if isinstance(valor, float):
            return f"{valor:.{self.decimales}f}"
        return str(valor)

    def guardar(self, destino: Union[str, Path]) -> Path:
        """Escribe el CSV en disco y devuelve la ruta final."""
        ruta = Path(destino)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        lineas = [",".join(self.cabecera)] + [",".join(f) for f in self.filas]
        ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
        return ruta

    def __len__(self) -> int:
        return len(self.filas)


def _selfcheck() -> None:
    """Comprobaciones minimas del formato de traza."""
    import tempfile

    assert formatear_tiempo(0.0) == "00:00:00.000"
    assert formatear_tiempo(3661.5) == "01:01:01.500"
    assert formatear_tiempo(28800.0) == "08:00:00.000"

    traza = TrazaEventos("Prueba")
    linea = traza.registrar(65.25, "llegada_orden", "Orden #7")
    assert linea.startswith("[00:01:05.250] LLEGADA_ORDEN")
    assert "Orden #7" in linea
    traza.registrar(70.0, "fin_ensamblaje", "Orden #7")
    assert len(traza) == 2
    assert traza.contar("llegada_orden") == 1

    serie = TrazaSerie(["t_horas", "valor"])
    serie.registrar([0.0, 1.5])
    serie.registrar([1.0, 2.5])
    assert len(serie) == 2
    try:
        serie.registrar([1.0])
    except ValidacionError:
        pass
    else:
        raise AssertionError("TrazaSerie acepto una fila con ancho incorrecto")

    with tempfile.TemporaryDirectory() as tmp:
        ruta_log = traza.guardar(Path(tmp) / "t.log")
        texto = ruta_log.read_text(encoding="utf-8")
        assert "TRAZA DE EVENTOS - PRUEBA" in texto
        assert "LLEGADA_ORDEN" in texto

        ruta_csv = serie.guardar(Path(tmp) / "t.csv")
        filas = ruta_csv.read_text(encoding="utf-8").strip().splitlines()
        assert filas[0] == "t_horas,valor"
        assert len(filas) == 3

    print("selfcheck tracer: OK")


if __name__ == "__main__":
    _selfcheck()
