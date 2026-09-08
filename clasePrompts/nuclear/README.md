# Simulador de Reacción Nuclear en Cadena y Dinámica de Reactor (SimPy + Pygame)

Módulo computacional de simulación estocástica por eventos discretos e interactiva con renderizado top-down, desarrollado para la cátedra de **Métodos Cuantitativos** en la **Universidad José Antonio Páez**.

---

## 1. Fundamentos Científicos y Físicos

El sistema modela la física neutrónica de un núcleo de reactor nuclear térmico de investigación/potencia:

### Fisión Nuclear
Un neutrón térmico ($E \approx 0.025\text{ eV}$) colisiona con un núcleo de Uranio-235 ($^{235}\text{U}$), formándose un núcleo compuesto excitado que se fisiona en dos fragmentos más ligeros, liberando:
* $\approx 200\text{ MeV}$ de energía térmica.
* Un promedio de $\nu \approx 2.43$ neutrones prontos rápidos ($E \approx 2\text{ MeV}$).

### Moderación
Los neutrones rápidos son desacelerados mediante colisiones elásticas con el refrigerante/moderador (agua ligera $H_2O$) hasta alcanzar el equilibrio térmico, donde la sección eficaz de fisión del $^{235}\text{U}$ es órdenes de magnitud mayor.

### Barras de Control (Boro / Cadmio)
Materiales con alta sección eficaz de absorción parasitaria sin fisión ($\text{n} + ^{10}\text{B} \to ^{7}\text{Li} + \alpha$). Al insertarse en el núcleo sustraen neutrones del ciclo; al extraerse permiten un mayor crecimiento de la población neutrónica.

### Factor de Multiplicación Efectivo ($k_{\text{eff}}$)
Razón entre la cantidad de neutrones producidos por fisión y la cantidad total de neutrones absorbidos o fugados:
* **$k_{\text{eff}} < 1.0$ (Subcrítico):** La reacción en cadena decae exponencialmente hasta extinguirse.
* **$k_{\text{eff}} = 1.0$ (Crítico):** Estado auto-sostenido estacionario a potencia constante.
* **$k_{\text{eff}} > 1.0$ (Supercrítico):** Crecimiento exponencial de población neutrónica y potencia térmica.
* **$k_{\text{eff}} \ge 1 + \beta$ (Prompt Crítico):** Excursión descontrolada peligrosa sin intervención de neutrones retardados.

### Dinámica Térmica y Seguridad Intrínseca (Efecto Doppler)
La temperatura del combustible evoluciona según la primera ley de la termodinámica:
$$\frac{dT}{dt} = \frac{P_{\text{térmica}} - Q_{\text{enfriamiento}}}{C_{\text{núcleo}}}$$
Al aumentar la temperatura, el ensanchamiento Doppler de las resonancias de absorción en $^{238}\text{U}$ aumenta la captura no fisible, introduciendo reactividad negativa automática (coeficiente Doppler negativo de seguridad pasiva).

### Sistema SCRAM
Parada rápida de emergencia que deja caer por gravedad todas las barras de control al 100% de inserción para apagar inmediatamente la reacción.

---

## 2. Arquitectura de Software (POO)

El diseño desacopla completamente el modelado físico, los procesos discretos de SimPy, la presentación gráfica en Pygame y el lazo de control:

```
nuclear/
├── requirements.txt            # Dependencias (simpy, pygame, pytest)
├── main.py                     # Punto de entrada interactivo y CLI
├── README.md                   # Documentación técnica
│
├── src/
│   ├── constants.py            # Parámetros físicos, geométricos y colores
│   │
│   ├── models/
│   │   ├── particle.py         # Clases Neutron y FissionBurst
│   │   ├── fuel_element.py     # Pastillas y ensambles U-235 / U-238
│   │   ├── control_rod.py      # Barras de control (absorción y SCRAM)
│   │   ├── reactor_core.py     # Geometría, vasija y termohidráulica
│   │   └── stats.py            # Telemetría, series temporales y contabilidad
│   │
│   ├── simulation/
│   │   └── reactor_sim.py      # Motor SimPy con procesos concurrentes
│   │
│   ├── view/
│   │   ├── core_view.py        # Renderizado de vasija, Cherenkov y partículas
│   │   └── hud_view.py         # Panel de instrumentación, medidores y gráfico
│   │
│   └── engine/
│       ├── controller.py       # Sincronización reloj Pygame - reloj SimPy
│       └── input_handler.py    # Procesamiento de eventos de teclado y ventana
│
└── tests/
    ├── test_physics_models.py  # Pruebas de absorción, moderación y Doppler
    ├── test_simulation.py      # Pruebas de procesos SimPy y SCRAM
    └── test_engine.py          # Pruebas de ejecución headless y reportes
```

---

## 3. Controles Interactivos del Operador

| Tecla | Acción |
| :--- | :--- |
| **`[ESPACIO]`** | Disparar pulso de neutrones fuente ($\text{Cf-252}$) para arrancar la reacción |
| **`[FLECHA ARRIBA]`** | Extraer barras de control (+ reactividad, incrementa $k_{\text{eff}}$) |
| **`[FLECHA ABAJO]`** | Insertar barras de control (- reactividad, decrementa $k_{\text{eff}}$) |
| **`[S]`** | **SCRAM de Emergencia:** inserción gravitacional inmediata de todas las barras al 100% |
| **`[B]`** | Alternar bombas de refrigeración (circulación forzada vs convección natural) |
| **`[P]`** | Pausar / Reanudar simulación |
| **`[1, 2, 3, 4]`** | Modificar multiplicador de velocidad temporal (1x, 2x, 4x, 8x) |
| **`[R]`** | Reiniciar el núcleo con combustible fresco |
| **`[ESC]`** | Finalizar simulación y desplegar reporte cuantitativo en consola |

---

## 4. Instrucciones de Ejecución

### Requisitos Previos
Asegurarse de tener instaladas las dependencias del módulo:
```bash
pip install -r requirements.txt
```

### Modo Interactivo con Interfaz Gráfica
```bash
# Ejecución estándar (20% enriquecimiento, barras al 50%)
python main.py

# Parámetros personalizados
python main.py --enrichment 0.25 --rods 0.40 --speed 2.0
```

### Modo Headless (Benchmarks Cuantitativos y CI)
Ejecuta la simulación a máxima velocidad computacional sin abrir ventana gráfica:
```bash
python main.py --headless --duration 60 --enrichment 0.20
```

---

## 5. Pruebas Unitarias Automatizadas

El proyecto cuenta con una batería de pruebas con `pytest`:
```bash
pytest tests/ -v
```
