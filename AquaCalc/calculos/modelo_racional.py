"""Modelo de tasa racional decreciente q(t) = A / [(1 + at)(1 + bt)]."""

from __future__ import annotations

import math
from dataclasses import dataclass

from calculos.constantes import ML_POR_LITRO
from calculos.validaciones import validar_no_negativo, validar_positivo


@dataclass
class FraccionesParciales:
    """Constantes de la descomposición A / [(1+at)(1+bt)] = P/(1+at) + Q/(1+bt)."""

    P: float
    Q: float
    a: float
    b: float
    A: float
    caso: str


@dataclass
class ResultadoImpropiaRacional:
    """Resultado analítico de la integral impropia del modelo racional."""

    converge: bool
    volumen_infinito_ml: float
    volumen_infinito_L: float
    expresion: str
    mensaje: str


class ModeloRacional:
    """Tasa de pérdida que disminuye con el tiempo."""

    def __init__(self, A: float, a: float, b: float):
        self.A = validar_no_negativo(A, "tasa A")
        self.a = validar_positivo(a, "constante a")
        self.b = validar_positivo(b, "constante b")

    @classmethod
    def desde_goteo(cls, r: float, v: float, a: float, b: float) -> "ModeloRacional":
        r = validar_no_negativo(r, "frecuencia de goteo")
        v = validar_no_negativo(v, "volumen de cada gota")
        return cls(r * v, a, b)

    @property
    def factores_iguales(self) -> bool:
        return math.isclose(self.a, self.b, rel_tol=0.0, abs_tol=1e-18)

    def tasa(self, t: float) -> float:
        """q(t) = A / [(1 + at)(1 + bt)]  (ml/s)."""
        t = validar_no_negativo(t, "tiempo")
        return self.A / ((1.0 + self.a * t) * (1.0 + self.b * t))

    def fracciones_parciales(self) -> FraccionesParciales:
        """
        Calcula P y Q cuando a ≠ b.

        P = A a / (a − b)
        Q = −A b / (a − b)
        """
        if self.factores_iguales:
            # Caso a = b: q(t) = A / (1 + at)^2, no hay dos polos distintos.
            return FraccionesParciales(
                P=self.A,
                Q=0.0,
                a=self.a,
                b=self.b,
                A=self.A,
                caso="iguales",
            )
        denominador = self.a - self.b
        P = (self.A * self.a) / denominador
        Q = (-self.A * self.b) / denominador
        return FraccionesParciales(
            P=P, Q=Q, a=self.a, b=self.b, A=self.A, caso="distintos"
        )

    def volumen_ml(self, T: float) -> float:
        """
        V(T) = ∫₀ᵀ q(t) dt  (ml).

        Si a ≠ b:  V(T) = [A / (a − b)] × ln[(1 + aT) / (1 + bT)]
        Si a = b:  V(T) = A T / (1 + a T)
        """
        T = validar_no_negativo(T, "tiempo")
        if self.A == 0 or T == 0:
            return 0.0
        if self.factores_iguales:
            return (self.A * T) / (1.0 + self.a * T)
        return (self.A / (self.a - self.b)) * math.log(
            (1.0 + self.a * T) / (1.0 + self.b * T)
        )

    def volumen_litros(self, T: float) -> float:
        return self.volumen_ml(T) / ML_POR_LITRO

    def volumen_infinito_ml(self) -> float:
        """
        Límite analítico lim(T→∞) V(T), sin sustituir infinito numéricamente.

        Si a ≠ b:  V(∞) = [A / (a − b)] × ln(a / b)
        Si a = b:  V(∞) = A / a
        """
        if self.A == 0:
            return 0.0
        if self.factores_iguales:
            return self.A / self.a
        return (self.A / (self.a - self.b)) * math.log(self.a / self.b)

    def volumen_infinito_litros(self) -> float:
        return self.volumen_infinito_ml() / ML_POR_LITRO

    def integral_impropia(self) -> ResultadoImpropiaRacional:
        volumen = self.volumen_infinito_ml()
        if self.factores_iguales:
            expresion = "A / a"
        else:
            expresion = "[A / (a − b)] × ln(a / b)"
        return ResultadoImpropiaRacional(
            converge=True,
            volumen_infinito_ml=volumen,
            volumen_infinito_L=volumen / ML_POR_LITRO,
            expresion=expresion,
            mensaje=(
                "El modelo racional decreciente presenta una integral impropia "
                "convergente. Esto significa que el volumen acumulado se aproxima "
                "a un valor máximo finito, debido a que la tasa de pérdida "
                "disminuye con el tiempo."
            ),
        )

    def verificar_descomposicion(self, t: float = 1.0) -> float:
        """
        Error relativo entre q(t) y P/(1+at)+Q/(1+bt).
        Si a = b se compara con A/(1+at)^2.
        """
        t = validar_no_negativo(t, "tiempo")
        q = self.tasa(t)
        fp = self.fracciones_parciales()
        if fp.caso == "iguales":
            reconstruida = self.A / (1.0 + self.a * t) ** 2
        else:
            reconstruida = fp.P / (1.0 + self.a * t) + fp.Q / (1.0 + self.b * t)
        if q == 0:
            return 0.0 if reconstruida == 0 else float("inf")
        return abs(q - reconstruida) / abs(q)
