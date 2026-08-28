"""
Punto de Entrada Principal — Calculadora de Teoria de Inventarios (Parcial II)
Universidad Jose Antonio Paez — Metodos Cuantitativos
Arquitectura Top-Down Modular.
"""
import sys
import os
import argparse

# Asegurar que el directorio base este en sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.eoq_model import ModeloEOQClasico
from src.core.discount_model import ModeloQuiebrePrecios
from src.core.constrained_model import ModeloRestriccionesInventario, resolver_restricciones_lagrange, calcular_lambda_aproximado
from src.core.probabilistic_model import ModeloProbabilistico
from src.services.reporter import ReportService

def resolver_ejercicio1_parcial2(exportar=True):
    """
    Resuelve el Ejercicio 1 del Parcial II (Modelo EOQ Clasico).
    
    Enunciado:
    Una empresa distribuye productos electronicos con:
    - Demanda anual: 6000 unidades
    - Costo por pedido (S): $50
    - Precio del producto (C): $20 por unidad
    - Costo de almacenamiento anual: 20% del costo del producto (H = $4.00)
    - Demanda diaria: 20 unidades
    - Tiempo de entrega: 5 dias
    """
    demanda = 6000.0
    costo_pedido = 50.0
    precio_unitario = 20.0
    i_porcentaje = 20.0
    costo_mantenimiento = (i_porcentaje / 100.0) * precio_unitario  # 4.00 $/unid/ano
    demanda_diaria = 20.0
    tiempo_entrega = 5.0
    rop = demanda_diaria * tiempo_entrega  # 100 unidades

    mod = ModeloEOQClasico(
        demanda=demanda,
        costo_pedido=costo_pedido,
        costo_mantenimiento=costo_mantenimiento,
        precio_unitario=precio_unitario,
        es_mensual=False,
        i_porcentaje=i_porcentaje
    )
    mod.calcular()
    
    rep_base = mod.generar_reporte()
    costo_sistema_inventario = mod.costo_pedido_anual + mod.costo_mantenimiento_anual
    
    rep_completo = (
        rep_base +
        "Respuestas Especificas a los Literales del Examen:\n"
        "--------------------------------------------------\n"
        f" a) Cantidad Optima de Pedido (EOQ): {mod.eoq:.2f} unidades\n"
        f" b) Punto de Reorden (ROP = d * L = {demanda_diaria:.0f} * {tiempo_entrega:.0f}): {rop:.2f} unidades\n"
        f" c) Costo Total Anual del Sistema (solo pedidos + mantenimiento): ${costo_sistema_inventario:.2f}\n"
        f"    (Costo Total incluyendo adquisicion: ${mod.costo_total_anual:.2f})\n"
        f" d) Numero de Pedidos al Ano (N = D / Q*): {mod.num_pedidos:.2f} pedidos/ano\n"
        f"    (Frecuencia: cada {mod.frecuencia_meses:.2f} meses o {mod.frecuencia_anios * 360:.1f} dias)\n"
        "==================================================\n"
    )
    
    if exportar:
        out_dir = os.path.join(BASE_DIR, "outputs")
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, "Ejercicio 1 - Modelo EOQ Clasico.txt")
        ReportService.guardar_reporte(rep_completo, out_file)
        
    return mod, rep_completo

def resolver_ejercicio2_parcial2(exportar=True):
    """
    Resuelve el Ejercicio 2 del Parcial II (Modelo de Descuentos por Cantidad / Quiebre de Precios).
    
    Enunciado:
    Demanda anual: 10,000 unidades
    Precio base: $10 por unidad
    Costo por pedido (S): $100
    Costo de almacenamiento anual: 25% del precio del producto
    
    Esquema de descuentos:
    - Tramo 1: 0 - 999       -> 0% descuento ($10.00)
    - Tramo 2: 1000 - 1999   -> 3% descuento ($9.70)
    - Tramo 3: 2000 - 2999   -> 5% descuento ($9.50)
    - Tramo 4: 3000 o mas    -> 7% descuento ($9.30)
    """
    demanda = 10000.0
    costo_pedido = 100.0
    i_pct = 25.0
    
    tramos = [
        (0, 999, 10.00),
        (1000, 1999, 9.70),
        (2000, 2999, 9.50),
        (3000, float('inf'), 9.30)
    ]
    
    mod = ModeloQuiebrePrecios(
        demanda_anual=demanda,
        costo_pedido=costo_pedido,
        costo_almacenamiento_porcentaje=i_pct,
        tramos=tramos
    )
    mod.calcular()
    reporte = mod.generar_reporte()
    
    if exportar:
        out_dir = os.path.join(BASE_DIR, "outputs")
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, "Ejercicio 2 - Quiebre de Precios Descuentos.txt")
        ReportService.guardar_reporte(reporte, out_file)
        
    return mod, reporte

def resolver_ejercicio3_parcial2(exportar=True):
    """
    Resuelve el Ejercicio 3 del Parcial II (Modelo Multi-Articulo con Restricciones).
    
    Enunciado:
    - Articulos: A, B, C
    - Demanda mensual: 300, 250, 400 unidades (Anual: 3600, 3000, 4800)
    - Costo de pedido: 30, 35, 40
    - Costo de almacenamiento: 5, 6, 7
    - Capacidad total: 700 unidades
    - Presupuesto: 8000
    - Demanda diaria: 10, 8, 15 unidades
    - Tiempo de entrega: 3, 4, 5 dias
    """
    articulos = ['A', 'B', 'C']
    demandas_mensuales = [300, 250, 400]
    demandas_anuales = [d * 12 for d in demandas_mensuales]  # 3600, 3000, 4800
    costos_pedido = [30, 35, 40]
    costos_almacenamiento = [5, 6, 7]
    capacidad_total = 700
    presupuesto = 8000
    demandas_diarias = [10, 8, 15]
    tiempos_entrega = [3, 4, 5]
    
    mod = ModeloRestriccionesInventario(
        articulos=articulos,
        demandas=demandas_anuales,
        costos_pedido=costos_pedido,
        costos_almacenamiento=costos_almacenamiento,
        capacidad_total=capacidad_total,
        presupuesto=presupuesto,
        demandas_diarias=demandas_diarias,
        tiempos_entrega=tiempos_entrega,
        metodo="Multiplicadores de Lagrange (Exacto)"
    )
    mod.calcular()
    reporte = mod.generar_reporte()
    
    if exportar:
        out_dir = os.path.join(BASE_DIR, "outputs")
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, "Ejercicio 3 - Modelo con Restricciones.txt")
        ReportService.guardar_reporte(reporte, out_file)
        
    return mod, reporte

def resolver_todos(exportar=True):
    """Ejecuta y exporta la resolucion de los 3 ejercicios del Parcial II."""
    print("\n" + "="*60)
    print("   EJECUCION PARCIAL II — EJERCICIO 1 (EOQ CLASICO)   ")
    print("="*60 + "\n")
    _, rep1 = resolver_ejercicio1_parcial2(exportar=exportar)
    print(rep1)
    
    print("\n" + "="*60)
    print("   EJECUCION PARCIAL II — EJERCICIO 2 (QUIEBRE DE PRECIOS)   ")
    print("="*60 + "\n")
    _, rep2 = resolver_ejercicio2_parcial2(exportar=exportar)
    print(rep2)
    
    print("\n" + "="*60)
    print("   EJECUCION PARCIAL II — EJERCICIO 3 (RESTRICCIONES)   ")
    print("="*60 + "\n")
    _, rep3 = resolver_ejercicio3_parcial2(exportar=exportar)
    print(rep3)
    
    print("\nLos 3 reportes .txt generados exitosamente en parcial2/outputs/\n")

def main():
    parser = argparse.ArgumentParser(description="Calculadora de Teoria de Inventarios — Parcial II")
    parser.add_argument("--ejercicio1", action="store_true", help="Resuelve el Ejercicio 1 (EOQ Clasico)")
    parser.add_argument("--ejercicio2", action="store_true", help="Resuelve el Ejercicio 2 (Descuentos / Quiebre de Precios)")
    parser.add_argument("--ejercicio3", action="store_true", help="Resuelve el Ejercicio 3 (Multi-Articulo con Restricciones)")
    parser.add_argument("--todos", "--all", dest="todos", action="store_true", help="Resuelve todos los ejercicios del Parcial II")
    parser.add_argument("--cli", action="store_true", help="Ejecuta en modo linea de comandos")
    parser.add_argument("--gui", action="store_true", help="Fuerza la ejecucion de la interfaz grafica Tkinter")
    parser.add_argument("--no-export", action="store_true", help="No exporta los archivos .txt de salida")
    
    args = parser.parse_args()
    
    if args.todos:
        resolver_todos(exportar=not args.no_export)
        return
        
    if args.ejercicio1:
        print("\n" + "="*60)
        print("   EJECUCION PARCIAL II — EJERCICIO 1 (EOQ CLASICO)   ")
        print("="*60 + "\n")
        _, rep = resolver_ejercicio1_parcial2(exportar=not args.no_export)
        print(rep)
        return
        
    if args.ejercicio2:
        print("\n" + "="*60)
        print("   EJECUCION PARCIAL II — EJERCICIO 2 (QUIEBRE DE PRECIOS)   ")
        print("="*60 + "\n")
        _, rep = resolver_ejercicio2_parcial2(exportar=not args.no_export)
        print(rep)
        return
        
    if args.ejercicio3:
        print("\n" + "="*60)
        print("   EJECUCION PARCIAL II — EJERCICIO 3 (RESTRICCIONES)   ")
        print("="*60 + "\n")
        _, rep = resolver_ejercicio3_parcial2(exportar=not args.no_export)
        print(rep)
        return
        
    if args.cli and not args.gui:
        resolver_todos(exportar=not args.no_export)
        return

    # Si no se especifica flag o se pide gui, intentar abrir GUI
    try:
        from src.gui.app import Application
        app = Application()
        app.mainloop()
    except Exception as e:
        print(f"Aviso: No se pudo inicializar la interfaz grafica ({e}).")
        print("Ejecutando en modo consola (CLI)...\n")
        resolver_todos(exportar=not args.no_export)

if __name__ == "__main__":
    main()
