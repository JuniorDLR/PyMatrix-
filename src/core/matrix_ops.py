"""
Módulo de Operaciones Matriciales Básicas y Ecuaciones Matriciales para PyMatrix.

Contiene la lógica matemática para:
1. Suma y resta de matrices A ± B (con validación de dimensiones m × n).
2. Multiplicación de una matriz por un escalar c · A.
3. Multiplicación de matrices A_m×n · B_n×p:
   - Validación de compatibilidad dimensional: columnas de A == filas de B.
   - Algoritmo estándar con triple bucle anidado for/for/for documentado paso a paso.
   - Generación de desgloses de cálculo posicional para fines didácticos e informe técnico.
4. Producto matriz-vector A · x (regla fila-vector y combinación lineal de columnas).
5. Resolución computacional de la ecuación matricial Ax = b mediante matriz aumentada [A | b].

RESTRICCIÓN DIDÁCTICA:
Implementado estrictamente con Python estándar (listas, bucles, condicionales).
Prohibido el uso de NumPy o SciPy.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional

from src.core.domain import (
    Matriz, formatear_numero, formatear_fraccion, a_subindice
)
from src.core.gauss import (
    resolver_gauss_jordan, copiar_matriz, PasoGauss,
    SolucionUnica, SolucionInfinita, SinSolucion, SolucionGeneral
)
from src.core.vectors import Vector


# =========================================================================
# 1. SUMA Y RESTA DE MATRICES
# =========================================================================

def validar_dimensiones_matrices_iguales(A: Matriz, B: Matriz, operacion: str = "operación") -> Tuple[int, int]:
    """Verifica que dos matrices tengan exactamente las mismas dimensiones m × n.
    
    Procedimiento algebraico:
    La adición y sustracción de matrices solo están definidas si ambas matrices
    tienen el mismo número de filas y el mismo número de columnas (A, B ∈ M_{m × n}(ℝ)).
    
    Raises:
        ValueError: Si alguna matriz está vacía o sus dimensiones difieren.
    """
    if not A or not A[0] or not B or not B[0]:
        raise ValueError("Las matrices no pueden estar vacías.")
    
    filas_A, cols_A = len(A), len(A[0])
    filas_B, cols_B = len(B), len(B[0])
    
    if filas_A != filas_B or cols_A != cols_B:
        raise ValueError(
            f"Error de dimensiones en {operacion}: La matriz A tiene tamaño {filas_A}×{cols_A} "
            f"y la matriz B tiene tamaño {filas_B}×{cols_B}. Para sumar o restar, "
            f"ambas deben tener idénticas dimensiones m × n."
        )
    return filas_A, cols_A


def sumar_matrices(A: Matriz, B: Matriz) -> Matriz:
    """Calcula la suma matricial C = A + B.
    
    Procedimiento algebraico:
    Dadas A, B ∈ M_{m × n}(ℝ), la matriz resultante C = A + B tiene entradas:
    C_{ij} = A_{ij} + B_{ij}  para todo 1 ≤ i ≤ m, 1 ≤ j ≤ n.
    Se suman los elementos correspondientes posición a posición.
    """
    m, n = validar_dimensiones_matrices_iguales(A, B, "suma matricial")
    C: Matriz = []
    for i in range(m):
        fila: List[float] = []
        for j in range(n):
            fila.append(round(A[i][j] + B[i][j], 9))
        C.append(fila)
    return C


def restar_matrices(A: Matriz, B: Matriz) -> Matriz:
    """Calcula la resta matricial C = A - B.
    
    Procedimiento algebraico:
    A - B = A + (-1)·B.
    C_{ij} = A_{ij} - B_{ij}  para todo 1 ≤ i ≤ m, 1 ≤ j ≤ n.
    Se resta cada elemento de B al correspondiente elemento de A.
    """
    m, n = validar_dimensiones_matrices_iguales(A, B, "resta matricial")
    C: Matriz = []
    for i in range(m):
        fila: List[float] = []
        for j in range(n):
            fila.append(round(A[i][j] - B[i][j], 9))
        C.append(fila)
    return C


# =========================================================================
# 2. MULTIPLICACIÓN POR UN ESCALAR
# =========================================================================

def multiplicar_matriz_escalar(c: float, A: Matriz) -> Matriz:
    """Calcula el producto de un escalar por una matriz C = c · A.
    
    Procedimiento algebraico:
    Dado c ∈ ℝ y A ∈ M_{m × n}(ℝ):
    (c · A)_{ij} = c · A_{ij}  para todo 1 ≤ i ≤ m, 1 ≤ j ≤ n.
    Cada entrada de la matriz se multiplica por el factor escalar c.
    """
    if not A or not A[0]:
        raise ValueError("La matriz no puede estar vacía.")
    
    m, n = len(A), len(A[0])
    C: Matriz = []
    for i in range(m):
        fila: List[float] = []
        for j in range(n):
            fila.append(round(c * A[i][j], 9))
        C.append(fila)
    return C


def combinacion_matrices(c_A: float, A: Matriz, c_B: float, B: Matriz, restar: bool = False) -> Matriz:
    """Calcula la combinación lineal de dos matrices C = c_A·A + c_B·B (o c_A·A - c_B·B si restar=True).
    
    Procedimiento algebraico:
    Dadas A, B ∈ M_{m × n}(ℝ) y escalares c_A, c_B ∈ ℝ:
    C_{ij} = c_A·A_{ij} ± c_B·B_{ij} para todo 1 ≤ i ≤ m, 1 ≤ j ≤ n.
    """
    m, n = validar_dimensiones_matrices_iguales(A, B, "combinación lineal matricial")
    signo = -1.0 if restar else 1.0
    C: Matriz = []
    for i in range(m):
        fila: List[float] = []
        for j in range(n):
            val = round(c_A * A[i][j] + signo * c_B * B[i][j], 9)
            fila.append(val)
        C.append(fila)
    return C



# =========================================================================
# 3. MULTIPLICACIÓN DE MATRICES (A_m×n · B_n×p)
# =========================================================================

@dataclass
class ResultadoMultiplicacionMatricial:
    """Almacena el resultado y el desglose paso a paso de la multiplicación A · B."""
    matriz_resultado: Matriz
    dimensiones_A: Tuple[int, int]
    dimensiones_B: Tuple[int, int]
    dimensiones_resultado: Tuple[int, int]
    desglose_pasos: List[str]


def multiplicar_matrices(A: Matriz, B: Matriz, modo: str = "fraccion") -> ResultadoMultiplicacionMatricial:
    """Calcula el producto matricial C = A · B de dimensiones (m × n) · (n × p) = (m × p).
    
    Procedimiento algebraico:
    1. Condición de Compatibilidad:
       El producto A · B está definido si y solo si el número de columnas de A
       es exactamente igual al número de filas de B (cols_A == filas_B = n).
    
    2. Regla de Producto Fila por Columna (Producto Punto):
       Cada entrada C_{ij} de la matriz producto resulta del producto escalar entre
       la fila i-ésima de A y la columna j-ésima de B:
       C_{ij} = ∑_{k=1}^{n} (A_{ik} · B_{kj}) = A_{i1}B_{1j} + A_{i2}B_{2j} + ... + A_{in}B_{nj}
    
    3. Explicación de la Lógica de Bucles Anidados:
       - Bucle exterior (i de 0 a m-1): Itera sobre cada fila de la matriz A.
       - Bucle intermedio (j de 0 a p-1): Itera sobre cada columna de la matriz B.
       - Bucle interior (k de 0 a n-1): Acumula la suma de productos de los elementos
         correspondientes de la fila i de A y la columna j de B.
    """
    if not A or not A[0] or not B or not B[0]:
        raise ValueError("Ninguna de las matrices puede estar vacía.")
    
    m = len(A)       # Filas de A
    n_A = len(A[0])  # Columnas de A
    n_B = len(B)     # Filas de B
    p = len(B[0])    # Columnas de B
    
    if n_A != n_B:
        raise ValueError(
            f"Incompatibilidad de dimensiones para multiplicación: A es {m}×{n_A} y B es {n_B}×{p}. "
            f"El número de columnas de A ({n_A}) debe ser igual al número de filas de B ({n_B})."
        )
    
    n = n_A
    C: Matriz = []
    desgloses: List[str] = []
    
    # Bucle i: Recorre las filas de la matriz A (tamaño m)
    for i in range(m):
        fila_C: List[float] = []
        # Bucle j: Recorre las columnas de la matriz B (tamaño p)
        for j in range(p):
            acumulador = 0.0
            terminos_texto: List[str] = []
            
            # Bucle k: Recorre los elementos compartidos de dimensión n
            for k in range(n):
                prod = A[i][k] * B[k][j]
                acumulador += prod
                a_str = formatear_numero(A[i][k], modo)
                b_str = formatear_numero(B[k][j], modo)
                terminos_texto.append(f"({a_str})·({b_str})")
            
            acumulador_redondeado = round(acumulador, 9)
            fila_C.append(acumulador_redondeado)
            
            # Formatear el desglose didáctico de la celda C[i+1, j+1]
            desglose_celda = (
                f"c{a_subindice(i+1)}{a_subindice(j+1)} = " +
                " + ".join(terminos_texto) +
                f" = {formatear_numero(acumulador_redondeado, modo)}"
            )
            desgloses.append(desglose_celda)
        C.append(fila_C)
        
    return ResultadoMultiplicacionMatricial(
        matriz_resultado=C,
        dimensiones_A=(m, n),
        dimensiones_B=(n, p),
        dimensiones_resultado=(m, p),
        desglose_pasos=desgloses
    )


# =========================================================================
# 4. PRODUCTO MATRIZ-VECTOR (A · x)
# =========================================================================

@dataclass
class ResultadoProductoMatrizVector:
    """Resultado del cálculo Ax."""
    vector_resultado: Vector
    desglose_filas: List[str]
    combinacion_columnas: str


def multiplicar_matriz_vector(A: Matriz, x: Vector, modo: str = "fraccion") -> ResultadoProductoMatrizVector:
    """Calcula el producto matriz-vector b = A · x.
    
    Procedimiento algebraico:
    Si A es una matriz m × n con columnas a₁, a₂, ..., aₙ y x ∈ ℝⁿ, entonces:
    1. Regla de Combinación Lineal de Columnas:
       Ax = x₁a₁ + x₂a₂ + ... + xₙaₙ
    2. Regla Fila-Vector:
       La i-ésima entrada de Ax es el producto punto de la fila i de A con el vector x:
       (Ax)ᵢ = ∑_{j=1}^{n} (A_{ij} · xⱼ).
    """
    if not A or not A[0]:
        raise ValueError("La matriz A no puede estar vacía.")
    if not x:
        raise ValueError("El vector x no puede estar vacío.")
    
    m = len(A)
    n = len(A[0])
    
    if len(x) != n:
        raise ValueError(
            f"Dimensión incompatible en A·x: La matriz A tiene {n} columnas, "
            f"pero el vector x tiene {len(x)} entradas. Se requiere x ∈ ℝ{a_subindice(n)}."
        )
    
    resultado: Vector = []
    desgloses_filas: List[str] = []
    
    for i in range(m):
        suma_fila = 0.0
        terminos: List[str] = []
        for j in range(n):
            prod = A[i][j] * x[j]
            suma_fila += prod
            terminos.append(f"({formatear_numero(A[i][j], modo)})·({formatear_numero(x[j], modo)})")
        
        suma_redondeada = round(suma_fila, 9)
        resultado.append(suma_redondeada)
        desgloses_filas.append(
            f"Fila {i+1}: " + " + ".join(terminos) + f" = {formatear_numero(suma_redondeada, modo)}"
        )
    
    # Expresión como combinación de columnas: x₁a₁ + ... + xₙaₙ
    partes_cols: List[str] = []
    for j in range(n):
        xj_str = formatear_numero(x[j], modo)
        partes_cols.append(f"({xj_str})·a{a_subindice(j+1)}")
    comb_columnas = " + ".join(partes_cols)
    
    return ResultadoProductoMatrizVector(
        vector_resultado=resultado,
        desglose_filas=desgloses_filas,
        combinacion_columnas=comb_columnas
    )


# =========================================================================
# 5. ECUACIONES MATRICIALES (Ax = b)
# =========================================================================

@dataclass
class ResultadoEcuacionMatricial:
    """Resultado de la resolución del sistema Ax = b."""
    clasificacion: str
    es_consistente: bool
    solucion_unica: Optional[Vector]
    solucion_general: Optional[SolucionGeneral]
    matriz_aumentada: Matriz
    matriz_rref: Matriz
    pasos_gauss: List[PasoGauss]
    resumen_explicativo: str


def resolver_ecuacion_matricial(A: Matriz, b: Vector, modo: str = "fraccion") -> ResultadoEcuacionMatricial:
    """Evalúa y resuelve computacionalmente la ecuación matricial Ax = b.
    
    Teorema Fundamental de Álgebra Lineal:
    Si A es una matriz m × n con columnas a₁, ..., aₙ y b ∈ ℝᵐ,
    la ecuación matricial:
        Ax = b
    tiene exactamente el mismo conjunto solución que la ecuación vectorial:
        x₁a₁ + x₂a₂ + ... + xₙaₙ = b
    y a la vez, tiene el mismo conjunto solución que el sistema lineal cuya matriz aumentada es:
        [ a₁  a₂  ...  aₙ | b ] = [ A | b ]
    
    Procedimiento:
    1. Valida dimensiones: filas de A deben coincidir con la longitud de b (b ∈ ℝᵐ).
    2. Forma la matriz aumentada [A | b] de dimensiones m × (n + 1).
    3. Aplica Gauss-Jordan para clasificar el sistema y obtener la solución.
    """
    if not A or not A[0]:
        raise ValueError("La matriz A no puede estar vacía.")
    if not b:
        raise ValueError("El vector b no puede estar vacío.")
    
    m = len(A)
    n = len(A[0])
    
    if len(b) != m:
        raise ValueError(
            f"Dimensión incompatible en Ax = b: La matriz A tiene {m} filas, "
            f"pero el vector b tiene dimensión {len(b)}. El vector b debe pertenecer a ℝ{a_subindice(m)}."
        )
    
    # Construcción de la matriz aumentada [A | b]
    matriz_aumentada: Matriz = []
    for i in range(m):
        fila = A[i][:] + [b[i]]
        matriz_aumentada.append(fila)
    
    pasos, res, sol_gen = resolver_gauss_jordan(matriz_aumentada)
    matriz_rref = sol_gen.matriz_rref if sol_gen else pasos[-1].matriz_estado
    
    if isinstance(res, SinSolucion):
        explicacion = (
            "La ecuación matricial Ax = b es INCONSISTENTE (No tiene solución).\n"
            "Justificación: Al escalonar la matriz [A | b], se genera una fila contradictoria [0 ... 0 | k] con k ≠ 0.\n"
            "El vector b no se encuentra en el espacio columna generado por las columnas de A."
        )
        return ResultadoEcuacionMatricial(
            clasificacion="Inconsistente (Sin Solución)",
            es_consistente=False,
            solucion_unica=None,
            solucion_general=None,
            matriz_aumentada=matriz_aumentada,
            matriz_rref=matriz_rref,
            pasos_gauss=pasos,
            resumen_explicativo=explicacion
        )
    elif isinstance(res, SolucionUnica):
        sol_vector = res.variables
        lineas_sol = [f"x{a_subindice(j+1)} = {formatear_numero(sol_vector[j], modo)}" for j in range(n)]
        explicacion = (
            "La ecuación matricial Ax = b tiene SOLUCIÓN ÚNICA (Consistente Determinado).\n"
            "Vector solución x ∈ ℝⁿ:\n  x = [" + ", ".join([formatear_numero(val, modo) for val in sol_vector]) + "]ᵀ\n\n"
            "Valores de las incógnitas:\n  " + "\n  ".join(lineas_sol)
        )
        return ResultadoEcuacionMatricial(
            clasificacion="Consistente Determinado (Solución Única)",
            es_consistente=True,
            solucion_unica=sol_vector,
            solucion_general=sol_gen,
            matriz_aumentada=matriz_aumentada,
            matriz_rref=matriz_rref,
            pasos_gauss=pasos,
            resumen_explicativo=explicacion
        )
    else:  # SolucionInfinita
        vars_libres = res.variables_libres
        lineas_param = sol_gen.a_strings(n, modo=modo) if sol_gen else []
        explicacion = (
            f"La ecuación matricial Ax = b tiene INFINITAS SOLUCIONES (Consistente Indeterminado).\n"
            f"Posee {len(vars_libres)} variable(s) libre(s) como parámetro(s).\n\n"
            "Solución general parametrizada:\n  " + "\n  ".join(lineas_param)
        )
        return ResultadoEcuacionMatricial(
            clasificacion="Consistente Indeterminado (Infinitas Soluciones)",
            es_consistente=True,
            solucion_unica=None,
            solucion_general=sol_gen,
            matriz_aumentada=matriz_aumentada,
            matriz_rref=matriz_rref,
            pasos_gauss=pasos,
            resumen_explicativo=explicacion
        )


# =========================================================================
# 6. PROPIEDADES DEL PRODUCTO MATRIZ - VECTOR Ax (TEOREMA DE LINEALIDAD)
# =========================================================================

@dataclass
class VerificacionPropiedadAditivaAx:
    """Demostración y verificación paso a paso de A(u + v) = Au + Av."""
    u: Vector
    v: Vector
    u_mas_v: Vector
    lado_izq_A_u_mas_v: Vector
    Au: Vector
    Av: Vector
    lado_der_Au_mas_Av: Vector
    se_cumple: bool
    desglose_pasos: List[str]


@dataclass
class VerificacionPropiedadEscalarAx:
    """Demostración y verificación paso a paso de A(cu) = c(Au)."""
    c: float
    u: Vector
    c_u: Vector
    lado_izq_A_cu: Vector
    Au: Vector
    lado_der_c_Au: Vector
    se_cumple: bool
    desglose_pasos: List[str]


def verificar_propiedad_aditiva_ax(A: Matriz, u: Vector, v: Vector, modo: str = "fraccion") -> VerificacionPropiedadAditivaAx:
    """Verifica paso a paso la propiedad distributiva: A(u + v) = Au + Av.
    
    Teorema: Si A es una matriz m × n, y u, v son vectores en ℝⁿ:
      Lado Izquierdo (L.I.): Primero suma u + v, luego multiplica A · (u + v).
      Lado Derecho   (L.D.): Multiplica A·u y A·v por separado, y luego suma Au + Av.
      Conclusión: L.I. == L.D.
    """
    if not A or not A[0]:
        raise ValueError("La matriz A no puede estar vacía.")
    m = len(A)
    n = len(A[0])
    if len(u) != n or len(v) != n:
        raise ValueError(
            f"Dimensión incompatible: La matriz A tiene {n} columnas, pero u tiene {len(u)} componentes "
            f"y v tiene {len(v)} componentes. Ambos vectores deben pertenecer a ℝ{a_subindice(n)}."
        )

    # 1. Lado Izquierdo: A(u + v)
    u_mas_v = [round(ui + vi, 9) for ui, vi in zip(u, v)]
    res_A_u_mas_v = multiplicar_matriz_vector(A, u_mas_v, modo=modo)
    lado_izq = res_A_u_mas_v.vector_resultado

    # 2. Lado Derecho: Au + Av
    res_Au = multiplicar_matriz_vector(A, u, modo=modo)
    res_Av = multiplicar_matriz_vector(A, v, modo=modo)
    lado_der = [round(au + av, 9) for au, av in zip(res_Au.vector_resultado, res_Av.vector_resultado)]

    # 3. Comprobación de igualdad numérica
    se_cumple = all(abs(izq - der) < 1e-7 for izq, der in zip(lado_izq, lado_der))

    # 4. Desglose detallado
    pasos: List[str] = []
    pasos.append("======================================================================")
    pasos.append("  PROPIEDAD a) DEL PRODUCTO MATRIZ-VECTOR: A(u + v) = Au + Av")
    pasos.append("======================================================================\n")
    pasos.append(f"Teorema: Si A es una matriz de {m}×{n} y u, v son vectores en ℝ{a_subindice(n)},")
    pasos.append("la multiplicación matriz-vector se distribuye sobre la suma de vectores.\n")
    
    pasos.append("--- [1] DESARROLLO DEL LADO IZQUIERDO: A(u + v) ---")
    u_str = "[" + ", ".join([formatear_numero(x, modo) for x in u]) + "]ᵀ"
    v_str = "[" + ", ".join([formatear_numero(x, modo) for x in v]) + "]ᵀ"
    u_mas_v_str = "[" + ", ".join([formatear_numero(x, modo) for x in u_mas_v]) + "]ᵀ"
    pasos.append(f"  Vector u = {u_str}")
    pasos.append(f"  Vector v = {v_str}")
    pasos.append("  Paso 1.1: Sumar vectores w = u + v componente a componente:")
    for i, (ui, vi, wi) in enumerate(zip(u, v, u_mas_v)):
        pasos.append(f"    w{a_subindice(i+1)} = ({formatear_numero(ui, modo)}) + ({formatear_numero(vi, modo)}) = {formatear_numero(wi, modo)}")
    pasos.append(f"  Vector suma (u + v) = {u_mas_v_str}\n")
    
    pasos.append("  Paso 1.2: Multiplicar A por el vector suma (u + v):")
    for linea in res_A_u_mas_v.desglose_filas:
        pasos.append(f"    {linea}")
    izq_str = "[" + ", ".join([formatear_numero(x, modo) for x in lado_izq]) + "]ᵀ"
    pasos.append(f"  => Vector L.I. = A(u + v) = {izq_str}\n")

    pasos.append("--- [2] DESARROLLO DEL LADO DERECHO: Au + Av ---")
    pasos.append("  Paso 2.1: Multiplicar A · u:")
    for linea in res_Au.desglose_filas:
        pasos.append(f"    {linea}")
    Au_str = "[" + ", ".join([formatear_numero(x, modo) for x in res_Au.vector_resultado]) + "]ᵀ"
    pasos.append(f"    Au = {Au_str}\n")

    pasos.append("  Paso 2.2: Multiplicar A · v:")
    for linea in res_Av.desglose_filas:
        pasos.append(f"    {linea}")
    Av_str = "[" + ", ".join([formatear_numero(x, modo) for x in res_Av.vector_resultado]) + "]ᵀ"
    pasos.append(f"    Av = {Av_str}\n")

    pasos.append("  Paso 2.3: Sumar los vectores resultantes Au + Av:")
    for i, (au_i, av_i, der_i) in enumerate(zip(res_Au.vector_resultado, res_Av.vector_resultado, lado_der)):
        pasos.append(f"    Fila {i+1}: ({formatear_numero(au_i, modo)}) + ({formatear_numero(av_i, modo)}) = {formatear_numero(der_i, modo)}")
    der_str = "[" + ", ".join([formatear_numero(x, modo) for x in lado_der]) + "]ᵀ"
    pasos.append(f"  => Vector L.D. = Au + Av = {der_str}\n")

    pasos.append("--- [3] CONCLUSIÓN Y VERIFICACIÓN TEÓRICA ---")
    pasos.append(f"  Lado Izquierdo A(u + v) = {izq_str}")
    pasos.append(f"  Lado Derecho   Au + Av  = {der_str}")
    if se_cumple:
        pasos.append("\n  ✓ ¡PROPIEDAD VERIFICADA CON ÉXITO!")
        pasos.append("    Se cumple idénticamente que A(u + v) = Au + Av para cada componente.")
    else:
        pasos.append("\n  ✗ Discrepancia encontrada en la verificación numérica.")

    return VerificacionPropiedadAditivaAx(
        u=u, v=v, u_mas_v=u_mas_v,
        lado_izq_A_u_mas_v=lado_izq,
        Au=res_Au.vector_resultado,
        Av=res_Av.vector_resultado,
        lado_der_Au_mas_Av=lado_der,
        se_cumple=se_cumple,
        desglose_pasos=pasos
    )


def verificar_propiedad_escalar_ax(A: Matriz, u: Vector, c: float, modo: str = "fraccion") -> VerificacionPropiedadEscalarAx:
    """Verifica paso a paso la propiedad de homogeneidad escalar: A(cu) = c(Au).
    
    Teorema: Si A es una matriz m × n, u es un vector en ℝⁿ, y c es un escalar:
      Lado Izquierdo (L.I.): Primero escala el vector cu, luego multiplica A · (cu).
      Lado Derecho   (L.D.): Primero multiplica A · u, luego escala el resultado c · (Au).
      Conclusión: L.I. == L.D.
    """
    if not A or not A[0]:
        raise ValueError("La matriz A no puede estar vacía.")
    m = len(A)
    n = len(A[0])
    if len(u) != n:
        raise ValueError(
            f"Dimensión incompatible: La matriz A tiene {n} columnas, pero el vector u tiene {len(u)} componentes."
        )

    c_fmt = formatear_numero(c, modo)

    # 1. Lado Izquierdo: A(cu)
    cu = [round(c * ui, 9) for ui in u]
    res_A_cu = multiplicar_matriz_vector(A, cu, modo=modo)
    lado_izq = res_A_cu.vector_resultado

    # 2. Lado Derecho: c(Au)
    res_Au = multiplicar_matriz_vector(A, u, modo=modo)
    c_Au = [round(c * aui, 9) for aui in res_Au.vector_resultado]

    # 3. Comprobación de igualdad numérica
    se_cumple = all(abs(izq - der) < 1e-7 for izq, der in zip(lado_izq, c_Au))

    # 4. Desglose detallado
    pasos: List[str] = []
    pasos.append("======================================================================")
    pasos.append("  PROPIEDAD b) DEL PRODUCTO MATRIZ-VECTOR: A(cu) = c(Au)")
    pasos.append("======================================================================\n")
    pasos.append(f"Teorema: Si A es una matriz de {m}×{n}, u es un vector en ℝ{a_subindice(n)}, y c = {c_fmt} es un escalar,")
    pasos.append("el escalar puede operar antes o después de la multiplicación matriz-vector.\n")

    pasos.append("--- [1] DESARROLLO DEL LADO IZQUIERDO: A(cu) ---")
    u_str = "[" + ", ".join([formatear_numero(x, modo) for x in u]) + "]ᵀ"
    cu_str = "[" + ", ".join([formatear_numero(x, modo) for x in cu]) + "]ᵀ"
    pasos.append(f"  Vector u = {u_str}")
    pasos.append(f"  Escalar c = {c_fmt}")
    pasos.append("  Paso 1.1: Multiplicar escalar por vector w = c · u:")
    for i, (ui, c_ui) in enumerate(zip(u, cu)):
        pasos.append(f"    w{a_subindice(i+1)} = ({c_fmt}) · ({formatear_numero(ui, modo)}) = {formatear_numero(c_ui, modo)}")
    pasos.append(f"  Vector escalado (cu) = {cu_str}\n")

    pasos.append("  Paso 1.2: Multiplicar A por el vector escalado (cu):")
    for linea in res_A_cu.desglose_filas:
        pasos.append(f"    {linea}")
    izq_str = "[" + ", ".join([formatear_numero(x, modo) for x in lado_izq]) + "]ᵀ"
    pasos.append(f"  => Vector L.I. = A(cu) = {izq_str}\n")

    pasos.append("--- [2] DESARROLLO DEL LADO DERECHO: c(Au) ---")
    pasos.append("  Paso 2.1: Multiplicar A · u:")
    for linea in res_Au.desglose_filas:
        pasos.append(f"    {linea}")
    Au_str = "[" + ", ".join([formatear_numero(x, modo) for x in res_Au.vector_resultado]) + "]ᵀ"
    pasos.append(f"    Au = {Au_str}\n")

    pasos.append(f"  Paso 2.2: Multiplicar el resultado Au por el escalar c = {c_fmt}:")
    for i, (au_i, c_au_i) in enumerate(zip(res_Au.vector_resultado, c_Au)):
        pasos.append(f"    Fila {i+1}: ({c_fmt}) · ({formatear_numero(au_i, modo)}) = {formatear_numero(c_au_i, modo)}")
    der_str = "[" + ", ".join([formatear_numero(x, modo) for x in c_Au]) + "]ᵀ"
    pasos.append(f"  => Vector L.D. = c(Au) = {der_str}\n")

    pasos.append("--- [3] CONCLUSIÓN Y VERIFICACIÓN TEÓRICA ---")
    pasos.append(f"  Lado Izquierdo A(cu) = {izq_str}")
    pasos.append(f"  Lado Derecho   c(Au) = {der_str}")
    if se_cumple:
        pasos.append("\n  ✓ ¡PROPIEDAD VERIFICADA CON ÉXITO!")
        pasos.append("    Se cumple idénticamente que A(cu) = c(Au) para cada componente.")
    else:
        pasos.append("\n  ✗ Discrepancia encontrada en la verificación numérica.")

    return VerificacionPropiedadEscalarAx(
        c=c, u=u, c_u=cu,
        lado_izq_A_cu=lado_izq,
        Au=res_Au.vector_resultado,
        lado_der_c_Au=c_Au,
        se_cumple=se_cumple,
        desglose_pasos=pasos
    )
