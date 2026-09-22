"""
Pruebas automatizadas para los módulos de Vectores y Operaciones Matriciales.
Verifica los ejercicios y teoremas de las diapositivas de la UAM (Programa 3).
"""

import sys
import os

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Asegurar que la raíz del proyecto esté en PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.vectors import (
    sumar_vectores, restar_vectores, multiplicar_vector_escalar,
    sumar_multiples_vectores, restar_multiples_vectores, combinacion_lineal_ponderada,
    producto_punto, norma_vector, son_proporcionales_2_vectores,
    evaluar_combinacion_lineal, evaluar_independencia_lineal
)
from src.core.matrix_ops import (
    sumar_matrices, restar_matrices, multiplicar_matriz_escalar,
    combinacion_matrices,
    multiplicar_matrices, multiplicar_matriz_vector, resolver_ecuacion_matricial
)


def test_operaciones_vectoriales_basicas():
    print("=== Test 1: Operaciones Vectoriales Básicas ===")
    # Slide 4: u = [1, -2]^T, v = [2, 5]^T
    u = [1.0, -2.0]
    v = [2.0, 5.0]
    suma = sumar_vectores(u, v)
    assert suma == [3.0, 3.0], f"Fallo en suma: {suma}"
    print("✓ Suma de vectores [1, -2] + [2, 5] = [3, 3]")

    # Slide 4: u = [3, -1]^T, c = 5
    u3 = [3.0, -1.0]
    esc = multiplicar_vector_escalar(5.0, u3)
    assert esc == [15.0, -5.0], f"Fallo en escalar: {esc}"
    print("✓ Escalar por vector 5 · [3, -1] = [15, -5]")

    # Slide 4 Ej 4: 4u + (-3)v con u = [1, -2], v = [2, -5]
    u4 = [1.0, -2.0]
    v4 = [2.0, -5.0]
    res4 = sumar_vectores(multiplicar_vector_escalar(4.0, u4), multiplicar_vector_escalar(-3.0, v4))
    assert res4 == [-2.0, 7.0], f"Fallo en 4u + (-3)v: {res4}"
    print("✓ Combinación básica 4u - 3v = [-2, 7]")

    # Producto punto y norma
    pp = producto_punto([1.0, 2.0, 3.0], [4.0, -5.0, 6.0])
    assert pp == 12.0, f"Fallo producto punto: {pp}"
    print("✓ Producto punto [1, 2, 3] · [4, -5, 6] = 12")

    # Múltiples vectores (k = 3 en ℝ³)
    v1 = [1.0, 2.0, 3.0]
    v2 = [4.0, 5.0, 6.0]
    v3 = [7.0, 8.0, 9.0]
    
    # Suma de todos
    sum_all = sumar_multiples_vectores([v1, v2, v3])
    assert sum_all == [12.0, 15.0, 18.0], f"Fallo suma múltiple: {sum_all}"
    print("✓ Suma acumulada de 3 vectores [12, 15, 18]")

    # Resta sucesiva v1 - v2 - v3
    sub_all = restar_multiples_vectores([v1, v2, v3])
    # 1 - 4 - 7 = -10, 2 - 5 - 8 = -11, 3 - 6 - 9 = -12
    assert sub_all == [-10.0, -11.0, -12.0], f"Fallo resta múltiple: {sub_all}"
    print("✓ Resta sucesiva de 3 vectores [-10, -11, -12]")

    # Combinación lineal ponderada c₁v₁ + c₂v₂ + c₃v₃ con c = [2, -1, 3]
    # 2*[1,2,3] - [4,5,6] + 3*[7,8,9]
    # x: 2(1) - 4 + 3(7) = 2 - 4 + 21 = 19
    # y: 2(2) - 5 + 3(8) = 4 - 5 + 24 = 23
    # z: 2(3) - 6 + 3(9) = 6 - 6 + 27 = 27
    comb_pond = combinacion_lineal_ponderada([2.0, -1.0, 3.0], [v1, v2, v3])
    assert comb_pond == [19.0, 23.0, 27.0], f"Fallo combinación ponderada: {comb_pond}"
    print("✓ Combinación lineal ponderada de 3 vectores con escalares independientes [19, 23, 27]")


def test_combinacion_lineal():
    print("\n=== Test 2: Evaluación de Combinación Lineal ===")
    # Slide 11: a1 = [1, -2, -5], a2 = [2, 5, 6], b = [7, 4, -3]
    a1 = [1.0, -2.0, -5.0]
    a2 = [2.0, 5.0, 6.0]
    b = [7.0, 4.0, -3.0]
    res_comb = evaluar_combinacion_lineal([a1, a2], b)
    assert res_comb.es_combinacion is True
    assert res_comb.pesos is not None
    assert round(res_comb.pesos[0], 2) == 3.0
    assert round(res_comb.pesos[1], 2) == 2.0
    print("✓ Diapositiva 11: b es combinación lineal única con c₁=3 y c₂=2")

    # Inconsistente (no es combinación lineal)
    v1 = [1.0, 0.0]
    v2 = [2.0, 0.0]
    b_inc = [1.0, 5.0]
    res_inc = evaluar_combinacion_lineal([v1, v2], b_inc)
    assert res_inc.es_combinacion is False
    print("✓ Detección exitosa de vector que NO es combinación lineal")


def test_independencia_lineal():
    print("\n=== Test 3: Independencia y Dependencia Lineal ===")
    # Slide 12-14: v1=[1, -2, 3], v2=[2, -2, 0], v3=[0, 1, 7] -> L.I.
    v1 = [1.0, -2.0, 3.0]
    v2 = [2.0, -2.0, 0.0]
    v3 = [0.0, 1.0, 7.0]
    res_li = evaluar_independencia_lineal([v1, v2, v3])
    assert res_li.es_linealmente_independiente is True
    print("✓ Diapositiva 12-14: Conjunto identificado correctamente como L.I.")

    # Slide 15-16: v1=[1, -3, 0], v2=[3, 0, 4], v3=[11, -6, 12] -> L.D.
    u1 = [1.0, -3.0, 0.0]
    u2 = [3.0, 0.0, 4.0]
    u3 = [11.0, -6.0, 12.0]
    res_ld = evaluar_independencia_lineal([u1, u2, u3])
    assert res_ld.es_linealmente_independiente is False
    assert res_ld.relacion_dependencia is not None
    print(f"✓ Diapositiva 15-16: Conjunto identificado como L.D. Relación: {res_ld.relacion_dependencia}")

    # Slide 20: v1=[3, 1], v2=[6, 2] -> L.D. por múltiplos escalares
    p1 = [3.0, 1.0]
    p2 = [6.0, 2.0]
    res_prop = evaluar_independencia_lineal([p1, p2])
    assert res_prop.es_linealmente_independiente is False
    print("✓ Diapositiva 20: Detección por inspección de 2 vectores múltiplos escalares")

    # Slide 22: Teorema p > n (4 vectores en R^3)
    w1 = [1.0, 7.0, 6.0]
    w2 = [0.0, 0.0, 9.0]
    w3 = [3.0, 1.0, 5.0]
    w4 = [4.0, 1.0, 8.0]
    res_pn = evaluar_independencia_lineal([w1, w2, w3, w4])
    assert res_pn.es_linealmente_independiente is False
    assert "p > n" in res_pn.criterio_utilizado
    print("✓ Diapositiva 22: Detección por teorema p > n (4 vectores en ℝ³)")

    # Slide 22: Contiene vector cero
    z1 = [2.0, 3.0, 5.0]
    z2 = [0.0, 0.0, 0.0]
    z3 = [1.0, 1.0, 8.0]
    res_zero = evaluar_independencia_lineal([z1, z2, z3])
    assert res_zero.es_linealmente_independiente is False
    assert "Cero" in res_zero.criterio_utilizado
    print("✓ Diapositiva 22: Detección por contener vector cero")


def test_operaciones_matriciales():
    print("\n=== Test 4: Operaciones Matriciales Básicas ===")
    A = [[1.0, 2.0], [3.0, 4.0]]
    B = [[5.0, 6.0], [7.0, 8.0]]

    # Suma
    S = sumar_matrices(A, B)
    assert S == [[6.0, 8.0], [10.0, 12.0]]
    print("✓ Suma de matrices A + B correcta")

    # Resta
    R = restar_matrices(B, A)
    assert R == [[4.0, 4.0], [4.0, 4.0]]
    print("✓ Resta de matrices B - A correcta")

    # Escalar
    E = multiplicar_matriz_escalar(3.0, A)
    assert E == [[3.0, 6.0], [9.0, 12.0]]
    print("✓ Multiplicación de matriz por escalar 3·A correcta")

    # Combinación lineal matricial c_A·A + c_B·B con c_A=2, c_B=-1
    # 2*[[1, 2], [3, 4]] - [[5, 6], [7, 8]] = [[2-5, 4-6], [6-7, 8-8]] = [[-3, -2], [-1, 0]]
    comb_mat = combinacion_matrices(2.0, A, -1.0, B)
    assert comb_mat == [[-3.0, -2.0], [-1.0, 0.0]]
    print("✓ Combinación lineal matricial 2·A - 1·B correcta")

    # Multiplicación matricial: A (2x3) y B (3x2)
    # A = [[1, 2, -1], [0, -5, 3]]
    # B = [[4, 1], [3, 0], [7, 2]]
    M_A = [[1.0, 2.0, -1.0], [0.0, -5.0, 3.0]]
    M_B = [[4.0, 1.0], [3.0, 0.0], [7.0, 2.0]]
    res_mult = multiplicar_matrices(M_A, M_B)
    assert res_mult.dimensiones_resultado == (2, 2)
    # C11 = 1*4 + 2*3 + (-1)*7 = 4 + 6 - 7 = 3
    # C12 = 1*1 + 2*0 + (-1)*2 = 1 - 2 = -1
    # C21 = 0*4 + (-5)*3 + 3*7 = -15 + 21 = 6
    # C22 = 0*1 + (-5)*0 + 3*2 = 6
    assert res_mult.matriz_resultado == [[3.0, -1.0], [6.0, 6.0]]
    print("✓ Multiplicación matricial A · B con bucles anidados verificada")

    # Multiplicación matricial B · A: (3x2) x (2x3) -> (3x3)
    # B = [[4, 1], [3, 0], [7, 2]], A = [[1, 2, -1], [0, -5, 3]]
    # fila 1: [4(1)+1(0), 4(2)+1(-5), 4(-1)+1(3)] = [4, 3, -1]
    # fila 2: [3(1)+0(0), 3(2)+0(-5), 3(-1)+0(3)] = [3, 6, -3]
    # fila 3: [7(1)+2(0), 7(2)+2(-5), 7(-1)+2(3)] = [7, 4, -1]
    res_mult_ba = multiplicar_matrices(M_B, M_A)
    assert res_mult_ba.dimensiones_resultado == (3, 3)
    assert res_mult_ba.matriz_resultado == [
        [4.0, 3.0, -1.0],
        [3.0, 6.0, -3.0],
        [7.0, 4.0, -1.0]
    ]
    print("✓ Multiplicación matricial B · A (3x3) verificada")

    # Validación de dimensiones incompatibles
    try:
        multiplicar_matrices([[1.0, 2.0]], [[1.0, 2.0]])
        assert False, "Debió lanzar ValueError"
    except ValueError as err:
        assert "Incompatibilidad" in str(err)
        print(f"✓ Captura esperada de dimensiones incompatibles: {err}")


def test_ecuaciones_matriciales():
    print("\n=== Test 5: Ecuaciones Matriciales (Ax = b) ===")
    # Slide 4: A = [[1, 2, -1], [0, -5, 3]], x = [4, 3, 7] -> [3, 6]
    A = [[1.0, 2.0, -1.0], [0.0, -5.0, 3.0]]
    x = [4.0, 3.0, 7.0]
    prod_mv = multiplicar_matriz_vector(A, x)
    assert prod_mv.vector_resultado == [3.0, 6.0]
    print("✓ Slide 4: Producto matriz-vector A · x = [3, 6] verificado")

    # Slide 5: A = [[2, -3], [8, 0], [-5, 2]], x = [4, 7] -> [-13, 32, -6]
    A5 = [[2.0, -3.0], [8.0, 0.0], [-5.0, 2.0]]
    x5 = [4.0, 7.0]
    prod_mv5 = multiplicar_matriz_vector(A5, x5)
    assert prod_mv5.vector_resultado == [-13.0, 32.0, -6.0]
    print("✓ Slide 5: Producto matriz-vector A · x = [-13, 32, -6] verificado")

    # Resolución de Ax = b
    # A = [[1, 2, -1], [0, -5, 3]], b = [3, 6]
    res_eq = resolver_ecuacion_matricial(A, [3.0, 6.0])
    assert res_eq.es_consistente is True
    print("✓ Resolución computacional de Ax = b consistente comprobada")


if __name__ == "__main__":
    test_operaciones_vectoriales_basicas()
    test_combinacion_lineal()
    test_independencia_lineal()
    test_operaciones_matriciales()
    test_ecuaciones_matriciales()
    print("\n=======================================================")
    print("   TODAS LAS PRUEBAS MATEMÁTICAS PASARON CON ÉXITO!   ")
    print("=======================================================")
