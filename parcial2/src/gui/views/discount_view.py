import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.core.discount_model import ModeloQuiebrePrecios
from src.gui.styles import BG_MAIN, BG_CARD, COLOR_PRIMARY, COLOR_ACCENT, COLOR_TEXT
from src.gui.widgets import Card

class DescuentosTramosFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_MAIN)
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=4)
        self.grid_columnconfigure(0, weight=1)
        
        self.modelo = None
        
        self.card_top = Card(self, title="Configuracion de Tramos y Parametros (Quiebre de Inventario)")
        self.card_top.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        self.card_bottom = Card(self, title="Resultados y Comparativa de Costos")
        self.card_bottom.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        
        self.build_top_panel()
        self.build_bottom_panel()

    def build_top_panel(self):
        param_frame = tk.Frame(self.card_top, bg=BG_CARD)
        param_frame.pack(fill="x", padx=15, pady=5)
        
        lbl_D = tk.Label(param_frame, text="Demanda Anual (D):", font=("Segoe UI", 9, "bold"), bg=BG_CARD)
        lbl_D.grid(row=0, column=0, sticky="w", padx=5)
        self.ent_D = tk.Entry(param_frame, width=12, font=("Segoe UI", 9), bd=1, relief="solid")
        self.ent_D.insert(0, "5000")
        self.ent_D.grid(row=0, column=1, sticky="w", padx=5)
        
        lbl_K = tk.Label(param_frame, text="Costo Pedido (K/S):", font=("Segoe UI", 9, "bold"), bg=BG_CARD)
        lbl_K.grid(row=0, column=2, sticky="w", padx=5)
        self.ent_K = tk.Entry(param_frame, width=12, font=("Segoe UI", 9), bd=1, relief="solid")
        self.ent_K.insert(0, "49")
        self.ent_K.grid(row=0, column=3, sticky="w", padx=5)
        
        lbl_i = tk.Label(param_frame, text="% Mant. Anual (i%):", font=("Segoe UI", 9, "bold"), bg=BG_CARD)
        lbl_i.grid(row=0, column=4, sticky="w", padx=5)
        self.ent_i = tk.Entry(param_frame, width=12, font=("Segoe UI", 9), bd=1, relief="solid")
        self.ent_i.insert(0, "20")
        self.ent_i.grid(row=0, column=5, sticky="w", padx=5)
        
        btn_frame = tk.Frame(self.card_top, bg=BG_CARD)
        btn_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        btn_add = tk.Button(btn_frame, text="+ Agregar Tramo", font=("Segoe UI", 9, "bold"), bg="#10b981", fg="#ffffff",
                            relief="flat", bd=0, cursor="hand2", padx=10, command=self.agregar_fila)
        btn_add.pack(side="left", padx=(0, 5))
        
        btn_remove = tk.Button(btn_frame, text="- Eliminar Tramo", font=("Segoe UI", 9, "bold"), bg="#ef4444", fg="#ffffff",
                               relief="flat", bd=0, cursor="hand2", padx=10, command=self.eliminar_fila)
        btn_remove.pack(side="left", padx=5)
        
        btn_solve = tk.Button(btn_frame, text="Calcular Optimo", font=("Segoe UI", 10, "bold"), bg=COLOR_PRIMARY, fg="#ffffff",
                              relief="flat", bd=0, cursor="hand2", padx=20, pady=4, command=self.resolver)
        btn_solve.pack(side="right")
        
        self.table_scroll = ttk.Frame(self.card_top)
        self.table_scroll.pack(fill="both", expand=True, padx=15, pady=(5, 10))
        
        self.canvas = tk.Canvas(self.table_scroll, borderwidth=0, background=BG_CARD, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.table_scroll, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_CARD)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.headers = ["Tramo", "Limite Inferior (Q Min)", "Limite Superior (Q Max o 'inf')", "Precio Unitario ($)"]
        for col_idx, header in enumerate(self.headers):
            lbl = tk.Label(self.scrollable_frame, text=header, font=("Segoe UI", 9, "bold"), 
                           bg="#f8fafc", fg=COLOR_TEXT, bd=1, relief="solid", padx=10, pady=5)
            lbl.grid(row=0, column=col_idx, sticky="ew")
            
        self.scrollable_frame.grid_columnconfigure(0, minsize=80)
        self.scrollable_frame.grid_columnconfigure(1, minsize=180)
        self.scrollable_frame.grid_columnconfigure(2, minsize=180)
        self.scrollable_frame.grid_columnconfigure(3, minsize=150)
        
        self.filas = []
        tramos_defecto = [
            (0, 999, 5.00),
            (1000, 1999, 4.80),
            (2000, "inf", 4.75)
        ]
        for lim_inf, lim_sup, precio in tramos_defecto:
            self.agregar_fila(lim_inf, lim_sup, precio)

    def agregar_fila(self, lim_inf=0, lim_sup="", precio=0.0):
        row_idx = len(self.filas) + 1
        
        lbl_num = tk.Label(self.scrollable_frame, text=f"Tramo {row_idx}", font=("Segoe UI", 9), 
                           bg=BG_CARD, fg=COLOR_TEXT, bd=1, relief="solid", pady=4)
        lbl_num.grid(row=row_idx, column=0, sticky="ew")
        
        ent_inf = tk.Entry(self.scrollable_frame, font=("Segoe UI", 9), bd=1, relief="solid", justify="center")
        ent_inf.insert(0, str(lim_inf))
        ent_inf.grid(row=row_idx, column=1, sticky="ew", padx=2, pady=2)
        
        ent_sup = tk.Entry(self.scrollable_frame, font=("Segoe UI", 9), bd=1, relief="solid", justify="center")
        ent_sup.insert(0, str(lim_sup))
        ent_sup.grid(row=row_idx, column=2, sticky="ew", padx=2, pady=2)
        
        ent_precio = tk.Entry(self.scrollable_frame, font=("Segoe UI", 9), bd=1, relief="solid", justify="center")
        ent_precio.insert(0, f"{precio:.2f}" if precio > 0 else "")
        ent_precio.grid(row=row_idx, column=3, sticky="ew", padx=2, pady=2)
        
        self.filas.append({
            "lbl_num": lbl_num,
            "ent_inf": ent_inf,
            "ent_sup": ent_sup,
            "ent_precio": ent_precio
        })

    def eliminar_fila(self):
        if len(self.filas) <= 1:
            messagebox.showwarning("Aviso", "Debe haber al menos un tramo definido.")
            return
            
        fila = self.filas.pop()
        fila["lbl_num"].destroy()
        fila["ent_inf"].destroy()
        fila["ent_sup"].destroy()
        fila["ent_precio"].destroy()

    def build_bottom_panel(self):
        bottom_controls = tk.Frame(self.card_bottom, bg=BG_CARD)
        bottom_controls.pack(side="bottom", fill="x", padx=15, pady=5)
        
        self.lbl_optimo = tk.Label(bottom_controls, text="Realiza el calculo para encontrar el lote de pedido optimo.", 
                                   font=("Segoe UI", 10, "bold"), bg=BG_CARD, fg=COLOR_PRIMARY, anchor="w")
        self.lbl_optimo.pack(side="left", fill="x", expand=True)
        
        self.btn_export = tk.Button(bottom_controls, text="Exportar Reporte (.txt)", font=("Segoe UI", 9, "bold"), bg="#475569", fg="#ffffff",
                                    relief="flat", bd=0, cursor="hand2", padx=15, pady=4, state="disabled", command=self.exportar)
        self.btn_export.pack(side="right")

        self.tree = ttk.Treeview(self.card_bottom, columns=("tramo", "rango", "precio", "eoq_calc", "cant_ajust", "costo_ped", "costo_mant", "costo_prod", "costo_total", "estado"), show="headings")
        self.tree.pack(side="top", fill="both", expand=True, padx=15, pady=(5, 5))
        
        col_headers = {
            "tramo": ("Tramo", 60),
            "rango": ("Rango Cantidad", 120),
            "precio": ("Precio ($)", 80),
            "eoq_calc": ("EOQ Teorico", 100),
            "cant_ajust": ("Cant. Ajustada", 110),
            "costo_ped": ("Costo Pedido", 100),
            "costo_mant": ("Costo Almac.", 100),
            "costo_prod": ("Costo Producto", 110),
            "costo_total": ("Costo Anual Total", 130),
            "estado": ("Estado Factibilidad", 180)
        }
        
        for col_name, (label, width) in col_headers.items():
            self.tree.heading(col_name, text=label)
            self.tree.column(col_name, width=width, anchor="center")

    def resolver(self):
        try:
            D = float(self.ent_D.get())
            K = float(self.ent_K.get())
            i_pct = float(self.ent_i.get())
            
            tramos = []
            for idx, fila in enumerate(self.filas):
                inf_val = float(fila["ent_inf"].get())
                sup_str = fila["ent_sup"].get().strip().lower()
                sup_val = float('inf') if (sup_str == "inf" or sup_str == "" or sup_str == "none") else float(sup_str)
                precio_val = float(fila["ent_precio"].get())
                tramos.append((inf_val, sup_val, precio_val))
                
            self.modelo = ModeloQuiebrePrecios(
                demanda_anual=D, costo_pedido=K,
                costo_almacenamiento_porcentaje=i_pct, tramos=tramos
            )
            self.modelo.calcular()
            
            for row in self.tree.get_children():
                self.tree.delete(row)
                
            for r in self.modelo.resultados_tramos:
                lim_sup_str = "inf" if r["limite_superior"] == float('inf') else f"{r['limite_superior']:.0f}"
                rango_str = f"{r['limite_inferior']:.0f} - {lim_sup_str}"
                
                eoq_teorico = f"{r['eoq_calculado']:.2f}"
                cant_ajustada = f"{r['cantidad_ajustada']:.2f}" if r["factible"] else "N/A"
                
                if r["factible"]:
                    c_pedidos = (D / r["cantidad_ajustada"]) * K
                    c_almacenaje = (r["cantidad_ajustada"] / 2) * (i_pct / 100.0 * r["precio_unidad"])
                    c_producto = D * r["precio_unidad"]
                    costo_total = f"${r['costo_total']:.2f}"
                else:
                    c_pedidos = 0.0
                    c_almacenaje = 0.0
                    c_producto = 0.0
                    costo_total = "N/A"
                    
                self.tree.insert("", "end", values=(
                    f"Tramo {r['tramo']}",
                    rango_str,
                    f"${r['precio_unidad']:.2f}",
                    eoq_teorico,
                    cant_ajustada,
                    f"${c_pedidos:.2f}" if r["factible"] else "N/A",
                    f"${c_almacenaje:.2f}" if r["factible"] else "N/A",
                    f"${c_producto:.2f}" if r["factible"] else "N/A",
                    costo_total,
                    r["estado"]
                ))
                
            if self.modelo.optimo:
                opt = self.modelo.optimo
                self.lbl_optimo.config(
                    text=f"OPTIMO GLOBAL: Ordenar {opt['cantidad']:.2f} unidades (Tramo {opt['tramo']}, precio ${opt['precio_aplicado']:.2f}) -> Costo Minimo: ${opt['costo_total']:.2f}",
                    fg=COLOR_ACCENT
                )
                self.btn_export.config(state="normal")
            else:
                self.lbl_optimo.config(
                    text="No se pudo encontrar ninguna solucion factible con los tramos dados.",
                    fg="#ef4444"
                )
                self.btn_export.config(state="disabled")
                
        except ValueError as ex:
            messagebox.showerror("Error de Entrada", f"Verifica que los datos ingresados sean correctos: {str(ex)}")

    def exportar(self):
        if not self.modelo:
            messagebox.showwarning("Aviso", "No hay calculos para exportar.")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de Texto", "*.txt")],
            title="Guardar Reporte Quiebre de Precios"
        )
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.modelo.generar_reporte())
                messagebox.showinfo("Exito", "El reporte se ha exportado correctamente.")
            except Exception as ex:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(ex)}")
