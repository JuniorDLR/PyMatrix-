"""
MÓDULO 1: SISTEMAS DE ECUACIONES LINEALES (SEL)
Calculadora de Álgebra Lineal — Programa 4
"""

from typing import List
from src.core.gauss import resolver_gauss, resolver_gauss_jordan
from src.core.domain import formatear_numero, Matriz, a_subindice
from modulos.utilidades_cli import leer_numero, leer_entero_positivo, imprimir_matriz_aumentada, pausar
from teoremas.resumen_teoremas import teoremas_sistemas


LOGO_SISTEMAS = """
======================================================
 [ [1 2 | 3] ] MÓDULO: SISTEMAS DE ECUACIONES (SEL)
 [ [0 1 | 5] ] Métodos: Gauss, Gauss-Jordan
======================================================
"""


def ejecutar_modulo_sistemas(modo_global: str = "fraccion") -> str:
    """Menú interactivo del Módulo 1: Sistemas de Ecuaciones Lineales."""
    modo = modo_global

    while True:
        print(LOGO_SISTEMAS)
        print(f" Formato numérico activo: [{modo.upper()}] (Fracciones / Decimales)")
        print("-" * 54)
        print(" 0. Ver Teoremas Clave del Módulo")
        print(" 1. Resolver Sistema por Eliminación de Gauss (Forma REF)")
        print(" 2. Resolver Sistema por Gauss-Jordan (Forma RREF)")
        print(" 3. Cargar Ejemplo Predefinido de Clase")
        print(" 4. Cambiar Formato Numérico (Fracción ↔ Decimal)")
        print(" 5. Volver al Menú Principal")
        print("-" * 54)

        opcion = input("Seleccione una opción [0-5]: ").strip()

        if opcion == "0":
            print(teoremas_sistemas())
            pausar()

        elif opcion in ("1", "2"):
            metodo_nombre = "Gauss" if opcion == "1" else "Gauss-Jordan"
            print(f"\n--- RESOLUCIÓN POR MÉTODO: {metodo_nombre.upper()} ---")
            m = leer_entero_positivo("Ingrese número de ecuaciones (filas m) [1-10]: ", 1, 10)
            n = leer_entero_positivo("Ingrese número de incógnitas (variables n) [1-10]: ", 1, 10)

            print(f"\nIngrese los coeficientes de la matriz aumentada [A | b] ({m} filas × {n+1} columnas):")
            print("  (Puede ingresar fracciones como '1/2', '-3/4' o decimales como '0.5')")

            matriz: Matriz = []
            for i in range(m):
                print(f"\n>> Ecuación {i+1} (Fila {i+1}):")
                fila = []
                for j in range(n):
                    val = leer_numero(f"  Coeficiente de x{a_subindice(j+1)}: ")
                    fila.append(val)
                ti = leer_numero(f"  Término independiente (= b{a_subindice(i+1)}): ")
                fila.append(ti)
                matriz.append(fila)

            _resolver_y_mostrar_sel(matriz, opcion == "2", modo)
            pausar()

        elif opcion == "3":
            print("\n--- EJEMPLOS PREDEFINIDOS DE CLASE ---")
            print(" 1. Sistema 3×3 con Solución Única (x₁=2, x₂=3, x₃=-1)")
            print(" 2. Sistema 3×4 con Infinitas Soluciones (Variables libres)")
            print(" 3. Sistema Inconsistente (Sin solución, 0 = k)")
            sub_op = input("Seleccione ejemplo [1-3]: ").strip()

            if sub_op == "1":
                mat = [
                    [2.0, 1.0, -1.0, 8.0],
                    [-3.0, -1.0, 2.0, -11.0],
                    [-2.0, 1.0, 2.0, -3.0]
                ]
            elif sub_op == "2":
                mat = [
                    [1.0, 2.0, -1.0, 1.0, 3.0],
                    [2.0, 4.0, -2.0, 2.0, 6.0],
                    [1.0, 2.0, 0.0, -1.0, 1.0]
                ]
            else:
                mat = [
                    [1.0, 1.0, 1.0, 2.0],
                    [0.0, 1.0, -1.0, 1.0],
                    [2.0, 3.0, 1.0, 7.0]
                ]

            print("\nMatriz aumentada del ejemplo cargado:")
            imprimir_matriz_aumentada(mat, modo)
            print("\nResolviendo con Gauss-Jordan:")
            _resolver_y_mostrar_sel(mat, True, modo)
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


def _resolver_y_mostrar_sel(matriz: Matriz, usar_gauss_jordan: bool, modo: str) -> None:
    """Ejecuta Gauss o Gauss-Jordan y muestra el procedimiento completo en consola."""
    print("\n--- 1. MATRIZ AUMENTADA INICIAL [A | b] ---")
    imprimir_matriz_aumentada(matriz, modo)

    if usar_gauss_jordan:
        pasos, resultado, sol_gen = resolver_gauss_jordan(matriz)
    else:
        pasos, resultado, sol_gen = resolver_gauss(matriz)

    if pasos and len(pasos) > 1:
        print("\n--- 2. PROCESO DE REDUCCIÓN PASO A PASO ---")
        for idx, paso in enumerate(pasos[1:], 1):
            print(f">> Paso {idx}: {paso.descripcion}")
            imprimir_matriz_aumentada(paso.matriz_estado, modo)

    matriz_final = pasos[-1].matriz_estado if pasos else matriz
    nombre_forma = "FORMA ESCALONADA REDUCIDA (RREF)" if usar_gauss_jordan else "FORMA ESCALONADA POR FILAS (REF)"
    print(f"\n--- 3. {nombre_forma} ---")
    imprimir_matriz_aumentada(matriz_final, modo)

    print("\n--- 4. CLASIFICACIÓN Y SOLUCIÓN FINAL ---")
    tipo = resultado.tipo
    print(f"Tipo de Sistema: {tipo.upper()}")

    if tipo == "Consistente Determinado":
        print("  ✓ Sistema con SOLUCIÓN ÚNICA:")
        for idx, val in enumerate(resultado.variables, 1):
            print(f"    x{a_subindice(idx)} = {formatear_numero(val, modo)}")

    elif tipo == "Consistente Indeterminado":
        print("  ✓ Sistema con INFINITAS SOLUCIONES:")
        if sol_gen:
            print(f"  • Variables Básicas: {', '.join(f'x{a_subindice(v+1)}' for v in sol_gen.variables_basicas)}")
            print(f"  • Variables Libres:  {', '.join(f'x{a_subindice(v+1)}' for v in sol_gen.variables_libres)}")
            print("\n  Solución General Parametrizada:")
            num_vars = len(matriz[0]) - 1
            for linea in sol_gen.a_strings(num_vars, modo):
                print(f"    {linea}")

    else:
        print("  ✗ Sistema INCONSISTENTE (SIN SOLUCIÓN):")
        print("    Surge una contradicción algebraica del tipo 0 = k (con k ≠ 0).")
