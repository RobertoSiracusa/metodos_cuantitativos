# Tarea 6 — Programación No Lineal
### Modelos de Optimización Clásica, Multiplicadores de Lagrange, Gradiente, KKT y Modelado Físico

**Autores:** Roberto Siracusa (C.I. 30.195.953) e Ignacio Aceña (C.I. 31.352.123)  
**Universidad José Antonio Páez — Facultad de Ingeniería**  
**Escuela de Ingeniería en Computación — Métodos Cuantitativos / Investigación de Operaciones II**  

---

## Descripción General

Este proyecto implementa una solución integral en Python para el análisis, cálculo, simulación y resolución analítica y numérica de **Problemas de Programación No Lineal (PNL)**. Diseñado bajo principios de ingeniería de software con arquitectura modular descendente (**Top-Down Design**), Orientación a Objetos (POO), desacoplamiento estructural, tipado estricto, pruebas unitarias automatizadas (`pytest`) y generación de reportes técnicos detallados.

El sistema resuelve los 5 problemas planteados en la pauta oficial del curso:
1. **Problema sin restricciones:** Minimizacion de costos mediante derivadas parciales y analisis de convexidad con la matriz Hessiana.
2. **Método de Lagrange:** Maximizacion de area rectangular bajo restriccion de perimetro fijo y analisis con Hessiano Orlado.
3. **Método del Gradiente:** Maximizacion cuadratica por busqueda iterativa (ascenso de gradiente) y analisis del paso optimo.
4. **Problema con múltiples restricciones:** Maximizacion de ganancias bajo desigualdades de capacidad y no negatividad mediante condiciones **Karush-Kuhn-Tucker (KKT)**.
5. **Problema de volumen mínimo:** Dimensionamiento fisico optimo de un cilindro para minimizar su area superficial con volumen constante.

---

## Enunciados y Formulación Matemática

El enunciado oficial se encuentra transcrito en [`Tarea 6 - Programacion No Lineal.md`](Tarea%206%20-%20Programacion%20No%20Lineal.md). La deduccion analitica detallada paso a paso, demostraciones de segundo orden y conclusiones academicas estan desarrolladas en [`Hoja_de_Examen_Tarea6.md`](Hoja_de_Examen_Tarea6.md).

### Resumen de Modelos

| N° | Problema | Función Objetivo | Restricciones | Solución Óptima | Multiplicador / Sensibilidad |
|:--:|:---|:---|:---|:---|:---|
| **1** | Costo sin restricciones | $\min C(x,y) = x^2 + y^2 - 4x - 6y + 20$ | Ninguna | $x^* = 2$, $y^* = 3$<br>$C^* = 7$ | Hessiano: $D_1=2>0, \det=4>0$ (Mínimo global) |
| **2** | Lagrange Rectángulo | $\max A(x,y) = xy$ | $2x + 2y = 40$ | $x^* = 10$, $y^* = 10$<br>$A^* = 100$ | $\lambda^* = 5$ ($dA^*/dP = 5$, Cuadrado) |
| **3** | Gradiente Iterativo | $\max f(x,y) = -(x^2 + y^2) + 4x + 6y$ | Ninguna, inicio en $(0,0)$ | $x^* = 2$, $y^* = 3$<br>$f^* = 13$ | $\alpha^* = 0.5$ (1 iteración analítica) |
| **4** | KKT Múltiples Restricciones | $\max G(x,y) = 5x + 8y - 0.1x^2 - 0.2y^2$ | $x + y \le 40$<br>$x, y \ge 0$ | $x^* = 65/3 \approx 21.67$<br>$y^* = 55/3 \approx 18.33$<br>$G^* = 845/6 \approx 140.83$ | $\mu_1^* = 2/3 \approx 0.67$<br>($\mu_2 = \mu_3 = 0$) |
| **5** | Cilindro Físico | $\min A(r,h) = 2\pi r^2 + 2\pi rh$ | $\pi r^2 h = 500\text{ cm}^3$ | $r^* = \sqrt[3]{250/\pi} \approx 4.3013\text{ cm}$<br>$h^* = 2r^* \approx 8.6025\text{ cm}$<br>$A^* \approx 348.7342\text{ cm}^2$ | $\lambda^* \approx 0.4650\text{ cm}^{-1}$ ($h = 2r = \text{diámetro}$) |

---

## Arquitectura Orientada a Objetos (POO)

El código fuente se encuentra desacoplado en capas de dominio (`src/core/`) y de servicios (`src/services/`):

| Clase / Módulo | Archivo | Responsabilidad |
| :--- | :--- | :--- |
| `ResultadoOptimizacion` | `src/core/base.py` | Dataclass inmutable que almacena las variables optimas, valor objetivo, tipo de optimo, multiplicadores, estado de convergencia y conclusion. |
| `OptimizadorSinRestricciones` | `src/core/problema1_sin_restricciones.py` | Modela la funcion de costo multivariable, evalua gradiente, matriz Hessiana y clasifica el punto critico. |
| `OptimizadorLagrangeRectangulo` | `src/core/problema2_lagrange.py` | Plantea el Lagrangiano para el rectangulo con perimetro fijo, evalua el Hessiano Orlado y calcula el precio sombra $\lambda$. |
| `OptimizadorGradienteAscenso` | `src/core/problema3_gradiente.py` | Implementa el algoritmo de ascenso de gradiente paso a paso, registra la trayectoria iterativa y compara con el paso optimo exacto. |
| `OptimizadorKKTMultiplesRestricciones` | `src/core/problema4_kkt.py` | Evalua factibilidad del punto no restringido, formula el sistema Karush-Kuhn-Tucker, identifica fronteras activas y calcula multiplicadores duales $\mu_i$. |
| `OptimizadorCilindroFisico` | `src/core/problema5_cilindro.py` | Optimiza el dimensionamiento de un cilindro cerrado o abierto, demuestra la relacion $h = 2r$ y calcula la sensibilidad superficial. |
| `Reporter` | `src/services/reporter.py` | Formatea tablas ASCII, trazas de iteracion y reportes tecnicos completos listos para impresion o entrega. |

---

## Estructura del Directorio

```text
tarea6/
├── Tarea 6 - Programacion No Lineal.md       # Transcripción del enunciado oficial (PDF)
├── Hoja_de_Examen_Tarea6.md                  # Hoja de examen con modelos matemáticos y conclusiones formales
├── prompt_nanobanana.md                      # Prompts optimizados para generar la hoja escaneada a mano
├── README.md                                 # Documentación técnica del proyecto
├── main.py                                   # CLI ejecutable principal
├── requirements.txt                          # Dependencias del proyecto (numpy, scipy, pytest)
├── datos/
│   └── problemas.json                        # Parámetros por defecto de los 5 problemas
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── base.py                           # Clases base, dataclasses y validadores
│   │   ├── problema1_sin_restricciones.py    # Modelo y resolución del Problema 1
│   │   ├── problema2_lagrange.py             # Modelo y resolución del Problema 2
│   │   ├── problema3_gradiente.py            # Modelo y resolución del Problema 3
│   │   ├── problema4_kkt.py                  # Modelo y resolución del Problema 4
│   │   └── problema5_cilindro.py             # Modelo y resolución del Problema 5
│   └── services/
│       ├── __init__.py
│       └── reporter.py                       # Servicio de formateo y exportación a texto
├── tests/
│   ├── __init__.py
│   ├── conftest.py                           # Configuración de rutas para pytest
│   ├── test_problema1.py                     # Pruebas analíticas y validación de P1
│   ├── test_problema2.py                     # Pruebas de Lagrange y Hessiano Orlado de P2
│   ├── test_problema3.py                     # Pruebas de convergencia del Gradiente de P3
│   ├── test_problema4.py                     # Pruebas de condiciones KKT y comparación SciPy de P4
│   ├── test_problema5.py                     # Pruebas geométricas y físicas de P5
│   └── test_cli_y_reporter.py                # Pruebas del CLI y exportación
└── outputs/
    └── reporte_tarea6.txt                    # Reporte generado por el programa (entrega Acrópolis)
```

---

## Instalación y Ejecución

### 1. Requisitos Previos e Instalación de Dependencias

```bash
cd tarea6
python3 -m pip install -r requirements.txt
```

### 2. Ejecutar Todos los Problemas

Para resolver los 5 problemas en consola y generar el reporte completo en `outputs/reporte_tarea6.txt`:

```bash
python3 main.py
```

### 3. Ejecutar un Problema Específico

```bash
# Problema 1: Sin restricciones
python3 main.py --problema 1

# Problema 2: Lagrange (rectangulo con perimetro 40)
python3 main.py --problema 2 --perimetro 40

# Problema 3: Metodo del Gradiente
python3 main.py --problema 3 --alfa 0.1 --iteraciones 50

# Problema 4: Condiciones KKT
python3 main.py --problema 4 --capacidad 40

# Problema 5: Cilindro de volumen minimo
python3 main.py --problema 5 --volumen 500
```

### 4. Opciones Adicionales

- `--sin-exportar`: Ejecuta los cálculos en pantalla sin sobrescribir archivos en `outputs/`.
- `--datos <ruta>`: Permite especificar un archivo JSON de configuración alternativo.

---

## Ejecución de Pruebas Automatizadas

El proyecto incluye 25 pruebas unitarias exhaustivas con `pytest` que verifican soluciones analíticas exactas, matrices hessianas, convergencia numérica, validación de entradas erróneas y consistencia con algoritmos industriales (`scipy.optimize.minimize` SLSQP):

```bash
pytest -v
```

Resultado de ejecución:
```text
tests/test_cli_y_reporter.py::test_main_ejecucion_completa_sin_exportar PASSED
tests/test_cli_y_reporter.py::test_main_ejecucion_individual[1] PASSED
tests/test_cli_y_reporter.py::test_main_ejecucion_individual[2] PASSED
tests/test_cli_y_reporter.py::test_main_ejecucion_individual[3] PASSED
tests/test_cli_y_reporter.py::test_main_ejecucion_individual[4] PASSED
tests/test_cli_y_reporter.py::test_main_ejecucion_individual[5] PASSED
tests/test_cli_y_reporter.py::test_main_con_parametros_personalizados PASSED
tests/test_cli_y_reporter.py::test_guardar_reporte_crea_archivo PASSED
tests/test_problema1.py::test_problema1_solucion_oficial PASSED
tests/test_problema1.py::test_problema1_gradiente_y_hessiano PASSED
tests/test_problema1.py::test_problema1_validaciones PASSED
tests/test_problema2.py::test_problema2_solucion_oficial PASSED
tests/test_problema2.py::test_problema2_hessiano_orlado PASSED
tests/test_problema2.py::test_problema2_sensibilidad_precio_sombra PASSED
tests/test_problema2.py::test_problema2_validaciones PASSED
tests/test_problema3.py::test_problema3_gradiente_y_optimo_analitico PASSED
tests/test_problema3.py::test_problema3_paso_optimo_un_paso PASSED
tests/test_problema3.py::test_problema3_convergencia_iterativa_alfa_01 PASSED
tests/test_problema3.py::test_problema3_validaciones PASSED
tests/test_problema4.py::test_problema4_optimo_no_restringido_y_kkt PASSED
tests/test_problema4.py::test_problema4_comparacion_scipy_slsqp PASSED
tests/test_problema4.py::test_problema4_validaciones PASSED
tests/test_problema5.py::test_problema5_cilindro_cerrado PASSED
tests/test_problema5.py::test_problema5_cilindro_abierto PASSED
tests/test_problema5.py::test_problema5_validaciones PASSED

============================== 25 passed in 0.84s ==============================
```
