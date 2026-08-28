# Parcial II — Teoría de Inventarios
### Modelos de Decisión y Optimización de Operaciones

**Universidad José Antonio Páez — Facultad de Ingeniería**  
**Escuela de Ingeniería en Computación — Métodos Cuantitativos**  
**Profesor:** Argenis  
**Período:** Junio 2025 / Agosto 2026

---

## Origen del Código — Reutilización y Adaptación de la Tarea 2

El código fuente de la calculadora modular implementada en este directorio (`src/` y `main.py`) fue **tomado principalmente y adaptado de la Tarea 2 (Teoría de Inventarios)** de la materia. Se reutilizó la arquitectura modular descendente (*Top-Down*), los modelos matemáticos orientados a objetos (POO), la interfaz gráfica en Tkinter y los motores de cálculo (EOQ clásico, quiebre de precios con descuentos por volumen y modelos multi-artículo con restricciones de capacidad y presupuesto mediante multiplicadores de Lagrange) como base para resolver y verificar los ejercicios del Parcial II.

---

## Descripción General

Este directorio contiene la solución analítica, computacional y documental para los **tres ejercicios del Parcial II de Métodos Cuantitativos (Teoría de Inventarios)**:
1. **Ejercicio 1:** Modelo EOQ Clásico con costo de almacenamiento porcentual ($i\%$), cálculo de $ROP$, costo de inventario y frecuencia anual.
2. **Ejercicio 2:** Modelo de Descuentos por Cantidad / Quiebre de Precios (4 tramos escalonados), análisis de factibilidad de lotes, trade-off de costos y ahorro neto.
3. **Ejercicio 3:** Modelo Multi-Artículo con Restricciones de Capacidad y Presupuesto, evaluación de multiplicadores de Lagrange ($\lambda$), puntos de reorden y análisis de holguras operativas.

---

## Estructura del Directorio `parcial2/`

```text
parcial2/
│
├── main.py                                           # Punto de entrada (Soporta GUI interactiva y CLI por ejercicio)
├── Parcial II. Teoría de Inventarios  308C1 junio 2025.pdf  # Enunciado oficial del parcial
│
├── respuestaPregunta1.md                             # Desarrollo matemático formato examen — Ejercicio 1 (EOQ)
├── respuestaPregunta2.md                             # Desarrollo matemático formato examen — Ejercicio 2 (Quiebre)
├── respuestaPregunta3.md                             # Desarrollo matemático formato examen — Ejercicio 3 (Restricciones)
│
├── src/                                              # Arquitectura Top-Down modular (basada en Tarea 2)
│   ├── __init__.py
│   ├── core/                                         # Capa de Lógica de Negocio y Modelos Matemáticos
│   │   ├── __init__.py
│   │   ├── eoq_model.py                              # Modelo EOQ Clásico (Ejercicio 1)
│   │   ├── discount_model.py                         # Modelo de Descuentos / Quiebre de Precios (Ejercicio 2)
│   │   ├── constrained_model.py                      # Modelo Multi-Artículo con Restricciones (Ejercicio 3)
│   │   └── probabilistic_model.py                    # Modelo Probabilístico con Stock de Seguridad
│   │
│   ├── gui/                                          # Capa de Presentación (Tkinter Slate & Blue)
│   │   ├── __init__.py
│   │   ├── app.py                                    # Ventana principal y ruteador
│   │   ├── styles.py                                 # Constantes de diseño
│   │   ├── widgets.py                                # Componentes UI reutilizables
│   │   └── views/                                    # Vistas por modelo de inventario
│   │       ├── eoq_view.py
│   │       ├── discount_view.py
│   │       ├── constrained_view.py
│   │       └── probabilistic_view.py
│   │
│   └── services/                                     # Servicios de exportación y formateo
│       ├── __init__.py
│       └── reporter.py                               # Generador y persistencia de reportes .txt
│
└── outputs/                                          # Salidas del programa en formato .txt para entrega
    ├── Ejercicio 1 - Modelo EOQ Clasico.txt          # Salida oficial Ejercicio 1
    ├── Ejercicio 2 - Quiebre de Precios Descuentos.txt # Salida oficial Ejercicio 2
    └── Ejercicio 3 - Modelo con Restricciones.txt    # Salida oficial Ejercicio 3
```

---

## Instrucciones de Ejecución

### 1. Resolución Automática de los Ejercicios (CLI + Exportación .txt)
Para resolver todos los ejercicios del examen de una vez y generar los archivos `.txt` en `outputs/`:
```bash
python3 main.py --todos
```

O por ejercicio individual:
```bash
python3 main.py --ejercicio1
python3 main.py --ejercicio2
python3 main.py --ejercicio3
```

### 2. Ejecutar la Interfaz Gráfica (GUI)
Para abrir la aplicación gráfica interactiva con todos los módulos:
```bash
python3 main.py
```

---

## Archivos de Entrega del Parcial

1. **Código Fuente Python:** Todo el código modular en `parcial2/src/` y `parcial2/main.py`.
2. **Salidas del Programa (`.txt` en `outputs/`):**
   - [`outputs/Ejercicio 1 - Modelo EOQ Clasico.txt`](outputs/Ejercicio%201%20-%20Modelo%20EOQ%20Clasico.txt)
   - [`outputs/Ejercicio 2 - Quiebre de Precios Descuentos.txt`](outputs/Ejercicio%202%20-%20Quiebre%20de%20Precios%20Descuentos.txt)
   - [`outputs/Ejercicio 3 - Modelo con Restricciones.txt`](outputs/Ejercicio%203%20-%20Modelo%20con%20Restricciones.txt)
3. **Respuestas Escritas Formato Examen (`.md`):**
   - [`respuestaPregunta1.md`](respuestaPregunta1.md): Desarrollo paso a paso y respuestas a los 4 literales del Ejercicio 1.
   - [`respuestaPregunta2.md`](respuestaPregunta2.md): Evaluación tramo por tramo, factibilidad, análisis de trade-off y conclusión del Ejercicio 2.
   - [`respuestaPregunta3.md`](respuestaPregunta3.md): Formulación KKT, verificación de capacidad y presupuesto, $ROP$ y conclusión del Ejercicio 3.
