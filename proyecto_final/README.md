# Proyecto final — Simulador de Optimización para Redes de Centros de Datos

**Autores:** Roberto Siracusa (C.I. 30.195.953) e Ignacio Acena (C.I. 31.352.123)

**Universidad José Antonio Páez — Facultad de Ingeniería**
**Escuela de Ingeniería en Computación — Métodos Cuantitativos, octubre 2026**

Simulador en POO de una red de centros de datos que combina los tres módulos del enunciado
(pauta: `Proyecto Metodos Cuantitativos Octubre de 2026.pdf`):

| Módulo | Requisito | Dónde |
|--------|-----------|-------|
| M1 — Programación dinámica | R1 ruta más corta por etapas, R2 mochila 0/1 | `src/core/programacion_dinamica/` |
| M2 — Optimización no lineal | R3 modelo térmico y derivadas, R4 gradiente, R5 Lagrange | `src/core/no_lineal/` |
| M3 — Simulación y visualización | R6 SimPy, R7 Gemini + PDF, R8-R10 Pygame | `src/simulation/`, `src/services/`, `src/gui/` |

![Dashboard](docs/dashboard.png)

## Instalación

```bash
cd proyecto_final
python3.11 -m venv venvProyecto
source venvProyecto/bin/activate
pip install -r requirements.txt
```

Para el análisis de IA del PDF se usa `GEMINI_API_KEY`, que se lee de `proyecto_final/.env`, del
`.env` de la raíz del repositorio o del entorno (plantilla: `.env.example`). Sin clave o sin red el
PDF se genera igual, con la sección de IA marcada como no disponible.

## Ejecución

```bash
python main.py                          # Dashboard Pygame en vivo
python main.py --headless               # Simulación SimPy sin ventana (semilla 42, 300 u.t.)
python main.py --headless --reporte     # ... y genera el PDF en outputs/
python main.py --headless --reporte --sin-ia
python main.py --modulo m1              # Sólo módulo 1: tabla de DP, ruta y mochila
python main.py --modulo m1 --cluster C3 --fallar N1 --fallar A2
python main.py --modulo m2              # Sólo módulo 2: derivadas, gradiente y Lagrange
python main.py --modulo m2 --carga 85 --iteraciones 30
python main.py --captura docs/dashboard.png --tiempo-captura 120   # imagen del dashboard sin ventana
python main.py --escenario mi_escenario.json ...                   # otros datos (se validan, P6)
```

Teclas del dashboard: `ESPACIO` pausa, `+`/`-` velocidad, `P` genera el reporte PDF, `S` guarda una
captura en `outputs/`, `ESC` sale.

## Datos por defecto (P7)

`data/escenario_default.json`: 1 gateway, 3 routers de núcleo, 4 de agregación, 4 switches ToR y
4 clústeres de 2 servidores (capacidad 16), 14 paquetes de prueba para la mochila y la sección
`parametros` con los coeficientes de M2 y de la simulación. Cualquier escenario cargado pasa por
`Validador.validar_escenario`, que junta **todos** los errores en un solo mensaje.

## Modelos

### M1 — Programación dinámica
- **Ruta más corta (R1)**: red por etapas `gateway → núcleo → agregación → ToR`, recursión hacia
  atrás `f_k(s) = min_x { c(s,x) + f_{k+1}(x) }`. El costo del enlace es
  `c = l0 · (1 + ρ/(1−ρ))` (congestión M/M/1); un nodo caído vale infinito.
- **Mochila 0/1 (R2)**: `V[i][w] = max(V[i−1][w], V[i−1][w−w_i] + v_i)`. En la simulación, cada
  servidor la corre en cada ventana de despacho sobre su cola con su capacidad libre.

Resultado con los datos por defecto (`--modulo m1`): ruta `GW → N1 → A2 → T1` con costo 7, y la
mochila de C1 (capacidad 16) elige P2, P4, P6 y P7, con valor 30 y peso 16.

### M2 — Optimización no lineal
- **Térmico (R3)**: `T(c) = 0.0002c³ − 0.03c² + 1.26c + 30`, `T'(c) = 0.0006(c−30)(c−70)`.
  Máximo local en 30 % (46.2 °C), mínimo local en 70 % (39.8 °C), inflexión en 50 %. El punto
  crítico de emergencia es el menor entre la inflexión y la carga donde `T ≥ T_max` (50 °C → 94.56 %),
  o sea 50 %.
- **Gradiente (R4)**: `E(v) = a·v³ + b·Q/v`, paso `v ← v − α·E'(v)` por tick, acotado a
  `[v_min, v_max]`; se compara con el óptimo analítico `v* = (bQ/3a)^(1/4)` (Q = 60 → v* = 1).
- **Lagrange (R5)**: maximiza `Σ w_i ln(1+E_i)` con `Σ E_i = E_max`: `λ = Σw_i/(E_max+n)`,
  `E_i = w_i/λ − 1`, y si algún `E_i < 0` se fija en 0 y se re-resuelve (KKT).

### M3 — Simulación
- **SimPy (R6)**: llegadas Poisson (λ = 4), tránsito por la ruta óptima del momento, despacho con
  mochila, servicio exponencial y fallas/reparaciones exponenciales (MTBF 200, MTTR 15) de routers
  y servidores. Cada tick de control calcula la temperatura y da un paso de cada optimizador.
- **Pygame (R8-R10)**: topología con paquetes animados y nodos caídos en rojo, rutas óptimas por
  clúster que parpadean en amarillo al cambiar, curva `T(c)` con la carga actual, `v(t)` vs `v*(t)`,
  barras `E_i` y `λ(t)`, y el registro de eventos.
- **Reporte (R7)**: `GeneradorReportePDF` (fpdf2 + matplotlib) con parámetros, métricas, rutas,
  decisiones de mochila, análisis de M2, gráficos y el análisis de Gemini.

Corrida de referencia (`--headless`, semilla 42, 300 u.t.): 1225 paquetes generados, 1115
completados, 88 perdidos (86 por no tener ruta durante la caída de un ToR), `Wq = 1.17`, `W = 3.45`,
utilización 34 %, 353 cambios de ruta, 35 fallas y 16 emergencias térmicas.

## Arquitectura

```text
src/
├── core/                      # modelos matemáticos: no importan SimPy, Pygame ni servicios
│   ├── network_entities.py    # Nodo (ABC), Router, Servidor, Enlace, Paquete
│   ├── red.py                 # Red por etapas, Cluster
│   ├── programacion_dinamica/ # ModeloProgramacionDinamica (Template Method), RutaMasCorta, Mochila
│   └── no_lineal/             # Optimizador (ABC), ModeloTermico, GradienteEnfriamiento, AsignadorLagrange
├── simulation/                # MotorSimulacion, EstadoSimulacion, Evento, MetricasColas
├── gui/                       # AplicacionPygame, Panel (ABC) y sus 5 paneles
├── services/                  # ProveedorIA (ABC), ClienteGemini, ProveedorSinConexion, GeneradorReportePDF
└── utils/                     # Configuracion, Validador, ErrorValidacion
```

La GUI y el reporte sólo leen `EstadoSimulacion` (una foto inmutable); nunca modifican el motor.
El detalle de clases, pilares de POO y patrones está en `PLAN.md` (sección 2.1) y la guía para la
defensa en `GUIA_DEFENSA.md`.

## Pruebas

```bash
python -m pytest -q        # 71 tests
```

Cubren cada módulo por separado con casos resueltos a mano (tabla de DP, mochila, derivadas,
convergencia del gradiente, reparto de Lagrange con KKT, fórmulas M/M/1), la reproducibilidad con
semilla y la conservación de paquetes del motor, un test de humo del dashboard y el PDF con y sin IA
(sin usar la red).
