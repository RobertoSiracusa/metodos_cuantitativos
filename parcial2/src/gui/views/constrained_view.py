import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
from src.core.constrained_model import ModeloRestriccionesInventario
from src.gui.styles import BG_MAIN, BG_CARD, COLOR_PRIMARY, COLOR_TEXT, COLOR_TEXT_LIGHT
from src.gui.widgets import Card

class RestriccionesFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_MAIN)
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=2)
        self.grid_columnconfigure(0, weight=1)
        
        self.modelo = None
        
        self.var_col_area = tk.BooleanVar(value=False)
        self.var_col_precio = tk.BooleanVar(value=False)
        self.var_col_rop = tk.BooleanVar(value=True)
        
        self.card_top = Card(self, title="Articulos e Inventarios (Modelo con Restricciones)")
        self.card_top.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        self.card_bottom = Card(self, title="Optimo Ajustado con Restricciones")
        self.card_bottom.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        
        self.datos_filas = [
            {"name": "A", "D": "100", "S": "20.00", "H": "2.00", "area": "1.0", "C": "10.00", "d": "5", "L": "2"},
            {"name": "B", "D": "150", "S": "25.00", "H": "3.00", "area": "1.0", "C": "15.00", "d": "6", "L": "3"},
            {"name": "C", "D": "200", "S": "30.00", "H": "4.00", "area": "1.0", "C": "20.00", "d": "7", "L": "4"}
        ]
        self.widgets_filas = []
        
        self.build_top_panel()
        self.build_bottom_panel()
        self.reconstruir_tabla()

    def build_top_panel(self):
        rest_frame = tk.Frame(self.card_top, bg=BG_CARD)
        rest_frame.pack(fill="x", padx=15, pady=(5, 2))
        
        lbl_pres = tk.Label(rest_frame, text="Presupuesto Max ($):", font=("Segoe UI", 9, "bold"), bg=BG_CARD)
        lbl_pres.grid(row=0, column=0, sticky="w", padx=5)
        self.ent_presupuesto = tk.Entry(rest_frame, width=10, font=("Segoe UI", 9), bd=1, relief="solid")
        self.ent_presupuesto.insert(0, "1000")
        self.ent_presupuesto.grid(row=0, column=1, sticky="w", padx=5)
        
        lbl_esp = tk.Label(rest_frame, text="Capacidad Almacenamiento (m2 / Unid):", font=("Segoe UI", 9, "bold"), bg=BG_CARD)
        lbl_esp.grid(row=0, column=2, sticky="w", padx=5)
        self.ent_espacio = tk.Entry(rest_frame, width=10, font=("Segoe UI", 9), bd=1, relief="solid")
        self.ent_espacio.insert(0, "500")
        self.ent_espacio.grid(row=0, column=3, sticky="w", padx=5)
        
        lbl_met = tk.Label(rest_frame, text="Metodo:", font=("Segoe UI", 9, "bold"), bg=BG_CARD)
        lbl_met.grid(row=0, column=4, sticky="w", padx=5)
        self.combo_metodo = ttk.Combobox(rest_frame, values=["Multiplicadores de Lagrange (Exacto)", "Aproximacion de Lagrange (Formula)", "Heuristica de Escalamiento Lineal"], state="readonly", font=("Segoe UI", 9), width=32)
        self.combo_metodo.set("Multiplicadores de Lagrange (Exacto)")
        self.combo_metodo.grid(row=0, column=5, sticky="w", padx=5)
        
        col_select_frame = tk.Frame(self.card_top, bg="#f1f5f9", bd=1, relief="solid")
        col_select_frame.pack(fill="x", padx=15, pady=(4, 6))
        
        lbl_cols = tk.Label(col_select_frame, text="Columnas Opcionales:", font=("Segoe UI", 8, "bold"), bg="#f1f5f9", fg=COLOR_TEXT)
        lbl_cols.pack(side="left", padx=(10, 10), pady=3)
        
        chk_area = tk.Checkbutton(col_select_frame, text="Area Unit. (a en m2)", variable=self.var_col_area,
                                  font=("Segoe UI", 8), bg="#f1f5f9", activebackground="#f1f5f9", command=self.reconstruir_tabla)
        chk_area.pack(side="left", padx=8)
        
        chk_precio = tk.Checkbutton(col_select_frame, text="Costo Unitario (C)", variable=self.var_col_precio,
                                    font=("Segoe UI", 8), bg="#f1f5f9", activebackground="#f1f5f9", command=self.reconstruir_tabla)
        chk_precio.pack(side="left", padx=8)
        
        chk_rop = tk.Checkbutton(col_select_frame, text="Punto Reorden (Dem. Diaria 'd' y T. Entrega 'L')", variable=self.var_col_rop,
                                 font=("Segoe UI", 8), bg="#f1f5f9", activebackground="#f1f5f9", command=self.reconstruir_tabla)
        chk_rop.pack(side="left", padx=8)
        
        btn_frame = tk.Frame(self.card_top, bg=BG_CARD)
        btn_frame.pack(fill="x", padx=15, pady=(2, 5))
        
        btn_add = tk.Button(btn_frame, text="+ Agregar Articulo", font=("Segoe UI", 9, "bold"), bg="#10b981", fg="#ffffff",
                            relief="flat", bd=0, cursor="hand2", padx=10, command=self.agregar_articulo)
        btn_add.pack(side="left", padx=(0, 5))
        
        btn_remove = tk.Button(btn_frame, text="- Eliminar Articulo", font=("Segoe UI", 9, "bold"), bg="#ef4444", fg="#ffffff",
                               relief="flat", bd=0, cursor="hand2", padx=10, command=self.eliminar_articulo)
        btn_remove.pack(side="left", padx=5)
        
        btn_solve = tk.Button(btn_frame, text="Optimizar Inventarios", font=("Segoe UI", 10, "bold"), bg=COLOR_PRIMARY, fg="#ffffff",
                              relief="flat", bd=0, cursor="hand2", padx=20, pady=4, command=self.resolver)
        btn_solve.pack(side="right")
        
        self.table_scroll = ttk.Frame(self.card_top)
        self.table_scroll.pack(fill="both", expand=True, padx=15, pady=(2, 10))
        
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

    def guardar_datos_actuales(self):
        for idx, row in enumerate(self.widgets_filas):
            if idx < len(self.datos_filas):
                for key in ["name", "D", "S", "H", "area", "C", "d", "L"]:
                    if key in row:
                        self.datos_filas[idx][key] = row[key].get().strip()

    def reconstruir_tabla(self):
        self.guardar_datos_actuales()
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.widgets_filas.clear()
        
        self.columnas_activas = [
            ("name", "Articulo", 75),
            ("D", "Demanda (D)", 125),
            ("S", "Costo Pedido (S/Cp)", 135),
            ("H", "Costo Almacenaje (H/Cm)", 145)
        ]
        if self.var_col_area.get():
            self.columnas_activas.append(("area", "Area Unit. (a en m2)", 135))
        if self.var_col_precio.get():
            self.columnas_activas.append(("C", "Costo Unitario (C)", 125))
        if self.var_col_rop.get():
            self.columnas_activas.append(("d", "Dem. Diaria (d)", 115))
            self.columnas_activas.append(("L", "T. Entrega (L)", 115))
            
        for col_idx, (key, title, width) in enumerate(self.columnas_activas):
            lbl = tk.Label(self.scrollable_frame, text=title, font=("Segoe UI", 9, "bold"), 
                           bg="#f8fafc", fg=COLOR_TEXT, bd=1, relief="solid", padx=6, pady=5)
            lbl.grid(row=0, column=col_idx, sticky="ew")
            self.scrollable_frame.grid_columnconfigure(col_idx, minsize=width)
            
        for row_idx, item_data in enumerate(self.datos_filas, start=1):
            row_dict = {}
            for col_idx, (key, _, _) in enumerate(self.columnas_activas):
                ent = tk.Entry(self.scrollable_frame, font=("Segoe UI", 9), bd=1, relief="solid", justify="center")
                val = item_data.get(key, "1.0" if key == "area" else ("0" if key in ["d", "L"] else ""))
                ent.insert(0, str(val))
                ent.grid(row=row_idx, column=col_idx, sticky="ew", padx=2, pady=2)
                row_dict[key] = ent
            self.widgets_filas.append(row_dict)
            
        self.actualizar_treeview_columnas()

    def agregar_articulo(self):
        self.guardar_datos_actuales()
        n = len(self.datos_filas) + 1
        self.datos_filas.append({
            "name": f"Art_{n}", "D": "100", "S": "20.00", "H": "2.00",
            "area": "1.0", "C": "10.00", "d": "5", "L": "2"
        })
        self.reconstruir_tabla()

    def eliminar_articulo(self):
        if len(self.datos_filas) <= 1:
            messagebox.showwarning("Aviso", "Debe haber al menos un articulo definido.")
            return
        self.guardar_datos_actuales()
        self.datos_filas.pop()
        self.reconstruir_tabla()

    def build_bottom_panel(self):
        self.results_frame = tk.Frame(self.card_bottom, bg=BG_CARD)
        self.results_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        self.tree_res = ttk.Treeview(self.results_frame, show="headings", height=4)
        self.tree_res.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=5)
        
        bottom_bar = tk.Frame(self.results_frame, bg=BG_CARD)
        bottom_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        
        self.lbl_global_res = tk.Label(bottom_bar, text="Introduce articulos y haz clic en 'Optimizar Inventarios'.", 
                                       font=("Segoe UI", 10, "italic"), bg=BG_CARD, fg=COLOR_TEXT_LIGHT, justify="left")
        self.lbl_global_res.pack(side="left", fill="x", expand=True)
        
        self.btn_export = tk.Button(bottom_bar, text="Exportar Reporte (.txt)", font=("Segoe UI", 9, "bold"), bg="#475569", fg="#ffffff",
                                    relief="flat", bd=0, cursor="hand2", padx=15, pady=4, state="disabled", command=self.exportar)
        self.btn_export.pack(side="right")
        
        self.results_frame.grid_rowconfigure(0, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)

    def actualizar_treeview_columnas(self):
        cols = ["art"]
        if self.var_col_area.get():
            cols.append("area")
        cols.extend(["eoq_clasico", "eoq_ajust"])
        if self.var_col_rop.get():
            cols.append("rop")
            
        self.tree_res.config(columns=cols)
        self.tree_res.heading("art", text="Articulo")
        self.tree_res.column("art", width=100, anchor="center")
        
        if "area" in cols:
            self.tree_res.heading("area", text="Area Unit. (m2)")
            self.tree_res.column("area", width=120, anchor="center")
            
        self.tree_res.heading("eoq_clasico", text="EOQ Clasico")
        self.tree_res.column("eoq_clasico", width=130, anchor="center")
        
        self.tree_res.heading("eoq_ajust", text="Lote Ajustado (Q*)")
        self.tree_res.column("eoq_ajust", width=150, anchor="center")
        
        if "rop" in cols:
            self.tree_res.heading("rop", text="Punto Reorden (ROP)")
            self.tree_res.column("rop", width=150, anchor="center")

    def resolver(self):
        self.guardar_datos_actuales()
        try:
            presupuesto_lim = float(self.ent_presupuesto.get())
            espacio_lim = float(self.ent_espacio.get())
            metodo = self.combo_metodo.get()
            
            articulos = []
            demanda = []
            costo_pedido = []
            costo_almacenamiento = []
            areas = []
            demanda_diaria = []
            tiempo_entrega = []
            
            for item in self.datos_filas:
                name = item["name"] if item["name"] else "Art"
                D = float(item["D"])
                S = float(item["S"])
                H = float(item["H"])
                a_val = float(item["area"]) if (self.var_col_area.get() and item.get("area")) else 1.0
                d_diaria = float(item["d"]) if (self.var_col_rop.get() and item.get("d")) else 0.0
                L = float(item["L"]) if (self.var_col_rop.get() and item.get("L")) else 0.0
                
                articulos.append(name)
                demanda.append(D)
                costo_pedido.append(S)
                costo_almacenamiento.append(H)
                areas.append(a_val)
                demanda_diaria.append(d_diaria)
                tiempo_entrega.append(L)
                
            self.modelo = ModeloRestriccionesInventario(
                articulos=articulos, demandas=demanda, costos_pedido=costo_pedido,
                costos_almacenamiento=costo_almacenamiento, capacidad_total=espacio_lim,
                presupuesto=presupuesto_lim, demandas_diarias=demanda_diaria,
                tiempos_entrega=tiempo_entrega, areas=areas, metodo=metodo
            )
            self.modelo.calcular()
            
            for row in self.tree_res.get_children():
                self.tree_res.delete(row)
                
            for art in self.modelo.articulos:
                info = self.modelo.resultados_articulos[art]
                eoq_c = info.get("eoq_clasico", 0.0)
                if eoq_c == 0.0:
                    idx = self.modelo.articulos.index(art)
                    eoq_c = math.sqrt((2 * self.modelo.demandas[idx] * self.modelo.costos_pedido[idx]) / self.modelo.costos_almacenamiento[idx])
                
                row_vals = [art]
                if self.var_col_area.get():
                    row_vals.append(f"{info['area_unit']:.2f} m2")
                row_vals.extend([f"{eoq_c:.2f}", f"{info['cantidad_pedir']:.2f}"])
                if self.var_col_rop.get():
                    row_vals.append(f"{info['rop']:.2f}")
                    
                self.tree_res.insert("", "end", values=tuple(row_vals))
                
            lambda_info = f" | lambda = {self.modelo.lambda_calculado:.4f}" if self.modelo.lambda_calculado > 0 else ""
            if self.modelo.lambda_aprox > 0:
                lambda_info += f" (lambda aprox: {self.modelo.lambda_aprox:.4f})"
                
            unidad_espacio = "m2" if self.var_col_area.get() else "unidades"
            self.lbl_global_res.config(
                text=f"Metodo: {metodo} | Estado: {self.modelo.status}{lambda_info}\n"
                     f"Costo Total Optimizado: ${self.modelo.costo_total:.2f} (Almacenaje: ${self.modelo.costo_mantenimiento:.2f})\n"
                     f"Espacio/Area Utilizada: {self.modelo.espacio_utilizado:.2f} / {espacio_lim:.2f} {unidad_espacio}\n"
                     f"Presupuesto Utilizado: ${self.modelo.presupuesto_utilizado:.2f} / ${presupuesto_lim:.2f}",
                fg=COLOR_PRIMARY,
                font=("Segoe UI", 9, "bold")
            )
            self.btn_export.config(state="normal")
            
        except ValueError as ex:
            messagebox.showerror("Error de Entrada", f"Verifica que los datos ingresados sean correctos: {str(ex)}")

    def exportar(self):
        if not self.modelo:
            messagebox.showwarning("Aviso", "No hay calculos para exportar.")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de Texto", "*.txt")],
            title="Guardar Reporte de Restricciones"
        )
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.modelo.generar_reporte())
                messagebox.showinfo("Exito", "El reporte se ha exportado correctamente.")
            except Exception as ex:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(ex)}")
