import math

def calcular_eoq(demanda_anual, costo_pedido, costo_almacenamiento_unitario):
    """Calcula la Cantidad Economica de Pedido (EOQ) clasica."""
    return math.sqrt((2 * demanda_anual * costo_pedido) / costo_almacenamiento_unitario)

def calcular_costo_total(demanda_anual, costo_pedido, costo_almacenamiento_unitario, precio_unidad, Q):
    """Calcula el costo total anual (pedidos + almacenamiento + adquisicion)."""
    costo_pedido_total = (demanda_anual / Q) * costo_pedido
    costo_almacenamiento_total = (Q / 2) * costo_almacenamiento_unitario
    costo_producto_total = demanda_anual * precio_unidad
    return costo_pedido_total + costo_almacenamiento_total + costo_producto_total

def calcular_quiebre_precios(demanda_anual, costo_pedido, costo_almacenamiento_porcentaje, tramos):
    """
    Resuelve el modelo de quiebre de precios (descuentos por cantidad).
    Retorna un diccionario con el desglose de resultados de cada tramo y el optimo global.
    """
    resultados_tramos = []
    
    for i, (lim_inf, lim_sup, precio_unidad) in enumerate(tramos):
        lim_sup_val = float('inf') if (lim_sup is None or lim_sup == 'inf' or lim_sup == float('inf')) else float(lim_sup)
        lim_inf_val = float(lim_inf)
        
        costo_almacenamiento_unitario = (costo_almacenamiento_porcentaje / 100.0) * precio_unidad
        Q_calc = calcular_eoq(demanda_anual, costo_pedido, costo_almacenamiento_unitario)
        
        if lim_inf_val <= Q_calc <= lim_sup_val:
            Q_ajustada = Q_calc
            factible = True
            estado = "Factible (EOQ en rango)"
        elif Q_calc < lim_inf_val:
            Q_ajustada = lim_inf_val
            factible = True
            estado = "Ajustado al Limite Inferior"
        else:
            Q_ajustada = None
            factible = False
            estado = "No Factible (EOQ excede limite superior)"
            
        if factible:
            costo_total = calcular_costo_total(demanda_anual, costo_pedido, costo_almacenamiento_unitario, precio_unidad, Q_ajustada)
        else:
            costo_total = None
            
        resultados_tramos.append({
            "tramo": i + 1,
            "limite_inferior": lim_inf_val,
            "limite_superior": lim_sup_val,
            "precio_unidad": precio_unidad,
            "eoq_calculado": Q_calc,
            "cantidad_ajustada": Q_ajustada,
            "costo_total": costo_total,
            "estado": estado,
            "factible": factible
        })
        
    tramos_factibles = [r for r in resultados_tramos if r["factible"]]
    
    if tramos_factibles:
        mejor_tramo = min(tramos_factibles, key=lambda x: x["costo_total"])
        optimo = {
            "cantidad": mejor_tramo["cantidad_ajustada"],
            "costo_total": mejor_tramo["costo_total"],
            "tramo": mejor_tramo["tramo"],
            "precio_aplicado": mejor_tramo["precio_unidad"]
        }
    else:
        optimo = None
        
    return {
        "resultados": resultados_tramos,
        "optimo": optimo
    }

class ModeloQuiebrePrecios:
    """
    Clase que encapsula el modelo de quiebre de precios (descuentos por volumen).
    Sigue el paradigma de Programacion Orientada a Objetos.
    """
    def __init__(self, demanda_anual, costo_pedido, costo_almacenamiento_porcentaje, tramos):
        self.demanda_anual = demanda_anual
        self.costo_pedido = costo_pedido
        self.costo_almacenamiento_porcentaje = costo_almacenamiento_porcentaje
        self.tramos = tramos
        
        # Resultados
        self.resultados_tramos = []
        self.optimo = None

    def calcular(self):
        res = calcular_quiebre_precios(self.demanda_anual, self.costo_pedido, self.costo_almacenamiento_porcentaje, self.tramos)
        self.resultados_tramos = res["resultados"]
        self.optimo = res["optimo"]

    def generar_reporte(self) -> str:
        reporte = (
            "==================================================\n"
            "   REPORTE DE INVENTARIO: QUIEBRE DE PRECIOS\n"
            "==================================================\n"
            "Parametros de Entrada:\n"
            f" - Demanda Anual (D): {self.demanda_anual:.2f} unidades\n"
            f" - Costo de Pedido (S/K): ${self.costo_pedido:.2f}\n"
            f" - Costo Almacenaje Anual (%): {self.costo_almacenamiento_porcentaje:.2f}%\n\n"
            "Desglose de Tramos:\n"
        )
        
        for r in self.resultados_tramos:
            lim_sup_str = "inf" if r["limite_superior"] == float('inf') else f"{r['limite_superior']:.0f}"
            rango = f"{r['limite_inferior']:.0f} a {lim_sup_str}"
            
            reporte += (
                f" Tramo {r['tramo']} [{rango}] @ ${r['precio_unidad']:.2f}/unidad:\n"
                f"   * EOQ Teorico: {r['eoq_calculado']:.2f}\n"
                f"   * Estado: {r['estado']}\n"
            )
            if r['factible']:
                c_pedidos = (self.demanda_anual / r["cantidad_ajustada"]) * self.costo_pedido
                c_almacenaje = (r["cantidad_ajustada"] / 2) * ((self.costo_almacenamiento_porcentaje / 100.0) * r["precio_unidad"])
                c_producto = self.demanda_anual * r["precio_unidad"]
                reporte += (
                    f"   * Cantidad Ajustada: {r['cantidad_ajustada']:.2f}\n"
                    f"   * Costo Anual de Pedidos: ${c_pedidos:.2f}\n"
                    f"   * Costo Anual de Almacenamiento: ${c_almacenaje:.2f}\n"
                    f"   * Costo Anual de Adquisicion: ${c_producto:.2f}\n"
                    f"   * Costo Anual Total: ${r['costo_total']:.2f}\n"
                )
            else:
                reporte += "   * Cantidad Ajustada: N/A (Descartado)\n"
            reporte += "\n"
            
        reporte += "==================================================\n"
        if self.optimo:
            opt_tramo_num = self.optimo["tramo"]
            opt_costo = self.optimo["costo_total"]
            opt_cant = self.optimo["cantidad"]
            opt_precio = self.optimo["precio_aplicado"]
            n_pedidos = self.demanda_anual / opt_cant

            reporte += (
                "                 OPTIMO RECOMENDADO\n"
                "==================================================\n"
                f" - Cantidad Optima a Ordenar (Q*): {opt_cant:.2f} unidades\n"
                f" - Tramo Optimo: Tramo {opt_tramo_num}\n"
                f" - Precio Aplicable: ${opt_precio:.2f}/unidad\n"
                f" - Costo Minimo Total Anual: ${opt_costo:.2f}\n"
                "==================================================\n"
                "       INTERPRETACION Y ANALISIS DE DECISION\n"
                "==================================================\n"
                f"1. Conclusion General:\n"
                f"   El Tramo {opt_tramo_num} es la alternativa economicamente optima con un lote de {opt_cant:.2f} unidades\n"
                f"   a un precio de ${opt_precio:.2f}/unidad, logrando el Costo Total Anual minimo de ${opt_costo:.2f}.\n"
                f"   Se recomienda realizar {n_pedidos:.2f} pedidos al ano para cubrir la demanda total de {self.demanda_anual:.0f} unidades.\n\n"
                f"2. Comparativa Cuantitativa de Optimalidad entre Tramos:\n"
            )

            for r in self.resultados_tramos:
                t_num = r["tramo"]
                if t_num == opt_tramo_num:
                    continue
                if r["factible"]:
                    diferencia_costo = r["costo_total"] - opt_costo
                    pct_ahorro = (diferencia_costo / r["costo_total"]) * 100.0
                    pct_mas_caro = (diferencia_costo / opt_costo) * 100.0
                    
                    reporte += (
                        f"   * Frente al Tramo {t_num} (Costo: ${r['costo_total']:.2f}):\n"
                        f"     - El Tramo {opt_tramo_num} genera un ahorro anual de ${diferencia_costo:.2f} ({pct_ahorro:.2f}% de ahorro neto).\n"
                        f"     - Operar en el Tramo {t_num} resultaria un {pct_mas_caro:.2f}% mas costoso que la solucion optima.\n"
                    )
                else:
                    reporte += (
                        f"   * Frente al Tramo {t_num} [{r['estado']}]:\n"
                        f"     - Tramo descartado por no factibilidad operativa (el EOQ calculado excede los limites validos).\n"
                    )

            reporte += (
                f"\n3. Analisis Economico del Trade-Off (Costo de Pedido vs Almacenamiento vs Adquisicion):\n"
            )
            c_ped_opt = (self.demanda_anual / opt_cant) * self.costo_pedido
            c_alm_opt = (opt_cant / 2) * ((self.costo_almacenamiento_porcentaje / 100.0) * opt_precio)
            c_adq_opt = self.demanda_anual * opt_precio

            for r in self.resultados_tramos:
                t_num = r["tramo"]
                if t_num == opt_tramo_num:
                    continue
                if r["factible"]:
                    c_ped_t = (self.demanda_anual / r["cantidad_ajustada"]) * self.costo_pedido
                    c_alm_t = (r["cantidad_ajustada"] / 2) * ((self.costo_almacenamiento_porcentaje / 100.0) * r["precio_unidad"])
                    c_adq_t = self.demanda_anual * r["precio_unidad"]
                    
                    dif_adq = c_adq_t - c_adq_opt
                    dif_ped = c_ped_t - c_ped_opt
                    dif_alm = c_alm_t - c_alm_opt
                    
                    if r["precio_unidad"] > opt_precio:
                        reporte += (
                            f"   * Tramo {t_num} vs Tramo Optimo {opt_tramo_num}:\n"
                            f"     Aunque en el Tramo {t_num} el costo de almacenamiento es menor por ordenar menos unidades,\n"
                            f"     el descuento por volumen del Tramo {opt_tramo_num} ahorra ${dif_adq:.2f} en adquisicion\n"
                            f"     y ${dif_ped:.2f} en pedidos, compensando con creces el incremento de ${-dif_alm:.2f} en almacenamiento.\n"
                        )
                    elif r["precio_unidad"] < opt_precio:
                        reporte += (
                            f"   * Tramo {t_num} vs Tramo Optimo {opt_tramo_num}:\n"
                            f"     Aunque el Tramo {t_num} ofrece un precio unitario menor (${r['precio_unidad']:.2f} vs ${opt_precio:.2f}),\n"
                            f"     exige ordenar un lote muy elevado ({r['cantidad_ajustada']:.2f} unidades) para acceder al descuento,\n"
                            f"     lo que incrementa el costo de almacenamiento en ${dif_alm:.2f}. Dicho costo de posesion\n"
                            f"     supera el ahorro conjunto en compra (${-dif_adq:.2f}) y pedidos (${-dif_ped:.2f}), haciendo que el Tramo {t_num} sea menos conveniente.\n"
                        )
                    else:
                        reporte += (
                            f"   * Tramo {t_num} vs Tramo Optimo {opt_tramo_num}:\n"
                            f"     Ambos tienen el mismo precio base, pero el lote del Tramo {opt_tramo_num} equilibra mejor pedidos y almacenamiento.\n"
                        )
        else:
            reporte += " No se encontro ninguna solucion factible.\n"
        reporte += "==================================================\n"
        
        return reporte
