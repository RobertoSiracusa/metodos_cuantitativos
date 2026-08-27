# Tarea 2 — Teoría de Inventarios
### Modelos de Decisión y Optimización de Operaciones

**Universidad José Antonio Páez — Facultad de Ingeniería**  
**Escuela de Ingeniería en Computación — Métodos Cuantitativos**

---

## Descripción General

Este proyecto implementa una aplicación en Python para el análisis, cálculo y optimización de **Modelos Cuantitativos de Gestión de Inventarios**. Proporciona una arquitectura modular con diseño descendente (**Top-Down Design**), orientada a objetos (POO), desacoplada y con una interfaz gráfica moderna desarrollada en `Tkinter` (tema Slate & Blue).

El sistema permite resolver modelos determinísticos, probabilísticos y con restricciones, incluyendo la exportación de reportes técnicos detallados en formato `.txt`.

---

## Arquitectura Top-Down del Proyecto

La estructura del proyecto sigue una descomposición jerárquica clara dividida en capas de abstracción:

```text
tarea2/
│
├── main.py                             # Punto de entrada principal (ejecutable CLI / GUI)
│
├── src/                                # Código fuente modularizado (Top-Down Design)
│   ├── __init__.py
│   │
│   ├── core/                           # Capa de Lógica de Negocio y Modelos POO
│   │   ├── __init__.py
│   │   ├── eoq_model.py                # Modelo EOQ Clásico (Demanda determinística)
│   │   ├── probabilistic_model.py      # Modelo Probabilístico (Demanda variable y riesgo)
│   │   ├── discount_model.py           # Modelo de Quiebre de Precios (Descuentos por volumen)
│   │   └── constrained_model.py        # Modelo Multi-Artículo con Restricciones
│   │
│   ├── gui/                            # Capa de Presentación (Interfaz Gráfica Tkinter)
│   │   ├── __init__.py
│   │   ├── app.py                      # Ventana principal Application y navegación
│   │   ├── styles.py                   # Constantes de diseño, paleta Slate & Blue
│   │   ├── widgets.py                  # Componentes reutilizables (Card, etc.)
│   │   └── views/                      # Vistas / Paneles interactivos por modelo
│   │       ├── __init__.py
│   │       ├── eoq_view.py             # Panel interactivo de EOQ Clásico
│   │       ├── probabilistic_view.py   # Panel interactivo de Modelo Probabilístico
│   │       ├── discount_view.py        # Panel interactivo de Quiebre de Precios
│   │       └── constrained_view.py     # Panel interactivo de Multi-Artículo con Restricciones
│   │
│   └── services/                       # Capa de Servicios y Utilidades
│       ├── __init__.py
│       └── reporter.py                 # Servicio de persistencia y exportación de reportes .txt
│
├── outputs/                            # Archivos .txt generados para entrega oficial
│   ├── Ejercicio Teoria de inventario.txt        # Salida: EOQ Clásico
│   ├── Ejercicio Modelo Probabilistico.txt       # Salida: Modelo Probabilístico
│   ├── Ejercicio Quiebre de Inventario.txt       # Salida: Quiebre de Precios
│   └── Ejercicio Modelo con Restricciones.txt    # Salida: Multi-Artículo con Restricciones
│
├── tests/                              # Suite de pruebas unitarias automatizadas (pytest)
│   ├── __init__.py
│   ├── conftest.py                     # Configuración de rutas para pytest
│   ├── test_eoq_model.py               # Tests para EOQ Clásico
│   ├── test_probabilistic_model.py     # Tests para Modelo Probabilístico
│   ├── test_discount_model.py          # Tests para Quiebre de Precios
│   ├── test_constrained_model.py       # Tests para Modelo con Restricciones
│   ├── test_services.py                # Tests para el servicio de exportación
│   └── test_modelos_inventario.py      # Suite integral de verificación
│
├── Guia de Problemas de Teoria de Inventario.pdf # Guía de problemas del curso
├── Segunda tarea metodos cuantitativos agosto 2026.pdf # Pauta oficial de evaluación
└── README.md                           # Documentación técnica de la tarea
```

---

## Archivos .txt Requeridos para la Entrega

Según las pautas de la tarea ("Subir código y salida del programa en Acrópolis"), los **4 archivos `.txt`** que corresponden a las salidas oficiales son:

1. [`outputs/Ejercicio Teoria de inventario.txt`](file:///Users/robertosiracusa/Documents/metodos_cuantitativos/tarea2/outputs/Ejercicio%20Teoria%20de%20inventario.txt):
   - **Módulo**: EOQ Clásico.
   - **Caso de la guía**: Ejercicio 1 (Ramón / Equipos Acer, $D = 500$, $S = \$5000$, $H = \$25$, $C = \$3700$).
   - **Resultados clave**: $Q^* = 447.21$ unidades, $N = 1.12$ pedidos/año, $CT = \$1,861,180.34$.

2. [`outputs/Ejercicio Modelo Probabilistico.txt`](file:///Users/robertosiracusa/Documents/metodos_cuantitativos/tarea2/outputs/Ejercicio%20Modelo%20Probabilistico.txt):
   - **Módulo**: Modelo Probabilístico con Demanda Normal.
   - **Caso de la guía**: Ejercicio 7 (Distribución de desayunos, $d = 200$, $\sigma_d = 150$, $L = 4$ días, $ns = 95\%$, $S = \$20$, $C = \$10$, $i = 20\%$, $N = 250$).
   - **Resultados clave**: $Q^* = 1000$ unidades, $SS = 495$ unidades ($Z = 1.65$), $ROP = 1295$ unidades, Costo Relevante Total $= \$2990.00$.

3. [`outputs/Ejercicio Quiebre de Inventario.txt`](file:///Users/robertosiracusa/Documents/metodos_cuantitativos/tarea2/outputs/Ejercicio%20Quiebre%20de%20Inventario.txt):
   - **Módulo**: Descuentos por Cantidad / Quiebre de Precios.
   - **Caso de la guía**: Ejercicio 4 (3 tramos de precios, $D = 5000$, $K = \$49$, $i = 20\%$).
   - **Resultados clave**: Óptimo en **Tramo 2** ($Q^* = 1000$ unidades, precio $\$4.80$, Costo Total Mínimo $= \$24,725.00$). Incluye análisis de trade-off y comparativa de ahorro frente a los tramos 1 y 3.

4. [`outputs/Ejercicio Modelo con Restricciones.txt`](file:///Users/robertosiracusa/Documents/metodos_cuantitativos/tarea2/outputs/Ejercicio%20Modelo%20con%20Restricciones.txt):
   - **Módulo**: Multi-Artículo con Restricciones.
   - **Caso de la guía**: Ejercicio 8 (3 artículos A, B, C con Presupuesto $\$1000$ y Capacidad $500\text{ m}^2$).
   - **Resultados clave**: $Q_A = 44.72$, $Q_B = 50.00$, $Q_C = 54.77$, $ROP_A = 10$, $ROP_B = 18$, $ROP_C = 28$, Espacio Utilizado $= 149.49\text{ m}^2$, Costo Total $= \$458.53$, $\lambda = 0.0000$ (holgura completa).

---

## Modelos Implementados y Fundamento Matemático

### 1. Modelo EOQ Clásico (Cantidad Económica de Pedido)
Resuelve el lote económico fundamental considerando demanda determinística constante.
* **Cálculo del Lote Óptimo:**
  $$Q^* = \sqrt{\frac{2 \cdot D \cdot S}{H}}$$
* **Frecuencia y Número de Pedidos:**
  $$N = \frac{D}{Q^*}, \quad T = \frac{Q^*}{D} \text{ (años o meses)}$$
* **Desglose de Costos:** Costo anual de pedidos, costo de almacenamiento, costo de adquisición del producto y costo total ($CT$).

---

### 2. Modelo Probabilístico con Demanda Variable (Riesgo y Stock de Seguridad)
Modela la incertidumbre en la demanda durante el tiempo de entrega asumiendo una distribución normal.
* **Demanda y Variabilidad en Tiempo de Entrega:**
  $$d_L = d \cdot L, \quad \sigma_L = \sigma_d \sqrt{L}$$
* **Stock de Seguridad ($SS$) y Punto de Reorden ($ROP$):**
  $$SS = Z \cdot \sigma_L, \quad ROP = d_L + SS$$
* **Lote Económico Probabilístico:**
  $$Q^* = \sqrt{\frac{2 \cdot (d \cdot N) \cdot S}{(i\% / 100) \cdot C}}$$

---

### 3. Modelo de Quiebre de Inventario (Descuentos por Volumen)
Evalúa estructuras de precios escalonados por rangos de cantidad para determinar el lote que minimiza el costo total anual.
* **Evaluación Tramo a Tramo:** Para cada tramo $j$ con precio $P_j$ y costo $H_j = i\% \cdot P_j$:
  $$EOQ_j = \sqrt{\frac{2 \cdot D \cdot K}{H_j}}$$
* **Lógica de Factibilidad:**
  * Si $Q_{\text{min}, j} \le EOQ_j \le Q_{\text{max}, j}$: Se toma $EOQ_j$ como factible.
  * Si $EOQ_j < Q_{\text{min}, j}$: Se ajusta la cantidad al límite inferior $Q_{\text{min}, j}$.
  * Si $EOQ_j > Q_{\text{max}, j}$: El tramo se marca como no factible y se descarta.
* **Cálculo del Costo Total Anual:**
  $$CT_j = \frac{D}{Q_j} K + \frac{Q_j}{2} H_j + D \cdot P_j$$

---

### 4. Modelo Multi-Artículo con Restricciones (Capacidad y Presupuesto)
Optimiza simultáneamente las cantidades a ordenar de múltiples artículos sujetos a límites de espacio y presupuesto.
* **Restricción de Capacidad:** $\sum a_i Q_i \le A$
* **Restricción de Presupuesto:** $\sum CT_i \le B$
* **Multiplicadores de Lagrange (Exacto):**
  $$Q_i^* = \sqrt{\frac{2 D_i S_i}{H_i + 2 \lambda a_i}}$$
* **Aproximación de Lagrange (Fórmula Clásica de Hamdy Taha):**
  $$\lambda \approx \frac{n^2 \bar{a} \overline{C_p D}}{A^2} - \frac{\bar{C}_m}{2\bar{a}}$$
* **Punto de Reorden ($ROP$):**
  $$ROP_i = d_i \cdot L_i$$

---

## Requisitos e Instrucciones de Uso

### Requisitos
* **Python 3.8** o superior instalado en el sistema.
* Módulos estándar de Python requeridos: `tkinter`, `math`, `statistics`.

### Cómo Ejecutar la Aplicación

1. Abrir una terminal en el directorio `tarea2`:
   ```bash
   cd tarea2
   ```

2. Ejecutar la aplicación principal:
   ```bash
   python main.py
   ```

### Ejecución de Pruebas Unitarias

Para verificar todos los cálculos de manera automatizada:
```bash
pytest tests/ -v
```
