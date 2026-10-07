"""
UNIVERSIDAD AMERICANA (UAM)
Facultad de Ingeniería y Arquitectura (FIA)
Asignatura: Álgebra Lineal (MTM0120)

PROGRAMA PRINCIPAL: main.py
Punto de entrada de PyMatrix integrado con modulos/modulo_matrices.py.
Contiene la interfaz de usuario interactiva por consola con menú de operaciones matriciales,
soporte para entrada de matrices fraccionarias/decimales, ejemplos didácticos automáticos
y documentación matemática teórica integrada dinámicamente en el resultado de cada ejercicio.
"""

import sys
import os
from typing import List, Tuple, Optional, Any
from fractions import Fraction

# Asegurar codificación UTF-8 en salida estándar para caracteres matemáticos y bordes Unicode
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Asegurar que el directorio raíz del proyecto esté en el PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from modulos.modulo_matrices import (
    MatrizF, parsear_fraccion, crear_matriz, copiar_matriz, matriz_identidad,
    son_matrices_iguales, matriz_a_cadena,
    sumar_matrices, restar_matrices, multiplicar_escalar,
    multiplicar_matrices, multiplicar_matrices_explicado, trasponer_matriz,
    determinante_cofactores, determinante_sarrus, determinante_triangulacion,
    inversa_gauss_jordan, inversa_adjunta,
    verificar_propiedad_inversa_de_inversa, verificar_propiedad_inversa_del_producto,
    verificar_propiedad_inversa_de_traspuesta, verificar_propiedad_determinante_de_inversa,
    verificar_propiedades_operaciones_fila_det, verificar_propiedad_matriz_triangular,
    analizar_suma_matrices, analizar_resta_matrices, analizar_escalar_matriz,
    analizar_producto_matricial, analizar_transposicion_matriz
)


# =============================================================================
# FUNCIONES AUXILIARES DE ENTRADA Y FORMATEO POR CONSOLA
# =============================================================================

def limpiar_pantalla():
    """Imprime una separación visual limpia entre opciones."""
    print("\n" + "═" * 78 + "\n")


def pausar():
    """Pausa la ejecución esperando que el usuario presione ENTER."""
    input("\nPresione [ENTER] para regresar al menú principal...")


def leer_entero(mensaje: str, min_val: int = 1, max_val: int = 10, valor_default: Optional[int] = None) -> int:
    """Solicita un número entero dentro de un rango con validación continua."""
    def_str = f" [por defecto {valor_default}]" if valor_default is not None else ""
    while True:
        try:
            texto = input(f"{mensaje}{def_str}: ").strip()
            if not texto and valor_default is not None:
                return valor_default
            val = int(texto)
            if min_val <= val <= max_val:
                return val
            print(f"⚠️ Por favor ingrese un número entre {min_val} y {max_val}.")
        except ValueError:
            print("⚠️ Entrada inválida. Debe ser un número entero.")


def leer_matriz_consola(nombre: str, filas: int, columnas: int) -> MatrizF:
    """Permite ingresar los elementos de una matriz fila por fila."""
    print(f"\n>> Ingrese los valores para la matriz {nombre} ({filas} × {columnas}):")
    print("   (Puede escribir enteros como '3', fracciones como '1/2' o '-3/4', o decimales como '0.5').")
    print("   Formato: Ingrese los valores de cada fila separados por espacios.")
    
    matriz: List[List[Fraction]] = []
    for i in range(filas):
        while True:
            try:
                linea = input(f"   Fila {i + 1} ({columnas} valores): ").strip()
                partes = linea.split()
                if len(partes) != columnas:
                    print(f"   ⚠️ Se esperaban {columnas} valores, pero ingresó {len(partes)}. Intente de nuevo.")
                    continue
                fila_vals = [parsear_fraccion(p) for p in partes]
                matriz.append(fila_vals)
                break
            except Exception as e:
                print(f"   ⚠️ Error al interpretar los valores: {e}. Intente de nuevo.")
    return matriz


def seleccionar_o_ejemplo_matriz(
    nombre: str, filas: int, columnas: int, ejemplo_default: List[List[Any]]
) -> MatrizF:
    """Ofrece al usuario la opción de cargar una matriz de ejemplo o ingresarla manualmente."""
    print(f"\nConfiguración para matriz {nombre} ({filas}×{columnas}):")
    print(f"  [1] Usar ejemplo didáctico precargado")
    print(f"  [2] Ingresar valores manualmente")
    opc = input("  Seleccione opción (1/2, default 1): ").strip()
    if opc == "2":
        return leer_matriz_consola(nombre, filas, columnas)
    else:
        print(f"  ✓ Matriz {nombre} cargada con valores de ejemplo:")
        M = crear_matriz(ejemplo_default)
        print(matriz_a_cadena(M))
        return M


# =============================================================================
# MANEJADORES DE CADA OPCIÓN DEL MENÚ CON DOCUMENTACIÓN MATEMÁTICA CONTEXTUAL
# =============================================================================

def opcion_1_suma():
    limpiar_pantalla()
    print("=== [1] SUMA DE MATRICES (A + B) ===")
    m = leer_entero("Ingrese número de filas m", 1, 6, 2)
    n = leer_entero("Ingrese número de columnas n", 1, 6, 2)

    A = seleccionar_o_ejemplo_matriz("A", m, n, [[1, 2], [3, 4]])
    B = seleccionar_o_ejemplo_matriz("B", m, n, [[5, -1], [0, 2]])

    C = sumar_matrices(A, B)

    print("\nMatriz A:")
    print(matriz_a_cadena(A))
    print("\nMatriz B:")
    print(matriz_a_cadena(B))
    print("\nResultado C = A + B:")
    print(matriz_a_cadena(C))

    analisis = analizar_suma_matrices(A, B, C)
    print("\n" + "\n".join(analisis))
    pausar()


def opcion_2_resta():
    limpiar_pantalla()
    print("=== [2] RESTA DE MATRICES (A - B) ===")
    m = leer_entero("Ingrese número de filas m", 1, 6, 2)
    n = leer_entero("Ingrese número de columnas n", 1, 6, 2)

    A = seleccionar_o_ejemplo_matriz("A", m, n, [[5, 3], [7, 9]])
    B = seleccionar_o_ejemplo_matriz("B", m, n, [[2, 1], [4, 6]])

    C = restar_matrices(A, B)

    print("\nMatriz A:")
    print(matriz_a_cadena(A))
    print("\nMatriz B:")
    print(matriz_a_cadena(B))
    print("\nResultado C = A - B:")
    print(matriz_a_cadena(C))

    analisis = analizar_resta_matrices(A, B, C)
    print("\n" + "\n".join(analisis))
    pausar()


def opcion_3_multiplicacion_escalar():
    limpiar_pantalla()
    print("=== [3] MULTIPLICACIÓN POR UN ESCALAR (c · A) ===")
    m = leer_entero("Ingrese número de filas m", 1, 6, 2)
    n = leer_entero("Ingrese número de columnas n", 1, 6, 3)

    c_txt = input("Ingrese el escalar c (ej. 3, -2, 1/2): ").strip() or "3"
    c_val = parsear_fraccion(c_txt)

    A = seleccionar_o_ejemplo_matriz("A", m, n, [[1, -2, 4], [0, 3, -1]])

    R = multiplicar_escalar(c_val, A)

    print(f"\nMatriz original A ({m}×{n}):")
    print(matriz_a_cadena(A))
    print(f"\nResultado ({c_val}) · A ({m}×{n}):")
    print(matriz_a_cadena(R))

    analisis = analizar_escalar_matriz(c_val, A, R)
    print("\n" + "\n".join(analisis))
    pausar()


def opcion_4_producto_matricial():
    limpiar_pantalla()
    print("=== [4] PRODUCTO MATRICIAL (A_m×n × B_n×p → C_m×p) ===")
    m = leer_entero("Filas de A (m)", 1, 6, 2)
    n = leer_entero("Columnas de A / Filas de B (n)", 1, 6, 3)
    p = leer_entero("Columnas de B (p)", 1, 6, 2)

    A = seleccionar_o_ejemplo_matriz("A", m, n, [[1, 2, -1], [3, 0, 4]])
    B = seleccionar_o_ejemplo_matriz("B", n, p, [[2, 1], [-1, 3], [0, 5]])

    detalle = multiplicar_matrices_explicado(A, B)
    print(f"\nMatriz A ({m}×{n}):")
    print(matriz_a_cadena(A))
    print(f"\nMatriz B ({n}×{p}):")
    print(matriz_a_cadena(B))
    print("\nDesglose posicional (Triple bucle anidado):")
    for paso in detalle.desglose_pasos:
        print(f"  {paso}")
    print(f"\nMatriz Producto Resultante C ({m}×{p}):")
    print(matriz_a_cadena(detalle.matriz_resultado))

    analisis = analizar_producto_matricial(A, B, detalle.matriz_resultado)
    print("\n" + "\n".join(analisis))
    pausar()


def opcion_5_transposicion():
    limpiar_pantalla()
    print("=== [5] TRANSPOSICIÓN DE MATRICES (Aᵀ) ===")
    m = leer_entero("Ingrese número de filas m", 1, 6, 2)
    n = leer_entero("Ingrese número de columnas n", 1, 6, 3)

    A = seleccionar_o_ejemplo_matriz("A", m, n, [[1, 2, 3], [4, 5, 6]])
    AT = trasponer_matriz(A)

    print(f"\nMatriz original A ({m}×{n}):")
    print(matriz_a_cadena(A))
    print(f"\nMatriz Transpuesta Aᵀ ({n}×{m}):")
    print(matriz_a_cadena(AT))

    analisis = analizar_transposicion_matriz(A, AT)
    print("\n" + "\n".join(analisis))
    pausar()


def opcion_6_determinante():
    limpiar_pantalla()
    print("=== [6] CÁLCULO DE DETERMINANTE ===")
    n = leer_entero("Ingrese orden de la matriz cuadrada n (n×n)", 1, 6, 3)

    if n == 3:
        ejemplo = [[1, 2, 3], [4, 5, 6], [7, 2, 9]]
    elif n == 2:
        ejemplo = [[3, -2], [4, 1]]
    else:
        ejemplo = [[1 if i == j else 0 for j in range(n)] for i in range(n)]

    A = seleccionar_o_ejemplo_matriz("A", n, n, ejemplo)
    print("\n" + "═" * 60)
    print(f"MATRIZ A ({n}×{n}):")
    print(matriz_a_cadena(A))
    print("═" * 60)

    # 1. Cofactores
    print("\n[MÉTODO 1: EXPANSIÓN POR COFACTORES (LAPLACE)]")
    det_cof, pasos_cof = determinante_cofactores(A)
    for p in pasos_cof:
        print(f"  {p}")
    print(f">> det(A) por Cofactores = {det_cof}")

    # 2. Sarrus (si es 3x3)
    if n == 3:
        print("\n[MÉTODO 2: REGLA DE SARRUS (EXCLUSIVO 3×3)]")
        det_sar, pasos_sar = determinante_sarrus(A)
        for p in pasos_sar:
            print(f"  {p}")
        print(f">> det(A) por Sarrus = {det_sar}")

    # 3. Triangulación
    print("\n[MÉTODO 3: REDUCCIÓN A MATRIZ TRIANGULAR]")
    det_tri, pasos_tri = determinante_triangulacion(A)
    for p in pasos_tri:
        print(f"  {p}")
    print(f">> det(A) por Triangulación = {det_tri}")

    es_inv = (det_cof != Fraction(0, 1))

    print("\n" + "─" * 70)
    print("📖 DOCUMENTACIÓN Y JUSTIFICACIÓN SEGÚN EL TEOREMA DE LA MATRIZ INVERTIBLE (TMI):")
    print(f"• Valor del determinante obtenido: det(A) = {det_cof}")
    if es_inv:
        print("• Diagnóstico de Invertibilidad: det(A) ≠ 0 → La matriz A ES INVERTIBLE (No Singular).")
        print("• Implicaciones Teóricas Fundamentales (TMI):")
        print(f"  1. Propiedad [c]: A posee exactamente {n} posiciones pivote (rango completo = {n}).")
        print("  2. Propiedad [e]: Las columnas de A forman un conjunto LINEALMENTE INDEPENDIENTE (L.I.).")
        print(f"  3. Propiedad [h]: Las columnas de A generan todo el espacio vectorial ℝ{n}.")
        print("  4. Para cualquier vector b ∈ ℝⁿ, la ecuación matricial Ax = b tiene SOLUCIÓN ÚNICA.")
        print("  5. El sistema homogéneo Ax = 0 tiene únicamente la solución trivial x = 0̄.")
    else:
        print("• Diagnóstico de Invertibilidad: det(A) = 0 → La matriz A ES SINGULAR (No Invertible).")
        print("• Implicaciones Teóricas Fundamentales (TMI):")
        print(f"  1. Propiedad [c]: A tiene menos de {n} pivotes (rango < {n}).")
        print("  2. Propiedad [e]: Las columnas de A son LINEALMENTE DEPENDIENTES (L.D.).")
        print(f"  3. Propiedad [h]: Las columnas de A NO generan ℝ{n}.")
        print("  4. El sistema homogéneo Ax = 0 posee soluciones no triviales (infinitas soluciones).")
        print("  5. NO existe matriz inversa A⁻¹.")
    print("─" * 70)
    pausar()


def opcion_7_inversa_gauss_jordan():
    limpiar_pantalla()
    print("=== [7] INVERSA POR GAUSS-JORDAN ([A | I] → [I | A⁻¹]) ===")
    n = leer_entero("Orden de la matriz cuadrada n (n×n)", 1, 6, 3)

    ejemplo = [[1, 2, 0], [-1, 3, 2], [2, 0, -1]]
    A = seleccionar_o_ejemplo_matriz("A", n, n, ejemplo)

    res = inversa_gauss_jordan(A)
    print("\nDESARROLLO PASO A PASO:")
    for paso in res.pasos:
        print(f"  {paso}")

    print("\n" + "─" * 70)
    print("📖 DOCUMENTACIÓN Y JUSTIFICACIÓN MATEMÁTICA DEL EJERCICIO:")
    if res.es_invertible and res.matriz_inversa is not None:
        print(f"• Rango Completo: Se encontraron {n} pivotes en la reducción por filas.")
        print("• Fundamento de Gauss-Jordan: Si [A | I] se reduce por operaciones elementales a [I | B],")
        print("  entonces B = A⁻¹ debido a que la sucesión de matrices elementales E_k...E₁ A = I implica")
        print("  que E_k...E₁ = A⁻¹.")
        print("• Justificación de la Comprobación: Por definición formal de elemento neutro e inverso,")
        print("  una matriz inversa debe verificar idénticamente A · A⁻¹ = A⁻¹ · A = Iₙ.")
        print(f"  Resultado de la comprobación: {'✓ EXITOSA (Identidad perfecta)' if res.comprobacion_identidad else '✗ Falló'}.")
    else:
        print("• Detección de Singularidad: El algoritmo se detuvo porque al menos una columna carece de pivote.")
        print(f"• Por el Teorema de la Matriz Invertible (inciso c), una matriz con rango < {n} no es equivalente")
        print("  por filas a la matriz identidad Iₙ, por lo cual es SINGULAR y no admite matriz inversa.")
    print("─" * 70)
    pausar()


def opcion_8_inversa_adjunta():
    limpiar_pantalla()
    print("=== [8] INVERSA POR MATRIZ ADJUNTA: A⁻¹ = (1/det(A)) · adj(A) ===")
    n = leer_entero("Orden de la matriz cuadrada n (n×n)", 1, 6, 3)

    ejemplo = [[1, 2, 0], [-1, 3, 2], [2, 0, -1]]
    A = seleccionar_o_ejemplo_matriz("A", n, n, ejemplo)

    res = inversa_adjunta(A)
    print("\nDESARROLLO PASO A PASO:")
    for paso in res.pasos:
        print(f"  {paso}")

    print("\n" + "─" * 70)
    print("📖 DOCUMENTACIÓN Y JUSTIFICACIÓN MATEMÁTICA DEL EJERCICIO:")
    if res.es_invertible and res.matriz_inversa is not None:
        print("• Teorema de la Matriz Adjunta: Para toda matriz cuadrada A se cumple la identidad:")
        print("      A · adj(A) = det(A) · Iₙ")
        print("• Deducción de la Fórmula: Dado que det(A) ≠ 0, dividimos ambos miembros entre el escalar det(A):")
        print("      A · [ (1/det(A)) · adj(A) ] = Iₙ")
        print("  Demostrando rigurosamente que el factor derecho es la matriz inversa A⁻¹.")
        print("• Construcción: Cada entrada de la adjunta adj(A)[i,j] es el cofactor C[j,i] (transpuesta).")
        print(f"• Comprobación Automática: {'✓ Verificada A · A⁻¹ = Iₙ' if res.comprobacion_identidad else '✗ Error'}.")
    else:
        print("• Imposibilidad Matemática: det(A) = 0. La división entre cero es indefinida.")
        print("• En consecuencia, la ecuación A · adj(A) = 0 · Iₙ = 0 no permite aislar la inversa,")
        print("  confirmando que la matriz carece de inversa.")
    print("─" * 70)
    pausar()


def opcion_9_verificador_propiedades():
    limpiar_pantalla()
    print("=== [9] VERIFICADOR DE PROPIEDADES ALGEBRAICAS (SESIONES 10 Y 11) ===")
    print("Se verificarán sistemáticamente las 6 propiedades con justificación teórica para cada una:\n")
    
    n = leer_entero("Orden n para las matrices cuadradas A y B", 2, 4, 2)
    ejemplo_A = [[2, 1], [5, 3]] if n == 2 else [[1, 2, 0], [-1, 3, 2], [2, 0, -1]]
    ejemplo_B = [[1, 2], [3, 4]] if n == 2 else [[2, 0, 1], [1, 1, 0], [0, 3, 1]]

    A = seleccionar_o_ejemplo_matriz("A", n, n, ejemplo_A)
    B = seleccionar_o_ejemplo_matriz("B", n, n, ejemplo_B)

    print("\n" + "═" * 78)
    print("DOCUMENTACIÓN Y COMPROBACIÓN DINÁMICA DE PROPIEDADES")
    print("═" * 78)

    # 1. (A⁻¹)⁻¹ = A
    p1 = verificar_propiedad_inversa_de_inversa(A)
    print(f"\n1. {p1.nombre} [{p1.formula}]:")
    print(f"   • Teorema: La operación de inversión matricial es involutiva.")
    print(f"   • (A⁻¹)⁻¹ =\n{p1.lado_izquierdo_str}")
    print(f"   • A original =\n{p1.lado_derecho_str}")
    print(f"   • Veredicto: {'✓ SE CUMPLE IDENTICAMENTE' if p1.se_cumple else '✗ NO SE CUMPLE'}")

    # 2. (AB)⁻¹ = B⁻¹ A⁻¹
    p2 = verificar_propiedad_inversa_del_producto(A, B)
    print(f"\n2. {p2.nombre} [{p2.formula}]:")
    print(f"   • Teorema: La inversa de un producto invierte el orden de los factores.")
    print(f"   • Demostración: (AB)(B⁻¹ A⁻¹) = A(B B⁻¹)A⁻¹ = A(I)A⁻¹ = AA⁻¹ = I.")
    print(f"   • Lado Izquierdo (AB)⁻¹ =\n{p2.lado_izquierdo_str}")
    print(f"   • Lado Derecho B⁻¹ · A⁻¹ =\n{p2.lado_derecho_str}")
    print(f"   • Veredicto: {'✓ SE CUMPLE IDENTICAMENTE' if p2.se_cumple else '✗ NO SE CUMPLE'}")

    # 3. (Aᵀ)⁻¹ = (A⁻¹)ᵀ
    p3 = verificar_propiedad_inversa_de_traspuesta(A)
    print(f"\n3. {p3.nombre} [{p3.formula}]:")
    print(f"   • Teorema: La transposición conmuta con la inversión: Aᵀ(A⁻¹)ᵀ = (A⁻¹ A)ᵀ = Iᵀ = I.")
    print(f"   • Lado Izquierdo (Aᵀ)⁻¹ =\n{p3.lado_izquierdo_str}")
    print(f"   • Lado Derecho (A⁻¹)ᵀ =\n{p3.lado_derecho_str}")
    print(f"   • Veredicto: {'✓ SE CUMPLE IDENTICAMENTE' if p3.se_cumple else '✗ NO SE CUMPLE'}")

    # 4. det(A⁻¹) = 1 / det(A)
    p4 = verificar_propiedad_determinante_de_inversa(A)
    print(f"\n4. {p4.nombre} [{p4.formula}]:")
    print(f"   • Teorema: Puesto que det(A · A⁻¹) = det(I) = 1, y det(AB) = det(A)·det(B),")
    print("     se deduce algebraicamente que det(A) · det(A⁻¹) = 1 → det(A⁻¹) = 1 / det(A).")
    print(f"   • {p4.lado_izquierdo_str}  vs  {p4.lado_derecho_str}")
    print(f"   • Veredicto: {'✓ SE CUMPLE IDENTICAMENTE' if p4.se_cumple else '✗ NO SE CUMPLE'}")

    # 5. Operaciones de fila en det(A)
    p5_list = verificar_propiedades_operaciones_fila_det(A)
    print("\n5. Propiedades de Operaciones Elementales de Fila en det(A):")
    for p in p5_list:
        print(f"   • {p.nombre} [{p.formula}]:")
        print(f"     L.I.: {p.lado_izquierdo_str}  |  L.D.: {p.lado_derecho_str}")
        print(f"     Justificación: {p.explicacion}")
        print(f"     Estado: {'✓ VERIFICADA' if p.se_cumple else '✗ DISCREPANCIA'}")

    # 6. Matriz triangular
    p6 = verificar_propiedad_matriz_triangular(A)
    print(f"\n6. {p6.nombre} [{p6.formula}]:")
    print(f"   • Teorema: En una matriz triangular, todos los cofactores correspondientes a las celdas")
    print("     fuera de la diagonal principal contienen filas o columnas de ceros, de modo que el")
    print("     determinante se reduce estrictamente al producto de los elementos diagonales ∏ t_{ii}.")
    print(f"   • {p6.lado_izquierdo_str}  vs  {p6.lado_derecho_str}")
    print(f"   • Veredicto: {'✓ SE CUMPLE IDENTICAMENTE' if p6.se_cumple else '✗ NO SE CUMPLE'}")

    print("\n" + "═" * 78)
    print("✓ TODAS LAS PROPIEDADES DE LAS SESIONES 10 Y 11 FUERON DOCUMENTADAS Y VERIFICADAS.")
    print("═" * 78)
    pausar()


def opcion_10_abrir_gui():
    limpiar_pantalla()
    print("Iniciando la Calculadora Gráfica PyMatrix (CustomTkinter)...")
    try:
        from src.ui.app import App
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"⚠️ No se pudo iniciar la interfaz gráfica: {e}")
        pausar()


# =============================================================================
# MENÚ PRINCIPAL
# =============================================================================

def menu_principal():
    """Muestra el menú interactivo de 9 operaciones con justificación contextual."""
    while True:
        limpiar_pantalla()
        print("  ┌──────────────────────────────────────────────────────────────────┐")
        print("  │            PyMatrix — CALCULADORA DE ÁLGEBRA LINEAL              │")
        print("  ├──────────────────────────────────────────────────────────────────┤")
        print("  │   1. Suma de matrices (mismas dimensiones)                       │")
        print("  │   2. Resta de matrices (mismas dimensiones)                      │")
        print("  │   3. Multiplicación por un escalar                               │")
        print("  │   4. Producto matricial (A_m×n × B_n×p → C_m×p)                  │")
        print("  │   5. Transposición de matrices (Aᵀ)                              │")
        print("  │   6. Determinante (Cofactores, Sarrus 3×3, Triangulación)        │")
        print("  │   7. Inversa por Gauss-Jordan ([A | I] → [I | A⁻¹])              │")
        print("  │   8. Inversa por Matriz Adjunta (A⁻¹ = 1/det(A) · adj(A))        │")
        print("  │   9. Verificador de Propiedades (Sesiones 10 y 11)               │")
        print("  │  10. 🚀 Abrir Calculadora Gráfica (CustomTkinter)                │")
        print("  │   0. Salir del programa                                          │")
        print("  └──────────────────────────────────────────────────────────────────┘")
        
        opcion = input("  Seleccione una opción [0-10]: ").strip()
        
        if opcion == "1":
            opcion_1_suma()
        elif opcion == "2":
            opcion_2_resta()
        elif opcion == "3":
            opcion_3_multiplicacion_escalar()
        elif opcion == "4":
            opcion_4_producto_matricial()
        elif opcion == "5":
            opcion_5_transposicion()
        elif opcion == "6":
            opcion_6_determinante()
        elif opcion == "7":
            opcion_7_inversa_gauss_jordan()
        elif opcion == "8":
            opcion_8_inversa_adjunta()
        elif opcion == "9":
            opcion_9_verificador_propiedades()
        elif opcion == "10":
            opcion_10_abrir_gui()
        elif opcion == "0":
            print("\n¡Gracias por utilizar PyMatrix! Hasta pronto.\n")
            break
        else:
            print("⚠️ Opción no válida. Por favor elija un número entre 0 y 10.")
            pausar()


def main():
    """Función de arranque principal."""
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("--gui", "-g"):
        opcion_10_abrir_gui()
    else:
        menu_principal()


if __name__ == "__main__":
    main()
