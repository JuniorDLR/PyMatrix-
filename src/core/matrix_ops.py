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
from typing import List, Tuple, Optional, Union

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
    """Demostración y verificación paso a paso de A(u + v) = Au + Av (o para k vectores)."""
    vectores: List[Vector]
    suma_vectores: Vector
    lado_izq_A_suma: Vector
    vectores_transformados: List[Vector]
    lado_der_suma_transformados: Vector
    se_cumple: bool
    desglose_pasos: List[str]

    @property
    def u(self) -> Vector:
        return self.vectores[0] if self.vectores else []

    @property
    def v(self) -> Vector:
        return self.vectores[1] if len(self.vectores) > 1 else []

    @property
    def u_mas_v(self) -> Vector:
        return self.suma_vectores

    @property
    def lado_izq_A_u_mas_v(self) -> Vector:
        return self.lado_izq_A_suma

    @property
    def Au(self) -> Vector:
        return self.vectores_transformados[0] if self.vectores_transformados else []

    @property
    def Av(self) -> Vector:
        return self.vectores_transformados[1] if len(self.vectores_transformados) > 1 else []

    @property
    def lado_der_Au_mas_Av(self) -> Vector:
        return self.lado_der_suma_transformados


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


@dataclass
class VerificacionLinealidadGeneralAx:
    """Demostración y verificación de A(c₁v₁ + ... + cₖvₖ) = c₁(Av₁) + ... + cₖ(Avₖ)."""
    vectores: List[Vector]
    escalares: List[float]
    comb_lineal_vectores: Vector
    lado_izq_A_comb: Vector
    vectores_transformados: List[Vector]
    vectores_escalados_transformados: List[Vector]
    lado_der_suma_escalados: Vector
    se_cumple: bool
    desglose_pasos: List[str]


def verificar_propiedad_aditiva_ax(
    A: Matriz,
    u_o_vectores: Union[Vector, List[Vector]],
    v: Optional[Vector] = None,
    modo: str = "fraccion"
) -> VerificacionPropiedadAditivaAx:
    """Verifica paso a paso la propiedad distributiva: A(u + v) = Au + Av (o para k vectores).
    
    Teorema: Si A es una matriz m × n, y los vectores pertenecen a ℝⁿ:
      Lado Izquierdo (L.I.): Primero suma los vectores, luego multiplica A por la suma.
      Lado Derecho   (L.D.): Multiplica A por cada vector y luego suma los resultados.
      Conclusión: L.I. == L.D.
    """
    if not A or not A[0]:
        raise ValueError("La matriz A no puede estar vacía.")
    m = len(A)
    n = len(A[0])

    # Manejar si se pasaron 2 vectores (u, v) o una lista de k vectores
    if v is not None:
        vectores: List[Vector] = [u_o_vectores, v]  # type: ignore
    elif isinstance(u_o_vectores, list) and u_o_vectores and isinstance(u_o_vectores[0], list):
        vectores = u_o_vectores  # type: ignore
    else:
        raise ValueError("Debe ingresar al menos dos vectores para verificar la propiedad distributiva.")

    k = len(vectores)
    if k < 2:
        raise ValueError("Se requieren al menos 2 vectores para verificar la propiedad aditiva.")

    for idx, vec in enumerate(vectores):
        if len(vec) != n:
            raise ValueError(
                f"Dimensión incompatible: La matriz A tiene {n} columnas, pero el vector {idx+1} "
                f"tiene {len(vec)} componentes. Todos los vectores deben pertenecer a ℝ{a_subindice(n)}."
            )

    es_caso_dos = (k == 2)
    nombres = ["u", "v"] if es_caso_dos else [f"v{a_subindice(j+1)}" for j in range(k)]

    # 1. Lado Izquierdo: A(v₁ + ... + vₖ)
    suma_vecs: Vector = [0.0] * n
    for vec in vectores:
        for i in range(n):
            suma_vecs[i] = round(suma_vecs[i] + vec[i], 9)

    res_A_suma = multiplicar_matriz_vector(A, suma_vecs, modo=modo)
    lado_izq = res_A_suma.vector_resultado

    # 2. Lado Derecho: A·v₁ + ... + A·vₖ
    res_A_vecs = [multiplicar_matriz_vector(A, vec, modo=modo) for vec in vectores]
    lado_der: Vector = [0.0] * m
    for r in res_A_vecs:
        for i in range(m):
            lado_der[i] = round(lado_der[i] + r.vector_resultado[i], 9)

    # 3. Comprobación de igualdad numérica
    se_cumple = all(abs(izq - der) < 1e-7 for izq, der in zip(lado_izq, lado_der))

    # 4. Desglose detallado
    pasos: List[str] = []
    pasos.append("======================================================================")
    if es_caso_dos:
        pasos.append("  PROPIEDAD a) DEL PRODUCTO MATRIZ-VECTOR: A(u + v) = Au + Av")
    else:
        formula_str = " + ".join(nombres)
        formula_der = " + ".join([f"A{nom}" for nom in nombres])
        pasos.append(f"  PROPIEDAD DISTRIBUTIVA GENERALIZADA: A({formula_str}) = {formula_der}")
    pasos.append("======================================================================\n")
    pasos.append(f"Teorema: Si A es una matriz de {m}×{n} y los {k} vectores pertenecen a ℝ{a_subindice(n)},")
    pasos.append("la multiplicación matriz-vector se distribuye sobre la suma de vectores.\n")

    # Desarrollo Lado Izquierdo
    expr_izq = "A(u + v)" if es_caso_dos else f"A({' + '.join(nombres)})"
    pasos.append(f"--- [1] DESARROLLO DEL LADO IZQUIERDO: {expr_izq} ---")
    for nom, vec in zip(nombres, vectores):
        v_str = "[" + ", ".join([formatear_numero(x, modo) for x in vec]) + "]ᵀ"
        pasos.append(f"  Vector {nom} = {v_str}")

    pasos.append(f"\n  Paso 1.1: Sumar vectores w = {' + '.join(nombres)} componente a componente:")
    for i in range(n):
        sumandos = " + ".join([f"({formatear_numero(vec[i], modo)})" for vec in vectores])
        pasos.append(f"    w{a_subindice(i+1)} = {sumandos} = {formatear_numero(suma_vecs[i], modo)}")
    suma_str = "[" + ", ".join([formatear_numero(x, modo) for x in suma_vecs]) + "]ᵀ"
    pasos.append(f"  Vector suma = {suma_str}\n")

    pasos.append(f"  Paso 1.2: Multiplicar A por el vector suma:")
    for linea in res_A_suma.desglose_filas:
        pasos.append(f"    {linea}")
    izq_str = "[" + ", ".join([formatear_numero(x, modo) for x in lado_izq]) + "]ᵀ"
    pasos.append(f"  => Vector L.I. = {expr_izq} = {izq_str}\n")

    # Desarrollo Lado Derecho
    expr_der = "Au + Av" if es_caso_dos else " + ".join([f"A{nom}" for nom in nombres])
    pasos.append(f"--- [2] DESARROLLO DEL LADO DERECHO: {expr_der} ---")
    for j, (nom, r) in enumerate(zip(nombres, res_A_vecs)):
        pasos.append(f"  Paso 2.{j+1}: Multiplicar A · {nom}:")
        for linea in r.desglose_filas:
            pasos.append(f"    {linea}")
        nom_r_str = "[" + ", ".join([formatear_numero(x, modo) for x in r.vector_resultado]) + "]ᵀ"
        pasos.append(f"    A · {nom} = {nom_r_str}\n")

    pasos.append(f"  Paso 2.{k+1}: Sumar los vectores transformados ({expr_der}):")
    for i in range(m):
        sumandos_der = " + ".join([f"({formatear_numero(r.vector_resultado[i], modo)})" for r in res_A_vecs])
        pasos.append(f"    Fila {i+1}: {sumandos_der} = {formatear_numero(lado_der[i], modo)}")
    der_str = "[" + ", ".join([formatear_numero(x, modo) for x in lado_der]) + "]ᵀ"
    pasos.append(f"  => Vector L.D. = {expr_der} = {der_str}\n")

    # Conclusión
    pasos.append("--- [3] CONCLUSIÓN Y VERIFICACIÓN TEÓRICA ---")
    pasos.append(f"  Lado Izquierdo {expr_izq} = {izq_str}")
    pasos.append(f"  Lado Derecho   {expr_der} = {der_str}")
    if se_cumple:
        pasos.append("\n  ✓ ¡PROPIEDAD VERIFICADA CON ÉXITO!")
        pasos.append(f"    Se cumple idénticamente que {expr_izq} = {expr_der} para cada componente.")
    else:
        pasos.append("\n  ✗ Discrepancia encontrada en la verificación numérica.")

    return VerificacionPropiedadAditivaAx(
        vectores=vectores,
        suma_vectores=suma_vecs,
        lado_izq_A_suma=lado_izq,
        vectores_transformados=[r.vector_resultado for r in res_A_vecs],
        lado_der_suma_transformados=lado_der,
        se_cumple=se_cumple,
        desglose_pasos=pasos
    )


def verificar_propiedad_escalar_ax(
    A: Matriz,
    u: Vector,
    c: float,
    modo: str = "fraccion",
    nombre_vector: str = "u"
) -> VerificacionPropiedadEscalarAx:
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
            f"Dimensión incompatible: La matriz A tiene {n} columnas, pero el vector {nombre_vector} tiene {len(u)} componentes."
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
    pasos.append(f"  PROPIEDAD b) DEL PRODUCTO MATRIZ-VECTOR: A(c·{nombre_vector}) = c(A·{nombre_vector})")
    pasos.append("======================================================================\n")
    pasos.append(f"Teorema: Si A es una matriz de {m}×{n}, {nombre_vector} está en ℝ{a_subindice(n)}, y c = {c_fmt} es un escalar,")
    pasos.append("el escalar puede operar antes o después de la multiplicación matriz-vector.\n")

    pasos.append(f"--- [1] DESARROLLO DEL LADO IZQUIERDO: A(c·{nombre_vector}) ---")
    u_str = "[" + ", ".join([formatear_numero(x, modo) for x in u]) + "]ᵀ"
    cu_str = "[" + ", ".join([formatear_numero(x, modo) for x in cu]) + "]ᵀ"
    pasos.append(f"  Vector {nombre_vector} = {u_str}")
    pasos.append(f"  Escalar c = {c_fmt}")
    pasos.append(f"  Paso 1.1: Multiplicar escalar por vector w = c · {nombre_vector}:")
    for i, (ui, c_ui) in enumerate(zip(u, cu)):
        pasos.append(f"    w{a_subindice(i+1)} = ({c_fmt}) · ({formatear_numero(ui, modo)}) = {formatear_numero(c_ui, modo)}")
    pasos.append(f"  Vector escalado (c·{nombre_vector}) = {cu_str}\n")

    pasos.append(f"  Paso 1.2: Multiplicar A por el vector escalado (c·{nombre_vector}):")
    for linea in res_A_cu.desglose_filas:
        pasos.append(f"    {linea}")
    izq_str = "[" + ", ".join([formatear_numero(x, modo) for x in lado_izq]) + "]ᵀ"
    pasos.append(f"  => Vector L.I. = A(c·{nombre_vector}) = {izq_str}\n")

    pasos.append(f"--- [2] DESARROLLO DEL LADO DERECHO: c(A·{nombre_vector}) ---")
    pasos.append(f"  Paso 2.1: Multiplicar A · {nombre_vector}:")
    for linea in res_Au.desglose_filas:
        pasos.append(f"    {linea}")
    Au_str = "[" + ", ".join([formatear_numero(x, modo) for x in res_Au.vector_resultado]) + "]ᵀ"
    pasos.append(f"    A · {nombre_vector} = {Au_str}\n")

    pasos.append(f"  Paso 2.2: Multiplicar el resultado A·{nombre_vector} por el escalar c = {c_fmt}:")
    for i, (au_i, c_au_i) in enumerate(zip(res_Au.vector_resultado, c_Au)):
        pasos.append(f"    Fila {i+1}: ({c_fmt}) · ({formatear_numero(au_i, modo)}) = {formatear_numero(c_au_i, modo)}")
    der_str = "[" + ", ".join([formatear_numero(x, modo) for x in c_Au]) + "]ᵀ"
    pasos.append(f"  => Vector L.D. = c(A·{nombre_vector}) = {der_str}\n")

    pasos.append("--- [3] CONCLUSIÓN Y VERIFICACIÓN TEÓRICA ---")
    pasos.append(f"  Lado Izquierdo A(c·{nombre_vector}) = {izq_str}")
    pasos.append(f"  Lado Derecho   c(A·{nombre_vector}) = {der_str}")
    if se_cumple:
        pasos.append("\n  ✓ ¡PROPIEDAD VERIFICADA CON ÉXITO!")
        pasos.append(f"    Se cumple idénticamente que A(c·{nombre_vector}) = c(A·{nombre_vector}) para cada componente.")
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


def verificar_linealidad_general_ax(
    A: Matriz,
    vectores: List[Vector],
    escalares: List[float],
    modo: str = "fraccion"
) -> VerificacionLinealidadGeneralAx:
    """Verifica el Principio de Superposición / Linealidad General:
    A(c₁v₁ + c₂v₂ + ... + cₖvₖ) = c₁(Av₁) + c₂(Av₂) + ... + cₖ(Avₖ).
    
    Combina las propiedades distributiva y de homogeneidad escalar para k vectores cualesquiera en ℝⁿ.
    """
    if not A or not A[0]:
        raise ValueError("La matriz A no puede estar vacía.")
    m = len(A)
    n = len(A[0])
    k = len(vectores)
    if k != len(escalares):
        raise ValueError(f"Debe haber igual número de vectores ({k}) que de escalares ({len(escalares)}).")
    if k < 2:
        raise ValueError("Se requieren al menos 2 vectores para la combinación lineal general.")

    for idx, vec in enumerate(vectores):
        if len(vec) != n:
            raise ValueError(f"El vector v{idx+1} tiene {len(vec)} componentes, pero la matriz A tiene {n} columnas.")

    nombres = ["u", "v"] if k == 2 else [f"v{a_subindice(j+1)}" for j in range(k)]

    # 1. Lado Izquierdo: A(∑ cᵢ vᵢ)
    comb_vec: Vector = [0.0] * n
    for c_val, vec in zip(escalares, vectores):
        for i in range(n):
            comb_vec[i] = round(comb_vec[i] + c_val * vec[i], 9)

    res_A_comb = multiplicar_matriz_vector(A, comb_vec, modo=modo)
    lado_izq = res_A_comb.vector_resultado

    # 2. Lado Derecho: ∑ cᵢ (A · vᵢ)
    res_A_vecs = [multiplicar_matriz_vector(A, vec, modo=modo) for vec in vectores]
    vecs_escalados: List[Vector] = []
    for c_val, r in zip(escalares, res_A_vecs):
        v_esc = [round(c_val * comp, 9) for comp in r.vector_resultado]
        vecs_escalados.append(v_esc)

    lado_der: Vector = [0.0] * m
    for v_esc in vecs_escalados:
        for i in range(m):
            lado_der[i] = round(lado_der[i] + v_esc[i], 9)

    # 3. Comprobación
    se_cumple = all(abs(izq - der) < 1e-7 for izq, der in zip(lado_izq, lado_der))

    # 4. Desglose
    pasos: List[str] = []
    pasos.append("======================================================================")
    pasos.append("  PRINCIPIO DE SUPERPOSICIÓN / LINEALIDAD GENERAL DEL PRODUCTO Ax")
    pasos.append("======================================================================\n")
    comb_formula = " + ".join([f"({formatear_numero(c, modo)})·{nom}" for c, nom in zip(escalares, nombres)])
    der_formula = " + ".join([f"({formatear_numero(c, modo)})·(A·{nom})" for c, nom in zip(escalares, nombres)])
    pasos.append(f"Teorema General: Para una matriz A de {m}×{n}, {k} vectores en ℝ{a_subindice(n)} y sus escalares:")
    pasos.append(f"  A( {comb_formula} ) = {der_formula}\n")

    # L.I.
    pasos.append("--- [1] DESARROLLO DEL LADO IZQUIERDO: A( ∑ cᵢ vᵢ ) ---")
    for nom, c_val, vec in zip(nombres, escalares, vectores):
        v_str = "[" + ", ".join([formatear_numero(x, modo) for x in vec]) + "]ᵀ"
        pasos.append(f"  Vector {nom} = {v_str}  (Escalar c = {formatear_numero(c_val, modo)})")

    pasos.append("\n  Paso 1.1: Calcular la combinación lineal de los vectores w = ∑ cᵢ vᵢ:")
    for i in range(n):
        sumandos = " + ".join([f"({formatear_numero(c, modo)})·({formatear_numero(v[i], modo)})" for c, v in zip(escalares, vectores)])
        pasos.append(f"    w{a_subindice(i+1)} = {sumandos} = {formatear_numero(comb_vec[i], modo)}")
    comb_str = "[" + ", ".join([formatear_numero(x, modo) for x in comb_vec]) + "]ᵀ"
    pasos.append(f"  Vector combinación lineal w = {comb_str}\n")

    pasos.append("  Paso 1.2: Multiplicar A por el vector combinación lineal:")
    for linea in res_A_comb.desglose_filas:
        pasos.append(f"    {linea}")
    izq_str = "[" + ", ".join([formatear_numero(x, modo) for x in lado_izq]) + "]ᵀ"
    pasos.append(f"  => Vector L.I. = A( ∑ cᵢ vᵢ ) = {izq_str}\n")

    # L.D.
    pasos.append("--- [2] DESARROLLO DEL LADO DERECHO: ∑ cᵢ (A · vᵢ) ---")
    for j, (nom, c_val, r, v_esc) in enumerate(zip(nombres, escalares, res_A_vecs, vecs_escalados)):
        pasos.append(f"  Paso 2.{j+1}a: Multiplicar A · {nom}:")
        nom_r_str = "[" + ", ".join([formatear_numero(x, modo) for x in r.vector_resultado]) + "]ᵀ"
        pasos.append(f"    A · {nom} = {nom_r_str}")
        pasos.append(f"  Paso 2.{j+1}b: Escalar por c = {formatear_numero(c_val, modo)}:")
        esc_str = "[" + ", ".join([formatear_numero(x, modo) for x in v_esc]) + "]ᵀ"
        pasos.append(f"    {formatear_numero(c_val, modo)} · (A·{nom}) = {esc_str}\n")

    pasos.append(f"  Paso 2.{k+1}: Sumar los vectores escalados resultantes:")
    for i in range(m):
        sumandos_der = " + ".join([f"({formatear_numero(ve[i], modo)})" for ve in vecs_escalados])
        pasos.append(f"    Fila {i+1}: {sumandos_der} = {formatear_numero(lado_der[i], modo)}")
    der_str = "[" + ", ".join([formatear_numero(x, modo) for x in lado_der]) + "]ᵀ"
    pasos.append(f"  => Vector L.D. = ∑ cᵢ (A · vᵢ) = {der_str}\n")

    # Conclusión
    pasos.append("--- [3] CONCLUSIÓN Y VERIFICACIÓN TEÓRICA ---")
    pasos.append(f"  Lado Izquierdo A( ∑ cᵢ vᵢ )  = {izq_str}")
    pasos.append(f"  Lado Derecho   ∑ cᵢ (A · vᵢ) = {der_str}")
    if se_cumple:
        pasos.append("\n  ✓ ¡PROPIEDAD DE LINEALIDAD GENERAL VERIFICADA CON ÉXITO!")
        pasos.append("    La transformación matricial preserva exactamente las combinaciones lineales.")
    else:
        pasos.append("\n  ✗ Discrepancia encontrada en la verificación numérica.")

    return VerificacionLinealidadGeneralAx(
        vectores=vectores,
        escalares=escalares,
        comb_lineal_vectores=comb_vec,
        lado_izq_A_comb=lado_izq,
        vectores_transformados=[r.vector_resultado for r in res_A_vecs],
        vectores_escalados_transformados=vecs_escalados,
        lado_der_suma_escalados=lado_der,
        se_cumple=se_cumple,
        desglose_pasos=pasos
    )
