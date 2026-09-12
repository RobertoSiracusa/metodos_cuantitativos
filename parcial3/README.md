# Parcial III - Simulacion

Universidad Jose Antonio Paez - Facultad de Ingenieria
Escuela de Ingenieria en Computacion - Metodos Cuantitativos

Programa en Python orientado a objetos que simula dos problemas durante un
periodo en horas indicado por el usuario, genera trazas analizables y archivos de
texto, y envia las metricas a una API de IA que devuelve una conclusion y una
recomendacion mostradas por pantalla.

---

## Instalacion y ejecucion

```bash
python3 -m pip install -r requirements.txt

# Menu interactivo
python3 main.py

# Sin interaccion
python3 main.py --problema 1 --horas 8 --headless
python3 main.py --problema 2 --horas 8 --headless
python3 main.py --problema ambos --horas 8 --headless

# Pruebas
python3 -m pytest tests/ -q
```

### Argumentos de linea de comandos

| Argumento | Descripcion |
|---|---|
| `--problema {1,2,ambos}` | Problema a ejecutar sin pasar por el menu. |
| `--horas FLOAT` | Periodo de simulacion en horas (por defecto 8). |
| `--headless` | Corre sin menu ni interaccion. Requiere `--problema`. |
| `--gui` | Lanza la animacion Pygame (bonus). |
| `--semilla INT` | Semilla de reproducibilidad (por defecto 2026). |
| `--sin-red` | Omite la API de IA y usa el motor experto local. |

### Menu

```
  [1] Problema 1: Fabrica de laptops (eventos discretos)
  [2] Problema 2: Cluster de servidores (simulacion continua)
  [3] Ejecutar ambos problemas
  [4] Animacion Pygame (bonus)
  [0] Salir
```

La duracion en horas se pide **antes** de cada corrida. Enter vacio toma el valor
por defecto de 8 h. Una entrada invalida muestra el motivo y vuelve a preguntar:
el usuario nunca ve un traceback.

---

## Archivos generados

Todos en `outputs/`.

| Archivo | Contenido |
|---|---|
| `traza_problema1.log` | Una linea por evento discreto, con tiempo simulado, tipo e identificador. |
| `traza_problema2.csv` | Serie temporal muestreada cada 60 s: `t_horas,trafico_gbps,temp_c,eficiencia,throughput_gbps,tb_acumulados`. |
| `reporte_problema1.txt` | Parametros, formulas M/M/1 desarrolladas, metricas y lectura del resultado. La respuesta de la IA se anexa al final. |
| `reporte_problema2.txt` | Idem para el cluster. La respuesta de la IA se anexa al final. |
| `conclusiones_manuscritas.txt` | Analisis propio para transcribir a mano. Tope duro de 200 palabras. |
| `metricas_problema*.json` | Cache interna de metricas. No es un entregable. |

Orden de ejecucion al cerrar cada problema, tal como lo pide el enunciado:
escribir la traza, escribir el reporte `.txt`, consultar la API de IA, mostrar la
conclusion por pantalla y anexar la respuesta al final del `.txt`.

---

## Problema 1: fabrica de laptops (eventos discretos)

Una unica estacion de ensamblaje, llegadas de Poisson e inventario de
procesadores con politica de revision continua `(s, Q)`. Con un solo servidor el
sistema es una cola **M/M/1**. Motor: SimPy.

### Parametros

| Parametro | Valor | Origen |
|---|---|---|
| `LAMBDA_ORDENES_HORA` | 10.0 ordenes/h | Enunciado |
| `MEDIA_ENSAMBLAJE_MIN` | 5.0 min | Enunciado (mu = 12 laptops/h) |
| `SERVIDORES` | 1 | Enunciado |
| `UMBRAL_CRITICO_S` | 10 unidades | Enunciado |
| `LEAD_TIME_MIN` | 15.0 min | Enunciado |
| `LOTE_Q` | 50 unidades | Enunciado |
| `STOCK_INICIAL` | 50 unidades | **SUPUESTO PROPIO** |
| `CONSUMO_POR_LAPTOP` | 1 procesador | **SUPUESTO PROPIO** |
| `HORAS_DEFECTO` | 8.0 h | Enunciado |

**Los dos supuestos propios** estan declarados tambien en el reporte generado.
El enunciado no fija el stock inicial de procesadores ni cuantos consume cada
laptop; se adoptaron un lote completo (50) y 1 procesador por laptop.

### Valores teoricos M/M/1 (lambda = 10, mu = 12)

| Indicador | Formula | Valor |
|---|---|---|
| rho | `lambda / mu` | 0.833333 |
| P0 | `1 - rho` | 0.166667 |
| L | `rho / (1 - rho)` | 5.0 |
| Lq | `rho^2 / (1 - rho)` | 4.166667 |
| W | `1 / (mu - lambda)` | 0.5 h = 30 min |
| Wq | `lambda / (mu * (mu - lambda))` | 0.416667 h = 25 min |

### Metricas reportadas

- Tiempo de espera promedio de las ordenes (Wq simulado, en minutos).
- **Tiempo total que toma despachar un lote.** El enunciado admite dos lecturas y
  se reportan las dos, etiquetadas sin ambiguedad:
  - **(a) Ciclo de reposicion de componentes**: desde que se dispara el pedido
    hasta que ingresan las 50 unidades.
  - **(b) Tiempo de despacho de un lote de produccion**: tiempo en completar
    50 laptops terminadas.
- Numero de veces que la linea se detuvo por falta de stock.
- Cantidad de ordenes retrasadas por falta de inventario.
- **Eficiencia en el reabastecimiento**, definida como la fraccion del tiempo
  simulado en que la linea **no** estuvo detenida por falta de procesadores:
  `eficiencia = 1 - (tiempo_linea_detenida / tiempo_total)`.

### Por que las paradas por falta de stock dan CERO

No es un defecto del modelo ni un error de la corrida: es el resultado correcto
con los parametros del enunciado.

El consumo esperado durante el lead time es

```
consumo = lambda * consumo_por_laptop * lead_time
consumo = 10 ordenes/h * 1 procesador * 0.25 h = 2.5 unidades
```

Ese valor esta muy por debajo del umbral critico `s = 10`, asi que el lote de 50
unidades llega mucho antes de que el stock se agote. El inventario esta
**sobredimensionado** respecto del consumo real.

El cuello de botella del sistema es la **estacion de ensamblaje**, que opera con
`rho = 0.833`, no el inventario. Los parametros no se ajustaron para forzar
paradas artificiales. El codigo implementa igualmente la parada de linea, la
reanudacion y sus contadores, y `tests/test_inventory.py` los ejercita con
parametros artificiales que si agotan el stock.

---

## Problema 2: cluster de servidores (simulacion continua)

Balance termico de primer orden acoplado a un modelo de rendimiento con thermal
throttling, integrado con **Runge-Kutta de cuarto orden** y paso de 1 segundo.

### Modelo

```
C * dT/dt = P_idle + k * trafico - h * (T - T_amb)
```

| Constante | Valor | Significado |
|---|---|---|
| `T_AMB_C` | 25.0 C | Temperatura ambiente del datacenter |
| `H_DISIP` | 20.0 W/C | Coeficiente de disipacion (refrigeracion liquida) |
| `P_IDLE_W` | 360.0 W | Potencia en reposo |
| `K_CARGA_W` | 180.0 W/Gbps | Potencia adicional por Gbps |
| `C_TERMICA` | 2400.0 J/C | Capacidad termica (tau = C/h = 120 s) |

Temperatura de equilibrio con trafico constante:

```
T_eq = T_amb + (P_idle + k * trafico) / h
```

| Trafico | T_eq |
|---|---|
| 1 Gbps | 52.0 C |
| 3 Gbps | **70.0 C** (temperatura de diseno) |
| 5 Gbps | 88.0 C |

La calibracion deja el equilibrio con trafico medio en 70 C **exactos**. Ese es
el hallazgo central del problema: el punto de operacion nominal esta justo en el
limite termico, sin margen.

### Eficiencia con thermal throttling

```
eta(T) = 0.90                                si T <= 70
eta(T) = max(0.30, 0.90 - 0.02 * (T - 70))   si T > 70

throughput = trafico * eta(T)
```

Datos acumulados: se integra el throughput en el tiempo; `Gb / 8 -> GB`,
`GB / 1000 -> TB`.

### Decisiones de modelado

- **Trafico Normal(3, 1) truncado a [1, 5] Gbps por rechazo**, no por recorte.
  Truncar descartando la muestra fuera de rango preserva la forma de la campana;
  recortar al limite acumularia masa de probabilidad en 1 y en 5, creando dos
  picos artificiales que el modelo no tiene.
- **El trafico se re-sortea cada 60 s con retencion de orden cero**, y se
  mantiene constante dentro de cada minuto. Un sorteo por segundo convertiria la
  demanda en ruido blanco: el filtro pasabajos que impone la inercia termica
  (tau = 120 s) lo promediaria todo y la temperatura quedaria clavada en el
  equilibrio medio, borrando la variabilidad que el enunciado pide medir.
- **La traza CSV se muestrea una vez por minuto**, no una vez por paso: 8 h dan
  480 filas analizables en lugar de 28.800 inservibles.
- **La corrida arranca en 70 C** (equilibrio nominal) y no en la temperatura
  ambiente, para que las metricas de variabilidad midan la respuesta al trafico y
  no el transitorio de encendido, que es un artefacto de arranque.

### Metricas reportadas

- Cantidad total de datos procesados (TB).
- Variabilidad de la temperatura: media, desviacion estandar, minimo y maximo.
- Eficiencia global de la red (eta ponderada en el tiempo) y throughput medio
  contra trafico medio.
- Porcentaje del tiempo con throttling activo (T > 70 C).

---

## API de IA

`src/services/ai_auditor.py` consulta en cascada, con un prompt distinto por
problema:

1. **Google Gemini** (`GEMINI_API_KEY`) - modelos `gemini-flash-latest`,
   `gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-pro-latest`.
2. **OpenAI** (`OPENAI_API_KEY`) - `gpt-4o-mini`.
3. **Ollama local** en el puerto 11434.
4. **Backend REST propio** (`LOCAL_API_URL`).
5. **Motor experto cuantitativo local**, determinista y sin red.

El paso 5 garantiza que el programa **siempre** muestre una conclusion y una
recomendacion por pantalla, aunque no haya conectividad ni credenciales. Es
respaldo, no sustituto: el camino normal es la API real.

Las credenciales se cargan en cascada desde variables de entorno, `parcial3/.env`
y `metodos_cuantitativos/.env`. Ver `.env.example`.

---

## Estructura

```
parcial3/
├── main.py                       Menu, prompts validados y CLI
├── requirements.txt
├── .env.example
├── src/
│   ├── core/
│   │   ├── mm1_analytical.py     M/M/1 teorico (rho, P0, L, Lq, W, Wq, Pn)
│   │   ├── factory_entities.py   Orden, EstacionEnsamblaje, InventarioProcesadores, EstadisticasFabrica
│   │   ├── traffic_model.py      Normal(3,1) truncada a [1,5] por rechazo
│   │   └── thermal_model.py      EDO del balance termico, RK4, eta(T) con throttling
│   ├── simulation/
│   │   ├── discrete_sim.py       Motor SimPy de la fabrica
│   │   └── continuous_sim.py     Integrador del cluster
│   ├── services/
│   │   ├── tracer.py             Trazas .log de eventos y .csv de series
│   │   ├── reporter.py           Reportes .txt
│   │   ├── ai_auditor.py         Cascada Gemini -> OpenAI -> Ollama -> motor local
│   │   └── conclusiones.py       El .txt manuscrito, maximo 200 palabras
│   └── utils/
│       ├── config.py             Defaults del enunciado y carga de .env en cascada
│       └── validators.py
├── tests/
└── outputs/                      Se crea en tiempo de ejecucion
```

Cada modulo con logica no trivial trae un **selfcheck** ejecutable sin pytest:

```bash
python3 -m src.core.thermal_model
python3 -m src.simulation.discrete_sim
python3 -m src.services.conclusiones
```

---

## Contrato para la capa grafica

Los dos motores exponen la misma interfaz, con el tiempo simulado **en segundos**
en ambos casos:

- `step(target_time: float) -> None` - avanza el motor hasta ese tiempo simulado.
- `tiempo_actual: float` - tiempo simulado actual, en segundos.
- `obtener_metricas() -> Dict` - metricas consolidadas en cualquier momento, no
  solo al final.

`FabricaSimulation` expone ademas, legibles en cualquier frame:
`ordenes_en_cola: List[Orden]`, `estacion` (con `.ocupada` y `.orden_actual`),
`inventario` (con `.nivel`, `.capacidad_lote`, `.en_reposicion`) y
`linea_detenida: bool`.

`ClusterSimulation` expone ademas: `temperatura_actual`, `trafico_actual`,
`eficiencia_actual`, `throughput_actual`, `tb_acumulados` e `historial_temp`
(ventana acotada a los ultimos 300 puntos, para el oscilograma).

La opcion `[4]` del menu esta preparada: `lanzar_gui()` en `main.py` importa
`src.gui.app.ejecutar_animacion(horas, semilla)` dentro de un `try/except
ImportError`. Mientras ese modulo no exista, imprime
`Modulo grafico no disponible en esta version` y vuelve al menu.

---

## Pruebas

```bash
python3 -m pytest tests/ -q
```

| Archivo | Cubre |
|---|---|
| `test_mm1_analytical.py` | rho, P0, L, Lq, W, Wq contra los valores cerrados; Ley de Little. |
| `test_inventory.py` | Disparo bajo umbral, ingreso del lote tras el lead time, contador de paradas con parametros artificiales que si agotan el stock. |
| `test_discrete_sim.py` | Reproducibilidad con semilla fija, Ley de Little con tolerancia amplia, ninguna metrica negativa, contrato de la GUI. |
| `test_thermal_model.py` | Equilibrios 1 -> 52, 3 -> 70, 5 -> 88; eta monotona decreciente y acotada a [0.30, 0.90]. |
| `test_rk4.py` | El integrador contra `T(t) = T_eq + (T0 - T_eq) * exp(-t/tau)`. |
| `test_traffic_model.py` | Truncamiento estricto en [1,5] sobre 50.000 muestras; media muestral ~3. |
| `test_services.py` | Escritura de reportes, `anexar_seccion`, lineas del tracer, auditor de IA con mocks. |
| `test_validators.py` | Horas negativas, cero, vacio, texto, None, NaN e infinito se rechazan sin traceback. |
| `test_conclusiones.py` | **El texto generado tiene 200 palabras o menos.** |

Ningun test sale a la red: los clientes HTTP se ejercitan con `unittest.mock`.

---

## Cumplimiento del enunciado

| Requisito | Donde |
|---|---|
| 1. Programacion orientada a objetos | Todo `src/`: `ModeloMM1`, `Orden`, `EstacionEnsamblaje`, `InventarioProcesadores`, `EstadisticasFabrica`, `GeneradorTrafico`, `ModeloTermico`, `FabricaSimulation`, `ClusterSimulation`, `ReportService`, `AIAuditorService`, `TrazaEventos`, `TrazaSerie`. |
| 2. Menu de opciones | `main.py::bucle_menu` |
| 3. El periodo en horas lo indica el usuario antes de ejecutar | `main.py::solicitar_horas` y `--horas` |
| 4. Trazas analizables | `outputs/traza_problema1.log`, `outputs/traza_problema2.csv` |
| 5. Consumir API de IA y mostrar conclusion por pantalla | `src/services/ai_auditor.py::ejecutar_auditoria` |
| 6. Generar archivos de texto | `src/services/reporter.py`, `src/services/conclusiones.py` |
| 7. Validaciones de los datos introducidos | `src/utils/validators.py`, con reintento en `main.py` |
| 8. Codigo comentado | Docstrings de modulo, de clase y de metodo en todo `src/` |
| 9. Datos por defecto de prueba | `src/utils/config.py` |

---

## Pregunta Bonus (2 puntos): animacion Pygame

Interfaz grafica interactiva en `src/gui/`, que visualiza en tiempo real el
comportamiento de los dos problemas. Se abre desde la opcion `[4]` del menu o
con `python3 main.py --gui`.

```bash
python3 main.py --gui
```

**Flujo obligatorio:** primero se elige que problema visualizar (pantalla
selectora, teclas `1`/`2` o clic en la tarjeta) y despues se corre **solo esa
vista**. Los dos problemas nunca se dibujan a la vez.

### Estructura

```
src/gui/
├── app.py             ejecutar_animacion() + pantalla selectora + bucle principal
├── styles.py           paleta, fuentes, interpolacion de color por temperatura
├── controller.py        sincronizacion reloj Pygame <-> motor de simulacion
├── input_handler.py     traduccion de eventos de teclado/mouse a comandos
├── hud.py                panel lateral de telemetria, comun a las dos vistas
├── factory_view.py      dibujo del Problema 1 (fabrica de laptops)
└── cluster_view.py       dibujo del Problema 2 (cluster de servidores)
```

Ninguna vista guarda una copia paralela del estado de dominio: leen
`controller.sim` en cada frame. El unico estado propio de una vista es
puramente visual (posicion interpolada de las cajas de la cola, particulas de
trafico, fase de un parpadeo).

### Vista Problema 1: fabrica de laptops

Cola de ordenes entrantes (cajas con su `id_orden`, interpoladas hacia la
estacion), estacion de ensamblaje **verde libre / roja ocupada**, contador de
laptops despachadas, y una barra vertical de inventario de procesadores con
marca en el umbral critico `s=10` (verde por encima, ambar cerca, roja bajo el
umbral, con parpadeo y rotulo `REPONIENDO` mientras hay un pedido en transito).
Si la linea se detiene por falta de stock, una franja roja lo indica.

### Vista Problema 2: cluster de servidores

Nodo del servidor cuyo color interpola de azul a rojo critico segun la
temperatura (ancla en 50 C / 70 C / 90 C, en `styles.color_por_temperatura`),
barra termica vertical con marca en 70 C (umbral de throttling), oscilograma
con el historial de temperatura, y particulas de trafico entrante cuya
densidad es proporcional a `trafico_actual`. Con thermal throttling activo, una
franja lo indica.

### Controles

| Tecla | Accion |
|---|---|
| `ESPACIO` | Pausa/reanuda la **animacion** (ver nota abajo). |
| `P` | Pausa total: congela tambien el motor. |
| `1` `2` `3` `4` | Escala de tiempo: x60, x300, x900, x3600 (segundos simulados por segundo real). |
| `R` | Reinicia la simulacion de la vista actual desde cero. |
| `ESC` | Vuelve al selector de problema. Desde el selector, sale. |

**Distincion pausa-animacion vs pausa-total (letra chica del enunciado):**
"pausar o reanudar la animacion sin detener el calculo logico de la
simulacion" se implementa de forma literal. Con `ESPACIO` activo, `sim.step()`
se sigue llamando en cada frame -el motor **no** se detiene- y el HUD sigue
mostrando datos frescos; lo unico que se congela es la representacion visual
(sprites interpolados). La tecla `P` es el extra que si detiene todo,
incluido el motor. `src/gui/controller.py::SimController.step` es el unico
lugar donde se decide esto: `pausa_total` es la unica condicion que detiene el
avance del motor, `pausa_animacion` nunca se consulta ahi.

### Pruebas

```bash
SDL_VIDEODRIVER=dummy python3 -m pytest tests/test_gui.py -v
```

Corren headless (`SDL_VIDEODRIVER=dummy`), sin abrir ninguna ventana real.
Cubren: import limpio de los siete modulos; la interpolacion de color por
temperatura (anclas, monotonia en rojo, saturacion fuera de rango); que el
controlador avanza el motor de cada problema; que `ESPACIO` pausa la animacion
sin detener el motor y que `P` si lo detiene; que las teclas `1`-`4` fijan la
escala esperada; y que ambas vistas, el HUD, el selector y el panel de cierre
renderizan un frame sobre una `pygame.Surface` sin excepcion.
