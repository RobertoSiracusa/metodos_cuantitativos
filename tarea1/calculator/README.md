**MM1 Calculator**

Calculadora POO para teoría de colas con soporte para M/M/1, M/M/c, M/D/1, M/D/c, M/G/1 y M/G/c.

**Descripción**: Este paquete calcula métricas operacionales de un sistema de colas con llegadas Poisson. Mantiene compatibilidad con el Ejercicio 1 (M/M/1) y el Ejercicio 2 (M/M/c), y agrega modelos con tiempo de servicio determinístico (M/D) y general (M/G) usando una generalización del core.

**Requisitos**: Python 3.8+ (no hay dependencias externas requeridas).

**Instalación y ejecución**:
- Clona o sitúa el folder `calculator` en el directorio de trabajo.
- Ejecuta desde la raíz del repositorio o desde `tarea1` usando los comandos indicados más abajo.

**Ejecutar pruebas**:
```bash
cd tarea1/calculator
pytest
```

**Modelos soportados**:
- **M/M/1**: servidor único, fórmulas simplificadas.
- **M/M/c**: múltiples servidores en paralelo, incluyendo el cálculo de $P_0$, $L_q$, $W$, $W_q$ y Erlang-C.
- **M/G/1**: servidor único con servicio de distribución general (exacto, Pollaczek-Khinchine).
- **M/G/c**: múltiples servidores con servicio general (aproximación de Allen-Cunneen).
- **M/D/1** y **M/D/c**: servicio determinístico, casos con $\sigma = 0$ de los anteriores.

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
- **Intensidad de tráfico**: $a = \dfrac{\lambda}{\mu}$
- **Probabilidad de sistema vacío**: $P_0 = \left[\sum_{n=0}^{c-1}\dfrac{(\lambda/\mu)^n}{n!} + \dfrac{(\lambda/\mu)^c}{c!}\left(\dfrac{1}{1-\rho}\right)\right]^{-1}$
- **Número esperado en cola**: $L_q = \dfrac{P_0(\lambda/\mu)^c\rho}{c!(1-\rho)^2}$
- **Número esperado en sistema**: $L = L_q + a$
- **Tiempo promedio en cola**: $W_q = \dfrac{L_q}{\lambda}$
- **Tiempo promedio en sistema**: $W = W_q + \dfrac{1}{\mu}$
- **Probabilidad de esperar**: $P_w = \dfrac{(\lambda/\mu)^c}{c!}\left(\dfrac{1}{1-\rho}\right)P_0$

M/G/1 (exacto, Pollaczek-Khinchine):
- **Factor de utilización**: $\rho = \dfrac{\lambda}{\mu}$
- **Probabilidad de sistema vacío**: $P_0 = 1 - \rho$
- **Número esperado en cola**: $L_q = \dfrac{\lambda^2\sigma^2 + \rho^2}{2(1-\rho)}$
- **Número esperado en sistema**: $L = L_q + \rho$
- **Tiempo promedio en cola**: $W_q = \dfrac{L_q}{\lambda}$
- **Tiempo promedio en sistema**: $W = W_q + \dfrac{1}{\mu}$

M/G/c (aproximación de Allen-Cunneen; no tiene fórmula cerrada exacta):
- **Factor de utilización**: $\rho = \dfrac{\lambda}{c\mu}$
- **Intensidad de tráfico**: $a = \dfrac{\lambda}{\mu}$
- **Coeficiente de variación al cuadrado**: $C_s^2 = (\sigma\mu)^2$
- **Probabilidad de sistema vacío**: igual que M/M/c
- **$L_q$ equivalente de M/M/c**: igual que M/M/c
- **Número esperado en cola**: $L_q \approx L_q^{(M/M/c)}\cdot\dfrac{1+C_s^2}{2}$
- **Número esperado en sistema**: $L = L_q + a$
- **Tiempo promedio en cola**: $W_q = \dfrac{L_q}{\lambda}$
- **Tiempo promedio en sistema**: $W = W_q + \dfrac{1}{\mu}$

M/D/1 (caso $\sigma = 0$ de M/G/1):
- **Número esperado en cola**: $L_q = \dfrac{\rho^2}{2(1-\rho)}$ (mitad de M/M/1)
- El resto de las fórmulas ($P_0$, $L$, $W_q$, $W$) son las mismas de M/G/1.

M/D/c (caso $\sigma = 0$ de M/G/c, es decir $C_s^2 = 0$):
- **Número esperado en cola**: $L_q \approx \dfrac{L_q^{(M/M/c)}}{2}$
- El resto de las fórmulas ($\rho$, $a$, $P_0$, $L$, $W_q$, $W$) son las mismas de M/G/c.

Para todos los modelos, `Pw` (Erlang-C) no se reporta con servicio general (M/G, M/D) porque asume
servicio exponencial.

**Ejemplo de ejecución**

Desde la raíz del workspace:

```bash
python -m calculator.main
```

Para ejecutar el Ejercicio 2 con tres servidores:

```bash
python calculator/main.py --exercise 2 --servers 3 --lambda 15.0 --mu 6.0
```

También puedes ejecutar el Ejercicio 2 solo con el selector del ejercicio:

```bash
python calculator/main.py --exercise 2
```

En ese caso la CLI usa automáticamente los valores por defecto del Ejercicio 2: `lambda=15.0`, `mu=6.0` y `servers=3`.

### Flags de la CLI

| Flag | Tipo | Default | Qué hace |
|------|------|---------|----------|
| `--model` | `mm1`, `mmc`, `md1`, `mdc`, `mg1`, `mgc` | deducido de `--exercise` / `--servers` | Modelo de cola a usar |
| `--lambda` | float | `0.8` | Tasa de llegada |
| `--mu` | float | `1.0` | Tasa de servicio |
| `--servers` | int | `1` | Número de servidores (`c`). Ignorado en `md1` y `mg1` |
| `--sigma` | float | `0.0` | Desviación estándar del tiempo de servicio. Sólo tiene efecto en `mg1` y `mgc`; en `md1` y `mdc` se acepta pero se fuerza a `0` (el servicio determinístico no tiene variabilidad por definición) |
| `--k` | int | `3` | Valor de `k` para `P(n > k)`. Sólo M/M/1 |
| `--exercise` | `1`, `2` | `1` | Atajo a los datos del Ejercicio 1 o 2 |

### Servicio determinístico y general (M/D/1, M/D/c, M/G/1, M/G/c)

Se seleccionan con `--model`. `--sigma` es la desviación estándar del tiempo de
servicio (en unidades de tiempo, no de tasa); sólo aplica a los modelos M/G.
Con `sigma = 1/mu` los modelos M/G reproducen exactamente M/M.

```bash
# M/D/1 - servicio determinístico, un servidor
python calculator/main.py --model md1 --lambda 0.5 --mu 1.2

# M/D/c - servicio determinístico, tres servidores
python calculator/main.py --model mdc --lambda 15 --mu 6 --servers 3

# M/G/1 - servicio general, sigma = 0.4 minutos
python calculator/main.py --model mg1 --lambda 0.5 --mu 1.2 --sigma 0.4

# M/G/c - servicio general, tres servidores, sigma = 0.1 minutos
python calculator/main.py --model mgc --lambda 15 --mu 6 --servers 3 --sigma 0.1
```

Las salidas completas de estos cuatro comandos están en `Salidas.md`. Las fórmulas de todos los
modelos están en la sección **Fórmulas implementadas** más arriba.

`L`, `W` y `Wq` se derivan por Little (`Wq = Lq / lambda`, `W = Wq + 1/mu`, `L = Lq + lambda/mu`).

### Desarrollo paso a paso

Por default, la CLI imprime el desarrollo completo antes del resumen: para cada métrica muestra la
fórmula, la sustitución numérica y el resultado. Se desactiva con `--no-steps` (vuelve a la salida
compacta de antes). Ejemplo real (`python calculator/main.py --model mmc --lambda 15 --mu 6 --servers 3`):

```text
M/M/3 - Desarrollo paso a paso
--------------------------------
Paso 1 - Factor de utilizacion (rho)
  Formula:      rho = lambda / (c * mu)
  Sustitucion:  rho = 15.0000 / (3 * 6.0000)
  Resultado:    rho = 0.833333

Paso 2 - Intensidad de trafico (a)
  Formula:      a = lambda / mu
  Sustitucion:  a = 15.0000 / 6.0000
  Resultado:    a = 2.500000

Paso 3 - Probabilidad de sistema vacio (P0)
  Formula:      P0 = [ sum_{n=0}^{c-1} a^n/n! + (a^c/c!) * (1/(1-rho)) ]^-1
  Sustitucion:  P0 = [ 6.6250 + 15.6250 ]^-1
  Resultado:    P0 = 0.044944
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

Nota: el reporte también muestra el tiempo en horas y su equivalente en minutos en la salida compacta del servicio.

**Comandos a usar**

```bash
# Ejecutar el Ejercicio 1 con los valores por defecto
python calculator/main.py

# Ejecutar el Ejercicio 1 con parámetros personalizados
python calculator/main.py --lambda 0.5 --mu 1.2 --k 5

# Ejecutar el Ejercicio 2 con los valores por defecto del caso
python calculator/main.py --exercise 2

# Ejecutar el Ejercicio 2 indicando explícitamente los parámetros
python calculator/main.py --exercise 2 --servers 3 --lambda 15.0 --mu 6.0
```

**Cómo cambiar los parámetros**: Puedes pasar parámetros por línea de comandos. El modo por defecto sigue usando el Ejercicio 1.

Ejemplos de uso:

```bash
# Ejercicio 1 con valores por defecto
python calculator/main.py

# Ejercicio 1 con parámetros personalizados
python calculator/main.py --lambda 0.5 --mu 1.2 --k 5

# Ejercicio 2 con 3 servidores
python calculator/main.py --exercise 2 --servers 3 --lambda 15.0 --mu 6.0
```

También puedes importar y usar directamente los modelos desde otro script:

```python
from src.core.mm1_model import MM1Model
from src.core.mmc_model import MMCModel

mm1 = MM1Model(0.8, 1.0)
mmc = MMCModel(15.0, 6.0, 3)
```

**Estructura del proyecto**

- `calculator/main.py` — Punto de entrada que permite ejecutar M/M/1 o M/M/c.
- `calculator/src/core/mm1_model.py` — Implementación compatible con el modelo M/M/1.
- `calculator/src/core/mmc_model.py` — Implementación general para M/M/c.
- `calculator/src/services/reporter.py` — Servicio para formatear la salida de ambos ejercicios.
- `calculator/src/utils/validators.py` — Validaciones de entrada, número de servidores y estabilidad del sistema.
- `calculator/tests/test_mmc_model.py` — Prueba del Ejercicio 2.

**Notas**:
- El sistema valida que la carga sea estable: $\rho < 1$.
- Para M/M/c el número de servidores debe ser un entero mayor o igual a 1.
- No se requieren dependencias externas adicionales para usar el paquete.
