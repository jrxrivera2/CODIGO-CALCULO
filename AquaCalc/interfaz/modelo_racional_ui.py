"""Sección del modelo racional decreciente."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from calculos.validaciones import ValidacionError, validar_no_negativo, validar_positivo
from graficas.graficas_modelos import GraficadorModelos
from interfaz.componentes import PanelGrafica, fmt, tarjeta
from interfaz.estado import AppState


class VistaRacional(ttk.Frame):
    def __init__(self, padre, estado: AppState):
        super().__init__(padre)
        self.estado = estado
        self.var_r = tk.StringVar()
        self.var_v = tk.StringVar()
        self.var_a = tk.StringVar()
        self.var_b = tk.StringVar()
        self.var_h = tk.StringVar(value="168")
        self.var_P = tk.StringVar()
        self.var_Q = tk.StringVar()
        self.var_VT = tk.StringVar()
        self.var_inf_ml = tk.StringVar()
        self.var_inf_L = tk.StringVar()
        self.mensaje = tk.StringVar()
        self.aviso_ab = tk.StringVar()
        self.grafica_v = None
        self.grafica_q = None
        self._construir()
        estado.suscribir(self.sincronizar)
        self.sincronizar()

    def _construir(self) -> None:
        ttk.Label(self, text="Modelo de tasa racional decreciente", style="Titulo.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            self,
            text="q(t) = A / [(1 + a t)(1 + b t)]    ·    la tasa disminuye con el tiempo",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=(0, 8))

        form = tarjeta(self, "Parámetros (A = r × v)")
        grid = ttk.Frame(form, style="Card.TFrame")
        self._campo(grid, "Frecuencia r (gotas/s)", self.var_r, 0)
        self._campo(grid, "Volumen de gota v (ml)", self.var_v, 1)
        self._campo(grid, "Constante a (s⁻¹)", self.var_a, 2)
        self._campo(grid, "Constante b (s⁻¹)", self.var_b, 3)
        self._campo(grid, "Horizonte de gráfica (horas)", self.var_h, 4)
        ttk.Button(
            grid, text="Actualizar modelo y gráfica", style="Acento.TButton", command=self.aplicar
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=8)
        ttk.Label(
            grid,
            text="Valores predeterminados: a = 1/3600  (1 hora)    b = 1/86400  (1 día)",
            style="Card.TLabel",
        ).grid(row=6, column=0, columnspan=2, sticky="w")
        grid.pack(anchor="w")
        form.pack(fill="x", pady=6)

        ttk.Label(self, textvariable=self.aviso_ab, style="Subtitulo.TLabel").pack(anchor="w")

        fp = tarjeta(self, "Descomposición en fracciones parciales")
        ttk.Label(
            fp,
            style="Card.TLabel",
            wraplength=860,
            text="A / [(1 + at)(1 + bt)] = P/(1 + at) + Q/(1 + bt),  con  P = A a/(a − b)  y  Q = −A b/(a − b).",
        ).pack(anchor="w")
        fila = ttk.Frame(fp, style="Card.TFrame")
        ttk.Label(fila, text="P =", style="Card.TLabel").pack(side="left")
        ttk.Label(fila, textvariable=self.var_P, style="Valor.TLabel").pack(side="left", padx=(4, 20))
        ttk.Label(fila, text="Q =", style="Card.TLabel").pack(side="left")
        ttk.Label(fila, textvariable=self.var_Q, style="Valor.TLabel").pack(side="left", padx=4)
        fila.pack(anchor="w", pady=6)
        fp.pack(fill="x", pady=6)

        integ = tarjeta(self, "Integración analítica")
        ttk.Label(
            integ,
            style="Card.TLabel",
            wraplength=860,
            text=(
                "∫ P/(1+at) dt = (P/a) ln(1+at) + C\n"
                "∫ Q/(1+bt) dt = (Q/b) ln(1+bt) + C\n"
                "V(T) = [A/(a − b)] × ln[(1 + aT)/(1 + bT)]   (ml)\n"
                "V(∞) = [A/(a − b)] × ln(a/b)   (límite analítico, sin sustituir infinito)"
            ),
        ).pack(anchor="w")
        integ.pack(fill="x", pady=6)

        cards = ttk.Frame(self)
        for titulo, var in (
            ("V(T) en el horizonte (L)", self.var_VT),
            ("V(∞) (ml)", self.var_inf_ml),
            ("V(∞) (L)", self.var_inf_L),
        ):
            card = tarjeta(cards, titulo)
            ttk.Label(card, textvariable=var, style="Valor.TLabel").pack(anchor="w")
            card.pack(side="left", fill="both", expand=True, padx=4)
        cards.pack(fill="x", pady=6)

        msg = tarjeta(self, "Integral impropia")
        ttk.Label(msg, textvariable=self.mensaje, style="Card.TLabel", wraplength=860).pack(
            anchor="w"
        )
        msg.pack(fill="x", pady=6)

        self.grafica_v = PanelGrafica(self, figsize=(8.2, 3.6))
        self.grafica_v.pack(fill="both", expand=True, pady=6)
        self.grafica_q = PanelGrafica(self, figsize=(8.2, 3.2), con_toolbar=False)
        self.grafica_q.pack(fill="both", expand=True, pady=6)

    def _campo(self, padre, texto, variable, fila) -> None:
        ttk.Label(padre, text=texto, style="Card.TLabel").grid(row=fila, column=0, sticky="w", pady=4)
        ttk.Entry(padre, textvariable=variable, width=24).grid(
            row=fila, column=1, sticky="w", padx=8, pady=4
        )

    def sincronizar(self) -> None:
        self.var_r.set(str(self.estado.r).replace(".", ","))
        self.var_v.set(str(self.estado.v).replace(".", ","))
        self.var_a.set(str(self.estado.a))
        self.var_b.set(str(self.estado.b))
        self._refrescar()

    def aplicar(self) -> None:
        try:
            r = validar_no_negativo(self.var_r.get(), "frecuencia de goteo")
            v = validar_no_negativo(self.var_v.get(), "volumen de cada gota")
            a = validar_positivo(self.var_a.get(), "constante a")
            b = validar_positivo(self.var_b.get(), "constante b")
            h = validar_no_negativo(self.var_h.get(), "horizonte")
            if h == 0:
                raise ValidacionError("El horizonte de la gráfica debe ser mayor que cero.")
        except ValidacionError as error:
            messagebox.showerror("Dato no válido", str(error))
            return
        self.estado.actualizar(r=r, v=v, a=a, b=b)
        self._refrescar()

    def _refrescar(self) -> None:
        modelo = self.estado.modelo_racional()
        try:
            horas = validar_no_negativo(self.var_h.get(), "horizonte")
            if horas == 0:
                horas = 168.0
        except ValidacionError:
            horas = 168.0
        T = horas * 3600.0
        fp = modelo.fracciones_parciales()
        if modelo.factores_iguales:
            self.aviso_ab.set(
                "Atención: a = b. No se usa la descomposición para factores distintos. "
                "Se aplica V(T) = A T / (1 + a T)  y  V(∞) = A / a."
            )
            self.var_P.set("caso a = b")
            self.var_Q.set("—")
        else:
            self.aviso_ab.set("")
            self.var_P.set(fmt(fp.P, 8))
            self.var_Q.set(fmt(fp.Q, 8))
        impropia = modelo.integral_impropia()
        self.var_VT.set(fmt(modelo.volumen_litros(T), 4))
        self.var_inf_ml.set(fmt(impropia.volumen_infinito_ml, 4))
        self.var_inf_L.set(fmt(impropia.volumen_infinito_L, 4))
        self.mensaje.set(impropia.mensaje)
        graficador = GraficadorModelos(self.estado.modelo_constante(), modelo)
        if self.grafica_v is not None:
            self.grafica_v.redibujar(lambda fig: graficador.grafica_racional(fig, horas=horas))
        if self.grafica_q is not None:
            self.grafica_q.redibujar(
                lambda fig: graficador.grafica_tasa_racional(fig, horas=min(horas, 72))
            )
