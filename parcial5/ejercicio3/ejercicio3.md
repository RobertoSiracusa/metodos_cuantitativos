# Ejercicio 3. Volumen de carga (versión para escribir a mano)

**Datos:** Tablet (2 kg, $40) · Dron (3 kg, $50) · Proyector (4 kg, $65) · Laptop (5 kg, $60). Capacidad 10 kg.

**Modelo:** Max Z = 40m1 + 50m2 + 65m3 + 60m4  s.a. 2m1 + 3m2 + 4m3 + 5m4 ≤ 10, mi = 0 o 1

## 1. Pasos

Recursión: **fi(y) = max{ f(i-1)(y) ; ri + f(i-1)(y − wi) }**, con f0(y) = 0

| y | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|----|
| f1 Tablet | 0 | 0 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 |
| f2 Dron | 0 | 0 | 40 | 50 | 50 | 90 | 90 | 90 | 90 | 90 | 90 |
| f3 Proyector | 0 | 0 | 40 | 50 | 65 | 90 | 105 | 115 | 115 | 155 | 155 |
| f4 Laptop | 0 | 0 | 40 | 50 | 65 | 90 | 105 | 115 | 115 | 155 | **155** |

Reconstrucción desde y = 10:
- f4(10) = max{155 ; 60 + 90} = 155 → Laptop **no** (y = 10)
- f3(10) = max{90 ; 65 + 90} = 155 → Proyector **sí** (y = 6)
- f2(6) = max{40 ; 50 + 40} = 90 → Dron **sí** (y = 3)
- f1(3) = 40 → Tablet **sí** (y = 1)

## 2. Respuesta

**Llevar Tablet, Dron y Proyector: 9 kg, valor máximo $155.**

## 3. Programa

`python3 main.py` → `outputs/reporte_ejercicio3.txt` (archivo para subir a Acrópolis).

## 4. Conclusión

El máximo es $155 con Tablet, Dron y Proyector, y coincide con el programa y con milp.
Sobra 1 kg: la combinación que llena los 10 kg (Tablet + Dron + Laptop) sólo vale $150.
La Laptop queda afuera por ser la de menor valor por kg ($12/kg).
