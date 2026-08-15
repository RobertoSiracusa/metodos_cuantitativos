# Parcial I — Ejercicio 2: Servidor web corporativo (M/D/1)

Universidad José Antonio Páez — Facultad de Ingeniería
Escuela de Ingeniería en Computación
Métodos Cuantitativos — Teoría de líneas de espera
Agosto 2026

Salidas de ejecución del programa. Modelo M/D/1 implementado en la clase
`MD1Model` de `tarea1/calculator/src/core/mg_model.py`.

---

## Parámetros de entrada

| Parámetro | Valor | Origen en el enunciado |
|-----------|-------|------------------------|
| λ | 10 | Llegadas cada 6 minutos → 60/6 = 10 por hora |
| μ | 12 | Servicio cada 5 minutos → 60/5 = 12 por hora |
| c | 1 | Un servidor web |
| σ | 0 | Servicio determinístico (lo fuerza el modelo `md1`) |

---

## Comando

Desde la raíz del repositorio `metodos_cuantitativos/`:

```bash
cd tarea1/calculator && python3 main.py --model md1 --lambda 10 --mu 12
```

| Argumento | Valor | Efecto |
|-----------|-------|--------|
| `--model` | `md1` | Selecciona `MD1Model` (M/D/1, σ = 0 forzado) |
| `--lambda` | `10` | Tasa de llegadas |
| `--mu` | `12` | Tasa de servicio |
| `--no-steps` | (opcional) | Omite el desarrollo paso a paso |

---

## Salida del programa

```
M/D/1 - Desarrollo paso a paso
--------------------------------
Paso 1 - Factor de utilizacion (rho)
  Formula:      rho = lambda / mu
  Sustitucion:  rho = 10.0000 / 12.0000
  Resultado:    rho = 0.833333

Paso 2 - Probabilidad de sistema vacio (P0)
  Formula:      P0 = 1 - rho
  Sustitucion:  P0 = 1 - 0.8333
  Resultado:    P0 = 0.166667

Paso 3 - Numero esperado en cola (Lq)
  Formula:      Lq = rho^2 / (2 * (1 - rho))
  Sustitucion:  Lq = 0.8333^2 / (2 * (1 - 0.8333))  [P-K con sigma = 0]
  Resultado:    Lq = 2.083333

Paso 4 - Numero esperado en sistema (L)
  Formula:      L = Lq + rho
  Sustitucion:  L = 2.0833 + 0.8333
  Resultado:    L = 2.916667

Paso 5 - Tiempo promedio en cola (Wq)
  Formula:      Wq = Lq / lambda
  Sustitucion:  Wq = 2.0833 / 10.0000
  Resultado:    Wq = 0.208333

Paso 6 - Tiempo promedio en sistema (W)
  Formula:      W = Wq + 1/mu
  Sustitucion:  W = 0.2083 + 1/12.0000
  Resultado:    W = 0.291667

M/D/1 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 10.000000
Mu (servicios/min): 12.000000
Servidores: 1.000000
Rho (utilizacion): 0.833333  rho = lambda / (c * mu)
P0 (sistema vacío): 0.166667
L (en sistema): 2.916667
Lq (en cola): 2.083333
W (tiempo en sistema): 0.291667
Wq (tiempo en cola): 0.208333
Sigma (desv. est. servicio): 0.000000
Cs^2 (coef. variacion^2): 0.000000

Resumen:

M/D/1 Reporte
----------------
Lambda (llegadas/minutos): 10.0000
Mu (servicios/minutos): 12.0000
Servidores: 1
Sigma (desv. est. del servicio): 0.0000
Cs^2 (coef. variación al cuadrado): 0.0000
Factor de utilización (rho): 0.8333
P0 (sistema vacío): 0.1667
Lq (en cola): 2.0833
L (en sistema): 2.9167
Wq (tiempo en cola, minutos): 0.2083
W (tiempo en sistema, minutos): 0.2917
```

### Cuadro de resultados

| Línea impresa por el programa | Valor |
|-------------------------------|-------|
| `Lambda (llegadas/min)` | `10.000000` |
| `Mu (servicios/min)` | `12.000000` |
| `Servidores` | `1.000000` |
| `Rho (utilizacion)` | `0.833333` |
| `P0 (sistema vacío)` | `0.166667` |
| `L (en sistema)` | `2.916667` |
| `Lq (en cola)` | `2.083333` |
| `W (tiempo en sistema)` | `0.291667` |
| `Wq (tiempo en cola)` | `0.208333` |
| `Sigma (desv. est. servicio)` | `0.000000` |
| `Cs^2 (coef. variacion^2)` | `0.000000` |

---

## Corridas adicionales

### Comandos

```bash
cd tarea1/calculator

# Reduccion del tiempo de servicio
python3 main.py --model md1 --lambda 10 --mu 13.333333 --no-steps   # 4.5 min
python3 main.py --model md1 --lambda 10 --mu 15        --no-steps   # 4.0 min
python3 main.py --model md1 --lambda 10 --mu 17.142857 --no-steps   # 3.5 min
python3 main.py --model md1 --lambda 10 --mu 20        --no-steps   # 3.0 min

# Segundo servidor
python3 main.py --model mdc --servers 2 --lambda 10 --mu 12 --no-steps

# Servicio exponencial
python3 main.py --model mm1 --lambda 10 --mu 12 --no-steps
```

### Salidas

```
M/D/1 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 10.000000
Mu (servicios/min): 13.333333
Servidores: 1.000000
Rho (utilizacion): 0.750000  rho = lambda / (c * mu)
P0 (sistema vacío): 0.250000
L (en sistema): 1.875000
Lq (en cola): 1.125000
W (tiempo en sistema): 0.187500
Wq (tiempo en cola): 0.112500
Sigma (desv. est. servicio): 0.000000
Cs^2 (coef. variacion^2): 0.000000

M/D/1 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 10.000000
Mu (servicios/min): 15.000000
Servidores: 1.000000
Rho (utilizacion): 0.666667  rho = lambda / (c * mu)
P0 (sistema vacío): 0.333333
L (en sistema): 1.333333
Lq (en cola): 0.666667
W (tiempo en sistema): 0.133333
Wq (tiempo en cola): 0.066667
Sigma (desv. est. servicio): 0.000000
Cs^2 (coef. variacion^2): 0.000000

M/D/1 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 10.000000
Mu (servicios/min): 17.142857
Servidores: 1.000000
Rho (utilizacion): 0.583333  rho = lambda / (c * mu)
P0 (sistema vacío): 0.416667
L (en sistema): 0.991667
Lq (en cola): 0.408333
W (tiempo en sistema): 0.099167
Wq (tiempo en cola): 0.040833
Sigma (desv. est. servicio): 0.000000
Cs^2 (coef. variacion^2): 0.000000

M/D/1 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 10.000000
Mu (servicios/min): 20.000000
Servidores: 1.000000
Rho (utilizacion): 0.500000  rho = lambda / (c * mu)
P0 (sistema vacío): 0.500000
L (en sistema): 0.750000
Lq (en cola): 0.250000
W (tiempo en sistema): 0.075000
Wq (tiempo en cola): 0.025000
Sigma (desv. est. servicio): 0.000000
Cs^2 (coef. variacion^2): 0.000000

M/D/2 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 10.000000
Mu (servicios/min): 12.000000
Servidores: 2.000000
Rho (utilizacion): 0.416667  rho = lambda / (c * mu)
P0 (sistema vacío): 0.411765
L (en sistema): 0.920868
Lq (en cola): 0.087535
W (tiempo en sistema): 0.092087
Wq (tiempo en cola): 0.008754
Sigma (desv. est. servicio): 0.000000
Cs^2 (coef. variacion^2): 0.000000
Nota: c > 1 con servicio general usa la aproximación de Allen-Cunneen.

M/M/1 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 10.000000
Mu (servicios/min): 12.000000
Servidores: 1.000000
Rho (utilizacion): 0.833333  rho = lambda / (c * mu)
P0 (sistema vacío): 0.166667
L (en sistema): 5.000000
Lq (en cola): 4.166667
W (tiempo en sistema): 0.500000
Wq (tiempo en cola): 0.416667
Pw (Erlang-C): 0.833333
P(n > 3): 0.482253  rho^(k+1) with k=3
```

