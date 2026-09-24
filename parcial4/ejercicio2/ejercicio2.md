# Ejercicio 2. Ramificación y acotamiento

## Modelo

```
Max Z = 80x1 + 45x2
s.a.
   x1 +  x2 <= 7
 12x1 + 5x2 <= 60
 x1, x2 >= 0 y enteras
```

## Solución en Python

Programa: `python3 main.py` (en esta carpeta). En cada nodo resuelve la relajación
lineal (linprog), ramifica sobre la primera variable fraccionaria y poda los nodos
infactibles o con Z <= la mejor solución entera.

## Nodos (salidas)

**P0 (relajación lineal):** se cortan x1 + x2 = 7 y 12x1 + 5x2 = 60
-> 12x1 + 5(7 - x1) = 60 -> 7x1 = 25
x1 = 3,57 ; x2 = 3,43 ; **Z = 440** (no es entera, se ramifica en x1)

**P1 (x1 <= 3):** x1 = 3 ; x2 = 4 ; **Z = 420** -> **entera**. Es la mejor por ahora (cota inferior = 420).

**P2 (x1 >= 4):** 12(4) + 5x2 = 60 -> x2 = 2,4
x1 = 4 ; x2 = 2,4 ; **Z = 428** (428 > 420, se ramifica en x2)

**P3 (x1 >= 4, x2 <= 2):** x1 = 50/12 = 4,17 ; x2 = 2 ; **Z = 423,33** (423,33 > 420, se ramifica en x1)

**P4 (x1 >= 4, x2 >= 3):** 12(4) + 5(3) = 63 > 60 -> **infactible**, se poda.

**P5 (x1 = 4, x2 <= 2):** x1 = 4 ; x2 = 2 ; **Z = 410** < 420 -> se poda.

**P6 (x1 >= 5, x2 <= 2):** x1 = 5 ; x2 = 0 ; **Z = 400** < 420 -> se poda.

## Árbol

```
                  P0: (3.57 , 3.43)  Z = 440
                 /                         \
            x1 <= 3                       x1 >= 4
               /                             \
  P1: (3 , 4)  Z = 420              P2: (4 , 2.4)  Z = 428
  ENTERA (mejor)                   /                  \
                              x2 <= 2                x2 >= 3
                                 /                       \
                P3: (4.17 , 2)  Z = 423.33          P4: INFACTIBLE
                 /                  \
            x1 <= 4               x1 >= 5
               /                      \
   P5: (4 , 2)  Z = 410       P6: (5 , 0)  Z = 400
   poda (410 < 420)           poda (400 < 420)
```

## Resultado

**x1 = 3 ; x2 = 4 ; Z máx = 420**

## Conclusión

La relajación lineal da Z = 440, pero con valores fraccionarios que no sirven.
Ramificando se llegó a la solución entera x1 = 3, x2 = 4, con Z = 420. Las demás
ramas se descartaron porque eran infactibles o daban un Z menor a 420. Por eso ese
es el óptimo. Se ve que la solución entera es peor que la relajada (420 < 440) y que
redondear la relajada, (4, 3), no era factible.
