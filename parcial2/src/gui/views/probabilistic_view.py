import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.core.probabilistic_model import ModeloProbabilistico, obtener_z
from src.gui.styles import BG_MAIN, BG_CARD, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_TEXT, COLOR_TEXT_LIGHT, COLOR_ACCENT, COLOR_BORDER
from src.gui.widgets import Card

class ProbabilisticoFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_MAIN)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=5)
        
        self.modelo = None
        
        self.card_form = Card(self, title="Datos del Modelo Probabilistico")
        self.card_form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.card_results = Card(self, title="Resultados del Analisis de Riesgo")
        self.card_results.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        self.build_form()
        self.build_results_placeholder()

    def build_form(self):
        self.entries = {}
        container = tk.Frame(self.card_form, bg=BG_CARD)
        container.pack(fill="both", expand=True, padx=20, pady=5)
        
        fields = [
            ("Demanda Promedio Diaria (d):", "d", "200", "Cantidad promedio consumida por dia"),
            ("Desviacion Estandar diaria (sd):", "sigma", "150", "Variacion de la demanda diaria"),
            ("Tiempo de Entrega (L en dias):", "L", "4", "Dias transcurridos hasta recibir pedido"),
            ("Nivel de Servicio Deseado (0-1):", "ns", "0.95", "Probabilidad sin rotura (ej: 0.95)"),
            ("Costo por Pedido (S):", "S", "20", "Costo fijo por ordenar ($)"),
            ("Costo Unitario (C):", "C", "10", "Precio de compra del producto ($)"),
            ("Porcentaje Mant. Anual (i%):", "i", "20", "Costo mantener anual en % de C (ej: 20)"),
            ("Dias Habiles al Ano (N):", "N", "250", "Dias habiles anuales (ej: 250 o 365)")
        ]
        
        row_idx = 0
        for label, name, def_val, tooltip in fields:
            lbl = tk.Label(container, text=label, font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=COLOR_TEXT)
            lbl.grid(row=row_idx*2, column=0, sticky="w", pady=(3, 1))
            
            entry = tk.Entry(container, font=("Segoe UI", 9), bd=1, relief="solid", highlightthickness=0)
            entry.insert(0, def_val)
            entry.grid(row=row_idx*2+1, column=0, sticky="ew", pady=(0, 3))
            if name == "ns":
                entry.bind("<KeyRelease>", self.actualizar_z_display)
            self.entries[name] = entry
            
            lbl_help = tk.Label(container, text=tooltip, font=("Segoe UI", 8), bg=BG_CARD, fg=COLOR_TEXT_LIGHT)
            lbl_help.grid(row=row_idx*2+1, column=1, sticky="w", padx=(10, 0), pady=(0, 3))
            row_idx += 1
            
        lbl_metodo_z = tk.Label(container, text="Metodo de Calculo Z:", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=COLOR_PRIMARY)
        lbl_metodo_z.grid(row=row_idx*2, column=0, sticky="w", pady=(4, 1))
        
        self.combo_metodo_z = ttk.Combobox(container, values=[
            "Tabla estandar (Libros)",
            "Distribucion Normal exacta",
            "Ingresar Z manualmente"
        ], state="readonly", font=("Segoe UI", 9))
        self.combo_metodo_z.set("Tabla estandar (Libros)")
        self.combo_metodo_z.grid(row=row_idx*2+1, column=0, sticky="ew", pady=(0, 3))
        self.combo_metodo_z.bind("<<ComboboxSelected>>", self.on_metodo_z_change)
        
        self.lbl_help_z = tk.Label(container, text="Tabla estandar de libros", font=("Segoe UI", 8), bg=BG_CARD, fg=COLOR_TEXT_LIGHT)
        self.lbl_help_z.grid(row=row_idx*2+1, column=1, sticky="w", padx=(10, 0), pady=(0, 3))
        row_idx += 1
        
        lbl_z = tk.Label(container, text="Valor Z Aplicado:", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=COLOR_TEXT)
        lbl_z.grid(row=row_idx*2, column=0, sticky="w", pady=(3, 1))
        
        self.ent_z = tk.Entry(container, font=("Segoe UI", 9), bd=1, relief="solid", highlightthickness=0)
        self.ent_z.insert(0, "1.65")
        self.ent_z.grid(row=row_idx*2+1, column=0, sticky="ew", pady=(0, 3))
        self.entries["z_manual"] = self.ent_z
        
        self.lbl_help_z_val = tk.Label(container, text="Valor Z para el calculo", font=("Segoe UI", 8), bg=BG_CARD, fg=COLOR_TEXT_LIGHT)
        self.lbl_help_z_val.grid(row=row_idx*2+1, column=1, sticky="w", padx=(10, 0), pady=(0, 3))
        row_idx += 1
        
        container.grid_columnconfigure(0, weight=3)
        container.grid_columnconfigure(1, weight=2)
        
        self.actualizar_z_display()
        
        btn_calc = tk.Button(self.card_form, text="Calcular Inventario Probabilistico", font=("Segoe UI", 10, "bold"),
                             bg=COLOR_PRIMARY, fg="#ffffff", activebackground=COLOR_PRIMARY_HOVER,
                             activeforeground="#ffffff", relief="flat", bd=0, cursor="hand2", pady=8,
                             command=self.calcular)
        btn_calc.pack(fill="x", padx=20, pady=(10, 10))

    def on_metodo_z_change(self, event=None):
        self.actualizar_z_display()

    def actualizar_z_display(self, event=None):
        metodo = self.combo_metodo_z.get()
        if "manual" in metodo.lower():
            self.ent_z.config(state="normal", bg="#ffffff")
            self.lbl_help_z.config(text="Modo manual", fg=COLOR_PRIMARY)
            self.lbl_help_z_val.config(text="Ingresa el valor Z deseado", fg=COLOR_PRIMARY)
        else:
            try:
                ns_str = self.entries["ns"].get().strip()
                if ns_str:
                    ns_val = float(ns_str)
                    if 0.0 < ns_val < 1.0:
                        if "tabla" in metodo.lower():
                            z_val = obtener_z(ns_val, metodo="tabla")
                            desc = f"Z = {z_val:.2f} (Tabla estandar)"
                        else:
                            z_val = obtener_z(ns_val, metodo="exacto")
                            desc = f"Z = {z_val:.4f} (Normal exacta)"
                        
                        self.ent_z.config(state="normal")
                        self.ent_z.delete(0, "end")
                        self.ent_z.insert(0, f"{z_val:.4f}" if "exacta" in metodo.lower() else f"{z_val:.2f}")
                        self.ent_z.config(state="readonly")
                        self.lbl_help_z.config(text=desc, fg=COLOR_TEXT_LIGHT)
                        self.lbl_help_z_val.config(text="Auto-calculado segun Nivel Servicio", fg=COLOR_TEXT_LIGHT)
            except ValueError:
                pass

    def build_results_placeholder(self):
        self.results_container = tk.Frame(self.card_results, bg=BG_CARD)
        self.results_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        lbl_msg = tk.Label(self.results_container, text="Introduce los datos y haz clic en\n'Calcular Inventario Probabilistico'\npara ver los resultados.", 
                           font=("Segoe UI", 10, "italic"), bg=BG_CARD, fg=COLOR_TEXT_LIGHT, justify="center")
        lbl_msg.pack(expand=True)

    def calcular(self):
        try:
            d = float(self.entries["d"].get())
            sigma = float(self.entries["sigma"].get())
            L = float(self.entries["L"].get())
            ns = float(self.entries["ns"].get())
            S = float(self.entries["S"].get())
            C = float(self.entries["C"].get())
            i_pct = float(self.entries["i"].get())
            N = float(self.entries["N"].get())
            
            if not (0.0 < ns < 1.0):
                raise ValueError("El nivel de servicio debe estar entre 0 y 1 (ej: 0.95 para 95%).")
            
            metodo_sel = self.combo_metodo_z.get()
            z_custom = None
            if "manual" in metodo_sel.lower():
                metodo_z = "manual"
                z_custom = float(self.ent_z.get())
            elif "exacta" in metodo_sel.lower():
                metodo_z = "exacto"
            else:
                metodo_z = "tabla"
            
            self.modelo = ModeloProbabilistico(
                demanda_diaria=d, desviacion_estandar=sigma, tiempo_entrega=L,
                nivel_servicio=ns, costo_pedido=S, precio_unitario=C,
                costo_mantenimiento_pct=i_pct, dias_habiles=N,
                metodo_z=metodo_z, z_manual=z_custom
            )
            self.modelo.calcular()
            
            for widget in self.results_container.winfo_children():
                widget.destroy()
                
            summary_frame = tk.Frame(self.results_container, bg=BG_CARD)
            summary_frame.pack(fill="x", pady=(5, 5))
            
            lbl_eoq_title = tk.Label(summary_frame, text="Cantidad a Pedir (Q* / EOQ):", 
                                     font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=COLOR_TEXT_LIGHT)
            lbl_eoq_title.grid(row=0, column=0, sticky="w")
            lbl_eoq = tk.Label(summary_frame, text=f"{self.modelo.eoq:.2f} unidades", 
                               font=("Segoe UI", 16, "bold"), bg=BG_CARD, fg=COLOR_PRIMARY)
            lbl_eoq.grid(row=1, column=0, sticky="w", pady=(0, 5))
            
            lbl_rop_title = tk.Label(summary_frame, text="Punto de Reorden (R / ROP):", 
                                     font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=COLOR_TEXT_LIGHT)
            lbl_rop_title.grid(row=0, column=1, sticky="w", padx=(15, 0))
            lbl_rop = tk.Label(summary_frame, text=f"{self.modelo.rop:.2f} unidades", 
                               font=("Segoe UI", 16, "bold"), bg=BG_CARD, fg=COLOR_PRIMARY)
            lbl_rop.grid(row=1, column=1, sticky="w", padx=(15, 0), pady=(0, 5))
            
            lbl_ss_title = tk.Label(summary_frame, text="Inventario de Seguridad (ss):", 
                                     font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=COLOR_TEXT_LIGHT)
            lbl_ss_title.grid(row=2, column=0, sticky="w")
            lbl_ss = tk.Label(summary_frame, text=f"{self.modelo.stock_seguridad:.2f} unidades", 
                               font=("Segoe UI", 16, "bold"), bg=BG_CARD, fg=COLOR_ACCENT)
            lbl_ss.grid(row=3, column=0, sticky="w")
            
            lbl_freq_title = tk.Label(summary_frame, text="Frecuencia de Pedidos:", 
                                      font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=COLOR_TEXT_LIGHT)
            lbl_freq_title.grid(row=2, column=1, sticky="w", padx=(15, 0))
            lbl_freq = tk.Label(summary_frame, text=f"{self.modelo.num_pedidos:.0f} pedidos/ano (cada {self.modelo.dias_entre_pedidos:.1f} dias)", 
                                font=("Segoe UI", 12, "bold"), bg=BG_CARD, fg=COLOR_TEXT)
            lbl_freq.grid(row=3, column=1, sticky="w", padx=(15, 0))
            
            sep = tk.Frame(self.results_container, bg=COLOR_BORDER, height=1)
            sep.pack(fill="x", pady=6)
            
            grid_frame = tk.Frame(self.results_container, bg=BG_CARD)
            grid_frame.pack(fill="x", pady=2)
            
            detalles = [
                ("Demanda Anual Estimada (D):", f"{self.modelo.demanda_anual:.0f} unidades"),
                ("Costo Almacenaje Unitario (H):", f"${self.modelo.costo_almacenaje_anual:.2f}/unidad/ano"),
                ("Valor Z Utilizado:", f"{self.modelo.z:.4f}"),
                ("Demanda en Tiempo de Entrega (dL):", f"{self.modelo.demanda_tiempo_entrega:.2f} unidades"),
                ("Desviacion en T. Entrega (sL):", f"{self.modelo.desv_tiempo_entrega:.2f} unidades"),
                ("Costo Anual de Pedidos (D/Q * S):", f"${self.modelo.costo_total_pedidos:.2f}"),
                ("Costo Mant. Ciclo (Q/2 * H):", f"${self.modelo.costo_almacenaje_ciclo:.2f}"),
                ("Costo Mant. Seguridad (ss * H):", f"${self.modelo.costo_almacenaje_seguridad:.2f}"),
                ("Costo Total Almacenamiento:", f"${self.modelo.costo_total_almacenaje:.2f}"),
                ("Costo Anual Relevante Total:", f"${self.modelo.costo_operacional_total:.2f}")
            ]
            
            for idx, (lbl_txt, val_txt) in enumerate(detalles):
                font_weight = "bold" if ("Total" in lbl_txt or "Relevante" in lbl_txt) else "normal"
                lbl_color = COLOR_PRIMARY if ("Total" in lbl_txt or "Relevante" in lbl_txt) else COLOR_TEXT
                
                l_widget = tk.Label(grid_frame, text=lbl_txt, font=("Segoe UI", 9, font_weight), bg=BG_CARD, fg=COLOR_TEXT)
                l_widget.grid(row=idx, column=0, sticky="w", pady=2)
                
                v_widget = tk.Label(grid_frame, text=val_txt, font=("Segoe UI", 9, "bold" if font_weight=="bold" else "normal"), 
                                    bg=BG_CARD, fg=lbl_color)
                v_widget.grid(row=idx, column=1, sticky="e", pady=2)
                
            grid_frame.columnconfigure(0, weight=1)
            grid_frame.columnconfigure(1, weight=1)
            
            btn_export = tk.Button(self.results_container, text="Exportar Reporte (.txt)", font=("Segoe UI", 10, "bold"),
                                   bg="#475569", fg="#ffffff", activebackground="#334155", activeforeground="#ffffff",
                                   relief="flat", bd=0, cursor="hand2", pady=8, command=self.exportar)
            btn_export.pack(fill="x", pady=(10, 0))
            
        except ValueError as ex:
            messagebox.showerror("Error de Entrada", f"Datos incorrectos: {str(ex)}")

    def exportar(self):
        if not self.modelo:
            messagebox.showwarning("Aviso", "No hay calculos para exportar.")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de Texto", "*.txt")],
            title="Guardar Reporte Probabilistico"
        )
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.modelo.generar_reporte())
                messagebox.showinfo("Exito", "El reporte se ha exportado correctamente.")
            except Exception as ex:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(ex)}")
