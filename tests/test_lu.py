"""Pruebas de factorización LU y doble sustitución de la sesión 12."""

from fractions import Fraction

import pytest

from src.core.lu import factorizar_lu, resolver_sistema_lu


def test_factorizacion_y_sistema_ejemplo_sesion_12():
    matriz_a = [[3, -7, -2], [-3, 5, 1], [6, -4, 0]]
    datos_originales = [fila[:] for fila in matriz_a]

    factores = factorizar_lu(matriz_a)
    solucion = resolver_sistema_lu(factores, [-7, 5, 2])

    assert matriz_a == datos_originales
    assert factores.matriz_l == [[1, 0, 0], [-1, 1, 0], [2, -5, 1]]
    assert factores.matriz_u == [[3, -7, -2], [0, -2, -1], [0, 0, -1]]
    assert factores.es_correcta
    assert solucion.vector_y == [-7, -2, 6]
    assert solucion.vector_x == [3, 4, -6]
    assert solucion.es_correcta
    assert solucion.pasos_adelante[-1].matriz_aumentada == [
        [1, 0, 0, -7], [0, 1, 0, -2], [0, 0, 1, 6],
    ]
    assert solucion.pasos_atras[-1].matriz_aumentada == [
        [1, 0, 0, 3], [0, 1, 0, 4], [0, 0, 1, -6],
    ]


def test_factorizacion_rectangular_con_columna_sin_pivote():
    matriz_a = [
        [2, 4, -1, 5, -2],
        [-4, -5, 3, -8, 1],
        [2, -5, -4, 1, 8],
        [-6, 0, 7, -3, 1],
    ]

    factores = factorizar_lu(matriz_a)

    assert factores.matriz_l == [
        [1, 0, 0, 0], [-2, 1, 0, 0], [1, -3, 1, 0], [-3, 4, 2, 1],
    ]
    assert factores.matriz_u == [
        [2, 4, -1, 5, -2], [0, 3, 1, 2, -3],
        [0, 0, 0, 2, 1], [0, 0, 0, 0, 5],
    ]
    assert factores.producto_lu == factores.matriz_a
    assert factores.es_correcta


def test_sistema_cuatro_por_cuatro_de_la_sesion_12():
    matriz_a = [
        [3, -7, -2, 2], [-3, 5, 1, 0],
        [6, -4, 0, -5], [-9, 5, -5, 12],
    ]

    solucion = resolver_sistema_lu(factorizar_lu(matriz_a), [-9, 5, 7, 11])

    assert solucion.vector_y == [-9, -4, 5, 1]
    assert solucion.vector_x == [3, 4, -6, -1]
    assert solucion.es_correcta


def test_fracciones_exactas_en_factores_y_solucion():
    factores = factorizar_lu([["1/2", 1], [1, 3]])
    solucion = resolver_sistema_lu(factores, ["3/2", 4])

    assert factores.matriz_l[1][0] == Fraction(2)
    assert solucion.vector_x == [Fraction(1), Fraction(1)]
    assert solucion.es_correcta


def test_pivote_nulo_inicial_intercambia_filas_y_resuelve_sistema():
    matriz_a = [[0, 2, 1], [1, 1, 0], [2, 3, 1]]
    factores = factorizar_lu(matriz_a)
    solucion = resolver_sistema_lu(factores, [7, 3, 11])

    assert factores.matriz_p == [[0, 1, 0], [1, 0, 0], [0, 0, 1]]
    assert factores.matriz_l == [[1, 0, 0], [0, 1, 0], [2, Fraction(1, 2), 1]]
    assert factores.matriz_u == [[1, 1, 0], [0, 2, 1], [0, 0, Fraction(1, 2)]]
    assert factores.producto_pa == factores.producto_lu
    assert factores.es_correcta
    assert any("F1 ↔ F2" in paso.descripcion for paso in factores.pasos)
    assert solucion.vector_pb == [3, 7, 11]
    assert solucion.vector_y == [3, 7, Fraction(3, 2)]
    assert solucion.vector_x == [1, 2, 3]
    assert solucion.producto_ax == solucion.vector_b
    assert solucion.es_correcta


def test_pivote_nulo_despues_de_eliminar_reordena_multiplicadores_previos():
    factores = factorizar_lu([[1, 1, 0], [2, 2, 1], [0, 3, 1]])
    solucion = resolver_sistema_lu(factores, [3, 9, 6])

    assert factores.matriz_p == [[1, 0, 0], [0, 0, 1], [0, 1, 0]]
    assert factores.matriz_l == [[1, 0, 0], [0, 1, 0], [2, 0, 1]]
    assert factores.producto_pa == factores.producto_lu
    assert solucion.vector_pb == [3, 6, 9]
    assert solucion.vector_x == [2, 1, 3]
    assert solucion.es_correcta


def test_dos_intercambios_y_columna_sin_pivote():
    factores = factorizar_lu([[0, 1, 0], [0, 0, 1], [1, 0, 0]])
    solucion = resolver_sistema_lu(factores, [3, 5, 2])

    assert sum("↔" in paso.descripcion for paso in factores.pasos) == 2
    assert factores.matriz_u == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    assert factores.producto_pa == factores.producto_lu
    assert solucion.vector_pb == [2, 3, 5]
    assert solucion.vector_x == [2, 3, 5]
    assert solucion.es_correcta

    rectangular = factorizar_lu([[0, 0, 1], [0, 1, 2]])
    assert rectangular.producto_pa == rectangular.producto_lu
    assert rectangular.matriz_p == [[0, 1], [1, 0]]
    assert any("sin pivote" in paso.descripcion for paso in rectangular.pasos)


def test_matriz_singular_con_lu_no_promete_solucion_unica():
    factores = factorizar_lu([[1, 2], [2, 4]])
    assert factores.es_correcta

    with pytest.raises(ValueError, match="no tiene solución única"):
        resolver_sistema_lu(factores, [1, 2])


@pytest.mark.parametrize("matriz_a", [
    [[0, 1], [0, 2]],
    [[1, 2], [2, 4], [3, 6]],
    [[0]],
])
def test_columnas_sin_pivote_y_rango_deficiente_conservan_lu(matriz_a):
    factores = factorizar_lu(matriz_a)

    assert factores.es_correcta
    assert factores.producto_lu == factores.matriz_a
    assert all(factores.matriz_l[i][i] == 1 for i in range(len(matriz_a)))
    assert any("sin pivote" in paso.descripcion for paso in factores.pasos)


def test_resolucion_rectangular_y_vector_incompatible_se_rechazan():
    factores_rectangulares = factorizar_lu([[1, 2, 3], [0, 1, 4]])
    with pytest.raises(ValueError, match="cuadrada"):
        resolver_sistema_lu(factores_rectangulares, [1, 2])

    factores_cuadrados = factorizar_lu([[1, 0], [0, 1]])
    with pytest.raises(ValueError, match="2 componentes"):
        resolver_sistema_lu(factores_cuadrados, [1])
