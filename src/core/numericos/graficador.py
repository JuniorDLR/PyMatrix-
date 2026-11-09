"""Muestreo de funciones para la gráfica, sin unir discontinuidades."""

from dataclasses import dataclass
import math

from src.core.numericos.expresiones import FuncionReal, compilar_funcion, numero_real


@dataclass(frozen=True)
class Grafica:
    funcion: FuncionReal
    x_min: float
    x_max: float
    segmentos: tuple[tuple[tuple[float, float], ...], ...]
    puntos_validos: int
    puntos_excluidos: int


def muestrear(
    expresion: str, texto_min: str, texto_max: str, muestras: int = 1201,
) -> Grafica:
    """Evalúa al menos mil puntos y corta cada salto de dominio observable."""
    funcion = compilar_funcion(expresion)
    x_min = numero_real(texto_min, "x_min")
    x_max = numero_real(texto_max, "x_max")
    if x_min >= x_max:
        raise ValueError("x_min debe ser menor que x_max.")
    if not math.isfinite(x_max - x_min):
        raise ValueError("El intervalo es demasiado amplio para graficarlo con float.")
    if not 1000 <= muestras <= 10000:
        raise ValueError("La cantidad de muestras debe estar entre 1000 y 10000.")

    segmentos: list[tuple[tuple[float, float], ...]] = []
    actual: list[tuple[float, float]] = []
    excluidos = 0
    anterior: float | None = None
    for indice in range(muestras):
        x = x_min + (x_max - x_min) * indice / (muestras - 1)
        try:
            y = funcion.evaluar(x)
        except ValueError:
            excluidos += 1
            if actual:
                segmentos.append(tuple(actual))
                actual = []
            anterior = None
            continue
        if anterior is not None and funcion.barrera_entre(anterior, x):
            if actual:
                segmentos.append(tuple(actual))
            actual = []
        actual.append((x, y))
        anterior = x
    if actual:
        segmentos.append(tuple(actual))
    validos = sum(len(segmento) for segmento in segmentos)
    if not validos:
        raise ValueError("La función no tiene puntos reales y finitos en este intervalo.")
    return Grafica(funcion, x_min, x_max, tuple(segmentos), validos, excluidos)
