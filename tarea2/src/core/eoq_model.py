import math

class ModeloEOQClasico:
    """
    Clase que encapsula el modelo de Cantidad Economica de Pedido (EOQ) clasico.
    Sigue el paradigma de Programacion Orientada a Objetos y base anual estandar.
    """
    def __init__(self, demanda, costo_pedido, costo_mantenimiento, precio_unitario=0.0, es_mensual=False, i_porcentaje=None, modo_h="directo"):
        self.demanda = demanda
        self.costo_pedido = costo_pedido
        self.costo_mantenimiento = costo_mantenimiento
        self.precio_unitario = precio_unitario
        self.es_mensual = es_mensual
        self.i_porcentaje = i_porcentaje
        self.modo_h = modo_h
        
        # Resultados a calcular
        self.demanda_anual = 0.0
        self.demanda_mensual = 0.0
        self.eoq = 0.0
        self.num_pedidos = 0.0
        self.frecuencia_anios = 0.0
        self.frecuencia_meses = 0.0
        self.costo_pedido_anual = 0.0
        self.costo_mantenimiento_anual = 0.0
        self.costo_adquisicion_anual = 0.0
        self.costo_total_anual = 0.0

    def calcular(self):
        # Demanda normalizada
        self.demanda_anual = self.demanda * 12.0 if self.es_mensual else self.demanda
        self.demanda_mensual = self.demanda if self.es_mensual else (self.demanda / 12.0)
        
        # Calculo de EOQ clasico en base anual estandar
        self.eoq = math.sqrt((2 * self.demanda_anual * self.costo_pedido) / self.costo_mantenimiento)
        
        # Numero de pedidos anuales (N = D / Q)
        self.num_pedidos = self.demanda_anual / self.eoq
        
        # Frecuencia entre pedidos usando la formula T = Q / D en Anios y Meses
        self.frecuencia_anios = self.eoq / self.demanda_anual
        self.frecuencia_meses = self.frecuencia_anios * 12.0
        
        # Costos anuales estandar
        self.costo_pedido_anual = (self.demanda_anual / self.eoq) * self.costo_pedido
        self.costo_mantenimiento_anual = (self.eoq / 2) * self.costo_mantenimiento
        self.costo_adquisicion_anual = self.demanda_anual * self.precio_unitario
        self.costo_total_anual = self.costo_pedido_anual + self.costo_mantenimiento_anual + self.costo_adquisicion_anual

    def generar_reporte(self) -> str:
        dem_tipo = "Mensual" if self.es_mensual else "Anual"
        rep = (
            "==================================================\n"
            "   REPORTE DE INVENTARIO: MODELO EOQ CLASICO\n"
            "==================================================\n"
            "Parametros de Entrada:\n"
            f" - Demanda ({dem_tipo}): {self.demanda:.2f} unidades\n"
            f" - Demanda Anualizada (D): {self.demanda_anual:.2f} unidades/ano\n"
            f" - Costo de Pedido (S/K): ${self.costo_pedido:.2f}\n"
        )
        if self.i_porcentaje is not None:
            rep += f" - Tasa de Mantenimiento Anual (i%): {self.i_porcentaje:.2f}%\n"
        rep += (
            f" - Costo de Mantenimiento Unitario (H): ${self.costo_mantenimiento:.2f}/unidad/ano\n"
            f" - Costo Unitario del Producto (C): ${self.precio_unitario:.2f}\n\n"
            "Resultados del Calculo:\n"
            f" - Cantidad Economica de Pedido (EOQ / Q*): {self.eoq:.2f} unidades\n"
            f" - Numero de Pedidos al Ano (N): {self.num_pedidos:.2f} pedidos/ano\n"
            f" - Frecuencia entre Pedidos (T = Q/D): {self.frecuencia_meses:.2f} meses ({self.frecuencia_anios:.4f} anos)\n\n"
            "Desglose de Costos Anuales:\n"
            f" - Costo de Pedidos: ${self.costo_pedido_anual:.2f}\n"
            f" - Costo de Almacenamiento: ${self.costo_mantenimiento_anual:.2f}\n"
            f" - Costo de Adquisicion (Producto): ${self.costo_adquisicion_anual:.2f}\n"
            f" - Costo Total Anual (CT): ${self.costo_total_anual:.2f}\n"
            "==================================================\n"
        )
        return rep
