import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.core.eoq_model import ModeloEOQClasico
from src.gui.styles import BG_MAIN, BG_CARD, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_TEXT, COLOR_TEXT_LIGHT, COLOR_BORDER
from src.gui.widgets import Card

class EOQClasicoFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_MAIN)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.modelo = None
        
        self.card_form = Card(self, title="Datos de Entrada")
        self.card_form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.card_results = Card(self, title="Resultados del Analisis")
        self.card_results.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        self.build_form()
        self.build_results_placeholder()

    def build_form(self):
        self.entries = {}
        container = tk.Frame(self.card_form, bg=BG_CARD)
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 1. Demanda
        lbl_D = tk.Label(container, text="Demanda:", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=COLOR_TEXT)
        lbl_D.grid(row=0, column=0, sticky="w", pady=(4, 1))
        ent_D = tk.Entry(container, font=("Segoe UI", 9), bd=1, relief="solid", highlightthickness=0)
        ent_D.insert(0, "500")
        ent_D.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        self.entries["D"] = ent_D
        lbl_help_D = tk.Label(container, text="Cantidad requerida en el periodo", font=("Segoe UI", 8), bg=BG_CARD, fg=COLOR_TEXT_LIGHT)
        lbl_help_D.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=(0, 4))
        
        # 2. Frecuencia Demanda
        lbl_frec = tk.Label(container, text="Frecuencia Demanda:", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=COLOR_TEXT)
        lbl_frec.grid(row=2, column=0, sticky="w", pady=(4, 1))
        combo_frec = ttk.Combobox(container, values=["Anual", "Mensual"], state="readonly", font=("Segoe UI", 9))
        combo_frec.set("Anual")
        combo_frec.grid(row=3, column=0, sticky="ew", pady=(0, 4))
        self.entries["frecuencia"] = combo_frec
        lbl_help_frec = tk.Label(container, text="Selecciona si la demanda es Anual o Mensual", font=("Segoe UI", 8), bg=BG_CARD, fg=COLOR_TEXT_LIGHT)
        lbl_help_frec.grid(row=3, column=1, sticky="w", padx=(10, 0), pady=(0, 4))
        
        # 3. Costo de Pedido (S/K)
        lbl_S = tk.Label(container, text="Costo de Pedido (S/K):", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=COLOR_TEXT)
        lbl_S.grid(row=4, column=0, sticky="w", pady=(4, 1))
        ent_S = tk.Entry(container, font=("Segoe UI", 9), bd=1, relief="solid", highlightthickness=0)
        ent_S.insert(0, "5000")
        ent_S.grid(row=5, column=0, sticky="ew", pady=(0, 4))
        self.entries["S"] = ent_S
        lbl_help_S = tk.Label(container, text="Costo fijo por ordenar ($)", font=("Segoe UI", 8), bg=BG_CARD, fg=COLOR_TEXT_LIGHT)
        lbl_help_S.grid(row=5, column=1, sticky="w", padx=(10, 0), pady=(0, 4))

        # 4. Modo de Definicion de Costo de Mantenimiento
        lbl_modo = tk.Label(container, text="Calculo de Mantenimiento:", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=COLOR_PRIMARY)
        lbl_modo.grid(row=6, column=0, sticky="w", pady=(6, 1))
        self.combo_modo_h = ttk.Combobox(container, values=["Ingresar H directamente ($/unid/ano)", "Calcular H = i% x Costo Unitario (C)"], state="readonly", font=("Segoe UI", 9))
        self.combo_modo_h.set("Ingresar H directamente ($/unid/ano)")
        self.combo_modo_h.grid(row=7, column=0, sticky="ew", pady=(0, 4))
        self.combo_modo_h.bind("<<ComboboxSelected>>", self.on_modo_h_change)
        lbl_help_modo = tk.Label(container, text="Selecciona como ingresar o calcular H", font=("Segoe UI", 8), bg=BG_CARD, fg=COLOR_TEXT_LIGHT)
        lbl_help_modo.grid(row=7, column=1, sticky="w", padx=(10, 0), pady=(0, 4))

        # 5. Tasa de Mantenimiento Anual (i%)
        lbl_i = tk.Label(container, text="Tasa Mantenimiento Anual (i%):", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=COLOR_TEXT)
        lbl_i.grid(row=8, column=0, sticky="w", pady=(4, 1))
        ent_i = tk.Entry(container, font=("Segoe UI", 9), bd=1, relief="solid", highlightthickness=0)
        ent_i.insert(0, "0.68")
        ent_i.grid(row=9, column=0, sticky="ew", pady=(0, 4))
        ent_i.bind("<KeyRelease>", self.actualizar_h_calculado)
        self.entries["i"] = ent_i
        self.lbl_help_i = tk.Label(container, text="Porcentaje anual del valor del producto (%)", font=("Segoe UI", 8), bg=BG_CARD, fg=COLOR_TEXT_LIGHT)
        self.lbl_help_i.grid(row=9, column=1, sticky="w", padx=(10, 0), pady=(0, 4))

        # 6. Costo Unitario (C)
        lbl_C = tk.Label(container, text="Costo Unitario (C):", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=COLOR_TEXT)
        lbl_C.grid(row=10, column=0, sticky="w", pady=(4, 1))
        ent_C = tk.Entry(container, font=("Segoe UI", 9), bd=1, relief="solid", highlightthickness=0)
        ent_C.insert(0, "3700")
        ent_C.grid(row=11, column=0, sticky="ew", pady=(0, 4))
        ent_C.bind("<KeyRelease>", self.actualizar_h_calculado)
        self.entries["C"] = ent_C
        self.lbl_help_C = tk.Label(container, text="Precio de compra por unidad ($)", font=("Segoe UI", 8), bg=BG_CARD, fg=COLOR_TEXT_LIGHT)
        self.lbl_help_C.grid(row=11, column=1, sticky="w", padx=(10, 0), pady=(0, 4))

        # 7. Costo de Mantenimiento (H)
        lbl_H = tk.Label(container, text="Costo Mantenimiento (H):", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=COLOR_TEXT)
        lbl_H.grid(row=12, column=0, sticky="w", pady=(4, 1))
        ent_H = tk.Entry(container, font=("Segoe UI", 9), bd=1, relief="solid", highlightthickness=0)
        ent_H.insert(0, "25")
        ent_H.grid(row=13, column=0, sticky="ew", pady=(0, 4))
        self.entries["H"] = ent_H
        self.lbl_help_H = tk.Label(container, text="Costo de mantener una unidad al ano ($)", font=("Segoe UI", 8), bg=BG_CARD, fg=COLOR_TEXT_LIGHT)
        self.lbl_help_H.grid(row=13, column=1, sticky="w", padx=(10, 0), pady=(0, 4))

        container.grid_columnconfigure(0, weight=3)
        container.grid_columnconfigure(1, weight=2)
        
        self.on_modo_h_change()
        
        btn_calc = tk.Button(self.card_form, text="Calcular EOQ", font=("Segoe UI", 10, "bold"),
                             bg=COLOR_PRIMARY, fg="#ffffff", activebackground=COLOR_PRIMARY_HOVER,
                             activeforeground="#ffffff", relief="flat", bd=0, cursor="hand2", pady=8,
                             command=self.calcular)
        btn_calc.pack(fill="x", padx=20, pady=(10, 15))

    def on_modo_h_change(self, event=None):
        modo = self.combo_modo_h.get()
        if "i%" in modo:
            self.entries["i"].config(state="normal")
            self.lbl_help_i.config(text="Requerido para calcular H (ej: 20%)", fg=COLOR_PRIMARY)
            self.lbl_help_C.config(text="Requerido para calcular H ($)", fg=COLOR_PRIMARY)
            self.entries["H"].config(state="readonly")
            self.lbl_help_H.config(text="Auto-calculado: H = (i% x C)", fg=COLOR_TEXT_LIGHT)
            self.actualizar_h_calculado()
        else:
            self.entries["H"].config(state="normal")
            self.lbl_help_H.config(text="Costo directo por unidad/ano ($)", fg=COLOR_PRIMARY)
            self.entries["i"].config(state="disabled")
            self.lbl_help_i.config(text="No requerido en modo directo", fg=COLOR_TEXT_LIGHT)
            self.lbl_help_C.config(text="Precio compra ($) - opcional", fg=COLOR_TEXT_LIGHT)

    def actualizar_h_calculado(self, event=None):
        if "i%" in self.combo_modo_h.get():
            try:
                i_str = self.entries["i"].get().strip()
                c_str = self.entries["C"].get().strip()
                if i_str and c_str:
                    i_val = float(i_str)
                    c_val = float(c_str)
                    h_val = (i_val / 100.0) * c_val
                    self.entries["H"].config(state="normal")
                    self.entries["H"].delete(0, "end")
                    self.entries["H"].insert(0, f"{h_val:.2f}")
                    self.entries["H"].config(state="readonly")
            except ValueError:
                pass

    def build_results_placeholder(self):
        self.results_container = tk.Frame(self.card_results, bg=BG_CARD)
        self.results_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        lbl_msg = tk.Label(self.results_container, text="Introduce los datos y haz clic en\n'Calcular EOQ' para ver los resultados.", 
                           font=("Segoe UI", 10, "italic"), bg=BG_CARD, fg=COLOR_TEXT_LIGHT, justify="center")
        lbl_msg.pack(expand=True)

    def calcular(self):
        try:
            D = float(self.entries["D"].get())
            S = float(self.entries["S"].get())
            
            if D <= 0 or S <= 0:
                messagebox.showerror("Error de Entrada", "La Demanda (D) y el Costo de Pedido (S) deben ser mayores que 0.")
                return
            
            C_str = self.entries["C"].get().strip()
            C = float(C_str) if C_str else 0.0
            
            modo = self.combo_modo_h.get()
            
            if "i%" in modo:
                i_str = self.entries["i"].get().strip()
                if not i_str:
                    messagebox.showerror("Error de Entrada", "Debes ingresar la Tasa de Mantenimiento Anual (i%).")
                    return
                if not C_str or C <= 0:
                    messagebox.showerror("Error de Entrada", "Para calcular H = i% x C, el Costo Unitario (C) debe ser mayor a 0.")
                    return
                i_pct = float(i_str)
                if i_pct <= 0:
                    messagebox.showerror("Error de Entrada", "La tasa de mantenimiento (i%) debe ser mayor a 0.")
                    return
                H = (i_pct / 100.0) * C
            else:
                H_str = self.entries["H"].get().strip()
                if not H_str:
                    messagebox.showerror("Error de Entrada", "Debes ingresar el Costo de Mantenimiento (H).")
                    return
                H = float(H_str)
                i_pct = (H / C * 100.0) if C > 0 else None
                
            if H <= 0:
                messagebox.showerror("Error de Entrada", "El costo de mantenimiento (H) debe ser mayor que 0.")
                return
                
            frecuencia_d = self.entries["frecuencia"].get()
            
            self.modelo = ModeloEOQClasico(
                demanda=D, costo_pedido=S, costo_mantenimiento=H,
                precio_unitario=C,
                es_mensual=(frecuencia_d == "Mensual"),
                i_porcentaje=i_pct, modo_h=modo
            )
            self.modelo.calcular()
            
            for widget in self.results_container.winfo_children():
                widget.destroy()
                
            lbl_eoq_title = tk.Label(self.results_container, text="Lote Optimo de Pedido (EOQ / Q*):", 
                                     font=("Segoe UI", 11), bg=BG_CARD, fg=COLOR_TEXT_LIGHT)
            lbl_eoq_title.pack(anchor="w", pady=(10, 2))
            
            lbl_eoq = tk.Label(self.results_container, text=f"{self.modelo.eoq:.2f} unidades", 
                               font=("Segoe UI", 24, "bold"), bg=BG_CARD, fg=COLOR_PRIMARY)
            lbl_eoq.pack(anchor="w", pady=(0, 15))
            
            sep = tk.Frame(self.results_container, bg=COLOR_BORDER, height=1)
            sep.pack(fill="x", pady=10)
            
            grid_frame = tk.Frame(self.results_container, bg=BG_CARD)
            grid_frame.pack(fill="x", pady=5)
            
            detalles = [
                ("Demanda Anualizada (D):", f"{self.modelo.demanda_anual:.2f} unidades/ano"),
                ("Costo Mantenimiento Unitario (H):", f"${self.modelo.costo_mantenimiento:.2f}/unidad/ano"),
                ("Costo Anual de Pedido:", f"${self.modelo.costo_pedido_anual:.2f}"),
                ("Costo Anual de Mantenimiento:", f"${self.modelo.costo_mantenimiento_anual:.2f}"),
                ("Costo de Adquisicion Anual:", f"${self.modelo.costo_adquisicion_anual:.2f}"),
                ("Costo Total Anual (CT):", f"${self.modelo.costo_total_anual:.2f}"),
                ("Numero de Pedidos Anuales (N):", f"{self.modelo.num_pedidos:.2f} pedidos/ano"),
                ("Frecuencia de Pedido (Meses):", f"{self.modelo.frecuencia_meses:.2f} meses"),
                ("Frecuencia de Pedido (Anos):", f"{self.modelo.frecuencia_anios:.4f} anos")
            ]
            if self.modelo.i_porcentaje is not None:
                detalles.insert(1, ("Tasa Mantenimiento Anual (i%):", f"{self.modelo.i_porcentaje:.2f}%"))
                
            for idx, (lbl_txt, val_txt) in enumerate(detalles):
                font_weight = "bold" if "Total" in lbl_txt else "normal"
                lbl_color = COLOR_PRIMARY if "Total" in lbl_txt else COLOR_TEXT
                
                l_widget = tk.Label(grid_frame, text=lbl_txt, font=("Segoe UI", 10, font_weight), bg=BG_CARD, fg=COLOR_TEXT)
                l_widget.grid(row=idx, column=0, sticky="w", pady=3)
                
                v_widget = tk.Label(grid_frame, text=val_txt, font=("Segoe UI", 10, "bold" if font_weight=="bold" else "normal"), 
                                    bg=BG_CARD, fg=lbl_color)
                v_widget.grid(row=idx, column=1, sticky="e", pady=3)
                
            grid_frame.columnconfigure(0, weight=1)
            grid_frame.columnconfigure(1, weight=1)
            
            btn_export = tk.Button(self.results_container, text="Exportar Reporte (.txt)", font=("Segoe UI", 10, "bold"),
                                   bg="#475569", fg="#ffffff", activebackground="#334155", activeforeground="#ffffff",
                                   relief="flat", bd=0, cursor="hand2", pady=8, command=self.exportar)
            btn_export.pack(fill="x", pady=(20, 0))
            
        except ValueError:
            messagebox.showerror("Error de Entrada", "Por favor ingresa numeros validos en los campos de texto.")

    def exportar(self):
        if not self.modelo:
            messagebox.showwarning("Aviso", "No hay calculos para exportar.")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de Texto", "*.txt")],
            title="Guardar Reporte EOQ"
        )
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.modelo.generar_reporte())
                messagebox.showinfo("Exito", "El reporte se ha exportado correctamente.")
            except Exception as ex:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(ex)}")
