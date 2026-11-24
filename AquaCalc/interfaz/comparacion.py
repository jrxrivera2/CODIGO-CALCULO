"""Comparación simultánea de ambos modelos."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from calculos.constantes import TIEMPOS_COMPARACION
from graficas.graficas_modelos import GraficadorModelos
from interfaz.componentes import PanelGrafica, fmt, tarjeta
from interfaz.estado import AppState


class VistaComparacion(ttk.Frame):
    def __init__(self, padre, estado: AppState):
        super().__init__(padre)
        self.estado = estado
        self.tabla = None
        self.grafica = None
        self.var_h = tk.StringVar(value="168")
        self._construir()
        estado.suscribir(self.refrescar)
        self.refrescar()

    def _construir(self) -> None:
        ttk.Label(self, text="Comparación de modelos", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            self,
            text="Los valores se calculan con las fórmulas analíticas, no están escritos a mano.",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=(0, 8))

        tabla_card = tarjeta(self, "Volumen acumulado según el tiempo")
        columnas = ("tiempo", "constante", "racional")
        self.tabla = ttk.Treeview(tabla_card, columns=columnas, show="headings", height=8)
        self.tabla.heading("tiempo", text="Tiempo")
        self.tabla.heading("constante", text="Modelo constante (L)")
        self.tabla.heading("racional", text="Modelo racional (L)")
        self.tabla.column("tiempo", width=140, anchor="center")
        self.tabla.column("constante", width=220, anchor="center")
        self.tabla.column("racional", width=220, anchor="center")
        self.tabla.pack(fill="x")
        tabla_card.pack(fill="x", pady=6)

        ctrl = ttk.Frame(self)
        ttk.Label(ctrl, text="Horizonte de la gráfica (horas):").pack(side="left")
        ttk.Entry(ctrl, textvariable=self.var_h, width=10).pack(side="left", padx=8)
        ttk.Button(ctrl, text="Actualizar gráfica", style="Acento.TButton", command=self.refrescar).pack(
            side="left"
        )
        ctrl.pack(anchor="w", pady=6)

        self.grafica = PanelGrafica(self, figsize=(8.4, 4.6))
        self.grafica.pack(fill="both", expand=True, pady=6)

        expl = tarjeta(self, "Interpretación")
        ttk.Label(
            expl,
            style="Card.TLabel",
            wraplength=860,
            text=(
                "La línea azul (tasa constante) crece de forma lineal y no se detiene: "
                "si la fuga no se repara, el desperdicio aumenta sin límite. La línea naranja "
                "(tasa racional decreciente) crece de forma más rápida al inicio y después se "
                "aplana hacia un valor máximo finito V(∞). Esa diferencia es exactamente la "
                "distinción entre una integral impropia divergente y una convergente."
            ),
        ).pack(anchor="w")
        expl.pack(fill="x", pady=6)

    def refrescar(self) -> None:
        constante = self.estado.modelo_constante()
        racional = self.estado.modelo_racional()
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for etiqueta, T in TIEMPOS_COMPARACION.items():
            self.tabla.insert(
                "",
                "end",
                values=(
                    etiqueta,
                    fmt(constante.volumen_litros(T), 4),
                    fmt(racional.volumen_litros(T), 4),
                ),
            )
        cte_inf = "Diverge" if constante.A > 0 else fmt(0.0, 4)
        self.tabla.insert(
            "",
            "end",
            values=(
                "Infinito",
                cte_inf,
                fmt(racional.volumen_infinito_litros(), 4),
            ),
        )
        try:
            horas = float(self.var_h.get().replace(",", "."))
            if horas <= 0:
                horas = 168.0
        except ValueError:
            horas = 168.0
        graficador = GraficadorModelos(constante, racional)
        if self.grafica is not None:
            self.grafica.redibujar(lambda fig: graficador.grafica_comparacion(fig, horas=horas))
