# Ejercicio 1. Verdadero o Falso

**a. Un modelo de programación entera puede tener restricciones lineales.**
**Verdadero.** Un modelo de programación entera es un modelo de programación lineal
al que se le exige que algunas o todas las variables sean enteras. Su función objetivo
y sus restricciones siguen siendo lineales (Programación Lineal Entera).

**b. El problema del viajero (TSP) puede formularse como un problema de programación entera.**
**Verdadero.** Se usan variables binarias x_ij = 1 si se viaja de la ciudad i a la j
(0 si no). Se minimiza la distancia total, con restricciones de entrar y salir una
sola vez de cada ciudad y restricciones que eliminan los subtours.

**c. Las soluciones de la programación lineal relajada siempre son válidas para la programación entera.**
**Falso.** La relajación lineal puede dar valores fraccionarios, que no sirven cuando
la variable debe ser entera. Sólo da una cota del óptimo entero. Ejemplo: en el
ejercicio 2 la relajación da x1 = 3,57 y x2 = 3,43. Además, redondear esa solución
puede dar un punto infactible o que no sea el óptimo.

**d. Los métodos exactos para resolver programación entera siempre garantizan la solución óptima.**
**Verdadero.** Los métodos exactos (ramificación y acotamiento, planos de corte,
ramificación y corte) exploran o descartan todas las soluciones posibles, así que al
terminar dan el óptimo. Su desventaja es el tiempo: en problemas grandes puede crecer
mucho.

**e. La programación entera puede resolverse con heurísticas cuando importa más la rapidez que la precisión.**
**Verdadero.** Las heurísticas (algoritmo voraz, búsqueda local, algoritmos genéticos,
etc.) encuentran rápido una solución buena, aunque no garantizan que sea la óptima.
Sirven cuando el problema es muy grande o se necesita la respuesta en poco tiempo.
