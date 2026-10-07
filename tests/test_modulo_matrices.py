"""Pruebas de modulos/modulo_matrices.py: operaciones, determinantes, inversas y propiedades.
Tema de clase: álgebra matricial y determinantes (sesiones 10 y 11), con resultados conocidos a mano.
Se ejecutan como script: py tests/test_modulo_matrices.py
Elaborado por: Grupo x"""
import sys
import os
from fractions import Fraction

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modulos.modulo_matrices import (
    crear_matriz, sumar_matrices, restar_matrices, multiplicar_escalar,
    multiplicar_matrices, trasponer_matriz, determinante_cofactores,
    determinante_sarrus, determinante_triangulacion, inversa_gauss_jordan,
    inversa_adjunta, matriz_cofactores, matriz_adjunta,
    verificar_propiedad_inversa_de_inversa, verificar_propiedad_inversa_del_producto,
    verificar_propiedad_inversa_de_traspuesta, verificar_propiedad_determinante_de_inversa,
    verificar_propiedades_operaciones_fila_det, verificar_propiedad_matriz_triangular,
    son_matrices_iguales, matriz_identidad
)


def run_all_tests():
    """Ejecuta todas las pruebas del módulo; falla con AssertionError si alguna no se cumple."""
    print("Iniciando pruebas unitarias de modulos/modulo_matrices.py...")

    # 1. Suma y Resta
    A = crear_matriz([[1, 2], [3, 4]])
    B = crear_matriz([[5, 6], [7, 8]])
    S = sumar_matrices(A, B)
    assert S == crear_matriz([[6, 8], [10, 12]]), "Fallo en suma"
    R = restar_matrices(A, B)
    assert R == crear_matriz([[-4, -4], [-4, -4]]), "Fallo en resta"
    print("✓ Suma y resta verificadas.")

    # 2. Escalar y Producto
    c = Fraction(1, 2)
    Esc = multiplicar_escalar(c, A)
    assert Esc == crear_matriz([["1/2", 1], ["3/2", 2]]), "Fallo en escalar"
    Prod = multiplicar_matrices(A, B)
    assert Prod == crear_matriz([[19, 22], [43, 50]]), "Fallo en producto"
    print("✓ Multiplicación escalar y producto matricial verificados.")

    # 3. Transposición
    M_rect = crear_matriz([[1, 2, 3], [4, 5, 6]])
    MT = trasponer_matriz(M_rect)
    assert MT == crear_matriz([[1, 4], [2, 5], [3, 6]]), "Fallo en transposición"
    print("✓ Transposición verificada.")

    # 4. Determinante 3x3 por Cofactores, Sarrus y Triangulación
    # Matriz conocida: det = -14
    # [1, 2, 3]
    # [4, 5, 6]
    # [7, 2, 9]
    M3 = crear_matriz([[1, 2, 3], [4, 5, 6], [7, 2, 9]])
    det_cof, _ = determinante_cofactores(M3)
    det_sar, _ = determinante_sarrus(M3)
    det_tri, _ = determinante_triangulacion(M3)
    assert det_cof == Fraction(-36, 1), f"Esperado -36, obtenido {det_cof}"
    assert det_sar == Fraction(-36, 1), f"Sarrus esperado -36, obtenido {det_sar}"
    assert det_tri == Fraction(-36, 1), f"Triangulación esperado -36, obtenido {det_tri}"
    print(f"✓ Determinantes coincidentes (-36) por Cofactores, Sarrus y Triangulación.")

    # 5. Inversa por Gauss-Jordan y por Adjunta
    A_inv_test = crear_matriz([[1, 2], [3, 4]]) # det = -2 != 0
    res_gj = inversa_gauss_jordan(A_inv_test)
    assert res_gj.es_invertible is True
    assert res_gj.comprobacion_identidad is True
    assert res_gj.matriz_inversa == crear_matriz([[-2, 1], ["3/2", "-1/2"]])

    res_adj = inversa_adjunta(A_inv_test)
    assert res_adj.es_invertible is True
    assert res_adj.comprobacion_identidad is True
    assert son_matrices_iguales(res_gj.matriz_inversa, res_adj.matriz_inversa)
    print("✓ Inversa por Gauss-Jordan y Matriz Adjunta verificadas con A * A⁻¹ = I.")

    # 6. Detección de singularidad
    singular = crear_matriz([[1, 2], [2, 4]])
    res_gj_sing = inversa_gauss_jordan(singular)
    assert res_gj_sing.es_invertible is False
    res_adj_sing = inversa_adjunta(singular)
    assert res_adj_sing.es_invertible is False
    print("✓ Detección de matrices singulares verificada.")

    # 7. Propiedades de Sesiones 10 y 11
    # Matriz invertible A y B
    A_p = crear_matriz([[2, 1], [5, 3]]) # det = 1
    B_p = crear_matriz([[1, 2], [3, 4]]) # det = -2

    p1 = verificar_propiedad_inversa_de_inversa(A_p)
    assert p1.se_cumple, "Fallo en propiedad 1"
    print(f"✓ Propiedad 1 verificada: {p1.formula}")

    p2 = verificar_propiedad_inversa_del_producto(A_p, B_p)
    assert p2.se_cumple, "Fallo en propiedad 2"
    print(f"✓ Propiedad 2 verificada: {p2.formula}")

    p3 = verificar_propiedad_inversa_de_traspuesta(A_p)
    assert p3.se_cumple, "Fallo en propiedad 3"
    print(f"✓ Propiedad 3 verificada: {p3.formula}")

    p4 = verificar_propiedad_determinante_de_inversa(A_p)
    assert p4.se_cumple, "Fallo en propiedad 4"
    print(f"✓ Propiedad 4 verificada: {p4.formula}")

    p5_list = verificar_propiedades_operaciones_fila_det(A_p)
    for p5 in p5_list:
        assert p5.se_cumple, f"Fallo en {p5.formula}"
        print(f"✓ Propiedad de operaciones de fila verificada: {p5.formula}")

    p6 = verificar_propiedad_matriz_triangular(A_p)
    assert p6.se_cumple, "Fallo en propiedad 6"
    print(f"✓ Propiedad matriz triangular verificada: {p6.formula}")

    print("\n🎉 TODAS LAS PRUEBAS DE modulo_matrices.py PASARON EXITOSAMENTE.")


if __name__ == "__main__":
    run_all_tests()
