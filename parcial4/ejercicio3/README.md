# Parcial IV - Ejercicio 3: Ubicación de Estaciones (Cubrimiento de Conjuntos)

**Universidad José Antonio Páez - Facultad de Ingeniería**
**Escuela de Ingeniería en Computación - Métodos Cuantitativos**

Programa de consola (CLI) que calcula el **mínimo de estaciones** que hay que
construir para que cada una de las 10 ciudades tenga una estación a 40 minutos o
menos. Es un problema de **cubrimiento de conjuntos** (*set covering*) con
variables binarias.

## Enunciado resumido

- 10 ciudades. La tabla da el tiempo `t(i, j)` para ir de la ciudad *i* a la *j*.
- **La tabla no es simétrica**: de 1 a 8 son 20 min, pero de 8 a 1 son 70 min.
- Criterio adoptado: la estación debe estar a 40 min o menos **de ida y de vuelta**.

## Explicación del modelo

**Variables:** `xj = 1` si se construye una estación en la ciudad *j*, `0` si no.

**Matriz de cobertura:** `a_ij = 1` si una estación en *j* cubre a la ciudad *i*:

```
a_ij = 1   si  t(i, j) <= 40   y   t(j, i) <= 40
```

**Modelo:**

```
Min Z = x1 + x2 + ... + x10              (cantidad de estaciones)
s.a.  sum_j a_ij * xj >= 1   para cada ciudad i   (toda ciudad queda cubierta)
      xj en {0, 1}
```

Cada restricción dice: "de las ciudades que pueden servir a la ciudad *i*, al
menos una tiene estación".

**Cómo lo resuelve el programa** (`src/core/set_covering.py`):
1. Construye `a_ij` a partir de la tabla, el límite y el sentido elegido.
2. Verifica que ninguna ciudad quede sin opciones. Si pasa, el problema es infactible.
3. Resuelve el modelo binario con `scipy.optimize.milp`.
4. Prueba todas las combinaciones del tamaño mínimo para listar los **óptimos
   alternativos**, y demuestra que con una estación menos no alcanza.

## Estructura

```text
ejercicio3/
├── main.py                        # CLI
├── ejercicio3.md                  # respuesta para transcribir a mano
├── requirements.txt
├── datos/tiempos.json             # tabla 10x10 del parcial y límite (40)
├── src/
│   ├── core/set_covering.py       # ModeloCubrimiento: cobertura, milp, enumeración
│   └── services/reporter.py       # modelo, resultado y asignación en texto
├── tests/test_set_covering.py     # pytest
└── outputs/reporte_ejercicio3.txt # salida generada
```

## Instalación y ejecución

```bash
cd parcial4/ejercicio3
python3 -m pip install -r requirements.txt

python3 main.py                                # parcial: 40 min, ida y vuelta
python3 main.py --sentido ciudad_a_estacion    # sólo t(ciudad -> estación) <= 40
python3 main.py --sentido estacion_a_ciudad    # sólo t(estación -> ciudad) <= 40
python3 main.py --limite 30                    # otro límite
python3 main.py --datos otra_tabla.json --sin-exportar

python3 -m pytest tests/ -q                    # pruebas
```

## Resultado

**Mínimo: 3 estaciones, en las ciudades 2, 3 y 9.**

| Estación | Ciudades que cubre     |
|----------|------------------------|
| 2        | 1, 2, 4, 5, 7, 8, 10   |
| 3        | 1, 3, 4, 6, 8          |
| 9        | 7, 8, 9, 10            |

- Con 2 estaciones no hay forma de cubrir las 10 ciudades.
- Hay **48 combinaciones óptimas** de 3 estaciones, por ejemplo {1, 2, 7} y
  {8, 9, 10}. El reporte las lista todas.
- Sensibilidad al criterio: si el límite se mide en un solo sentido, basta **1
  estación**. En sentido ciudad -> estación va en la ciudad 8, y en sentido
  estación -> ciudad, en la ciudad 10.

Conclusión y desarrollo para el examen: `ejercicio3.md`.
