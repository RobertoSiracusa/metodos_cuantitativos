# Ejercicio 3. Ubicación de estaciones (cubrimiento de conjuntos)

## Criterio

La tabla no es simétrica (ejemplo: de 1 a 8 = 20 min, de 8 a 1 = 70 min).
Se exige que la estación quede a 40 min o menos **en ida y en vuelta**:
la estación j cubre a la ciudad i si t(i,j) <= 40 **y** t(j,i) <= 40.

## Modelo

Variables: xj = 1 si se construye una estación en la ciudad j, 0 si no (j = 1..10)

```
Min Z = x1 + x2 + x3 + x4 + x5 + x6 + x7 + x8 + x9 + x10
s.a. (cada ciudad cubierta por al menos una estación)
 Ciudad 1:  x1 + x2 + x3 + x4 + x5 + x10      >= 1
 Ciudad 2:  x1 + x2 + x4 + x5 + x7 + x8 + x10 >= 1
 Ciudad 3:  x1 + x3 + x4 + x6 + x8            >= 1
 Ciudad 4:  x1 + x2 + x3 + x4 + x6 + x7 + x10 >= 1
 Ciudad 5:  x1 + x2 + x5 + x6 + x10           >= 1
 Ciudad 6:  x3 + x4 + x5 + x6 + x7 + x10      >= 1
 Ciudad 7:  x2 + x4 + x6 + x7 + x9            >= 1
 Ciudad 8:  x2 + x3 + x8 + x9                 >= 1
 Ciudad 9:  x7 + x8 + x9 + x10                >= 1
 Ciudad 10: x1 + x2 + x4 + x5 + x6 + x9 + x10 >= 1
 xj = 0 o 1
```

## Solución en Python

Programa: `python3 main.py` (en esta carpeta). Arma la matriz de cobertura
(a_ij = 1 si t(i,j) <= 40 y t(j,i) <= 40), resuelve el modelo binario con milp y
prueba todas las combinaciones para confirmar que con 2 estaciones no alcanza.

Salida: x2 = 1, x3 = 1, x9 = 1 (las demás en 0) ; **Z = 3**

## Resultado

**Mínimo 3 estaciones, en las ciudades 2, 3 y 9.**

| Estación | Ciudades que cubre (dentro de las 10) |
|----------|---------------------------------------|
| 2        | 1, 2, 4, 5, 7, 8, 10                  |
| 3        | 1, 3, 4, 6, 8                         |
| 9        | 7, 8, 9, 10                           |

## Conclusión

Con 3 estaciones (ciudades 2, 3 y 9) todas las ciudades quedan a 40 minutos o menos
de una estación, de ida y de vuelta. Con 2 estaciones no alcanza: se probaron todas
las combinaciones y ninguna cubre las 10 ciudades. El óptimo no es único: hay otras
combinaciones de 3 estaciones que también sirven (por ejemplo 1, 2 y 7, o 8, 9 y 10),
así que se puede elegir entre ellas por otro criterio, como el costo de construcción.
