"""Componentes reutilizables de la interfaz."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


COLORES = {
    "fondo": "#EEF4F7",
    "sidebar": "#0B3D4A",
    "sidebar_hover": "#145869",
    "sidebar_activo": "#1A7A8C",
    "tarjeta": "#FFFFFF",
    "texto": "#14323D",
    "texto_suave": "#4A6670",
    "acento": "#1A7A8C",
    "acento_oscuro": "#0E5A68",
    "peligro": "#B42318",
    "exito": "#0B6E4F",
    "borde": "#D5E3EA",
    "titulo": "#0B3D4A",
}


def fmt(numero: float, decimales: int = 4) -> str:
    """Formatea un número con coma decimal (español)."""
    texto = f"{numero:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def aplicar_estilo(raiz: tk.Tk) -> None:
    estilo = ttk.Style(raiz)
    try:
        estilo.theme_use("clam")
    except tk.TclError:
        pass
    estilo.configure("TFrame", background=COLORES["fondo"])
    estilo.configure("Card.TFrame", background=COLORES["tarjeta"])
    estilo.configure(
        "TLabel",
        background=COLORES["fondo"],
        foreground=COLORES["texto"],
        font=("Segoe UI", 10),
    )
    estilo.configure(
        "Card.TLabel",
        background=COLORES["tarjeta"],
        foreground=COLORES["texto"],
        font=("Segoe UI", 10),
    )
    estilo.configure(
        "Titulo.TLabel",
        background=COLORES["fondo"],
        foreground=COLORES["titulo"],
        font=("Segoe UI Semibold", 20),
    )
    estilo.configure(
        "Subtitulo.TLabel",
        background=COLORES["fondo"],
        foreground=COLORES["texto_suave"],
        font=("Segoe UI", 11),
    )
    estilo.configure(
        "CardTitulo.TLabel",
        background=COLORES["tarjeta"],
        foreground=COLORES["titulo"],
        font=("Segoe UI Semibold", 12),
    )
    estilo.configure(
        "Valor.TLabel",
        background=COLORES["tarjeta"],
        foreground=COLORES["acento_oscuro"],
        font=("Segoe UI Semibold", 16),
    )
    estilo.configure(
        "TButton",
        font=("Segoe UI", 10),
        padding=8,
    )
    estilo.configure(
        "Acento.TButton",
        background=COLORES["acento"],
        foreground="white",
        font=("Segoe UI Semibold", 10),
        padding=8,
    )
    estilo.map(
        "Acento.TButton",
        background=[("active", COLORES["acento_oscuro"])],
        foreground=[("active", "white")],
    )
    estilo.configure(
        "TEntry",
        fieldbackground="white",
        padding=5,
    )
    estilo.configure(
        "TCombobox",
        fieldbackground="white",
        padding=5,
    )
    estilo.configure(
        "Treeview",
        font=("Segoe UI", 10),
        rowheight=28,
        background="white",
        fieldbackground="white",
    )
    estilo.configure(
        "Treeview.Heading",
        font=("Segoe UI Semibold", 10),
        background=COLORES["sidebar"],
        foreground="white",
    )
    estilo.map("Treeview.Heading", background=[("active", COLORES["sidebar_activo"])])


def tarjeta(padre, titulo: str) -> ttk.Frame:
    marco = ttk.Frame(padre, style="Card.TFrame", padding=16)
    ttk.Label(marco, text=titulo, style="CardTitulo.TLabel").pack(anchor="w", pady=(0, 8))
    return marco


def etiqueta_valor(padre, titulo: str, variable: tk.StringVar) -> ttk.Frame:
    caja = ttk.Frame(padre, style="Card.TFrame")
    ttk.Label(caja, text=titulo, style="Card.TLabel").pack(anchor="w")
    ttk.Label(caja, textvariable=variable, style="Valor.TLabel").pack(anchor="w")
    return caja


class PanelGrafica:
    """Figura de Matplotlib incrustada en Tkinter, con barra de herramientas."""

    def __init__(self, padre, figsize=(8.2, 4.4), con_toolbar: bool = True):
        self.contenedor = ttk.Frame(padre, style="Card.TFrame")
        self.figura = Figure(figsize=figsize, dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figura, master=self.contenedor)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        if con_toolbar:
            barra = NavigationToolbar2Tk(self.canvas, self.contenedor, pack_toolbar=False)
            barra.update()
            barra.pack(side="bottom", fill="x")

    def pack(self, **kwargs):
        self.contenedor.pack(**kwargs)

    def redibujar(self, dibujar: Callable[[Figure], None]) -> None:
        dibujar(self.figura)
        self.canvas.draw_idle()


class MarcoDesplazable(ttk.Frame):
    """Contenedor con barra de desplazamiento vertical."""

    def __init__(self, padre, **kwargs):
        super().__init__(padre, **kwargs)
        self.canvas_tk = tk.Canvas(self, highlightthickness=0, bg=COLORES["fondo"])
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas_tk.yview)
        self.interior = ttk.Frame(self.canvas_tk)
        self.interior.bind(
            "<Configure>",
            lambda e: self.canvas_tk.configure(scrollregion=self.canvas_tk.bbox("all")),
        )
        self._ventana = self.canvas_tk.create_window((0, 0), window=self.interior, anchor="nw")
        self.canvas_tk.configure(yscrollcommand=scrollbar.set)
        self.canvas_tk.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas_tk.bind("<Configure>", self._ajustar_ancho)
        self.canvas_tk.bind_all("<MouseWheel>", self._rueda)

    def _ajustar_ancho(self, evento) -> None:
        self.canvas_tk.itemconfigure(self._ventana, width=evento.width)

    def _rueda(self, evento) -> None:
        self.canvas_tk.yview_scroll(int(-evento.delta / 120), "units")
