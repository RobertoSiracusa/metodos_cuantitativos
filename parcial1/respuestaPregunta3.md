# Parcial I — Ejercicio 3: Centro de datos, 5 servidores (M/M/5)

Universidad José Antonio Páez — Facultad de Ingeniería
Escuela de Ingeniería en Computación
Métodos Cuantitativos — Teoría de líneas de espera
Agosto 2026

Salidas de ejecución del programa. Modelo M/M/c implementado en la clase
`MMCModel` de `tarea1/calculator/src/core/mmc_model.py`.

---

## Parámetros de entrada

| Parámetro | Valor | Origen |
|-----------|-------|--------|
| λ | 10 | Llegadas cada 6 minutos → 60/6 = 10 por hora |
| μ | 12 | Servicio cada 5 minutos → 60/5 = 12 por hora |
| c | 5 | Cinco servidores en paralelo, cola infinita FIFO |

El enunciado del ejercicio 3 no especifica λ ni el tiempo de servicio: se
continúan los del ejercicio 2.

---

## Comando

Desde la raíz del repositorio `metodos_cuantitativos/`:

```bash
cd tarea1/calculator && python3 main.py --model mmc --servers 5 --lambda 10 --mu 12
```

| Argumento | Valor | Efecto |
|-----------|-------|--------|
| `--model` | `mmc` | Selecciona `MMCModel` (M/M/c, con Erlang-C) |
| `--servers` | `5` | Número de servidores en paralelo |
| `--lambda` | `10` | Tasa de llegadas |
| `--mu` | `12` | Tasa de servicio por servidor |
| `--no-steps` | (opcional) | Omite el desarrollo paso a paso |

---

## Salida del programa

```
M/M/5 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 10.000000
Mu (servicios/min): 12.000000
Servidores: 5.000000
Rho (utilizacion): 0.166667  rho = lambda / (c * mu)
P0 (sistema vacío): 0.434571
L (en sistema): 0.833683
Lq (en cola): 0.000349
W (tiempo en sistema): 0.083368
Wq (tiempo en cola): 0.000035
Pw (Erlang-C): 0.001746

Resumen:

M/M/5 Reporte
----------------
Lambda (llegadas/horas): 10.0000
Mu (servicios/horas): 12.0000
Servidores: 5
Factor de utilización (rho): 0.1667
P0 (sistema vacío): 0.4346
Lq (en cola): 0.0003
W (tiempo en sistema, horas): 0.0834
W (horas) = 0.0834 | 5.00 minutos
Pw (Erlang-C): 0.0017
```

### Cuadro de resultados

| Línea impresa por el programa | Valor |
|-------------------------------|-------|
| `Lambda (llegadas/min)` | `10.000000` |
| `Mu (servicios/min)` | `12.000000` |
| `Servidores` | `5.000000` |
| `Rho (utilizacion)` | `0.166667` |
| `P0 (sistema vacío)` | `0.434571` |
| `L (en sistema)` | `0.833683` |
| `Lq (en cola)` | `0.000349` |
| `W (tiempo en sistema)` | `0.083368` |
| `Wq (tiempo en cola)` | `0.000035` |
| `Pw (Erlang-C)` | `0.001746` |
| `W (horas) = 0.0834` | `5.00 minutos` |

---

## Corrida con c = 6 (sexto servidor)

### Comando

```bash
cd tarea1/calculator && python3 main.py --model mmc --servers 6 --lambda 10 --mu 12
```

Único cambio respecto de la corrida anterior: `--servers 6` en lugar de
`--servers 5`. λ y μ se mantienen.

### Salida del programa

```
M/M/6 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 10.000000
Mu (servicios/min): 12.000000
Servidores: 6.000000
Rho (utilizacion): 0.138889  rho = lambda / (c * mu)
P0 (sistema vacío): 0.434596
L (en sistema): 0.833371
Lq (en cola): 0.000038
W (tiempo en sistema): 0.083337
Wq (tiempo en cola): 0.000004
Pw (Erlang-C): 0.000235

Resumen:

M/M/6 Reporte
----------------
Lambda (llegadas/horas): 10.0000
Mu (servicios/horas): 12.0000
Servidores: 6
Factor de utilización (rho): 0.1389
P0 (sistema vacío): 0.4346
Lq (en cola): 0.0000
W (tiempo en sistema, horas): 0.0833
W (horas) = 0.0833 | 5.00 minutos
Pw (Erlang-C): 0.0002
```

### Cuadro de resultados

| Línea impresa por el programa | Valor |
|-------------------------------|-------|
| `Lambda (llegadas/min)` | `10.000000` |
| `Mu (servicios/min)` | `12.000000` |
| `Servidores` | `6.000000` |
| `Rho (utilizacion)` | `0.138889` |
| `P0 (sistema vacío)` | `0.434596` |
| `L (en sistema)` | `0.833371` |
| `Lq (en cola)` | `0.000038` |
| `W (tiempo en sistema)` | `0.083337` |
| `Wq (tiempo en cola)` | `0.000004` |
| `Pw (Erlang-C)` | `0.000235` |
| `W (horas) = 0.0833` | `5.00 minutos` |

---

## Comparativa c = 5 contra c = 6

Valores tal como los imprime el programa en cada corrida:

| Línea impresa | c = 5 | c = 6 |
|---------------|----------|----------|
| `Rho (utilizacion)` | `0.166667` | `0.138889` |
| `P0 (sistema vacío)` | `0.434571` | `0.434596` |
| `L (en sistema)` | `0.833683` | `0.833371` |
| `Lq (en cola)` | `0.000349` | `0.000038` |
| `W (tiempo en sistema)` | `0.083368` | `0.083337` |
| `Wq (tiempo en cola)` | `0.000035` | `0.000004` |
| `Pw (Erlang-C)` | `0.001746` | `0.000235` |
| `W (horas)` en minutos | `5.00 minutos` | `5.00 minutos` |

Diferencia entre ambas corridas:

| Medida | c = 5 | c = 6 | Diferencia |
|--------|----------|----------|------------|
| Rho | 0.166667 | 0.138889 | −0.027778 |
| P0 | 0.434571 | 0.434596 | +0.000025 |
| L | 0.833683 | 0.833371 | −0.000312 |
| Lq | 0.000349 | 0.000038 | −0.000311 |
| Wq (horas) | 0.000035 | 0.000004 | −0.000031 |
| W (horas) | 0.083368 | 0.083337 | −0.000031 |
| Pw (Erlang-C) | 0.001746 | 0.000235 | −0.001511 |

El programa reporta `5.00 minutos` en ambas corridas.
