"""Bisección de la guía oficial del Programa 7."""

from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Literal

from src.core.exact_math import parsear_fraccion
from src.core.numericos.expresiones import FuncionReal, compilar_funcion


Motivo = Literal["extremo", "raíz exacta", "tolerancia", "máximo", "precisión"]


@dataclass(frozen=True)
class Paso:
    k: int
    a: Fraction
    b: Fraction
    xr: Fraction
    fa: float
    fb: float
    fr: float
    eb: Fraction
    error_absoluto: Fraction | None
    error_relativo: Fraction | None
    nuevo_a: Fraction
    nuevo_b: Fraction


@dataclass(frozen=True)
class Resultado:
    funcion: FuncionReal
    inicial_a: Fraction
    inicial_b: Fraction
    final_a: Fraction
    final_b: Fraction
    tolerancia: Fraction
    max_iteraciones: int
    teoricas: int
    pasos: tuple[Paso, ...]
    raiz: Fraction
    motivo: Motivo

    @property
    def cumplio_tolerancia(self) -> bool:
        return self.motivo in ("extremo", "raíz exacta", "tolerancia")


def _fraccion(texto: str, nombre: str) -> Fraction:
    try:
        valor = parsear_fraccion(texto)
        float(valor)
    except (TypeError, ValueError, ZeroDivisionError, OverflowError) as error:
        raise ValueError(f"{nombre} debe ser un número finito o fracción válida.") from error
    return valor


def _teoricas(ancho: Fraction, tolerancia: Fraction) -> int:
    """Calcula ceil(log2(ancho/E)) mediante divisiones exactas."""
    pasos = 0
    while ancho > tolerancia:
        ancho /= 2
        pasos += 1
        if pasos > 10000:
            raise ValueError("La tolerancia exige más de 10000 iteraciones.")
    return pasos


def biseccion_programa7(
    expresion: str, texto_a: str, texto_b: str, texto_tolerancia: str,
    max_iteraciones: int,
) -> Resultado:
    """Registra el semiancho previo y detiene por Eb≤E, raíz o límite."""
    funcion = compilar_funcion(expresion)
    a = _fraccion(texto_a, "El límite inferior")
    b = _fraccion(texto_b, "El límite superior")
    tolerancia = _fraccion(texto_tolerancia, "La tolerancia E")
    if a >= b:
        raise ValueError("El límite inferior debe ser menor que el superior.")
    if not math.isfinite(float(b) - float(a)):
        raise ValueError("El intervalo es demasiado amplio para evaluarlo con float.")
    if tolerancia <= 0:
        raise ValueError("La tolerancia E debe ser positiva.")
    if type(max_iteraciones) is not int or not 1 <= max_iteraciones <= 1000:
        raise ValueError("El máximo de iteraciones debe estar entre 1 y 1000.")
    teoricas = _teoricas(b - a, tolerancia)
    fa, fb = funcion.evaluar(float(a)), funcion.evaluar(float(b))
    if fa == 0 or fb == 0:
        raiz = a if fa == 0 else b
        return Resultado(funcion, a, b, a, b, tolerancia, max_iteraciones,
                         teoricas, (), raiz, "extremo")
    funcion.verificar_intervalo(float(a), float(b))
    if (fa < 0) == (fb < 0):
        raise ValueError("No hay cambio de signo en los extremos; prueba otro intervalo.")

    inicial_a, inicial_b = a, b
    pasos: list[Paso] = []
    anterior: Fraction | None = None
    for k in range(1, max_iteraciones + 1):
        xr = (a + b) / 2
        eb = (b - a) / 2
        fr = funcion.evaluar(float(xr))
        error_absoluto = abs(xr - anterior) if anterior is not None else None
        error_relativo = (
            error_absoluto / abs(xr) if error_absoluto is not None and xr != 0
            else None
        )
        motivo: Motivo | None = None
        if fr == 0:
            motivo = "raíz exacta"
        elif eb <= tolerancia:
            motivo = "tolerancia"
        elif float(xr) in (float(a), float(b)):
            motivo = "precisión"
        nuevo_a, nuevo_b = a, b
        if motivo is None and (fa < 0) != (fr < 0):
            nuevo_b = xr
        elif motivo is None:
            nuevo_a = xr
        pasos.append(Paso(k, a, b, xr, fa, fb, fr, eb,
                          error_absoluto, error_relativo, nuevo_a, nuevo_b))
        if motivo:
            break
        anterior = xr
        a, b = nuevo_a, nuevo_b
        fa, fb = funcion.evaluar(float(a)), funcion.evaluar(float(b))
    else:
        motivo = "máximo"
    ultimo = pasos[-1]
    assert motivo is not None
    return Resultado(funcion, inicial_a, inicial_b, ultimo.nuevo_a, ultimo.nuevo_b,
                     tolerancia, max_iteraciones, teoricas, tuple(pasos), ultimo.xr, motivo)


def contraste_scipy(resultado: Resultado) -> tuple[float, float]:
    """Usa SciPy exclusivamente como contraste de un intervalo validado."""
    if not resultado.funcion.continuidad_global:
        raise ValueError("Comparación omitida: no se certificó continuidad para SciPy.")
    from scipy.optimize import bisect

    raiz = bisect(
        resultado.funcion.evaluar,
        float(resultado.inicial_a), float(resultado.inicial_b),
        xtol=2e-12, maxiter=1000,
    )
    return raiz, abs(raiz - float(resultado.raiz))
