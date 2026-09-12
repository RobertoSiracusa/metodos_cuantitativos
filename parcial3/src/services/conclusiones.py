"""
Generador del archivo de conclusiones manuscritas.

Este .txt NO es la respuesta de la IA: es el analisis propio, pensado para que
una persona lo transcriba a mano en una hoja de examen. De ahi las restricciones:

  - TOPE DURO DE 200 PALABRAS en total, contando los dos problemas. Es un
    requisito, no una guia. El generador falla si se pasa, antes que entregar un
    archivo fuera de contrato.
  - Texto plano: sin markdown, sin LaTeX, sin tablas, sin vinetas decorativas y
    sin emojis.
  - Formulas en notacion transcribible a mano: rho=lambda/mu, no simbolos griegos.
  - Todos los numeros salen de la corrida real, pasados como argumento. Nada
    hardcodeado ni inventado.

El conteo de palabras usa la misma definicion que `wc -w`: tokens separados por
espacios en blanco. Por eso el texto evita los signos "=" sueltos, que contarian
como una palabra cada uno.
"""

from pathlib import Path
from typing import Dict, Union

from src.utils.config import ARCHIVO_CONCLUSIONES, asegurar_directorio_salidas
from src.utils.validators import ValidacionError

TOPE_PALABRAS = 200


def contar_palabras(texto: str) -> int:
    """Cuenta palabras con el mismo criterio que `wc -w`: tokens entre espacios."""
    return len(texto.split())


def _bloque_problema1(m: Dict) -> str:
    """Analisis manuscrito del Problema 1, alrededor de 90 palabras."""
    rho = m["teorico_rho"]
    consumo_lead = (
        m["lambda_ordenes_hora"] * m["consumo_por_laptop"] * (m["lead_time_min"] / 60.0)
    )
    veredicto_stock = (
        "nunca se agota: esta sobredimensionado"
        if m["paradas_por_falta_stock"] == 0
        else "se agoto y freno la linea"
    )
    return (
        "PROBLEMA 1. FABRICA DE LAPTOPS (EVENTOS DISCRETOS)\n"
        f"Cola M/M/1 con lambda={m['lambda_ordenes_hora']:.0f} ordenes/h y "
        f"mu={m['mu_laptops_hora']:.0f} laptops/h, luego rho=lambda/mu={rho:.3f}.\n"
        f"Formula Wq=lambda/(mu*(mu-lambda))={m['teorico_wq_min']:.1f} min; la simulacion de "
        f"{m['tiempo_simulado_horas']:.0f} h dio {m['wq_promedio_min']:.1f} min.\n"
        f"Paradas de linea por falta de stock: {m['paradas_por_falta_stock']}. El umbral "
        f"s={m['umbral_critico_s']} cubre de sobra el consumo\n"
        f"durante el lead time ({m['lambda_ordenes_hora']:.0f} u/h por "
        f"{m['lead_time_min'] / 60.0:.2f} h, o sea {consumo_lead:.1f} unidades), asi que el "
        "inventario\n"
        f"{veredicto_stock}. El cuello de botella es la estacion unica,\n"
        f"con {rho * 100.0:.1f}% de utilizacion. Recomendacion: sumar una segunda estacion "
        "antes que\n"
        "tocar la politica de inventario."
    )


def _bloque_problema2(m: Dict) -> str:
    """Analisis manuscrito del Problema 2, alrededor de 90 palabras."""
    # Coeficiente de disipacion necesario para bajar el equilibrio medio a 65 C.
    p_total = m["p_idle_w"] + m["k_carga_w"] * m["trafico_media_nominal"]
    h_objetivo = p_total / (65.0 - m["temp_ambiente_c"])
    return (
        "PROBLEMA 2. CLUSTER DE SERVIDORES (SIMULACION CONTINUA)\n"
        "Balance termico C*dT/dt=P_idle+k*trafico-h*(T-T_amb), integrado con RK4 a paso de\n"
        f"{m['paso_integracion_s']:.0f} s. Trafico Normal({m['trafico_media_nominal']:.0f},"
        f"{m['trafico_desv_nominal']:.0f}) truncado a [{m['trafico_min_gbps']:.0f},"
        f"{m['trafico_max_gbps']:.0f}] Gbps, resorteado cada "
        f"{m['intervalo_resorteo_s']:.0f} s.\n"
        "Equilibrio T_eq=T_amb+(P_idle+k*trafico)/h da "
        f"{m['temp_equilibrio_media_c']:.0f} C con trafico medio, justo la\n"
        f"temperatura de diseno. Simulado: media {m['temp_media_c']:.1f} C, desviacion "
        f"{m['temp_desviacion_c']:.1f} C, rango {m['temp_min_c']:.1f} a\n"
        f"{m['temp_max_c']:.1f} C. El throttling estuvo activo {m['pct_tiempo_throttling']:.1f}% "
        "del tiempo y la eficiencia\n"
        f"global cayo a {m['eficiencia_global_pct']:.1f}%, procesando {m['tb_procesados']:.2f} TB. "
        "El diseno no deja margen termico.\n"
        f"Recomendacion: subir h de {m['h_disip']:.0f} a {h_objetivo:.1f} W/C para bajar T_eq a "
        "65 C."
    )


def generar_conclusiones(metricas_p1: Dict, metricas_p2: Dict) -> str:
    """
    Arma el texto completo de conclusiones con los numeros reales de la corrida.

    Falla con ValidacionError si se supera el tope de 200 palabras: entregar un
    archivo fuera de contrato es peor que abortar, porque el tope es un requisito
    del enunciado y nadie lo notaria al leer el .txt.
    """
    if not metricas_p1 or not metricas_p2:
        raise ValidacionError(
            "Se necesitan las metricas de los DOS problemas para generar las conclusiones. "
            "Corra la opcion [3] del menu o main.py --problema ambos."
        )

    texto = "\n\n".join(
        [
            "CONCLUSIONES - PARCIAL III",
            _bloque_problema1(metricas_p1),
            _bloque_problema2(metricas_p2),
        ]
    )

    palabras = contar_palabras(texto)
    if palabras > TOPE_PALABRAS:
        raise ValidacionError(
            f"El texto de conclusiones tiene {palabras} palabras y el tope duro es "
            f"{TOPE_PALABRAS}. Acorte los bloques antes de entregar."
        )
    return texto


def exportar_conclusiones(
    metricas_p1: Dict,
    metricas_p2: Dict,
    destino: Union[str, Path, None] = None,
) -> Path:
    """Genera el texto y lo escribe en outputs/conclusiones_manuscritas.txt."""
    texto = generar_conclusiones(metricas_p1, metricas_p2)
    ruta = Path(destino) if destino is not None else asegurar_directorio_salidas() / ARCHIVO_CONCLUSIONES
    if not ruta.is_absolute() and len(ruta.parts) == 1:
        ruta = asegurar_directorio_salidas() / ruta.name
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto.rstrip() + "\n", encoding="utf-8")
    return ruta


def _selfcheck() -> None:
    """Verifica el tope de palabras y la ausencia de marcas de formato."""
    from src.simulation.continuous_sim import ClusterSimulation
    from src.simulation.discrete_sim import FabricaSimulation

    m1 = FabricaSimulation(semilla=2026).ejecutar(8.0)
    m2 = ClusterSimulation(semilla=2026).ejecutar(8.0)
    texto = generar_conclusiones(m1, m2)

    palabras = contar_palabras(texto)
    assert palabras <= TOPE_PALABRAS, f"se paso del tope: {palabras} palabras"

    # Texto plano estricto: ni markdown, ni LaTeX, ni tablas
    for prohibido in ("**", "##", "`", "$", "|", "\\("):
        assert prohibido not in texto, f"marca de formato prohibida en el texto: {prohibido!r}"

    # Ni vinetas al inicio de linea (se revisa por linea, un guion interno es valido)
    for linea in texto.splitlines():
        assert not linea.lstrip().startswith(("- ", "* ", "+ ")), f"vineta en: {linea!r}"

    # Los numeros deben venir de la corrida, no estar hardcodeados
    assert f"{m2['temp_media_c']:.1f} C" in texto
    assert f"{m1['paradas_por_falta_stock']}" in texto
    assert "rho=lambda/mu" in texto
    assert "Wq=lambda/(mu*(mu-lambda))" in texto

    try:
        generar_conclusiones({}, m2)
    except ValidacionError:
        pass
    else:
        raise AssertionError("generar_conclusiones acepto metricas vacias")

    print(f"selfcheck conclusiones: OK ({palabras} palabras, tope {TOPE_PALABRAS})")


if __name__ == "__main__":
    _selfcheck()
