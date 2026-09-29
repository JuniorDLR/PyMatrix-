"""
MÓDULO 4: DETERMINANTES Y PROPIEDADES
Calculadora de Álgebra Lineal — Programa 4
"""

from typing import List
from src.core.matrix_ops import calcular_determinante
from src.core.domain import formatear_numero, Matriz
from modulos.utilidades_cli import (
    leer_numero, leer_entero_positivo, imprimir_matriz, pausar
)
from teoremas.resumen_teoremas import teoremas_determinantes


LOGO_DETERMINANTES = """
======================================================
 [ det(A) ] MÓDULO: DETERMINANTES Y PROPIEDADES
 [ ± ad-bc] Reducción por Filas e Invertibilidad
======================================================
"""


def ejecutar_modulo_determinantes(modo_global: str = "fraccion") -> str:
    """Menú interactivo del Módulo 4: Determinantes y Propiedades."""
    modo = modo_global

    while True:
        print(LOGO_DETERMINANTES)
        print(f" Formato numérico activo: [{modo.upper()}] (Fracciones / Decimales)")
        print("-" * 54)
        print(" 0. Ver Teoremas Clave del Módulo")
        print(" 1. Calcular Determinante (det(A)) con desarrollo paso a paso")
        print(" 2. Diagnóstico de Invertibilidad según el Determinante")
        print(" 3. Cargar Ejemplos Predefinidos de Clase")
        print(" 4. Cambiar Formato Numérico (Fracción ↔ Decimal)")
        print(" 5. Volver al Menú Principal")
        print("-" * 54)

        opcion = input("Seleccione una opción [0-5]: ").strip()

        if opcion == "0":
            print(teoremas_determinantes())
            pausar()

        elif opcion in ("1", "2"):
            print("\n--- CÁLCULO DE DETERMINANTE ---")
            n = leer_entero_positivo("Orden de la matriz cuadrada A (n) [1-8]: ", 1, 8)
            print(f"\nIngrese los coeficientes de la matriz A ({n}×{n}):")
            A: Matriz = []
            for i in range(n):
                fila = []
                for j in range(n):
                    val = leer_numero(f"  A[{i+1},{j+1}]: ")
                    fila.append(val)
                A.append(fila)

            _calcular_y_mostrar_determinante(A, modo)
            pausar()

        elif opcion == "3":
            print("\n--- EJEMPLOS PREDEFINIDOS DE DETERMINANTES ---")
            print(" 1. Matriz 2×2: A = [[3, -2], [4, 1]] (det = 11)")
            print(" 2. Matriz 3×3 Invertible: A = [[1, 2, 0], [-1, 3, 2], [2, 0, -1]]")
            print(" 3. Matriz 3×3 Singular (det = 0): A = [[1, 2, 3], [4, 5, 6], [5, 7, 9]]")
            sub_op = input("Seleccione ejemplo [1-3]: ").strip()

            if sub_op == "1":
                mat = [[3.0, -2.0], [4.0, 1.0]]
            elif sub_op == "2":
                mat = [[1.0, 2.0, 0.0], [-1.0, 3.0, 2.0], [2.0, 0.0, -1.0]]
            else:
                mat = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [5.0, 7.0, 9.0]]

            print("\nMatriz del ejemplo cargado:")
            imprimir_matriz(mat, modo)
            _calcular_y_mostrar_determinante(mat, modo)
            pausar()

        elif opcion == "4":
            modo = "decimal" if modo == "fraccion" else "fraccion"
            print(f"\n  ✓ Formato cambiado a: [{modo.upper()}]")
            pausar()

        elif opcion == "5":
            break
        else:
            print("  ⚠️ Opción no válida. Intente de nuevo.")

    return modo


def _calcular_y_mostrar_determinante(A: Matriz, modo: str) -> None:
    """Calcula y muestra el determinante y su análisis de invertibilidad."""
    print("\n--- MATRIZ A ---")
    imprimir_matriz(A, modo)

    res = calcular_determinante(A, modo=modo)
    print("\n--- PROCESO DE CÁLCULO ---")
    for p in res.pasos:
        print(p)

    print("\n--- RESULTADO Y ANÁLISIS ---")
    det_fmt = formatear_numero(res.determinante, modo)
    print(f"  • det(A) = {det_fmt}")
    if res.es_invertible:
        print(f"  • Invertibilidad: ✅ INVERTIBLE (det(A) = {det_fmt} ≠ 0).")
        print("    Las columnas de A son Linealmente Independientes y forman una base.")
    else:
        print(f"  • Invertibilidad: ⚠️ SINGULAR / NO INVERTIBLE (det(A) = 0).")
        print("    Las columnas de A son Linealmente Dependientes (al menos una fila/columna es redundante).")
