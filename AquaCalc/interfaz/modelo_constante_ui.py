"""Sección del modelo de tasa constante."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from calculos.validaciones import ValidacionError, validar_no_negativo
from interfaz.componentes import PanelGrafica, fmt, tarjeta
from interfaz.estado import AppState
from graficas.graficas_modelos import GraficadorModelos


class VistaConstante(ttk.Frame):
    def __init__(self, padre, estado: AppState):
        super().__init__(padre)
        self.estado = estado
        self.var_r = tk.StringVar()
        self.var_v = tk.StringVar()
        self.var_h = tk.StringVar(value="24")
        self.var_A = tk.StringVar()
        self.var_VT = tk.StringVar()
        self.var_lim = tk.StringVar()
        self.mensaje = tk.StringVar()
        self.grafica = None
        self._construir()
        estado.suscribir(self.sincronizar)
        self.sincronizar()

    def _construir(self) -> None:
        ttk.Label(self, text="Modelo de tasa constante", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            self,
            text="q(t) = A    ·    V(T) = ∫₀ᵀ A dt = A × T    ·    A = r × v",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=(0, 10))

        form = tarjeta(self, "Parámetros")
        grid = ttk.Frame(form, style="Card.TFrame")
        self._campo(grid, "Frecuencia r (gotas/s)", self.var_r, 0)
        self._campo(grid, "Volumen de gota v (ml)", self.var_v, 1)
        self._campo(grid, "Horizonte de gráfica (horas)", self.var_h, 2)
        ttk.Button(
            grid, text="Actualizar modelo y gráfica", style="Acento.TButton", command=self.aplicar
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=8)
        grid.pack(anchor="w")
        form.pack(fill="x", pady=6)

        cards = ttk.Frame(self)
        for titulo, var in (
            ("Tasa A (ml/s)", self.var_A),
            ("V(T) en el horizonte (L)", self.var_VT),
            ("Integral impropia ∫₀^∞ A dt", self.var_lim),
        ):
            card = tarjeta(cards, titulo)
            ttk.Label(card, textvariable=var, style="Valor.TLabel").pack(anchor="w")
            card.pack(side="left", fill="both", expand=True, padx=4)
        cards.pack(fill="x", pady=6)

        msg = tarjeta(self, "Análisis de la integral impropia")
        ttk.Label(msg, textvariable=self.mensaje, style="Card.TLabel", wraplength=860).pack(
            anchor="w"
        )
        msg.pack(fill="x", pady=6)

        self.grafica = PanelGrafica(self)
        self.grafica.pack(fill="both", expand=True, pady=8)

    def _campo(self, padre, texto, variable, fila) -> None:
        ttk.Label(padre, text=texto, style="Card.TLabel").grid(row=fila, column=0, sticky="w", pady=4)
        ttk.Entry(padre, textvariable=variable, width=22).grid(
            row=fila, column=1, sticky="w", padx=8, pady=4
        )

    def sincronizar(self) -> None:
        self.var_r.set(str(self.estado.r).replace(".", ","))
        self.var_v.set(str(self.estado.v).replace(".", ","))
        self._refrescar_resultados()

    def aplicar(self) -> None:
        try:
            r = validar_no_negativo(self.var_r.get(), "frecuencia de goteo")
            v = validar_no_negativo(self.var_v.get(), "volumen de cada gota")
            h = validar_no_negativo(self.var_h.get(), "horizonte")
            if h == 0:
                raise ValidacionError("El horizonte de la gráfica debe ser mayor que cero.")
        except ValidacionError as error:
            messagebox.showerror("Dato no válido", str(error))
            return
        self.estado.actualizar(r=r, v=v)
        self._refrescar_resultados()

    def _refrescar_resultados(self) -> None:
        modelo = self.estado.modelo_constante()
        try:
            horas = validar_no_negativo(self.var_h.get(), "horizonte")
            if horas == 0:
                horas = 24.0
        except ValidacionError:
            horas = 24.0
        T = horas * 3600.0
        impropia = modelo.integral_impropia()
        self.var_A.set(fmt(modelo.A, 6))
        self.var_VT.set(fmt(modelo.volumen_litros(T), 4))
        self.var_lim.set("Diverge (∞)" if impropia.diverge else impropia.limite_descripcion)
        self.mensaje.set(impropia.mensaje)
        graficador = GraficadorModelos(modelo, self.estado.modelo_racional())
        if self.grafica is not None:
            self.grafica.redibujar(lambda fig: graficador.grafica_constante(fig, horas=horas))
