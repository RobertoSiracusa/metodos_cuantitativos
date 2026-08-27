import tkinter as tk
from tkinter import ttk

# Colores del tema moderno (Slate & Blue)
BG_MAIN = "#f1f5f9"
BG_CARD = "#ffffff"
BG_SIDEBAR = "#1e293b"
COLOR_PRIMARY = "#2563eb"
COLOR_PRIMARY_HOVER = "#1d4ed8"
COLOR_TEXT = "#1e293b"
COLOR_TEXT_LIGHT = "#64748b"
COLOR_ACCENT = "#10b981"
COLOR_BORDER = "#cbd5e1"
COLOR_DANGER = "#ef4444"

def setup_ttk_styles():
    """Configura los estilos globales de TTK para la aplicacion."""
    style = ttk.Style()
    style.theme_use("clam")
    
    style.configure("Treeview", 
                    background=BG_CARD, 
                    foreground=COLOR_TEXT, 
                    rowheight=26, 
                    fieldbackground=BG_CARD,
                    font=("Segoe UI", 10))
    style.configure("Treeview.Heading", 
                    background="#e2e8f0", 
                    foreground=COLOR_TEXT, 
                    font=("Segoe UI", 10, "bold"),
                    relief="flat")
    style.map("Treeview.Heading",
              background=[('active', '#cbd5e1')])
    style.map("Treeview", 
              background=[('selected', '#dbeafe')],
              foreground=[('selected', '#1e40af')])
    
    style.configure("TLabel", background=BG_CARD, foreground=COLOR_TEXT, font=("Segoe UI", 10))
    style.configure("TFrame", background=BG_CARD)
