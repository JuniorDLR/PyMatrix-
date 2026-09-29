"""
MÓDULO 2: VECTORES E INDEPENDENCIA LINEAL
Calculadora de Álgebra Lineal — Programa 4
Cumple con todos los requerimientos técnicos y pedagógicos del Programa 4:
  1. Solicitar cantidad de vectores k y dimensión n.
  2. Construir el sistema homogéneo Ax = 0 con vectores como columnas.
  3. Reducir por filas mediante Gauss-Jordan, contar pivotes y variables libres.
  4. Emitir veredicto teórico explícito (L.I. o L.D.) y deducir relaciones de dependencia.
"""

from typing import List
from src.core.vectors import (
    Vector, evaluar_independencia_lineal, evaluar_combinacion_lineal,
    sumar_vectores, restar_vectores, multiplicar_vector_escalar, producto_punto
)
from src.core.domain import formatear_numero, a_subindice
from modulos.utilidades_cli import (
    leer_numero, leer_entero_positivo, imprimir_matriz,
    imprimir_matriz_aumentada, pausar
)
from teoremas.resumen_teoremas import teoremas_vectores


LOGO_VECTORES = """
======================================================
 MÓDULO: VECTORES E INDEPENDENCIA LINEAL
 Combinaciones Lineales, L.I. y L.D.
 Ax = 0
======================================================
"""


def ejecutar_modulo_vectores(modo_global: str = "fraccion") -> str:
    """Menú interactivo del Módulo 2: Vectores e Independencia Lineal."""
    modo = modo_global

    while True:
        print(LOGO_VECTORES)
        print(f" Formato numérico activo: [{modo.upper()}] (Fracciones / Decimales)")
        print("-" * 54)
        print(" 0. Ver Teoremas Clave del Módulo")
        print(" 1. Evaluar Independencia Lineal (L.I. / L.D.) [REQUISITO PROGRAMA 4]")
        print(" 2. Evaluar Combinación Lineal (b ∈ Gen{v₁ ... vₖ})")
        print(" 3. Operaciones Básicas entre Vectores (Suma, Resta, Escalar, Producto Punto)")
        print(" 4. Cargar Ejemplos Predefinidos de Clase")
        print(" 5. Cambiar Formato Numérico (Fracción ↔ Decimal)")
        print(" 6. Volver al Menú Principal")
        print("-" * 54)

        opcion = input("Seleccione una opción [0-6]: ").strip()

        if opcion == "0":
            print(teoremas_vectores())
            pausar()

        elif opcion == "1":
            print("\n--- EVALUACIÓN DE INDEPENDENCIA LINEAL EN ℝⁿ ---")
            k = leer_entero_positivo("Ingrese cantidad de vectores (k) [1-10]: ", 1, 10)
            n = leer_entero_positivo("Ingrese dimensión de los vectores (n) [1-10]: ", 1, 10)

            print(f"\nIngrese las componentes de cada vector en ℝ{a_subindice(n)}:")
            print("  (Acepta enteros, decimales '0.5' o fracciones '1/2', '-3/4')")

            vectores: List[Vector] = []
            for j in range(k):
                nom = f"v{a_subindice(j+1)}"
                print(f"\n>> Vector {nom}:")
                vec = []
                for i in range(n):
                    val = leer_numero(f"  Componente {i+1} de {nom}: ")
                    vec.append(val)
                vectores.append(vec)

            _evaluar_y_mostrar_independencia(vectores, modo)
            pausar()

        elif opcion == "2":
            print("\n--- EVALUACIÓN DE COMBINACIÓN LINEAL (b ∈ Gen{v₁ ... vₖ}) ---")
            k = leer_entero_positivo("Ingrese cantidad de vectores generadores (k) [1-10]: ", 1, 10)
            n = leer_entero_positivo("Ingrese dimensión de los vectores (n) [1-10]: ", 1, 10)

            vectores: List[Vector] = []
            for j in range(k):
                nom = f"v{a_subindice(j+1)}"
                print(f"\n>> Vector generador {nom}:")
                vec = [leer_numero(f"  Componente {i+1} de {nom}: ") for i in range(n)]
                vectores.append(vec)

            print("\n>> Vector objetivo b:")
            b = [leer_numero(f"  Componente {i+1} de b: ") for i in range(n)]

            _evaluar_y_mostrar_comb_lineal(vectores, b, modo)
            pausar()

        elif opcion == "3":
            _menu_operaciones_basicas_vectores(modo)

        elif opcion == "4":
            print("\n--- EJEMPLOS PREDEFINIDOS DE INDEPENDENCIA LINEAL ---")
            print(" 1. Diapositiva 12: v₁=[1,-2,3], v₂=[2,-2,0], v₃=[0,1,7] (Linealmente Independientes)")
            print(" 2. Diapositiva 15: v₁=[1,-3,0], v₂=[3,0,4], v₃=[11,-6,12] (Linealmente Dependientes)")
            print(" 3. Diapositiva 20: v₁=[3,1], v₂=[6,2] (L.D. por múltiplos escalares)")
            print(" 4. Diapositiva 22: 4 vectores en ℝ³ (L.D. por teorema p > n)")
            print(" 5. Diapositiva 22: Conjunto con vector cero (L.D.)")
            sub_op = input("Seleccione ejemplo [1-5]: ").strip()

            if sub_op == "1":
                vecs = [[1.0, -2.0, 3.0], [2.0, -2.0, 0.0], [0.0, 1.0, 7.0]]
            elif sub_op == "2":
                vecs = [[1.0, -3.0, 0.0], [3.0, 0.0, 4.0], [11.0, -6.0, 12.0]]
            elif sub_op == "3":
                vecs = [[3.0, 1.0], [6.0, 2.0]]
            elif sub_op == "4":
                vecs = [[1.0, 7.0, 6.0], [0.0, 0.0, 9.0], [3.0, 1.0, 5.0], [4.0, 1.0, 8.0]]
            else:
                vecs = [[2.0, 3.0, 5.0], [0.0, 0.0, 0.0], [1.0, 1.0, 8.0]]

            print("\nVectores del ejemplo cargado:")
            for idx, v in enumerate(vecs, 1):
                v_str = "[" + ", ".join(formatear_numero(x, modo) for x in v) + "]ᵀ"
                print(f"  v{a_subindice(idx)} = {v_str}")

            print("\nEvaluando con reducción por filas:")
            _evaluar_y_mostrar_independencia(vecs, modo)
            pausar()

        elif opcion == "5":
            modo = "decimal" if modo == "fraccion" else "fraccion"
            print(f"\n  ✓ Formato cambiado a: [{modo.upper()}]")
            pausar()

        elif opcion == "6":
            break
        else:
            print("  ⚠️ Opción no válida. Intente de nuevo.")

    return modo


def _evaluar_y_mostrar_independencia(vectores: List[Vector], modo: str) -> None:
    """Implementa el requerimiento central del Programa 4:
    Construye Ax = 0, aplica reducción por filas, cuenta pivotes y variables libres,
    y emite veredicto teórico explícito (L.I. o L.D.).
    """
    k = len(vectores)
    n = len(vectores[0])

    print("\n" + "=" * 60)
    print(" REQUERIMIENTO DEL PROGRAMA 4: INDEPENDENCIA LINEAL")
    print("=" * 60)

    # 1. Vectores de entrada
    print(f"\n• Conjunto de {k} vectores en ℝ{a_subindice(n)}:")
    for j, vec in enumerate(vectores):
        v_str = "[" + ", ".join(formatear_numero(x, modo) for x in vec) + "]ᵀ"
        print(f"    v{a_subindice(j+1)} = {v_str}")

    # 2. Matriz A con vectores como columnas
    matriz_a = [[vectores[j][i] for j in range(k)] for i in range(n)]
    print(f"\n--- 1. MATRIZ DE COLUMNAS A ({n} filas × {k} columnas) ---")
    imprimir_matriz(matriz_a, modo)

    # 3. Construir sistema homogéneo Ax = 0
    matriz_homogenea = [fila + [0.0] for fila in matriz_a]
    print("\n--- 2. SISTEMA HOMOGÉNEO A x = 0 (Matriz Aumentada [A | 0]) ---")
    print("Ecuación vectorial: c₁v₁ + c₂v₂ + ... + cₖvₖ = 0̄")
    imprimir_matriz_aumentada(matriz_homogenea, modo)

    # 4. Reducción por filas (Gauss-Jordan)
    res = evaluar_independencia_lineal(vectores, modo=modo)

    if res.pasos_gauss and len(res.pasos_gauss) > 1:
        print("\n--- 3. PROCESO DE REDUCCIÓN POR FILAS PASO A PASO ---")
        for idx, paso in enumerate(res.pasos_gauss[1:], 1):
            print(f">> Paso {idx}: {paso.descripcion}")
            imprimir_matriz_aumentada(paso.matriz_estado, modo)

    # 5. Salida requerida: Matriz reducida
    print("\n--- 4. FORMA ESCALONADA REDUCIDA (RREF) ---")
    imprimir_matriz_aumentada(res.matriz_rref, modo)

    # 6. Conteo de pivotes y variables libres
    pivotes = 0
    for fila in res.matriz_rref:
        for c in range(min(k, len(fila) - 1)):
            if abs(fila[c]) > 1e-10:
                pivotes += 1
                break
    variables_libres = k - pivotes

    print("\n--- 5. CONTEO DE PIVOTES Y VARIABLES LIBRES ---")
    print(f"  • Cantidad de columnas (vectores k):  {k}")
    print(f"  • Número de posiciones pivote:        {pivotes}")
    print(f"  • Número de variables libres:         {variables_libres}")

    # 7. Veredicto teórico explícito (L.I. o L.D.)
    print("\n" + "=" * 60)
    if res.es_linealmente_independiente:
        print("  VEREDICTO TEÓRICO: ✅ LINEALMENTE INDEPENDIENTE (L.I.)")
        print("=" * 60)
        print("  Justificación teórica:")
        print(f"  • Hay {pivotes} pivotes para las {k} columnas (rango completo en columnas).")
        print("  • No existen variables libres en el sistema homogéneo A·c = 0.")
        print("  • La única solución a c₁v₁ + c₂v₂ + ... + cₖvₖ = 0̄ es la trivial:")
        print("      c₁ = c₂ = ... = cₖ = 0.")
        print("  • Ningún vector del conjunto puede escribirse como combinación lineal de los otros.")
    else:
        print("  VEREDICTO TEÓRICO: ⚠️ LINEALMENTE DEPENDIENTE (L.D.)")
        print("=" * 60)
        print("  Justificación teórica:")
        print(f"  • El sistema tiene {variables_libres} variable(s) libre(s) (solo {pivotes} pivotes para {k} columnas).")
        print("  • La ecuación c₁v₁ + c₂v₂ + ... + cₖvₖ = 0̄ admite infinitas soluciones NO triviales.")
        if res.relacion_dependencia:
            print("\n  Relación de dependencia no trivial obtenida:")
            print(f"    {res.relacion_dependencia}")
        print("\n  " + res.explicacion.replace("\n", "\n  "))


def _evaluar_y_mostrar_comb_lineal(vectores: List[Vector], b: Vector, modo: str) -> None:
    """Evalúa si b es combinación lineal de los vectores dados."""
    res = evaluar_combinacion_lineal(vectores, b, modo=modo)
    print("\n--- MATRIZ AUMENTADA INICIAL [v₁ ... vₖ | b] ---")
    imprimir_matriz_aumentada(res.matriz_aumentada_inicial, modo)

    if res.pasos_gauss and len(res.pasos_gauss) > 1:
        print("\n--- PROCESO DE RESOLUCIÓN (GAUSS-JORDAN) ---")
        for idx, paso in enumerate(res.pasos_gauss[1:], 1):
            print(f">> Paso {idx}: {paso.descripcion}")
            imprimir_matriz_aumentada(paso.matriz_estado, modo)

    print("\n--- MATRIZ EN FORMA ESCALONADA REDUCIDA (RREF) ---")
    imprimir_matriz_aumentada(res.matriz_rref, modo)

    print("\n--- DIAGNÓSTICO ---")
    if res.es_combinacion:
        print("  🟢 SÍ ES COMBINACIÓN LINEAL.")
        if res.pesos is not None:
            terminos = [f"({formatear_numero(p, modo)})·v{a_subindice(i+1)}" for i, p in enumerate(res.pesos)]
            print(f"  Ecuación: b = {' + '.join(terminos)}")
            print("  Escalares:")
            for i, p in enumerate(res.pesos, 1):
                print(f"    c{a_subindice(i)} = {formatear_numero(p, modo)}")
        else:
            print("  Existen infinitas combinaciones posibles.")
    else:
        print("  🔴 NO ES COMBINACIÓN LINEAL.")
        print("  El sistema es inconsistente (surge una contradicción 0 = k con k ≠ 0).")


def _menu_operaciones_basicas_vectores(modo: str) -> None:
    """Submenú de operaciones básicas entre vectores."""
    print("\n--- OPERACIONES BÁSICAS ENTRE VECTORES ---")
    n = leer_entero_positivo("Dimensión de los vectores (n) [1-10]: ", 1, 10)
    print("\nIngrese vector u:")
    u = [leer_numero(f"  u[{i+1}]: ") for i in range(n)]
    print("\nIngrese vector v:")
    v = [leer_numero(f"  v[{i+1}]: ") for i in range(n)]

    u_str = "[" + ", ".join(formatear_numero(x, modo) for x in u) + "]ᵀ"
    v_str = "[" + ", ".join(formatear_numero(x, modo) for x in v) + "]ᵀ"

    print("\n1. Suma (u + v):")
    suma = sumar_vectores(u, v)
    print("   u + v = [" + ", ".join(formatear_numero(x, modo) for x in suma) + "]ᵀ")

    print("\n2. Resta (u - v):")
    resta = restar_vectores(u, v)
    print("   u - v = [" + ", ".join(formatear_numero(x, modo) for x in resta) + "]ᵀ")

    print("\n3. Producto Punto (u · v):")
    pp = producto_punto(u, v)
    print(f"   u · v = {formatear_numero(pp, modo)}")

    c = leer_numero("\nIngrese escalar c para calcular c·u: ")
    cu = multiplicar_vector_escalar(c, u)
    c_fmt = formatear_numero(c, modo)
    print(f"   {c_fmt} · u = [" + ", ".join(formatear_numero(x, modo) for x in cu) + "]ᵀ")
    pausar()
