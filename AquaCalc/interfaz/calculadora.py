"""Sección de calculadora de fugas (modelo V(T) = r × v × T)."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from calculos.constantes import UNIDADES_TIEMPO, VOLUMEN_GOTA_ML
from calculos.validaciones import ValidacionError, validar_no_negativo
from interfaz.componentes import fmt, tarjeta
from interfaz.estado import AppState


class VistaCalculadora(ttk.Frame):
    def __init__(self, padre, estado: AppState):
        super().__init__(padre)
        self.estado = estado
        self.var_r = tk.StringVar(value="1")
        self.var_v = tk.StringVar(value=str(VOLUMEN_GOTA_ML).replace(".", ","))
        self.var_t = tk.StringVar(value="24")
        self.var_unidad = tk.StringVar(value="horas")
        self.res_q = tk.StringVar(value="—")
        self.res_T = tk.StringVar(value="—")
        self.res_ml = tk.StringVar(value="—")
        self.res_L = tk.StringVar(value="—")
        self._construir()

    def _construir(self) -> None:
        ttk.Label(self, text="Calculadora de fugas", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            self,
            text="Ingrese los datos de la fuga. El tiempo se convierte automáticamente a segundos.",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=(0, 12))

        form = tarjeta(self, "Datos de la fuga")
        grid = ttk.Frame(form, style="Card.TFrame")
        self._campo(grid, "Frecuencia de goteo (gotas por segundo)", self.var_r, 0)
        self._campo(grid, "Volumen de cada gota (ml por gota)", self.var_v, 1)
        self._campo(grid, "Tiempo de duración de la fuga", self.var_t, 2)
        ttk.Label(grid, text="Unidad de tiempo", style="Card.TLabel").grid(
            row=3, column=0, sticky="w", pady=6
        )
        combo = ttk.Combobox(
            grid,
            textvariable=self.var_unidad,
            values=list(UNIDADES_TIEMPO.keys()),
            state="readonly",
            width=28,
        )
        combo.grid(row=3, column=1, sticky="w", pady=6, padx=8)
        grid.pack(fill="x")

        botones = ttk.Frame(form, style="Card.TFrame")
        ttk.Button(botones, text="Calcular", style="Acento.TButton", command=self.calcular).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(botones, text="Limpiar campos", command=self.limpiar).pack(side="left")
        botones.pack(anchor="w", pady=(12, 0))
        form.pack(fill="x", pady=6)

        ttk.Label(
            self,
            text="Fórmulas:  q = r × v    ·    V(T) = r × v × T",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=8)

        resultados = ttk.Frame(self)
        for titulo, var in (
            ("Tasa de pérdida q (ml/s)", self.res_q),
            ("Tiempo en segundos", self.res_T),
            ("Volumen acumulado (ml)", self.res_ml),
            ("Volumen acumulado (L)", self.res_L),
        ):
            card = tarjeta(resultados, titulo)
            ttk.Label(card, textvariable=var, style="Valor.TLabel").pack(anchor="w")
            card.pack(side="left", fill="both", expand=True, padx=4)
        resultados.pack(fill="x", pady=8)

        nota = tarjeta(self, "Notas de validación")
        ttk.Label(
            nota,
            style="Card.TLabel",
            wraplength=860,
            text=(
                "No se admiten campos vacíos, valores negativos ni datos no numéricos. "
                "La frecuencia y el tiempo pueden ser cero (no hay goteo o no ha transcurrido "
                "tiempo). El volumen predeterminado de gota es 0,25 ml."
            ),
        ).pack(anchor="w")
        nota.pack(fill="x", pady=6)

    def _campo(self, padre, etiqueta, variable, fila) -> None:
        ttk.Label(padre, text=etiqueta, style="Card.TLabel").grid(
            row=fila, column=0, sticky="w", pady=6
        )
        ttk.Entry(padre, textvariable=variable, width=30).grid(
            row=fila, column=1, sticky="w", pady=6, padx=8
        )

    def calcular(self) -> None:
        try:
            r = validar_no_negativo(self.var_r.get(), "frecuencia de goteo")
            v = validar_no_negativo(self.var_v.get(), "volumen de cada gota")
            t_ing = validar_no_negativo(self.var_t.get(), "tiempo")
            unidad = self.var_unidad.get()
            if unidad not in UNIDADES_TIEMPO:
                raise ValidacionError("Seleccione una unidad de tiempo válida.")
            T = t_ing * UNIDADES_TIEMPO[unidad]
            q = r * v
            V_ml = q * T
            V_L = V_ml / 1000.0
        except ValidacionError as error:
            messagebox.showerror("Dato no válido", str(error))
            return

        self.res_q.set(fmt(q, 6))
        self.res_T.set(fmt(T, 2))
        self.res_ml.set(fmt(V_ml, 4))
        self.res_L.set(fmt(V_L, 6))
        self.estado.actualizar(
            r=r,
            v=v,
            T=T,
            unidad_tiempo=unidad,
            tiempo_ingresado=t_ing,
        )

    def limpiar(self) -> None:
        self.var_r.set("1")
        self.var_v.set(str(VOLUMEN_GOTA_ML).replace(".", ","))
        self.var_t.set("24")
        self.var_unidad.set("horas")
        for var in (self.res_q, self.res_T, self.res_ml, self.res_L):
            var.set("—")
