"""
Pruebas de la capa de servicios: tracer, reporter y auditor de IA.

NINGUN test de este archivo sale a la red. El auditor se prueba por su motor
experto local, por la construccion del prompt y por el manejo de errores; los
clientes HTTP se ejercitan con mocks.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
import requests

from src.services.ai_auditor import MODELOS_GEMINI, AIAuditorService
from src.services.reporter import ReportService
from src.services.tracer import TrazaEventos, TrazaSerie, formatear_tiempo
from src.simulation.continuous_sim import CABECERA_TRAZA_P2, ClusterSimulation
from src.utils.validators import ValidacionError


# ----------------------------------------------------------------------
# Tracer
# ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "segundos,esperado",
    [
        (0.0, "00:00:00.000"),
        (1.5, "00:00:01.500"),
        (60.0, "00:01:00.000"),
        (3661.5, "01:01:01.500"),
        (28800.0, "08:00:00.000"),
    ],
    ids=["cero", "1s", "1min", "1h1m1s", "8h"],
)
def test_formateo_de_tiempo_simulado(segundos, esperado):
    assert formatear_tiempo(segundos) == esperado


def test_tiempo_negativo_se_rechaza():
    with pytest.raises(ValidacionError):
        formatear_tiempo(-1.0)


def test_la_traza_de_eventos_escribe_las_lineas_esperadas(tmp_path):
    traza = TrazaEventos("Prueba")
    traza.registrar(0.0, "inicio_simulacion", "arranque")
    traza.registrar(65.25, "llegada_orden", "Orden #7")
    traza.registrar(120.0, "fin_ensamblaje", "Orden #7")

    ruta = traza.guardar(tmp_path / "traza.log")
    assert ruta.exists()
    lineas = ruta.read_text(encoding="utf-8").splitlines()

    assert "TRAZA DE EVENTOS - PRUEBA" in lineas[1]
    cuerpo = [l for l in lineas if l.startswith("[")]
    assert len(cuerpo) == 3
    assert cuerpo[1].startswith("[00:01:05.250] LLEGADA_ORDEN")
    assert "Orden #7" in cuerpo[1]


def test_la_traza_de_eventos_rechaza_un_tipo_vacio():
    traza = TrazaEventos("Prueba")
    with pytest.raises(ValidacionError):
        traza.registrar(0.0, "   ")


def test_la_traza_csv_escribe_cabecera_y_filas(tmp_path):
    serie = TrazaSerie(["t_horas", "valor"])
    serie.registrar([0.0, 1.5])
    serie.registrar([1.0, 2.25])

    ruta = serie.guardar(tmp_path / "serie.csv")
    filas = ruta.read_text(encoding="utf-8").strip().splitlines()
    assert filas[0] == "t_horas,valor"
    assert len(filas) == 3
    assert filas[1].startswith("0.000000,1.500000")


def test_la_traza_csv_rechaza_filas_de_ancho_distinto():
    serie = TrazaSerie(["a", "b", "c"])
    with pytest.raises(ValidacionError):
        serie.registrar([1, 2])


def test_la_traza_del_problema2_se_muestrea_por_minuto():
    """8 h con muestreo cada 60 s deben dar 480 filas, no 28.800."""
    sim = ClusterSimulation(semilla=1)
    sim.ejecutar(8.0)
    assert len(sim.tracer) == 480
    assert sim.tracer.cabecera == CABECERA_TRAZA_P2


# ----------------------------------------------------------------------
# Reporter
# ----------------------------------------------------------------------

def test_reporte_problema1_contiene_las_metricas_del_enunciado(metricas_p1):
    texto = ReportService.generar_texto_problema1(metricas_p1)
    for fragmento in (
        "PROBLEMA 1: FABRICA DE LAPTOPS",
        "Tiempo de espera promedio de las ordenes (Wq)",
        "Ciclo de reposicion de componentes",
        "Tiempo de despacho de un lote de produccion",
        "Veces que la linea se detuvo por falta de stock",
        "Ordenes retrasadas por falta de inventario",
        "Eficiencia en el reabastecimiento",
        "SUPUESTO PROPIO",
    ):
        assert fragmento in texto, f"falta en el reporte: {fragmento}"


def test_reporte_problema2_contiene_las_metricas_del_enunciado(metricas_p2):
    texto = ReportService.generar_texto_problema2(metricas_p2)
    for fragmento in (
        "PROBLEMA 2: CLUSTER DE SERVIDORES",
        "Total en Terabytes",
        "Temperatura media",
        "Desviacion estandar",
        "Temperatura minima",
        "Temperatura maxima",
        "Eficiencia global",
        "throttling activo",
        "C * dT/dt = P_idle + k * trafico - h * (T - T_amb)",
    ):
        assert fragmento in texto, f"falta en el reporte: {fragmento}"


def test_el_reporte_se_escribe_en_disco(tmp_path, metricas_p1):
    texto = ReportService.generar_texto_problema1(metricas_p1)
    ruta = ReportService.exportar_reporte_txt(texto, tmp_path / "reporte.txt")
    assert ruta.exists()
    contenido = ruta.read_text(encoding="utf-8")
    assert contenido.startswith("=")
    assert contenido.endswith("\n")


def test_anexar_seccion_agrega_al_final(tmp_path):
    ruta = tmp_path / "r.txt"
    ReportService.exportar_reporte_txt("CUERPO ORIGINAL", ruta)
    original = ruta.read_text(encoding="utf-8")

    ReportService.anexar_seccion(ruta, "respuesta de la api", "Conclusion y recomendacion.")
    final = ruta.read_text(encoding="utf-8")

    assert final.startswith(original)
    assert final.index("RESPUESTA DE LA API") > final.index("CUERPO ORIGINAL")
    assert "Conclusion y recomendacion." in final


def test_anexar_dos_veces_conserva_el_orden(tmp_path):
    ruta = tmp_path / "r.txt"
    ReportService.exportar_reporte_txt("BASE", ruta)
    ReportService.anexar_seccion(ruta, "primera", "uno")
    ReportService.anexar_seccion(ruta, "segunda", "dos")
    final = ruta.read_text(encoding="utf-8")
    assert final.index("PRIMERA") < final.index("SEGUNDA")


def test_anexar_a_un_reporte_inexistente_falla(tmp_path):
    with pytest.raises(FileNotFoundError):
        ReportService.anexar_seccion(tmp_path / "no_existe.txt", "t", "c")


def test_los_reportes_no_llevan_emojis(metricas_p1, metricas_p2):
    """Regla dura del proyecto: cero emojis en todo lo generado."""
    textos = [
        ReportService.generar_texto_problema1(metricas_p1),
        ReportService.generar_texto_problema2(metricas_p2),
    ]
    for texto in textos:
        for caracter in texto:
            assert ord(caracter) < 0x2190, f"caracter no ASCII sospechoso: {caracter!r}"


# ----------------------------------------------------------------------
# Auditor de IA (sin red)
# ----------------------------------------------------------------------

def test_la_lista_de_modelos_gemini_esta_limpia():
    """Los modelos inexistentes solo agregan round-trips fallidos."""
    assert "gemini-3.6-flash" not in MODELOS_GEMINI
    assert "gemini-3.5-flash" not in MODELOS_GEMINI
    assert MODELOS_GEMINI == [
        "gemini-flash-latest",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-pro-latest",
    ]


@pytest.fixture
def auditor():
    """Auditor sin credenciales: obliga a usar el camino local."""
    a = AIAuditorService(api_key="")
    a.gemini_key = ""
    a.openai_key = ""
    a.local_url = ""
    return a


@pytest.mark.parametrize("problema", [1, 2])
def test_el_motor_experto_local_produce_conclusion_y_recomendaciones(
    auditor, problema, metricas_p1, metricas_p2
):
    metricas = metricas_p1 if problema == 1 else metricas_p2
    diagnostico = auditor.motor_experto_local(problema, metricas)
    assert "RECOMENDACIONES" in diagnostico
    assert "Recomendacion 1" in diagnostico
    assert "Recomendacion 3" in diagnostico
    assert len(diagnostico) > 500


def test_el_motor_experto_local_usa_los_numeros_de_la_corrida(auditor, metricas_p2):
    diagnostico = auditor.motor_experto_local(2, metricas_p2)
    assert f"{metricas_p2['pct_tiempo_throttling']:.2f} %" in diagnostico
    assert f"{metricas_p2['tb_procesados']:.4f} TB" in diagnostico


def test_problema_desconocido_se_rechaza(auditor, metricas_p1):
    with pytest.raises(ValidacionError):
        auditor.motor_experto_local(9, metricas_p1)
    with pytest.raises(ValidacionError):
        auditor.construir_prompt(9, "x")


@pytest.mark.parametrize("problema", [1, 2])
def test_el_prompt_incluye_el_reporte_y_es_distinto_por_problema(auditor, problema):
    prompt = auditor.construir_prompt(problema, "CONTENIDO DEL REPORTE")
    assert "CONTENIDO DEL REPORTE" in prompt
    assert "sin emojis" in prompt
    otro = auditor.construir_prompt(2 if problema == 1 else 1, "CONTENIDO DEL REPORTE")
    assert prompt != otro


def test_auditoria_sin_red_cae_al_motor_local_y_anexa(tmp_path, auditor, metricas_p1):
    ruta = tmp_path / "reporte.txt"
    ReportService.exportar_reporte_txt("REPORTE BASE", ruta)

    diagnostico, fuente = auditor.ejecutar_auditoria(1, metricas_p1, ruta, sin_red=True)

    assert "respaldo" in fuente.lower()
    final = ruta.read_text(encoding="utf-8")
    assert "RESPUESTA DE LA API DE IA" in final
    assert "Recomendacion 1" in final
    assert diagnostico.splitlines()[0] in final


def test_auditoria_sobre_reporte_inexistente_falla(tmp_path, auditor, metricas_p1):
    with pytest.raises(FileNotFoundError):
        auditor.ejecutar_auditoria(1, metricas_p1, tmp_path / "no_existe.txt", sin_red=True)


def test_sin_clave_gemini_no_se_intenta_la_llamada(auditor):
    ok, motivo = auditor.consultar_gemini("prompt")
    assert ok is False
    assert "GEMINI_API_KEY" in motivo


def test_sin_clave_openai_no_se_intenta_la_llamada(auditor):
    ok, motivo = auditor.consultar_openai("prompt")
    assert ok is False
    assert "OPENAI_API_KEY" in motivo


def test_un_error_de_conexion_no_propaga_excepcion(auditor):
    """La caida de red debe devolver (False, motivo), no reventar la simulacion."""
    with patch("src.services.ai_auditor.requests.post", autospec=True) as mock_post:
        mock_post.side_effect = requests.ConnectionError("red caida")
        ok, motivo = auditor.consultar_ollama("prompt")
    assert ok is False
    assert "no disponible" in motivo.lower()


def test_la_cascada_completa_falla_sin_excepcion(auditor):
    with patch("src.services.ai_auditor.requests.post", autospec=True) as mock_post:
        mock_post.side_effect = requests.ConnectionError("sin red")
        ok, motivo, fuente = auditor.consultar_api_externa("prompt")
    assert ok is False
    assert fuente == ""
    assert motivo


def test_gemini_exitoso_devuelve_el_texto():
    """Se mockea la respuesta HTTP: el test no sale a la red."""
    a = AIAuditorService(api_key="clave-de-prueba")

    class RespuestaFalsa:
        status_code = 200

        @staticmethod
        def json():
            return {"candidates": [{"content": {"parts": [{"text": "Conclusion simulada."}]}}]}

    with patch("src.services.ai_auditor.requests.post", autospec=True) as mock_post:
        mock_post.return_value = RespuestaFalsa()
        ok, texto = a.consultar_gemini("prompt")

    assert ok is True
    assert texto == "Conclusion simulada."
    assert mock_post.call_count == 1, "debe cortar en el primer modelo que responde"


def test_clave_invalida_corta_la_cascada_de_modelos():
    a = AIAuditorService(api_key="clave-mala")

    class RespuestaFalsa:
        status_code = 400
        text = "API_KEY_INVALID"

        @staticmethod
        def json():
            return {"error": {"message": "API key not valid"}}

    with patch("src.services.ai_auditor.requests.post", autospec=True) as mock_post:
        mock_post.return_value = RespuestaFalsa()
        ok, motivo = a.consultar_gemini("prompt")

    assert ok is False
    assert "no valida" in motivo
    assert mock_post.call_count == 1, "no tiene sentido reintentar con la misma clave mala"


def test_las_conclusiones_del_motor_local_no_llevan_emojis(auditor, metricas_p1, metricas_p2):
    for problema, metricas in ((1, metricas_p1), (2, metricas_p2)):
        texto = auditor.motor_experto_local(problema, metricas)
        for caracter in texto:
            assert ord(caracter) < 0x2190, f"caracter sospechoso: {caracter!r}"
