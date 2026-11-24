"""Ventana principal con panel lateral de navegación."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from interfaz.analisis import VistaAnalisis
from interfaz.calculadora import VistaCalculadora
from interfaz.comparacion import VistaComparacion
from interfaz.componentes import COLORES, aplicar_estilo
from interfaz.estado import AppState
from interfaz.inicio import VistaInicio
from interfaz.modelo_constante_ui import VistaConstante
from interfaz.modelo_racional_ui import VistaRacional
from interfaz.resultados import VistaResultados


SECCIONES = [
    ("inicio", "Inicio"),
    ("calculadora", "Calculadora de fugas"),
    ("constante", "Modelo de tasa constante"),
    ("racional", "Modelo racional decreciente"),
    ("comparacion", "Comparación de modelos"),
    ("analisis", "Análisis de integrales impropias"),
    ("resultados", "Resultados y reportes"),
]


class VentanaPrincipal(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("AquaCalc – Calculadora de Desperdicio de Agua")
        self.geometry("1280x820")
        self.minsize(1024, 680)
        self.configure(bg=COLORES["fondo"])
        aplicar_estilo(self)

        self.estado = AppState()
        self._botones: dict[str, tk.Button] = {}
        self._vistas: dict[str, ttk.Frame] = {}
        self._clave_actual = "inicio"

        self._construir_layout()
        self.mostrar("inicio")

    def _construir_layout(self) -> None:
        sidebar = tk.Frame(self, bg=COLORES["sidebar"], width=260)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="AquaCalc",
            bg=COLORES["sidebar"],
            fg="white",
            font=("Segoe UI Semibold", 18),
        ).pack(anchor="w", padx=20, pady=(22, 0))
        tk.Label(
            sidebar,
            text="Desperdicio de agua\nIntegrales impropias",
            bg=COLORES["sidebar"],
            fg="#B7D6DE",
            font=("Segoe UI", 10),
            justify="left",
        ).pack(anchor="w", padx=20, pady=(4, 18))

        for clave, titulo in SECCIONES:
            boton = tk.Button(
                sidebar,
                text=titulo,
                anchor="w",
                bd=0,
                padx=18,
                pady=12,
                font=("Segoe UI", 10),
                fg="white",
                bg=COLORES["sidebar"],
                activebackground=COLORES["sidebar_hover"],
                activeforeground="white",
                cursor="hand2",
                command=lambda k=clave: self.mostrar(k),
            )
            boton.pack(fill="x")
            self._botones[clave] = boton

        tk.Label(
            sidebar,
            text="v1.0  ·  Python · Tkinter",
            bg=COLORES["sidebar"],
            fg="#7EA8B2",
            font=("Segoe UI", 8),
        ).pack(side="bottom", pady=16)

        cuerpo = ttk.Frame(self)
        cuerpo.pack(side="right", fill="both", expand=True)

        self.area = tk.Canvas(cuerpo, bg=COLORES["fondo"], highlightthickness=0)
        scroll = ttk.Scrollbar(cuerpo, orient="vertical", command=self.area.yview)
        self.contenedor = ttk.Frame(self.area, padding=22)
        self.contenedor.bind(
            "<Configure>",
            lambda e: self.area.configure(scrollregion=self.area.bbox("all")),
        )
        self._win = self.area.create_window((0, 0), window=self.contenedor, anchor="nw")
        self.area.configure(yscrollcommand=scroll.set)
        self.area.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.area.bind("<Configure>", self._ajustar)
        self.area.bind_all("<MouseWheel>", self._rueda)

        constructores = {
            "inicio": lambda: VistaInicio(self.contenedor, self.estado, self.mostrar),
            "calculadora": lambda: VistaCalculadora(self.contenedor, self.estado),
            "constante": lambda: VistaConstante(self.contenedor, self.estado),
            "racional": lambda: VistaRacional(self.contenedor, self.estado),
            "comparacion": lambda: VistaComparacion(self.contenedor, self.estado),
            "analisis": lambda: VistaAnalisis(self.contenedor, self.estado),
            "resultados": lambda: VistaResultados(self.contenedor, self.estado),
        }
        for clave, factory in constructores.items():
            vista = factory()
            self._vistas[clave] = vista

    def _ajustar(self, evento) -> None:
        self.area.itemconfigure(self._win, width=evento.width)

    def _rueda(self, evento) -> None:
        self.area.yview_scroll(int(-evento.delta / 120), "units")

    def mostrar(self, clave: str) -> None:
        for vista in self._vistas.values():
            vista.pack_forget()
        self._vistas[clave].pack(fill="both", expand=True)
        self._clave_actual = clave
        for k, boton in self._botones.items():
            boton.configure(
                bg=COLORES["sidebar_activo"] if k == clave else COLORES["sidebar"]
            )
        self.area.yview_moveto(0)
        # Las vistas con gráficas se refrescan al suscribirse; forzamos un update visual.
        vista = self._vistas[clave]
        if hasattr(vista, "refrescar"):
            vista.refrescar()
        elif hasattr(vista, "sincronizar"):
            vista.sincronizar()
