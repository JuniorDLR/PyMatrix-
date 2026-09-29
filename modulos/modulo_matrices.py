"""
MÓDULO 3: ÁLGEBRA DE MATRICES E INVERSA
Calculadora de Álgebra Lineal — Programa 4
"""

from typing import List
from src.core.matrix_ops import (
    sumar_matrices, restar_matrices, multiplicar_matriz_escalar,
    multiplicar_matrices, trasponer_matriz, invertir_matriz,
    multiplicar_matriz_vector, verificar_propiedad_aditiva_ax,
    verificar_propiedad_escalar_ax
)
from src.core.domain import formatear_numero, Matriz
from modulos.utilidades_cli import (
    leer_numero, leer_entero_positivo, imprimir_matriz, pausar
)
from teoremas.resumen_teoremas import teoremas_matrices


LOGO_MATRICES = """
======================================================
 [ A ][ B ] MÓDULO: ÁLGEBRA DE MATRICES
 [ C ][ D ] Operaciones, Traspuesta y Matriz Inversa
======================================================
"""


def ejecutar_modulo_matrices(modo_global: str = "fraccion") -> str:
    """Menú interactivo del Módulo 3: Álgebra de Matrices e Inversa."""
    modo = modo_global

    while True:
        print(LOGO_MATRICES)
        print(f" Formato numérico activo: [{modo.upper()}] (Fracciones / Decimales)")
        print("-" * 54)
        print(" 0. Ver Teoremas Clave del Módulo")
        print(" 1. Suma de Matrices (A + B)")
        print(" 2. Resta de Matrices (A − B)")
        print(" 3. Multiplicación por Escalar (c · A)")
        print(" 4. Multiplicación Matricial (A · B con bucles anidados)")
        print(" 5. Traspuesta de una Matriz (Aᵀ)")
        print(" 6. Matriz Inversa (A⁻¹ mediante [A | I] → [I | A⁻¹])")
        print(" 7. Producto Matriz-Vector (A · x) y Propiedades de Linealidad")
        print(" 8. Cambiar Formato Numérico (Fracción ↔ Decimal)")
        print(" 9. Volver al Menú Principal")
        print("-" * 54)

        opcion = input("Seleccione una opción [0-9]: ").strip()

        if opcion == "0":
            print(teoremas_matrices())
            pausar()

        elif opcion in ("1", "2"):
            op_nombre = "SUMA" if opcion == "1" else "RESTA"
            print(f"\n--- {op_nombre} DE MATRICES (A {'+' if opcion == '1' else '−'} B) ---")
            m = leer_entero_positivo("Filas de las matrices (m) [1-10]: ", 1, 10)
            n = leer_entero_positivo("Columnas de las matrices (n) [1-10]: ", 1, 10)

            print(f"\nIngrese matriz A ({m}×{n}):")
            A = _leer_matriz_cli(m, n, "A")
            print(f"\nIngrese matriz B ({m}×{n}):")
            B = _leer_matriz_cli(m, n, "B")

            if opcion == "1":
                R = sumar_matrices(A, B)
                print(f"\nResultado A + B ({m}×{n}):")
            else:
                R = restar_matrices(A, B)
                print(f"\nResultado A − B ({m}×{n}):")

            imprimir_matriz(R, modo)
            pausar()

        elif opcion == "3":
            print("\n--- MULTIPLICACIÓN DE MATRIZ POR ESCALAR (c · A) ---")
            m = leer_entero_positivo("Filas de A (m) [1-10]: ", 1, 10)
            n = leer_entero_positivo("Columnas de A (n) [1-10]: ", 1, 10)
            A = _leer_matriz_cli(m, n, "A")
            c = leer_numero("\nIngrese el escalar c: ")

            R = multiplicar_matriz_escalar(c, A)
            c_str = formatear_numero(c, modo)
            print(f"\nResultado {c_str} · A ({m}×{n}):")
            imprimir_matriz(R, modo)
            pausar()

        elif opcion == "4":
            print("\n--- MULTIPLICACIÓN DE MATRICES (A · B) ---")
            print("Condición de compatibilidad: Columnas de A debe ser igual a Filas de B.")
            mA = leer_entero_positivo("Filas de A (m) [1-10]: ", 1, 10)
            nA = leer_entero_positivo("Columnas de A (n) [1-10]: ", 1, 10)
            print(f"\nPara que el producto esté definido, la matriz B debe tener {nA} filas.")
            pB = leer_entero_positivo("Columnas de B (p) [1-10]: ", 1, 10)

            print(f"\nIngrese matriz A ({mA}×{nA}):")
            A = _leer_matriz_cli(mA, nA, "A")
            print(f"\nIngrese matriz B ({nA}×{pB}):")
            B = _leer_matriz_cli(nA, pB, "B")

            res_prod = multiplicar_matrices(A, B, modo=modo)
            print("\nProcedimiento posicional (algoritmo triple bucle anidado):")
            for paso in res_prod.desglose_pasos:
                print(f"  {paso}")

            print(f"\nResultado C = A · B ({mA}×{pB}):")
            imprimir_matriz(res_prod.matriz_resultado, modo)
            pausar()

        elif opcion == "5":
            print("\n--- MATRIZ TRASPUESTA (Aᵀ) ---")
            m = leer_entero_positivo("Filas de A (m) [1-10]: ", 1, 10)
            n = leer_entero_positivo("Columnas de A (n) [1-10]: ", 1, 10)
            A = _leer_matriz_cli(m, n, "A")

            At = trasponer_matriz(A)
            print(f"\nMatriz original A ({m}×{n}):")
            imprimir_matriz(A, modo)
            print(f"\nMatriz traspuesta Aᵀ ({n}×{m}):")
            imprimir_matriz(At, modo)
            pausar()

        elif opcion == "6":
            print("\n--- MATRIZ INVERSA (A⁻¹) POR GAUSS-JORDAN [A | I] ---")
            n = leer_entero_positivo("Orden de la matriz cuadrada A (n) [1-8]: ", 1, 8)
            A = _leer_matriz_cli(n, n, "A")

            res_inv = invertir_matriz(A, modo=modo)
            print("\nProcedimiento de inversión:")
            for p in res_inv.pasos:
                print(p)

            print(res_inv.explicacion)
            if res_inv.es_invertible and res_inv.matriz_inversa:
                print(f"\nMatriz Inversa A⁻¹ ({n}×{n}):")
                imprimir_matriz(res_inv.matriz_inversa, modo)
            pausar()

        elif opcion == "7":
            _menu_producto_matriz_vector(modo)

        elif opcion == "8":
            modo = "decimal" if modo == "fraccion" else "fraccion"
            print(f"\n  ✓ Formato cambiado a: [{modo.upper()}]")
            pausar()

        elif opcion == "9":
            break
        else:
            print("  ⚠️ Opción no válida. Intente de nuevo.")

    return modo


def _leer_matriz_cli(filas: int, cols: int, nombre: str = "A") -> Matriz:
    """Solicita al usuario los elementos fila a fila para una matriz."""
    mat: Matriz = []
    for i in range(filas):
        fila = []
        for j in range(cols):
            val = leer_numero(f"  {nombre}[{i+1},{j+1}]: ")
            fila.append(val)
        mat.append(fila)
    return mat


def _menu_producto_matriz_vector(modo: str) -> None:
    """Submenú de producto matriz-vector y verificación de propiedades."""
    print("\n--- PRODUCTO MATRIZ-VECTOR (A · x) Y PROPIEDADES ---")
    m = leer_entero_positivo("Filas de A (m) [1-8]: ", 1, 8)
    n = leer_entero_positivo("Columnas de A / Dimensión de vectores (n) [1-8]: ", 1, 8)

    print(f"\nIngrese matriz A ({m}×{n}):")
    A = _leer_matriz_cli(m, n, "A")

    print(f"\nIngrese vector u ({n} componentes):")
    u = [leer_numero(f"  u[{i+1}]: ") for i in range(n)]
    print(f"\nIngrese vector v ({n} componentes):")
    v = [leer_numero(f"  v[{i+1}]: ") for i in range(n)]
    c = leer_numero("\nIngrese escalar c: ")

    print("\n" + "=" * 54)
    print(" 1. Verificación Propiedad Aditiva: A(u + v) = Au + Av")
    print("=" * 54)
    res_aditiva = verificar_propiedad_aditiva_ax(A, u, v, modo=modo)
    for linea in res_aditiva.desglose_pasos:
        print(linea)

    print("\n" + "=" * 54)
    print(" 2. Verificación Propiedad Escalar: A(cu) = c(Au)")
    print("=" * 54)
    res_escalar = verificar_propiedad_escalar_ax(A, u, c, modo=modo)
    for linea in res_escalar.desglose_pasos:
        print(linea)

    pausar()
