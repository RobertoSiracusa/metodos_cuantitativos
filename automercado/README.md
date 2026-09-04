# Simulacion de Automercado: Modelos de Lineas de Espera (SimPy + Pygame)

**Universidad Jose Antonio Paez — Facultad de Ingenieria**  
**Escuela de Ingenieria en Computacion — Metodos Cuantitativos**

Proyecto cuantitativo de simulacion estocastica por eventos discretos implementado en Python bajo el paradigma de **Programacion Orientada a Objetos (POO)**. Modela el flujo de atencion de clientes y carritos de compra en una bateria de cajas registradoras de un automercado, comparando las dos disciplinas clasicas de la teoria de lineas de espera:
1. **Cola Unica Centralizada ($M/M/c$):** Fila comun para todas las cajas (disciplina bancaria/farmacia).
2. **Colas Paralelas Multiples ($c \times M/M/1$):** Una fila independiente por cada caja registradora (disciplina tradicional de automercado con eleccion de cola mas corta y caja express).

El sistema visualiza en tiempo real el comportamiento estocastico a traves de una interfaz grafica cenital (vista top-down 2D) desarrollada con **Pygame**, contrastando en vivo las metricas analiticas de la investigacion de operaciones frente a las metricas empiricas acumuladas en **SimPy**.

---

## 1. Fundamento Teorico: Modelos Cuantitativos de Colas

### Notacion de Kendall y Parametros del Sistema
* **M (Llegadas Poisson):** Intervalos entre arribos distribuidos exponencialmente con parametro $\lambda$ (clientes por minuto).
* **M (Servicio Exponencial):** Tiempos de atencion en caja distribuidos exponencialmente con parametro $\mu$ (clientes atendidos por minuto por cada caja registradora).
* **c (Servidores en Paralelo):** $c$ cajas registradoras operando de forma simultanea y concurrente ($1 \le c \le 5$).
* **Capacidad de cola acotada ($K$):** Si las colas fisicas superan el umbral maximo tolerable, los clientes entrantes desisten de ingresar (rechazo o *balking*).

---

### A. Modelo Analitico M/M/c (Cola Unica Centralizada)
1. **Intensidad de trafico ofrecida (Erlangs):**
   $$a = \frac{\lambda}{\mu}$$
2. **Factor de utilizacion de los servidores:**
   $$\rho = \frac{\lambda}{c \cdot \mu} \quad (\text{Estabilidad estocastica: } \rho < 1)$$
3. **Probabilidad de que el sistema este vacio ($P_0$):**
   $$P_0 = \left[ \sum_{n=0}^{c-1} \frac{a^n}{n!} + \frac{a^c}{c!} \left(\frac{1}{1 - \rho}\right) \right]^{-1}$$
4. **Numero promedio de clientes en cola ($L_q$):**
   $$L_q = \frac{P_0 \cdot a^c \cdot \rho}{c! \cdot (1 - \rho)^2}$$
5. **Tiempo promedio de espera en cola ($W_q$):**
   $$W_q = \frac{L_q}{\lambda}$$
6. **Tiempo promedio total de permanencia en la tienda ($W$):**
   $$W = W_q + \frac{1}{\mu}$$
7. **Numero promedio de clientes en el automercado ($L$):**
   $$L = L_q + a = \lambda \cdot W$$
8. **Probabilidad de demora de Erlang-C ($P_w$):**
   $$P_w = \frac{a^c}{c!} \left(\frac{1}{1 - \rho}\right) P_0$$

---

### B. Modelo Analitico $c \times M/M/1$ (Colas Multiples Paralelas)
Cuando cada cliente se incorpora a una cola individual independiente, el flujo total de arribos $\lambda$ se distribuye equitativamente entre las $c$ cajas en estado estacionario ($\lambda_i = \lambda / c$):
1. **Utilizacion individual por caja:**
   $$\rho_i = \frac{\lambda / c}{\mu} = \rho$$
2. **Clientes en cola por caja individual ($L_{q,1}$):**
   $$L_{q,1} = \frac{\rho^2}{1 - \rho}$$
3. **Total de clientes en cola en el automercado ($L_q$):**
   $$L_{q,\text{paralelo}} = c \cdot L_{q,1} = c \cdot \frac{\rho^2}{1 - \rho}$$
4. **Tiempo promedio de espera en cola ($W_q$):**
   $$W_{q,\text{paralelo}} = \frac{L_{q,\text{paralelo}}}{\lambda} = \frac{\rho}{\mu(1 - \rho)}$$
5. **Tiempo total en el automercado ($W$):**
   $$W_{\text{paralelo}} = \frac{1}{\mu(1 - \rho)}$$

> **Teorema de Eficiencia Cuantitativa:** Para cualquier sistema con $c > 1$ y $\rho < 1$, se cumple rigurosamente que $W_q^{M/M/c} < W_q^{c \times M/M/1}$. La unificacion en una cola centralizada optimiza la utilizacion de los tiempos ociosos de los cajeros y reduce significativamente la congestion.

---

## 2. Arquitectura de Software (POO)

El diseno sigue una arquitectura modular en capas desacopladas:

```text
automercado/
├── main.py                     # Punto de entrada ejecutable y argumentos CLI
├── requirements.txt            # Dependencias del proyecto (simpy, pygame, pytest)
├── README.md                   # Documentacion tecnica y matematica
├── src/
│   ├── constants.py            # Constantes, estados, paletas de color y coordenadas
│   ├── models/                 # Capa de Dominio (POO)
│   │   ├── queue_model.py      # Calculadoras analiticas M/M/c y c x M/M/1
│   │   ├── customer.py         # Entidad Cliente con carrito, articulos y cinematica
│   │   ├── checkout.py         # Entidad Caja Registradora, cinta, escaner y cajero
│   │   └── stats.py            # Colector y agregador de metricas cuantitativas
│   ├── simulation/             # Motor de Eventos Discretos
│   │   └── market_sim.py       # Orquestador SimPy: arribos, colas, atencion y salida
│   ├── view/                   # Capa de Presentacion Grafica (Pygame)
│   │   ├── market_view.py      # Renderizado top-down: piso, pasillos, cajas, molinetes
│   │   ├── hud_view.py         # Panel lateral con telemetria y comparativa en vivo
│   │   └── customer_drawer.py  # Renderizado procedural vectorial de cliente y carrito
│   └── engine/                 # Controlador y Sincronizacion
│       ├── controller.py       # MarketController: sincroniza tick Pygame con SimPy
│       └── input_handler.py    # Captura de teclado y atajos interactivos
└── tests/                      # Suite de pruebas automatizadas (pytest)
    ├── test_queue_theory.py    # Verificacion formulas teoricas M/M/c y c x M/M/1
    ├── test_simulation.py      # Verificacion de procesos SimPy y transiciones de cola
    ├── test_customer.py        # Verificacion cinematica, articulos y tiempos
    └── test_engine.py          # Verificacion de ejecucion headless y reporte
```

---

## 3. Elementos de la Visualizacion Top-Down

* **Area Comercial (Cenital):**
  - **Piso de baldosas pulidas:** Cuadricula clara con acabados limpios y demarcacion perimetral.
  - **Acceso y Carritos:** Puerta corrediza de entrada, alfombra sensorizada y bahia de carritos de compras apilados.
  - **Gondolas de mercancia organizadas por departamento:**
    1. Frutas y Verduras (Verde esmeralda)
    2. Abarrotes y Granos (Naranja corporativo)
    3. Panaderia y Dulces (Amarillo trigo)
    4. Carnes y Embutidos (Rojo carmin)
    5. Lacteos y Quesos (Azul royal)
    6. Bebidas y Licores (Purpura amatista)
* **Bateria de Cajas Registradoras:**
  - Estaciones de cobro paralelas con cinta transportadora de goma negra y articulos en transito.
  - Escaner laser de codigo de barras con haz luminoso activo durante la atencion.
  - Cajero/cajera top-down con uniforme corporativo y terminal POS con monitor.
  - Luces LED de estado en poste superior:
    - **Verde:** Caja abierta y disponible.
    - **Amarillo:** Atendiendo cliente y escaneando compras.
    - **Rojo:** Caja cerrada fuera de servicio.
  - Soporte para **Caja 1 Express** (prioridad para clientes con $\le 10$ articulos).
* **Clientes y Carritos en Movimiento:**
  - Renderizado procedural: cabeza, hombros, franela cromatica, brazos sujetando el manillar del carrito.
  - Carrito metalico con ruedas y articulos de colores visibles segun la cesta de compra.
  - Insignia flotante con el contador de articulos pendientes.
  - Navegacion suave por waypoints: entrada -> compras -> eleccion de cola -> caja -> salida por molinetes.
* **Panel Lateral de Telemetria (HUD):**
  - Reloj de simulacion, velocidad temporal activa y tasa de refresco (FPS).
  - **Tabla comparativa cuantitativa en vivo:** Parametros teoricos versus estadisticas empiricas de SimPy ($\lambda$, $\mu$, $c$, $\rho$, $P_0$, $L_q$, $W_q$, $L$, $W$).
  - Indicadores operativos: clientes arribados, atendidos, rechazados (*balking*), items escaneados e ingresos estimados.
  - Guia interactiva de comandos de teclado.

---

## 4. Instalacion y Requisitos

### Requisitos Previos
* Python 3.9 o superior.

### Dependencias
Instalar las dependencias listadas en `requirements.txt`:
```bash
pip install -r requirements.txt
```
*(O utilizar el entorno virtual existente en `claseSimulacion/venv`)*.

---

## 5. Instrucciones de Ejecucion

### Modo Grafico Interactivo
Desde la raiz de `automercado/`:
```bash
python main.py
```

### Parametrizacion por Linea de Comandos
```bash
# Iniciar con 3 cajas, tasa de arribos de 6.0/min y atencion de 2.0/min
python main.py --registers 3 --lamb 6.0 --mu 2.0

# Iniciar directamente en disciplina de Cola Unica Central (M/M/c)
python main.py --queue-mode single

# Iniciar a 2x de velocidad
python main.py --speed 2.0
```

### Modo Headless (Benchmarking Cuantitativo sin Ventana)
Para ejecucion desatendida y generacion instantanea de reportes comparativos:
```bash
python main.py --headless --duration 300
```

---

## 6. Controles Interactivos en Tiempo de Ejecucion

| Tecla | Accion |
|---|---|
| `[ESPACIO]` | Pausar / Reanudar la simulacion |
| `[1, 2, 3, 4]` | Modificar velocidad (1x, 2x, 5x, 10x) |
| `[+]` / `[-]` | Aumentar / Disminuir tasa de arribos $\lambda$ (+/- 0.5 clientes/min) |
| `[A]` | Abrir una nueva caja registradora (incrementa $c$) |
| `[Z]` | Cerrar una caja registradora (decrementa $c$) |
| `[M]` | Alternar disciplina de cola: **Cola Unica ($M/M/c$)** vs **Colas Paralelas ($c \times M/M/1$)** |
| `[R]` | Reiniciar simulacion a estado inicial |
| `[ESC]` | Finalizar ejecucion y desplegar reporte analitico en consola |

---

## 7. Ejecucion de Pruebas Unitarias

La suite de pruebas automatizadas verifica la precision numerica de los modelos matematicos, el avance estocastico de SimPy, la cinematica y el modo headless:

```bash
pytest tests/ -v
```
