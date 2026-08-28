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
