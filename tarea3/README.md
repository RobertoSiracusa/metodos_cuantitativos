# Tarea 3 — Simulador Dinamico de Redes de Computadoras
### Modelos Cuantitativos, Teoria de Colas e Investigacion de Operaciones

**Universidad Jose Antonio Paez — Facultad de Ingenieria**  
**Escuela de Ingenieria en Computacion — Metodos Cuantitativos y Simulacion**

---

## Descripcion General

Este proyecto implementa un simulador visual, estocastico e interactivo de una red de computadoras en tiempo real desarrollado en Python mediante el motor de eventos discretos **SimPy**, la biblioteca grafica **Pygame** a 60 FPS, modelos de optimizacion combinatoria (**SciPy / Algoritmo Hungaro**), integracion HTTP con APIs de Inteligencia Artificial (**Google Gemini AI / OpenAI**) y generacion automatizada del informe tecnico formal en Word (**python-docx**).

Sigue los mismos estandares de ingenieria de software, arquitectura modular descendente (**Top-Down Design**), orientacion a objetos (POO) y desacoplamiento estructural aplicados en las Tareas 1 y 2 del curso.

---

## Arquitectura Top-Down del Proyecto

La estructura del proyecto organiza la logica en capas limpias e independientes:

```text
tarea3/
│
├── main.py                             # Punto de entrada principal (GUI interactiva y CLI Headless)
├── requirements.txt                    # Dependencias formales del proyecto
├── .env.example                        # Plantilla de configuracion para credenciales de API
├── .gitignore                          # Exclusiones de control de versiones
├── README.md                           # Documentacion tecnica del sistema
│
├── src/                                # Codigo fuente modularizado (Top-Down Design)
│   ├── __init__.py
│   │
│   ├── core/                           # Capa de Dominio Cuantitativo y Modelos POO
│   │   ├── __init__.py
│   │   ├── queuing_model.py            # Teoria de Colas (M/M/1/K analitico y empirico, Little)
│   │   ├── inventory_model.py          # Control de Inventario en Buffers (politica (s, Q), costos)
│   │   ├── hungarian_model.py          # Algoritmo Hungaro (SciPy y Kuhn-Munkres nativo O(n^3))
│   │   └── network_entities.py         # Entidades puras: Packet, NetworkLink, RouterNode
│   │
│   ├── services/                       # Capa de Servicios y Orquestacion
│   │   ├── __init__.py
│   │   ├── simulation_service.py       # Motor estocastico SimPy (Poisson, servidores exponenciales)
│   │   ├── reporter.py                 # Exportador de reportes planos .txt segun pauta oficial
│   │   ├── ai_auditor.py               # Cliente HTTP (Gemini/OpenAI) y Motor Experto Local
│   │   └── docx_service.py             # Compilador del Informe Tecnico institucional en Word (.docx)
│   │
│   ├── gui/                            # Capa de Presentacion (Pygame a 60 FPS)
│   │   ├── __init__.py
│   │   ├── app.py                      # Ventana principal SimulatorApp y ciclo de eventos
│   │   ├── styles.py                   # Paleta Slate 900, colores condicionales y tipografia
│   │   ├── widgets.py                  # Botones interactivos, tarjetas HUD y notificaciones
│   │   ├── renderer.py                 # Renderizado de nodos, enlaces dinamicos y paquetes animados
│   │   └── dashboard.py                # Panel lateral de control y telemetria HUD
│   │
│   └── utils/                          # Capa de Utilidades y Configuracion
│       ├── __init__.py
│       ├── config.py                   # Carga de entorno, constantes globales y rutas
│       └── validators.py               # Validaciones de consistencia cuantitativa
│
├── outputs/                            # Entregables oficiales generados
│   ├── reporte_simulacion.txt          # [Entregable 2] Reporte con metricas y auditoria
│   ├── Informe_Tecnico_Simulador_Redes.docx # [Entregable 3] Informe formal UJAP
│   └── captura_simulacion.png          # Captura de la interfaz interactiva para el informe
│
└── tests/                              # Suite de pruebas automatizadas (pytest)
    ├── __init__.py
    ├── conftest.py                     # Configuracion de rutas para el harness de pruebas
    ├── test_queuing_model.py           # Pruebas analiticas de colas M/M/1/K y Ley de Little
    ├── test_inventory_model.py         # Pruebas de politica (s, Q) y costos de inventario
    ├── test_hungarian_model.py         # Pruebas de asignacion optima (SciPy vs Nativo)
    ├── test_simulation_engine.py       # Pruebas de corrida estocastica, fallas y desborde
    └── test_services.py                # Pruebas de exportacion TXT, DOCX y auditoria
```

---

## Fundamentacion Matematica y Modelos Cuantitativos

### 1. Teoria de Colas (Lineas de Espera M/M/1/K)
- **Generacion de Trafico**: Proceso de Poisson con tasa media `lambda` paquetes/segundo. El tiempo entre llegadas consecutivas sigue una distribucion exponencial $t \sim \text{Exp}(\lambda)$.
- **Atencion en Routers**: Servidores con disciplina FIFO y tiempos de servicio exponenciales con tasa media `mu` paquetes/segundo ($t_s \sim \text{Exp}(\mu)$).
- **Metricas Computadas**:
  - $L$: Numero promedio de paquetes en el sistema (en buffer + en servidor).
  - $L_q$: Numero promedio de paquetes esperando en cola de buffer.
  - $W$: Tiempo medio de estancia total en la red.
  - $W_q$: Tiempo medio de espera en cola antes de ser atendido.
  - **Ley de Little Verificada**: $L = \lambda_{\text{efectivo}} \cdot W$ y $L_q = \lambda_{\text{efectivo}} \cdot W_q$.
  - **Factor de Utilizacion**: $\rho = \frac{\lambda}{c \cdot \mu}$.

### 2. Gestion de Inventario en Buffers (Politica (s, Q))
- **Capacidad Maxima ($S$)**: Limite de paquetes almacenables por router.
- **Politica de Reabastecimiento / Control de Flujo ($s, Q$)**: Cuando el nivel de ocupacion del buffer desciende por debajo del umbral minimo $s$, el router genera una senal de control de flujo para autorizar un nuevo lote de $Q$ paquetes o liberar el canal de entrada.
- **Desbordamiento de Buffer (Buffer Overflow)**: Si arriba un paquete y el buffer tiene $q \ge S$, ocurre un descarte forzoso (Packet Loss).
- **Costos Cuantitativos**:
  - Costo de Mantener (Holding Cost en RAM): $C_h = \$0.05$ por paquete por segundo almacenado.
  - Costo de Ruptura / Penalizacion (Shortage Cost): $C_s = \$10.00$ por paquete descartado.
  - Costo Global: $C_{\text{global}} = C_h \cdot \int_0^T q(t) \, dt + C_s \cdot (\text{Paquetes Perdidos})$.

### 3. Modelo de Asignacion Optima (Algoritmo Hungaro)
En intervalos discretos $\Delta t = 1.0\text{ s}$, el enrutador evalua la matriz de costos dinamicamente:
$$C_{ij} = \text{Latencia Actual del Enlace}_{ij} + \alpha \cdot \left(\frac{\text{Cola Actual del Nodo}_j}{S_j}\right)$$
donde $\alpha = 40.0\text{ ms}$ pondera la saturacion del buffer. Ante una falla o desconexion de enlace, el costo se fija en $C_{ij} = 10^6$ (penalizacion prohibitiva), obligando al algoritmo a seleccionar una ruta alternativa disponible.

El sistema implementa resolucion mediante SciPy (`linear_sum_assignment`) y cuenta con una implementacion nativa propia de **Kuhn-Munkres $O(n^3)$ con ajuste de potenciales duales**, garantizando operacion 100% autonoma.

---

## Codigo de Color Condicional de Routers (Pauta Oficial)

- **Verde**: Saturacion de buffer $< 50\%$.
- **Amarillo**: Saturacion de buffer entre $50\%$ y $80\%$.
- **Rojo**: Saturacion de buffer $> 80\%$ (con halo de advertencia reactivo).

---

## Instalacion y Requisitos

### Requisitos Previos:
- Python 3.10 o superior (compatible con Linux, macOS y Windows).

### Pasos de Instalacion:
1. Clonar o acceder a la carpeta del proyecto:
   ```bash
   cd tarea3
   ```
2. Instalar dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```
3. (Opcional) Configurar clave de API de Google Gemini en `.env`:
   ```bash
   cp .env.example .env
   ```
   Edita `.env` (puede ubicarse en `tarea3/.env` o en la raiz del repositorio `metodos_cuantitativos/.env`):
   ```env
   GEMINI_API_KEY=AIzaSy...tu_clave_de_gemini_aqui
   ```
   *Nota: El sistema detecta automaticamente la clave y consulta el modelo oficial `gemini-flash-latest`. Si no se configura una clave, el Motor Experto Cuantitativo Local de Respaldo evalua automaticamente las metricas sin fallos.*

---

## Guia de Uso

### Modo Interactivo Visual (Pygame a 60 FPS):
Inicia la aplicacion grafica completa con animacion en tiempo real de nodos, enlaces, paquetes estocasticos y panel de telemetria HUD:
```bash
python main.py
```

### Modo por Lotes / Headless (Consola):
Ejecuta la simulacion estocastica por consola y genera automaticamente el reporte plano `.txt` y el informe formal `.docx`:
```bash
python main.py --headless --duration 60 --lambda 15.0 --mu 18.0 --capacidad-s 50
```

---

## Tabla de Controles (Teclado y Raton)

| Accion | Atajo de Teclado | Control por Raton |
| :--- | :---: | :--- |
| **Pausar / Reanudar** | `ESPACIO` o `P` | Boton `Pausa` en Dashboard |
| **Ajustar Tasa Llegada ($\lambda$)** | `FLECHA ARRIBA` / `ABAJO` | Botones `λ +` / `λ -` en Dashboard |
| **Ajustar Tasa Servicio ($\mu$)** | `FLECHA DERECHA` / `IZQ` | Botones `μ +` / `μ -` en Dashboard |
| **Simular Caida de Enlaces** | `F1`, `F2`, `F3` | Clic directo sobre la linea del enlace |
| **Selector de Velocidad** | `1`, `2`, `3`, `4`, `5` | Botones `0.25x`, `0.5x`, `1.0x`, `2.0x`, `4.0x` |
| **Pantalla Expandida** | `F11` | Boton `Expandir` en Dashboard |
| **Capturar Pantalla** | `F12` | Guarda automaticamente `outputs/captura_simulacion.png` |
| **Exportar y Auditar con IA** | `E` | Boton `Exportar` en Dashboard |
| **Reiniciar Simulacion** | `R` | Boton `Reiniciar` en Dashboard |
| **Finalizar y Guardar** | `ESC` | Cierre de ventana o tecla Escape |

---

## Entregables Oficiales Generados

1. **Codigo Fuente (`src/` y `main.py`)**: Implementacion completa modular, tipada y comentada.
2. **Archivo de Salida (`outputs/reporte_simulacion.txt`)**: Muestra con la estructura exacta exigida en el PDF y el analisis automatizado recibido de la API.
3. **Informe Tecnico (`outputs/Informe_Tecnico_Simulador_Redes.docx`)**: Documento Word institucional con marco teorico, tabla formal de metricas, captura de pantalla de la interfaz y recomendaciones de ingenieria.

---

## Suite de Pruebas Automatizadas

Para correr las pruebas unitarias:
```bash
pytest tests/ -v
```

Casos cubiertos:
- Calculo analitico de colas M/M/1/K y verificacion de la Ley de Little.
- Contabilidad de costos de almacenamiento y penalizaciones por desborde.
- Matriz de costos del Algoritmo Hungaro y equivalencia exacta entre SciPy y Kuhn-Munkres nativo.
- Simulacion estocastica de 120 segundos, conmutacion de fallas y desbordamiento bajo estres.
- Exportacion de reportes TXT, auditoria cuantitativa y generacion de informe DOCX.
