"""Reporte PDF de la simulacion con graficos y el analisis de la IA (R7)."""

from __future__ import annotations

import math
import tempfile
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from fpdf import FPDF  # noqa: E402

from src.services.ia import ProveedorIA  # noqa: E402
from src.simulation.motor_simpy import EstadoSimulacion  # noqa: E402

_REEMPLAZOS = {
    "λ": "lambda", "ρ": "rho", "μ": "mu", "≈": "~", "≤": "<=", "≥": ">=", "—": "-", "–": "-",
    "•": "-", "“": '"', "”": '"', "‘": "'", "’": "'", "…": "...", "→": "->", "·": "*", "²": "^2",
}


def _latin1(texto: str) -> str:
    """Las fuentes base de fpdf solo cubren latin-1: se traducen simbolos comunes y se quita markdown."""
    for a, b in _REEMPLAZOS.items():
        texto = texto.replace(a, b)
    texto = texto.replace("**", "").replace("##", "").replace("# ", "")
    return texto.encode("latin-1", "replace").decode("latin-1")


def _fmt(valor: float | None) -> str:
    return "no hay" if valor is None else f"{valor:.2f}"


def resumen_texto(estado: EstadoSimulacion, contexto: dict | None = None) -> str:
    """Resumen en texto plano del estado; es lo que se envia a la IA."""
    contexto = contexto or {}
    m = estado.metricas
    lineas = [f"Tiempo simulado: {estado.tiempo:.1f}"]
    if "parametros" in contexto:
        lineas.append("Parametros: " + ", ".join(f"{k}={v}" for k, v in contexto["parametros"].items()))
    lineas += [
        "Metricas: " + ", ".join(f"{k}={v:.4f}" if isinstance(v, float) else f"{k}={v}" for k, v in m.items()),
        "Eventos: " + ", ".join(f"{k}={v}" for k, v in estado.conteo_eventos.items()),
    ]
    if "mm1" in contexto:
        lineas.append("M/M/1 de referencia por servidor: " + ", ".join(f"{k}={v:.4f}" for k, v in contexto["mm1"].items()))
    puntos = "; ".join(f"{t} en c={c:.1f}% (T={temp:.2f})" for c, temp, t in estado.puntos_estacionarios)
    lineas.append(f"Modelo termico: {puntos}; inflexion c={_fmt(estado.punto_inflexion)}%; punto critico c={_fmt(estado.punto_critico)}%")
    g = estado.series_gradiente
    if g.get("tiempo"):
        lineas.append(f"Gradiente: v final={g['velocidad'][-1]:.4f}, v* final={g['velocidad_optima'][-1]:.4f}, E final={g['energia'][-1]:.4f}")
    lineas.append(
        f"Lagrange: lambda={estado.lambda_:.4f}, energia=" + ", ".join(f"{k}={v:.2f}" for k, v in estado.energia_clusteres.items())
    )
    lineas.append("Rutas finales: " + "; ".join(f"{k}: {' -> '.join(v) or 'sin ruta'}" for k, v in estado.rutas.items()))
    return "\n".join(lineas)


class GeneradorReportePDF:
    """Arma el PDF: parametros, metricas, M1, M2, graficos y el analisis del ProveedorIA."""

    def __init__(self, proveedor: ProveedorIA) -> None:
        self._proveedor = proveedor

    def generar(self, estado: EstadoSimulacion, ruta_salida: str | Path | None = None, contexto: dict | None = None) -> Path:
        contexto = contexto or {}
        if ruta_salida is None:
            ruta_salida = Path("outputs") / f"reporte_{datetime.now():%Y%m%d_%H%M%S}.pdf"
        ruta_salida = Path(ruta_salida)
        ruta_salida.parent.mkdir(parents=True, exist_ok=True)

        resumen = resumen_texto(estado, contexto)
        analisis = self._proveedor.analizar(resumen)

        pdf = FPDF()
        pdf.set_auto_page_break(True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 15)
        pdf.cell(0, 9, _latin1("Reporte del simulador de red de centros de datos"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 5, _latin1(f"Metodos Cuantitativos - UJAP - generado {datetime.now():%Y-%m-%d %H:%M}"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        self._seccion(pdf, "1. Parametros y metricas de colas (R6)")
        filas = [(k, f"{v:.4f}" if isinstance(v, float) else str(v)) for k, v in contexto.get("parametros", {}).items()]
        filas += [(k, f"{v:.4f}" if isinstance(v, float) else str(v)) for k, v in estado.metricas.items()]
        filas += [(f"M/M/1 {k}", "inf" if math.isinf(v) else f"{v:.4f}") for k, v in contexto.get("mm1", {}).items()]
        filas += [(f"eventos {k}", str(v)) for k, v in estado.conteo_eventos.items()]
        self._tabla(pdf, filas)

        self._seccion(pdf, "2. Modulo 1: programacion dinamica (R1, R2)")
        for cid, ruta in estado.rutas.items():
            self._parrafo(pdf, f"Ruta optima a {cid}: {' -> '.join(ruta) or 'sin ruta (nodo caido)'}")
        for sid, m in sorted(estado.ultimas_mochilas.items()):
            self._parrafo(
                pdf,
                f"Mochila {sid} (t={m['tiempo']:.0f}): capacidad libre {m['capacidad_libre']}, {m['en_cola']} en cola, "
                f"elige {', '.join(m['seleccionados']) or 'ninguno'} (valor {m['valor']}, peso {m['peso']})",
            )

        self._seccion(pdf, "3. Modulo 2: optimizacion no lineal (R3, R4, R5)")
        for c, t, tipo in estado.puntos_estacionarios:
            self._parrafo(pdf, f"T'(c) = 0 en c = {c:.2f} %: {tipo} local, T = {t:.2f} C")
        self._parrafo(pdf, f"Inflexion (T''(c) = 0): c = {_fmt(estado.punto_inflexion)} %  |  punto critico de emergencia: c = {_fmt(estado.punto_critico)} %")
        self._parrafo(pdf, f"Lagrange: lambda = {estado.lambda_:.4f}; " + ", ".join(f"{k} = {v:.2f}" for k, v in estado.energia_clusteres.items()))

        with tempfile.TemporaryDirectory() as tmp:
            for imagen in self._graficos(estado, Path(tmp)):
                pdf.image(str(imagen), w=180)

        self._seccion(pdf, f"4. Analisis de IA ({self._proveedor.nombre})")
        self._parrafo(pdf, analisis)

        pdf.output(str(ruta_salida))
        return ruta_salida

    # ------------------------------------------------------------------ auxiliares

    @staticmethod
    def _seccion(pdf: FPDF, titulo: str) -> None:
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 7, _latin1(titulo), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)

    @staticmethod
    def _parrafo(pdf: FPDF, texto: str) -> None:
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 4.5, _latin1(texto), new_x="LMARGIN", new_y="NEXT")

    @staticmethod
    def _tabla(pdf: FPDF, filas: list[tuple[str, str]]) -> None:
        pdf.set_font("Helvetica", "", 8)
        ancho = 45
        for i, (clave, valor) in enumerate(filas):
            pdf.cell(ancho, 4.5, _latin1(clave), border=1)
            pdf.cell(ancho, 4.5, _latin1(valor), border=1, new_x="LMARGIN" if i % 2 else "RIGHT", new_y="NEXT" if i % 2 else "TOP")
        if len(filas) % 2:
            pdf.ln(4.5)

    @staticmethod
    def _graficos(estado: EstadoSimulacion, carpeta: Path) -> list[Path]:
        rutas = []

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.2))
        cs = [c for c, _ in estado.curva_termica]
        ax1.plot(cs, [t for _, t in estado.curva_termica], color="black")
        for c, t, tipo in estado.puntos_estacionarios:
            ax1.scatter([c], [t], color="tab:green" if tipo == "minimo" else "tab:orange", zorder=3, label=f"{tipo} {c:.0f}%")
        if estado.punto_critico is not None:
            ax1.axvspan(estado.punto_critico, 100, color="tab:red", alpha=0.12, label="emergencia")
        ax1.set(title="T(c): modelo termico", xlabel="carga (%)", ylabel="T (C)")
        ax1.legend(fontsize=7)
        s = estado.series_termico
        ax2.plot(s["tiempo"], s["carga"], label="carga %", lw=0.8)
        ax2.set(title="Carga en el tiempo", xlabel="t")
        if estado.punto_critico is not None:
            ax2.axhline(estado.punto_critico, color="tab:red", ls="--", lw=0.8, label="critico")
        ax2.legend(fontsize=7)
        rutas.append(GeneradorReportePDF._guardar(fig, carpeta / "termico.png"))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.2))
        g = estado.series_gradiente
        ax1.plot(g.get("tiempo", []), g.get("velocidad", []), label="v (gradiente)", lw=0.9)
        ax1.plot(g.get("tiempo", []), g.get("velocidad_optima", []), label="v* analitico", lw=0.8, ls="--")
        ax1.set(title="Gradiente: velocidad del ventilador", xlabel="t")
        ax1.legend(fontsize=7)
        lg = estado.series_lagrange
        for clave in [k for k in lg if k.startswith("E_")]:
            ax2.plot(lg["tiempo"], lg[clave], label=clave, lw=0.8)
        ax2.set(title="Lagrange: energia por cluster", xlabel="t")
        ax2.legend(fontsize=7)
        rutas.append(GeneradorReportePDF._guardar(fig, carpeta / "optimizadores.png"))
        return rutas

    @staticmethod
    def _guardar(fig, ruta: Path) -> Path:
        fig.tight_layout()
        fig.savefig(ruta, dpi=110)
        plt.close(fig)
        return ruta
