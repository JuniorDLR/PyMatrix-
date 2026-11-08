"""Casos de la sesión 19 y precondiciones del método de bisección."""

from fractions import Fraction

import pytest

from src.core.biseccion import biseccion


def test_ejemplo_de_clase_con_13_iteraciones_y_tolerancia() -> None:
    resultado = biseccion([1, -5, "0.5", -11, 10], "0.55", "1.1", "0.0001")

    assert resultado.iteraciones_estimadas == 13
    assert len(resultado.pasos) == 13
    assert [paso.xr for paso in resultado.pasos[:3]] == [
        Fraction(33, 40), Fraction(11, 16), Fraction(121, 160),
    ]
    assert resultado.raiz == Fraction(125169, 163840)
    assert resultado.pasos[-1].ancho_final < resultado.tolerancia
    assert resultado.motivo == "ancho del intervalo menor que E"


def test_ejercicio_cinco_iteraciones_sin_declarar_convergencia() -> None:
    resultado = biseccion([1, 0, -4, -1], 2, 3, "0.0001", iteraciones=5)

    assert len(resultado.pasos) == 5
    assert resultado.motivo == "iteraciones solicitadas"
    assert resultado.pasos[-1].ancho_final >= resultado.tolerancia
    assert resultado.pasos[0].error_relativo is None


def test_extremo_y_punto_medio_exactos() -> None:
    extremo = biseccion([1, 0], 0, 1, "1/100")
    medio = biseccion([1, 0], -1, 1, "1/100")

    assert extremo.raiz == 0 and extremo.pasos == ()
    assert medio.raiz == 0 and medio.motivo == "raíz exacta"
    assert medio.pasos[0].error_relativo is None


@pytest.mark.parametrize("coeficientes,xl,xu,tolerancia,mensaje", [
    ([1, 0, 1], -1, 1, "0.01", "signos opuestos"),
    ([1, 0], 2, 1, "0.01", "menor"),
    ([1, 0], -1, 1, 0, "positiva"),
    ([1, "abc"], -1, 1, "0.01", "Coeficiente"),
    ([0, 1], -1, 1, "0.01", "grado mayor"),
])
def test_entradas_invalidas_fallan_con_mensaje(
    coeficientes: list[object], xl: object, xu: object, tolerancia: object, mensaje: str,
) -> None:
    with pytest.raises(ValueError, match=mensaje):
        biseccion(coeficientes, xl, xu, tolerancia)
