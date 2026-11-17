"""Casos de clase y rutas de validación de los métodos iterativos."""

import pytest

from src.core.numericos.iterativos import comparar_metodos


CLASE_A = [["10", "3", "1"], ["5", "-10", "3"], ["1", "3", "10"]]


def test_ejemplo_de_clase_reproduce_tablas_con_norma_euclidiana() -> None:
    resultado = comparar_metodos(CLASE_A, ["14", "-5", "14"], ["0"] * 3,
                                 "0.0001", "100", criterio="euclidiana")
    assert resultado.dominante
    assert resultado.jacobi.pasos[0].valores == pytest.approx((1.4, 0.5, 1.4))
    assert resultado.seidel.pasos[0].valores == pytest.approx((1.4, 1.2, 0.9))
    assert resultado.jacobi.estado == resultado.seidel.estado == "tolerancia"
    assert len(resultado.jacobi.pasos) == 16
    assert len(resultado.seidel.pasos) == 5
    assert resultado.referencia == pytest.approx((0.93283582, 1.24626866, 0.93283582))


def test_reordenamiento_de_filas_sigue_ejercicio_1112() -> None:
    resultado = comparar_metodos(
        [["2", "-6", "-1"], ["-3", "-1", "7"], ["-8", "1", "-2"]],
        ["-38", "-34", "-20"], ["0"] * 3, "0.0001", "100",
    )
    assert resultado.orden_filas == (2, 0, 1)
    assert resultado.dominante
    assert resultado.jacobi.estado == resultado.seidel.estado == "tolerancia"
    assert resultado.jacobi.pasos[-1].residuo < 0.01


def test_sin_convergencia_y_maximo_se_reportan_sin_fingir_solucion() -> None:
    divergente = comparar_metodos([["1", "2"], ["2", "1"]], ["3", "3"],
                                  ["0", "0"], "0.0001", "30", reordenar=False)
    assert divergente.jacobi.estado == "posible divergencia"
    assert divergente.seidel.estado == "posible divergencia"
    corto = comparar_metodos(CLASE_A, ["14", "-5", "14"], ["0"] * 3,
                             "0.0001", "1")
    assert corto.jacobi.estado == corto.seidel.estado == "máximo"


@pytest.mark.parametrize("matriz,b,x0,e,k,mensaje", [
    ([[]], ["1"], ["0"], "0.1", "10", "cuadrada"),
    ([["0"]], ["1"], ["0"], "0.1", "10", "diagonal"),
    ([["1"]], [], ["0"], "0.1", "10", "exactamente"),
    ([["1"]], ["a"], ["0"], "0.1", "10", "b\\[1\\]"),
    ([["1"]], ["1"], ["0"], "0", "10", "positiva"),
    ([["1"]], ["1"], ["0"], "0.1", "1.5", "entero"),
])
def test_entradas_invalidas_fallan_antes_de_iterar(matriz, b, x0, e, k, mensaje) -> None:
    with pytest.raises(ValueError, match=mensaje):
        comparar_metodos(matriz, b, x0, e, k)


def test_fracciones_y_negativos_son_entradas_validas() -> None:
    r = comparar_metodos([["2", "0"], ["0", "-3"]], ["1/2", "-6"],
                         ["-1", "1/3"], "1/1000", "10")
    assert r.jacobi.solucion == pytest.approx((0.25, 2))
    assert r.seidel.solucion == pytest.approx((0.25, 2))
