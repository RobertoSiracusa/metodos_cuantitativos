# Posibles preguntas de la defensa

Banco de preguntas que podría hacer el profesor, con una respuesta corta basada en lo que hace el
código y en los números que da el escenario por defecto. Complementa a `GUIA_DEFENSA.md`.

---

## Parte A — Conocimiento matemático

### A1. Programación dinámica: ruta más corta (R1)

**¿Qué es la programación dinámica y qué la diferencia de "probar todas las rutas"?**
Divide el problema en etapas y guarda la solución óptima de cada subproblema en una tabla, para no
recalcularla. Probar todas las rutas crece como el producto de los nodos por etapa; la DP solo
revisa cada enlace una vez.

**Enuncie el principio de optimalidad de Bellman.**
Una política óptima tiene la propiedad de que, sea cual sea el estado inicial y la primera
decisión, las decisiones restantes forman una política óptima para el estado que resulta. En la
red: si la mejor ruta de GW a T1 pasa por A2, entonces el tramo A2 → T1 también es el mejor
desde A2.

**Escriba la ecuación recursiva que usó.**
`f_k(s) = min_x { c(s, x) + f_{k+1}(x) }`, con `f(destino) = 0` y `f = ∞` para los demás nodos
de la última etapa. Está en `RutaMasCorta._construir_tabla`.

**¿Por qué recursión hacia atrás y no hacia adelante?**
Las dos dan el mismo óptimo. Hacia atrás, la tabla dice para cada nodo cuál es el mejor siguiente
salto hacia el destino, y la reconstrucción se hace avanzando desde el origen. Es el modelo de la
diligencia (stagecoach) visto en clase.

**¿Cuáles son la etapa, el estado, la decisión y el retorno en su modelo?**
- Etapa: la capa de la red (gateway, núcleo, agregación, ToR).
- Estado: el nodo en el que está el paquete.
- Decisión: el enlace que toma a la capa siguiente.
- Retorno: el costo (latencia) del enlace.

**Resuelva a mano la ruta GW → T1.**
Hacia atrás: `f(A1) = 2`, `f(A2) = 3`, `f(A3) = ∞` (no tiene enlace a T1). `f(N1) = min(4+2, 2+3, 6+∞) = 5`
por A2. `f(N2) = min(5+2, 3+3, 2+∞) = 6`. `f(N3) = min(6+3, 3+∞, 2+∞) = 9`. `f(GW) = min(2+5, 3+6, 4+9) = 7`.
Ruta: GW → N1 → A2 → T1, costo 7.

**¿Cómo entra la congestión en el costo?**
`c = l0 · (1 + ρ / (1 − ρ))`, con `ρ` = paquetes en tránsito / capacidad del enlace. El factor
`1 / (1 − ρ)` sale del tiempo de espera de una cola M/M/1: con poca ocupación el costo es casi
`l0`, y crece sin límite cuando `ρ → 1`.

**¿Por qué limitan ρ a 0.95?**
Para no dividir por cero. Con `ρ = 0.95` el factor vale `1 + 0.95/0.05 = 20`, así que un enlace
saturado cuesta 20 veces su latencia base y la DP lo evita.

**¿Cómo modela un nodo caído?**
Con `f = ∞`. Así ningún mínimo lo elige. Si todos los caminos pasan por nodos caídos, el costo
del origen queda en ∞ y el resultado es "no existe ruta".

**¿Cuál es la complejidad?**
Cada enlace se evalúa una vez: O(E), con E el número de enlaces (22 en el escenario).

**¿Por qué no usaron Dijkstra?**
El enunciado pide programación dinámica, y la red de un centro de datos ya está organizada por
capas sin ciclos, que es justo el caso de la DP por etapas. Dijkstra sirve para grafos generales
con costos no negativos y daría el mismo resultado aquí.

### A2. Programación dinámica: mochila 0/1 (R2)

**Plantee el modelo de la mochila.**
Maximizar `Σ v_i x_i` sujeto a `Σ w_i x_i ≤ W`, `x_i ∈ {0, 1}`. En el proyecto `w_i` es el
requerimiento de la tarea (RAM/CPU), `v_i` su prioridad y `W` la capacidad libre del servidor.

**Escriba la recurrencia.**
`V[i][w] = V[i−1][w]` si `w_i > w`; si no, `V[i][w] = max(V[i−1][w], V[i−1][w − w_i] + v_i)`, con
`V[0][w] = 0`. La respuesta es `V[n][W]`.

**¿Cómo se reconstruye la solución?**
Recorriendo la tabla hacia atrás: si `V[i][w] ≠ V[i−1][w]`, la tarea i entra y se resta su peso a
`w`. Ante un empate se prefiere no incluirla.

**¿Por qué 0/1 y no fraccionaria?**
Porque una tarea no se puede ejecutar a medias. La versión fraccionaria se resuelve con un
algoritmo voraz (ordenar por `v_i / w_i`), pero para 0/1 ese algoritmo no garantiza el óptimo.

**¿Cuál es la complejidad? ¿Es polinomial?**
O(n · W). Es pseudo-polinomial, porque depende del valor de W y no del número de bits con que se
escribe. La mochila 0/1 es NP-difícil en general; funciona rápido aquí porque W ≤ 16.

**Resultado con los datos por defecto.**
C1 con capacidad 16: elige P2 (4, 8), P4 (3, 10), P6 (2, 3) y P7 (7, 9). Peso 16, valor 30.

**¿Cómo se usa la mochila dentro de la simulación?**
En cada ventana de despacho (cada 1 unidad de tiempo), cada servidor operativo corre la mochila
sobre su cola con su capacidad libre. Las tareas elegidas pasan a procesarse y las demás esperan
a la ventana siguiente.

### A3. Cálculo: modelo térmico (R3)

**¿Qué función usaron y por qué?**
`T(c) = 0.0002c³ − 0.03c² + 1.26c + 30`, con c la carga en %. Es un cúbico elegido para que el
máximo, el mínimo y la inflexión queden dentro de [0, 100], como pide el enunciado.

**Derive y encuentre los puntos estacionarios.**
`T'(c) = 0.0006c² − 0.06c + 1.26 = 0.0006(c² − 100c + 2100) = 0.0006(c − 30)(c − 70)`.
`T'(c) = 0` en c = 30 y c = 70.

**Clasifíquelos.**
`T''(c) = 0.0012c − 0.06 = 0.0012(c − 50)`.
- `T''(30) = −0.024 < 0`: máximo local, T(30) = 46.2 °C.
- `T''(70) = 0.024 > 0`: mínimo local, T(70) = 39.8 °C.

**¿Dónde está el punto de inflexión y qué significa?**
`T''(c) = 0` en c = 50 (T = 43 °C). Ahí la curva pasa de cóncava a convexa: desde ese punto la
temperatura empieza a acelerarse hacia el alza.

**¿Cómo definieron el punto crítico de emergencia?**
Es el menor entre la inflexión (50 %) y la primera carga donde `T ≥ T_max` (con 50 °C eso ocurre
en 94.56 %). Gana la inflexión, así que el punto crítico es 50 %.

**¿Los extremos son globales?**
No, son locales. En [0, 100] el máximo global está en c = 100 (T = 56 °C) y el mínimo global en
c = 0 (T = 30 °C). Para extremos globales hay que comparar también los bordes del intervalo.

**¿Qué haría el programa si `T''` fuera 0 en un punto estacionario, o si el discriminante fuera negativo?**
Si `T'' = 0` el criterio de la segunda derivada no decide y se marca como "silla". Si el
discriminante es negativo, `T'` no tiene raíces reales: la función es monótona y no hay puntos
estacionarios (devuelve una lista vacía).

**Lectura física de la curva.**
La temperatura sube con la carga, baja cuando los ventiladores entran en régimen (entre 30 % y
70 %) y luego se dispara porque el enfriamiento ya no alcanza.

### A4. Método del gradiente (R4)

**¿Qué función minimizan?**
El consumo `E(v) = a·v³ + b·Q / v`. `a·v³` es la potencia del ventilador (ley de afinidad: crece
con el cubo de la velocidad) y `b·Q / v` penaliza el calor no extraído. Q es la carga actual.

**Escriba la iteración.**
`E'(v) = 3a·v² − b·Q / v²` y `v ← v − α·E'(v)`, recortado a `[v_min, v_max] = [0.1, 2]`, con α = 0.05.

**¿Por qué se resta el gradiente?**
El gradiente apunta hacia donde la función crece más rápido; para minimizar se avanza en sentido
contrario.

**Calcule el óptimo analítico.**
`E'(v) = 0 → 3a·v⁴ = b·Q → v* = (b·Q / 3a)^(1/4)`. Con a = 1, b = 0.05 y Q = 60:
`v* = (3/3)^(1/4) = 1`.

**¿Es un mínimo y es único?**
Sí. `E''(v) = 6a·v + 2b·Q / v³ > 0` para todo v > 0, así que E es estrictamente convexa y el punto
crítico es el único mínimo global.

**¿Converge siempre? ¿Cómo elegiría α?**
Cerca del óptimo converge si `α < 2 / E''(v*)`. Con Q = 60, `E''(1) = 6 + 6 = 12`, y el límite es
α < 0.167; se usa 0.05. Si α es muy grande el método oscila o diverge, y si es muy chico converge
lento. Las cotas `[v_min, v_max]` evitan que un paso grande saque a v del dominio.

**¿A qué velocidad converge?**
De forma lineal: el error se multiplica en cada paso por `|1 − α·E''(v*)| = |1 − 0.05·12| = 0.4`.
Se ve en la salida de `--modulo m2`: el error pasa de 0.085 a 0.036 entre las iteraciones 4 y 5.

**¿Por qué usan gradiente si tienen la fórmula cerrada?**
Porque el enunciado pide el método y porque en tiempo real Q cambia en cada tick. El gradiente da
un paso por tick y va siguiendo al óptimo a medida que se mueve; la fórmula sirve para verificarlo
(la curva v* del gráfico).

### A5. Multiplicadores de Lagrange (R5)

**Plantee el problema.**
Maximizar `R = Σ w_i · ln(1 + E_i)` sujeto a `Σ E_i = E_max` y `E_i ≥ 0`. `w_i` es la demanda del
clúster i.

**¿Por qué el logaritmo?**
Da rendimientos decrecientes: cada unidad extra de energía rinde menos que la anterior. El `+1`
hace que `E_i = 0` sea válido (ln 1 = 0).

**Resuelva con Lagrange.**
`L = Σ w_i ln(1 + E_i) − λ(Σ E_i − E_max)`.
`∂L/∂E_i = w_i / (1 + E_i) − λ = 0 → E_i = w_i / λ − 1`.
Sumando y usando la restricción: `Σ w_i / λ − n = E_max → λ = Σ w_i / (E_max + n)`.

**Hágalo con los datos por defecto.**
Demandas 36, 10, 8 y 9 (suma 63), E_max = 100, n = 4: `λ = 63 / 104 = 0.6058`.
`E_C1 = 36/0.6058 − 1 = 58.43`, `E_C2 = 15.51`, `E_C3 = 12.21`, `E_C4 = 13.86`. Suman 100.

**¿Qué significa λ?**
Es el precio sombra: cuánto aumenta el rendimiento óptimo por cada unidad extra de energía
disponible (`dR*/dE_max = λ`).

**¿Qué pasa si algún E_i sale negativo?**
Se aplican las condiciones de KKT: por holgura complementaria, ese clúster recibe `E_i = 0` y se
vuelve a resolver con los demás. Ejemplo del test: demandas 3 y 0.2 con E_max = 2 dan λ = 0.8 y
`E_2 < 0`; se fija `E_2 = 0` y queda λ = 1, `E_1 = 2`.

**¿Por qué ese ciclo termina?**
Quitar un clúster con `w_j < λ` hace que λ crezca, así que los ya excluidos siguen siendo
negativos y nunca vuelven a entrar. Termina en a lo sumo n vueltas.

**¿Cómo sabe que es un máximo y no un mínimo?**
R es cóncava (su Hessiana es diagonal con `−w_i / (1 + E_i)² < 0`) y la restricción es lineal, así
que las condiciones de KKT son suficientes y el punto es el máximo global.

**¿Y si ningún clúster tiene demanda?**
R vale 0 para cualquier reparto; el programa divide E_max en partes iguales.

### A6. Teoría de colas y simulación (R6)

**¿Qué distribuciones usan y por qué?**
- Llegadas Poisson con tasa λ = 4: equivale a tiempos entre llegadas exponenciales con media 1/λ.
- Servicio exponencial con media `requerimiento / tasa_servicio`.
- Fallas y reparaciones exponenciales con MTBF = 200 y MTTR = 15.

La exponencial no tiene memoria, que es la hipótesis de los modelos M/M/1 y M/M/c.

**Defina Wq, W, Lq y la utilización.**
- Wq: espera en cola antes del servicio.
- W: tiempo total en el servidor (espera + servicio).
- Lq: número medio de tareas en cola.
- Utilización: fracción de la capacidad ocupada.

Se relacionan por la ley de Little: `L = λ·W` y `Lq = λ·Wq`.

**Escriba las fórmulas M/M/1.**
`ρ = λ/μ`, `Lq = ρ² / (1 − ρ)`, `Wq = ρ / (μ − λ)`, `W = 1 / (μ − λ)`. Solo es estable si ρ < 1.

**¿Por qué el Wq simulado (1.17) es mayor que el M/M/1 de referencia (0.29)?**
El M/M/1 es solo una referencia; el sistema no es M/M/1:
- Las tareas se despachan por ventanas de 1 unidad: solo eso agrega en promedio ~0.5 de espera.
- Cada servidor atiende varias tareas en paralelo según su capacidad.
- Hay fallas: mientras un servidor está caído no despacha nada.

**¿Qué disponibilidad tiene cada nodo?**
`MTBF / (MTBF + MTTR) = 200 / 215 ≈ 93 %`.

**¿Por qué se pierden paquetes?**
Hubo 86 pérdidas "sin ruta", cuando cae el ToR de un clúster y no hay forma de llegar, y 2 "sin
servidor", cuando están caídos los dos servidores del clúster.

**¿Qué es una simulación de eventos discretos?**
El tiempo salta de un evento al siguiente (llegada, fin de servicio, falla), en vez de avanzar en
pasos fijos. SimPy mantiene la cola de eventos ordenada por tiempo.

**¿Cómo garantizan que los resultados sean reproducibles?**
El motor usa su propio `random.Random(semilla)`. Con la misma semilla se obtienen los mismos
eventos y métricas (lo verifica `test_misma_semilla_misma_corrida`).

**¿Una sola corrida alcanza para sacar conclusiones?**
No del todo: es una muestra de un proceso aleatorio. Lo correcto sería repetir con varias semillas
y reportar promedios con intervalos de confianza, y descartar el período inicial de calentamiento.

---

## Parte B — Programación

### B1. POO

**Muestre los cuatro pilares en su código.**
- Abstracción: `Nodo`, `ModeloProgramacionDinamica`, `Optimizador`, `Panel` y `ProveedorIA` son
  clases abstractas (`abc.ABC`).
- Encapsulamiento: atributos con `_` y propiedades; `tabla`, `historial` y `estado()` devuelven
  copias.
- Herencia: `Router` y `Servidor` heredan de `Nodo`; `RutaMasCorta` y `Mochila` de la base de DP.
- Polimorfismo: el motor hace `for opt in self._optimizadores: opt.actualizar(entrada)` sin saber
  si es gradiente o Lagrange.

**¿Qué es una clase abstracta y qué pasa si intento instanciarla?**
Define métodos sin implementación (`@abstractmethod`) que las subclases deben implementar.
Instanciarla, o instanciar una subclase incompleta, lanza `TypeError`.

**¿Qué patrones de diseño usaron?**
- Template Method: `ModeloProgramacionDinamica.resolver()` fija el orden preparar → construir
  tabla → reconstruir, y cada subclase llena los pasos. `Optimizador.actualizar()` hace lo mismo
  con `_paso`.
- Observer: `MotorSimulacion.suscribir(fn)` avisa de fallas, cambios de ruta y emergencias.
- Null Object: `ProveedorSinConexion` responde algo válido cuando no hay IA, sin `if`s en el
  reporte.

**¿Qué ventaja concreta le dio el Template Method?**
El esqueleto de la DP (y guardar la tabla) se escribe una sola vez. Agregar otro problema de DP
solo exige implementar tres métodos.

**¿Por qué `Paquete` y los resultados son `@dataclass(frozen=True)`?**
Son valores que no deben cambiar después de crearse. Inmutables, se pueden compartir sin riesgo y
usar en conjuntos o como claves de diccionario.

**¿Por qué `tabla` devuelve una copia profunda?**
Para que quien la lea desde afuera no pueda modificar el estado interno del modelo
(encapsulamiento).

**¿Composición o herencia? Dé un ejemplo de cada una.**
- Herencia, para relaciones "es un": un `Router` es un `Nodo`.
- Composición, para "tiene": `MotorSimulacion` tiene una `Red`, una `RutaMasCorta` y los
  optimizadores; `Red` tiene nodos y enlaces.

### B2. Arquitectura e independencia de módulos (P8)

**¿Cómo demuestra que los módulos son independientes?**
- `core/` no importa nada de `simulation/`, `gui/` ni `services/`.
- `--modulo m1` y `--modulo m2` se ejecutan sin cargar SimPy ni Pygame (los imports del motor y
  de la GUI en `main.py` son diferidos).
- Cada módulo tiene sus propios tests.

**¿Por qué `EntradaOptimizacion` está en `core/` y no usan directamente `EstadoSimulacion`?**
Si los optimizadores recibieran el estado del motor, `core/` dependería de `simulation/`. Con una
entrada mínima definida en `core/`, el motor la arma y los optimizadores no saben que existe SimPy.

**¿Puede la GUI modificar la simulación?**
No. Solo recibe `EstadoSimulacion`, una foto armada con copias; no tiene referencia a la red ni a
los modelos.

**¿Cómo agregaría un tercer optimizador o un panel nuevo?**
Se crea una subclase de `Optimizador` (implementando `_paso`) o de `Panel` (implementando
`_contenido`) y se agrega a la lista. El bucle del motor o de la GUI no cambia.

### B3. SimPy

**¿Cómo funciona un proceso en SimPy?**
Es una función generadora. Cada `yield env.timeout(t)` suspende el proceso hasta que el reloj
avance t. `env.process(...)` lo registra y `env.run(until=...)` ejecuta los eventos hasta ese
instante.

**¿Qué procesos tiene su simulación?**
- `_llegadas`: genera paquetes.
- `_viajar`: un proceso por paquete, salto a salto por la ruta.
- `_despachador`: uno por servidor, corre la mochila en cada ventana.
- `_servir`: uno por tarea en proceso.
- `_fallas`: uno por nodo.
- `_control`: térmico, gradiente, Lagrange y la detección de emergencias.

**¿Dónde se integran los módulos 1 y 2?**
- M1: cada paquete recalcula la ruta con los costos del momento (`_viajar`) y cada servidor usa la
  mochila (`_despachador`).
- M2: en cada tick de control, `_control` calcula la temperatura y da un paso de cada optimizador.

**¿Cómo detecta un cambio de ruta (R9)?**
`_actualizar_ruta` compara la ruta nueva con la anterior del clúster; si es distinta emite el
evento `cambio_ruta`, que el panel de topología muestra haciendo parpadear la ruta en amarillo.

**¿Cómo comprobaron que no se "pierden" paquetes por un error del código?**
Con un test de conservación: generados = completados + perdidos + en servidores + en tránsito.

### B4. Pygame

**¿Cómo se sincroniza el tiempo real con el tiempo simulado?**
El bucle corre a 30 cuadros por segundo. En cada cuadro el motor avanza `dt × velocidad` unidades
de simulación (5 por segundo por defecto, ajustable con +/−). Dibujar y simular están desacoplados.

**¿Cómo animan los paquetes?**
El estado trae, para cada paquete en tránsito, el enlace y el progreso entre 0 y 1. El panel
interpola la posición entre los dos nodos.

**¿Cómo probaron la GUI sin abrir una ventana?**
Con `SDL_VIDEODRIVER=dummy`. El test dibuja todos los paneles sobre una superficie y guarda la
imagen.

### B5. Validación de datos (P6) y datos por defecto (P7)

**¿Qué valida y dónde?**
`Validador` comprueba tipos, rangos, que los valores sean finitos (no NaN ni infinito), ids
duplicados, que los enlaces vayan a la capa siguiente, que exista un único gateway y que las
secciones de parámetros sean conocidas. Acumula todos los errores y los muestra juntos. Los
argumentos de la línea de comandos usan el mismo `validar_rango`: por ejemplo, `--carga 150` da
error.

**¿Por qué rechazan `True` como número?**
En Python `bool` es subclase de `int` (`True == 1`), pero un valor booleano en un campo numérico
es casi seguro un error del archivo.

**¿Dónde están los datos por defecto?**
En `data/escenario_default.json`: topología, clústeres, 14 paquetes de prueba y los parámetros de
M2 y de la simulación. Con `--escenario` se carga otro archivo, que pasa por la misma validación.

### B6. IA y reporte PDF (R7)

**¿Cómo se conecta a la IA?**
Con una petición HTTP POST a la API REST de Gemini usando `requests`. Prueba varios modelos en
orden y, si la clave es inválida (401/403), deja de intentar.

**¿Dónde guarda la clave y por qué no está en el código?**
En `.env`, que git ignora. La clave viaja en la cabecera `x-goog-api-key` y no en la URL, para que
no quede en registros.

**¿Qué pasa si no hay internet?**
`ClienteGemini` captura el error y devuelve el texto de `ProveedorSinConexion`. El PDF se genera
igual, con la sección de IA marcada como no disponible.

**¿Cómo testearon la IA sin gastar llamadas?**
Con `monkeypatch`: se reemplaza `requests.post` por una función que devuelve respuestas falsas
(éxito, clave inválida, sin red).

**¿Por qué existe la función `_latin1`?**
Las fuentes base de fpdf solo cubren latin-1, y la IA puede responder con símbolos como λ o →. Se
traducen o reemplazan para que el PDF no falle.

### B7. Pruebas

**¿Cómo saben que los algoritmos están bien?**
- 71 tests con casos resueltos a mano: tabla de la ruta, mochila, derivadas en puntos conocidos,
  convergencia a v*, Lagrange con y sin KKT, fórmulas M/M/1.
- La derivada analítica se compara contra una diferencia finita.
- También se prueban invariantes de la simulación (conservación, capacidad nunca excedida, suma de
  energía = E_max).

---

## Parte C — Preguntas incómodas (limitaciones honestas)

**¿Puede una tarea de baja prioridad quedarse esperando para siempre?**
Sí, puede haber inanición: la mochila siempre prefiere las de mayor valor. Se podría corregir
aumentando la prioridad con el tiempo de espera (aging).

**¿Las funciones térmica y de consumo son reales?**
Son modelos didácticos que respetan la forma física (ley del cubo del ventilador, rendimientos
decrecientes), pero los coeficientes no salen de mediciones. Se pueden cambiar en el JSON.

**¿Qué pasa con las tareas en proceso cuando un servidor falla?**
En el modelo terminan su servicio; el servidor caído solo deja de recibir y despachar tareas
nuevas. Es una simplificación.

**¿Por qué la ruta cambia tantas veces (≈350 en 300 unidades de tiempo)?**
Algunas rutas tienen costos base empatados (por ejemplo, las dos rutas a T4 cuestan 8). Cualquier
paquete en tránsito desempata, y la ruta oscila. Se podría agregar histéresis: cambiar solo si la
mejora supera un umbral.

**¿La ruta considera la latencia de los routers?**
La DP minimiza la suma de costos de los enlaces. La latencia de procesamiento de cada router se
suma al tiempo de tránsito en la simulación, pero no entra en la decisión porque es igual para
todos los routers del escenario.
