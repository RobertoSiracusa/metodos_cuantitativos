import tkinter as tk
from src.gui.styles import BG_CARD, COLOR_TEXT, COLOR_BORDER

class Card(tk.Frame):
    """Componente visual de tarjeta con borde sutil y titulo opcional."""
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, bg=BG_CARD, bd=0, **kwargs)
        self.config(highlightbackground=COLOR_BORDER, highlightcolor=COLOR_BORDER, highlightthickness=1)
        
        if title:
            lbl = tk.Label(self, text=title, font=("Segoe UI", 11, "bold"), bg=BG_CARD, fg=COLOR_TEXT, anchor="w")
            lbl.pack(fill="x", padx=15, pady=(12, 5))
            
            sep = tk.Frame(self, bg=COLOR_BORDER, height=1)
            sep.pack(fill="x", padx=15, pady=(0, 10))
