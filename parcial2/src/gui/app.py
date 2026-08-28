import tkinter as tk
from src.gui.styles import (
    BG_MAIN, BG_CARD, BG_SIDEBAR, COLOR_PRIMARY,
    COLOR_TEXT, setup_ttk_styles
)
from src.gui.views.eoq_view import EOQClasicoFrame
from src.gui.views.probabilistic_view import ProbabilisticoFrame
from src.gui.views.discount_view import DescuentosTramosFrame
from src.gui.views.constrained_view import RestriccionesFrame

class Application(tk.Tk):
    """
    Ventana principal de la aplicacion de Teoria de Inventarios.
    Maneja el layout general, la barra de navegacion lateral y el intercambio dinamico de vistas.
    """
    def __init__(self, start_tab="eoq_clasico"):
        super().__init__()
        self.title("Sistema de Gestion de Inventarios - Modelos de Decision")
        self.geometry("1150x785")
        self.minsize(1050, 700)
        self.configure(bg=BG_MAIN)
        
        setup_ttk_styles()
        
        self.active_button = None
        self.current_frame = None
        
        self.create_layout()
        self.select_option(start_tab)

    def create_layout(self):
        # Barra lateral de navegacion
        self.sidebar = tk.Frame(self, bg=BG_SIDEBAR, width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        lbl_title = tk.Label(self.sidebar, text="Modelos de Inventario", 
                             font=("Segoe UI", 13, "bold"), fg="#ffffff", bg=BG_SIDEBAR, pady=20)
        lbl_title.pack(fill="x")
        
        self.nav_buttons = {}
        options = [
            ("eoq_clasico", "EOQ Clasico"),
            ("probabilistico", "Modelo Probabilistico"),
            ("descuentos", "Quiebre de Inventario"),
            ("restricciones", "Modelo con Restricciones")
        ]
        
        for code, label in options:
            btn = tk.Button(self.sidebar, text=label, anchor="w", padx=20, pady=12,
                            font=("Segoe UI", 10, "bold"), bg=BG_SIDEBAR, fg="#94a3b8",
                            activebackground="#334155", activeforeground="#ffffff",
                            relief="flat", bd=0, cursor="hand2")
            btn.config(command=lambda c=code: self.select_option(c))
            btn.pack(fill="x")
            
            btn.bind("<Enter>", lambda e, b=btn: self.on_btn_hover(e, b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_btn_leave(e, b))
            
            self.nav_buttons[code] = btn

        # Contenedor principal
        self.main_container = tk.Frame(self, bg=BG_MAIN)
        self.main_container.pack(side="right", expand=True, fill="both")
        
        # Cabecera
        self.header_frame = tk.Frame(self.main_container, bg="#ffffff", height=60, bd=1, relief="solid")
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)
        
        self.header_label = tk.Label(self.header_frame, text="", font=("Segoe UI", 14, "bold"), 
                                     bg="#ffffff", fg=COLOR_TEXT, padx=20, pady=15)
        self.header_label.pack(side="left")

        # Area de contenido dinamico
        self.content_area = tk.Frame(self.main_container, bg=BG_MAIN, padx=25, pady=25)
        self.content_area.pack(expand=True, fill="both", side="bottom")

    def on_btn_hover(self, event, btn):
        if btn != self.active_button:
            btn.config(bg="#334155", fg="#f8fafc")

    def on_btn_leave(self, event, btn):
        if btn != self.active_button:
            btn.config(bg=BG_SIDEBAR, fg="#94a3b8")

    def select_option(self, option_code):
        if self.active_button:
            self.active_button.config(bg=BG_SIDEBAR, fg="#94a3b8")
            
        btn = self.nav_buttons[option_code]
        btn.config(bg=COLOR_PRIMARY, fg="#ffffff")
        self.active_button = btn
        
        self.header_label.config(text=btn.cget("text"))
        
        if self.current_frame:
            self.current_frame.destroy()
            
        if option_code == "eoq_clasico":
            self.current_frame = EOQClasicoFrame(self.content_area)
        elif option_code == "probabilistico":
            self.current_frame = ProbabilisticoFrame(self.content_area)
        elif option_code == "descuentos":
            self.current_frame = DescuentosTramosFrame(self.content_area)
        elif option_code == "restricciones":
            self.current_frame = RestriccionesFrame(self.content_area)
            
        self.current_frame.pack(expand=True, fill="both")
