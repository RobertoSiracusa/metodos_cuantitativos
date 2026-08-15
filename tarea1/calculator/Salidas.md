

**Modelos soportados**:
- **M/M/1**: servidor único, fórmulas simplificadas.
- **M/M/c**: múltiples servidores en paralelo, incluyendo el cálculo de $P_0$, $L_q$, $W$, $W_q$ y Erlang-C.
- **M/G/1**: servidor único con tiempo de servicio de distribución general (fórmula exacta de Pollaczek-Khinchine).
- **M/G/c**: múltiples servidores con servicio general (aproximación de Allen-Cunneen).
- **M/D/1**: servidor único con servicio determinístico; caso particular de M/G/1 con $\sigma = 0$.
- **M/D/c**: múltiples servidores con servicio determinístico; caso particular de M/G/c con $\sigma = 0$.

**Fórmulas implementadas**:

M/M/1:
- **Factor de utilización**: $\rho = \dfrac{\lambda}{\mu}$
- **Probabilidad de sistema vacío**: $P_0 = 1 - \rho$
- **Número esperado en sistema**: $L = \dfrac{\rho}{1-\rho}$
- **Número esperado en cola**: $L_q = \dfrac{\rho^2}{1-\rho}$
- **Tiempo promedio en sistema**: $W = \dfrac{1}{\mu - \lambda}$
- **Tiempo promedio en cola**: $W_q = \dfrac{\lambda}{\mu(\mu-\lambda)}$
- **Probabilidad de más de k clientes**: $P(n>k)=\rho^{k+1}$

M/M/c:
- **Factor de utilización**: $\rho = \dfrac{\lambda}{c\mu}$
- **Probabilidad de sistema vacío**: $P_0 = \left[\sum_{n=0}^{c-1}\dfrac{(\lambda/\mu)^n}{n!} + \dfrac{(\lambda/\mu)^c}{c!}\left(\dfrac{1}{1-\rho}\right)\right]^{-1}$
- **Número esperado en cola**: $L_q = \dfrac{P_0(\lambda/\mu)^c\rho}{c!(1-\rho)^2}$
- **Tiempo promedio en cola**: $W_q = \dfrac{L_q}{\lambda}$
- **Tiempo promedio en sistema**: $W = W_q + \dfrac{1}{\mu}$
- **Probabilidad de esperar**: $P_w = \dfrac{(\lambda/\mu)^c}{c!}\left(\dfrac{1}{1-\rho}\right)P_0$

M/G/1 (exacto, Pollaczek-Khinchine), con $\sigma$ = desviación estándar del tiempo de servicio:
- **Factor de utilización**: $\rho = \dfrac{\lambda}{\mu}$
- **Probabilidad de sistema vacío**: $P_0 = 1 - \rho$
- **Número esperado en cola**: $L_q = \dfrac{\lambda^2\sigma^2 + \rho^2}{2(1-\rho)}$
- **Número esperado en sistema**: $L = L_q + \rho$
- **Tiempo promedio en cola**: $W_q = \dfrac{L_q}{\lambda}$
- **Tiempo promedio en sistema**: $W = W_q + \dfrac{1}{\mu}$

M/G/c (aproximación de Allen-Cunneen; M/G/c no tiene fórmula cerrada exacta):
- **Coeficiente de variación al cuadrado**: $C_s^2 = (\sigma\mu)^2$
- **Número esperado en cola**: $L_q \approx L_q^{M/M/c}\dfrac{1+C_s^2}{2}$
- $P_0$, $W_q$, $W$ y $L$ se derivan igual que en M/M/c. No se reporta $P_w$ (Erlang-C asume servicio exponencial).

M/D/1 y M/D/c: casos con $\sigma = 0$, o sea $C_s^2 = 0$.
- **M/D/1**: $L_q = \dfrac{\rho^2}{2(1-\rho)}$ — exactamente la mitad de M/M/1.
- **M/D/c**: $L_q \approx \dfrac{L_q^{M/M/c}}{2}$.

Salida esperada para el Ejercicio 1:

```text
M/M/1 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 0.500000
Mu (servicios/min): 1.200000
Servidores: 1.000000
Rho (utilizacion): 0.416667  rho = lambda / (c * mu)
P0 (sistema vacío): 0.583333
L (en sistema): 0.714286
Lq (en cola): 0.297619
W (tiempo en sistema): 1.428571
Wq (tiempo en cola): 0.595238
P(n>k) para k=5: 0.416667^6 = 0.004771
```

Salida esperada para el Ejercicio 2:

```text
M/M/3 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 15.000000
Mu (servicios/min): 6.000000
Servidores: 3.000000
Rho (utilizacion): 0.833333  rho = lambda / (c * mu)
P0 (sistema vacío): 0.044944
L (en sistema): 5.922736
Lq (en cola): 3.511236
W (tiempo en sistema): 0.400749
Wq (tiempo en cola): 0.233415
Pw (Erlang-C): 0.702247
```

Salida esperada para M/G/1 (`--model mg1 --lambda 0.5 --mu 1.2 --sigma 0.4`):

```text
M/G/1 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 0.500000
Mu (servicios/min): 1.200000
Servidores: 1.000000
Rho (utilizacion): 0.416667  rho = lambda / (c * mu)
P0 (sistema vacío): 0.583333
L (en sistema): 0.599762
Lq (en cola): 0.183095
W (tiempo en sistema): 1.199524
Wq (tiempo en cola): 0.366190
Sigma (desv. est. servicio): 0.400000
Cs^2 (coef. variacion^2): 0.230400
```

Salida esperada para M/G/c (`--model mgc --lambda 15 --mu 6 --servers 3 --sigma 0.1`):

```text
M/G/3 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 15.000000
Mu (servicios/min): 6.000000
Servidores: 3.000000
Rho (utilizacion): 0.833333  rho = lambda / (c * mu)
P0 (sistema vacío): 0.044944
L (en sistema): 4.887640
Lq (en cola): 2.387640
W (tiempo en sistema): 0.325843
Wq (tiempo en cola): 0.159176
Sigma (desv. est. servicio): 0.100000
Cs^2 (coef. variacion^2): 0.360000
```

Salida esperada para M/D/1 (`--model md1 --lambda 0.5 --mu 1.2`):

```text
M/D/1 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 0.500000
Mu (servicios/min): 1.200000
Servidores: 1.000000
Rho (utilizacion): 0.416667  rho = lambda / (c * mu)
P0 (sistema vacío): 0.583333
L (en sistema): 0.565476
Lq (en cola): 0.148810
W (tiempo en sistema): 1.130952
Wq (tiempo en cola): 0.297619
Sigma (desv. est. servicio): 0.000000
Cs^2 (coef. variacion^2): 0.000000
```

Salida esperada para M/D/c (`--model mdc --lambda 15 --mu 6 --servers 3`):

```text
M/D/3 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 15.000000
Mu (servicios/min): 6.000000
Servidores: 3.000000
Rho (utilizacion): 0.833333  rho = lambda / (c * mu)
P0 (sistema vacío): 0.044944
L (en sistema): 4.255618
Lq (en cola): 1.755618
W (tiempo en sistema): 0.283708
Wq (tiempo en cola): 0.117041
Sigma (desv. est. servicio): 0.000000
Cs^2 (coef. variacion^2): 0.000000
```
