# Simulacion de Sistema Discreto: Juego Snake (SimPy + Pygame)

**Universidad Jose Antonio Paez — Facultad de Ingenieria**  
**Escuela de Ingenieria en Computacion — Metodos Cuantitativos**

Proyecto practico de simulacion estocastica y por eventos discretos implementado en Python bajo el paradigma de **Programacion Orientada a Objetos (POO)**. Modela el comportamiento temporal, cinematica de la serpiente, ciclo de vida de alimentos y recoleccion de metricas cuantitativas mediante **SimPy**, visualizado en tiempo real a traves de una interfaz interactiva con **Pygame**.

---

## 1. Fundamento Teorico y Vinculacion con Metodos Cuantitativos

En la teoria de simulacion cuantitativa, los sistemas pueden clasificarse segun la evolucion de sus variables de estado:
* **Reloj de Simulacion Discreta (SimPy):** A diferencia de un juego de arcade tradicional donde la logica avanza ligada rigidamente a los fotogramas de la GPU (`FPS`), en este proyecto la evolucion del estado es gobernada por procesos estocasticos concurrentes en un entorno `simpy.Environment`:
  1. `snake_step_process`: Modela la temporizacion de avance de la serpiente como eventos de salto temporal (`yield env.timeout(dt)`).
  2. `food_lifecycle_process`: Modela la aparicion, permanencia y expiracion temporal de alimentos especiales (Bonus) bajo distribuciones de probabilidad estocasticas.
  3. `metrics_sampler_process`: Muestrea metricas operativas a intervalos regulares de tiempo simulado.
* **Sincronizacion de Relojes:** El bucle de `Pygame` avanza el reloj de eventos de SimPy de forma determinista mediante interpolacion temporal `env.run(until=sim_target_time)`, permitiendo variar la velocidad de simulacion (`1x`, `2x`, `4x`) sin desfasar la precision de los calculos cuantitativos.
* **Analisis de Eficiencia:** La simulacion calcula en tiempo real la razon de pasos discretos requeridos por cada alimento capturado ($\text{Pasos}/\text{Alimento}$), longitud maxima alcanzada y tiempo de supervivencia del agente.

---

## 2. Arquitectura de Software (POO)

El proyecto sigue una arquitectura desacoplada organizada en capas:

```text
claseSimulacion/
├── main.py                  # Punto de entrada y configuracion de parametros CLI
├── requirements.txt         # Dependencias (simpy, pygame, pytest)
├── README.md                # Documentacion tecnica y de ejecucion
├── src/
│   ├── constants.py         # Configuraciones de cuadricula, direcciones, estados y paleta
│   ├── models/              # Modelos del dominio de negocio (POO)
│   │   ├── point.py         # Value Object inmutable (x, y) con distancia Manhattan
│   │   ├── food.py          # Entidad de alimento con ciclo de vida y expiracion
│   │   ├── snake.py         # Entidad de la serpiente (cuerpo deque, giros y colisiones)
│   │   └── stats.py         # Rastreao de metricas operacionales cuantitativas
│   ├── simulation/          # Capa de eventos discretos SimPy
│   │   ├── environment.py   # Orquestador de procesos SimPy (avance, comida, muestreo)
│   │   └── ai_agent.py      # Agente de IA para simulacion autonoma (BFS + heuristica)
│   ├── view/                # Capa de visualizacion
│   │   └── renderer.py      # Renderizado de cuadricula, serpiente, HUD y metricas
│   └── engine/              # Controlador y orquestador del bucle
│       ├── controller.py    # GameController (sincroniza Pygame tick con SimPy)
│       └── input_handler.py # Traductor de eventos de teclado
└── tests/                   # Suite de pruebas unitarias automatizadas (pytest)
    ├── test_models.py       # Pruebas de geometria, colisiones y logica de entidades
    ├── test_simulation.py   # Pruebas de avance en SimPy y agente BFS
    └── test_engine.py       # Pruebas del controlador en modo headless
```

---

## 3. Modos de Operacion

1. **Modo Manual (Jugador):** El usuario controla la direccion de la serpiente con el teclado, permitiendo evaluar la jugabilidad tradicional con la fisica del motor de eventos discretos.
2. **Modo Auto (Simulacion Autonoma con IA):** Un agente de IA toma el control de la navegacion calculando rutas optimas mediante **Busqueda por Anchura (BFS)** hacia los alimentos y una heuristica de supervivencia basada en espacio navegable (flood fill) para prevenir autocolisiones y callejones sin salida.
3. **Modo Headless (Benchmarking):** Ejecucion sin ventana grafica orientada a pruebas de rendimiento, simulaciones Monte Carlo o ejecucion en servidores CI.

---

## 4. Requisitos e Instalacion

El proyecto requiere Python 3.10 o superior.

```bash
# Opcion A: Instalar dependencias en el entorno activo
pip install -r requirements.txt

# Opcion B: Usar el interprete de la sesion actual
/Users/robertosiracusa/Documents/AC/.venv/bin/pip install -r requirements.txt
```

---

## 5. Instrucciones de Ejecucion

### Ejecucion Interactiva (Modo Manual por Defecto)
```bash
python main.py
```

### Ejecucion con Agente de IA (Simulacion Autonoma)
```bash
python main.py --mode auto
```

### Ejecucion a Velocidad Acelerada (ej. 2x o 4x)
```bash
python main.py --mode auto --speed 2.0
```

### Ejecucion Headless (Pruebas Automatizadas)
```bash
python main.py --headless --duration 30.0 --mode auto
```

---

## 6. Controles del Teclado

| Tecla | Accion |
|-------|--------|
| **Flechas / W, A, S, D** | Cambiar direccion de la serpiente (Modo Manual) |
| **ESPACIO** | Pausar / Reanudar la simulacion |
| **M** | Alternar entre Modo Manual y Modo Auto IA |
| **1 / 2 / 3** | Ajustar multiplicador de velocidad (1x, 2x, 4x) |
| **R** | Reiniciar simulacion y restablecer reloj de SimPy |
| **ESC** | Salir de la simulacion y mostrar reporte en consola |

---

## 7. Pruebas Unitarias

Para ejecutar la suite de 12 pruebas unitarias automatizadas con `pytest`:

```bash
pytest tests/ -v
```
