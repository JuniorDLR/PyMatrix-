"""Casos de la rúbrica del Programa 7 y rutas de error."""

from fractions import Fraction

import numpy as np
import pytest

from src.core.numericos.bases import convertir_posicional
from src.core.numericos.biseccion import biseccion_programa7, contraste_scipy
from src.core.numericos.errores import calcular_errores, calcular_propagacion, representar_float
from src.core.numericos.expresiones import compilar_funcion
from src.core.numericos.graficador import muestrear


@pytest.mark.parametrize("expresion,a,b,referencia", [
    ("x**3 - 2*x - 5", "2", "3", 2.09455148),
    ("cos(x) - x", "0", "1", 0.73908513),
    ("x**2 - 2", "1", "2", 1.41421356),
    ("x**3 + x - 1", "0", "1", 0.68232780),
])
def test_biseccion_casos_oficiales(expresion: str, a: str, b: str, referencia: float) -> None:
    resultado = biseccion_programa7(expresion, a, b, "0.0001", 100)
    assert resultado.teoricas == 14
    assert len(resultado.pasos) == 14
    assert resultado.motivo == "tolerancia"
    assert resultado.pasos[0].error_absoluto is None
    assert resultado.pasos[0].error_relativo is None
    assert resultado.pasos[0].eb == Fraction(1, 2)
    assert resultado.pasos[-1].eb <= resultado.tolerancia
    assert abs(float(resultado.raiz) - referencia) <= 0.0001


def test_biseccion_extremo_limite_y_contraste_externo() -> None:
    extremo = biseccion_programa7("x**2 - 1", "1", "2", "0.0001", 100)
    assert extremo.motivo == "extremo" and extremo.raiz == 1 and not extremo.pasos
    incompleto = biseccion_programa7("x**2 - 2", "1", "2", "0.0001", 2)
    assert incompleto.motivo == "máximo"
    assert not incompleto.cumplio_tolerancia
    raiz_scipy, diferencia = contraste_scipy(incompleto)
    assert abs(raiz_scipy - 2 ** 0.5) < 1e-10
    assert diferencia > 0
    diminuta = biseccion_programa7("(x-0.5)*1e-300", "0", "1", "0.0001", 100)
    assert diminuta.raiz == Fraction(1, 2)
    assert diminuta.motivo == "raíz exacta"
    racional = biseccion_programa7("(x-0.5)/(x+2)", "0", "1", "0.0001", 100)
    with pytest.raises(ValueError, match="continuidad"):
        contraste_scipy(racional)


@pytest.mark.parametrize("expresion,a,b", [
    ("x**2 + 1", "-1", "1"),
    ("1/x", "-1", "1"),
    ("1/(x-0.3)", "-1", "1"),
    ("tan(x)", "1", "2"),
])
def test_biseccion_rechaza_intervalos_no_validos(expresion: str, a: str, b: str) -> None:
    with pytest.raises(ValueError):
        biseccion_programa7(expresion, a, b, "0.0001", 100)


@pytest.mark.parametrize("expresion", [
    "__import__('os').system('echo no')", "x.__class__", "x[0]",
    "open('archivo')", "[x for x in (1, 2)]", "x^2",
])
def test_evaluador_bloquea_expresiones_no_autorizadas(expresion: str) -> None:
    with pytest.raises(ValueError):
        compilar_funcion(expresion)


def test_graficador_separa_dominio_y_asintotas() -> None:
    racional = muestrear("1/(x-0.3)", "-1", "1")
    assert racional.puntos_validos >= 1000
    assert len(racional.segmentos) == 2
    assert racional.segmentos[0][-1][0] < 0.3 < racional.segmentos[1][0][0]
    logaritmo = muestrear("log(x)", "-1", "2")
    assert logaritmo.puntos_excluidos > 0
    assert all(x > 0 for segmento in logaritmo.segmentos for x, _ in segmento)
    raiz = muestrear("sqrt(x)", "-1", "2")
    assert all(x >= 0 for segmento in raiz.segmentos for x, _ in segmento)


def test_bases_ejemplos_signo_y_errores() -> None:
    decimal = convertir_posicional("84506", 10)
    binario = convertir_posicional("11110011", 2)
    negativo = convertir_posicional("-11110011", 2)
    assert decimal.valor == 84506
    assert sum(t.aporte for t in decimal.terminos_decimales) == decimal.valor
    assert binario.valor == 243 and binario.decimal == "243"
    assert sum(t.aporte for t in binario.terminos_binarios) == 243
    assert negativo.valor == -243 and negativo.decimal == "-243"
    with pytest.raises(ValueError):
        convertir_posicional("10201", 2)


def test_errores_exacto_cero_y_propagacion() -> None:
    calculo = calcular_errores("1", "9/10")
    assert calculo.absoluto == Fraction(1, 10)
    assert calculo.relativo == Fraction(1, 10)
    assert calculo.porcentual == 10
    cero = calcular_errores("0", "1/10")
    assert cero.relativo is None and cero.porcentual is None
    propagacion = calcular_propagacion("1", "0.01")
    assert propagacion.diferencia < 0.0001
    flotantes = representar_float()
    assert not flotantes.comparacion
    assert flotantes.epsilon == float(np.finfo(float).eps)
