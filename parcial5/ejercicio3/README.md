# Parcial V - Ejercicio 3: Problema de Volumen de Carga

**Universidad José Antonio Páez - Facultad de Ingeniería**
**Escuela de Ingeniería en Computación - Métodos Cuantitativos**

Programa de consola (CLI) que resuelve el **problema de volumen de carga**: un stand
de feria tiene una capacidad de 10 kg y hay que elegir qué productos llevar (cada uno
0 o 1 vez) para que el precio total sea el máximo.

## Datos del parcial

| Producto            | Peso (kg) | Precio ($) | Precio/kg |
|----------------------|-----------|------------|-----------|
| Tablet Samsung       | 2         | 40         | 20,00     |
| Dron DJI Mini        | 3         | 50         | 16,67     |
| Proyector portatil   | 4         | 65         | 16,25     |
| Laptop ASUS ZenBook  | 5         | 60         | 12,00     |

Capacidad: 10 kg.

## Explicación del modelo

**Variables:** `mi = 1` si el producto *i* entra en la carga, `0` si no.

```
Max Z = 40m1 + 50m2 + 65m3 + 60m4
s.a.  2m1 + 3m2 + 4m3 + 5m4 <= 10
      mi en {0, 1}
```

**Cómo lo resuelve el programa** (`src/core/volumen_carga.py`):

1. **Programación dinámica por etapas (método principal):** una etapa por producto
   *i* = 1..4 (en el orden del JSON), con estado *y* = capacidad disponible (0..10):
   ```
   f_0(y) = 0
   f_i(y) = max( f_{i-1}(y) ,  ri + f_{i-1}(y - wi) )   si wi <= y
   ```
   Es decir, el producto *i* se deja afuera (`mi = 0`) o se mete (`mi = 1`); en caso
   de empate se deja afuera. Después se reconstruye hacia atrás desde `y = 10` en la
   etapa 4 para saber qué productos entraron.
2. **Verificación con `scipy.optimize.milp`:** resuelve el mismo modelo binario y
   comprueba que el valor coincida.
3. **Enumeración completa:** calcula las 2⁴ = 16 combinaciones posibles con su peso,
   su precio y si son factibles, y de ahí saca las combinaciones óptimas.
4. **Heurística voraz:** mete los productos de mayor precio por kg mientras quepan.
   Sirve para mostrar que una regla rápida no siempre garantiza el óptimo (en este
   caso sí llega al óptimo, por el orden de precio/kg de los productos).

## Estructura

```text
ejercicio3/
├── main.py                          # CLI
├── ejercicio3.md                    # respuesta para transcribir a mano
├── requirements.txt
├── datos/productos.json             # productos (nombre, peso, precio) y capacidad
├── src/
│   ├── core/volumen_carga.py        # VolumenCarga: etapas, milp, voraz, enumeracion
│   └── services/reporter.py         # modelo, tablas, reconstruccion y resultado en texto
├── tests/test_volumen_carga.py      # pytest
└── outputs/reporte_ejercicio3.txt   # salida generada
```

## Instalación y ejecución

```bash
cd parcial5/ejercicio3
python3 -m pip install -r requirements.txt

python3 main.py                          # problema del parcial
python3 main.py --capacidad 14           # otra capacidad (entran los 4 productos)
python3 main.py --datos otros.json --sin-exportar

python3 -m pytest tests/ -q              # pruebas
```

## Salida por terminal

Salida de `python3 main.py` con los datos del parcial:

```text
$ python3 main.py
EJERCICIO 3 - PROBLEMA DE VOLUMEN DE CARGA
===========================================

MODELO
------
mi = 1 si el producto i entra en la carga, 0 si no
Max Z = 40m1 + 50m2 + 65m3 + 60m4
s.a.
  2m1 + 3m2 + 4m3 + 5m4 <= 10
  mi en {0, 1}

Producto                      Peso  Precio  Precio/kg
  1 Tablet Samsung                2      40     20.00
  2 Dron DJI Mini                 3      50     16.67
  3 Proyector portatil            4      65     16.25
  4 Laptop ASUS ZenBook           5      60     12.00

TABLAS POR ETAPA
-----------------

Etapa 1 - Tablet Samsung (peso 2 kg, precio $40)
f_1(y) = max{ f_0(y) , 40 + f_0(y - 2) }

   y  m=0    m=1    f_i(y)  m_i*
   0      0      -       0     0
   1      0      -       0     0
   2      0     40      40     1
   3      0     40      40     1
   4      0     40      40     1
   5      0     40      40     1
   6      0     40      40     1
   7      0     40      40     1
   8      0     40      40     1
   9      0     40      40     1
  10      0     40      40     1

Etapa 2 - Dron DJI Mini (peso 3 kg, precio $50)
f_2(y) = max{ f_1(y) , 50 + f_1(y - 3) }

   y  m=0    m=1    f_i(y)  m_i*
   0      0      -       0     0
   1      0      -       0     0
   2     40      -      40     0
   3     40     50      50     1
   4     40     50      50     1
   5     40     90      90     1
   6     40     90      90     1
   7     40     90      90     1
   8     40     90      90     1
   9     40     90      90     1
  10     40     90      90     1

Etapa 3 - Proyector portatil (peso 4 kg, precio $65)
f_3(y) = max{ f_2(y) , 65 + f_2(y - 4) }

   y  m=0    m=1    f_i(y)  m_i*
   0      0      -       0     0
   1      0      -       0     0
   2     40      -      40     0
   3     50      -      50     0
   4     50     65      65     1
   5     90     65      90     0
   6     90    105     105     1
   7     90    115     115     1
   8     90    115     115     1
   9     90    155     155     1
  10     90    155     155     1

Etapa 4 - Laptop ASUS ZenBook (peso 5 kg, precio $60)
f_4(y) = max{ f_3(y) , 60 + f_3(y - 5) }

   y  m=0    m=1    f_i(y)  m_i*
   0      0      -       0     0
   1      0      -       0     0
   2     40      -      40     0
   3     50      -      50     0
   4     65      -      65     0
   5     90     60      90     0
   6    105     60     105     0
   7    115    100     115     0
   8    115    110     115     0
   9    155    125     155     0
  10    155    150     155     0

TABLA RESUMEN
-------------
             0     1     2     3     4     5     6     7     8     9    10   <- y
f_0          0     0     0     0     0     0     0     0     0     0     0
f_1          0     0    40    40    40    40    40    40    40    40    40
f_2          0     0    40    50    50    90    90    90    90    90    90
f_3          0     0    40    50    65    90   105   115   115   155   155
f_4          0     0    40    50    65    90   105   115   115   155   155

RECONSTRUCCION
--------------
Etapa 4 (Laptop ASUS ZenBook): f_4(10) = f_3(10) = 155 -> m4 = 0, y = 10
Etapa 3 (Proyector portatil): f_3(10) = 65 + f_2(6) = 155 -> m3 = 1, y = 6
Etapa 2 (Dron DJI Mini): f_2(6) = 50 + f_1(3) = 90 -> m2 = 1, y = 3
Etapa 1 (Tablet Samsung): f_1(3) = 40 + f_0(1) = 40 -> m1 = 1, y = 1

RESULTADO
---------
Programacion dinamica: productos Tablet Samsung, Dron DJI Mini, Proyector portatil
  peso 9 kg | precio $155 | libre 1 kg
  m = (1, 1, 1, 0)
Verificacion milp:     productos Tablet Samsung, Dron DJI Mini, Proyector portatil | peso 9 kg | precio $155
Coinciden en valor: SI

Combinaciones optimas (precio $155): 1
  productos Tablet Samsung, Dron DJI Mini, Proyector portatil peso 9 kg (libres 1 kg)

ENUMERACION COMPLETA
---------------------
  Tablet Samsung, Dron DJI Mini, Proyector portatil, Laptop ASUS ZenBook  peso  14 kg  precio $ 215  EXCEDE
  Dron DJI Mini, Proyector portatil, Laptop ASUS ZenBook                  peso  12 kg  precio $ 175  EXCEDE
  Tablet Samsung, Proyector portatil, Laptop ASUS ZenBook                 peso  11 kg  precio $ 165  EXCEDE
  Tablet Samsung, Dron DJI Mini, Proyector portatil                       peso   9 kg  precio $ 155  FACTIBLE
  Tablet Samsung, Dron DJI Mini, Laptop ASUS ZenBook                      peso  10 kg  precio $ 150  FACTIBLE
  Proyector portatil, Laptop ASUS ZenBook                                 peso   9 kg  precio $ 125  FACTIBLE
  Dron DJI Mini, Proyector portatil                                       peso   7 kg  precio $ 115  FACTIBLE
  Dron DJI Mini, Laptop ASUS ZenBook                                      peso   8 kg  precio $ 110  FACTIBLE
  Tablet Samsung, Proyector portatil                                      peso   6 kg  precio $ 105  FACTIBLE
  Tablet Samsung, Laptop ASUS ZenBook                                     peso   7 kg  precio $ 100  FACTIBLE
  Tablet Samsung, Dron DJI Mini                                           peso   5 kg  precio $  90  FACTIBLE
  Proyector portatil                                                      peso   4 kg  precio $  65  FACTIBLE
  Laptop ASUS ZenBook                                                     peso   5 kg  precio $  60  FACTIBLE
  Dron DJI Mini                                                           peso   3 kg  precio $  50  FACTIBLE
  Tablet Samsung                                                          peso   2 kg  precio $  40  FACTIBLE
  ninguno                                                                 peso   0 kg  precio $   0  FACTIBLE

COMPARACION CON HEURISTICA VORAZ
---------------------------------
Heuristica voraz (mayor precio/kg): productos Tablet Samsung, Dron DJI Mini, Proyector portatil
  peso 9 kg | precio $155
Diferencia contra el optimo: $0

Reporte guardado en: outputs/reporte_ejercicio3.txt
```

## Resultado

**Precio máximo: $155.** Se logra con una única combinación óptima:

| Productos                                          | Peso  | Precio | Libre |
|-----------------------------------------------------|-------|--------|-------|
| Tablet Samsung, Dron DJI Mini, Proyector portatil    | 9 kg  | $155   | 1 kg  |

La verificación con `scipy.optimize.milp` confirma el mismo valor. La heurística
voraz (mayor precio/kg) elige los mismos tres productos y también llega a $155
(diferencia $0), porque el orden por precio/kg coincide con la solución óptima en
este caso. Con `--capacidad 14` caben los 4 productos y el precio sube a $215.

`outputs/reporte_ejercicio3.txt` es el archivo que se sube como .txt a Acrópolis.

Desarrollo para el examen y conclusión: `ejercicio3.md`.
