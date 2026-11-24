"""Validación de entradas numéricas y parámetros de los modelos."""

from __future__ import annotations

from typing import Optional


class ValidacionError(ValueError):
    """Error de validación con mensaje comprensible en español."""


def _a_flotante(valor, nombre: str) -> float:
    """Convierte un valor a float o lanza ValidacionError."""
    if valor is None:
        raise ValidacionError(f"El campo «{nombre}» no puede estar vacío.")
    if isinstance(valor, str):
        texto = valor.strip().replace(",", ".")
        if texto == "":
            raise ValidacionError(f"El campo «{nombre}» no puede estar vacío.")
        try:
            return float(texto)
        except ValueError as exc:
            raise ValidacionError(
                f"El valor de «{nombre}» no es un número válido."
            ) from exc
    try:
        return float(valor)
    except (TypeError, ValueError) as exc:
        raise ValidacionError(
            f"El valor de «{nombre}» no es un número válido."
        ) from exc


def validar_no_negativo(valor, nombre: str) -> float:
    """Exige un número finito mayor o igual que cero."""
    numero = _a_flotante(valor, nombre)
    if not _es_finito(numero):
        raise ValidacionError(
            f"El valor de «{nombre}» es demasiado grande o no es finito."
        )
    if numero < 0:
        raise ValidacionError(f"El campo «{nombre}» no admite valores negativos.")
    return numero


def validar_positivo(valor, nombre: str) -> float:
    """Exige un número finito estrictamente mayor que cero."""
    numero = validar_no_negativo(valor, nombre)
    if numero == 0:
        raise ValidacionError(f"El campo «{nombre}» debe ser mayor que cero.")
    return numero


def validar_parametros_atenuacion(a, b, exigir_distintos: bool = True) -> tuple[float, float]:
    """Valida las constantes de atenuación a y b."""
    a_num = validar_positivo(a, "constante a")
    b_num = validar_positivo(b, "constante b")
    if exigir_distintos and abs(a_num - b_num) < 1e-18:
        raise ValidacionError(
            "Las constantes a y b deben ser distintas. "
            "Si a = b no se puede aplicar la descomposición en fracciones "
            "parciales para factores diferentes."
        )
    return a_num, b_num


def validar_parametros(
    frecuencia,
    volumen_gota,
    a: Optional[object] = None,
    b: Optional[object] = None,
    tiempo: Optional[object] = None,
    exigir_a_distinto_b: bool = False,
) -> dict:
    """Valida el conjunto de parámetros habituales de la aplicación."""
    r = validar_no_negativo(frecuencia, "frecuencia de goteo")
    v = validar_no_negativo(volumen_gota, "volumen de cada gota")
    resultado = {"r": r, "v": v, "A": r * v}

    if a is not None and b is not None:
        a_num, b_num = validar_parametros_atenuacion(
            a, b, exigir_distintos=exigir_a_distinto_b
        )
        resultado["a"] = a_num
        resultado["b"] = b_num

    if tiempo is not None:
        resultado["T"] = validar_no_negativo(tiempo, "tiempo")

    return resultado


def _es_finito(numero: float) -> bool:
    return numero == numero and numero not in (float("inf"), float("-inf"))
