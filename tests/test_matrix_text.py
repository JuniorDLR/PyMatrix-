"""Pruebas del lector de matrices pegadas en las vistas gráficas."""

from fractions import Fraction

import pytest

from src.ui.matrix_text import leer_matriz_texto, leer_vector_texto


@pytest.mark.parametrize("texto", [
    "1/2\t-2\n3\t4.5",
    "1/2, -2; 3, 4.5",
    "[[1/2, -2], [3, 4.5]]",
])
def test_lector_admite_pegado_y_fracciones(texto):
    assert leer_matriz_texto(texto) == [[Fraction(1, 2), -2], [3, Fraction(9, 2)]]


def test_lector_rechaza_matriz_irregular_y_valor_invalido():
    with pytest.raises(ValueError, match="irregular"):
        leer_matriz_texto("1 2\n3")
    with pytest.raises(ValueError):
        leer_matriz_texto("1 2\n3 palabra")
    with pytest.raises(ValueError, match="celda vacía"):
        leer_matriz_texto("1,,2\n3,4")
    with pytest.raises(ValueError, match="incompletos"):
        leer_matriz_texto("[[1,2], [3,4]")


def test_vector_acepta_fila_o_columna_y_valida_longitud():
    assert leer_vector_texto("1/2 3", 2) == [Fraction(1, 2), 3]
    assert leer_vector_texto("1/2\n3", 2) == [Fraction(1, 2), 3]
    with pytest.raises(ValueError, match="2 componentes"):
        leer_vector_texto("1 2 3", 2)
