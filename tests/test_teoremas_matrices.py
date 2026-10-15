"""Pruebas de cobertura de propiedades matriciales de la Tarea 6."""

from fractions import Fraction

import pytest

from src.core.teoremas_matrices import TEOREMAS, verificar_teorema


@pytest.mark.parametrize("clave", [teorema.clave for teorema in TEOREMAS])
def test_todos_los_teoremas_calculan_ambos_miembros(clave):
    A = [[2, 1], [1, 1]]
    B = [[1, 1], [0, 1]]
    C = [[3, 0], [1, 2]]
    if clave == "det_triangular":
        A = [[2, 1], [0, 3]]

    resultado = verificar_teorema(clave, A, B, C, "3/2")

    assert resultado.izquierdo is not None
    assert resultado.derecho is not None
    assert resultado.se_cumple


def test_propiedades_rectangulares_admiten_dimensiones_compatibles():
    A = [[1, 2, 3], [4, 5, 6]]
    B = [[1, 0], [0, 1], [1, 1]]
    C = [[2, 1], [1, 2]]

    assert verificar_teorema("traspuesta_producto", A, B).se_cumple
    assert verificar_teorema("asociativa", A, B, C).se_cumple
    assert verificar_teorema("doble_traspuesta", A).se_cumple


def test_operacion_de_fila_usa_escalar_suministrado():
    resultado = verificar_teorema("det_reemplazo", [[1, 2], [3, 4]], escalar="-7/3")

    assert resultado.intermedios[0][1] == [[-6, Fraction(-22, 3)], [3, 4]]
    assert resultado.izquierdo == resultado.derecho == Fraction(-2)


def test_precondiciones_rechazan_propiedades_no_definidas():
    with pytest.raises(ValueError, match="requiere B"):
        verificar_teorema("traspuesta_suma", [[1]])
    with pytest.raises(ValueError, match="singular"):
        verificar_teorema("identidad_inversa", [[1, 2], [2, 4]])
    with pytest.raises(ValueError, match="triangular"):
        verificar_teorema("det_triangular", [[1, 2], [3, 4]])
    with pytest.raises(ValueError, match="distinto de cero"):
        verificar_teorema("det_fila_escalar", [[1, 2], [3, 4]], escalar=0)
