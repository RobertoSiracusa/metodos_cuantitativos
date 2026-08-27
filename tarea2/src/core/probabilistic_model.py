import math
from statistics import NormalDist

TABLA_Z_LIBROS = {
    0.50: 0.00,
    0.75: 0.67,
    0.80: 0.84,
    0.85: 1.04,
    0.90: 1.28,
    0.95: 1.65,
    0.96: 1.75,
    0.97: 1.88,
    0.98: 2.05,
    0.99: 2.33,
    0.995: 2.58,
    0.999: 3.09
}

def obtener_z(nivel_servicio: float, metodo: str = "tabla", z_personalizado: float = None) -> float:
    """
    Calcula o busca el valor Z segun el metodo seleccionado:
    - 'tabla': busca en la tabla estandar de libros de texto.
    - 'exacto': calcula la funcion inversa de la distribucion normal continua.
    - 'manual': usa un valor Z ingresado directamente.
    """
    if metodo == "manual" and z_personalizado is not None:
        return float(z_personalizado)
    
    if metodo == "tabla":
        ns_redondeado = round(nivel_servicio, 3)
        if ns_redondeado in TABLA_Z_LIBROS:
            return TABLA_Z_LIBROS[ns_redondeado]
        ns_dos_dec = round(nivel_servicio, 2)
        if ns_dos_dec in TABLA_Z_LIBROS:
            return TABLA_Z_LIBROS[ns_dos_dec]
            
    return NormalDist().inv_cdf(nivel_servicio)

def calcular_eoq(demanda_anual: float, costo_pedido: float, costo_mantenimiento_anual: float) -> float:
    """Calcula la Cantidad Economica de Pedido (EOQ)."""
    return math.sqrt((2 * demanda_anual * costo_pedido) / costo_mantenimiento_anual)

def calcular_rop(demanda_promedio_diaria: float, desviacion_estandar_demanda: float, 
                 tiempo_entrega: float, nivel_servicio: float, metodo_z: str = "tabla", z_manual: float = None) -> dict:
    """Calcula el punto de reorden (ROP) y el stock de seguridad utilizando el valor Z correspondiente."""
    z = obtener_z(nivel_servicio, metodo=metodo_z, z_personalizado=z_manual)
    desv_tiempo_entrega = desviacion_estandar_demanda * math.sqrt(tiempo_entrega)
    stock_seguridad = z * desv_tiempo_entrega
    rop = (demanda_promedio_diaria * tiempo_entrega) + stock_seguridad
    return {
        "ROP": rop,
        "Stock de seguridad": stock_seguridad,
        "Valor Z": z,
        "Desviacion tiempo entrega": desv_tiempo_entrega
    }

class ModeloProbabilistico:
    """
    Clase que encapsula el modelo probabilistico de inventarios con demanda variable (normal).
    Sigue el paradigma de Programacion Orientada a Objetos.
    """
    def __init__(self, demanda_diaria, desviacion_estandar, tiempo_entrega, nivel_servicio, 
                 costo_pedido, precio_unitario, costo_mantenimiento_pct, dias_habiles,
                 metodo_z: str = "tabla", z_manual: float = None):
        self.demanda_diaria = demanda_diaria
        self.desviacion_estandar = desviacion_estandar
        self.tiempo_entrega = tiempo_entrega
        self.nivel_servicio = nivel_servicio
        self.costo_pedido = costo_pedido
        self.precio_unitario = precio_unitario
        self.costo_mantenimiento_pct = costo_mantenimiento_pct
        self.dias_habiles = dias_habiles
        self.metodo_z = metodo_z
        self.z_manual = z_manual
        
        # Resultados a calcular
        self.demanda_anual = 0.0
        self.costo_almacenaje_anual = 0.0
        self.eoq = 0.0
        self.z = 0.0
        self.desv_tiempo_entrega = 0.0
        self.demanda_tiempo_entrega = 0.0
        self.stock_seguridad = 0.0
        self.rop = 0.0
        self.num_pedidos = 0.0
        self.dias_entre_pedidos = 0.0
        self.costo_total_pedidos = 0.0
        self.costo_almacenaje_ciclo = 0.0
        self.costo_almacenaje_seguridad = 0.0
        self.costo_total_almacenaje = 0.0
        self.costo_operacional_total = 0.0

    def calcular(self):
        self.demanda_anual = self.demanda_diaria * self.dias_habiles
        self.costo_almacenaje_anual = (self.costo_mantenimiento_pct / 100.0) * self.precio_unitario
        
        # Lote economico (EOQ)
        self.eoq = calcular_eoq(self.demanda_anual, self.costo_pedido, self.costo_almacenaje_anual)
        
        # Frecuencia de pedidos
        self.num_pedidos = self.demanda_anual / self.eoq
        self.dias_entre_pedidos = (self.eoq / self.demanda_anual) * self.dias_habiles
        
        # Valor Z segun metodo
        self.z = obtener_z(self.nivel_servicio, metodo=self.metodo_z, z_personalizado=self.z_manual)
        
        # Demanda y desviacion estandar durante el tiempo de entrega
        self.demanda_tiempo_entrega = self.demanda_diaria * self.tiempo_entrega
        self.desv_tiempo_entrega = self.desviacion_estandar * math.sqrt(self.tiempo_entrega)
        
        # Stock de seguridad y Punto de Reorden (ROP)
        self.stock_seguridad = self.z * self.desv_tiempo_entrega
        self.rop = self.demanda_tiempo_entrega + self.stock_seguridad
        
        # Costos operacionales anuales
        self.costo_total_pedidos = (self.demanda_anual / self.eoq) * self.costo_pedido
        self.costo_almacenaje_ciclo = (self.eoq / 2) * self.costo_almacenaje_anual
        self.costo_almacenaje_seguridad = self.stock_seguridad * self.costo_almacenaje_anual
        self.costo_total_almacenaje = self.costo_almacenaje_ciclo + self.costo_almacenaje_seguridad
        self.costo_operacional_total = self.costo_total_pedidos + self.costo_total_almacenaje

    def generar_reporte(self) -> str:
        desc_z = "Tabla estandar (Libros de texto)" if self.metodo_z == "tabla" else ("Exacto (Normal continua)" if self.metodo_z == "exacto" else "Manual")
        return (
            "==================================================\n"
            "   REPORTE DE INVENTARIO: MODELO PROBABILISTICO\n"
            "==================================================\n"
            "Parametros de Entrada:\n"
            f" - Demanda Promedio Diaria (d): {self.demanda_diaria:.2f} unidades/dia\n"
            f" - Desviacion Estandar diaria (sd): {self.desviacion_estandar:.2f} unidades\n"
            f" - Tiempo de Entrega (L): {self.tiempo_entrega:.0f} dias\n"
            f" - Nivel de Servicio Deseado (ns): {self.nivel_servicio*100:.1f}%\n"
            f" - Metodo Valor Z: {desc_z} -> Z = {self.z:.4f}\n"
            f" - Costo por Pedido (S): ${self.costo_pedido:.2f}\n"
            f" - Costo Unitario del Producto (C): ${self.precio_unitario:.2f}\n"
            f" - Porcentaje Mantenimiento Anual (i%): {self.costo_mantenimiento_pct:.2f}%\n"
            f" - Dias Habiles al Ano (N): {self.dias_habiles:.0f} dias\n\n"
            "Resultados del Analisis:\n"
            f" - Demanda Anual Estimada (D): {self.demanda_anual:.0f} unidades/ano\n"
            f" - Costo Almacenaje Anual Unitario (H): ${self.costo_almacenaje_anual:.2f}/unidad/ano\n"
            f" - Cantidad Economica de Pedido (EOQ/Q*): {self.eoq:.2f} unidades\n"
            f" - Demanda Promedio en Tiempo de Entrega (dL): {self.demanda_tiempo_entrega:.2f} unidades\n"
            f" - Desviacion Estandar en T. Entrega (sL): {self.desv_tiempo_entrega:.2f} unidades\n"
            f" - Stock de Seguridad (ss): {self.stock_seguridad:.2f} unidades\n"
            f" - Punto de Reorden (ROP / R): {self.rop:.2f} unidades\n"
            f" - Frecuencia de Pedidos: {self.num_pedidos:.2f} pedidos/ano (cada {self.dias_entre_pedidos:.2f} dias habiles)\n\n"
            "Desglose de Costos Anuales Relevantes:\n"
            f" - Costo Anual de Realizar Pedidos: ${self.costo_total_pedidos:.2f}\n"
            f" - Costo Mantenimiento de Ciclo (Q/2 * H): ${self.costo_almacenaje_ciclo:.2f}\n"
            f" - Costo Mantenimiento Stock Seguridad (ss * H): ${self.costo_almacenaje_seguridad:.2f}\n"
            f" - Costo Total de Almacenamiento: ${self.costo_total_almacenaje:.2f}\n"
            f" - Costo Anual Relevante Total: ${self.costo_operacional_total:.2f}\n"
            "==================================================\n"
        )
