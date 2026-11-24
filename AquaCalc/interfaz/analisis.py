"""Sección educativa de integrales impropias."""

from __future__ import annotations

from tkinter import ttk

from graficas.graficas_modelos import GraficadorModelos
from interfaz.componentes import PanelGrafica, fmt, tarjeta
from interfaz.estado import AppState


class VistaAnalisis(ttk.Frame):
    def __init__(self, padre, estado: AppState):
        super().__init__(padre)
        self.estado = estado
        self.txt_c = None
        self.txt_r = None
        self.grafica = None
        self._construir()
        estado.suscribir(self.refrescar)
        self.refrescar()

    def _construir(self) -> None:
        ttk.Label(self, text="Análisis de integrales impropias", style="Titulo.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            self,
            text="Convergencia frente a divergencia cuando el límite superior tiende a infinito.",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=(0, 8))

        col = ttk.Frame(self)
        izq = tarjeta(col, "Modelo constante")
        self.txt_c = ttk.Label(izq, style="Card.TLabel", wraplength=420, justify="left")
        self.txt_c.pack(anchor="w")
        izq.pack(side="left", fill="both", expand=True, padx=(0, 6))

        der = tarjeta(col, "Modelo racional")
        self.txt_r = ttk.Label(der, style="Card.TLabel", wraplength=420, justify="left")
        self.txt_r.pack(anchor="w")
        der.pack(side="left", fill="both", expand=True, padx=(6, 0))
        col.pack(fill="x", pady=6)

        self.grafica = PanelGrafica(self, figsize=(9.2, 4.4))
        self.grafica.pack(fill="both", expand=True, pady=8)

        extra = tarjeta(self, "Por qué ocurre cada comportamiento")
        ttk.Label(
            extra,
            style="Card.TLabel",
            wraplength=860,
            text=(
                "Una integral impropia ∫₀^∞ q(t) dt converge si el área bajo la curva de la "
                "tasa es finita. En el modelo constante q(t) = A > 0 no se apaga nunca, así "
                "que el área es un rectángulo infinito. En el modelo racional, q(t) decae "
                "como 1/t² para tiempos grandes (producto de dos factores lineales), y esa "
                "decaída es suficiente para que el área restante sea finita. El valor de esa "
                "área se obtiene con el límite analítico [A/(a−b)] ln(a/b), no sustituyendo "
                "infinito en el computador."
            ),
        ).pack(anchor="w")
        extra.pack(fill="x", pady=6)

    def refrescar(self) -> None:
        c = self.estado.modelo_constante()
        r = self.estado.modelo_racional()
        v1 = c.volumen_litros(3600)
        v24 = c.volumen_litros(86400)
        vsem = c.volumen_litros(7 * 86400)
        self.txt_c.configure(
            text=(
                f"Integral parcial: V(T) = ∫₀ᵀ A dt = A × T\n"
                f"A = {fmt(c.A, 6)} ml/s\n\n"
                f"V(1 h) = {fmt(v1, 4)} L\n"
                f"V(24 h) = {fmt(v24, 4)} L\n"
                f"V(1 semana) = {fmt(vsem, 4)} L\n\n"
                f"Resultado: {'divergente' if c.A > 0 else 'nula (A = 0)'}.\n"
                "Al aumentar T, V(T) crece de forma lineal y no se satura."
            )
        )
        inf = r.volumen_infinito_litros()
        self.txt_r.configure(
            text=(
                "Integral parcial:\n"
                "V(T) = ∫₀ᵀ A / [(1+at)(1+bt)] dt\n\n"
                f"V(1 h) = {fmt(r.volumen_litros(3600), 4)} L\n"
                f"V(24 h) = {fmt(r.volumen_litros(86400), 4)} L\n"
                f"V(1 semana) = {fmt(r.volumen_litros(7 * 86400), 4)} L\n"
                f"V(∞) = {fmt(inf, 4)} L  ({fmt(r.volumen_infinito_ml(), 2)} ml)\n\n"
                "Resultado: convergente.\n"
                "El volumen aumenta al principio y luego se acerca a un máximo finito."
            )
        )
        graficador = GraficadorModelos(c, r)
        if self.grafica is not None:
            self.grafica.redibujar(graficador.grafica_analisis_impropia)
