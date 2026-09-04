# Simulacion de Estacion de Gasolina: Modelo de Linea de Espera M/M/c (SimPy + Pygame)

**Universidad Jose Antonio Paez — Facultad de Ingenieria**  
**Escuela de Ingenieria en Computacion — Metodos Cuantitativos**

Proyecto cuantitativo de simulacion estocastica por eventos discretos implementado en Python bajo el paradigma de **Programacion Orientada a Objetos (POO)**. Modela el flujo de atencion de vehiculos en una estacion de servicio de combustible utilizando la teoria de lineas de espera ($M/M/c$ y $M/M/c/K$) mediante **SimPy**, y lo visualiza en tiempo real a traves de una interfaz grafica cenital (vista top-down) desarrollada con **Pygame**.

---

## 1. Fundamento Teorico: Teoria de Colas y Eventos Discretos

El sistema responde a la notacion de Kendall **M/M/c**:
* **M (Llegadas):** Proceso de Poisson con tiempos entre arribos distribuidos exponencialmente con parametro $\lambda$ (vehiculos por minuto).
* **M (Servicio):** Tiempos de atencion y despacho distribuidos exponencialmente con parametro $\mu$ por cada surtidor (vehiculos por minuto por bomba).
* **c (Servidores en Paralelo):** $c$ surtidores o bombas de combustible independientes que operan de forma simultanea y concurrente.
* **Disciplina de Atencion:** FIFO (First In, First Out) con capacidad de cola acotada ($K$) donde los vehiculos que encuentran la capacidad maxima de cola fisica se desvian (rechazo/balking).

### Formulacion Matematica Analitica (Modelo M/M/c)
1. **Intensidad de trafico ofrecida:**
   $$a = \frac{\lambda}{\mu}$$
2. **Factor de utilizacion de los servidores:**
   $$\rho = \frac{\lambda}{c \cdot \mu}$$
   *(Condicion de estabilidad estocastica: $\rho < 1$)*
3. **Probabilidad de que el sistema este vacio ($P_0$):**
   $$P_0 = \left[ \sum_{n=0}^{c-1} \frac{a^n}{n!} + \frac{a^c}{c!} \left(\frac{1}{1 - \rho}\right) \right]^{-1}$$
4. **Numero promedio de vehiculos en cola ($L_q$):**
   $$L_q = \frac{P_0 \cdot a^c \cdot \rho}{c! \cdot (1 - \rho)^2}$$
5. **Tiempo promedio de espera en cola ($W_q$):**
   $$W_q = \frac{L_q}{\lambda}$$
6. **Tiempo promedio total en el sistema ($W$):**
   $$W = W_q + \frac{1}{\mu}$$
7. **Numero promedio de vehiculos en el sistema ($L$):**
   $$L = L_q + a = \lambda \cdot W$$
8. **Probabilidad de demora de Erlang-C ($P_w$):**
   $$P_w = \frac{a^c}{c!} \left(\frac{1}{1 - \rho}\right) P_0$$

La simulacion contrasta en vivo estos valores analiticos teoricos contra las metricas empiricas acumuladas por los eventos discretos de SimPy.

---

## 2. Arquitectura de Software (POO)

El proyecto esta disenado de forma modular y desacoplada en capas:

```text
estacion/
├── main.py                     # Punto de entrada ejecutable y argumentos CLI
├── requirements.txt            # Dependencias del proyecto (simpy, pygame, pytest)
├── README.md                   # Documentacion tecnica y teorica
├── src/
│   ├── constants.py            # Constantes, paletas, coordenadas y enumeraciones
│   ├── models/                 # Capa de Dominio (POO)
│   │   ├── queue_model.py      # Calculadora analitica teorica M/M/c
│   │   ├── vehicle.py          # Entidad vehiculo con cinematica e historial temporal
│   │   ├── pump.py             # Entidad surtidor con estados y contadores
│   │   ├── tank.py             # Tanque de almacenamiento central de combustible
│   │   └── stats.py            # Colector y agregador de metricas operacionales
│   ├── simulation/             # Motor de Eventos Discretos
│   │   └── gas_station_sim.py  # Orquestador SimPy: arribos, despacho y cisterna
│   ├── view/                   # Capa de Presentacion Grafica (Pygame)
│   │   ├── station_view.py     # Renderizado top-down: pista, marquesina, bombas
│   │   ├── hud_view.py         # Panel lateral con telemetria en tiempo real
│   │   └── car_drawer.py       # Renderizado procedural vectorial de autos
│   └── engine/                 # Controlador y Sincronizacion
│       ├── controller.py       # StationController: sincroniza tick de Pygame con SimPy
│       └── input_handler.py    # Captura de teclado y atajos interactivos
└── tests/                      # Suite de pruebas automatizadas (pytest)
    ├── test_queue_theory.py    # Verificacion de formulas de colas M/M/c
    ├── test_simulation.py      # Verificacion de procesos SimPy y tanque
    ├── test_vehicle.py         # Verificacion cinematica y estados del vehiculo
    └── test_engine.py          # Verificacion de ejecucion headless
```

---

## 3. Elementos de la Visualizacion Top-Down

* **Area de Estacion (Cenital):**
  - Calzada principal de asfalto con carril de ingreso, zona de cola demarcada con lineas amarillas discontinuas y via de salida.
  - Pista de concreto de la estacion con marquesina semi-transparente, columnas estructurales y senalizacion vial.
  - **Islas de Bombas ($c=3$):** Surtidores independientes con luces LED de estado:
    - **Verde:** Bomba libre disponible.
    - **Ambar:** Bomba ocupada surtiendo combustible (con manguera conectada al auto).
    - **Rojo:** Sin combustible disponible en el tanque central.
  - **Tanque Central:** Indicador superior del nivel subterraneo de combustible (litros disponibles y porcentaje).
* **Vehiculos en Movimiento:**
  - Carrocerias procedurales con variedad cromatica, faros, parabrisas y ruedas.
  - Transicion cinematica suave entre waypoints: ingreso -> cola ordenada -> bomba asignada -> repostaje con barra de progreso flotante -> salida a la calzada.
* **Panel Lateral (HUD):**
  - Reloj de simulacion (tiempo transcurrido, multiplicador de velocidad, FPS).
  - **Tabla Comparativa Cuantitativa:** Parametros analiticos $M/M/c$ versus estadisticas simuladas en tiempo real ($\rho$, $W_q$, $W$, $L_q$, $L$).
  - Metricas operacionales: arribos totales, vehiculos atendidos, vehiculos rechazados por cola llena y nivel de tanque.
  - Guia interactiva de comandos de teclado.

---

## 4. Instalacion y Requisitos

### Requisitos Previos
* Python 3.9 o superior.

### Instalacion de Dependencias
```bash
pip install -r requirements.txt
```

---

## 5. Modos de Ejecucion

### 1. Ejecucion Grafica Interactiva Estandar
```bash
python main.py
```

### 2. Parametrizacion por Linea de Comandos
Es posible modificar el numero de bombas, las tasas de llegada y servicio, y la velocidad inicial:
```bash
# Estacion con 3 bombas, lambda=5.0 veh/min, mu=2.0 veh/min, velocidad 2x
python main.py --pumps 3 --lamb 5.0 --mu 2.0 --speed 2.0
```

### 3. Modo Headless (Benchmarking y Validacion Cuantitativa)
Permite correr simulaciones extensas a maxima velocidad sin abrir ventana grafica, emitiendo un reporte cuantitativo al finalizar:
```bash
# Simular 10 minutos (600 segundos simulados) de operacion
python main.py --headless --duration 600
```

---

## 6. Controles Interactivos Durante la Simulacion

| Tecla | Accion |
|:---|:---|
| **[ESPACIO]** | Pausar o reanudar el reloj de la simulacion |
| **[1, 2, 3, 4]** | Ajustar multiplicador de velocidad: 1x, 2x, 5x o 10x |
| **[+] / [-]** | Incrementar o disminuir dinamicamente la tasa de llegada ($\lambda$) |
| **[C]** | Solicitar despacho de camion cisterna para reabastecer el tanque central |
| **[R]** | Reiniciar la simulacion y contadores a su estado inicial |
| **[ESC]** | Cerrar la ventana y desplegar el informe cuantitativo final en consola |

---

## 7. Pruebas Unitarias Automatizadas

El proyecto incluye una suite de 10 pruebas unitarias desarrolladas con `pytest` que validan el comportamiento matematico y de eventos discretos:

```bash
pytest tests/ -v
```

**Cobertura de pruebas:**
* Validacion analitica de las formulas $M/M/c$ frente a casos estandar de la literatura de investigacion de operaciones.
* Deteccion automatica de inestabilidad estocastica cuando $\rho \ge 1$.
* Avance temporal determinista y consumo de combustible en el entorno `SimPy`.
* Ciclo de reabastecimiento con camion cisterna.
* Cinemática e interpolacion de waypoints de vehiculos.
* Ejecucion correcta del motor en modo headless y generacion de reportes.
