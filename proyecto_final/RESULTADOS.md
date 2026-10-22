# Resultados del proyecto final

Respuestas del simulador con el escenario por defecto (`data/escenario_default.json`). Cada sección
explica qué se obtuvo, por qué, y con qué comando se reproduce. La simulación usa la semilla 42 y
dura 300 unidades de tiempo.

| Pregunta | Respuesta corta |
|----------|-----------------|
| Ruta más corta GW → C1 | GW → N1 → A2 → T1, latencia 7 |
| Tareas que procesa C1 (capacidad 16) | P2, P4, P6 y P7: valor 30, peso 16 |
| Máximo y mínimo de temperatura | máx. local 46.2 °C en 30 %, mín. local 39.8 °C en 70 % |
| Punto crítico de enfriamiento | 50 % de carga (punto de inflexión) |
| Velocidad óptima del ventilador (carga 60 %) | v* = 1, consumo E = 4 |
| Ahorro de energía de refrigeración en la simulación | 70.9 % frente al ventilador a velocidad máxima |
| Reparto de 100 unidades de energía | C1 58.43, C2 15.51, C3 12.21, C4 13.86 (λ = 0.6058) |
| Paquetes atendidos en la simulación | 1115 de 1225 (91 %); 88 perdidos (7.2 %) |

---

## 1. Módulo 1 — Programación dinámica

### 1.1 Ruta más corta (R1)

Comando: `python main.py --modulo m1` (y `--cluster C2`, `C3`, `C4`).

La red tiene 4 etapas: gateway → núcleo (N1-N3) → agregación (A1-A4) → ToR (T1-T4). Se resuelve
hacia atrás con `f_k(s) = min_x { c(s, x) + f_{k+1}(x) }`, donde `c` es la latencia del enlace
(sin congestión, porque no hay tráfico en este modo).

**Tabla de la etapa para el destino T1:**

| Etapa | Nodo | Cálculo | f | Siguiente |
|-------|------|---------|---|-----------|
| 3 | T1 | destino | 0 | — |
| 2 | A1 | 2 + 0 | 2 | T1 |
| 2 | A2 | 3 + 0 | 3 | T1 |
| 2 | A3, A4 | sin enlace a T1 | ∞ | — |
| 1 | N1 | min(4+2, **2+3**, 6+∞) | 5 | A2 |
| 1 | N2 | min(5+2, **3+3**, 2+∞) | 6 | A2 |
| 1 | N3 | min(**6+3**, 3+∞, 2+∞) | 9 | A2 |
| 0 | GW | min(**2+5**, 3+6, 4+9) | 7 | N1 |

**¿Por qué GW → N1 → A2 → T1?** Desde el gateway, ir a N1 cuesta 2 y desde N1 lo mejor que queda
cuesta 5 (por A2), total 7. Las otras opciones del gateway suman 9 (por N2) y 13 (por N3). La ruta
directa por A1 (GW → N1 → A1 → T1) cuesta 8: el enlace N1 → A1 es caro (4) y no lo compensa el
enlace A1 → T1 barato (2).

**Rutas óptimas a todos los clústeres:**

| Clúster | Ruta | Costo | Por qué |
|---------|------|-------|---------|
| C1 (T1) | GW → N1 → A2 → T1 | 7 | 2 + 2 + 3; la siguiente mejor, por A1, cuesta 8 |
| C2 (T2) | GW → N1 → A2 → T2 | 6 | 2 + 2 + 2, todos los enlaces son los más baratos de su etapa |
| C3 (T3) | GW → N2 → A3 → T3 | 7 | 3 + 2 + 2; ir por N1 obliga a usar A2 → T3 (5) o N1 → A3 (6) |
| C4 (T4) | GW → N2 → A3 → T4 | 8 | **empate** con GW → N3 → A4 → T4 (4 + 2 + 2 = 8); gana N2 porque se evalúa primero |

N1 y A2 son los nodos más usados (aparecen en las rutas a C1 y C2): son los puntos más sensibles
de la red.

**Qué pasa cuando falla un nodo** (`--fallar`):

| Nodo caído | Nueva ruta a C1 | Costo | Lectura |
|------------|-----------------|-------|---------|
| A2 | GW → N1 → A1 → T1 | 8 (+1) | hay un reemplazo casi igual de bueno |
| N1 | GW → N2 → A2 → T1 | 9 (+2) | se pierde el enlace barato GW → N1 |
| T1 | no existe | ∞ | T1 es el único acceso al clúster C1 |

Conclusión: la red tolera la caída de cualquier router de núcleo o de agregación pagando 1-2
unidades más de latencia, pero el switch ToR es un punto único de falla de su clúster. Eso explica
casi todas las pérdidas de la simulación (sección 3).

### 1.2 Mochila: qué tareas procesa cada servidor (R2)

Comando: `python main.py --modulo m1 --cluster C1`.

Cada tarea tiene un peso (requerimiento de RAM/CPU) y un valor (prioridad). El servidor tiene
capacidad 16. Se resuelve con `V[i][w] = max(V[i−1][w], V[i−1][w − w_i] + v_i)`.

**Clúster C1** (8 tareas, peso total 36, no caben todas):

| Tarea | Peso | Valor | Valor/peso | ¿Entra? |
|-------|------|-------|------------|---------|
| P4 | 3 | 10 | 3.33 | ✅ |
| P2 | 4 | 8 | 2.00 | ✅ |
| P6 | 2 | 3 | 1.50 | ✅ |
| P7 | 7 | 9 | 1.29 | ✅ |
| P8 | 1 | 1 | 1.00 | — |
| P3 | 6 | 6 | 1.00 | — |
| P5 | 8 | 7 | 0.88 | — |
| P1 | 5 | 2 | 0.40 | — |

Se eligen P2, P4, P6 y P7: **peso 16 (llena exactamente la capacidad) y valor 30**. Las
alternativas cercanas dan menos; por ejemplo P4 + P2 + P7 + P8 pesa 15 y vale 28, y P4 + P2 + P3 +
P6 + P8 pesa 16 y vale 28. En este caso coincide con elegir por mayor valor/peso, pero eso no
siempre pasa en la mochila 0/1; la DP sí garantiza el óptimo.

**Clústeres C2, C3 y C4:** sus tareas pesan 10, 8 y 9, así que caben todas y la mochila las
selecciona completas (valor 13 cada uno). La restricción de capacidad solo es activa en C1.

En la simulación la mochila se corre en cada ventana de despacho con la capacidad libre del
momento. Al final de la corrida, por ejemplo, el servidor S1b tenía 16 unidades libres y 2 tareas
en cola, y eligió las dos (valor 18, peso 11).

---

## 2. Módulo 2 — Optimización no lineal

### 2.1 Temperatura en función de la carga (R3)

Comando: `python main.py --modulo m2`.

Modelo: `T(c) = 0.0002c³ − 0.03c² + 1.26c + 30` (c en %, T en °C).

- `T'(c) = 0.0006(c − 30)(c − 70)` → puntos estacionarios en 30 % y 70 %.
- `T''(c) = 0.0012(c − 50)`.

| Punto | Carga | T | Criterio | Tipo |
|-------|-------|---|----------|------|
| Estacionario | 30 % | 46.2 °C | T''(30) = −0.024 < 0 | máximo local |
| Estacionario | 70 % | 39.8 °C | T''(70) = +0.024 > 0 | mínimo local |
| Inflexión | 50 % | 43.0 °C | T''(50) = 0 | cambio de concavidad |
| Umbral T_max = 50 °C | 94.56 % | 50.0 °C | primera carga con T ≥ 50 | — |

**Interpretación:** con carga baja la temperatura sube (hasta 46.2 °C en 30 %). Entre 30 % y 70 %
los ventiladores entran en régimen y la temperatura baja hasta 39.8 °C. Pasado el 70 % el
enfriamiento ya no alcanza y la temperatura se dispara (56 °C al 100 %).

**Punto crítico de enfriamiento de emergencia: 50 %.** Se toma el menor entre la inflexión (50 %) y
la carga donde se alcanza T_max (94.56 %). Desde la inflexión la curva se vuelve convexa: la
temperatura empieza a acelerarse, así que conviene actuar antes de llegar al umbral.

**En la simulación:** la carga media fue 33.9 % (máximo 66.7 %) y la temperatura media 44.45 °C.
La temperatura más alta de la corrida fue 46.2 °C, exactamente el máximo local, porque la carga
nunca pasó del 70 %; nunca se llegó a los 50 °C. Aun así hubo 16 alertas de emergencia (29 de 299
ticks, ~10 % del tiempo), porque el criterio de la inflexión es preventivo: avisa cuando la carga
cruza el 50 %, antes de que la temperatura sea peligrosa.

### 2.2 Consumo eléctrico de la refrigeración: método del gradiente (R4)

Modelo de consumo: `E(v) = v³ + 0.05·Q / v`, con v la velocidad del ventilador y Q la carga.
- `v³` es la potencia del ventilador: crece con el cubo de la velocidad.
- `0.05·Q / v` es la penalización por el calor que no se extrae.

Las dos fuerzas se oponen: girar rápido cuesta mucho, girar lento deja calor. El óptimo es el
equilibrio `E'(v) = 3v² − 0.05·Q / v² = 0 → v* = (0.05·Q / 3)^(1/4)`.

**Caso de prueba con Q = 60 %** (α = 0.05, empieza en v = 0.3):

| Iteración | v | E(v) | E'(v) |
|-----------|---|------|-------|
| inicio | 0.300 | 10.03 | — |
| 1 | 1.953 | 8.99 | −33.06 |
| 2 | 1.420 | 4.98 | 10.66 |
| 3 | 1.192 | 4.21 | 4.56 |
| 5 | 1.036 | 4.01 | 0.98 |
| 10 | 1.000 | 4.00 | 0.01 |

- Converge a **v* = 1 con consumo E = 4**: un **60 % menos** que al inicio (10.03).
- En la primera iteración se pasa del óptimo (v = 1.95), porque en v = 0.3 la pendiente es muy
  grande. Después se acerca, reduciendo el error a ~0.4 veces el anterior en cada paso.
- La velocidad óptima depende de la carga: Q = 20 % → v* = 0.76 (E = 1.75); Q = 60 % → v* = 1
  (E = 4); Q = 85 % → v* = 1.09 (E = 5.19). A más carga, más ventilación.

**Consumo acumulado en la simulación de 300 unidades de tiempo:**

| Estrategia | Consumo total | Diferencia frente al gradiente |
|------------|---------------|--------------------------------|
| Ventilador siempre a velocidad máxima (v = 2) | 2645.7 | el gradiente ahorra **70.9 %** |
| Ventilador fijo a velocidad media (v = 1) | 806.3 | el gradiente ahorra 4.6 % |
| Método del gradiente (un paso por tick) | 769.6 | — |
| Óptimo exacto en cada instante (`v*`) | 768.0 | el gradiente gasta solo 0.2 % más |

**Conclusión del análisis de consumo:** ajustar la velocidad a la carga en tiempo real ahorra
71 % frente a la práctica conservadora de ventilar al máximo. El gradiente sigue al óptimo
teórico tan de cerca (diferencia media |v − v*| = 0.024) que solo pierde 0.2 % de energía, aun
dando un solo paso por tick mientras la carga cambia. Frente a una velocidad fija bien elegida
(v = 1) el ahorro es menor (4.6 %), porque la carga media (34 %) está cerca de la que hace óptima
esa velocidad; el beneficio del ajuste dinámico crece cuanto más varía la carga.

### 2.3 Reparto del presupuesto eléctrico entre clústeres: Lagrange (R5)

Problema: maximizar el rendimiento `R = Σ w_i · ln(1 + E_i)` con `Σ E_i = E_max = 100`. `w_i` es la
demanda de cada clúster (suma de requerimientos de sus tareas).

Solución: `λ = Σ w_i / (E_max + n) = 63 / 104 = 0.6058` y `E_i = w_i / λ − 1`.

| Clúster | Demanda w_i | Energía E_i | % del total | Rendimiento marginal w_i / (1 + E_i) |
|---------|-------------|-------------|-------------|--------------------------------------|
| C1 | 36 | 58.43 | 58.4 % | 0.6058 |
| C2 | 10 | 15.51 | 15.5 % | 0.6058 |
| C3 | 8 | 12.21 | 12.2 % | 0.6058 |
| C4 | 9 | 13.86 | 13.9 % | 0.6058 |
| **Total** | 63 | **100.00** | 100 % | λ = 0.6058 |

**¿Por qué este reparto?**
- **Condición de optimalidad:** en el óptimo, la última unidad de energía rinde lo mismo en todos
  los clústeres (la última columna es igual a λ en todas las filas). Si un clúster rindiera más,
  convendría pasarle energía de otro.
- **C1 recibe más de la mitad** porque concentra el 57 % de la demanda (36 de 63). La fórmula
  reparte `E_max + n = 104` en proporción a la demanda y luego resta 1 a cada uno; por eso C1 queda
  apenas por encima de su proporción (58.4 % frente a 57.1 %).
- **λ = 0.6058 es el precio sombra:** si el presupuesto subiera de 100 a 101, el rendimiento óptimo
  aumentaría en ~0.61.

**Comparación con otros repartos:**

| Reparto | Rendimiento R |
|---------|---------------|
| Partes iguales (25 cada uno) | 205.26 |
| Proporcional a la demanda | 220.00 |
| Lagrange | **220.02** (el máximo) |

Lagrange supera en 7.2 % al reparto igual. Frente al proporcional la ganancia es mínima; aquí
ambos casi coinciden porque los E_i son grandes y el "−1" de la fórmula pesa poco.

**En la simulación** el reparto se recalcula en cada tick con la demanda del momento. λ promedió
0.69 y varió entre 0 y 1.88. Cada clúster quedó con energía 0 en algunos ticks (entre 18 y 36),
cuando no tenía demanda o sus servidores estaban caídos: es la condición de KKT, que fija `E_i = 0`
y reparte el presupuesto entre los que sí lo necesitan. Al final de la corrida, C3 y C1 se llevaban
la mayor parte (44.95 y 40.12) y C2 casi nada (1.42) por tener la cola vacía.

---

## 3. Módulo 3 — Simulación del sistema completo (R6)

Comando: `python main.py --headless` (o `python main.py` para verlo en el dashboard).

Llegan en promedio 4 tareas por unidad de tiempo (Poisson), viajan por la ruta óptima del momento,
cada servidor elige con la mochila cuáles procesar, y routers y servidores fallan al azar
(MTBF = 200, MTTR = 15).

### 3.1 Métricas de colas

| Métrica | Simulado | M/M/1 de referencia |
|---------|----------|---------------------|
| Tareas generadas | 1225 | — |
| Completadas | 1115 (91.0 %) | — |
| Perdidas | 88 (7.2 %) | — |
| Utilización | 33.9 % | ρ = 31.6 % |
| Throughput | 3.73 tareas/u.t. | λ = 4 |
| Espera en cola Wq | 1.17 | 0.29 |
| Tiempo en el servidor W | 3.45 | 0.93 |
| Largo medio de colas Lq (todo el sistema) | 6.24 | 0.15 por servidor |

**Lectura:**
- **La utilización simulada (33.9 %) coincide con la teórica (31.6 %)**: la carga de trabajo está
  bien modelada y el sistema está holgado.
- **La espera es ~4 veces la del M/M/1**, por tres razones del diseño:
  - Las tareas se despachan por ventanas de 1 unidad de tiempo; solo eso agrega en promedio ~0.5
    de espera.
  - La mochila prioriza las tareas de mayor valor, así que las de baja prioridad esperan más.
  - Mientras un servidor está caído su cola no avanza.
- **El throughput (3.73) es menor que la tasa de llegada (4)** por las tareas perdidas y las que
  seguían en el sistema al cortar la simulación.

### 3.2 Pérdidas y fallas

- Hubo 35 fallas con sus 35 reparaciones. Cada nodo está disponible el 200 / 215 ≈ **93 %** del
  tiempo.
- **86 de las 88 pérdidas (98 %) fueron "sin ruta"**: tareas que llegaron mientras el switch ToR de
  su clúster estaba caído. Es lo que anticipaba el análisis de fallas de la sección 1.1: el ToR es
  un punto único de falla.
- Solo 2 tareas se perdieron porque los dos servidores de su clúster estaban caídos a la vez.
- **Recomendación:** conectar cada clúster a dos switches ToR eliminaría casi todas las pérdidas.

### 3.3 Cambios de ruta por congestión (R9)

Hubo 353 cambios de ruta en 300 unidades de tiempo:
- **199 (56 %) fueron de C4** alternando entre GW → N2 → A3 → T4 y GW → N3 → A4 → T4. Las dos
  cuestan 8 sin tráfico (el empate de la sección 1.1); cualquier tarea en tránsito por una de ellas
  sube su costo y la otra pasa a ser la mejor. El tráfico hacia C4 se balancea solo entre los dos
  caminos.
- **C1 alternó entre A2 y A1** (30 y 26 veces): la ruta por A1 cuesta solo 1 más, así que la
  congestión en A2 basta para desviarla.
- El resto son desvíos por fallas de nodos y, en el caso de C2, 4 períodos "sin ruta" mientras su
  acceso estuvo caído.

Con una histéresis (cambiar de ruta solo si la mejora supera un umbral) se reducirían las
oscilaciones, a cambio de tolerar rutas apenas peores.

---

## 4. Conclusiones

1. **Rutas (DP):** la ruta óptima a cada clúster sale de minimizar la latencia etapa por etapa; N1 y
   A2 forman el camino principal. La red resiste fallas de routers con 1-2 unidades más de
   latencia, pero el switch ToR es un punto único de falla.
2. **Mochila:** solo C1 tiene más demanda que capacidad; la DP llena exactamente las 16 unidades con
   el máximo valor posible (30).
3. **Temperatura:** el punto crítico es 50 % de carga. Con la carga de la simulación (media 34 %) la
   temperatura nunca pasó de 46.2 °C, pero la alerta preventiva se activó ~10 % del tiempo.
4. **Consumo eléctrico:** el método del gradiente reduce el gasto de refrigeración 71 % frente al
   ventilador a máxima velocidad y queda a 0.2 % del óptimo teórico.
5. **Presupuesto eléctrico:** Lagrange iguala el rendimiento marginal de todos los clústeres
   (λ = 0.6058), da 7.2 % más rendimiento que el reparto igual y deja sin energía a los clústeres
   sin demanda.
6. **Sistema completo:** atiende el 91 % de las tareas con 34 % de utilización. Las pérdidas vienen
   casi todas de caídas de switches ToR, y la espera extra frente al M/M/1 viene del despacho por
   ventanas.
