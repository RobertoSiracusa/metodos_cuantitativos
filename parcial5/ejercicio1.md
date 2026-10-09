# Ejercicio 1. Verdadero o Falso

**a. Si un problema tiene subproblemas superpuestos pero no cumple con el principio de optimalidad, puede resolverse eficientemente con programación dinámica.**
**Falso.** La programación dinámica necesita las dos condiciones: subproblemas
superpuestos (para reutilizar resultados) y el principio de optimalidad de Bellman
(subestructura óptima). Sin este último, combinar las soluciones óptimas de los
subproblemas no garantiza la solución óptima del problema completo, así que la tabla
de la programación dinámica daría un resultado que puede no ser el óptimo. Ejemplo:
el camino simple más largo en un grafo con ciclos.

**b. El algoritmo de Floyd-Warshall para rutas más cortas aplica programación dinámica, evaluando todas las posibles rutas intermedias entre pares de nodos.**
**Verdadero.** Floyd-Warshall es programación dinámica: en la etapa k permite usar el
nodo k como intermedio y aplica
D_k[i][j] = min( D_{k-1}[i][j] , D_{k-1}[i][k] + D_{k-1}[k][j] ).
Al terminar las n etapas consideró todos los nodos como posibles intermedios para
cada par (i, j). No enumera las rutas una por una; las compara a través de la tabla,
con O(n³) operaciones.

**c. En un problema de volumen de carga, si todos los paquetes tienen pesos que son múltiplos de un mismo valor, se puede reducir el espacio de la tabla de programación dinámica sin afectar la solución óptima.**
**Verdadero.** Si todos los pesos son múltiplos de g, se dividen los pesos entre g y la
capacidad se reemplaza por ⌊W/g⌋. Las combinaciones factibles son las mismas, así
que la solución óptima no cambia, y la tabla tiene g veces menos columnas.
Ejemplo: pesos 2, 4 y 6 con W = 10 → pesos 1, 2 y 3 con W = 5.

**d. La programación dinámica puede adaptarse para resolver problemas de múltiples restricciones, como capacidad de peso y volumen simultáneamente.**
**Verdadero.** Se agrega una dimensión al estado por cada restricción:
f_i(p, v) = max{ f_{i-1}(p, v) , r_i + f_{i-1}(p − p_i, v − v_i) }.
La recurrencia es la misma; lo que crece es el tamaño de la tabla
(n × P × V), por eso sirve mientras las capacidades sean moderadas.

**e. La solución óptima de un problema de volumen de carga puede involucrar dejar espacio libre en la mochila.**
**Verdadero.** Los pesos son enteros y los productos son indivisibles, así que la
combinación de mayor valor no siempre llena la capacidad. Ejemplo: en el
ejercicio 3 el óptimo (Tablet + Dron + Proyector) pesa 9 kg y vale $155, y deja 1 kg
libre. La única combinación que usa los 10 kg (Tablet + Dron + Laptop) vale sólo $150.
