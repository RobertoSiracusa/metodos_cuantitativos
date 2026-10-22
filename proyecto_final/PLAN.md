# Plan — Simulador de Optimización para Redes de Centros de Datos

**Universidad José Antonio Páez — Facultad de Ingeniería — Métodos Cuantitativos**
**Proyecto final, octubre 2026**
**Equipo:** Roberto Siracusa (C.I. 30.195.953) · Ignacio Acena (C.I. 31.352.123)

Estado: **COMPLETO 2026-10-22** — F1 a F6 implementadas (71 tests en verde). Ver `README.md` y `GUIA_DEFENSA.md`.

Pauta oficial: `Proyecto Metodos Cuantitativos Octubre de 2026.pdf` (en esta carpeta).

---

## 1. Requisitos del enunciado (trazabilidad)

| ID | Requisito | Módulo | Pts |
|----|-----------|--------|-----|
| R1 | Ruta más corta (menor latencia) entre routers con programación dinámica | M1 | 5 |
| R2 | Modelo volumen-carga (mochila): maximizar valor de tareas sin exceder capacidad del servidor | M1 | |
| R3 | Función no lineal carga→temperatura; puntos estacionarios (máx, mín, inflexión) por diferenciación; punto crítico de enfriamiento de emergencia | M2 | 5 |
| R4 | Método de gradiente para ajustar potencia de ventiladores en tiempo real (mínimo consumo) | M2 | |
| R5 | Lagrange: rendimiento f(E1..En) por clúster, sujeto a energía total máxima | M2 | |
| R6 | SimPy: llegadas aleatorias (colas), tiempo de procesamiento, fallas estocásticas de nodos | M3 | 5 |
| R7 | Conexión a API de IA y generación de reportes PDF | M3 | |
| R8 | Pygame: mapa de topología con tráfico en movimiento | M3 | |
| R9 | Pygame: indicador visual cuando la ruta más corta cambia por congestión | M3 | |
| R10 | Pygame: gráficos en tiempo real del gradiente (enfriamiento) y de Lagrange (reparto de energía) | M3 | |
| P2 | Programación orientada a objetos | todos | |
| P6 | Validación de datos del usuario (comandos y datos cargados) | todos | |
| P7 | Datos por defecto para pruebas | todos | |
| P8 | Por módulo: funcionamiento e **independencia**, legibilidad/comentarios, conceptos aplicados | todos | |
| P3 | Defensa (5 pts), presencial | — | 5 |

---

## 2. Arquitectura propuesta (mismo patrón que `tarea3/`)

```text
proyecto_final/
├── main.py                         # Entrada: GUI Pygame / --headless / --modulo <m1|m2> standalone
├── requirements.txt
├── .env.example                    # GEMINI_API_KEY (la real sigue en el .env de la raíz, ignorado)
├── data/
│   └── escenario_default.json      # Datos por defecto (P7): topología, servidores, tareas, clústeres
├── src/
│   ├── core/
│   │   ├── network_entities.py     # Nodo, Router, Servidor, Enlace, Paquete
│   │   ├── red.py                  # Red, Cluster
│   │   ├── programacion_dinamica/
│   │   │   ├── base.py             # ModeloProgramacionDinamica (ABC)
│   │   │   ├── ruta_mas_corta.py   # R1
│   │   │   └── mochila.py          # R2
│   │   └── no_lineal/
│   │       ├── base.py             # Optimizador (ABC)
│   │       ├── modelo_termico.py   # R3
│   │       ├── gradiente_enfriamiento.py  # R4
│   │       └── lagrange_energia.py # R5
│   ├── simulation/
│   │   ├── motor_simpy.py          # R6: MotorSimulacion, EstadoSimulacion
│   │   └── metricas.py             # MetricasColas
│   ├── gui/
│   │   ├── app.py                  # AplicacionPygame
│   │   └── paneles.py              # R8-R10: Panel (ABC) y sus subclases
│   ├── services/
│   │   ├── ia.py                   # R7: ProveedorIA, ClienteGemini (patrón de tarea3)
│   │   └── reporte_pdf.py          # R7: GeneradorReportePDF
│   └── utils/
│       ├── config.py
│       └── validators.py           # P6
├── tests/                          # pytest por módulo, con casos resueltos a mano
├── outputs/                        # Reportes PDF generados
└── README.md
```

**Independencia (P8):** cada modelo matemático (`core/`) no importa SimPy ni Pygame; se puede
ejecutar y testear solo (`python main.py --modulo m1`, `--modulo m2`). El motor SimPy los consume; la
GUI sólo lee el estado del motor.

---

## 2.1 Diseño de clases (P2 — programación orientada a objetos)

### Diagrama (texto)

```text
Herencia ( ◁── )                         Composición ( ◆── "tiene" ) / uso ( ··> )

Nodo (ABC)                               Red ◆── Nodo (1..*)
 ├◁── Router   (capa: núcleo/agreg./ToR)  Red ◆── Enlace (1..*)
 └◁── Servidor (capacidad, cola)          Cluster ◆── Servidor (1..*)

ModeloProgramacionDinamica (ABC)         MotorSimulacion ◆── Red
 ├◁── RutaMasCorta                        MotorSimulacion ◆── RutaMasCorta
 └◁── Mochila                             MotorSimulacion ◆── Mochila (una por servidor)
                                          MotorSimulacion ◆── ModeloTermico
Optimizador (ABC)                         MotorSimulacion ◆── Optimizador (1..*)
 ├◁── GradienteEnfriamiento               MotorSimulacion ◆── MetricasColas
 └◁── AsignadorLagrange                   MotorSimulacion ··> EstadoSimulacion (snapshot)

Panel (ABC)                              AplicacionPygame ◆── MotorSimulacion
 ├◁── PanelTopologia                      AplicacionPygame ◆── Panel (1..*)
 ├◁── PanelTermico                        Panel ··> EstadoSimulacion (sólo lectura)
 ├◁── PanelGradiente
 ├◁── PanelLagrange                      GeneradorReportePDF ◆── ProveedorIA
 └◁── PanelEventos                        GeneradorReportePDF ··> EstadoSimulacion

ProveedorIA (ABC)                        Configuracion ··> Validador
 ├◁── ClienteGemini
 └◁── ProveedorSinConexion (sin clave o sin red)
```

### Responsabilidades y métodos públicos

| Clase | Archivo | Responsabilidad | Métodos / propiedades públicas |
|-------|---------|-----------------|--------------------------------|
| `Nodo` (ABC) | `core/network_entities.py` | Estado común de un nodo: id, posición, operativo o caído | `fallar()`, `reparar()`, `esta_operativo`, `tiempo_servicio(paquete)` *(abstracto)* |
| `Router` | idem | Reenvía paquetes con latencia de procesamiento | `tiempo_servicio(paquete)`, `capa` |
| `Servidor` | idem | Procesa tareas dentro de su capacidad de RAM/CPU | `tiempo_servicio(paquete)`, `capacidad`, `carga_actual`, `encolar(paquete)` |
| `Enlace` | idem | Conexión entre dos nodos con latencia que crece con la congestión | `costo_actual()`, `entrar(paquete)`, `salir(paquete)` |
| `Paquete` | idem (`@dataclass`) | Tarea en tránsito: requerimiento (peso) y prioridad (valor) | atributos de sólo lectura |
| `Red` | `core/red.py` | Grafo por etapas; consulta de vecinos y nodos activos | `etapas()`, `vecinos(nodo)`, `enlace(a, b)`, `nodos_operativos()` |
| `Cluster` | idem | Agrupa servidores; expone su demanda para Lagrange | `demanda()`, `energia_asignada` |
| `ModeloProgramacionDinamica` (ABC) | `core/programacion_dinamica/base.py` | Esqueleto común: construir tabla, reconstruir solución | `resolver()` *(plantilla)*, `tabla` (copia de sólo lectura); `_construir_tabla()` y `_reconstruir()` abstractos |
| `RutaMasCorta` | `.../ruta_mas_corta.py` | Recursión hacia atrás por etapas (R1) | `resolver(origen, destino) → ResultadoRuta` |
| `Mochila` | `.../mochila.py` | Mochila 0/1 tabular (R2) | `resolver(paquetes) → ResultadoMochila` |
| `ModeloTermico` | `core/no_lineal/modelo_termico.py` | `T(c)` y su análisis por derivadas (R3) | `temperatura(c)`, `derivada(c)`, `segunda_derivada(c)`, `puntos_estacionarios()`, `punto_inflexion()`, `punto_critico()` |
| `Optimizador` (ABC) | `core/no_lineal/base.py` | Interfaz común para optimizadores que se actualizan cada tick | `actualizar(estado) → ResultadoOptimizacion` *(abstracto)*, `historial`, `series_para_grafico()` |
| `GradienteEnfriamiento` | `.../gradiente_enfriamiento.py` | Un paso de gradiente por tick sobre `E(v)` (R4) | `actualizar(estado)`, `optimo_analitico(Q)`, `velocidad_actual` |
| `AsignadorLagrange` | `.../lagrange_energia.py` | Reparto de `E_max` entre clústeres con KKT (R5) | `actualizar(estado)`, `resolver(demandas, e_max)`, `lambda_actual` |
| `MetricasColas` | `simulation/metricas.py` | Acumula `Wq`, `W`, `Lq`, utilización, pérdidas | `registrar(evento)`, `resumen()`, `comparar_mm1(lam, mu)` |
| `MotorSimulacion` | `simulation/motor_simpy.py` | Procesos SimPy (llegadas, servicio, fallas, control) e integración de M1 y M2 (R6) | `avanzar(hasta)`, `estado() → EstadoSimulacion`, `suscribir(observador)` |
| `EstadoSimulacion` | idem (`@dataclass(frozen=True)`) | Foto inmutable del sistema para la GUI y el PDF | atributos de sólo lectura |
| `Panel` (ABC) | `gui/paneles.py` | Área del dashboard | `dibujar(superficie, estado)` *(abstracto)* |
| `PanelTopologia`, `PanelTermico`, `PanelGradiente`, `PanelLagrange`, `PanelEventos` | idem | Cada gráfico de R8-R10 | `dibujar(superficie, estado)` |
| `AplicacionPygame` | `gui/app.py` | Bucle principal: avanza el motor y dibuja los paneles | `ejecutar()` |
| `ProveedorIA` (ABC) | `services/ia.py` | Interfaz para pedir un análisis | `analizar(resumen) → str` *(abstracto)* |
| `ClienteGemini` | idem | Llamada HTTP a Gemini (R7) | `analizar(resumen)` |
| `ProveedorSinConexion` | idem | Respuesta fija cuando no hay clave o red | `analizar(resumen)` |
| `GeneradorReportePDF` | `services/reporte_pdf.py` | Arma el PDF con métricas, gráficos y el análisis de la IA (R7) | `generar(estado, ruta_salida) → Path` |
| `Configuracion` | `utils/config.py` | Carga el escenario JSON o los valores por defecto (P7) | `desde_archivo(ruta)`, `por_defecto()` |
| `Validador` / `ErrorValidacion` | `utils/validators.py` | Valida argumentos de comandos y datos cargados (P6) | `validar_rango(...)`, `validar_escenario(dict)`, excepción propia con mensaje claro |

### Dónde se aplica cada pilar (guía para la defensa)

| Pilar | Dónde | Cómo |
|-------|-------|------|
| **Abstracción** | `Nodo`, `ModeloProgramacionDinamica`, `Optimizador`, `Panel`, `ProveedorIA` | Clases abstractas (`abc.ABC`) que definen *qué* hace cada familia sin fijar *cómo* |
| **Encapsulamiento** | `Servidor._carga`, `Enlace._en_transito`, tablas de DP, `historial` | Estado interno con `_` y acceso por propiedades; `tabla` e `historial` devuelven copias; resultados como `@dataclass(frozen=True)` |
| **Herencia** | `Router`/`Servidor` de `Nodo`; `RutaMasCorta`/`Mochila` de `ModeloProgramacionDinamica`; etc. | El código común (fallar/reparar, el esqueleto `resolver()`, el historial) vive una sola vez en la base |
| **Polimorfismo** | Motor: `for opt in optimizadores: opt.actualizar(estado)`; GUI: `for p in paneles: p.dibujar(...)`; SimPy: `nodo.tiempo_servicio(paquete)`; reporte: `proveedor.analizar(...)` | El llamador no sabe la clase concreta; agregar un optimizador o un panel nuevo no cambia el bucle |
| **Composición** | `Red`, `Cluster`, `MotorSimulacion`, `AplicacionPygame`, `GeneradorReportePDF` | Los objetos se arman con otros en vez de heredar de ellos |
| **Patrones** | *Template Method* (`resolver()` de DP), *Observer* (`suscribir` para cambio de ruta y caída de nodo, R9), *Null Object* (`ProveedorSinConexion`) | Nombrados en los docstrings para poder explicarlos |

**Regla de dependencias:** `core/` no importa nada de `simulation/`, `gui/` ni `services/`. `gui/` y
`services/` sólo leen `EstadoSimulacion`; nunca modifican el motor. Así se cumple la independencia
de módulos (P8) y cada clase de `core/` se testea sola.

---

## 3. Módulo 1 — Programación dinámica

### R1. Ruta más corta
- **Propuesta:** red por etapas (modelo de la diligencia / *stagecoach* del curso):
  `Gateway → Routers núcleo → Routers agregación → Switches ToR → Clúster de servidores`.
- Recursión hacia atrás: `f_n(s) = min_x { c(s, x) + f_{n+1}(x) }`, con tabla de etapas que se
  puede mostrar paso a paso en la defensa.
- Costo del enlace = latencia base + término de congestión según la cola del enlace
  (p. ej. `c = l0 · (1 + ρ / (1 − ρ))`). Nodo caído = costo infinito.
- Se recalcula ante cada cambio de congestión o falla; si la ruta cambia, se emite un evento (R9).

### R2. Mochila (volumen-carga)
- Mochila 0/1 por servidor: capacidad entera (unidades de RAM/CPU), cada tarea con peso
  (requerimiento) y valor (prioridad).
- DP tabular `V[i][w] = max(V[i-1][w], V[i-1][w - w_i] + v_i)` con reconstrucción de la solución.
- En la simulación se aplica por **ventana de despacho**: las tareas en cola de un servidor se
  seleccionan con la mochila; las no elegidas esperan a la próxima ventana.

---

## 4. Módulo 2 — Optimización no lineal

### R3. Modelo térmico (una variable)
- **Propuesta:** polinomio cúbico `T(c)` con carga `c ∈ [0, 100] %`, elegido para que tenga
  máximo local, mínimo local y punto de inflexión **dentro** del dominio.
- `T'(c) = 0` → puntos estacionarios; `T''(c)` → clasificación; `T''(c) = 0` → inflexión.
  Cálculo analítico (fórmula de la cuadrática), sin librerías simbólicas, para que se vea la
  derivación en el código.
- Punto crítico de emergencia: ver decisión **D3**.

### R4. Gradiente (refrigeración)
- **Propuesta:** consumo total en función de la velocidad del ventilador `v`:
  `E(v) = a·v³ + b·Q / v` (ley de afinidad de ventiladores + penalización térmica por calor `Q`
  no extraído; `Q` depende de la carga actual).
- Cada tick de SimPy: `v ← v − α·E'(v)`, con `E'(v) = 3a·v² − b·Q / v²`, acotado a `[v_min, v_max]`.
- Se grafica la trayectoria de `v` y `E` contra el óptimo analítico `v* = (bQ / 3a)^(1/4)`.

### R5. Lagrange (presupuesto eléctrico)
- **Propuesta:** rendimiento `R(E1..En) = Σ w_i · ln(1 + E_i)`, sujeto a `Σ E_i = E_max`.
- `∂L/∂E_i = w_i / (1 + E_i) − λ = 0` → `E_i = w_i / λ − 1`, `λ = Σ w_i / (E_max + n)`.
- Si algún `E_i < 0`, se fija en 0 y se re-resuelve con los clústeres restantes (condición KKT).
- `w_i` = demanda actual del clúster (la actualiza SimPy). Se grafica `λ` y las barras `E_i`.

---

## 5. Módulo 3 — Simulación y visualización

### R6. SimPy
- Llegadas Poisson (interarribo exponencial, tasa `λ`) en el gateway.
- Tiempo de servicio exponencial (tasa `μ`) por servidor; colas por servidor.
- Fallas de routers/servidores: tiempo entre fallas y de reparación exponenciales (MTBF / MTTR).
- Métricas: `Wq`, `W`, `Lq`, utilización, paquetes perdidos; comparación con M/M/1 teórico.

### R7. IA + PDF
- Gemini por HTTP (`requests`), mismo esquema que `tarea3/src/services/ai_auditor.py`, clave en `.env`.
- Al terminar (o con una tecla) se genera un PDF en `outputs/` con: parámetros, métricas,
  rutas usadas, resultados de mochila, puntos estacionarios, trayectoria del gradiente,
  reparto de Lagrange, gráficos y el análisis de la IA.
- Sin clave o sin red: el PDF se genera igual, con la sección de IA marcada como no disponible.

### R8-R10. Pygame (dashboard)
- Panel de topología con paquetes animados y nodos caídos en rojo.
- Ruta óptima resaltada; al cambiar, destello y aviso en el registro de eventos.
- Gráficos en vivo: `v(t)` y `E(t)` del gradiente; barras `E_i` y `λ(t)` de Lagrange; curva `T(c)`
  con los puntos estacionarios marcados.

---

## 6. Fases de entrega (cada una se puede commitear)

| Fase | Contenido | Verificación | Estado |
|------|-----------|--------------|--------|
| F1 | Entidades + M1 (ruta, mochila) + validadores + escenario por defecto | pytest con casos a mano | ✅ 39 tests |
| F2 | M2 (térmico, gradiente, Lagrange) | pytest: derivadas, convergencia, suma = E_max | ✅ `tests/test_no_lineal.py` |
| F3 | Motor SimPy en modo `--headless` integrando M1 y M2 | corrida reproducible con semilla | ✅ `tests/test_simulacion.py` |
| F4 | Dashboard Pygame | corrida manual + captura | ✅ `docs/dashboard.png`, `tests/test_gui.py` |
| F5 | Gemini + reporte PDF | PDF generado con y sin clave | ✅ `tests/test_reporte.py` + corrida real con `gemini-3.8-flash` |
| F6 | README, actualizar el README raíz, guía de defensa | revisión | ✅ |

### Notas de implementación (desvíos menores respecto al diseño)

- La sección `parametros` del escenario agrupa `termico`, `gradiente`, `lagrange` y `simulacion`;
  `Configuracion` construye los modelos de M2 con esos valores y el validador rechaza secciones o
  claves desconocidas.
- `Optimizador.actualizar()` recibe una `EntradaOptimizacion` (definida en `core/`) en vez del
  `EstadoSimulacion`, para que `core/` no dependa de `simulation/`.
- `MetricasColas` expone métodos por tipo de evento (`llegada`, `inicio_servicio`, `fin_servicio`,
  `perdido`, `muestrear`) en lugar de un único `registrar(evento)`.
- Parámetros de la simulación ajustados por corrida: `tasa_llegada = 4`, `escala_latencia = 0.2`
  (con 1.0 la congestión de los enlaces se retroalimentaba y los paquetes quedaban atascados),
  `mtbf = 200`.

---

## 7. Decisiones (aprobadas 2026-10-07 con la propuesta por defecto)

| ID | Pregunta | Propuesta por defecto |
|----|----------|-----------------------|
| D1 | Tamaño de la topología | 1 gateway, 3 núcleo, 4 agregación, 4 ToR, 4 clústeres (≈16 nodos) |
| D2 | ¿Aceptás las funciones de las secciones 4.R3-R5 o el profesor dio otras en clase? | Las propuestas |
| D3 | Definición del punto crítico de emergencia | Punto de inflexión de `T(c)` o umbral `T_max`, lo que ocurra primero |
| D4 | Librería PDF | `fpdf2` + gráficos con `matplotlib` |
| D5 | Entorno | `venvProyecto/` dentro de la carpeta (como `venvTarea3`), Python 3.11 (el mismo de tarea3) |
| D6 | Fecha de entrega | Desconocida — define el orden y profundidad de F4-F6 |
| D7 | ¿La entrega incluye un informe escrito aparte (como el `.docx` de tarea3)? | No, salvo que lo pidan |
