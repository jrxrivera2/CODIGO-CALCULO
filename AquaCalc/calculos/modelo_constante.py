"""Modelo de tasa de pérdida constante q(t) = A."""

from __future__ import annotations

from dataclasses import dataclass

from calculos.constantes import ML_POR_LITRO
from calculos.validaciones import validar_no_negativo


@dataclass
class ResultadoImpropiaConstante:
    """Resultado del análisis de la integral impropia del modelo constante."""

    diverge: bool
    limite_descripcion: str
    mensaje: str
    A: float


class ModeloConstante:
    """Calcula el desperdicio de agua con tasa constante A = r × v."""

    def __init__(self, A: float):
        self.A = validar_no_negativo(A, "tasa A")

    @classmethod
    def desde_goteo(cls, r: float, v: float) -> "ModeloConstante":
        """Construye el modelo a partir de frecuencia y volumen de gota."""
        r = validar_no_negativo(r, "frecuencia de goteo")
        v = validar_no_negativo(v, "volumen de cada gota")
        return cls(r * v)

    def tasa(self, t: float = 0.0) -> float:
        """q(t) = A (ml/s). El tiempo no altera la tasa."""
        validar_no_negativo(t, "tiempo")
        return self.A

    def volumen_ml(self, T: float) -> float:
        """V(T) = ∫₀ᵀ A dt = A × T  (ml)."""
        T = validar_no_negativo(T, "tiempo")
        return self.A * T

    def volumen_litros(self, T: float) -> float:
        """Volumen acumulado en litros."""
        return self.volumen_ml(T) / ML_POR_LITRO

    def integral_impropia(self) -> ResultadoImpropiaConstante:
        """
        Evalúa lim(T→∞) A × T de forma analítica.

        Si A > 0 el límite es +∞ y la integral diverge.
        Si A = 0 el límite es 0 y la integral converge trivialmente.
        """
        if self.A > 0:
            return ResultadoImpropiaConstante(
                diverge=True,
                limite_descripcion="∞",
                mensaje=(
                    "El modelo de tasa constante presenta una integral impropia "
                    "divergente. Esto significa que, si la fuga mantiene una tasa "
                    "positiva constante durante un tiempo indefinido, el volumen "
                    "acumulado continuará aumentando sin alcanzar un valor máximo."
                ),
                A=self.A,
            )
        return ResultadoImpropiaConstante(
            diverge=False,
            limite_descripcion="0",
            mensaje=(
                "La tasa A es nula, por lo que no hay fuga. El volumen acumulado "
                "permanece en cero para cualquier intervalo de tiempo, incluida "
                "la integral impropia."
            ),
            A=self.A,
        )

    def volumenes_vector(self, tiempos):
        """Evalúa V(T) para una secuencia de tiempos (ml)."""
        return [self.volumen_ml(t) for t in tiempos]
