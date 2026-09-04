# Métodos Cuantitativos — Repositorio

**Universidad José Antonio Páez — Facultad de Ingeniería**  
**Escuela de Ingeniería en Computación — Métodos Cuantitativos**

Este repositorio agrupa las tareas y proyectos prácticos desarrollados durante el curso de Métodos Cuantitativos. Cada tarea se encuentra aislada en su respectiva carpeta (`tarea1/`, `tarea2/`, `parcial1/`) y contiene la implementación en Python bajo el paradigma de Programación Orientada a Objetos (POO), suites de pruebas unitarias automatizadas (`pytest`) y documentación técnica.

---

## Organización del Repositorio

```text
metodos_cuantitativos/
│
├── tarea1/                             # Tarea 1: Teoría de Líneas de Espera / Colas
│   ├── calculator/
│   │   ├── main.py                     # CLI ejecutable
│   │   ├── src/                        # Modelos M/M/1, M/M/c, M/G/1, M/D/1
│   │   ├── tests/                      # Tests unitarios con pytest
│   │   └── README.md                   # Documentación específica de Tarea 1
│   └── Tarea I ...pdf                  # Pauta oficial de la tarea
│
├── tarea2/                             # Tarea 2: Teoría de Inventarios
│   ├── main.py                         # Punto de entrada principal (GUI Tkinter)
│   ├── src/                            # Arquitectura Top-Down: core, gui, services
│   ├── outputs/                        # Reportes de texto (.txt) oficiales generados
│   ├── tests/                          # Tests unitarios con pytest (19 tests)
│   ├── Guia de Problemas ...pdf        # Guía de problemas del curso
│   ├── Segunda tarea ...pdf            # Pauta oficial de la tarea
│   └── README.md                   # Documentación específica de Tarea 2
├── parcial1/                           # Evaluaciones y respuestas del Parcial I
├── parcial2/                           # Evaluaciones, calculadora y respuestas del Parcial II (Inventarios)
│   ├── main.py                         # Punto de entrada (GUI interactiva / CLI examen)
│   ├── src/                            # Arquitectura modular Top-Down de inventarios (reutilizada de Tarea 2)
│   ├── outputs/                        # Salidas .txt oficiales (3 ejercicios)
│   ├── respuestaPregunta1.md           # Respuesta escrita Ejercicio 1 (EOQ)
│   ├── respuestaPregunta2.md           # Respuesta escrita Ejercicio 2 (Quiebre de precios)
│   └── respuestaPregunta3.md           # Respuesta escrita Ejercicio 3 (Restricciones)
├── claseSimulacion/                    # Simulacion de Eventos Discretos: Juego Snake (SimPy + Pygame en POO)
│   ├── main.py                         # Punto de entrada (Modo manual, Auto IA, Headless)
│   ├── src/                            # Arquitectura POO: models, simulation, view, engine
│   ├── tests/                          # Tests unitarios con pytest (12 tests)
│   └── README.md                       # Documentacion tecnica y de ejecucion
│
├── estacion/                           # Simulacion de Linea de Espera: Estacion de Gasolina M/M/c (SimPy + Pygame)
│   ├── main.py                         # Punto de entrada interactivo y CLI
│   ├── src/                            # Arquitectura POO: models, simulation, view, engine
│   ├── tests/                          # Tests unitarios con pytest (10 tests)
│   └── README.md                       # Documentacion tecnica y fundamentos M/M/c
│
├── automercado/                        # Simulacion de Linea de Espera: Automercado M/M/c y c x M/M/1 (SimPy + Pygame)
│   ├── main.py                         # Punto de entrada interactivo y CLI
│   ├── src/                            # Arquitectura POO: models, simulation, view, engine
│   ├── tests/                          # Tests unitarios con pytest (12 tests)
│   └── README.md                       # Documentacion tecnica, teoria de colas y ejecucion
│
├── transporte/                         # Optimizacion de Redes de Transporte & Flota (Dijkstra + A* + Pygame)
│   ├── main.py                         # Punto de entrada interactivo y CLI
│   ├── src/                            # Arquitectura POO: models, simulation, view, engine
│   ├── tests/                          # Tests unitarios con pytest (12 tests)
│   └── README.md                       # Documentacion tecnica, grafos y ejecucion
│
├── nuclear/                            # Simulacion de Reaccion Nuclear y Dinamica de Reactor (SimPy + Pygame)
│   ├── main.py                         # Punto de entrada interactivo y CLI
│   ├── src/                            # Arquitectura POO: models, simulation, view, engine
│   ├── tests/                          # Tests unitarios con pytest (11 tests)
│   └── README.md                       # Documentacion tecnica, fisica neutronica y manual
│
└── README.md                           # Documentación general del repositorio
```

---

## Contenido de las Tareas

### Tarea 1 — Teoría de Líneas de Espera (Colas)
Implementa una calculadora orientada a objetos para análisis de sistemas de colas con llegadas Poisson:
* **Modelos soportados:** $M/M/1$, $M/M/c$, $M/G/1$, $M/G/c$, $M/D/1$, $M/D/c$.
* **Métricas calculadas:** Factor de utilización ($\rho$), probabilidad de sistema vacío ($P_0$), número esperado en cola/sistema ($L_q$, $L$), tiempos de espera promedio ($W_q$, $W$) y probabilidad de espera Erlang-C ($P_w$).
* **Ubicación:** `tarea1/calculator/`

### Tarea 2 — Teoría de Inventarios (Modelos de Decisión y Optimización)
Implementa una aplicación con arquitectura modular Top-Down Design e interfaz gráfica en Tkinter (tema Slate & Blue) para la optimización de inventarios:
* **Modelos implementados:**
  1. **EOQ Clásico:** Lote económico determinístico, frecuencia $T = Q/D$, número de pedidos $N$ y desglose de costos.
  2. **Modelo Probabilístico:** Demanda variable bajo distribución normal, stock de seguridad ($SS = Z \cdot \sigma_L$), punto de reorden ($ROP$) y costos operacionales relevantes.
  3. **Quiebre de Inventario:** Descuentos por volumen por tramos de precio, ajuste de factibilidad y análisis cuantitativo de trade-off de costos.
  4. **Multi-Artículo con Restricciones:** Optimización simultánea con límites de espacio/área física y presupuesto financiero mediante Multiplicadores de Lagrange (exacto y aproximación clásica de Taha).
* **Exportación de reportes:** Generación de archivos `.txt` en `tarea2/outputs/` con diagnósticos e interpretaciones económicas de decisión.
* **Ubicación:** `tarea2/`

### Clase Simulación — Sistema Discreto: Juego Snake (SimPy + Pygame)
Implementa un modelo de simulación por eventos discretos bajo el paradigma de Programación Orientada a Objetos (POO):
* **Motor SimPy:** Modela procesos estocásticos y saltos discretos temporales para el movimiento de la serpiente, ciclo de vida de alimentos normales/bonus y muestreo de métricas.
* **Motor Pygame:** Visualización en tiempo real desacoplada con soporte para velocidad variable (1x, 2x, 4x), HUD de telemetría y controles interactivos.
* **Modo Auto IA:** Agente autónomo con búsqueda por anchura (BFS) y heurística de supervivencia navegable para análisis y benchmarking sin intervención humana.
* **Ubicación:** `claseSimulacion/`

### Estación de Servicio — Líneas de Espera M/M/c (SimPy + Pygame)
Implementa un modelo estocástico de atención de combustible bajo la teoría de colas $M/M/c$ con vista cenital interactiva:
* **Motor SimPy:** Llegadas Poisson ($\lambda$), tiempos de servicio exponenciales ($\mu$), surtidores paralelos ($c=3$), tanque de almacenamiento y cisterna de reabastecimiento.
* **Motor Pygame Top-Down:** Animación cenital de vehículos, islas de bombas con LEDs de estado, mangueras activas, cola física delimitada y tablero HUD con contraste analítico (teórico vs simulado).
* **Ubicación:** `estacion/`

### Automercado — Líneas de Espera M/M/c vs c x M/M/1 (SimPy + Pygame)
Implementa un modelo estocástico de atención en batería de cajas registradoras con carritos de compra y vista cenital interactiva:
* **Motor SimPy:** Llegadas Poisson ($\lambda$), tiempos de servicio exponenciales ($\mu$), cajas paralelas ($c=1..5$), recorrido de compras por góndolas, escaneo progresivo láser y pago.
* **Disciplinas de Cola Soportadas:** Comparación interactiva en vivo entre **Cola Única Centralizada ($M/M/c$)** y **Colas Paralelas ($c \times M/M/1$)**, demostrando analítica y empíricamente la reducción drástica de tiempos de espera en fila única.
* **Motor Pygame Top-Down:** Animación cenital de clientes con carritos, pasillos con 6 departamentos, cajas con cintas transportadoras, LEDs de estado, molinetes y HUD de telemetría en vivo.
* **Ubicación:** `automercado/`

### Transporte — Optimización de Redes y Asignación de Flota (Dijkstra, A* + Pygame)
Implementa un modelo de investigación de operaciones para la resolución del problema de la ruta más corta (Shortest Path) y despacho de flota de camiones:
* **Algoritmos de Redes:** Cálculo exacto de rutas de mínimo costo mediante **Dijkstra** y búsqueda heurística informada mediante **$A^*$**, con cálculo comparativo de ahorro frente a rutas alternativas.
* **Modelo de Flota:** Asignación óptima de camiones según restricciones de capacidad, minimización de costos de reposición y traslado de carga.
* **Motor Pygame Top-Down:** Animación 2D de carreteras, selección interactiva de nodos (origen y destino) por clic, visualización de rutas óptimas iluminadas (cyan neón) y telemetría HUD en vivo.
* **Ubicación:** `transporte/`

### Reactor Nuclear — Reacción en Cadena y Dinámica de Reactor (SimPy + Pygame)
Implementa un modelo estocástico de cinética neutrónica y termohidráulica de un reactor nuclear con vista cenital interactiva:
* **Motor SimPy:** Transporte de neutrones, fisiones en $^{235}\text{U}$, captura parasitaria en barras de control, moderación elástica en agua ligera, decaimiento de precursores con neutrones retardados ($\beta$) y balance térmico.
* **Control y Seguridad Intrínseca:** Regulación de reactividad mediante barras de control móviles (Boro/Cadmio), sistema SCRAM de parada rápida de emergencia y coeficiente de temperatura Doppler negativo de seguridad pasiva.
* **Motor Pygame Top-Down:** Animación de vasija de contención cilíndrica blindada, efecto de radiación Cherenkov reactivo a la potencia, destellos térmicos de fisión, partículas neutrónicas (rápidas/térmicas) y tablero HUD con osciloscopio en vivo.
* **Ubicación:** `nuclear/`

---

## Instrucciones de Ejecución

### Ejecutar Tarea 1 (Líneas de Espera - CLI)

Desde la raíz del repositorio:
```bash
cd tarea1/calculator
python main.py --exercise 2 --servers 3 --lambda 15.0 --mu 6.0
```

O en modo interactivo:
```bash
cd tarea1/calculator
python main.py --exercise 1
```

### Ejecutar Tarea 2 (Teoría de Inventarios - GUI)

Desde la raíz del repositorio:
```bash
cd tarea2
python main.py
```

### Ejecutar Clase Simulación (Snake SimPy + Pygame)

Desde la raíz del repositorio:
```bash
cd claseSimulacion
python main.py             # Modo manual interactivo
python main.py --mode auto # Modo simulacion autonoma con IA
```

### Ejecutar Estación de Servicio (Gasolinera M/M/c SimPy + Pygame)

Desde la raíz del repositorio:
```bash
cd estacion
python main.py                                      # Vista grafica interactiva
python main.py --pumps 3 --lamb 5.0 --mu 2.0        # Parametrizado
python main.py --headless --duration 300            # Benchmarking sin ventana
```

### Ejecutar Automercado (Líneas de Espera SimPy + Pygame)

Desde la raíz del repositorio:
```bash
cd automercado
python main.py                                      # Vista grafica interactiva
python main.py --registers 4 --lamb 5.0 --mu 1.5    # Parametrizado
python main.py --queue-mode single                  # Fila unica central M/M/c
python main.py --headless --duration 300            # Benchmarking sin ventana
```

### Ejecutar Transporte (Optimización de Rutas Pygame)

Desde la raíz del repositorio:
```bash
cd transporte
python main.py                                      # Vista grafica interactiva
python main.py --origin VAL --dest CCS --speed 2.0  # Ruta especifica
python main.py --headless --auto --duration 30      # Benchmarking sin ventana
```

### Ejecutar Reactor Nuclear (SimPy + Pygame)

Desde la raíz del repositorio:
```bash
cd nuclear
python main.py                                      # Vista grafica interactiva
python main.py --enrichment 0.20 --rods 0.40        # Parametrizado
python main.py --headless --duration 60             # Benchmarking sin ventana
```

---

## Ejecución de Pruebas Unitarias

Cada tarea cuenta con su propia suite de pruebas automatizadas con `pytest`:

### Pruebas de Tarea 1
```bash
cd tarea1/calculator
pytest tests/ -v
```

### Pruebas de Tarea 2
```bash
cd tarea2
pytest tests/ -v
```

### Pruebas de Clase Simulación
```bash
cd claseSimulacion
pytest tests/ -v
```

### Pruebas de Estación de Servicio
```bash
cd estacion
pytest tests/ -v
```

### Pruebas de Automercado
```bash
cd automercado
pytest tests/ -v
```

### Pruebas de Transporte
```bash
cd transporte
pytest tests/ -v
```

### Pruebas de Reactor Nuclear
```bash
cd nuclear
pytest tests/ -v
```
