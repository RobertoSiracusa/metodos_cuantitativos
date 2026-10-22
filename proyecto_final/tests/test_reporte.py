"""Tests del reporte PDF y del proveedor de IA (R7), sin usar la red."""

from src.services import ia
from src.services.ia import ClienteGemini, ProveedorSinConexion
from src.services.reporte_pdf import GeneradorReportePDF, _latin1, resumen_texto
from src.simulation.motor_simpy import MotorSimulacion
from src.utils.config import Configuracion


def _estado():
    motor = MotorSimulacion(Configuracion.por_defecto(), semilla=5)
    motor.avanzar(80)
    return motor, motor.estado()


def test_pdf_sin_conexion(tmp_path):
    motor, estado = _estado()
    contexto = {"parametros": motor.parametros, "mm1": motor.comparacion_mm1()}
    ruta = GeneradorReportePDF(ProveedorSinConexion()).generar(estado, tmp_path / "r.pdf", contexto)
    assert ruta.read_bytes().startswith(b"%PDF")
    assert ruta.stat().st_size > 20_000  # incluye los graficos


def test_resumen_incluye_los_tres_modulos():
    motor, estado = _estado()
    texto = resumen_texto(estado, {"mm1": motor.comparacion_mm1()})
    for clave in ("Rutas finales", "Modelo termico", "Gradiente", "Lagrange", "M/M/1"):
        assert clave in texto


def test_latin1_traduce_simbolos():
    assert _latin1("**λ** ≈ 0.5 → ok") == "lambda ~ 0.5 -> ok"


class _Respuesta:
    def __init__(self, codigo, datos):
        self.status_code = codigo
        self._datos = datos

    def json(self):
        return self._datos


def test_gemini_devuelve_el_texto(monkeypatch):
    datos = {"candidates": [{"content": {"parts": [{"text": "todo bien"}]}}]}
    monkeypatch.setattr(ia.requests, "post", lambda *a, **k: _Respuesta(200, datos))
    assert ClienteGemini("clave").analizar("x") == "todo bien"


def test_gemini_con_clave_invalida_cae_al_modo_sin_conexion(monkeypatch):
    llamadas = []

    def post(*a, **k):
        llamadas.append(a)
        return _Respuesta(403, {})

    monkeypatch.setattr(ia.requests, "post", post)
    assert "no disponible" in ClienteGemini("mala").analizar("x")
    assert len(llamadas) == 1


def test_gemini_sin_red(monkeypatch):
    def post(*a, **k):
        raise ia.requests.ConnectionError("sin red")

    monkeypatch.setattr(ia.requests, "post", post)
    assert "no disponible" in ClienteGemini("clave").analizar("x")
