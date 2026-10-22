"""Tests para la interfaz de linea de comandos (CLI) y servicio de reportes."""

import os
import pytest
from main import main
from src.core.problema1_sin_restricciones import OptimizadorSinRestricciones
from src.core.problema2_lagrange import OptimizadorLagrangeRectangulo
from src.core.problema3_gradiente import OptimizadorGradienteAscenso
from src.core.problema4_kkt import OptimizadorKKTMultiplesRestricciones
from src.core.problema5_cilindro import OptimizadorCilindroFisico
from src.services.reporter import generar_reporte_completo, guardar_reporte


def test_main_ejecucion_completa_sin_exportar(capsys):
    cod = main(["--sin-exportar"])
    assert cod == 0
    salida = capsys.readouterr().out
    assert "PROBLEMA 1" in salida
    assert "PROBLEMA 2" in salida
    assert "PROBLEMA 3" in salida
    assert "PROBLEMA 4" in salida
    assert "PROBLEMA 5" in salida
    assert "RESUMEN EJECUTIVO" in salida


@pytest.mark.parametrize("prob_id", [1, 2, 3, 4, 5])
def test_main_ejecucion_individual(prob_id, capsys):
    cod = main(["--problema", str(prob_id), "--sin-exportar"])
    assert cod == 0
    salida = capsys.readouterr().out
    assert f"PROBLEMA {prob_id}" in salida


def test_main_con_parametros_personalizados(capsys):
    cod = main([
        "--problema", "3",
        "--alfa", "0.2",
        "--iteraciones", "20",
        "--sin-exportar",
    ])
    assert cod == 0
    salida = capsys.readouterr().out
    assert "PROBLEMA 3" in salida
    assert "alfa = 0.2" in salida


def test_guardar_reporte_crea_archivo(tmp_path):
    opt1 = OptimizadorSinRestricciones().resolver()
    opt2 = OptimizadorLagrangeRectangulo().resolver()
    opt3, hist3 = OptimizadorGradienteAscenso().resolver_iterativo()
    opt4 = OptimizadorKKTMultiplesRestricciones().resolver()
    opt5 = OptimizadorCilindroFisico().resolver()

    texto = generar_reporte_completo(opt1, opt2, opt3, hist3, opt4, opt5)
    ruta = guardar_reporte(texto, str(tmp_path), "test_reporte.txt")

    assert os.path.exists(ruta)
    with open(ruta, "r", encoding="utf-8") as f:
        contenido = f.read()
    assert "PROBLEMA 1" in contenido
    assert "FIN DEL INFORME TECNICO" in contenido
