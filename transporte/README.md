# Optimizacion de Redes de Transporte y Asignacion de Flota (Pygame + Grafos)

**Universidad Jose Antonio Paez — Facultad de Ingenieria**  
**Escuela de Ingenieria en Computacion — Metodos Cuantitativos**

Proyecto cuantitativo de investigacion de operaciones y optimizacion de redes desarrollado bajo el paradigma de **Programacion Orientada a Objetos (POO)**. Implementa la resolucion del **Problema de la Ruta Mas Corta (Shortest Path Problem)** mediante los algoritmos de **Dijkstra** y **$A^*$**, combinado con un modelo de **Asignacion de Vehiculos y Flota de Transporte (Vehicle Routing & Dispatching)**. El sistema esta totalmente integrado a una interfaz interactiva en tiempo real desarrollada con **Pygame**, que permite seleccionar pares origen-destino sobre un grafo vial, visualizar la cinemática de los camiones de carga y contrastar cuantitativamente el ahorro economico frente a rutas alternativas.

---

## 1. Fundamento Teorico Cuantitativo

### 1.1. Modelado de la Red de Transporte como Grafo Ponderado
La red vial se formaliza mediante un grafo no dirigido o bidireccional ponderado $G = (V, E, W)$:
* **Vertices $V$:** Representan nodos logisticos del territorio (Centros de Distribucion o *Hubs*, Ciudades con demanda de consumo, e Intersecciones viales o Peajes).
* **Aristas $E$:** Tramos viales directos entre pares de nodos $(u, v) \in V \times V$.
* **Ponderaciones $W$:** Cada arista posee un vector de atributos cuantificables:
  * $d_{uv}$: Distancia fisica vial en kilometros ($km$).
  * $p_{uv}$: Tarifa fija de peajes y servicios en unidades monetarias (\$).
  * $v_{\max}$: Limite maximo de velocidad permitido ($km/h$).

### 1.2. Formulacion Matematica del Camino Minimo (Shortest Path)
Dado un nodo origen $s \in V$ y un nodo destino $t \in V$, el problema busca encontrar la secuencia de aristas $(e_1, e_2, \dots, e_k)$ que minimice la funcion de costo total:

$$\min \sum_{e \in E} c_e \cdot x_e$$

Sujeto a las restricciones de conservacion de flujo:

$$\sum_{j \in V} x_{ij} - \sum_{k \in V} x_{ki} = \begin{cases} 1 & \text{si } i = s \\ -1 & \text{si } i = t \\ 0 & \text{en otro caso} \end{cases} \quad \forall i \in V$$

$$x_{ij} \in \{0, 1\}$$

Donde el costo del tramo para un camion de tipo $k$ con costo operativo por kilometro $c_k$ se define como:
$$c_e = (d_e \cdot c_k) + p_e$$

### 1.3. Algoritmos de Optimizacion Implementados
1. **Algoritmo de Dijkstra (Exacto):**
   * Mantiene una cola de prioridad min-heap con las distancias tentativas minimas $g(v)$.
   * Garantiza la solucion optima global en complejidad temporal $O((|E| + |V|) \log |V|)$.
2. **Algoritmo $A^*$ (Busqueda Heuristica Informada):**
   * Evalua cada vertice mediante la funcion de costo:
     $$f(n) = g(n) + h(n)$$
     donde $g(n)$ es el costo acumulado desde el origen hasta $n$, y $h(n)$ es la funcion heuristica.
   * **Heuristica Admisible y Consistente:** Se utiliza la distancia euclidiana espacial entre las coordenadas cartesianas del nodo $n$ y el nodo destino $t$:
     $$h(n) = \alpha \cdot \sqrt{(x_t - x_n)^2 + (y_t - y_n)^2} \le d(n, t)$$
     Garantizando que nunca sobrestime el costo real de viaje hacia la meta.
3. **Analisis Cuantitativo de Ahorro:**
   * El sistema calcula concurrentemente una ruta secundaria viable penalizando la arista critica de la ruta optima, permitiendo calcular en vivo el beneficio economico:
     $$\text{Ahorro} = \text{Costo}_{\text{Alternativa}} - \text{Costo}_{\text{Optima}}$$

### 1.4. Modelo de Asignacion de Flota de Camiones
Para despachar un pedido con demanda $q$ toneladas entre el nodo $s$ y el nodo $t$:
1. **Restriccion de Capacidad:** Solo son elegibles los camiones libres cuya capacidad maxima sea suficiente:
   $$Q_k \ge q$$
2. **Optimizacion de Despacho:** Se evalua la ubicacion actual de cada camion eligible $u_k$ y se selecciona el que minimice el costo total acumulado:
   $$\min_{k} \left[ \text{Costo}(u_k \to s) + \text{Costo}(s \to t) \right]$$

---

## 2. Arquitectura de Software (POO)

El diseno sigue una arquitectura modular desacoplada en capas:

```text
transporte/
├── main.py                         # Punto de entrada interactivo y CLI configurable
├── requirements.txt                # Dependencias (pygame, pytest)
├── README.md                       # Documentacion teorica, arquitectonica y de uso
├── src/
│   ├── constants.py                # Red vial base, tipos de camiones, estados y paletas
│   ├── models/                     # Capa de Dominio Logistico (POO)
│   │   ├── graph.py                # Modelado del grafo: Node, Edge, TransportGraph
│   │   ├── pathfinding.py          # Optimizadores de camino minimo: Dijkstra y A*
│   │   ├── truck.py                # Entidad camion: cinematica 2D, estados y capacidades
│   │   ├── order.py                # Modelo de ordenes de carga y metricas de flete
│   │   └── fleet_manager.py        # Gestor de asignacion optima de flota y cola de pedidos
│   ├── simulation/                 # Motor de Simulacion Temporal
│   │   └── transport_sim.py        # Sincronizacion de pedidos, pasos temporales y telemetria
│   ├── view/                       # Capa de Presentacion Grafica (Pygame)
│   │   ├── network_view.py         # Renderizado de carreteras, halos de nodos y rutas
│   │   ├── truck_view.py           # Renderizado vectorial de camiones con rotacion 2D
│   │   └── hud_view.py             # Tablero lateral con telemetria, comparativas y atajos
│   └── engine/                     # Control y Sincronizacion
│       ├── controller.py           # Orquestador del bucle principal y modo headless
│       └── input_handler.py        # Captura de eventos de raton y atajos de teclado
└── tests/                          # Suite de pruebas automatizadas (pytest)
    ├── test_graph_and_pathfinding.py # Validacion de Dijkstra, A* y equivalencias
    ├── test_fleet_assignment.py      # Validacion de asignacion y capacidad de carga
    ├── test_truck_kinematics.py      # Validacion de movimiento, rotacion y descarga
    └── test_headless_engine.py       # Validacion de reportes cuantitativos en headless
```

---

## 3. Caracteristicas y Controles Interactivos en Pygame

* **Seleccion Interactiva de Nodos:** Al hacer clic izquierdo sobre cualquier nodo en pantalla, se define de inmediato como **Origen** (halo cyan) o **Destino** (halo verde neon), recalculando y trazando la ruta optima en tiempo real.
* **Resaltado Visual de Rutas:**
  * **Cyan Neon:** Ruta mas corta calculada con flechas orientadas en el sentido de avance.
  * **Rosa / Rojo:** Ruta alternativa suboptima de comparacion para visualizacion de trade-offs.
* **Despacho Inmediato:** Al pulsar `[D]`, el sistema busca el camion mas cercano con capacidad adecuada, calcula la ruta de reposicion hacia el origen, realiza el proceso de carga y traslada la mercancia al destino final.
* **Modo Automatico Continuo:** Pulsar `[A]` activa un generador estocastico continuo de solicitudes de carga entre los nodos de la red.
* **Telemetria en Tiempo Real:** El panel lateral HUD despliega kilometros acumulados, toneladas movilizadas, costo de fletes y ahorro generado por optimizacion.

### Tabla de Atajos de Teclado
| Tecla | Accion |
|---|---|
| **Clic Izquierdo** | Seleccionar Origen y Destino sobre el mapa |
| **`[D]`** | Despachar camion optimo para la ruta seleccionada |
| **`[A]`** | Activar / Desactivar despacho automatico continuo |
| **`[T]`** | Alternar algoritmo en caliente (Dijkstra $\leftrightarrow$ A*) |
| **`[1, 2, 3, 4]`** | Modificar velocidad de simulacion ($1\times, 2\times, 5\times, 10\times$) |
| **`[ESPACIO]`** | Pausar / Reanudar la simulacion |
| **`[R]`** | Reiniciar la simulacion y reubicar la flota |
| **`[ESC]`** | Salir y desplegar el reporte cuantitativo en consola |

---

## 4. Instrucciones de Ejecucion

### Ejecucion Interactiva (Ventana Grafica Pygame)

Desde la raiz del repositorio (`metodos_cuantitativos/`):
```bash
cd transporte
python main.py
```

Con parametros iniciales personalizados:
```bash
python main.py --origin VAL --dest CCS --cargo 18.0 --speed 2.0
```

Con algoritmo A* y despacho automatico activado desde el inicio:
```bash
python main.py --algorithm astar --auto --speed 5.0
```

### Ejecucion en Modo Headless (Benchmarks Cuantitativos sin Ventana)

Ideal para servidores, integracion continua o extraccion masiva de metricas:
```bash
python main.py --headless --auto --duration 30
```

---

## 5. Ejecucion de Pruebas Unitarias

La suite de pruebas automatizadas verifica la correccion matematica de los algoritmos de caminos minimos, el respeto a las restricciones de capacidad de los camiones y la cinematica en 2D:

Desde el directorio `transporte/`:
```bash
pytest tests/ -v
```
