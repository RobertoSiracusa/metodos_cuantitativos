# Parcial I — Ejercicio 1: Lava carro (M/M/1)

Universidad José Antonio Páez — Facultad de Ingeniería
Escuela de Ingeniería en Computación
Métodos Cuantitativos — Teoría de líneas de espera
Agosto 2026

Salidas de ejecución del programa. Modelo M/M/1 implementado en la clase
`MM1Model` de `tarea1/calculator/src/core/mm1_model.py`.

---

## Parámetros de entrada

| Parámetro | Valor | Origen |
|-----------|-------|--------|
| λ | 9 | Tasa media de llegadas: 9 autos por hora |
| μ | 12 | Servicio de 5 minutos por auto → 60/5 = 12 por hora |
| c | 1 | Un puesto de lavado |
| k | 3 y 5 | Valores de n para P(n > k) |

---

## Comando

Desde la raíz del repositorio `metodos_cuantitativos/`:

```bash
cd tarea1/calculator && python3 main.py --model mm1 --lambda 9 --mu 12 --k 3
```

| Argumento | Valor | Efecto |
|-----------|-------|--------|
| `--model` | `mm1` | Selecciona `MM1Model` (M/M/1) |
| `--lambda` | `9` | Tasa de llegadas |
| `--mu` | `12` | Tasa de servicio |
| `--k` | `3` | Valor de k para el cálculo de P(n > k) |
| `--no-steps` | (opcional) | Omite el desarrollo paso a paso |

---

## Salida del programa

```
M/M/1 - Desarrollo paso a paso
--------------------------------
Paso 1 - Factor de utilizacion (rho)
  Formula:      rho = lambda / mu
  Sustitucion:  rho = 9.0000 / 12.0000
  Resultado:    rho = 0.750000

Paso 2 - Probabilidad de sistema vacio (P0)
  Formula:      P0 = 1 - rho
  Sustitucion:  P0 = 1 - 0.7500
  Resultado:    P0 = 0.250000

Paso 3 - Numero esperado en sistema (L)
  Formula:      L = rho / (1 - rho)
  Sustitucion:  L = 0.7500 / (1 - 0.7500)
  Resultado:    L = 3.000000

Paso 4 - Numero esperado en cola (Lq)
  Formula:      Lq = rho^2 / (1 - rho)
  Sustitucion:  Lq = 0.7500^2 / (1 - 0.7500)
  Resultado:    Lq = 2.250000

Paso 5 - Tiempo promedio en sistema (W)
  Formula:      W = 1 / (mu - lambda)
  Sustitucion:  W = 1 / (12.0000 - 9.0000)
  Resultado:    W = 0.333333

Paso 6 - Tiempo promedio en cola (Wq)
  Formula:      Wq = lambda / (mu * (mu - lambda))
  Sustitucion:  Wq = 9.0000 / (12.0000 * (12.0000 - 9.0000))
  Resultado:    Wq = 0.250000

Paso 7 - Probabilidad de mas de 3 clientes (P(n>3))
  Formula:      P(n > k) = rho^(k+1)
  Sustitucion:  P(n > 3) = 0.7500^4
  Resultado:    P(n > 3) = 0.316406

M/M/1 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 9.000000
Mu (servicios/min): 12.000000
Servidores: 1.000000
Rho (utilizacion): 0.750000  rho = lambda / (c * mu)
P0 (sistema vacío): 0.250000
L (en sistema): 3.000000
Lq (en cola): 2.250000
W (tiempo en sistema): 0.333333
Wq (tiempo en cola): 0.250000
Pw (Erlang-C): 0.750000
P(n > 3): 0.316406  rho^(k+1) with k=3

Resumen:

M/M/1 Reporte
---------------
Lambda (llegadas/min): 9.0000
Mu (servicios/min): 12.0000
Factor de utilización (rho): 0.7500
P0 (servidor ocioso): 0.2500
L (en sistema): 3.0000
Lq (en cola): 2.2500
W (tiempo en sistema, min): 0.3333
Wq (tiempo en cola, min): 0.2500
P(n > 3): 0.316406
```

### Cuadro de resultados

| Línea impresa por el programa | Valor |
|-------------------------------|-------|
| `Lambda (llegadas/min)` | `9.000000` |
| `Mu (servicios/min)` | `12.000000` |
| `Servidores` | `1.000000` |
| `Rho (utilizacion)` | `0.750000` |
| `P0 (sistema vacío)` | `0.250000` |
| `L (en sistema)` | `3.000000` |
| `Lq (en cola)` | `2.250000` |
| `W (tiempo en sistema)` | `0.333333` |
| `Wq (tiempo en cola)` | `0.250000` |
| `Pw (Erlang-C)` | `0.750000` |
| `P(n > 3)` | `0.316406` |

---

## Corrida con k = 5

### Comando

```bash
cd tarea1/calculator && python3 main.py --model mm1 --lambda 9 --mu 12 --k 5 --no-steps
```

Único cambio respecto de la corrida anterior: `--k 5` en lugar de `--k 3`.
λ y μ se mantienen.

### Salida del programa

```
M/M/1 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 9.000000
Mu (servicios/min): 12.000000
Servidores: 1.000000
Rho (utilizacion): 0.750000  rho = lambda / (c * mu)
P0 (sistema vacío): 0.250000
L (en sistema): 3.000000
Lq (en cola): 2.250000
W (tiempo en sistema): 0.333333
Wq (tiempo en cola): 0.250000
Pw (Erlang-C): 0.750000
P(n > 5): 0.177979  rho^(k+1) with k=5

Resumen:

M/M/1 Reporte
---------------
Lambda (llegadas/min): 9.0000
Mu (servicios/min): 12.0000
Factor de utilización (rho): 0.7500
P0 (servidor ocioso): 0.2500
L (en sistema): 3.0000
Lq (en cola): 2.2500
W (tiempo en sistema, min): 0.3333
Wq (tiempo en cola, min): 0.2500
P(n > 3): 0.316406
```

### Cuadro de resultados

| Línea impresa por el programa | Valor |
|-------------------------------|-------|
| `Lambda (llegadas/min)` | `9.000000` |
| `Mu (servicios/min)` | `12.000000` |
| `Servidores` | `1.000000` |
| `Rho (utilizacion)` | `0.750000` |
| `P0 (sistema vacío)` | `0.250000` |
| `L (en sistema)` | `3.000000` |
| `Lq (en cola)` | `2.250000` |
| `W (tiempo en sistema)` | `0.333333` |
| `Wq (tiempo en cola)` | `0.250000` |
| `Pw (Erlang-C)` | `0.750000` |
| `P(n > 5)` | `0.177979` |

---

## Comparativa k = 3 contra k = 5

Valores tal como los imprime el programa en cada corrida:

| Línea impresa | k = 3 | k = 5 |
|---------------|----------|----------|
| `Rho (utilizacion)` | `0.750000` | `0.750000` |
| `P0 (sistema vacío)` | `0.250000` | `0.250000` |
| `L (en sistema)` | `3.000000` | `3.000000` |
| `Lq (en cola)` | `2.250000` | `2.250000` |
| `W (tiempo en sistema)` | `0.333333` | `0.333333` |
| `Wq (tiempo en cola)` | `0.250000` | `0.250000` |
| `P(n > k)` | `0.316406` | `0.177979` |

El parámetro `--k` solo afecta a `P(n > k)`. Las demás medidas dependen
únicamente de λ y μ, por lo que son idénticas en ambas corridas.

---

## Notas sobre la salida

**Bloque `Resumen` de la corrida k = 5.** La línea final del resumen imprime
`P(n > 3): 0.316406` aunque se ejecutó con `--k 5`. El valor correcto para
k = 5 aparece en la sección `Resultados detallados`:
`P(n > 5): 0.177979`. El reporte de resumen tiene el valor de k fijo en 3.

**Literales c y d del enunciado.** El programa no implementa las
probabilidades de tiempo de espera P(Wq > t) ni P(W > t), por lo que esos
dos literales no figuran en la salida. El enunciado del ejercicio 1 indica
resolverlo a mano en la hoja de examen.
