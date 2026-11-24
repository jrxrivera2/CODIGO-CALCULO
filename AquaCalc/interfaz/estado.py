"""Estado compartido de parámetros entre todas las secciones."""

from __future__ import annotations

from typing import Callable

from calculos.constantes import (
    A_PREDETERMINADO_S,
    B_PREDETERMINADO_S,
    VOLUMEN_GOTA_ML,
)
from calculos.modelo_constante import ModeloConstante
from calculos.modelo_racional import ModeloRacional
from calculos.validacion_numerica import InformeValidacion, validar_modelos


class AppState:
    """Parámetros de la fuga y de ambos modelos matemáticos."""

    def __init__(self) -> None:
        self.r = 1.0
        self.v = VOLUMEN_GOTA_ML
        self.a = A_PREDETERMINADO_S
        self.b = B_PREDETERMINADO_S
        self.T = 86400.0
        self.unidad_tiempo = "horas"
        self.tiempo_ingresado = 24.0
        self._oyentes: list[Callable[[], None]] = []

    @property
    def A(self) -> float:
        return self.r * self.v

    def suscribir(self, oyente: Callable[[], None]) -> None:
        self._oyentes.append(oyente)

    def notificar(self) -> None:
        for oyente in self._oyentes:
            oyente()

    def actualizar(self, **kwargs) -> None:
        for clave, valor in kwargs.items():
            setattr(self, clave, valor)
        self.notificar()

    def modelo_constante(self) -> ModeloConstante:
        return ModeloConstante(self.A)

    def modelo_racional(self) -> ModeloRacional:
        return ModeloRacional(self.A, self.a, self.b)

    def validar(self, T: float | None = None) -> InformeValidacion:
        return validar_modelos(
            self.modelo_constante(),
            self.modelo_racional(),
            T if T is not None else max(self.T, 1.0),
        )
