"""Errores absolutos, representación float y propagación de primer orden."""

import math
import sys
from dataclasses import dataclass
from fractions import Fraction

from src.core.exact_math import parsear_fraccion
from src.core.numericos.expresiones import numero_real


TIPOS_ERROR = (
    ("Inherente", "Incertidumbre presente en el dato original; una medición de 2.50 m puede tener resolución de 0.01 m."),
    ("Redondeo", "Al guardar 1/3 con cifras finitas se obtiene una aproximación."),
    ("Truncamiento", "Cortar una serie numérica, por ejemplo sin(x)≈x, omite términos posteriores."),
    ("Overflow", "Un cálculo supera el máximo representable del tipo float."),
    ("Underflow", "Una magnitud no nula cae por debajo de la precisión representable y puede llegar a cero."),
    ("Modelo", "Una ecuación simplifica el fenómeno: ignorar la resistencia del aire altera la predicción."),
)


@dataclass(frozen=True)
class MedicionError:
    verdadero: Fraction
    aproximado: Fraction
    absoluto: Fraction
    relativo: Fraction | None
    porcentual: Fraction | None


@dataclass(frozen=True)
class Propagacion:
    x: float
    delta_x: float
    fx: float
    derivada: float
    delta_aproximado: float
    delta_real: float
    diferencia: float


@dataclass(frozen=True)
class RepresentacionFloat:
    suma: float
    comparacion: bool
    epsilon: float
    fuente_epsilon: str
    overflow: float
    underflow: float
    maximo: float
    minimo_normal: float


def calcular_errores(texto_verdadero: str, texto_aproximado: str) -> MedicionError:
    """Calcula errores exactos y deja indefinido el relativo si xv=0."""
    try:
        verdadero = parsear_fraccion(texto_verdadero.strip())
        aproximado = parsear_fraccion(texto_aproximado.strip())
    except (ValueError, ZeroDivisionError, OverflowError) as error:
        raise ValueError("Escribe valores verdaderos y aproximados numéricos.") from error
    absoluto = abs(verdadero - aproximado)
    relativo = absoluto / abs(verdadero) if verdadero else None
    porcentual = relativo * 100 if relativo is not None else None
    return MedicionError(verdadero, aproximado, absoluto, relativo, porcentual)


def calcular_propagacion(texto_x: str, texto_delta: str) -> Propagacion:
    """Compara el diferencial lineal con el cambio real de sin(x)+x²."""
    x = numero_real(texto_x, "x")
    delta = numero_real(texto_delta, "Δx")
    try:
        fx = math.sin(x) + x * x
        derivada = math.cos(x) + 2 * x
        aproximado = derivada * delta
        real = math.sin(x + delta) + (x + delta) ** 2 - fx
        diferencia = abs(aproximado - real)
    except (ArithmeticError, OverflowError) as error:
        raise ValueError("x o Δx producen un resultado fuera del rango float.") from error
    if not all(math.isfinite(item) for item in (fx, derivada, aproximado, real, diferencia)):
        raise ValueError("x o Δx producen un resultado fuera del rango float.")
    return Propagacion(x, delta, fx, derivada, aproximado, real, diferencia)


def representar_float() -> RepresentacionFloat:
    """Muestra fenómenos de doble precisión en la plataforma actual."""
    try:
        import numpy as np
    except ImportError:
        epsilon = sys.float_info.epsilon
        maximo = sys.float_info.max
        minimo = sys.float_info.min
        fuente = "sys.float_info.epsilon (NumPy no instalado)"
        overflow = maximo * 2
        underflow = minimo * epsilon / 4
    else:
        informacion = np.finfo(float)
        epsilon = float(informacion.eps)
        maximo = float(informacion.max)
        minimo = float(informacion.tiny)
        fuente = "numpy.finfo(float).eps"
        with np.errstate(over="ignore", under="ignore"):
            overflow = float(np.float64(maximo) * np.float64(2))
            underflow = float(np.float64(minimo) * np.float64(epsilon) / np.float64(4))
    return RepresentacionFloat(
        0.1 + 0.2, 0.1 + 0.2 == 0.3, epsilon, fuente,
        overflow, underflow, maximo, minimo,
    )
