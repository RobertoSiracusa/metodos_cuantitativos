"""Servicio de formateo y exportacion de reportes tecnicos para la Tarea 6."""

from __future__ import annotations

import os
from typing import List
from ..core.base import ResultadoOptimizacion
from ..core.problema3_gradiente import PasoGradiente


SEPARADOR_GRUESO = "=" * 80
SEPARADOR_FINO = "-" * 80


def formatear_problema_1(res: ResultadoOptimizacion) -> str:
    """Formatea el reporte del Problema 1: Minimizacion sin restricciones."""
    lineas = [
        SEPARADOR_GRUESO,
        "PROBLEMA 1: PROBLEMA SIN RESTRICCIONES (DERIVADAS PARCIALES)",
        SEPARADOR_GRUESO,
        "Modelo Matematico:",
        "  Minimizar C(x, y) = x^2 + y^2 - 4x - 6y + 20",
        "",
        "Condiciones de Primer Orden (CPO):",
        "  dC/dx = 2x - 4 = 0   ==>   x* = 2.0000",
        "  dC/dy = 2y - 6 = 0   ==>   y* = 3.0000",
        "",
        "Condiciones de Segundo Orden (CSO - Matriz Hessiana):",
        "  H = [[ 2.0,  0.0 ],",
        "       [ 0.0,  2.0 ]]",
        f"  Menor principal D1 = {res.detalles.get('d1_hessiano', 2.0):.4f} > 0",
        f"  Determinante det(H) = {res.detalles.get('det_hessiano', 4.0):.4f} > 0",
        f"  Clasificacion: {res.detalles.get('clasificacion_punto', 'Minimo global estricto')}",
        "",
        "Resultados Optimos:",
        f"  Variable x* : {res.variables_optimas['x']:.4f}",
        f"  Variable y* : {res.variables_optimas['y']:.4f}",
        f"  Costo Minimo C(x*, y*): {res.valor_optimo:.4f}",
        f"  Forma canonica: C(x, y) = (x - 2)^2 + (y - 3)^2 + 7 >= 7",
        "",
        "Conclusion:",
        f"  {res.conclusion}",
        "",
    ]
    return "\n".join(lineas)


def formatear_problema_2(res: ResultadoOptimizacion) -> str:
    """Formatea el reporte del Problema 2: Metodo de Lagrange."""
    lineas = [
        SEPARADOR_GRUESO,
        "PROBLEMA 2: METODO DE LAGRANGE (RESTRICCION DE IGUALDAD)",
        SEPARADOR_GRUESO,
        "Modelo Matematico:",
        "  Maximizar A(x, y) = x * y",
        "  Sujeto a: 2x + 2y = 40",
        "",
        "Lagrangiano:",
        "  L(x, y, lambda) = x*y - lambda*(2x + 2y - 40)",
        "",
        "Condiciones de Primer Orden (CPO):",
        "  dL/dx = y - 2*lambda = 0       ==>  y = 2*lambda",
        "  dL/dy = x - 2*lambda = 0       ==>  x = 2*lambda",
        "  dL/dlambda = -(2x + 2y - 40) = 0 ==>  2(2*lambda) + 2(2*lambda) = 40 ==> lambda* = 5.0000",
        "",
        "Condiciones de Segundo Orden (Hessiano Orlado):",
        "  H_bar = [[ 0,  2,  2 ],",
        "           [ 2,  0,  1 ],",
        "           [ 2,  1,  0 ]]",
        f"  det(H_bar) = {res.detalles.get('det_hessiano_orlado', 8.0):.4f} > 0 ==> Maximo local estricto garantizado",
        "",
        "Resultados Optimos:",
        f"  Dimension x* : {res.variables_optimas['x']:.4f} unidades",
        f"  Dimension y* : {res.variables_optimas['y']:.4f} unidades (Configuracion: Cuadrado)",
        f"  Area Maxima A(x*, y*): {res.valor_optimo:.4f} unidades cuadradas",
        f"  Multiplicador lambda*: {res.multiplicadores.get('lambda', 0.0):.4f}",
        f"  Perimetro verificado : {res.detalles.get('perimetro_verificado', 40.0):.4f} unidades",
        f"  Sensibilidad marginal (dA*/dP): {res.detalles.get('sensibilidad_dA_dP', 5.0):.4f}",
        "",
        "Conclusion:",
        f"  {res.conclusion}",
        "",
    ]
    return "\n".join(lineas)


def formatear_problema_3(res: ResultadoOptimizacion, historial: List[PasoGradiente]) -> str:
    """Formatea el reporte del Problema 3: Metodo del Gradiente."""
    lineas = [
        SEPARADOR_GRUESO,
        "PROBLEMA 3: METODO DEL GRADIENTE (BUSQUEDA ITERATIVA)",
        SEPARADOR_GRUESO,
        "Modelo Matematico:",
        "  Maximizar f(x, y) = -(x^2 + y^2) + 4x + 6y",
        f"  Punto inicial: {res.detalles.get('punto_inicial', (0.0, 0.0))}",
        "  Regla de actualizacion: x_{k+1} = x_k + alfa * grad(f(x_k))",
        "  Gradiente: grad(f) = [ -2x + 4,  -2y + 6 ]",
        "",
        "Tabla de Iteraciones de Ascenso de Gradiente:",
        f"{'Iter':<6}{'x':<10}{'y':<10}{'f(x, y)':<12}{'grad_x':<10}{'grad_y':<10}{'||grad||':<12}",
        SEPARADOR_FINO,
    ]

    # Muestra los primeros pasos, algunos intermedios y el final
    total = len(historial)
    pasos_a_mostrar = []
    for i, p in enumerate(historial):
        if i <= 5 or i % 5 == 0 or i == total - 1:
            if not pasos_a_mostrar or pasos_a_mostrar[-1].iteracion != p.iteracion:
                pasos_a_mostrar.append(p)

    for p in pasos_a_mostrar:
        lineas.append(
            f"{p.iteracion:<6}{p.x:<10.4f}{p.y:<10.4f}{p.f_val:<12.4f}{p.grad_x:<10.4f}{p.grad_y:<10.4f}{p.norma_gradiente:<12.2e}"
        )

    opt_teo = res.detalles.get("optimo_analitico", {"x": 2.0, "y": 3.0, "f": 13.0})
    lineas.extend([
        SEPARADOR_FINO,
        "",
        "Resultados Optimos Obtenidos:",
        f"  Punto final (x, y)     : ({res.variables_optimas['x']:.4f}, {res.variables_optimas['y']:.4f})",
        f"  Valor maximo f(x, y)   : {res.valor_optimo:.4f}",
        f"  Iteraciones ejecutadas : {res.detalles.get('iteraciones_totales', len(historial)-1)}",
        f"  Norma gradiente final  : {res.detalles.get('norma_gradiente_final', 0.0):.2e}",
        f"  Optimo analitico exacto: ({opt_teo['x']:.4f}, {opt_teo['y']:.4f}) con f* = {opt_teo['f']:.4f}",
        f"  Paso optimo analitico  : alfa* = 0.5 (convergencia en 1 iteracion exacta)",
        "",
        "Conclusion:",
        f"  {res.conclusion}",
        "",
    ])
    return "\n".join(lineas)


def formatear_problema_4(res: ResultadoOptimizacion) -> str:
    """Formatea el reporte del Problema 4: Multiples Restricciones KKT."""
    det = res.detalles
    lineas = [
        SEPARADOR_GRUESO,
        "PROBLEMA 4: PROBLEMA CON MULTIPLES RESTRICCIONES (CONDICIONES KKT)",
        SEPARADOR_GRUESO,
        "Modelo Matematico:",
        "  Maximizar G(x, y) = 5x + 8y - 0.1x^2 - 0.2y^2",
        "  Sujeto a:",
        "    g1(x, y) = x + y - 40 <= 0",
        "    g2(x, y) = -x <= 0",
        "    g3(x, y) = -y <= 0",
        "",
        "Diagnostico de Factibilidad sin restricciones:",
        f"  Optimo no restringido : ({det['optimo_sin_restricciones']['x']:.2f}, {det['optimo_sin_restricciones']['y']:.2f})",
        f"  Suma x + y            : {det['optimo_sin_restricciones']['suma']:.2f} > 40.00 (Infactible en el dominio)",
        f"  Estado de restriccion : {det['restriccion_activa']}",
        "",
        "Sistema Karush-Kuhn-Tucker (KKT):",
        "  Estacionariedad:",
        "    5 - 0.2x - mu1 = 0   ==>  mu1 = 5 - 0.2x",
        "    8 - 0.4y - mu1 = 0   ==>  mu1 = 8 - 0.4y",
        "  Activacion de frontera:",
        "    x + y = 40           ==>  y = 40 - x",
        "  Resolviendo:",
        "    5 - 0.2x = 8 - 0.4(40 - x) ==> 0.6x = 13 ==> x* = 65/3 = 21.6667",
        "    y* = 40 - 65/3 = 55/3 = 18.3333",
        "    mu1 = 5 - 0.2(65/3) = 2/3 = 0.6667 > 0",
        "",
        "Resultados Optimos:",
        f"  Variable x* : {res.variables_optimas['x']:.4f} (Exacto: {det.get('fraccion_exacta_x', '65/3')})",
        f"  Variable y* : {res.variables_optimas['y']:.4f} (Exacto: {det.get('fraccion_exacta_y', '55/3')})",
        f"  Ganancia Maxima G(x*, y*): {res.valor_optimo:.4f} (Exacto: {det.get('fraccion_exacta_ganancia', '845/6')})",
        f"  Multiplicador mu1 (Capacidad): {res.multiplicadores.get('mu_capacidad (mu1)', 0.0):.4f} (Exacto: {det.get('fraccion_exacta_mu1', '2/3')})",
        f"  Multiplicadores mu2 (x>=0)   : {res.multiplicadores.get('mu_no_neg_x (mu2)', 0.0):.4f} (Holgura estricta)",
        f"  Multiplicadores mu3 (y>=0)   : {res.multiplicadores.get('mu_no_neg_y (mu3)', 0.0):.4f} (Holgura estricta)",
        f"  Sensibilidad marginal (dG*/dB): {det.get('sensibilidad_dG_dB', 0.6667):.4f}",
        "",
        "Conclusion:",
        f"  {res.conclusion}",
        "",
    ]
    return "\n".join(lineas)


def formatear_problema_5(res: ResultadoOptimizacion) -> str:
    """Formatea el reporte del Problema 5: Cilindro Fisico de Volumen Fijo."""
    det = res.detalles
    lineas = [
        SEPARADOR_GRUESO,
        "PROBLEMA 5: PROBLEMA DE VOLUMEN MINIMO (DIMENSIONAMIENTO FISICO DE CILINDRO)",
        SEPARADOR_GRUESO,
        "Modelo Matematico:",
        "  Minimizar Area Superficial A(r, h) = 2*pi*r^2 + 2*pi*r*h",
        "  Sujeto a: V(r, h) = pi*r^2*h = 500 cm^3",
        "",
        "Reduccion Unidimensional y Derivadas:",
        "  h(r) = 500 / (pi * r^2)",
        "  A(r) = 2*pi*r^2 + 1000 / r",
        "  A'(r) = 4*pi*r - 1000 / r^2 = 0  ==>  r* = cbrt(250 / pi)",
        "  h* = 500 / (pi * (r*)^2) = 2 * r*",
        f"  A''(r*) = {det.get('segunda_derivada', 37.6991):.4f} > 0 ==> Minimo global certificado",
        "",
        "Resultados Optimos:",
        f"  Radio optimo (r*)    : {res.variables_optimas['radio_r']:.4f} cm",
        f"  Altura optima (h*)   : {res.variables_optimas['altura_h']:.4f} cm",
        f"  Diametro optimo (d*) : {det.get('diametro', 0.0):.4f} cm",
        f"  Relacion geometrica  : {det.get('relacion_geometrica', 'h = 2r')}",
        f"  Area Superficial Min.: {res.valor_optimo:.4f} cm^2",
        f"  Volumen verificado   : {det.get('volumen_verificado', 500.0):.4f} cm^3",
        f"  Multiplicador lambda : {res.multiplicadores.get('lambda_volumen', 0.0):.4f} cm^(-1)",
        f"  Sensibilidad (dA*/dV): {det.get('sensibilidad_dA_dV', 0.0):.4f} cm^2 / cm^3",
        "",
        "Conclusion:",
        f"  {res.conclusion}",
        "",
    ]
    return "\n".join(lineas)


def generar_reporte_completo(
    res1: ResultadoOptimizacion,
    res2: ResultadoOptimizacion,
    res3: ResultadoOptimizacion,
    historial3: List[PasoGradiente],
    res4: ResultadoOptimizacion,
    res5: ResultadoOptimizacion,
) -> str:
    """Genera el reporte integral consolidado de la Tarea 6."""
    encabezado = [
        SEPARADOR_GRUESO,
        "UNIVERSIDAD JOSE ANTONIO PAEZ - FACULTAD DE INGENIERIA",
        "ESCUELA DE INGENIERIA EN COMPUTACION",
        "CATEDRA: METODOS CUANTITATIVOS / INVESTIGACION DE OPERACIONES II",
        "INFORME TECNICO Y HOJA DE RESULTADOS - TAREA 6: PROGRAMACION NO LINEAL",
        "Autores: Roberto Siracusa (C.I. 30.195.953) e Ignacio Acena (C.I. 31.352.123)",
        SEPARADOR_GRUESO,
        "",
        "RESUMEN EJECUTIVO DE MODELOS Y CONCLUSIONES:",
        "  1. Sin restricciones   : x* = 2.0000, y* = 3.0000 ==> Costo Minimo = 7.0000",
        "  2. Lagrange Rectangulo : x* = 10.0000, y* = 10.0000 ==> Area Maxima = 100.0000 (lambda = 5.0000)",
        "  3. Gradiente Iterativo : x* = 2.0000, y* = 3.0000 ==> f Maxima = 13.0000 (Convergente)",
        "  4. KKT Desigualdades   : x* = 21.6667, y* = 18.3333 ==> Ganancia Maxima = 140.8333 (mu1 = 0.6667)",
        "  5. Cilindro Fisico     : r* = 4.3013 cm, h* = 8.6025 cm ==> Area Minima = 348.7342 cm^2 (h = 2r)",
        "",
    ]

    partes = [
        "\n".join(encabezado),
        formatear_problema_1(res1),
        formatear_problema_2(res2),
        formatear_problema_3(res3, historial3),
        formatear_problema_4(res4),
        formatear_problema_5(res5),
        SEPARADOR_GRUESO,
        "FIN DEL INFORME TECNICO - TAREA 6",
        SEPARADOR_GRUESO,
    ]
    return "\n".join(partes)


def guardar_reporte(texto: str, directorio_salida: str, nombre_archivo: str = "reporte_tarea6.txt") -> str:
    """Guarda el contenido del reporte en un archivo de texto en el directorio indicado."""
    os.makedirs(directorio_salida, exist_ok=True)
    ruta_archivo = os.path.join(directorio_salida, nombre_archivo)
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        f.write(texto)
    return ruta_archivo
