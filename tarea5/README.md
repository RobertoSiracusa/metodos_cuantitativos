# Tarea 5 - Modelo de Tamano de la Fuerza de Trabajo

**Autores:** Roberto Siracusa (C.I. 30.195.953) e Ignacio Acena (C.I. 31.352.123)

**Universidad José Antonio Páez - Facultad de Ingeniería**
**Escuela de Ingeniería en Computación - Métodos Cuantitativos / Investigación de Operaciones II**

Programa de consola (CLI) en POO que resuelve el **modelo de tamaño de la fuerza de
trabajo** por **programación dinámica** (recursividad hacia atrás y reconstrucción de
la política óptima hacia adelante).

## Enunciado

Un contratista estima que el tamaño de la fuerza de trabajo necesaria durante las
siguientes 5 semanas es de 5, 7, 8, 4 y 6 trabajadores, respectivamente. La mano de
obra excedente conservada en la fuerza de trabajo cuesta $300 por trabajador por
semana, y una nueva contratación en cualquier semana incurre en un costo fijo de $400
más $200 por trabajador. El despido no tiene costo ($0).

Enunciado completo (pauta oficial): [`Tarea 5 - Modelo de tamano de la fuerza de
trabajo.md`](Tarea%205%20-%20Modelo%20de%20tamano%20de%20la%20fuerza%20de%20trabajo.md).

### Datos del problema

```
b1 = 5, b2 = 7, b3 = 8, b4 = 4, b5 = 6
x0 = 0 (fuerza inicial)
```

## Formulación matemática

**Costo por exceso:**
```
C1(xi - bi) = 300 * (xi - bi)   si xi > bi
            = 0                 en otro caso
```

**Costo por contratación:**
```
C2(xi - x[i-1]) = 400 + 200 * (xi - x[i-1])   si xi > x[i-1]
                = 0                            en otro caso
```

**Ecuación recursiva de Bellman:**
```
f_i(x_{i-1}) = min { C1(xi - bi) + C2(xi - x[i-1]) + f_{i+1}(xi) }
f_{n+1}(xn) = 0
```

## Espacio de estados y alternativas (calculado, no fijo)

El espacio de alternativas y de estados de entrada de cada semana se **calcula** a
partir de las demandas en `configurar_espacios_estados()` (`src/core/fuerza_trabajo.py`),
en vez de usar un conjunto fijo copiado de la guía:

- **Alternativas de la semana i:** `xi` en el rango `[bi, max(bi, ..., bn)]`. Nunca
  conviene tener menos personal que lo que exige la semana, ni más que la mayor demanda
  que queda por cubrir de ahí en adelante (eso sólo agrega costo de excedente sin evitar
  ningún costo futuro).
- **Estados de entrada `x_{i-1}`:** en la semana 1 es `[fuerza_inicial]` (`x0`); de la
  semana 2 en adelante son las alternativas de la semana anterior.

Con las demandas de la tarea (5, 7, 8, 4, 6) este cálculo reproduce exactamente los
conjuntos de la guía de clase: `x1` en `{5,6,7,8}`, `x2` en `{7,8}`, `x3` en `{8}`,
`x4` en `{4,5,6}`, `x5` en `{6}`.

## Arquitectura orientada a objetos (POO)

| Clase | Responsabilidad |
| :--- | :--- |
| `PoliticaCostos` | Encapsula las tarifas de exceso, contratación y despido, y evalúa `C1` y `C2`. Valida que los costos sean numéricos (no bool) y `>= 0`. |
| `EvaluacionAlternativa` | Registra el desglose de costos para un par `(x_{i-1}, x_i)`. |
| `EstadoEtapa` | Agrupa las alternativas evaluadas para un estado `x_{i-1}` y selecciona la óptima `x_i*` con su costo mínimo `f_i(x_{i-1})`. |
| `EtapaFuerzaTrabajo` | Representa la semana `i`, calcula los estados de entrada y las alternativas, y ejecuta la recurrencia. |
| `ResumenSemanal` | Decisión final tomada en cada semana durante la reconstrucción hacia adelante. |
| `ModeloFuerzaTrabajoDP` | Orquesta las etapas, la recursión hacia atrás y la reconstrucción. Valida demandas y fuerza inicial. No imprime ni escribe nada. |

El formateo de tablas y del reporte vive aparte, en `src/services/reporter.py`
(`formatear_etapa`, `formatear_resumen`, `generar_reporte`, `guardar_reporte`): el
modelo sólo calcula.

## Estructura

```text
tarea5/
├── main.py                                                      # CLI
├── Tarea 5 - Modelo de tamano de la fuerza de trabajo.md        # enunciado (pauta oficial)
├── requirements.txt
├── datos/fuerza_trabajo.json       # demandas, fuerza inicial y costos
├── src/
│   ├── core/fuerza_trabajo.py      # PoliticaCostos, EtapaFuerzaTrabajo, ModeloFuerzaTrabajoDP, ...
│   └── services/reporter.py        # tablas, resumen y reporte en texto
├── tests/test_fuerza_trabajo.py    # pytest
└── outputs/salidas_fuerza_trabajo.txt   # salida generada (archivo para subir a Acrópolis)
```

## Instalación y ejecución

```bash
cd tarea5
python3 -m pip install -r requirements.txt

python3 main.py                                  # problema de la tarea (demandas 5,7,8,4,6)
python3 main.py --demandas "5,7,8,4,6"           # otras demandas
python3 main.py --inicial 2                      # otra fuerza inicial x0
python3 main.py --excedente 300 --fijo 400 --variable 200 --despido 0
python3 main.py --datos otros.json
python3 main.py --sin-exportar                   # no guardar el reporte en outputs/

python3 -m pytest tests/ -q                      # pruebas
```

Cada flag sobrescribe el valor correspondiente del JSON. Un error de datos (JSON
inválido, clave faltante, demanda no numérica, etc.) imprime `Error: ...` en stderr y
termina con código 1, sin traceback.

## Salida por terminal

Salida de `python3 main.py` con los datos de la tarea (encabezado, etapa 5 a etapa 2
resumidas con `...`, etapa 1 completa y resumen final completos):

```text
$ python3 main.py
================================================================================
UNIVERSIDAD JOSE ANTONIO PAEZ
FACULTAD DE INGENIERIA - ESCUELA DE INGENIERIA EN COMPUTACION
METODOS CUANTITATIVOS / INVESTIGACION DE OPERACIONES II

TAREA 5 - MODELO DE TAMANO DE LA FUERZA DE TRABAJO
================================================================================

1. DATOS DEL PROBLEMA:
   - Duracion del proyecto: 5 semanas.
   - Requerimientos minimos de personal: [5, 7, 8, 4, 6]
   - Fuerza laboral inicial: 0 trabajadores.
   - Estructura de costos:
     * Costo por mano de obra excedente: $300 por trabajador/semana.
     * Costo de contratacion: $400 (fijo) + $200 por trabajador.
     * Costo por despido: $0.

2. ECUACION RECURSIVA DE BELLMAN (Recursividad hacia atras):
   f_i(x_{i-1}) = min { C_1(x_i - b_i) + C_2(x_i - x_{i-1}) + f_{i+1}(x_i) }
   con condicion de frontera: f_{n+1}(x_n) = 0

================================================================================
              RESOLUCION PASO POR PASO (DE ETAPA 5 A ETAPA 1)
================================================================================

================================================================================
  ETAPA 5 (SEMANA 5) | Requerimiento minimo: b_5 = 6
  Alternativas evaluadas: x_5 in [6]
  Ecuacion: f_5(x_4) = min { C_1(x_5 - 6) + C_2(x_5 - x_4) + f_6(x_5) }
--------------------------------------------------------------------------------
  x_4    |          x_5=6           |    f_5(x)    |   x_5*
-------------------------------------------------------------
   4     |      0+ 800+   0= 800    |     $800     |    6
   5     |      0+ 600+   0= 600    |     $600     |    6
   6     |      0+   0+   0=   0    |      $0      |    6
--------------------------------------------------------------------------------
  Leyenda celda: [C_excedente + C_contratacion + f_futuro = Costo_Total]

...  (ETAPA 4, ETAPA 3 y ETAPA 2 con el mismo formato: ver
      outputs/salidas_fuerza_trabajo.txt para el detalle completo)

================================================================================
  ETAPA 1 (SEMANA 1) | Requerimiento minimo: b_1 = 5
  Alternativas evaluadas: x_1 in [5, 6, 7, 8]
  Ecuacion: f_1(x_0) = min { C_1(x_1 - 5) + C_2(x_1 - x_0) + f_2(x_1) }
--------------------------------------------------------------------------------
  x_0    |          x_1=5           |          x_1=6           |          x_1=7           |          x_1=8           |    f_1(x)    |   x_1*
----------------------------------------------------------------------------------------------------------------------------------------------
   0     |      0+1400+1900=3300    |    300+1600+1700=3600    |    600+1800+1200=3600    |    900+2000+ 900=3800    |    $3300     |    5
--------------------------------------------------------------------------------
  Leyenda celda: [C_excedente + C_contratacion + f_futuro = Costo_Total]

================================================================================
                    RESUMEN DE LA POLITICA OPTIMA FINAL
================================================================================
 Semana  |  Min Req  |  Personal Real  |            Decision tomada             | Costo Sem ($) | Costo Acum ($)
----------------------------------------------------------------------------------------------------------------
   1     |     5     |        5        | Contratar 5 trabajadores               |         $1400 |          $1400
   2     |     7     |        8        | Contratar 3 trabajadores (1 excedente) |         $1300 |          $2700
   3     |     8     |        8        | Ningun cambio                          |            $0 |          $2700
   4     |     4     |        6        | Despedir 2 trabajadores (2 excedentes) |          $600 |          $3300
   5     |     6     |        6        | Ningun cambio                          |            $0 |          $3300
================================================================================================================
  >>> COSTO TOTAL MINIMO DE MANO DE OBRA PARA EL PROYECTO: $3300 USD <<<
================================================================================

Autores: Roberto Siracusa (C.I. 30.195.953), Ignacio Acena (C.I. 31.352.123)

Reporte guardado en: outputs/salidas_fuerza_trabajo.txt
```

## Resultado

| Semana | Mínimo requerido (bi) | Personal óptimo (xi) | Decisión | Costo semanal | Costo acumulado |
| :---: | :---: | :---: | :--- | :---: | :---: |
| 1 | 5 | 5 | Contratar 5 trabajadores | $1400 | $1400 |
| 2 | 7 | 8 | Contratar 3 trabajadores (1 excedente) | $1300 | $2700 |
| 3 | 8 | 8 | Ningún cambio | $0 | $2700 |
| 4 | 4 | 6 | Despedir 2 trabajadores (2 excedentes) | $600 | $3300 |
| 5 | 6 | 6 | Ningún cambio | $0 | $3300 |

**Costo total mínimo de mano de obra: $3300.**

`outputs/salidas_fuerza_trabajo.txt` (en ASCII, sin tildes) es el archivo que se sube
como .txt a Acrópolis.
