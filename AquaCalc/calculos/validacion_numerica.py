"""Validación cruzada: fórmulas analíticas frente a integración numérica."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from scipy.integrate import quad

from calculos.constantes import TOLERANCIA_RELATIVA, VOLUMEN_GOTA_ML
from calculos.modelo_constante import ModeloConstante
from calculos.modelo_racional import ModeloRacional


@dataclass
class ComparacionNumerica:
    """Comparación entre un valor analítico y uno numérico."""

    nombre: str
    analitico: float
    numerico: Optional[float]
    error_relativo: Optional[float]
    coincide: bool
    detalle: str


@dataclass
class InformeValidacion:
    """Conjunto de comprobaciones matemáticas del estado actual."""

    comparaciones: list[ComparacionNumerica] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)

    @property
    def todo_correcto(self) -> bool:
        return all(c.coincide for c in self.comparaciones) and not self.advertencias


def _error_relativo(analitico: float, numerico: float) -> float:
    if analitico == 0 and numerico == 0:
        return 0.0
    denom = max(abs(analitico), abs(numerico), 1e-15)
    return abs(analitico - numerico) / denom


def _integrar(funcion: Callable[[float], float], t0: float, t1: float) -> tuple[float, float]:
    valor, error_est = quad(funcion, t0, t1, epsabs=1e-10, limit=200)
    return valor, error_est


def validar_modelos(
    constante: ModeloConstante,
    racional: ModeloRacional,
    T: float = 3600.0,
) -> InformeValidacion:
    """Compara fórmulas analíticas con scipy.integrate.quad en [0, T]."""
    informe = InformeValidacion()

    # 1) Modelo constante: ∫ A dt = A T
    anal_c = constante.volumen_ml(T)
    num_c, _ = _integrar(lambda t: constante.tasa(t), 0.0, T)
    err_c = _error_relativo(anal_c, num_c)
    ok_c = err_c < TOLERANCIA_RELATIVA * 100 or err_c < 1e-8
    informe.comparaciones.append(
        ComparacionNumerica(
            nombre=f"Modelo constante V({T:.0f} s)",
            analitico=anal_c,
            numerico=num_c,
            error_relativo=err_c,
            coincide=ok_c,
            detalle="∫₀ᵀ A dt frente a A × T",
        )
    )
    if not ok_c:
        informe.advertencias.append(
            "La integración numérica del modelo constante no coincide con A × T."
        )

    # 2) Descomposición en fracciones parciales
    err_fp = racional.verificar_descomposicion(t=T if T > 0 else 1.0)
    ok_fp = err_fp < 1e-9
    fp = racional.fracciones_parciales()
    informe.comparaciones.append(
        ComparacionNumerica(
            nombre="Descomposición en fracciones parciales",
            analitico=racional.tasa(T if T > 0 else 1.0),
            numerico=None if fp.caso == "iguales" else fp.P + fp.Q,
            error_relativo=err_fp,
            coincide=ok_fp,
            detalle=f"P = {fp.P:.8g}, Q = {fp.Q:.8g}, caso = {fp.caso}",
        )
    )
    if not ok_fp:
        informe.advertencias.append(
            "La descomposición en fracciones parciales no reproduce q(t)."
        )

    # 3) Modelo racional en intervalo finito
    anal_r = racional.volumen_ml(T)
    num_r, _ = _integrar(lambda t: racional.tasa(t), 0.0, T)
    err_r = _error_relativo(anal_r, num_r)
    ok_r = err_r < 1e-6
    informe.comparaciones.append(
        ComparacionNumerica(
            nombre=f"Modelo racional V({T:.0f} s)",
            analitico=anal_r,
            numerico=num_r,
            error_relativo=err_r,
            coincide=ok_r,
            detalle="∫ q(t) dt frente a [A/(a−b)] ln[(1+aT)/(1+bT)]",
        )
    )
    if not ok_r:
        informe.advertencias.append(
            "La integración numérica del modelo racional no coincide con la fórmula analítica."
        )

    # 4) Límite analítico (no se integra hasta infinito)
    v_inf = racional.volumen_infinito_ml()
    v_grande = racional.volumen_ml(1e12)
    err_lim = _error_relativo(v_inf, v_grande)
    ok_lim = err_lim < 1e-6
    informe.comparaciones.append(
        ComparacionNumerica(
            nombre="Límite analítico V(∞)",
            analitico=v_inf,
            numerico=v_grande,
            error_relativo=err_lim,
            coincide=ok_lim,
            detalle=racional.integral_impropia().expresion,
        )
    )

    # 5) Divergencia del modelo constante
    imp_c = constante.integral_impropia()
    if constante.A > 0 and not imp_c.diverge:
        informe.advertencias.append("El modelo constante debería divergir cuando A > 0.")
        ok_div = False
    else:
        ok_div = True
    informe.comparaciones.append(
        ComparacionNumerica(
            nombre="Divergencia del modelo constante",
            analitico=float("inf") if imp_c.diverge else 0.0,
            numerico=None,
            error_relativo=None,
            coincide=ok_div,
            detalle=imp_c.limite_descripcion,
        )
    )

    # 6) Valor de referencia del proyecto (solo si coinciden los parámetros típicos)
    if (
        abs(racional.A - VOLUMEN_GOTA_ML) < 1e-12
        and abs(racional.a - 1.0 / 3600.0) < 1e-18
        and abs(racional.b - 1.0 / 86400.0) < 1e-18
    ):
        esperado = 2984.61
        err_ref = _error_relativo(esperado, v_inf)
        ok_ref = abs(v_inf - esperado) < 0.05
        informe.comparaciones.append(
            ComparacionNumerica(
                nombre="Referencia del proyecto V(∞) ≈ 2984,61 ml",
                analitico=esperado,
                numerico=v_inf,
                error_relativo=err_ref,
                coincide=ok_ref,
                detalle="Parámetros predeterminados A=0,25; a=1/3600; b=1/86400",
            )
        )
        if not ok_ref:
            informe.advertencias.append(
                "V(∞) no coincide con el valor de referencia 2984,61 ml."
            )

    return informe
