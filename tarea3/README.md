# Simulador Dinámico de Redes de Computadoras

### Universidad José Antonio Páez — Facultad de Ingeniería

### Escuela de Ingeniería en Computación | Métodos Cuantitativos y Simulación

Simulador estocástico, visual e interactivo de una red de computadoras desarrollado en **Python** integrando el motor de eventos discretos **SimPy**, la biblioteca gráfica **Pygame** a 60 FPS, modelos de optimización combinatoria (**SciPy / Algoritmo Húngaro**), auditoría automatizada mediante **Google Gemini AI** y compilación del informe técnico en Word (**python-docx**).

---

## IMPORTANTE: Configuración de la API Key de Google Gemini

> [!IMPORTANT]
> **ATENCIÓN AL EVALUADOR / USUARIO:**
> Para realizar peticiones HTTP en vivo a la API de **Google Gemini**, **es indispensable ingresar una API Key propia**, ya que la clave personal del creador del código se encuentra protegida por motivos de seguridad y confidencialidad.

### ¿Cómo obtener y configurar tu propia API Key de Google Gemini?

1. **Obtener la clave gratuita en Google AI Studio:**
   - Ingresa a [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) con tu cuenta de Google.
   - Haz clic en **"Create API key"** (Crear clave de API).
   - Copia la clave generada (suele comenzar por `AIzaSy...` y tener 39 caracteres).

2. **Configurarla en el proyecto (Cualquiera de los 2 métodos siguientes):**
   - **Método A: Mediante archivo `.env` (Recomendado):**
     Abre o edita el archivo `.env` en la raíz del proyecto y coloca tu clave:

     ```env
     GEMINI_API_KEY=AIzaSyTuClaveOficialDeGoogleStudioAqui
     ```

   - **Método B: Variable de entorno del sistema:**
     - En **PowerShell**:
       ```powershell
       $env:GEMINI_API_KEY="AIzaSyTuClaveOficialDeGoogleStudioAqui"
       ```
     - En **CMD (Símbolo del sistema)**:
       ```cmd
       set GEMINI_API_KEY=AIzaSyTuClaveOficialDeGoogleStudioAqui
       ```

### Motor de Contingencia (Modo de Respaldo Local)

Si no dispones de una clave de API al momento de la prueba o si no cuentas con conexión a Internet:

- El software **no se detendrá ni arrojará errores**.
- El módulo [gemini_client.py](file:///c:/Users/usuario/Desktop/Metodos-Cuantitativos-Simulaciones/gemini_client.py) activará automáticamente el **Motor Experto Cuantitativo Local de Respaldo**.
- Este motor evaluará matemáticamente las métricas de la simulación ($L, L_q, W, W_q$, tasa de pérdida y costos) y generará el diagnóstico y las 3 recomendaciones de optimización requeridas por el enunciado tanto en consola como en [reporte_simulacion.txt](file:///c:/Users/usuario/Desktop/Metodos-Cuantitativos-Simulaciones/reporte_simulacion.txt).

---

## Tabla de Contenidos

1. [Descripción General de la Red](#-descripción-general-de-la-red)
2. [Fundamentación Matemática y Modelado Cuantitativo](#-fundamentación-matemática-y-modelado-cuantitativo)
   - [A. Teoría de Colas (Líneas de Espera M/M/1/K)](#a-teoría-de-colas-líneas-de-espera-mm1k)
   - [B. Gestión de Inventario en Buffers (s, Q)](#b-gestión-de-inventario-en-buffers-s-q)
   - [C. Asignación Óptima y Enrutamiento (Algoritmo Húngaro)](#c-asignación-óptima-y-enrutamiento-algoritmo-húngaro)
3. [Estructura del Repositorio y Entregables](#-estructura-del-repositorio-y-entregables)
4. [Instalación y Requisitos](#-instalación-y-requisitos)
5. [Guía de Uso y Controles Interactivos](#-guía-de-uso-y-controles-interactivos)
6. [Generación de Entregables Oficiales](#-generación-de-entregables-oficiales)
7. [Pruebas Automatizadas Unitarias](#-pruebas-automatizadas-unitarias)

---

## Descripción General de la Red

El sistema modela una infraestructura de red de computadoras estocástica en tiempo real con la siguiente topología:

- **Fuentes Emisoras ($S_1, S_2, S_3$)**:
  - $S_1$: Servidor Web de alta concurrencia.
  - $S_2$: Clúster Transaccional de Base de Datos.
  - $S_3$: Plataforma CDN / Multimedia Streaming.
- **Capa de Conmutación y Routers Core ($R_1, R_2, R_3, R_4$)**:
  - Cuatro nodos intermedios que disponen de procesadores de modulación (servidores SimPy) y buffers de almacenamiento temporal (capacidad $S$ y umbral $s$).
- **Gateways WAN de Salida ($D_1, D_2$)**:
  - Destinos finales de los paquetes de datos.
- **Enlaces de Comunicación Dinámicos**:
  - Canales con retardo de propagación estocástico (latencia base + fluctuación gaussiana / jitter) y soporte para simular fallas imprevistas.

```
       [S1: Web] ---------\
                           +----> [R1: Router Core 1] -----\
       [S2: BaseDatos] --->+----> [R2: Router Core 2] ----->+----> [D1: Gateway WAN A]
                           +----> [R3: Router Core 3] ----->+----> [D2: Gateway WAN B]
       [S3: CDN] ---------/-----> [R4: Router Core 4] -----/
                                (Buffers S, s, Q)
```

---

## Fundamentación Matemática y Modelado Cuantitativo

### A. Teoría de Colas (Líneas de Espera $M/M/1/K$)

Cada router opera como una estación de servicio exponencial con buffer finito:

- **Llegadas de Tráfico**: Proceso de Poisson con tasa media $\lambda$ (paquetes/segundo). La probabilidad de $k$ arribos en un intervalo $t$ es:
  $$P(N(t) = k) = \frac{(\lambda t)^k e^{-\lambda t}}{k!}$$
  El tiempo entre arribos consecutivos sigue una distribución exponencial: $t_{\text{arribo}} \sim \text{Exp}(\lambda)$.
- **Tiempos de Servicio**: Distribución exponencial con tasa media $\mu$ (paquetes/segundo): $t_{\text{servicio}} \sim \text{Exp}(\mu)$.
- **Métricas Computadas en Tiempo Real**:
  - $L$: Número promedio de paquetes en el sistema (en buffer + en transmisión):
    $$L = \frac{1}{T} \int_{0}^{T} N(t) \, dt$$
  - $L_q$: Número promedio de paquetes esperando en cola de buffer:
    $$L_q = \frac{1}{T} \int_{0}^{T} q(t) \, dt$$
  - $W$: Tiempo medio de permanencia en la red (desde creación hasta entrega):
    $$W = \frac{1}{K} \sum_{i=1}^{K} (t_{\text{entrega}} - t_{\text{creación}})_i$$
  - $W_q$: Tiempo medio de retardo en cola antes de ser atendido:
    $$W_q = \frac{1}{K} \sum_{i=1}^{K} (t_{\text{inicio\_servicio}} - t_{\text{ingreso\_buffer}})_i$$
  - **Ley de Little Verificada**: $L = \lambda_{\text{efectivo}} \cdot W$ y $L_q = \lambda_{\text{efectivo}} \cdot W_q$.
  - **Factor de Utilización ($\rho$)**: $\rho = \frac{\lambda}{c \cdot \mu}$, indicando la fracción de tiempo que los servidores están ocupados.

---

### B. Gestión de Inventario en Buffers ($(s, Q)$)

Los buffers de memoria RAM se modelan bajo la teoría clásica de control de inventarios:

- **Capacidad Máxima ($S$)**: Límite de paquetes almacenables en la cola del router.
- **Política de Control de Flujo $(s, Q)$**: Cuando la cantidad de paquetes en buffer disminuye por debajo del umbral mínimo $s$, el router emite una señal de control de flujo (análoga al crédito de ventana TCP) para liberar un lote $Q$ de paquetes o desbloquear el canal de entrada.
- **Desbordamiento de Buffer (Buffer Overflow / Ruptura de Stock)**: Si un paquete arriba y el buffer tiene $q \ge S$, el paquete es descartado (Packet Loss).
- **Modelo Económico y Costos del Sistema**:
  - **Costo de Mantener en Memoria ($C_h$)**: Asociado al tiempo de ocupación de RAM y latencia ($C_h = \$0.05$ / paquete / segundo):
    $$C_{\text{almacenamiento}} = C_h \cdot \int_{0}^{T} q(t) \, dt$$
  - **Costo de Ruptura / Penalización ($C_s$)**: Penalización financiera por cada paquete perdido ($C_s = \$10.00$ / descarte):
    $$C_{\text{penalización}} = C_s \cdot (\text{Total Paquetes Descartados})$$
  - **Costo Global del Sistema**:
    $$C_{\text{global}} = C_{\text{almacenamiento}} + C_{\text{penalización}}$$

---

### C. Asignación Óptima y Enrutamiento (Algoritmo Húngaro)

Cada intervalo discreto $\Delta t = 1.0\text{ s}$, el sistema evalúa los flujos de paquetes pendientes y los enlaces de transmisión disponibles.

- **Matriz de Costos Dinámicos ($C_{ij}$)**:
  $$C_{ij} = \text{Latencia Actual del Enlace}_{ij} + \alpha \cdot \left(\frac{\text{Cola Actual del Nodo}_j}{S_j}\right)$$
  donde:
  - $\text{Latencia Actual}_{ij}$: Retardo de propagación en milisegundos con fluctuación (jitter).
  - $\frac{\text{Cola Actual}_j}{S_j} \in [0.0, 1.0]$: Saturación actual del buffer de destino.
  - $\alpha = 40.0\text{ ms}$: Factor de ponderación que penaliza el envío de paquetes a routers congestionados.
  - **Penalización de Enlace Caído**: Si un enlace sufre una falla imprevista o es inhabilitado, su costo se establece en $C_{ij} = 10^6$, forzando al algoritmo a reasignar el tráfico por rutas operativas alternas.
- **Resolución**: Implementado mediante `scipy.optimize.linear_sum_assignment` con una implementación propia del algoritmo de Kuhn-Munkres para entornos nativos.

---

## Estructura del Repositorio y Entregables

```
Metodos-Cuantitativos-Simulaciones/
│
├── main.py                                  # [ENTREGABLE 1] Aplicación principal (Pygame + SimPy)
├── red_simulacion.py                        # Motor estocástico, colas M/M/1/K y buffer (s, Q)
├── hungarian_router.py                      # Algoritmo Húngaro (SciPy y Kuhn-Munkres nativo)
├── gui_network.py                           # Interfaz gráfica Slate 900 y Dashboard HUD a 60 FPS
├── gemini_client.py                         # Cliente HTTP Google Gemini + Motor Cuantitativo Local
├── reporte_simulacion.txt                   # [ENTREGABLE 2] Reporte estructurado con métricas y AI
├── Informe_Tecnico_Simulador_Redes.docx     # [ENTREGABLE 3] Informe formal UJAP en Word
├── generar_informe_docx.py                  # Script para compilar/recompilar el informe Word
├── test_simulacion.py                       # Suite de pruebas unitarias automatizadas (5/5 OK)
├── captura_simulacion.png                   # Captura real de la interfaz gráfica del simulador
├── requirements.txt                         # Lista de dependencias del proyecto
└── .env                                     # Archivo para configurar tu GEMINI_API_KEY
```

---

## Instalación y Requisitos

### Requisitos Previos:

- Python 3.10 o superior (probado en Python 3.13 en Windows 64-bit).

### Pasos de Instalación:

1. **Abrir la terminal en la carpeta del proyecto**:

   ```bash
   cd c:\Users\usuario\Desktop\Metodos-Cuantitativos-Simulaciones
   ```

2. **Instalar dependencias necesarias**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar tu API Key de Gemini**:
   Edita el archivo `.env` y coloca tu clave:
   ```env
   GEMINI_API_KEY=tu_clave_de_google_ai_studio
   ```

---

## Guía de Uso y Controles Interactivos

Para iniciar el simulador interactivo ejecuta:

```bash
python main.py
```

### Tabla de Controles por Teclado y Ratón:

| Control                              |           Atajo           | Función                                                                          |
| :----------------------------------- | :-----------------------: | :------------------------------------------------------------------------------- |
| **Pantalla Expandida**               |       `F11` o Botón       | Alterna entre Pantalla Expandida (maximizada por defecto) y Ventana Reducida     |
| **Pausar / Reanudar**                |      `ESPACIO` o `P`      | Detiene temporalmente el avance del reloj de SimPy                               |
| **Ajustar Velocidad**                |  `1`, `2`, `3`, `4`, `5`  | Selector directo: `0.25x` (Lento), `0.5x` (Didáctico), `1x` (Normal), `2x`, `4x` |
| **Paso de Velocidad**                |   `[` o `-` / `]` o `+`   | Disminuye o aumenta la velocidad de la simulación gradualmente                   |
| **Ajustar Tasa Llegada ($\lambda$)** | `FLECHA ARRIBA` / `ABAJO` | Aumenta o disminuye el volumen de tráfico entrante                               |
| **Ajustar Tasa Servicio ($\mu$)**    | `FLECHA DERECHA` / `IZQ`  | Acelera o ralentiza la capacidad de modulación de routers                        |
| **Simular Caída de Enlaces**         |  `F1`, `F2`, `F3` o Clic  | Desconecta/reconecta enlaces ($S_1$-$R_1$, etc.) para observar re-enrutamiento   |
| **Exportar y Auditar con Gemini**    |            `E`            | Genera `reporte_simulacion.txt` y consulta la API de IA                          |
| **Capturar Pantalla**                |           `F12`           | Guarda `captura_simulacion.png` para el informe técnico                          |
| **Reiniciar Simulación**             |            `R`            | Reinicia todos los acumuladores y buffers a cero                                 |
| **Salir de la Aplicación**           |           `ESC`           | Exporta el estado final a TXT y cierra la ventana                                |
| **Botones HUD de Velocidad**         |   Clic en `0.25x`..`4x`   | Permite alternar la velocidad directamente desde el panel                        |

### Desglose Comprensible de Estadísticas (Dashboard HUD):

- **1. Tráfico y Estabilidad**: Monitoreo de $\lambda$, $\mu$ e intervalo de arribos en milisegundos, junto con la Utilización de CPU ($\rho = \lambda / c\mu$) y su insignia de estabilidad (`[🟢 ESTABLE]`).
- **2. Teoría de Colas (Significado Físico)**:
  - **Espera en Cola ($W_q$)**: Demora promedio antes de ser atendido en milisegundos (`ms`) y segundos con insignia de diagnóstico (`[⚡ ÓPTIMO]`).
  - **Estancia en Red ($W$)**: Tiempo total invertido desde el origen hasta el Gateway WAN.
  - **En Sistema ($L$)**: Promedio de paquetes activos simultáneamente en la red.
  - **En Cola ($L_q$)**: Promedio de paquetes varados en colas de espera.
  - **Pérdida por Desborde**: Cantidad y % de paquetes descartados ante saturación.
- **3. Inventario y Buffers ($(s, Q)$)**: Capacidad $S$, umbral de reabastecimiento $s$, lote $Q$, y monitores individuales de ocupación en routers $R_1..R_4$ con barras dinámicas y porcentajes.
- **4. Costos Cuantitativos**: Almacenamiento RAM ($C_h = \$0.05/\text{paq}\cdot\text{s}$), Penalización por Ruptura ($C_s = \$10.00/\text{descarte}$) y Costo Global con insignia de eficiencia financiera.
- **5. Algoritmo Húngaro**: Mapeo óptimo vigente de flujos hacia enlaces y costo de latencia en milisegundos.

### Código de Color Condicional de Routers (Exigencia del Enunciado):

- 🟢 **Verde**: Saturación de buffer $< 50\%$.
- 🟡 **Amarillo**: Saturación de buffer entre $50\%$ y $80\%$.
- 🔴 **Rojo**: Saturación de buffer $> 80\%$ (con halo de advertencia intermitente).

---

## Generación de Entregables Oficiales

### 1. Código Fuente (`.py`)

Todo el código está completamente estructurado bajo el paradigma de **Programación Orientada a Objetos (POO)**, con tipado estático (`typing`), comentarios explicativos y manejo riguroso de excepciones.

### 2. Archivo de Salida (`reporte_simulacion.txt`)

Se genera automáticamente al presionar la tecla **`E`** o al cerrar el simulador. Cumple exactamente con la estructura de texto plano solicitada en el enunciado:

```text
==================================================
REPORTE DE SIMULACIÓN DE RED
==================================================
Tiempo Total de Simulación: 120.0 s
Tasa de Llegada (lambda): 15.0 paquetes/s
Tasa de Servicio (mu): 18.0 paquetes/s
Capacidad de Buffer (S): 50 paquetes
Umbral Reabastecimiento (s): 10 paquetes

METRICAS OBTENIDAS:
- Paquetes Procesados: 1796
- Paquetes Perdidos (Overflow): 0
- Tasa de Pérdida: 0.00%
- Tiempo Medio en Cola (Wq): 0.0435 s
- Promedio Paquetes en Sistema (L): 0.90
- Costo Total de Almacenamiento: $3.91
- Costo Total de Penalización (Ruptura): $0.00
- Costo Global del Sistema: $3.91
==================================================

==================================================
ANÁLISIS AUTOMATIZADO Y RECOMENDACIONES (GEMINI AI)
==================================================
[Diagnóstico de Colas, Inventario y 3 Recomendaciones de Optimización]
==================================================
```

### 3. Informe Técnico en Word (`Informe_Tecnico_Simulador_Redes.docx`)

Para compilar o actualizar el informe Word con las métricas y capturas más recientes:

```bash
python generar_informe_docx.py
```

El documento generado incluye:

- Membrete y portada formal de la **Universidad José Antonio Páez**.
- Justificación teórica y fórmulas matemáticas completas.
- Tabla formateada con todos los resultados numéricos de la corrida.
- Captura de pantalla de la interfaz gráfica en ejecución incrustada en alta resolución.
- Análisis cualitativo devuelto por el modelo inteligente.
- Conclusiones y recomendaciones de ingeniería para dimensionamiento de red.

---

## Pruebas Automatizadas Unitarias

El proyecto incluye una suite de pruebas unitarias que valida cada componente de manera independiente:

```bash
python test_simulacion.py
```

### Casos de Prueba Incluidos:

1. `test_01_hungarian_router_cost_matrix`: Verifica que la matriz de costos $C_{ij}$ suma correctamente latencia y saturación ponderada, y penaliza con $10^6$ los enlaces caídos.
2. `test_02_hungarian_assignment_resolution`: Valida que el Algoritmo Húngaro minimiza el costo total y descarta enlaces caídos.
3. `test_03_simpy_network_simulation_run`: Ejecuta una simulación estocástica de 120 s en SimPy comprobando la coherencia de $L, L_q, W, W_q$.
4. `test_04_buffer_overflow_and_holding_costs`: Somete el sistema a estrés ($\lambda \gg \mu$) para verificar que se generen descartes de paquetes y costos de penalización por desbordamiento.
5. `test_05_export_report_txt_and_gemini_auditor`: Verifica la generación del archivo `reporte_simulacion.txt` y la invocación de la API / motor experto.
