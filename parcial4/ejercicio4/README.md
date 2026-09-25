# Parcial IV - Ejercicio 4: Problema de la Mochila

**Universidad José Antonio Páez - Facultad de Ingeniería**
**Escuela de Ingeniería en Computación - Métodos Cuantitativos**

Programa de consola (CLI) que resuelve el **problema de la mochila 0/1**: elegir qué
objetos llevar para que el valor total sea el máximo sin pasar la capacidad de 50 kg.

## Datos del parcial

| Objeto | Peso (kg) | Valor ($) | Valor/kg |
|--------|-----------|-----------|----------|
| 1      | 10        | 60        | 6,00     |
| 2      | 20        | 100       | 5,00     |
| 3      | 15        | 90        | 6,00     |
| 4      | 25        | 120       | 4,80     |
| 5      | 30        | 150       | 5,00     |
| 6      | 12        | 80        | 6,67     |

## Explicación del modelo

**Variables:** `xi = 1` si el objeto *i* entra en la mochila, `0` si no.

```
Max Z = 60x1 + 100x2 + 90x3 + 120x4 + 150x5 + 80x6
s.a.  10x1 + 20x2 + 15x3 + 25x4 + 30x5 + 12x6 <= 50
      xi en {0, 1}
```

**Cómo lo resuelve el programa** (`src/core/knapsack.py`):

1. **Programación dinámica (método principal):** arma la tabla
   `F[i][c]` = mejor valor usando los primeros *i* objetos con capacidad *c*:
   ```
   F[i][c] = max( F[i-1][c] ,  F[i-1][c - wi] + vi )   si wi <= c
   ```
   Es decir, el objeto *i* se deja afuera o se mete. Después recorre la tabla hacia
   atrás para saber qué objetos entraron.
2. **Verificación con `scipy.optimize.milp`:** resuelve el mismo modelo binario y
   comprueba que el valor coincida.
3. **Óptimos alternativos:** prueba todas las combinaciones y lista las que llegan
   al valor máximo. Recomienda la de menor peso.
4. **Heurística voraz:** mete los objetos de mayor valor por kg mientras quepan.
   Sirve para mostrar que una regla rápida no garantiza el óptimo.

## Estructura

```text
ejercicio4/
├── main.py                        # CLI
├── ejercicio4.md                  # respuesta para transcribir a mano
├── requirements.txt
├── datos/objetos.json             # pesos, valores y capacidad del parcial
├── src/
│   ├── core/knapsack.py           # ModeloMochila: DP, milp, voraz, alternativos
│   └── services/reporter.py       # modelo, resultado y comparación en texto
├── tests/test_knapsack.py         # pytest
└── outputs/reporte_ejercicio4.txt # salida generada
```

## Instalación y ejecución

```bash
cd parcial4/ejercicio4
python3 -m pip install -r requirements.txt

python3 main.py                          # problema del parcial
python3 main.py --capacidad 60           # otra capacidad
python3 main.py --datos otros.json --sin-exportar

python3 -m pytest tests/ -q              # pruebas
```

## Salida por terminal

Salida de `python3 main.py` con los datos del parcial:

```text
$ python3 main.py
EJERCICIO 4 - PROBLEMA DE LA MOCHILA
====================================

MODELO
------
xi = 1 si el objeto i entra en la mochila, 0 si no
Max Z = 60x1 + 100x2 + 90x3 + 120x4 + 150x5 + 80x6
s.a.
  10x1 + 20x2 + 15x3 + 25x4 + 30x5 + 12x6 <= 50
  xi en {0, 1}

Objeto  Peso  Valor  Valor/kg
     1    10     60      6.00
     2    20    100      5.00
     3    15     90      6.00
     4    25    120      4.80
     5    30    150      5.00
     6    12     80      6.67

RESULTADO
---------
Programacion dinamica: objetos 1, 3, 4 | peso 50 kg | valor $270
  x = (1, 0, 1, 1, 0, 0)
Verificacion milp:     objetos 2, 3, 6 | peso 47 kg | valor $270
Coinciden en valor: SI

Combinaciones que alcanzan $270: 2
  objetos 2, 3, 6    peso 47 kg (libres 3 kg)
  objetos 1, 3, 4    peso 50 kg (libres 0 kg)
Recomendada (mismo valor, menor peso): objetos 2, 3, 6

Heuristica voraz (mayor valor/kg): objetos 1, 3, 6 | peso 37 kg | valor $230
Diferencia contra el optimo: $40

Reporte guardado en: outputs/reporte_ejercicio4.txt
```

## Resultado

**Valor máximo: $270.** Hay dos combinaciones que lo alcanzan:

| Objetos  | Peso  | Valor | Libre |
|----------|-------|-------|-------|
| 2, 3, 6  | 47 kg | $270  | 3 kg  |
| 1, 3, 4  | 50 kg | $270  | 0 kg  |

Se recomienda **2, 3 y 6**, porque da el mismo valor con menos peso. La heurística
voraz (objetos 6, 1 y 3) sólo llega a $230, $40 menos que el óptimo.

Conclusión y desarrollo para el examen: `ejercicio4.md`.
