"""Pantalla de bienvenida de AquaCalc."""

from __future__ import annotations

from tkinter import ttk

from interfaz.componentes import tarjeta
from interfaz.estado import AppState


class VistaInicio(ttk.Frame):
    def __init__(self, padre, estado: AppState, ir_a):
        super().__init__(padre)
        self.estado = estado
        self.ir_a = ir_a
        self._construir()

    def _construir(self) -> None:
        ttk.Label(self, text="AquaCalc", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            self,
            text="Calculadora de Desperdicio de Agua mediante integrales impropias",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=(0, 16))

        intro = tarjeta(self, "Propósito del software")
        ttk.Label(
            intro,
            style="Card.TLabel",
            wraplength=860,
            justify="left",
            text=(
                "AquaCalc estima el volumen de agua desperdiciado por una fuga de grifo "
                "a partir de la frecuencia de goteo y el volumen de cada gota. Combina "
                "cálculo integral, descomposición en fracciones parciales y visualización "
                "para comparar un modelo de tasa constante (integral divergente) con un "
                "modelo racional decreciente (integral convergente)."
            ),
        ).pack(anchor="w")
        intro.pack(fill="x", pady=8)

        objetivo = tarjeta(self, "Objetivo principal")
        ttk.Label(
            objetivo,
            style="Card.TLabel",
            wraplength=860,
            justify="left",
            text=(
                "Demostrar, con fórmulas analíticas y validación numérica, cómo se "
                "acumula el desperdicio en el tiempo y qué ocurre cuando el tiempo "
                "tiende a infinito: el modelo constante no tiene cota, mientras que el "
                "modelo racional se aproxima a un volumen máximo finito."
            ),
        ).pack(anchor="w")
        objetivo.pack(fill="x", pady=8)

        uso = tarjeta(self, "Cómo funciona")
        ttk.Label(
            uso,
            style="Card.TLabel",
            wraplength=860,
            justify="left",
            text=(
                "1. Ingrese la frecuencia de goteo, el volumen de gota y el tiempo en "
                "la calculadora.\n"
                "2. Analice el modelo constante q(t) = A y el modelo racional "
                "q(t) = A / [(1 + at)(1 + bt)].\n"
                "3. Compare ambos en una misma tabla y gráfica.\n"
                "4. Revise la convergencia o divergencia de las integrales impropias.\n"
                "5. Exporte CSV, PNG y un reporte PDF."
            ),
        ).pack(anchor="w")
        uso.pack(fill="x", pady=8)

        indicadores = ttk.Frame(self)
        for titulo, valor in (
            ("Volumen de referencia por gota", "0,25 ml"),
            ("Unidad de tiempo", "segundos (conversión automática)"),
            ("Unidades de volumen", "mililitros y litros"),
        ):
            card = tarjeta(indicadores, titulo)
            ttk.Label(card, text=valor, style="Valor.TLabel").pack(anchor="w")
            card.pack(side="left", fill="both", expand=True, padx=4)
        indicadores.pack(fill="x", pady=8)

        accesos = tarjeta(self, "Acceso a las herramientas")
        botones = ttk.Frame(accesos, style="Card.TFrame")
        destinos = [
            ("Calculadora de fugas", "calculadora"),
            ("Modelo constante", "constante"),
            ("Modelo racional", "racional"),
            ("Comparación", "comparacion"),
            ("Integrales impropias", "analisis"),
            ("Resultados y reportes", "resultados"),
        ]
        for i, (texto, clave) in enumerate(destinos):
            ttk.Button(
                botones,
                text=texto,
                style="Acento.TButton",
                command=lambda k=clave: self.ir_a(k),
            ).grid(row=i // 3, column=i % 3, padx=6, pady=6, sticky="ew")
        for col in range(3):
            botones.columnconfigure(col, weight=1)
        botones.pack(fill="x")
        accesos.pack(fill="x", pady=8)
