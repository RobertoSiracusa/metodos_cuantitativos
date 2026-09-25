# Parcial IV - Ejercicio 2: Ramificación y Acotamiento

**Universidad José Antonio Páez - Facultad de Ingeniería**
**Escuela de Ingeniería en Computación - Métodos Cuantitativos**

Programa de consola (CLI) que resuelve un problema de programación lineal entera
por ramificación y acotamiento (*Branch and Bound*). Muestra cada nodo, la rama
que lo generó, su solución y por qué se ramifica o se poda, y dibuja el árbol.

## Problema del parcial

```
Max Z = 80x1 + 45x2
s.a.
   x1 +  x2 <= 7
 12x1 + 5x2 <= 60
 x1, x2 >= 0 y enteras
```

## Explicación del método

1. **Relajación lineal (P0):** se resuelve el problema sin exigir enteros. Su Z es
   una cota superior del óptimo entero.
2. **Ramificación:** si alguna variable sale fraccionaria (ej. x1 = 3,57), se parte
   el problema en dos: una rama con `x1 <= 3` y otra con `x1 >= 4`. El valor
   fraccionario queda fuera de las dos ramas y no se pierde ninguna solución entera.
3. **Acotamiento (poda):** un nodo se descarta si
   - es **infactible**;
   - su Z es **menor o igual** que la mejor solución entera encontrada, porque
     ramificarlo sólo daría soluciones peores;
   - su solución ya es **entera**. En ese caso se guarda como la mejor, si mejora
     a la anterior.
4. Se sigue hasta que no queden nodos abiertos. La mejor solución entera guardada
   es el óptimo.

Reglas del programa:
- ramifica sobre la **primera variable fraccionaria** (x1, después x2);
- explora **en profundidad**, primero la rama `<=`;
- los nodos se numeran en el orden en que se crean.

La relajación de cada nodo se resuelve con `scipy.optimize.linprog`. La ramificación,
la poda y el árbol están programados en `src/core/branch_and_bound.py`.

## Estructura

```text
ejercicio2/
├── main.py                        # CLI
├── ejercicio2.md                  # respuesta para transcribir a mano
├── requirements.txt
├── datos/problema.json            # c, A y b del parcial
├── src/
│   ├── core/branch_and_bound.py   # ModeloBranchAndBound: nodos, ramificación, poda
│   └── services/reporter.py       # modelo, tabla de nodos, árbol y resultado en texto
├── tests/test_branch_and_bound.py # pytest: relajación, árbol, óptimo, contraste con milp
└── outputs/reporte_ejercicio2.txt # salida generada
```

## Instalación y ejecución

```bash
cd parcial4/ejercicio2
python3 -m pip install -r requirements.txt

python3 main.py                        # resuelve el problema del parcial
python3 main.py --sin-exportar         # sólo muestra en pantalla
python3 main.py --datos mi_problema.json

python3 -m pytest tests/ -q            # pruebas
```

Formato de `--datos` (maximización con restricciones `<=` y variables `>= 0`):

```json
{ "c": [80, 45], "A": [[1, 1], [12, 5]], "b": [7, 60] }
```

## Salida por terminal

Salida de `python3 main.py` con los datos del parcial:

```text
$ python3 main.py
EJERCICIO 2 - RAMIFICACION Y ACOTAMIENTO
========================================

MODELO
------
Max Z = 80x1 + 45x2
s.a.
  x1 + x2 <= 7
  12x1 + 5x2 <= 60
  x1, x2 >= 0 y enteras

NODOS (en orden de exploracion)
-------------------------------
P0  [relajacion lineal]  x = (3.5714, 3.4286)  Z = 440  -> RAMIFICADO en x1 = 3.5714
P1  [x1 <= 3]  x = (3, 4)  Z = 420  -> ENTERA (mejor solucion hasta ahora)
P2  [x1 >= 4]  x = (4, 2.4)  Z = 428  -> RAMIFICADO en x2 = 2.4000
P3  [x2 <= 2]  x = (4.1667, 2)  Z = 423.3333  -> RAMIFICADO en x1 = 4.1667
P5  [x1 <= 4]  x = (4, 2)  Z = 410  -> PODADO (Z = 410.00 <= 420.00)
P6  [x1 >= 5]  x = (5, 0)  Z = 400  -> PODADO (Z = 400.00 <= 420.00)
P4  [x2 >= 3]  infactible  -> INFACTIBLE

ARBOL
-----
P0 (3.5714, 3.4286) Z=440  RAMIFICADO en x1 = 3.5714
|-- [x1 <= 3] P1 (3, 4) Z=420  ENTERA (mejor solucion hasta ahora)
`-- [x1 >= 4] P2 (4, 2.4) Z=428  RAMIFICADO en x2 = 2.4000
    |-- [x2 <= 2] P3 (4.1667, 2) Z=423.3333  RAMIFICADO en x1 = 4.1667
    |   |-- [x1 <= 4] P5 (4, 2) Z=410  PODADO (Z = 410.00 <= 420.00)
    |   `-- [x1 >= 5] P6 (5, 0) Z=400  PODADO (Z = 400.00 <= 420.00)
    `-- [x2 >= 3] P4 infactible  INFACTIBLE

RESULTADO
---------
x1 = 3 ; x2 = 4 ; Z optimo = 420

Reporte guardado en: outputs/reporte_ejercicio2.txt
```

## Resultado

| Nodo | Rama     | Solución       | Z      | Estado     |
|------|----------|----------------|--------|------------|
| P0   | -        | (3,57 ; 3,43)  | 440    | se ramifica en x1 |
| P1   | x1 <= 3  | (3 ; 4)        | 420    | entera, la mejor |
| P2   | x1 >= 4  | (4 ; 2,4)      | 428    | se ramifica en x2 |
| P3   | x2 <= 2  | (4,17 ; 2)     | 423,33 | se ramifica en x1 |
| P5   | x1 <= 4  | (4 ; 2)        | 410    | se poda (< 420) |
| P6   | x1 >= 5  | (5 ; 0)        | 400    | se poda (< 420) |
| P4   | x2 >= 3  | -              | -      | infactible |

**Óptimo: x1 = 3, x2 = 4, Z = 420.** El test lo contrasta con `scipy.optimize.milp`.

Conclusión y desarrollo para el examen: `ejercicio2.md`.
