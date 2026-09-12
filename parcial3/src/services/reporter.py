"""
Servicio de generacion y exportacion de reportes en texto plano (.txt).

Cumple el requisito del enunciado de "generar archivos de texto". Un reporte por
problema, con los parametros de entrada, las metricas obtenidas y el contraste
contra los valores teoricos. La respuesta de la API de IA se anexa despues al
final del mismo archivo con anexar_seccion.

Regla de formato: texto plano ASCII, sin markdown y sin emojis.
"""

from pathlib import Path
from typing import Dict, List, Union

from src.core.mm1_analytical import ModeloMM1
from src.utils.config import EFICIENCIA_BASE, asegurar_directorio_salidas

ANCHO = 70
SEPARADOR = "=" * ANCHO
SUBSEPARADOR = "-" * ANCHO

ENCABEZADO_INSTITUCIONAL = [
    SEPARADOR,
    "UNIVERSIDAD JOSE ANTONIO PAEZ - FACULTAD DE INGENIERIA",
    "ESCUELA DE INGENIERIA EN COMPUTACION",
    "METODOS CUANTITATIVOS - PARCIAL III - SIMULACION",
    SEPARADOR,
]


class ReportService:
    """Compila y persiste los reportes estructurados de texto plano."""

    # ------------------------------------------------------------------
    # PROBLEMA 1
    # ------------------------------------------------------------------

    @staticmethod
    def generar_texto_problema1(metricas: Dict) -> str:
        """Arma el reporte del Problema 1 a partir del diccionario de metricas."""
        m = metricas
        modelo = ModeloMM1(lamb=m["lambda_ordenes_hora"], mu=m["mu_laptops_hora"])

        lineas: List[str] = list(ENCABEZADO_INSTITUCIONAL)
        lineas += [
            "PROBLEMA 1: FABRICA DE LAPTOPS",
            "Simulacion de eventos discretos (SimPy) sobre una cola M/M/1 con",
            "inventario de procesadores bajo politica de revision continua (s, Q).",
            SEPARADOR,
            "",
            "1. PARAMETROS DE ENTRADA",
            SUBSEPARADOR,
            f"Periodo simulado                      : {m['tiempo_simulado_horas']:.2f} horas "
            f"({m['tiempo_simulado_s']:.0f} s)",
            f"Semilla de reproducibilidad           : {m['semilla']}",
            f"Tasa de llegada de ordenes (lambda)   : {m['lambda_ordenes_hora']:.2f} ordenes/hora",
            f"Media de ensamblaje                   : {m['media_ensamblaje_min']:.2f} min/laptop",
            f"Tasa de servicio (mu)                 : {m['mu_laptops_hora']:.2f} laptops/hora",
            f"Estaciones de ensamblaje (c)          : {m['servidores']}",
            f"Stock inicial de procesadores         : {m['stock_inicial']} unidades  [SUPUESTO PROPIO]",
            f"Umbral critico de reposicion (s)      : {m['umbral_critico_s']} unidades",
            f"Tamano del lote de reposicion (Q)     : {m['lote_q']} unidades",
            f"Lead time del proveedor               : {m['lead_time_min']:.2f} min",
            f"Consumo por laptop ensamblada         : {m['consumo_por_laptop']} procesador(es)  [SUPUESTO PROPIO]",
            f"Lote de produccion de referencia      : {m['lote_produccion']} laptops",
            "",
            "NOTA SOBRE LOS SUPUESTOS: el enunciado no fija el stock inicial de",
            "procesadores ni cuantos consume cada laptop. Se adoptaron 50 unidades",
            "iniciales (un lote completo) y 1 procesador por laptop. Los dos valores",
            "quedan declarados aca de forma explicita por transparencia metodologica.",
            "",
            "2. VALORES TEORICOS M/M/1 (FORMULAS CERRADAS)",
            SUBSEPARADOR,
        ]

        for nombre, formula, sustitucion, resultado in modelo.pasos_desarrollados():
            lineas.append(f"{nombre}")
            lineas.append(f"    {formula}")
            lineas.append(f"    {sustitucion}")
            lineas.append(f"    {resultado}")

        lineas += [
            "",
            "3. METRICAS OBTENIDAS EN LA SIMULACION",
            SUBSEPARADOR,
            f"Ordenes generadas                     : {m['ordenes_generadas']}",
            f"Laptops completadas                   : {m['ordenes_completadas']}",
            f"Ordenes aun en el sistema al cierre   : {m['ordenes_en_sistema']}",
            "",
            "Tiempo de espera promedio de las ordenes (Wq):",
            f"    Simulado                          : {m['wq_promedio_min']:.4f} min "
            f"({m['wq_promedio_horas']:.6f} h)",
            f"    Teorico M/M/1                     : {m['teorico_wq_min']:.4f} min",
            f"    Desviacion contra el teorico      : "
            f"{ReportService._desvio_pct(m['wq_promedio_min'], m['teorico_wq_min'])}",
            "",
            "Tiempo promedio en el sistema (W):",
            f"    Simulado                          : {m['w_promedio_min']:.4f} min",
            f"    Teorico M/M/1                     : {m['teorico_w_min']:.4f} min",
            "",
            "Ocupacion promedio:",
            f"    Ordenes en cola (Lq) simulado     : {m['lq_promedio']:.4f}",
            f"    Ordenes en cola (Lq) teorico      : {m['teorico_lq']:.4f}",
            f"    Ordenes en sistema (L) simulado   : {m['l_promedio']:.4f}",
            f"    Ordenes en sistema (L) teorico    : {m['teorico_l']:.4f}",
            f"    Utilizacion de la estacion        : {m['utilizacion_estacion_pct']:.2f} % "
            f"(rho teorico {m['teorico_rho'] * 100.0:.2f} %)",
            "",
            "4. TIEMPO TOTAL QUE TOMA DESPACHAR UN LOTE",
            SUBSEPARADOR,
            "El enunciado admite dos lecturas de esta metrica. Se reportan las dos,",
            "etiquetadas sin ambiguedad:",
            "",
            "(a) Ciclo de reposicion de componentes",
            "    Tiempo desde que se dispara el pedido al proveedor hasta que",
            f"    ingresan las {m['lote_q']} unidades al inventario.",
            f"    Promedio observado                : {m['ciclo_reposicion_promedio_min']:.4f} min",
            f"    Ciclos observados                 : {m['ciclos_reposicion_observados']}",
            f"    Valor nominal (lead time)         : {m['lead_time_min']:.2f} min",
            "",
            "(b) Tiempo de despacho de un lote de produccion",
            f"    Tiempo en completar {m['lote_produccion']} laptops terminadas.",
            f"    Promedio observado                : {m['despacho_lote_promedio_min']:.4f} min "
            f"({m['despacho_lote_promedio_min'] / 60.0:.4f} h)",
            f"    Lotes completos observados        : {m['lotes_produccion_observados']}",
            "",
            "5. INVENTARIO Y CONTINUIDAD DE LA LINEA",
            SUBSEPARADOR,
            f"Veces que la linea se detuvo por falta de stock : {m['paradas_por_falta_stock']}",
            f"Ordenes retrasadas por falta de inventario      : {m['ordenes_retrasadas_por_stock']}",
            f"Tiempo total de linea detenida                  : {m['tiempo_linea_detenida_min']:.4f} min",
            f"Pedidos de reposicion disparados                : {m['pedidos_disparados']}",
            f"Lotes recibidos del proveedor                   : {m['lotes_recibidos']}",
            f"Unidades consumidas                             : {m['unidades_consumidas']}",
            f"Unidades recibidas                              : {m['unidades_recibidas']}",
            f"Nivel de stock al cierre                        : {m['stock_actual']} unidades",
            f"Nivel minimo alcanzado                          : {m['stock_minimo']} unidades",
            "",
            "Eficiencia en el reabastecimiento:",
            "    Definicion adoptada: fraccion del tiempo simulado en que la linea",
            "    NO estuvo detenida por falta de procesadores.",
            "        eficiencia = 1 - (tiempo_linea_detenida / tiempo_total)",
            f"    Valor obtenido                    : {m['eficiencia_reabastecimiento_pct']:.2f} %",
            "",
            "6. LECTURA DEL RESULTADO",
            SUBSEPARADOR,
        ]
        lineas += ReportService._lectura_problema1(m)
        lineas += ["", SEPARADOR]
        return "\n".join(lineas)

    @staticmethod
    def _lectura_problema1(m: Dict) -> List[str]:
        """Interpretacion cuantitativa automatica de los numeros del Problema 1."""
        consumo_hora = m["lambda_ordenes_hora"] * m["consumo_por_laptop"]
        consumo_lead = consumo_hora * (m["lead_time_min"] / 60.0)

        texto = [
            f"La estacion opera con rho = {m['teorico_rho']:.4f}, es decir al "
            f"{m['teorico_rho'] * 100.0:.1f} % de su capacidad.",
            "Con un solo servidor y una utilizacion tan alta, la cola es sensible a",
            "cualquier incremento de lambda: el cuello de botella del sistema es la",
            "estacion de ensamblaje, no el inventario.",
            "",
            "Sobre el inventario, el consumo esperado durante el lead time es:",
            f"    consumo = lambda * consumo_por_laptop * lead_time",
            f"    consumo = {m['lambda_ordenes_hora']:.2f} * {m['consumo_por_laptop']} * "
            f"{m['lead_time_min'] / 60.0:.4f} h = {consumo_lead:.2f} unidades",
            f"Ese valor esta muy por debajo del umbral critico s = {m['umbral_critico_s']}, "
            "de modo que",
            "el pedido llega mucho antes de que el stock se agote.",
        ]

        if m["paradas_por_falta_stock"] == 0:
            texto += [
                "",
                "Por eso la simulacion reporta CERO paradas de linea por falta de stock.",
                "No es un defecto del modelo ni un error de la corrida: es la conclusion",
                "correcta con los parametros del enunciado. El inventario esta",
                "sobredimensionado respecto del consumo real, y la politica (s, Q) podria",
                "relajarse sin riesgo de desabastecimiento.",
            ]
        else:
            texto += [
                "",
                f"La simulacion registro {m['paradas_por_falta_stock']} parada(s) de linea "
                "por falta de stock,",
                f"con {m['tiempo_linea_detenida_min']:.2f} min de produccion perdida. "
                "Conviene elevar el",
                "umbral critico s o reducir el lead time del proveedor.",
            ]
        return texto

    # ------------------------------------------------------------------
    # PROBLEMA 2
    # ------------------------------------------------------------------

    @staticmethod
    def generar_texto_problema2(metricas: Dict) -> str:
        """Arma el reporte del Problema 2 a partir del diccionario de metricas."""
        m = metricas
        lineas: List[str] = list(ENCABEZADO_INSTITUCIONAL)
        lineas += [
            "PROBLEMA 2: CLUSTER DE SERVIDORES",
            "Simulacion continua del balance termico y del rendimiento, resuelta",
            "con Runge-Kutta de cuarto orden.",
            SEPARADOR,
            "",
            "1. PARAMETROS DE ENTRADA",
            SUBSEPARADOR,
            f"Periodo simulado                      : {m['tiempo_simulado_horas']:.2f} horas "
            f"({m['tiempo_simulado_s']:.0f} s)",
            f"Semilla de reproducibilidad           : {m['semilla']}",
            f"Paso de integracion RK4               : {m['paso_integracion_s']:.2f} s",
            f"Re-sorteo del trafico                 : cada {m['intervalo_resorteo_s']:.0f} s "
            "(retencion de orden cero)",
            f"Trafico entrante                      : Normal({m['trafico_media_nominal']:.1f}, "
            f"{m['trafico_desv_nominal']:.1f}) truncada a "
            f"[{m['trafico_min_gbps']:.1f}, {m['trafico_max_gbps']:.1f}] Gbps",
            f"Temperatura ambiente (T_amb)          : {m['temp_ambiente_c']:.2f} C",
            f"Temperatura de diseno                 : {m['temp_diseno_c']:.2f} C",
            f"Temperatura inicial                   : {m['temp_inicial_c']:.2f} C",
            f"Coeficiente de disipacion (h)         : {m['h_disip']:.2f} W/C",
            f"Potencia en reposo (P_idle)           : {m['p_idle_w']:.2f} W",
            f"Potencia por Gbps (k)                 : {m['k_carga_w']:.2f} W/Gbps",
            f"Capacidad termica (C)                 : {m['c_termica']:.2f} J/C",
            f"Constante de tiempo (tau = C/h)       : {m['tau_s']:.2f} s",
            "",
            "2. MODELO MATEMATICO",
            SUBSEPARADOR,
            "Balance termico de primer orden:",
            "    C * dT/dt = P_idle + k * trafico - h * (T - T_amb)",
            "",
            "Temperatura de equilibrio con trafico constante:",
            "    T_eq = T_amb + (P_idle + k * trafico) / h",
            f"    Trafico 1 Gbps -> T_eq = {m['temp_ambiente_c'] + (m['p_idle_w'] + m['k_carga_w'] * 1.0) / m['h_disip']:.2f} C",
            f"    Trafico 3 Gbps -> T_eq = {m['temp_equilibrio_media_c']:.2f} C  (temperatura de diseno)",
            f"    Trafico 5 Gbps -> T_eq = {m['temp_ambiente_c'] + (m['p_idle_w'] + m['k_carga_w'] * 5.0) / m['h_disip']:.2f} C",
            "",
            "Eficiencia con thermal throttling:",
            "    eta(T) = 0.90                                si T <= 70",
            "    eta(T) = max(0.30, 0.90 - 0.02 * (T - 70))   si T > 70",
            "",
            "Rendimiento entregado:",
            "    throughput = trafico * eta(T)",
            "    datos acumulados = integral de throughput en el tiempo",
            "",
            "3. DATOS PROCESADOS",
            SUBSEPARADOR,
            f"Total en Gigabits                     : {m['gb_procesados']:.2f} Gb",
            f"Total en Gigabytes                    : {m['gb_procesados_bytes']:.2f} GB",
            f"Total en Terabytes                    : {m['tb_procesados']:.4f} TB",
            "",
            "4. VARIABILIDAD DE LA TEMPERATURA",
            SUBSEPARADOR,
            f"Temperatura media                     : {m['temp_media_c']:.4f} C",
            f"Desviacion estandar                   : {m['temp_desviacion_c']:.4f} C",
            f"Temperatura minima                    : {m['temp_min_c']:.4f} C",
            f"Temperatura maxima                    : {m['temp_max_c']:.4f} C",
            f"Temperatura al cierre                 : {m['temp_actual_c']:.4f} C",
            f"Muestras tomadas (1 por segundo)      : {m['muestras_temperatura']}",
            "",
            "5. EFICIENCIA GLOBAL DE LA RED",
            SUBSEPARADOR,
            f"Eficiencia global (eta ponderada en el tiempo) : {m['eficiencia_global_pct']:.2f} %",
            f"Trafico medio ofrecido                        : {m['trafico_medio_gbps']:.4f} Gbps",
            f"Throughput medio entregado                    : {m['throughput_medio_gbps']:.4f} Gbps",
            f"Perdida TOTAL contra el trafico ofrecido      : {m['perdida_total_pct']:.2f} %",
            f"   de la cual, ineficiencia base (eta = 0.90) : {(100.0 - EFICIENCIA_BASE * 100.0):.2f} %",
            f"   de la cual, atribuible al throttling       : {m['perdida_por_throttling_pct']:.2f} %",
            "",
            "   La ineficiencia base existe aunque el cluster este frio: eta vale 0.90",
            "   incluso a 70 C o menos. Solo la segunda componente es recuperable",
            "   mejorando la refrigeracion.",
            "",
            "6. THERMAL THROTTLING",
            SUBSEPARADOR,
            f"Porcentaje del tiempo con throttling activo (T > "
            f"{m['temp_diseno_c']:.0f} C) : {m['pct_tiempo_throttling']:.2f} %",
            f"Tiempo acumulado con throttling               : {m['segundos_throttling']:.0f} s "
            f"({m['segundos_throttling'] / 3600.0:.2f} h)",
            "",
            "7. LECTURA DEL RESULTADO",
            SUBSEPARADOR,
        ]
        lineas += ReportService._lectura_problema2(m)
        lineas += ["", SEPARADOR]
        return "\n".join(lineas)

    @staticmethod
    def _lectura_problema2(m: Dict) -> List[str]:
        """Interpretacion cuantitativa automatica de los numeros del Problema 2."""
        texto = [
            f"El cluster esta calibrado para que el trafico medio de "
            f"{m['trafico_media_nominal']:.1f} Gbps lo",
            f"deje exactamente en la temperatura de diseno de {m['temp_diseno_c']:.0f} C. La media "
            f"observada fue de",
            f"{m['temp_media_c']:.2f} C, consistente con esa calibracion.",
            "",
            f"La desviacion estandar de {m['temp_desviacion_c']:.2f} C refleja la variabilidad del "
            "trafico filtrada",
            f"por la inercia termica del sistema (tau = {m['tau_s']:.0f} s). La temperatura se movio",
            f"entre {m['temp_min_c']:.2f} C y {m['temp_max_c']:.2f} C, dentro de los equilibrios "
            "extremos que",
            "corresponden a 1 y 5 Gbps.",
            "",
        ]

        pct = m["pct_tiempo_throttling"]
        if pct <= 0.0:
            texto += [
                "El throttling no se activo en ningun momento: la refrigeracion sostuvo",
                "la eficiencia nominal del 90 % durante toda la corrida.",
            ]
        elif pct < 60.0:
            texto += [
                f"El throttling estuvo activo el {pct:.2f} % del tiempo. Como el diseno deja el",
                "equilibrio medio justo en el limite de 70 C, cualquier pico de trafico por",
                "encima de la media empuja al sistema a la zona de penalizacion. El diseno",
                "no tiene margen termico.",
            ]
        else:
            texto += [
                f"El throttling estuvo activo el {pct:.2f} % del tiempo, lo que indica que el",
                "punto de operacion esta demasiado cerca del limite termico y el cluster",
                "pasa la mayor parte del tiempo entregando menos de su capacidad nominal.",
            ]

        texto += [
            "",
            f"El resultado neto es una eficiencia global del {m['eficiencia_global_pct']:.2f} % frente "
            "al 90 % nominal,",
            f"es decir una perdida del {m['perdida_por_throttling_pct']:.2f} % atribuible al throttling. "
            "Contra el trafico",
            f"ofrecido la perdida total es del {m['perdida_total_pct']:.2f} %, pero esa cifra incluye los "
            f"{(100.0 - EFICIENCIA_BASE * 100.0):.0f} puntos",
            "de ineficiencia base del equipo, que no dependen de la temperatura.",
            "Aumentar el coeficiente de disipacion h es la palanca directa: baja T_eq de",
            "forma proporcional y recupera eficiencia sin tocar la carga.",
        ]
        return texto

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------

    @staticmethod
    def _desvio_pct(simulado: float, teorico: float) -> str:
        """Desviacion porcentual del valor simulado contra el teorico."""
        if teorico == 0:
            return "no aplica (teorico = 0)"
        return f"{(simulado - teorico) / teorico * 100.0:+.2f} %"

    @classmethod
    def exportar_reporte_txt(cls, contenido: str, destino: Union[str, Path]) -> Path:
        """
        Escribe el reporte en un archivo .txt plano y devuelve la ruta final.

        Si el destino es un nombre suelto, se resuelve dentro del directorio de
        salidas del proyecto.
        """
        ruta = Path(destino)
        if not ruta.is_absolute() and len(ruta.parts) == 1:
            ruta = asegurar_directorio_salidas() / ruta.name
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(contenido.rstrip() + "\n", encoding="utf-8")
        return ruta

    @classmethod
    def anexar_seccion(cls, ruta: Union[str, Path], titulo: str, contenido: str) -> Path:
        """Anexa un bloque titulado al final de un archivo de texto ya existente."""
        ruta_p = Path(ruta)
        if not ruta_p.exists():
            raise FileNotFoundError(
                f"No se puede anexar a un reporte inexistente: {ruta_p}. "
                "Genere primero el reporte con exportar_reporte_txt."
            )
        bloque = (
            "\n\n"
            + SEPARADOR
            + "\n"
            + f"{titulo.upper()}\n"
            + SEPARADOR
            + "\n"
            + f"{contenido.strip()}\n"
            + SEPARADOR
            + "\n"
        )
        with open(ruta_p, "a", encoding="utf-8") as f:
            f.write(bloque)
        return ruta_p


def _selfcheck() -> None:
    """Verifica que los dos reportes se generen y que anexar_seccion agregue al final."""
    import tempfile

    from src.simulation.continuous_sim import ClusterSimulation
    from src.simulation.discrete_sim import FabricaSimulation

    m1 = FabricaSimulation(semilla=1).ejecutar(1.0)
    texto1 = ReportService.generar_texto_problema1(m1)
    assert "PROBLEMA 1: FABRICA DE LAPTOPS" in texto1
    assert "Ciclo de reposicion de componentes" in texto1
    assert "Tiempo de despacho de un lote de produccion" in texto1
    assert "Eficiencia en el reabastecimiento" in texto1

    m2 = ClusterSimulation(semilla=1).ejecutar(1.0)
    texto2 = ReportService.generar_texto_problema2(m2)
    assert "PROBLEMA 2: CLUSTER DE SERVIDORES" in texto2
    assert "Terabytes" in texto2
    assert "throttling activo" in texto2

    with tempfile.TemporaryDirectory() as tmp:
        ruta = ReportService.exportar_reporte_txt(texto1, Path(tmp) / "r1.txt")
        assert ruta.exists()
        original = ruta.read_text(encoding="utf-8")
        ReportService.anexar_seccion(ruta, "respuesta de la api", "Conclusion de prueba.")
        final = ruta.read_text(encoding="utf-8")
        assert final.startswith(original.rstrip()[:200])
        assert final.index("Conclusion de prueba.") > len(original) - 10

    print("selfcheck reporter: OK")


if __name__ == "__main__":
    _selfcheck()
