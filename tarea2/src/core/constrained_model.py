import math

def calcular_lambda_aproximado(demandas, costos_pedido, costos_almacenamiento, areas, capacidad_total):
    """
    Calcula el valor aproximado de Lambda usando la formula clasica de Investigacion de Operaciones (Hamdy Taha):
    lambda approx (n^2 * a_prom * CpD_prom / A^2) - (Cm_prom / 2 * a_prom)
    """
    n = len(demandas)
    cm_prom = sum(costos_almacenamiento) / n
    a_prom = sum(areas) / n if sum(areas) > 0 else 1.0
    cpd_prom = sum(costos_pedido[i] * demandas[i] for i in range(n)) / n
    A = capacidad_total
    
    if A <= 0 or a_prom <= 0:
        return 0.0
        
    term1 = (n**2 * a_prom * cpd_prom) / (A**2)
    term2 = cm_prom / (2 * a_prom)
    
    lambda_aprox = term1 - term2
    return max(0.0, lambda_aprox)

def resolver_restricciones_lagrange(articulos, demandas, costos_pedido, costos_almacenamiento, areas, capacidad_total, presupuesto, usar_aprox=False):
    """
    Resuelve el modelo de inventario multi-articulo con restricciones de almacenamiento (area) y presupuesto
    usando Multiplicadores de Lagrange (Exacto o Formula Aproximada).
    """
    n = len(articulos)
    if areas is None or len(areas) != n:
        areas = [1.0] * n
        
    eoqs = [math.sqrt((2 * demandas[i] * costos_pedido[i]) / costos_almacenamiento[i]) for i in range(n)]
    
    espacio_usado_eoq = sum(areas[i] * eoqs[i] for i in range(n))
    costo_total_inv_eoq = sum((demandas[i] / eoqs[i]) * costos_pedido[i] + (eoqs[i] / 2) * costos_almacenamiento[i] for i in range(n))
    
    if espacio_usado_eoq <= capacidad_total and costo_total_inv_eoq <= presupuesto:
        return {
            "status": "Optimal (Sin restricciones activas)",
            "cantidades": eoqs,
            "costo_total": costo_total_inv_eoq,
            "lambda_espacio": 0.0,
            "lambda_aprox": 0.0,
            "factor_ajuste": 1.0,
            "explicacion": "Los lotes EOQ cumplen todas las capacidades y presupuesto sin requerir ajustes."
        }
        
    lambda_aprox = calcular_lambda_aproximado(demandas, costos_pedido, costos_almacenamiento, areas, capacidad_total)
    
    if espacio_usado_eoq > capacidad_total:
        if usar_aprox:
            lambda_opt = lambda_aprox
        else:
            low, high = 0.0, 10000.0
            for _ in range(100):
                mid = (low + high) / 2.0
                q_test = [math.sqrt((2 * demandas[i] * costos_pedido[i]) / (costos_almacenamiento[i] + 2 * mid * areas[i])) for i in range(n)]
                if sum(areas[i] * q_test[i] for i in range(n)) > capacidad_total:
                    low = mid
                else:
                    high = mid
            lambda_opt = (low + high) / 2.0
            
        q_opt = [math.sqrt((2 * demandas[i] * costos_pedido[i]) / (costos_almacenamiento[i] + 2 * lambda_opt * areas[i])) for i in range(n)]
        c_tot = sum((demandas[i] / q_opt[i]) * costos_pedido[i] + (q_opt[i] / 2) * costos_almacenamiento[i] for i in range(n))
        
        tipo_lbl = "Aproximado" if usar_aprox else "Exacto"
        return {
            "status": f"Optimal (Restriccion de Area Activa - {tipo_lbl})",
            "cantidades": q_opt,
            "costo_total": c_tot,
            "lambda_espacio": lambda_opt,
            "lambda_aprox": lambda_aprox,
            "factor_ajuste": sum(areas[i] * q_opt[i] for i in range(n)) / espacio_usado_eoq,
            "explicacion": f"Lotes ajustados con multiplicador de Lagrange lambda = {lambda_opt:.4f} (lambda aprox = {lambda_aprox:.4f}) para cumplir el limite de {capacidad_total:.1f} m2."
        }
        
    factor = presupuesto / costo_total_inv_eoq
    q_opt = [eoqs[i] * factor for i in range(n)]
    c_tot = sum((demandas[i] / q_opt[i]) * costos_pedido[i] + (q_opt[i] / 2) * costos_almacenamiento[i] for i in range(n))
    
    return {
        "status": "Optimal (Restriccion de Presupuesto Activa)",
        "cantidades": q_opt,
        "costo_total": c_tot,
        "lambda_espacio": 0.0,
        "lambda_aprox": lambda_aprox,
        "factor_ajuste": factor,
        "explicacion": "Lotes ajustados para no exceder el presupuesto maximo disponible."
    }

class ModeloRestriccionesInventario:
    """
    Clase que encapsula el modelo de inventarios de multiples articulos con restricciones.
    Sigue el paradigma de Programacion Orientada a Objetos.
    """
    def __init__(self, articulos, demandas, costos_pedido, costos_almacenamiento, 
                 capacidad_total, presupuesto, demandas_diarias, tiempos_entrega, 
                 areas=None, metodo="Multiplicadores de Lagrange (Exacto)"):
        self.articulos = articulos
        self.demandas = demandas
        self.costos_pedido = costos_pedido
        self.costos_almacenamiento = costos_almacenamiento
        self.capacidad_total = capacidad_total
        self.presupuesto = presupuesto
        self.demandas_diarias = demandas_diarias
        self.tiempos_entrega = tiempos_entrega
        self.areas = areas if areas is not None else [1.0] * len(articulos)
        self.metodo = metodo
        
        # Resultados a calcular
        self.status = "No calculado"
        self.costo_total = 0.0
        self.costo_mantenimiento = 0.0
        self.costo_pedidos = 0.0
        self.resultados_articulos = {}
        self.espacio_utilizado = 0.0
        self.presupuesto_utilizado = 0.0
        self.explicacion_heuristica = ""
        self.factor_ajuste = 1.0
        self.lambda_calculado = 0.0
        self.lambda_aprox = 0.0
        self.espacio_eoq_total = 0.0
        self.costo_total_eoq = 0.0

    def calcular(self):
        n = len(self.articulos)
        eoqs = [math.sqrt((2 * self.demandas[i] * self.costos_pedido[i]) / self.costos_almacenamiento[i]) for i in range(n)]
        self.espacio_eoq_total = sum(self.areas[i] * eoqs[i] for i in range(n))
        self.costo_total_eoq = sum((self.demandas[i] / eoqs[i]) * self.costos_pedido[i] + (eoqs[i] / 2) * self.costos_almacenamiento[i] for i in range(n))
        
        if "Lagrange" in self.metodo:
            usar_aprox = "Aproximad" in self.metodo
            res = resolver_restricciones_lagrange(
                self.articulos, self.demandas, self.costos_pedido, self.costos_almacenamiento,
                self.areas, self.capacidad_total, self.presupuesto, usar_aprox=usar_aprox
            )
            self.status = res["status"]
            self.explicacion_heuristica = res["explicacion"]
            self.factor_ajuste = res["factor_ajuste"]
            self.lambda_calculado = res["lambda_espacio"]
            self.lambda_aprox = res.get("lambda_aprox", 0.0)
            q_optimas = res["cantidades"]
        else:
            espacio_usado_eoq = self.espacio_eoq_total
            costos_totales_eoq = self.costo_total_eoq
            
            self.factor_ajuste = 1.0
            self.explicacion_heuristica = "Cumple con las restricciones sin ajustes."
            
            if espacio_usado_eoq > self.capacidad_total:
                self.factor_ajuste = min(self.factor_ajuste, self.capacidad_total / espacio_usado_eoq)
                self.explicacion_heuristica = "Ajustado proporcionalmente por restriccion de Espacio."
                
            if costos_totales_eoq > self.presupuesto:
                self.factor_ajuste = min(self.factor_ajuste, self.presupuesto / costos_totales_eoq)
                self.explicacion_heuristica = "Ajustado proporcionalmente por restriccion de Presupuesto."
                
            self.status = "Optimal (Heuristica de Escalamiento)"
            q_optimas = [eoqs[i] * self.factor_ajuste for i in range(n)]

        self.costo_total = 0.0
        self.costo_mantenimiento = 0.0
        self.costo_pedidos = 0.0
        self.espacio_utilizado = sum(self.areas[i] * q_optimas[i] for i in range(n))
        self.resultados_articulos = {}
        
        for i in range(n):
            q_opt = q_optimas[i]
            rop = self.demandas_diarias[i] * self.tiempos_entrega[i]
            
            c_ped = (self.demandas[i] / q_opt) * self.costos_pedido[i]
            c_mant = (q_opt / 2) * self.costos_almacenamiento[i]
            
            self.costo_pedidos += c_ped
            self.costo_mantenimiento += c_mant
            self.costo_total += (c_ped + c_mant)
            
            self.resultados_articulos[self.articulos[i]] = {
                "articulo": self.articulos[i],
                "area_unit": self.areas[i],
                "cantidad_pedir": q_opt,
                "rop": rop,
                "eoq_clasico": eoqs[i]
            }
            
        self.presupuesto_utilizado = self.costo_total

    def generar_reporte(self) -> str:
        reporte = (
            "==================================================\n"
            "   REPORTE DE INVENTARIO: MULTI-ARTICULO CON REST.\n"
            "==================================================\n"
            "Parametros Globales:\n"
            f" - Presupuesto Maximo ($): ${self.presupuesto:.2f}\n"
            f" - Capacidad Almacenamiento (Area / Q Max): {self.capacidad_total:.2f} m2 (o unidades)\n"
            f" - Metodo Utilizado: {self.metodo}\n"
            f" - Estado de Solucion: {self.status}\n"
        )
        if self.lambda_calculado > 0:
            reporte += f" - Multiplicador de Lagrange lambda: {self.lambda_calculado:.4f} (lambda aprox: {self.lambda_aprox:.4f})\n"
        if self.explicacion_heuristica:
            reporte += f" - Diagnostico: {self.explicacion_heuristica} (Factor Ajuste: {self.factor_ajuste:.4f})\n"
        
        reporte += (
            "\nDetalles por Articulo:\n"
            "--------------------------------------------------\n"
        )
        for art in self.articulos:
            info = self.resultados_articulos[art]
            idx = self.articulos.index(art)
            eoq_c = info.get("eoq_clasico", math.sqrt((2 * self.demandas[idx] * self.costos_pedido[idx]) / self.costos_almacenamiento[idx]))
            
            reporte += (
                f" Articulo {art}:\n"
                f"   * Demanda Anual (D): {self.demandas[idx]:.0f} unidades\n"
                f"   * Costo Pedido (S/Cp): ${self.costos_pedido[idx]:.2f}\n"
                f"   * Costo Almacenaje (H/Cm): ${self.costos_almacenamiento[idx]:.2f}\n"
                f"   * Area Unit. (a): {self.areas[idx]:.2f} m2\n"
                f"   * EOQ Clasico sin restriccion: {eoq_c:.2f}\n"
                f"   * Cantidad Optima Ajustada (Q*): {info['cantidad_pedir']:.2f}\n"
                f"   * Punto de Reorden (ROP): {info['rop']:.2f} unidades\n"
                "\n"
            )
            
        reporte += (
            "==================================================\n"
            "                RESUMEN DE USO\n"
            "==================================================\n"
            f" - Presupuesto Utilizado: ${self.presupuesto_utilizado:.2f} de ${self.presupuesto:.2f}\n"
            f" - Espacio Almacenamiento Utilizado: {self.espacio_utilizado:.2f} de {self.capacidad_total:.2f} m2\n"
            f" - Costo Total de Almacenamiento Anual: ${self.costo_mantenimiento:.2f}\n"
            f" - Costo Total de Pedidos Anual: ${self.costo_pedidos:.2f}\n"
            f" - Costo Total Anual Optimizado: ${self.costo_total:.2f}\n"
            "==================================================\n"
            "       INTERPRETACION Y ANALISIS DE DECISION\n"
            "==================================================\n"
        )
        
        pct_espacio = (self.espacio_utilizado / self.capacidad_total) * 100.0 if self.capacidad_total > 0 else 0.0
        pct_presupuesto = (self.presupuesto_utilizado / self.presupuesto) * 100.0 if self.presupuesto > 0 else 0.0
        holgura_espacio = max(0.0, self.capacidad_total - self.espacio_utilizado)
        holgura_presupuesto = max(0.0, self.presupuesto - self.presupuesto_utilizado)
        diferencia_costo = self.costo_total - self.costo_total_eoq
        pct_incremento_costo = (diferencia_costo / self.costo_total_eoq) * 100.0 if self.costo_total_eoq > 0 else 0.0
        
        if self.lambda_calculado > 0 or self.factor_ajuste < 0.9999:
            if "Area" in self.status or "Espacio" in self.explicacion_heuristica or self.lambda_calculado > 0:
                reporte += (
                    "1. Diagnostico de Restriccion de Capacidad de Almacenamiento:\n"
                    f"   - La solucion ideal (EOQ clasico) requeria {self.espacio_eoq_total:.2f} m2 de almacen,\n"
                    f"     lo que excedia la capacidad disponible de {self.capacidad_total:.2f} m2 en {self.espacio_eoq_total - self.capacidad_total:.2f} m2.\n"
                    f"   - Se ajustaron los lotes de pedido (factor de escala ~{self.factor_ajuste:.4f}) reduciendo el inventario promedio\n"
                    f"     para cumplir estrictamente con el limite fisico de {self.capacidad_total:.2f} m2 (100.00% de ocupacion).\n"
                )
                if self.lambda_calculado > 0:
                    reporte += (
                        f"   - Interpretacion del Multiplicador de Lagrange (Precio Sombra lambda = {self.lambda_calculado:.4f}):\n"
                        f"     Por cada 1 m2 adicional que se amplie la capacidad de almacenamiento, el costo total anual\n"
                        f"     de inventario se reduciria en aproximadamente ${self.lambda_calculado:.4f} al ano.\n"
                    )
            elif "Presupuesto" in self.status or "Presupuesto" in self.explicacion_heuristica:
                reporte += (
                    "1. Diagnostico de Restriccion Presupuestaria:\n"
                    f"   - Los lotes sin restricciones requerian un costo anual de ${self.costo_total_eoq:.2f},\n"
                    f"     superando el presupuesto asignado de ${self.presupuesto:.2f}.\n"
                    f"   - Se redujeron los lotes con un factor de {self.factor_ajuste:.4f} para operar dentro del limite financiero.\n"
                )
            
            reporte += (
                f"\n2. Impacto Economico de las Restricciones (Costo de Oportunidad):\n"
                f"   - Costo Total Ideal (Sin Restricciones): ${self.costo_total_eoq:.2f}\n"
                f"   - Costo Total Optimizado (Con Restricciones): ${self.costo_total:.2f}\n"
                f"   - Sobrecosto por restriccion: ${diferencia_costo:.2f} (+{pct_incremento_costo:.2f}% de incremento debido a pedidos mas frecuentes).\n"
            )
        else:
            reporte += (
                "1. Diagnostico de Restricciones y Holguras:\n"
                f"   - Los lotes economicos (EOQ) operan con holgura completa sin violar ninguna restriccion:\n"
                f"     * Espacio utilizado: {self.espacio_utilizado:.2f} m2 de {self.capacidad_total:.2f} m2 ({pct_espacio:.2f}% ocupado | {holgura_espacio:.2f} m2 libres / {100-pct_espacio:.2f}% de holgura).\n"
                f"     * Presupuesto utilizado: ${self.presupuesto_utilizado:.2f} de ${self.presupuesto:.2f} ({pct_presupuesto:.2f}% utilizado | ${holgura_presupuesto:.2f} disponibles / {100-pct_presupuesto:.2f}% de holgura).\n"
                f"   - La solucion obtenida es 100% optima a nivel global (Multiplicador de Lagrange lambda = 0.0000), sin sobrecosto ni penalizacion por capacidad o presupuesto.\n"
            )
            
        reporte += (
            f"\n2. Resumen Operativo de Politicas de Inventario por Articulo:\n"
        )
        for art in self.articulos:
            info = self.resultados_articulos[art]
            idx = self.articulos.index(art)
            q_ped = info['cantidad_pedir']
            n_ped = self.demandas[idx] / q_ped if q_ped > 0 else 0
            t_meses = (q_ped / self.demandas[idx]) * 12.0 if self.demandas[idx] > 0 else 0
            
            det_art = f"   * Articulo {art}: Ordenar lotes de {q_ped:.2f} unidades cada {t_meses:.2f} meses ({n_ped:.2f} pedidos/ano)."
            if self.demandas_diarias[idx] > 0 and self.tiempos_entrega[idx] > 0:
                det_art += f" Punto de Reorden (ROP): {info['rop']:.2f} unidades."
            reporte += det_art + "\n"
            
        reporte += "==================================================\n"
        return reporte
