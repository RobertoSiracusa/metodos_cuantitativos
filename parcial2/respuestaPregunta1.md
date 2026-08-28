# Parcial II — Ejercicio 1: Modelo EOQ Clásico (Productos Electrónicos)

**Universidad José Antonio Páez — Facultad de Ingeniería**  
**Escuela de Ingeniería en Computación**  
**Cátedra:** Métodos Cuantitativos — Teoría de Inventarios  
**Profesor:** Argenis  
**Período:** Junio 2025 / Agosto 2026  

---

## 1. Enunciado del Problema

> **Una empresa distribuye productos electrónicos con una demanda anual de 6,000 unidades. El costo por pedido es de $50 y el precio del producto es de $20 por unidad, y el costo de almacenamiento anual se estima como el 20% del costo del producto. La demanda diaria es de 20 unidades y el tiempo de entrega es de 5 días. (Resolver en hoja de examen)**  
> - **a)** Determine la cantidad óptima de pedido (EOQ). *(1.5 ptos)*  
> - **b)** Calcule el punto de reorden. *(1.5 ptos)*  
> - **c)** ¿Cuál es el costo total anual del sistema de inventario (solo pedidos + mantenimiento)? *(1.5 ptos)*  
> - **d)** ¿Cuántos pedidos se deben realizar en el año? *(1.5 ptos)*  

---

## 2. Identificación y Tabla de Datos

| Variable | Símbolo | Valor | Unidades | Descripción |
| :--- | :---: | :---: | :---: | :--- |
| **Demanda Anual** | $D$ | 6,000 | unidades/año | Demanda constante conocida |
| **Costo por Pedido** | $S$ ($K$) | 50.00 | \$/pedido | Costo fijo de emisión y transporte |
| **Precio Unitario del Producto** | $C$ | 20.00 | \$/unidad | Costo de adquisición unitario |
| **Tasa Anual de Almacenamiento** | $i$ | 20% (0.20) | anual | Porcentaje del valor del artículo |
| **Costo Unitario de Almacenamiento** | $H$ ($C_m$) | 4.00 | \$/unidad/año | $H = i \cdot C = 0.20 \times 20 = \$4.00$ |
| **Demanda Diaria** | $d$ | 20 | unidades/día | Consumo diario promedio |
| **Tiempo de Entrega (Lead Time)** | $L$ | 5 | días | Plazo de entrega del proveedor |

---

## 3. Desarrollo Matemático Paso a Paso (Formato Hoja de Examen)

### Literal a) Cantidad Óptima de Pedido (EOQ / $Q^*$)

Se aplica la fórmula clásica del Lote Económico de Wilson para demanda determinística:

$$Q^* = \sqrt{\frac{2 \cdot D \cdot S}{H}}$$

**Sustitución de valores:**
$$Q^* = \sqrt{\frac{2 \cdot (6000\text{ unid}) \cdot (\$50)}{4\text{ \$/unid/año}}}$$

$$Q^* = \sqrt{\frac{600000}{4}} = \sqrt{150000} \approx \mathbf{387.30\text{ unidades}}$$

*(Valor analítico exacto: $Q^* = 50\sqrt{60} \approx 387.2983$ unidades).*

---

### Literal b) Punto de Reorden ($ROP$)

El punto de reorden indica el nivel de stock en el cual se debe colocar un nuevo pedido para no incurrir en quiebre de inventario durante el tiempo de entrega del proveedor ($L$):

$$ROP = d \cdot L$$

**Sustitución de valores:**
$$ROP = (20\text{ unidades/día}) \cdot (5\text{ días}) = \mathbf{100.00\text{ unidades}}$$

**Interpretación:** Tan pronto el inventario disponible descienda a **100 unidades**, debe emitirse inmediatamente una nueva orden de compra por **387 unidades**.

---

### Literal c) Costo Total Anual del Sistema de Inventario (Solo Pedidos + Mantenimiento)

La función de costo relevante del sistema de inventario está compuesta por la suma del costo anual de ordenar más el costo anual de almacenar:

$$CT_{\text{inv}}(Q^*) = CP + CA = \left( \frac{D}{Q^*} \right) S + \left( \frac{Q^*}{2} \right) H$$

#### 1. Costo Anual de Emitir Pedidos ($CP$):
$$CP = \left( \frac{6000}{387.2983} \right) \cdot 50 = (15.4919) \cdot 50 = \mathbf{\$774.60\text{ /año}}$$

#### 2. Costo Anual de Almacenamiento / Mantenimiento ($CA$):
$$CA = \left( \frac{387.2983}{2} \right) \cdot 4 = (193.6492) \cdot 4 = \mathbf{\$774.60\text{ /año}}$$

#### 3. Costo Total de Gestión de Inventario:
$$CT_{\text{inv}} = \$774.60 + \$774.60 = \mathbf{\$1,549.19\text{ /año}}$$

*(Nótese que en el lote óptimo $Q^*$, el costo de ordenar iguala exactamente al costo de almacenar: $CP = CA = \$774.60$).*

*(Nota complementaria: Si se incluye el costo de compra o adquisición del producto $CADQ = D \cdot C = 6000 \cdot \$20 = \$120,000.00$, el Costo Total General es $CT = \$120,000.00 + \$1,549.19 = \mathbf{\$121,549.19\text{ /año}}$).*

---

### Literal d) Número de Pedidos al Año ($N$) y Frecuencia ($T$)

#### 1. Número de pedidos a emitir en el año:
$$N = \frac{D}{Q^*} = \frac{6000}{387.2983} \approx \mathbf{15.49\text{ pedidos/año}}$$

*(Aproximadamente 15 a 16 órdenes anuales).*

#### 2. Frecuencia / Tiempo entre pedidos ($T$):
$$T_{\text{años}} = \frac{Q^*}{D} = \frac{387.2983}{6000} = \mathbf{0.0645\text{ años}}$$

$$T_{\text{meses}} = 0.0645 \times 12\text{ meses} = \mathbf{0.77\text{ meses}}$$

$$T_{\text{días}} = 0.0645 \times 360\text{ días} \approx \mathbf{23.24\text{ días}}$$

---

## 4. Comando de Ejecución del Programa en Python

Desde el directorio `parcial2/`:

```bash
python3 main.py --ejercicio1
```

---

## 5. Salida Oficial del Programa (`.txt`)

```text
==================================================
   REPORTE DE INVENTARIO: MODELO EOQ CLASICO
==================================================
Parametros de Entrada:
 - Demanda (Anual): 6000.00 unidades
 - Demanda Anualizada (D): 6000.00 unidades/ano
 - Costo de Pedido (S/K): $50.00
 - Tasa de Mantenimiento Anual (i%): 20.00%
 - Costo de Mantenimiento Unitario (H): $4.00/unidad/ano
 - Costo Unitario del Producto (C): $20.00

Resultados del Calculo:
 - Cantidad Economica de Pedido (EOQ / Q*): 387.30 unidades
 - Numero de Pedidos al Ano (N): 15.49 pedidos/ano
 - Frecuencia entre Pedidos (T = Q/D): 0.77 meses (0.0645 anos)

Desglose de Costos Anuales:
 - Costo de Pedidos: $774.60
 - Costo de Almacenamiento: $774.60
 - Costo de Adquisicion (Producto): $120000.00
 - Costo Total Anual (CT): $121549.19
==================================================
Respuestas Especificas a los Literales del Examen:
--------------------------------------------------
 a) Cantidad Optima de Pedido (EOQ): 387.30 unidades
 b) Punto de Reorden (ROP = d * L = 20 * 5): 100.00 unidades
 c) Costo Total Anual del Sistema (solo pedidos + mantenimiento): $1549.19
    (Costo Total incluyendo adquisicion: $121549.19)
 d) Numero de Pedidos al Ano (N = D / Q*): 15.49 pedidos/ano
    (Frecuencia: cada 0.77 meses o 23.2 dias)
==================================================
```

---

## 6. Cuadro Resumen de Resultados Finales

| Literal | Pregunta del Examen | Fórmula Empleada | Valor Obtenido | Unidades |
| :---: | :--- | :---: | :---: | :---: |
| **a** | Cantidad Óptima de Pedido (EOQ) | $Q^* = \sqrt{\frac{2DS}{H}}$ | **387.30** | unidades |
| **b** | Punto de Reorden | $ROP = d \cdot L$ | **100.00** | unidades |
| **c** | Costo Total Anual del Sistema | $CT_{\text{inv}} = CP + CA$ | **\$1,549.19** | \$/año |
| **c.1** | *Costo de Pedidos Anual* | $CP = (D/Q^*) \cdot S$ | \$774.60 | \$/año |
| **c.2** | *Costo de Almacenaje Anual* | $CA = (Q^*/2) \cdot H$ | \$774.60 | \$/año |
| **d** | Número de Pedidos al Año | $N = D / Q^*$ | **15.49** | pedidos/año |
| **d.1** | *Tiempo entre Pedidos* | $T = (Q^*/D) \cdot 12$ | **0.77** | meses (~23 días) |

---

## 7. Conclusión para la Hoja de Examen

> **RESPUESTAS CONSOLIDADAS PARA EL EXAMEN:**
>
> 1. **Cantidad Óptima de Pedido ($EOQ$):** El tamaño de lote que minimiza los costos combinados de pedidos y almacenamiento es de **$387.30$ unidades** (aproximadamente $387$ unidades por orden).
> 2. **Punto de Reorden ($ROP$):** Se debe emitir una nueva orden de reabastecimiento en el momento exacto en que el nivel de existencias en almacén descienda a **$100$ unidades**, garantizando la cobertura de las $20$ unidades diarias requeridas durante los $5$ días de entrega.
> 3. **Costo Total del Sistema:** El costo anual mínimo de operación del sistema de inventario (pedidos + almacenamiento) es de **$\$1,549.19$ al año** (desglosado equitativamente en $\$774.60$ de emisión de órdenes y $\$774.60$ de mantenimiento físico).
> 4. **Frecuencia de Reabastecimiento:** La empresa debe colocar un total de **$15.49$ pedidos al año**, lo que equivale operativamente a emitir un pedido cada **$0.77$ meses** (aproximadamente cada **$23$ días** hábiles).
