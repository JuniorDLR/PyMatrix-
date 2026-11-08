"""Bisección de polinomios con aritmética racional exacta."""

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from src.core.exact_math import parsear_fraccion


@dataclass(frozen=True)
class PasoBiseccion:
    iteracion: int
    xl: Fraction
    xu: Fraction
    xr: Fraction
    f_xl: Fraction
    f_xu: Fraction
    f_xr: Fraction
    error_relativo: Fraction | None
    nuevo_xl: Fraction
    nuevo_xu: Fraction

    @property
    def ancho_inicial(self) -> Fraction:
        return self.xu - self.xl

    @property
    def ancho_final(self) -> Fraction:
        return self.nuevo_xu - self.nuevo_xl


@dataclass(frozen=True)
class ResultadoBiseccion:
    coeficientes: tuple[Fraction, ...]
    pasos: tuple[PasoBiseccion, ...]
    raiz: Fraction
    tolerancia: Fraction
    motivo: str
    iteraciones_estimadas: int


def _fraccion(valor: Any, nombre: str) -> Fraction:
    try:
        return parsear_fraccion(valor)
    except (TypeError, ValueError, ZeroDivisionError, OverflowError) as error:
        raise ValueError(f"{nombre} debe ser un número, decimal o fracción válida.") from error


def evaluar_polinomio(coeficientes: tuple[Fraction, ...], x: Fraction) -> Fraction:
    resultado = Fraction(0)
    for coeficiente in coeficientes:
        resultado = resultado * x + coeficiente
    return resultado


def biseccion(
    datos_coeficientes: list[Any], datos_xl: Any, datos_xu: Any,
    datos_tolerancia: Any, *, iteraciones: int | None = None,
    max_iteraciones: int = 1000,
) -> ResultadoBiseccion:
    """Aplica únicamente el procedimiento de bisección de la sesión 19.

    Los coeficientes van del mayor exponente al término independiente.
    Con ``iteraciones`` se hacen exactamente esos pasos salvo raíz exacta.
    En modo automático se detiene cuando el ancho actualizado es menor que E.
    """
    if len(datos_coeficientes) < 2:
        raise ValueError("El polinomio requiere al menos grado 1 y término independiente.")
    coeficientes = tuple(
        _fraccion(valor, f"Coeficiente de x^{len(datos_coeficientes) - i - 1}")
        for i, valor in enumerate(datos_coeficientes)
    )
    if coeficientes[0] == 0:
        raise ValueError("El coeficiente del grado mayor no puede ser cero.")
    xl = _fraccion(datos_xl, "x_l")
    xu = _fraccion(datos_xu, "x_u")
    tolerancia = _fraccion(datos_tolerancia, "La tolerancia E")
    if xl >= xu:
        raise ValueError("El límite inferior x_l debe ser menor que x_u.")
    if tolerancia <= 0:
        raise ValueError("La tolerancia E debe ser positiva.")
    if type(max_iteraciones) is not int or max_iteraciones < 1 or max_iteraciones > 10000:
        raise ValueError("El máximo de iteraciones debe estar entre 1 y 10000.")
    if iteraciones is not None and (type(iteraciones) is not int or not 1 <= iteraciones <= max_iteraciones):
        raise ValueError("La cantidad de iteraciones debe estar entre 1 y el máximo permitido.")

    f_xl = evaluar_polinomio(coeficientes, xl)
    f_xu = evaluar_polinomio(coeficientes, xu)
    if f_xl == 0 or f_xu == 0:
        raiz = xl if f_xl == 0 else xu
        return ResultadoBiseccion(coeficientes, (), raiz, tolerancia, "raíz exacta en un extremo", 0)
    if f_xl * f_xu > 0:
        raise ValueError("f(x_l) y f(x_u) deben tener signos opuestos; elige otro intervalo.")

    ancho_estimado = xu - xl
    estimadas = 0
    while ancho_estimado >= tolerancia and estimadas < max_iteraciones:
        ancho_estimado /= 2
        estimadas += 1

    pasos: list[PasoBiseccion] = []
    anterior: Fraction | None = None
    limite = iteraciones if iteraciones is not None else max_iteraciones
    for i in range(1, limite + 1):
        xr = (xl + xu) / 2
        f_xr = evaluar_polinomio(coeficientes, xr)
        error = abs((xr - anterior) / xr) if anterior is not None and xr != 0 else None
        producto = f_xl * f_xr
        nuevo_xl, nuevo_xu = xl, xu
        if producto < 0:
            nuevo_xu = xr
        elif producto > 0:
            nuevo_xl = xr
        pasos.append(PasoBiseccion(i, xl, xu, xr, f_xl, f_xu, f_xr, error, nuevo_xl, nuevo_xu))
        if producto == 0:
            motivo = "raíz exacta"
            break
        if iteraciones is None and nuevo_xu - nuevo_xl < tolerancia:
            motivo = "ancho del intervalo menor que E"
            break
        anterior = xr
        xl, xu = nuevo_xl, nuevo_xu
        f_xl = evaluar_polinomio(coeficientes, xl)
        f_xu = evaluar_polinomio(coeficientes, xu)
    else:
        motivo = "iteraciones solicitadas" if iteraciones is not None else "máximo de iteraciones"
    return ResultadoBiseccion(coeficientes, tuple(pasos), pasos[-1].xr, tolerancia, motivo, estimadas)
