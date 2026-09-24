# Ejercicio 4. Problema de la mochila

## Modelo

Variables: xi = 1 si el objeto i entra en la mochila, 0 si no (i = 1..6)

```
Max Z = 60x1 + 100x2 + 90x3 + 120x4 + 150x5 + 80x6
s.a.
 10x1 + 20x2 + 15x3 + 25x4 + 30x5 + 12x6 <= 50
 xi = 0 o 1
```

## Solución en Python

Programa: `python3 main.py` (en esta carpeta). Lo resuelve por programación
dinámica, F[i][c] = max(F[i-1][c], F[i-1][c - wi] + vi), y verifica el resultado
con milp.

Salida: Z = 270, con dos combinaciones posibles (objetos 2, 3, 6 u objetos 1, 3, 4)

## Resultado

**Objetos 2, 3 y 6 -> peso = 20 + 15 + 12 = 47 kg ; valor = 100 + 90 + 80 = $270**

Hay otro óptimo con el mismo valor: objetos 1, 3 y 4 -> 50 kg y $270.

## Conclusión

El valor máximo que cabe en la mochila es $270. Una forma de lograrlo es llevar los
objetos 2, 3 y 6, que pesan 47 kg y dejan 3 kg libres. La otra es llevar los objetos
1, 3 y 4, que usan los 50 kg completos. Conviene la primera porque da el mismo valor
con menos peso. Llevar primero los de mejor valor por kg (6, 1 y 3) sólo da $230, así
que el método voraz no garantiza el óptimo y hace falta la programación entera.
