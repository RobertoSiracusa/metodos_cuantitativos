# Parcial II — Ejercicio 3: Modelo Multi-Artículo con Restricciones

**Universidad José Antonio Páez — Facultad de Ingeniería**  
**Escuela de Ingeniería en Computación**  
**Cátedra:** Métodos Cuantitativos — Teoría de Inventarios  
**Profesor:** Argenis  
**Período:** Junio 2025 / Agosto 2026  

---

## 1. Enunciado del Problema

> **Una gran empresa con alta demanda, costos elevados, espacio limitado y un presupuesto ajustado. Debe priorizar cuidadosamente para minimizar costos.**  
> - **Artículos:** A, B, C  
> - **Demanda mensual:** 300, 250, 400 unidades  
> - **Costo de pedido por unidad ($S$):** 30, 35, 40  
> - **Costo de almacenamiento por unidad ($H$):** 5, 6, 7  
> - **Capacidad total:** 700 unidades (muy limitada para la demanda)  
> - **Presupuesto:** 8000 (ajustado considerando demanda)  
> - **Demanda diaria ($d$):** 10, 8, 15 unidades  
> - **Tiempo de entrega ($L$):** 3, 4, 5 días  
>  
> *Resolver en Python y subir el código y las salidas del programa en txt (5 ptos).*  
> *Escribe en hoja de examen la conclusión del problema (3 ptos).*

---

## 2. Identificación y Tabla de Parámetros de Entrada

Para el análisis cuantitativo y la aplicación de los modelos matemáticos en base anual estándar ($1\text{ año} = 12\text{ meses}$):

| Parámetro / Variable | Artículo A | Artículo B | Artículo C | Global / Límite |
| :--- | :---: | :---: | :---: | :---: |
| **Demanda Mensual ($D_{\text{mes}}$)** | 300 unid/mes | 250 unid/mes | 400 unid/mes | 950 unid/mes |
| **Demanda Anualizada ($D = 12 \cdot D_{\text{mes}}$)** | **3,600 unid/año** | **3,000 unid/año** | **4,800 unid/año** | **11,400 unid/año** |
| **Costo por Pedido ($S$ o $C_p$)** | \$30.00 /pedido | \$35.00 /pedido | \$40.00 /pedido | — |
| **Costo de Almacenamiento ($H$ o $C_m$)** | \$5.00 /unid/año | \$6.00 /unid/año | \$7.00 /unid/año | — |
| **Área / Espacio Unitario ($a_i$)** | 1.00 unid | 1.00 unid | 1.00 unid | — |
| **Capacidad Máxima de Almacén ($A$)** | — | — | — | **700 unidades** |
| **Presupuesto Máximo Anual ($B$)** | — | — | — | **\$8,000.00** |
| **Demanda Diaria ($d$)** | 10 unid/día | 8 unid/día | 15 unid/día | — |
| **Tiempo de Entrega / Lead Time ($L$)** | 3 días | 4 días | 5 días | — |

---

## 3. Desarrollo Matemático Paso a Paso (Formato Hoja de Examen)

### Paso 1: Formulación del Modelo de Optimización (KKT / Lagrange)

Se busca determinar las cantidades óptimas a pedir ($Q_A, Q_B, Q_C$) que minimicen la función de costo total anual de inventario:

$$\min CT(Q_A, Q_B, Q_C) = \sum_{i \in \{A,B,C\}} \left[ \frac{D_i}{Q_i} S_i + \frac{Q_i}{2} H_i \right]$$

Sujeto a:
1. **Restricción de Capacidad de Almacenamiento:**
   $$\sum_{i \in \{A,B,C\}} a_i Q_i \le 700 \implies Q_A + Q_B + Q_C \le 700$$
2. **Restricción Presupuestaria:**
   $$CT(Q_A, Q_B, Q_C) \le 8000$$
3. **No Negatividad:**
   $$Q_A > 0, \quad Q_B > 0, \quad Q_C > 0$$

---

### Paso 2: Cálculo de los Lotes Económicos de Pedido Ideales (EOQ Clásico)

Se calcula la solución no restringida mediante la fórmula del Lote Económico de Wilson:

$$Q_i^* = \sqrt{\frac{2 \cdot D_i \cdot S_i}{H_i}}$$

#### **Artículo A:**
$$Q_A^* = \sqrt{\frac{2 \cdot (3600) \cdot (30)}{5}} = \sqrt{\frac{216000}{5}} = \sqrt{43200} \approx \mathbf{207.85\text{ unidades}}$$

#### **Artículo B:**
$$Q_B^* = \sqrt{\frac{2 \cdot (3000) \cdot (35)}{6}} = \sqrt{\frac{210000}{6}} = \sqrt{35000} \approx \mathbf{187.08\text{ unidades}}$$

#### **Artículo C:**
$$Q_C^* = \sqrt{\frac{2 \cdot (4800) \cdot (40)}{7}} = \sqrt{\frac{384000}{7}} = \sqrt{54857.1428} \approx \mathbf{234.22\text{ unidades}}$$

---

### Paso 3: Evaluación y Verificación de la Restricción de Capacidad

Calculamos la suma total de las cantidades óptimas a almacenar simultáneamente:

$$Q_{\text{total}} = Q_A^* + Q_B^* + Q_C^* = 207.8461 + 187.0829 + 234.2160 = \mathbf{629.14\text{ unidades}}$$

**Comparación con el límite de capacidad física ($A = 700$ unidades):**
$$629.14 \le 700 \quad \checkmark \quad \textbf{(Cumple satisfactoriamente)}$$

- **Porcentaje de ocupación del almacén:**
  $$\% \text{ Ocupación} = \left( \frac{629.14}{700} \right) \cdot 100\% = \mathbf{89.88\%}$$
- **Holgura de capacidad (espacio libre disponible):**
  $$\text{Holgura}_{\text{capacidad}} = 700 - 629.14 = \mathbf{70.86\text{ unidades (10.12\% de margen libre)}}$$

---

### Paso 4: Desglose de Costos de Inventario y Verificación Presupuestaria

#### A. Costo Anual de Emitir Pedidos ($CP$):
$$CP_A = \frac{D_A}{Q_A^*} \cdot S_A = \frac{3600}{207.8461} \cdot 30 = \$519.62$$
$$CP_B = \frac{D_B}{Q_B^*} \cdot S_B = \frac{3000}{187.0829} \cdot 35 = \$561.25$$
$$CP_C = \frac{D_C}{Q_C^*} \cdot S_C = \frac{4800}{234.2160} \cdot 40 = \$819.76$$
$$\sum CP = 519.62 + 561.25 + 819.76 = \mathbf{\$1,900.62\text{ /año}}$$

#### B. Costo Anual de Almacenamiento / Mantenimiento ($CA$):
$$CA_A = \frac{Q_A^*}{2} \cdot H_A = \frac{207.8461}{2} \cdot 5 = \$519.62$$
$$CA_B = \frac{Q_B^*}{2} \cdot H_B = \frac{187.0829}{2} \cdot 6 = \$561.25$$
$$CA_C = \frac{Q_C^*}{2} \cdot H_C = \frac{234.2160}{2} \cdot 7 = \$819.76$$
$$\sum CA = 519.62 + 561.25 + 819.76 = \mathbf{\$1,900.62\text{ /año}}$$

#### C. Costo Total Anual del Sistema ($CT$):
$$CT = \sum CP + \sum CA = \$1,900.62 + \$1,900.62 = \mathbf{\$3,801.24\text{ /año}}$$

**Comparación con el Presupuesto Máximo Disponible ($B = \$8,000.00$):**
$$\$3,801.24 \le \$8,000.00 \quad \checkmark \quad \textbf{(Cumple holgadamente)}$$

- **Porcentaje de presupuesto utilizado:**
  $$\% \text{ Presupuesto} = \left( \frac{3801.24}{8000.00} \right) \cdot 100\% = \mathbf{47.52\%}$$
- **Holgura financiera:**
  $$\text{Holgura}_{\text{presupuesto}} = \$8,000.00 - \$3,801.24 = \mathbf{\$4,198.76\text{ disponibles (52.48\% de ahorro)}}$$

---

### Paso 5: Análisis de Multiplicadores de Lagrange ($\lambda$)

De acuerdo con las condiciones de optimalidad de Karush-Kuhn-Tucker (KKT) para restricciones de desigualdad con holgura positiva:

$$\lambda_1 (Q_{\text{total}} - 700) = 0 \implies \text{Como } Q_{\text{total}} < 700 \implies \mathbf{\lambda_1 = 0.0000}$$
$$\lambda_2 (CT - 8000) = 0 \implies \text{Como } CT < 8000 \implies \mathbf{\lambda_2 = 0.0000}$$

**Conclusión Matemática:** Al no activarse ninguna restricción en la frontera, los lotes económicos ideales $Q^*$ no requieren penalización ni ajuste por Lagrange, alcanzando el **mínimo global de costos**.

---

### Paso 6: Cálculo de los Puntos de Reorden ($ROP$)

El Punto de Reorden indica el nivel de existencias en el cual se debe colocar un nuevo pedido para cubrir la demanda durante el tiempo de entrega del proveedor ($L_i$):

$$ROP_i = d_i \cdot L_i$$

- **Artículo A:** $ROP_A = 10\text{ unid/día} \cdot 3\text{ días} = \mathbf{30.00\text{ unidades}}$
- **Artículo B:** $ROP_B = 8\text{ unid/día} \cdot 4\text{ días} = \mathbf{32.00\text{ unidades}}$
- **Artículo C:** $ROP_C = 15\text{ unid/día} \cdot 5\text{ días} = \mathbf{75.00\text{ unidades}}$

---

### Paso 7: Política Operativa y Frecuencia de Pedidos

- **Número de pedidos anuales ($N = D / Q^*$):**
  - Artículo A: $N_A = \frac{3600}{207.85} = \mathbf{17.32\text{ pedidos/año}}$
  - Artículo B: $N_B = \frac{3000}{187.08} = \mathbf{16.04\text{ pedidos/año}}$
  - Artículo C: $N_C = \frac{4800}{234.22} = \mathbf{20.49\text{ pedidos/año}}$
- **Frecuencia entre pedidos ($T = (Q^* / D) \cdot 12\text{ meses}$):**
  - Artículo A: $T_A = 0.69\text{ meses}$ ($\approx 21\text{ días}$)
  - Artículo B: $T_B = 0.75\text{ meses}$ ($\approx 22.5\text{ días}$)
  - Artículo C: $T_C = 0.59\text{ meses}$ ($\approx 17.6\text{ días}$)

---

## 4. Comando de Ejecución del Programa en Python

Desde el directorio `parcial2/`:

```bash
python3 main.py --ejercicio3
```

---

## 5. Salida Oficial del Programa (`.txt`)

```text
==================================================
   REPORTE DE INVENTARIO: MULTI-ARTICULO CON REST.
==================================================
Parametros Globales:
 - Presupuesto Maximo ($): $8000.00
 - Capacidad Almacenamiento (Area / Q Max): 700.00 m2 (o unidades)
 - Metodo Utilizado: Multiplicadores de Lagrange (Exacto)
 - Estado de Solucion: Optimal (Sin restricciones activas)
 - Diagnostico: Los lotes EOQ cumplen todas las capacidades y presupuesto sin requerir ajustes. (Factor Ajuste: 1.0000)

Detalles por Articulo:
--------------------------------------------------
 Articulo A:
   * Demanda Anual (D): 3600 unidades
   * Costo Pedido (S/Cp): $30.00
   * Costo Almacenaje (H/Cm): $5.00
   * Area Unit. (a): 1.00 m2
   * EOQ Clasico sin restriccion: 207.85
   * Cantidad Optima Ajustada (Q*): 207.85
   * Punto de Reorden (ROP): 30.00 unidades

 Articulo B:
   * Demanda Anual (D): 3000 unidades
   * Costo Pedido (S/Cp): $35.00
   * Costo Almacenaje (H/Cm): $6.00
   * Area Unit. (a): 1.00 m2
   * EOQ Clasico sin restriccion: 187.08
   * Cantidad Optima Ajustada (Q*): 187.08
   * Punto de Reorden (ROP): 32.00 unidades

 Articulo C:
   * Demanda Anual (D): 4800 unidades
   * Costo Pedido (S/Cp): $40.00
   * Costo Almacenaje (H/Cm): $7.00
   * Area Unit. (a): 1.00 m2
   * EOQ Clasico sin restriccion: 234.22
   * Cantidad Optima Ajustada (Q*): 234.22
   * Punto de Reorden (ROP): 75.00 unidades

==================================================
                RESUMEN DE USO
==================================================
 - Presupuesto Utilizado: $3801.24 de $8000.00
 - Espacio Almacenamiento Utilizado: 629.14 de 700.00 m2
 - Costo Total de Almacenamiento Anual: $1900.62
 - Costo Total de Pedidos Anual: $1900.62
 - Costo Total Anual Optimizado: $3801.24
==================================================
       INTERPRETACION Y ANALISIS DE DECISION
==================================================
1. Diagnostico de Restricciones y Holguras:
   - Los lotes economicos (EOQ) operan con holgura completa sin violar ninguna restriccion:
     * Espacio utilizado: 629.14 m2 de 700.00 m2 (89.88% ocupado | 70.86 m2 libres / 10.12% de holgura).
     * Presupuesto utilizado: $3801.24 de $8000.00 (47.52% utilizado | $4198.76 disponibles / 52.48% de holgura).
   - La solucion obtenida es 100% optima a nivel global (Multiplicador de Lagrange lambda = 0.0000), sin sobrecosto ni penalizacion por capacidad o presupuesto.

2. Resumen Operativo de Politicas de Inventario por Articulo:
   * Articulo A: Ordenar lotes de 207.85 unidades cada 0.69 meses (17.32 pedidos/ano). Punto de Reorden (ROP): 30.00 unidades.
   * Articulo B: Ordenar lotes de 187.08 unidades cada 0.75 meses (16.04 pedidos/ano). Punto de Reorden (ROP): 32.00 unidades.
   * Articulo C: Ordenar lotes de 234.22 unidades cada 0.59 meses (20.49 pedidos/ano). Punto de Reorden (ROP): 75.00 unidades.
==================================================
```

---

## 6. Cuadro Resumen de Resultados Finales

| Métrica / Artículo | Artículo A | Artículo B | Artículo C | Total del Sistema | Límite Disponible | Holgura / Margen |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Lote Óptimo ($Q^*$)** | **207.85** | **187.08** | **234.22** | **629.14 unid** | 700.00 unid | 70.86 unid (10.12%) |
| **Punto Reorden ($ROP$)** | **30.00** | **32.00** | **75.00** | — | — | — |
| **N° Pedidos / Año ($N$)** | 17.32 | 16.04 | 20.49 | 53.85 pedidos | — | — |
| **Frecuencia ($T$ en meses)** | 0.69 mes | 0.75 mes | 0.59 mes | — | — | — |
| **Costo de Pedidos ($CP$)** | \$519.62 | \$561.25 | \$819.76 | \$1,900.62 | — | — |
| **Costo Almacenaje ($CA$)**| \$519.62 | \$561.25 | \$819.76 | \$1,900.62 | — | — |
| **Costo Total Anual ($CT$)**| \$1,039.24| \$1,122.50| \$1,639.51| **\$3,801.24** | **\$8,000.00** | **\$4,198.76 (52.48%)** |

---

## 7. Conclusión del Problema (Para Escribir en la Hoja de Examen — 3 ptos)

> **CONCLUSIÓN DEL PROBLEMA:**
>
> 1. **Viabilidad y Factibilidad Global:** La política de inventarios óptima determinada mediante los lotes económicos de pedido ($Q_A^* = 207.85$, $Q_B^* = 187.08$, $Q_C^* = 234.22$ unidades) es plenamente factible y no requiere ajuste ni reducción restrictiva.
>
> 2. **Comportamiento del Almacén y Capacidad:** La suma total requerida para los lotes de los tres artículos es de **$629.14$ unidades**, lo cual aprovecha eficientemente el **$89.88\%$** de la capacidad física disponible ($700$ unidades), manteniendo una holgura segura de **$70.86$ unidades ($10.12\%$)** para absorber fluctuaciones operativas.
>
> 3. **Eficiencia Presupuestaria:** El costo total anual mínimo de operación es de **$\$3,801.24$**, el cual se encuentra holgadamente por debajo del límite presupuestario de **$\$8,000.00$**, consumiendo únicamente el **$47.52\%$** del capital asignado y generando una holgura financiera de **$\$4,198.76$ ($52.48\%$)**.
>
> 4. **Análisis de Lagrange y Condiciones KKT:** Dado que ambas restricciones se satisfacen con holgura estricta, los multiplicadores de Lagrange asociados son **$\lambda = 0.0000$**, lo que demuestra matemáticamente que la empresa opera en su **óptimo económico global absoluto** sin incurrir en sobrecostos por penalización de espacio o fondos.
>
> 5. **Política Operativa de Control Continuo ($Q, R$):**
>    - **Artículo A:** Emitir una orden de **$208$ unidades** cada vez que el inventario descienda a **$30$ unidades** (aproximadamente cada $21$ días).
>    - **Artículo B:** Emitir una orden de **$187$ unidades** cada vez que el inventario descienda a **$32$ unidades** (aproximadamente cada $23$ días).
>    - **Artículo C:** Emitir una orden de **$234$ unidades** cada vez que el inventario descienda a **$75$ unidades** (aproximadamente cada $18$ días).
