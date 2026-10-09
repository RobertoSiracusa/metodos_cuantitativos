# Parcial V - Ejercicio 2: Ruta más corta

**Universidad José Antonio Páez - Facultad de Ingeniería**
**Escuela de Ingeniería en Computación - Métodos Cuantitativos**

Programa de consola (CLI) que resuelve la **ruta más corta** de la oficina anterior
(nodo 1) a la oficina nueva (nodo 13) en un grafo no dirigido, por cuatro caminos
distintos: programación dinámica por etapas (hacia adelante y hacia atrás),
Floyd-Warshall y Bellman-Ford, verificados contra `scipy.sparse.csgraph.shortest_path`.

## Datos del parcial

| Nodo 1 | Nodo 2 | Peso |
|--------|--------|------|
| 1      | 2      | 100  |
| 1      | 3      | 50   |
| 1      | 4      | 40   |
| 3      | 4      | 20   |
| 2      | 5      | 100  |
| 3      | 5      | 100  |
| 4      | 6      | 100  |
| 5      | 6      | 40   |
| 5      | 7      | 120  |
| 5      | 8      | 130  |
| 6      | 9      | 100  |
| 7      | 8      | 50   |
| 8      | 9      | 100  |
| 7      | 10     | 60   |
| 8      | 10     | 70   |
| 9      | 11     | 100  |
| 10     | 12     | 200  |
| 10     | 13     | 100  |
| 11     | 12     | 50   |
| 12     | 13     | 100  |

**Etapas:** `[1] [2,3,4] [5,6] [7,8,9] [10,11] [12,13]`.

## Explicación de los métodos

**Programación dinámica por etapas (`src/core/etapas.py`):** el grafo está agrupado
en 6 etapas. Además del paso entre etapas consecutivas hay aristas dentro de una
misma etapa (3-4, 5-6, 7-8, 8-9, 12-13), así que después de evaluar los vecinos de
la etapa anterior/siguiente se relajan esas aristas internas hasta que no mejoren más.

- **Hacia adelante** (desde el nodo 1): `f_s(j) = min_i { f_(s-1)(i) + d(i,j) }`
- **Hacia atrás** (desde el nodo 13): `g_s(i) = min_j { d(i,j) + g_(s+1)(j) }`

**Floyd-Warshall** (`src/core/floyd_warshall.py`), todos los pares:

```
D_k[i][j] = min( D_(k-1)[i][j],  D_(k-1)[i][k] + D_(k-1)[k][j] )
```

**Bellman-Ford** (`src/core/bellman_ford.py`), un solo origen, hasta n-1 relajaciones
de todos los arcos (ambos sentidos) con corte anticipado si una pasada no cambia nada:

```
d_k(v) = min( d_(k-1)(v),  min_u { d_(k-1)(u) + w(u,v) } )
```

**Verificación:** `scipy.sparse.csgraph.shortest_path` con `method="FW"` y `method="BF"`
sobre la misma matriz de adyacencia, comparando `D[1][13]` contra los tres métodos propios.

## Estructura

```text
ejercicio2/
├── main.py                        # CLI
├── ejercicio2.md                  # respuesta para transcribir a mano
├── requirements.txt
├── datos/grafo.json               # nodos, aristas y etapas del parcial
├── src/
│   ├── core/
│   │   ├── grafo.py                # Grafo: no dirigido, valida nodos/aristas
│   │   ├── etapas.py               # RutaPorEtapas: recursion adelante y atras
│   │   ├── floyd_warshall.py       # FloydWarshall: todos los pares
│   │   └── bellman_ford.py         # BellmanFord: un origen, detecta ciclo negativo
│   └── services/reporter.py       # las 7 secciones del reporte, en texto
├── tests/test_rutas.py            # pytest
└── outputs/reporte_ejercicio2.txt # salida generada
```

## Instalación y ejecución

```bash
cd parcial5/ejercicio2
python3 -m pip install -r requirements.txt

python3 main.py                              # problema del parcial (1 -> 13)
python3 main.py --origen 2 --destino 9       # otro par de nodos
python3 main.py --datos otro_grafo.json --sin-exportar

python3 -m pytest tests/ -q                  # pruebas
```

## Salida por terminal

Salida de `python3 main.py` con los datos del parcial (secciones 2, 3 y 6 completas;
la matriz de Floyd-Warshall se recorta con `...`):

```text
$ python3 main.py
EJERCICIO 2 - RUTA MAS CORTA (PROGRAMACION DINAMICA)
====================================================

Parcial V - Ejercicio 2: oficina anterior (1) a oficina nueva (13)
Origen (oficina anterior): 1   Destino (oficina nueva): 13

Aristas (no dirigidas):
   1 - 2  : 100
   1 - 3  : 50
   1 - 4  : 40
   3 - 4  : 20
   2 - 5  : 100
   3 - 5  : 100
   4 - 6  : 100
   5 - 6  : 40
   5 - 7  : 120
   5 - 8  : 130
   6 - 9  : 100
   7 - 8  : 50
   8 - 9  : 100
   7 - 10 : 60
   8 - 10 : 70
   9 - 11 : 100
  10 - 12 : 200
  10 - 13 : 100
  11 - 12 : 50
  12 - 13 : 100

Etapas:
  Etapa 0: [1]
  Etapa 1: [2, 3, 4]
  Etapa 2: [5, 6]
  Etapa 3: [7, 8, 9]
  Etapa 4: [10, 11]
  Etapa 5: [12, 13]

RECURSION HACIA ADELANTE (desde el nodo 1)
------------------------------------------
f_s(j) = min_i { f_(s-1)(i) + d(i,j) }   (mas relajacion interna de la etapa)

Etapa 0:
  nodo 1:
    f(1) = 0   decision: -

Etapa 1:
  nodo 2:
    via 1: 0 + 100 = 100  <- min
    f(2) = 100   decision: 1
  nodo 3:
    via 1: 0 + 50 = 50  <- min
    f(3) = 50   decision: 1
  nodo 4:
    via 1: 0 + 40 = 40  <- min
    f(4) = 40   decision: 1

Etapa 2:
  nodo 5:
    via 2: 100 + 100 = 200
    via 3: 50 + 100 = 150  <- min
    f(5) = 150   decision: 3
  nodo 6:
    via 4: 40 + 100 = 140  <- min
    f(6) = 140   decision: 4

Etapa 3:
  nodo 7:
    via 5: 150 + 120 = 270  <- min
    f(7) = 270   decision: 5
  nodo 8:
    via 5: 150 + 130 = 280  <- min
    f(8) = 280   decision: 5
  nodo 9:
    via 6: 140 + 100 = 240  <- min
    f(9) = 240   decision: 6

Etapa 4:
  nodo 10:
    via 7: 270 + 60 = 330  <- min
    via 8: 280 + 70 = 350
    f(10) = 330   decision: 7
  nodo 11:
    via 9: 240 + 100 = 340  <- min
    f(11) = 340   decision: 9

Etapa 5:
  nodo 12:
    via 10: 330 + 200 = 530
    via 11: 340 + 50 = 390  <- min
    f(12) = 390   decision: 11
  nodo 13:
    via 10: 330 + 100 = 430  <- min
    f(13) = 430   decision: 10

Ruta (adelante) 1 -> 13: 1 -> 3 -> 5 -> 7 -> 10 -> 13
Costo total: 430

RECURSION HACIA ATRAS (desde el nodo 13)
----------------------------------------
g_s(i) = min_j { d(i,j) + g_(s+1)(j) }   (mas relajacion interna de la etapa)

Etapa 5:
  nodo 12:
    via 13: 0 + 100 = 100  <- min
    g(12) = 100   decision: 13
  nodo 13:
    g(13) = 0   decision: -

Etapa 4:
  nodo 10:
    via 12: 100 + 200 = 300
    via 13: 0 + 100 = 100  <- min
    g(10) = 100   decision: 13
  nodo 11:
    via 12: 100 + 50 = 150  <- min
    g(11) = 150   decision: 12

Etapa 3:
  nodo 7:
    via 10: 100 + 60 = 160  <- min
    g(7) = 160   decision: 10
  nodo 8:
    via 10: 100 + 70 = 170  <- min
    g(8) = 170   decision: 10
  nodo 9:
    via 11: 150 + 100 = 250  <- min
    g(9) = 250   decision: 11

Etapa 2:
  nodo 5:
    via 7: 160 + 120 = 280  <- min
    via 8: 170 + 130 = 300
    g(5) = 280   decision: 7
  nodo 6:
    via 9: 250 + 100 = 350
    via 5: 280 + 40 = 320  <- min
    g(6) = 320   decision: 5

Etapa 1:
  nodo 2:
    via 5: 280 + 100 = 380  <- min
    g(2) = 380   decision: 5
  nodo 3:
    via 5: 280 + 100 = 380  <- min
    g(3) = 380   decision: 5
  nodo 4:
    via 6: 320 + 100 = 420
    via 3: 380 + 20 = 400  <- min
    g(4) = 400   decision: 3

Etapa 0:
  nodo 1:
    via 2: 380 + 100 = 480
    via 3: 380 + 50 = 430  <- min
    via 4: 400 + 40 = 440
    g(1) = 430   decision: 3

Ruta (atras) 1 -> 13: 1 -> 3 -> 5 -> 7 -> 10 -> 13
Costo total: 430

BELLMAN-FORD (origen 1)
-----------------------
d_k(v) = min( d_(k-1)(v), min_u { d_(k-1)(u) + w(u,v) } )

Iteracion       1     2     3     4     5     6     7     8     9    10    11    12    13
1               0   100    50    40   150   140   270   280   240   330   340   390   430
2               0   100    50    40   150   140   270   280   240   330   340   390   430

Iteraciones hasta converger: 2

Ruta: 1 -> 3 -> 5 -> 7 -> 10 -> 13
Costo total: 430

FLOYD-WARSHALL
--------------
D_k[i][j] = min( D_(k-1)[i][j], D_(k-1)[i][k] + D_(k-1)[k][j] )

Matriz de distancias final (D):
           1     2     3     4     5     6     7     8     9    10    11    12    13
     1     0   100    50    40   150   140   270   280   240   330   340   390   430
     2   100     0   150   140   100   140   220   230   240   280   340   390   380
...
    13   430   380   380   400   280   320   160   170   250   100   150   100     0

Celdas (i, j) mejoradas por cada nodo intermedio k:
  k=1: 4 celdas
  ...
  k=13: 0 celdas

Ruta 1 -> 13: 1 -> 3 -> 5 -> 7 -> 10 -> 13
Costo total: 430

VERIFICACION
------------
scipy Floyd-Warshall: D[1][13] = 430   ruta: 1 -> 3 -> 5 -> 7 -> 10 -> 13
scipy Bellman-Ford:   D[1][13] = 430   ruta: 1 -> 3 -> 5 -> 7 -> 10 -> 13
scipy FW y BF dan el mismo D[1][13]: SI

Metodo           |    Distancia 1->13 | Ruta
Etapas (DP)      |                430 | 1 -> 3 -> 5 -> 7 -> 10 -> 13
Floyd-Warshall   |                430 | 1 -> 3 -> 5 -> 7 -> 10 -> 13
Bellman-Ford     |                430 | 1 -> 3 -> 5 -> 7 -> 10 -> 13
scipy (FW/BF)    |                430 | 1 -> 3 -> 5 -> 7 -> 10 -> 13

Coinciden: SI

COMPLEJIDAD
-----------
n = 13 nodos, m = 20 aristas no dirigidas (40 arcos dirigidos)
Floyd-Warshall: O(n^3) = 13^3 = 2197 operaciones basicas
Bellman-Ford:   O(n*m) = 13*40 = 520 en el peor caso; esta corrida convergio en 2 iteraciones (80 relajaciones reales)
Floyd-Warshall conviene cuando se necesitan TODOS los pares de distancias; Bellman-Ford conviene para un solo origen y, a diferencia de Dijkstra, admite pesos negativos en grafos dirigidos (aqui no aplica: el grafo es no dirigido y los pesos son todos > 0).

Reporte guardado en: outputs/reporte_ejercicio2.txt
```

## Resultado

**Ruta más corta de la oficina anterior (1) a la oficina nueva (13): `1 -> 3 -> 5 -> 7 -> 10 -> 13`,
costo 430.** Los cuatro métodos (programación dinámica por etapas, Floyd-Warshall,
Bellman-Ford y `scipy`) coinciden exactamente en la ruta y en el costo.

| Método              | Distancia 1->13 | Ruta                        |
|---------------------|------------------|-----------------------------|
| Etapas (DP)         | 430              | 1 -> 3 -> 5 -> 7 -> 10 -> 13 |
| Floyd-Warshall      | 430              | 1 -> 3 -> 5 -> 7 -> 10 -> 13 |
| Bellman-Ford        | 430              | 1 -> 3 -> 5 -> 7 -> 10 -> 13 |
| scipy (FW/BF)       | 430              | 1 -> 3 -> 5 -> 7 -> 10 -> 13 |

Desarrollo para el examen: `ejercicio2.md`.
