"""Construcción de las gráficas del proyecto sobre figuras de Matplotlib."""

from __future__ import annotations

import numpy as np
from matplotlib.figure import Figure

from calculos.constantes import ML_POR_LITRO, VOLUMEN_GOTA_ML
from calculos.modelo_constante import ModeloConstante
from calculos.modelo_racional import ModeloRacional
from graficas.estilos import COLORES, aplicar_estilo


class GraficadorModelos:
    """Dibuja las cuatro gráficas académicas y las vistas de cada sección."""

    def __init__(self, constante: ModeloConstante, racional: ModeloRacional):
        self.constante = constante
        self.racional = racional

    def actualizar(self, constante: ModeloConstante, racional: ModeloRacional) -> None:
        self.constante = constante
        self.racional = racional

    def grafica_constante(self, figura: Figure, horas: float = 24.0) -> None:
        """Gráfica 1 / sección constante: volumen acumulado vs tiempo."""
        figura.clear()
        eje = figura.add_subplot(111)
        t_h = np.linspace(0, horas, 400)
        t_s = t_h * 3600.0
        v_L = np.array([self.constante.volumen_litros(t) for t in t_s])
        eje.plot(t_h, v_L, color=COLORES["constante"], linewidth=2.4, label="V(T) = A·T")
        eje.set_title("Desperdicio acumulado – Modelo de tasa constante")
        eje.set_xlabel("Tiempo (horas)")
        eje.set_ylabel("Volumen acumulado (L)")
        eje.legend()
        aplicar_estilo(figura)
        figura.tight_layout()

    def grafica_racional(self, figura: Figure, horas: float = 168.0) -> None:
        """Volumen del modelo racional y su asíntota V(∞)."""
        figura.clear()
        eje = figura.add_subplot(111)
        t_h = np.linspace(0, horas, 500)
        t_s = t_h * 3600.0
        v_L = np.array([self.racional.volumen_litros(t) for t in t_s])
        limite = self.racional.volumen_infinito_litros()
        eje.plot(
            t_h, v_L, color=COLORES["racional"], linewidth=2.4, label="V(T) racional"
        )
        eje.axhline(
            limite,
            color=COLORES["acento"],
            linestyle="--",
            linewidth=1.6,
            label=f"V(∞) = {limite:.3f} L",
        )
        eje.set_title("Desperdicio acumulado – Modelo racional decreciente")
        eje.set_xlabel("Tiempo (horas)")
        eje.set_ylabel("Volumen acumulado (L)")
        eje.legend()
        aplicar_estilo(figura)
        figura.tight_layout()

    def grafica_tasa_racional(self, figura: Figure, horas: float = 48.0) -> None:
        """Evolución de q(t) para el modelo racional."""
        figura.clear()
        eje = figura.add_subplot(111)
        t_h = np.linspace(0, horas, 400)
        t_s = t_h * 3600.0
        q = np.array([self.racional.tasa(t) for t in t_s])
        eje.plot(t_h, q, color=COLORES["racional"], linewidth=2.2, label="q(t)")
        eje.set_title("Tasa de pérdida decreciente q(t)")
        eje.set_xlabel("Tiempo (horas)")
        eje.set_ylabel("Tasa (ml/s)")
        eje.legend()
        aplicar_estilo(figura)
        figura.tight_layout()

    def grafica_comparacion(self, figura: Figure, horas: float = 168.0) -> None:
        """Gráfica 4: constante vs racional."""
        figura.clear()
        eje = figura.add_subplot(111)
        t_h = np.linspace(0, horas, 500)
        t_s = t_h * 3600.0
        v_c = np.array([self.constante.volumen_litros(t) for t in t_s])
        v_r = np.array([self.racional.volumen_litros(t) for t in t_s])
        limite = self.racional.volumen_infinito_litros()
        eje.plot(t_h, v_c, color=COLORES["constante"], linewidth=2.3, label="Tasa constante")
        eje.plot(t_h, v_r, color=COLORES["racional"], linewidth=2.3, label="Tasa racional")
        eje.axhline(
            limite,
            color=COLORES["acento"],
            linestyle="--",
            linewidth=1.4,
            label=f"Límite racional = {limite:.3f} L",
        )
        eje.set_title("Comparación de volumen acumulado entre modelos")
        eje.set_xlabel("Tiempo (horas)")
        eje.set_ylabel("Volumen acumulado (L)")
        eje.legend()
        aplicar_estilo(figura)
        figura.tight_layout()

    def grafica_goteo_24h(self, figura: Figure) -> None:
        """Gráfica 1: fuga de una gota por segundo durante 24 horas (constante)."""
        modelo = ModeloConstante(1.0 * VOLUMEN_GOTA_ML)
        figura.clear()
        eje = figura.add_subplot(111)
        t_h = np.linspace(0, 24, 300)
        v_L = np.array([modelo.volumen_litros(t * 3600.0) for t in t_h])
        eje.plot(
            t_h,
            v_L,
            color=COLORES["constante"],
            linewidth=2.4,
            label="1 gota/s · 0,25 ml",
        )
        eje.set_title("Desperdicio acumulado para una fuga de una gota por segundo")
        eje.set_xlabel("Tiempo (horas)")
        eje.set_ylabel("Volumen acumulado (L)")
        eje.legend()
        aplicar_estilo(figura)
        figura.tight_layout()

    def grafica_frecuencias(self, figura: Figure, horas: float = 24.0) -> None:
        """Gráfica 2: comparación según frecuencia de goteo (modelo constante)."""
        figura.clear()
        eje = figura.add_subplot(111)
        t_h = np.linspace(0, horas, 300)
        frecuencias = (1, 2, 3, 5)
        colores = (
            COLORES["gota1"],
            COLORES["gota2"],
            COLORES["gota3"],
            COLORES["gota5"],
        )
        for r, color in zip(frecuencias, colores):
            modelo = ModeloConstante(r * VOLUMEN_GOTA_ML)
            v_L = np.array([modelo.volumen_litros(t * 3600.0) for t in t_h])
            eje.plot(t_h, v_L, color=color, linewidth=2.1, label=f"{r} gota(s)/s")
        eje.set_title("Comparación según la frecuencia de goteo")
        eje.set_xlabel("Tiempo (horas)")
        eje.set_ylabel("Volumen acumulado (L)")
        eje.legend()
        aplicar_estilo(figura)
        figura.tight_layout()

    def grafica_integrales_parciales(self, figura: Figure) -> None:
        """Gráfica 3: crecimiento de la integral parcial del modelo constante."""
        figura.clear()
        eje = figura.add_subplot(111)
        limites_h = np.array([1, 6, 12, 24, 48, 72, 168], dtype=float)
        volumenes = [self.constante.volumen_litros(h * 3600.0) for h in limites_h]
        eje.plot(
            limites_h,
            volumenes,
            marker="o",
            color=COLORES["constante"],
            linewidth=2.2,
            markersize=7,
            label="V(T) = ∫₀ᵀ A dt",
        )
        eje.set_title("Integral parcial del modelo constante al aumentar T")
        eje.set_xlabel("Límite superior T (horas)")
        eje.set_ylabel("Integral parcial (L)")
        eje.legend()
        aplicar_estilo(figura)
        figura.tight_layout()

    def grafica_analisis_impropia(self, figura: Figure, horas: float = 240.0) -> None:
        """Dos paneles: divergencia constante y convergencia racional."""
        figura.clear()
        t_h = np.linspace(0, horas, 500)
        t_s = t_h * 3600.0
        v_c = np.array([self.constante.volumen_litros(t) for t in t_s])
        v_r = np.array([self.racional.volumen_litros(t) for t in t_s])
        limite = self.racional.volumen_infinito_litros()

        eje1 = figura.add_subplot(1, 2, 1)
        eje1.plot(t_h, v_c, color=COLORES["constante"], linewidth=2.3)
        eje1.set_title("Modelo constante (divergente)")
        eje1.set_xlabel("Tiempo (horas)")
        eje1.set_ylabel("V(T) (L)")

        eje2 = figura.add_subplot(1, 2, 2)
        eje2.plot(t_h, v_r, color=COLORES["racional"], linewidth=2.3)
        eje2.axhline(limite, color=COLORES["acento"], linestyle="--", label=f"V(∞)={limite:.3f} L")
        eje2.set_title("Modelo racional (convergente)")
        eje2.set_xlabel("Tiempo (horas)")
        eje2.set_ylabel("V(T) (L)")
        eje2.legend()
        aplicar_estilo(figura)
        figura.tight_layout()

    def guardar_png(self, figura: Figure, ruta: str, dpi: int = 160) -> None:
        figura.savefig(ruta, dpi=dpi, bbox_inches="tight", facecolor=figura.get_facecolor())
