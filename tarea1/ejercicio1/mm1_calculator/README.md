**MM1 Calculator**

Calculadora simple para el modelo M/M/1 implementada en Python usando POO.

**Descripción**: Este paquete calcula las métricas operacionales clásicas de una cola M/M/1 (servidor único, llegadas Poisson, tiempos de servicio exponenciales) usando los parámetros de llegada (`lambda`) y servicio (`mu`). El código sigue un diseño top-down y está ubicado en la carpeta del ejercicio.

**Fórmulas implementadas**:
- **Factor de utilización**:  $\rho = \dfrac{\lambda}{\mu}$
- **Probabilidad servidor ocioso**: $P_0 = 1 - \rho$
- **Número esperado en sistema**: $L = \dfrac{\rho}{1-\rho}$
- **Número esperado en cola**: $L_q = \dfrac{\rho^2}{1-\rho}$
- **Tiempo promedio en sistema**: $W = \dfrac{1}{\mu - \lambda}$ (minutos)
- **Tiempo promedio en cola**: $W_q = \dfrac{\lambda}{\mu(\mu-\lambda)}$ (minutos)
- **Probabilidad de más de k clientes**: $P(n>k)=\rho^{k+1}$

**Ejemplo de ejecución**

```bash
# Desde la raíz del workspace
python -m tarea1.ejercicio1.mm1_calculator.main
```

Salida por defecto (para $\lambda=0.8$, $\mu=1.0$, $k=3$):

M/M/1 - Resultados detallados
--------------------------------
Lambda (llegadas/min): 0.800000
Mu (servicios/min): 1.000000
Rho (utilizacion): 0.800000  rho = lambda / mu
P0 (servidor ocioso): 0.200000  P0 = 1 - rho
L (en sistema): 4.000000  L = rho / (1 - rho)
Lq (en cola): 3.200000  Lq = rho^2 / (1 - rho)
W (tiempo en sistema, min): 5.000000  W = 1 / (mu - lambda)
Wq (tiempo en cola, min): 4.000000  Wq = lambda / (mu * (mu - lambda))
P(n > 3): 0.409600  rho^(k+1) with k=3

Resumen:

M/M/1 Reporte
---------------
Lambda (llegadas/min): 0.8000
Mu (servicios/min): 1.0000
Factor de utilización (rho): 0.8000
P0 (servidor ocioso): 0.2000
L (en sistema): 4.0000
Lq (en cola): 3.2000
W (tiempo en sistema, min): 5.0000
Wq (tiempo en cola, min): 4.0000
P(n > 3): 0.409600

**Cómo cambiar los parámetros**: Puedes pasar parámetros por línea de comandos. Por defecto los datos de ejemplo son usados (`lambda=0.8`, `mu=1.0`).

Ejemplos de uso:

```bash
# Usar los valores por defecto (lambda=0.8, mu=1.0)
python tarea1/ejercicio1/mm1_calculator/main.py

# Especificar lambda y mu desde la CLI
python tarea1/ejercicio1/mm1_calculator/main.py --lambda 0.5 --mu 1.2

# Cambiar k para P(n>k)
python tarea1/ejercicio1/mm1_calculator/main.py --lambda 0.8 --mu 1.0 --k 5
```

Internamente también puedes importar y usar `src.core.mm1_model.MM1Model` desde otro script si deseas integrar el modelo en tu código.

**Estructura del proyecto**

- `tarea1/ejercicio1/mm1_calculator/main.py` — Punto de entrada que construye el modelo y muestra el reporte.
- `tarea1/ejercicio1/mm1_calculator/src/core/mm1_model.py` — Implementación de la clase `MM1Model` con las fórmulas.
- `tarea1/ejercicio1/mm1_calculator/src/services/reporter.py` — Servicio para formatear la salida.
- `tarea1/ejercicio1/mm1_calculator/src/utils/validators.py` — Validaciones de entrada (tasas positivas y estabilidad).
- `.gitignore` — Reglas para ignorar archivos generados.

**Notas**:
- El modelo valida que `0 < \lambda < \mu` y lanzará un error si el sistema es inestable.
- No dependencias externas son necesarias para el uso básico del paquete.

Si quieres que añada soporte para parámetros por línea de comandos (`--lambda`, `--mu`) o que genere un pequeño script `example.py` para pruebas rápidas, dime y lo implemento.
