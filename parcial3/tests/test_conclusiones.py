"""
Pruebas del archivo de conclusiones manuscritas.

El test obligatorio es el tope de 200 palabras: el .txt se transcribe a mano en
una hoja de examen, asi que pasarse no es un detalle de estilo sino un
incumplimiento del requisito.
"""

import pytest

from src.services.conclusiones import (
    TOPE_PALABRAS,
    contar_palabras,
    exportar_conclusiones,
    generar_conclusiones,
)
from src.utils.validators import ValidacionError


@pytest.fixture
def texto(metricas_p1, metricas_p2):
    return generar_conclusiones(metricas_p1, metricas_p2)


# ----------------------------------------------------------------------
# Tope de palabras (requisito obligatorio)
# ----------------------------------------------------------------------

def test_el_texto_tiene_200_palabras_o_menos(texto):
    palabras = contar_palabras(texto)
    assert palabras <= TOPE_PALABRAS, f"se paso del tope: {palabras} palabras"


def test_el_tope_declarado_es_200():
    assert TOPE_PALABRAS == 200


def test_el_archivo_escrito_tambien_respeta_el_tope(tmp_path, metricas_p1, metricas_p2):
    """Lo que cuenta `wc -w` sobre el archivo final, no solo el texto en memoria."""
    ruta = exportar_conclusiones(metricas_p1, metricas_p2, tmp_path / "conclusiones.txt")
    assert ruta.exists()
    assert contar_palabras(ruta.read_text(encoding="utf-8")) <= TOPE_PALABRAS


def test_el_conteo_coincide_con_el_criterio_de_wc():
    """contar_palabras debe partir por espacios, igual que `wc -w`."""
    assert contar_palabras("uno dos tres") == 3
    assert contar_palabras("  uno   dos  \n tres \t cuatro ") == 4
    assert contar_palabras("") == 0
    assert contar_palabras("rho=lambda/mu") == 1
    assert contar_palabras("rho = lambda/mu") == 3


# ----------------------------------------------------------------------
# Formato transcribible a mano
# ----------------------------------------------------------------------

def test_no_hay_markdown_ni_latex_ni_tablas(texto):
    for prohibido in ("**", "##", "`", "$", "|", "<", ">", "\\"):
        assert prohibido not in texto, f"marca de formato prohibida: {prohibido!r}"


def test_no_hay_vinetas_al_inicio_de_linea(texto):
    for linea in texto.splitlines():
        assert not linea.lstrip().startswith(("- ", "* ", "+ ", "1.", "2.")) or linea.startswith(
            "PROBLEMA"
        ), f"vineta en: {linea!r}"


def test_no_hay_emojis_ni_caracteres_no_transcribibles(texto):
    for caracter in texto:
        assert ord(caracter) < 128, f"caracter no ASCII: {caracter!r}"


def test_las_formulas_estan_en_notacion_transcribible(texto):
    assert "rho=lambda/mu" in texto
    assert "Wq=lambda/(mu*(mu-lambda))" in texto
    assert "T_eq=T_amb+(P_idle+k*trafico)/h" in texto
    assert "C*dT/dt" in texto


# ----------------------------------------------------------------------
# Contenido: los dos problemas y los numeros reales
# ----------------------------------------------------------------------

def test_cubre_los_dos_problemas(texto):
    assert "PROBLEMA 1." in texto
    assert "PROBLEMA 2." in texto


def test_reparte_el_espacio_entre_los_dos_problemas(texto):
    """Alrededor de 100 palabras por problema, ninguno se come al otro."""
    bloques = texto.split("PROBLEMA 2.")
    assert len(bloques) == 2
    p1 = contar_palabras(bloques[0])
    p2 = contar_palabras(bloques[1])
    assert 60 <= p1 <= 120, p1
    assert 60 <= p2 <= 120, p2


def test_usa_los_numeros_reales_de_la_corrida(texto, metricas_p1, metricas_p2):
    """Nada hardcodeado: los valores deben venir de las metricas."""
    assert f"{metricas_p1['wq_promedio_min']:.1f} min" in texto
    assert f"{metricas_p1['paradas_por_falta_stock']}" in texto
    assert f"media {metricas_p2['temp_media_c']:.1f} C" in texto
    assert f"{metricas_p2['tb_procesados']:.2f} TB" in texto
    assert f"{metricas_p2['pct_tiempo_throttling']:.1f}%" in texto


def test_explica_las_cero_paradas_del_problema1(texto, metricas_p1):
    """El enunciado pide justificar por que las paradas dan 0."""
    assert metricas_p1["paradas_por_falta_stock"] == 0
    assert "lead time" in texto
    assert "sobredimensionado" in texto
    assert "cuello de botella es la estacion" in texto


def test_incluye_una_recomendacion_por_problema(texto):
    assert texto.count("Recomendacion:") == 2


def test_el_texto_cambia_con_los_numeros(metricas_p1, metricas_p2):
    """Si las metricas cambian, el texto debe cambiar: no es una plantilla fija."""
    from src.simulation.discrete_sim import FabricaSimulation

    otras = FabricaSimulation(semilla=99).ejecutar(4.0)
    a = generar_conclusiones(metricas_p1, metricas_p2)
    b = generar_conclusiones(otras, metricas_p2)
    assert a != b


# ----------------------------------------------------------------------
# Validacion
# ----------------------------------------------------------------------

@pytest.mark.parametrize("faltante", ["p1", "p2", "ambos"])
def test_faltan_metricas_de_un_problema(metricas_p1, metricas_p2, faltante):
    m1 = {} if faltante in ("p1", "ambos") else metricas_p1
    m2 = {} if faltante in ("p2", "ambos") else metricas_p2
    with pytest.raises(ValidacionError, match="DOS problemas"):
        generar_conclusiones(m1, m2)


def test_exportar_crea_el_directorio_si_hace_falta(tmp_path, metricas_p1, metricas_p2):
    destino = tmp_path / "sub" / "dir" / "conclusiones.txt"
    ruta = exportar_conclusiones(metricas_p1, metricas_p2, destino)
    assert ruta.exists()
    assert ruta.read_text(encoding="utf-8").endswith("\n")
