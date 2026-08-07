**MM1 Calculator**

Calculadora POO para teoría de colas con soporte para M/M/1 y M/M/c.

**Descripción**: Este paquete calcula métricas operacionales de un sistema de colas con llegadas Poisson y tiempos de servicio exponenciales. Mantiene compatibilidad con el Ejercicio 1 (M/M/1) y agrega soporte para el Ejercicio 2 (M/M/c) usando una generalización del core.

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
