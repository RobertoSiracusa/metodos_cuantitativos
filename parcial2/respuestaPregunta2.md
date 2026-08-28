# Parcial II — Ejercicio 2: Modelo de Quiebre de Precios (Descuentos por Volumen)

**Universidad José Antonio Páez — Facultad de Ingeniería**  
**Escuela de Ingeniería en Computación**  
**Cátedra:** Métodos Cuantitativos — Teoría de Inventarios  
**Profesor:** Argenis  
**Período:** Junio 2025 / Agosto 2026  

---

## 1. Enunciado del Problema

> **Un proveedor ofrece el siguiente esquema de descuentos para un producto con una demanda anual de 10,000 unidades. El precio base es $10 por unidad. El costo por pedido es de $100 y el costo de almacenamiento anual es el 25% del precio del producto.**  
> - **a)** Resolver en hoja de examen *(3 ptos)*  
> - **b)** Resolver en Python y subir códigos y salidas de txt en Acrópolis *(3 ptos)*  
>
> | Tamaño del lote ($Q$) | Descuento (%) |
> | :---: | :---: |
> | 0 – 999 | 0% |
> | 1000 – 1999 | 3% |
> | 2000 – 2999 | 5% |
> | 3000 o más | 7% |

---

## 2. Identificación y Tabla de Datos por Tramo

| Parámetro / Variable | Símbolo | Valor Base | Unidades |
| :--- | :---: | :---: | :---: |
| **Demanda Anual** | $D$ | 10,000 | unidades/año |
| **Costo por Pedido** | $S$ ($K$) | 100.00 | \$/pedido |
| **Tasa Anual de Almacenamiento** | $i$ | 25% (0.25) | anual |
| **Precio Base Unitario** | $P_{\text{base}}$ | 10.00 | \$/unidad |

### Estructura de Tramos de Precios y Costos de Mantenimiento ($H_j = i \cdot P_j$):

| Tramo $j$ | Rango de Cantidad ($Q$) | Descuento | Precio Unitario ($P_j$) | Costo Almacenaje ($H_j = 0.25 \cdot P_j$) |
| :---: | :---: | :---: | :---: | :---: |
| **1** | $0 \le Q \le 999$ | 0% | **\$10.00** | $0.25 \times 10.00 = \mathbf{\$2.500\text{ /unid/año}}$ |
| **2** | $1000 \le Q \le 1999$ | 3% | $10 \cdot (1 - 0.03) = \mathbf{\$9.70}$ | $0.25 \times 9.70 = \mathbf{\$2.425\text{ /unid/año}}$ |
| **3** | $2000 \le Q \le 2999$ | 5% | $10 \cdot (1 - 0.05) = \mathbf{\$9.50}$ | $0.25 \times 9.50 = \mathbf{\$2.375\text{ /unid/año}}$ |
| **4** | $Q \ge 3000$ | 7% | $10 \cdot (1 - 0.07) = \mathbf{\$9.30}$ | $0.25 \times 9.30 = \mathbf{\$2.325\text{ /unid/año}}$ |

---

## 3. Desarrollo Matemático Paso a Paso (Literal a — Hoja de Examen)

### Metodología de Resolución
Para cada tramo $j$:
1. Se calcula el lote económico no restringido:
   $$EOQ_j = \sqrt{\frac{2 \cdot D \cdot S}{H_j}}$$
2. Se evalúa la **factibilidad**:
   - Si $Q_{\text{mín}, j} \le EOQ_j \le Q_{\text{máx}, j}$: El lote es factible tal cual ($Q_j^* = EOQ_j$).
   - Si $EOQ_j < Q_{\text{mín}, j}$: El lote ideal cae a la izquierda; por convexidad de la curva de costos, el menor costo alcanzable en este tramo ocurre en el límite inferior ($Q_j^* = Q_{\text{mín}, j}$).
   - Si $EOQ_j > Q_{\text{máx}, j}$: El tramo es no factible y se descarta.
3. Se calcula el **Costo Total Anual** para la cantidad ajustada $Q_j^*$:
   $$CT_j = CP_j + CA_j + CADQ_j = \left( \frac{D}{Q_j^*} \right) S + \left( \frac{Q_j^*}{2} \right) H_j + D \cdot P_j$$

---

### Evaluación del Tramo 1 ($0 \le Q \le 999$ | $P_1 = \$10.00$, $H_1 = \$2.50$)

$$EOQ_1 = \sqrt{\frac{2 \cdot (10000) \cdot (100)}{2.50}} = \sqrt{\frac{2000000}{2.50}} = \sqrt{800000} \approx \mathbf{894.43\text{ unidades}}$$

- **Factibilidad:** $0 \le 894.43 \le 999 \implies$ **Factible en rango**.
- **Cantidad a ordenar:** $Q_1^* = \mathbf{894.43\text{ unidades}}$.
- **Desglose de Costos:**
  - Costo de Pedidos: $CP_1 = \left( \frac{10000}{894.4272} \right) \cdot 100 = \mathbf{\$1,118.03}$
  - Costo de Almacenaje: $CA_1 = \left( \frac{894.4272}{2} \right) \cdot 2.50 = \mathbf{\$1,118.03}$
  - Costo de Adquisición: $CADQ_1 = 10000 \cdot 10.00 = \mathbf{\$100,000.00}$
  - **Costo Total Anual:**
    $$CT_1 = \$1,118.03 + \$1,118.03 + \$100,000.00 = \mathbf{\$102,236.07\text{ /año}}$$

---

### Evaluación del Tramo 2 ($1000 \le Q \le 1999$ | $P_2 = \$9.70$, $H_2 = \$2.425$)

$$EOQ_2 = \sqrt{\frac{2 \cdot (10000) \cdot (100)}{2.425}} = \sqrt{\frac{2000000}{2.425}} = \sqrt{824742.27} \approx \mathbf{908.15\text{ unidades}}$$

- **Factibilidad:** $908.15 < 1000 \implies$ **Cae por debajo del rango**.
- **Ajuste:** Se toma el límite inferior del tramo: $Q_2^* = \mathbf{1,000.00\text{ unidades}}$.
- **Desglose de Costos:**
  - Costo de Pedidos: $CP_2 = \left( \frac{10000}{1000} \right) \cdot 100 = 10 \cdot 100 = \mathbf{\$1,000.00}$
  - Costo de Almacenaje: $CA_2 = \left( \frac{1000}{2} \right) \cdot 2.425 = 500 \cdot 2.425 = \mathbf{\$1,212.50}$
  - Costo de Adquisición: $CADQ_2 = 10000 \cdot 9.70 = \mathbf{\$97,000.00}$
  - **Costo Total Anual:**
    $$CT_2 = \$1,000.00 + \$1,212.50 + \$97,000.00 = \mathbf{\$99,212.50\text{ /año}}$$

---

### Evaluación del Tramo 3 ($2000 \le Q \le 2999$ | $P_3 = \$9.50$, $H_3 = \$2.375$)

$$EOQ_3 = \sqrt{\frac{2 \cdot (10000) \cdot (100)}{2.375}} = \sqrt{\frac{2000000}{2.375}} = \sqrt{842105.26} \approx \mathbf{917.66\text{ unidades}}$$

- **Factibilidad:** $917.66 < 2000 \implies$ **Cae por debajo del rango**.
- **Ajuste:** Se toma el límite inferior del tramo: $Q_3^* = \mathbf{2,000.00\text{ unidades}}$.
- **Desglose de Costos:**
  - Costo de Pedidos: $CP_3 = \left( \frac{10000}{2000} \right) \cdot 100 = 5 \cdot 100 = \mathbf{\$500.00}$
  - Costo de Almacenaje: $CA_3 = \left( \frac{2000}{2} \right) \cdot 2.375 = 1000 \cdot 2.375 = \mathbf{\$2,375.00}$
  - Costo de Adquisición: $CADQ_3 = 10000 \cdot 9.50 = \mathbf{\$95,000.00}$
  - **Costo Total Anual:**
    $$CT_3 = \$500.00 + \$2,375.00 + \$95,000.00 = \mathbf{\$97,875.00\text{ /año}}$$

---

### Evaluación del Tramo 4 ($Q \ge 3000$ | $P_4 = \$9.30$, $H_4 = \$2.325$)

$$EOQ_4 = \sqrt{\frac{2 \cdot (10000) \cdot (100)}{2.325}} = \sqrt{\frac{2000000}{2.325}} = \sqrt{860215.05} \approx \mathbf{927.48\text{ unidades}}$$

- **Factibilidad:** $927.48 < 3000 \implies$ **Cae por debajo del rango**.
- **Ajuste:** Se toma el límite inferior del tramo: $Q_4^* = \mathbf{3,000.00\text{ unidades}}$.
- **Desglose de Costos:**
  - Costo de Pedidos: $CP_4 = \left( \frac{10000}{3000} \right) \cdot 100 = 3.3333 \cdot 100 = \mathbf{\$333.33}$
  - Costo de Almacenaje: $CA_4 = \left( \frac{3000}{2} \right) \cdot 2.325 = 1500 \cdot 2.325 = \mathbf{\$3,487.50}$
  - Costo de Adquisición: $CADQ_4 = 10000 \cdot 9.30 = \mathbf{\$93,000.00}$
  - **Costo Total Anual:**
    $$CT_4 = \$333.33 + \$3,487.50 + \$93,000.00 = \mathbf{\$96,820.83\text{ /año}}$$

---

## 4. Comparativa de Optimalidad y Análisis de Trade-Off

Comparación de los cuatro tramos evaluados:

| Tramo $j$ | Rango | Lote Evaluado ($Q_j^*$) | Precio Unit. | Costo Pedidos ($CP$) | Costo Almacén ($CA$) | Costo Compra ($CADQ$) | Costo Total Anual ($CT$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tramo 1** | $0 - 999$ | $894.43$ unid | \$10.00 | \$1,118.03 | \$1,118.03 | \$100,000.00 | **\$102,236.07** |
| **Tramo 2** | $1000 - 1999$ | $1,000.00$ unid | \$9.70 | \$1,000.00 | \$1,212.50 | \$97,000.00 | **\$99,212.50** |
| **Tramo 3** | $2000 - 2999$ | $2,000.00$ unid | \$9.50 | \$500.00 | \$2,375.00 | \$95,000.00 | **\$97,875.00** |
| **Tramo 4** | **$\ge 3000$** | **3,000.00 unid** | **\$9.30** | **\$333.33** | **\$3,487.50** | **\$93,000.00** | **\$96,820.83 (MÍNIMO)** |

### Análisis del Trade-Off Económico:
- **Ahorro en Adquisición:** Pasar del Tramo 1 al Tramo 4 ahorra **\$7,000.00** anuales en compras (\$100,000 vs \$93,000).
- **Ahorro en Emisión de Pedidos:** Al pedir lotes mayores de 3,000 unidades, se emiten solo 3.33 órdenes al año en lugar de 11.18, ahorrando **\$784.70** en pedidos.
- **Incremento en Almacenamiento:** El costo de mantener inventario sube de \$1,118.03 a \$3,487.50 (+**\$2,369.47**).
- **Balance Neto:** El ahorro combinado en compras y pedidos (\$7,784.70) supera ampliamente el sobrecosto de almacenaje (\$2,369.47), generando un **ahorro neto anual de \$5,415.24 (5.30%)**.

---

## 5. Comando de Ejecución del Programa en Python (Literal b)

Desde el directorio `parcial2/`:

```bash
python3 main.py --ejercicio2
```

---

## 6. Salida Oficial del Programa (`.txt`)

```text
==================================================
   REPORTE DE INVENTARIO: QUIEBRE DE PRECIOS
==================================================
Parametros de Entrada:
 - Demanda Anual (D): 10000.00 unidades
 - Costo de Pedido (S/K): $100.00
 - Costo Almacenaje Anual (%): 25.00%

Desglose de Tramos:
 Tramo 1 [0 a 999] @ $10.00/unidad:
   * EOQ Teorico: 894.43
   * Estado: Factible (EOQ en rango)
   * Cantidad Ajustada: 894.43
   * Costo Anual de Pedidos: $1118.03
   * Costo Anual de Almacenamiento: $1118.03
   * Costo Anual de Adquisicion: $100000.00
   * Costo Anual Total: $102236.07

 Tramo 2 [1000 a 1999] @ $9.70/unidad:
   * EOQ Teorico: 908.15
   * Estado: Ajustado al Limite Inferior
   * Cantidad Ajustada: 1000.00
   * Costo Anual de Pedidos: $1000.00
   * Costo Anual de Almacenamiento: $1212.50
   * Costo Anual de Adquisicion: $97000.00
   * Costo Anual Total: $99212.50

 Tramo 3 [2000 a 2999] @ $9.50/unidad:
   * EOQ Teorico: 917.66
   * Estado: Ajustado al Limite Inferior
   * Cantidad Ajustada: 2000.00
   * Costo Anual de Pedidos: $500.00
   * Costo Anual de Almacenamiento: $2375.00
   * Costo Anual de Adquisicion: $95000.00
   * Costo Anual Total: $97875.00

 Tramo 4 [3000 a inf] @ $9.30/unidad:
   * EOQ Teorico: 927.48
   * Estado: Ajustado al Limite Inferior
   * Cantidad Ajustada: 3000.00
   * Costo Anual de Pedidos: $333.33
   * Costo Anual de Almacenamiento: $3487.50
   * Costo Anual de Adquisicion: $93000.00
   * Costo Anual Total: $96820.83

==================================================
                 OPTIMO RECOMENDADO
==================================================
 - Cantidad Optima a Ordenar (Q*): 3000.00 unidades
 - Tramo Optimo: Tramo 4
 - Precio Aplicable: $9.30/unidad
 - Costo Minimo Total Anual: $96820.83
==================================================
       INTERPRETACION Y ANALISIS DE DECISION
==================================================
1. Conclusion General:
   El Tramo 4 es la alternativa economicamente optima con un lote de 3000.00 unidades
   a un precio de $9.30/unidad, logrando el Costo Total Anual minimo de $96820.83.
   Se recomienda realizar 3.33 pedidos al ano para cubrir la demanda total de 10000 unidades.

2. Comparativa Cuantitativa de Optimalidad entre Tramos:
   * Frente al Tramo 1 (Costo: $102236.07):
     - El Tramo 4 genera un ahorro anual de $5415.23 (5.30% de ahorro neto).
     - Operar en el Tramo 1 resultaria un 5.59% mas costoso que la solucion optima.
   * Frente al Tramo 2 (Costo: $99212.50):
     - El Tramo 4 genera un ahorro anual de $2391.67 (2.41% de ahorro neto).
     - Operar en el Tramo 2 resultaria un 2.47% mas costoso que la solucion optima.
   * Frente al Tramo 3 (Costo: $97875.00):
     - El Tramo 4 genera un ahorro anual de $1054.17 (1.08% de ahorro neto).
     - Operar en el Tramo 3 resultaria un 1.09% mas costoso que la solucion optima.

3. Analisis Economico del Trade-Off (Costo de Pedido vs Almacenamiento vs Adquisicion):
   * Tramo 1 vs Tramo Optimo 4:
     Aunque en el Tramo 1 el costo de almacenamiento es menor por ordenar menos unidades,
     el descuento por volumen del Tramo 4 ahorra $7000.00 en adquisicion
     y $784.70 en pedidos, compensando con creces el incremento de $2369.47 en almacenamiento.
   * Tramo 2 vs Tramo Optimo 4:
     Aunque en el Tramo 2 el costo de almacenamiento es menor por ordenar menos unidades,
     el descuento por volumen del Tramo 4 ahorra $4000.00 en adquisicion
     y $666.67 en pedidos, compensando con creces el incremento de $2275.00 en almacenamiento.
   * Tramo 3 vs Tramo Optimo 4:
     Aunque en el Tramo 3 el costo de almacenamiento es menor por ordenar menos unidades,
     el descuento por volumen del Tramo 4 ahorra $2000.00 en adquisicion
     y $166.67 en pedidos, compensando con creces el incremento de $1112.50 en almacenamiento.
==================================================
```

---

## 7. Conclusión para la Hoja de Examen

> **CONCLUSIÓN DEL PROBLEMA (EJERCICIO 2):**
>
> 1. **Decisión y Tamaño de Lote Óptimo:** La empresa debe acogerse al **Tramo 4** de la escala de descuentos, realizando pedidos por un tamaño de lote de **$Q^* = 3,000$ unidades** para acceder al precio con el $7\%$ de descuento (**$\$9.30$ por unidad**).
> 2. **Costo Total Mínimo:** Esta política arroja el **Costo Total Anual Mínimo de $\$96,820.83$**, compuesto por $\$333.33$ en emisión de órdenes (3.33 pedidos/año), $\$3,487.50$ en almacenamiento físico del inventario, y $\$93,000.00$ en costo directo de adquisición del producto.
> 3. **Justificación Cuantitativa (Trade-Off):** Aunque ordenar lotes grandes incrementa el costo de almacenaje en $\$2,369.47$ respecto al Tramo 1 (sin descuento), el descuento por volumen produce un ahorro de $\$7,000.00$ en compras y $\$784.70$ en órdenes, resultando en un **ahorro neto anual de $\$5,415.24$ ($5.30\%$)** a favor de la empresa.
