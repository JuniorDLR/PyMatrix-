"""Operaciones matriciales en Python estándar (sin NumPy/SciPy), con desglose paso a paso.
Implementa suma/resta, producto por escalar, A·B, producto matriz-vector A·x y ecuación Ax = b,
propiedades de linealidad de Ax, traspuesta, inversa y determinantes.
Elaborado por: Grupo x
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


def validar_dimensiones_matrices_iguales(A: Matriz, B: Matriz, operacion: str = "operación") -> Tuple[int, int]:
    """Verifica que A y B tengan las mismas dimensiones m × n y devuelve (m, n).
    Lanza ValueError si alguna está vacía o difieren: la suma/resta solo existe entre matrices iguales."""
    if not A or not A[0] or not B or not B[0]:
        raise ValueError("Las matrices no pueden estar vacías.")
    
    # Validar dimensiones antes de operar: A ± B solo está definida si ambas son m × n.
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
    """Calcula C = A + B con C_ij = A_ij + B_ij; recibe dos matrices m × n y devuelve la suma."""
    m, n = validar_dimensiones_matrices_iguales(A, B, "suma matricial")
    C: Matriz = []
    for i in range(m):
        fila: List[float] = []
        for j in range(n):
            # round(…, 9) elimina ruido de punto flotante (p. ej. 0.1 + 0.2).
            fila.append(round(A[i][j] + B[i][j], 9))
        C.append(fila)
    return C


def restar_matrices(A: Matriz, B: Matriz) -> Matriz:
    """Calcula C = A - B con C_ij = A_ij - B_ij; recibe dos matrices m × n y devuelve la resta."""
    m, n = validar_dimensiones_matrices_iguales(A, B, "resta matricial")
    C: Matriz = []
    for i in range(m):
        fila: List[float] = []
        for j in range(n):
            fila.append(round(A[i][j] - B[i][j], 9))
        C.append(fila)
    return C


def multiplicar_matriz_escalar(c: float, A: Matriz) -> Matriz:
    """Calcula C = c · A multiplicando cada entrada de A por el escalar c; devuelve C."""
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
    """Calcula C = c_A·A + c_B·B (o c_A·A - c_B·B si restar=True) entre matrices m × n.
    Valida dimensiones iguales y devuelve la matriz resultante."""
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


@dataclass
class ResultadoMultiplicacionMatricial:
    """Almacena el resultado y el desglose paso a paso de la multiplicación A · B."""
    matriz_resultado: Matriz
    dimensiones_A: Tuple[int, int]
    dimensiones_B: Tuple[int, int]
    dimensiones_resultado: Tuple[int, int]
    desglose_pasos: List[str]


def multiplicar_matrices(A: Matriz, B: Matriz, modo: str = "fraccion") -> ResultadoMultiplicacionMatricial:
    """Calcula C = A · B con C_ij = Σₖ A_ik·B_kj; exige columnas de A == filas de B.
    Recibe A (m×n), B (n×p) y modo de formato; devuelve ResultadoMultiplicacionMatricial
    con la matriz (m×p) y el desglose por celda."""
    if not A or not A[0] or not B or not B[0]:
        raise ValueError("Ninguna de las matrices puede estar vacía.")
    
    m = len(A)
    n_A = len(A[0])
    n_B = len(B)
    p = len(B[0])
    
    # A·B existe solo si columnas de A == filas de B (producto fila por columna).
    if n_A != n_B:
        raise ValueError(
            f"Incompatibilidad de dimensiones para multiplicación: A es {m}×{n_A} y B es {n_B}×{p}. "
            f"El número de columnas de A ({n_A}) debe ser igual al número de filas de B ({n_B})."
        )
    
    n = n_A
    C: Matriz = []
    desgloses: List[str] = []
    
    for i in range(m):
        fila_C: List[float] = []
        for j in range(p):
            acumulador = 0.0
            terminos_texto: List[str] = []
            
            for k in range(n):
                prod = A[i][k] * B[k][j]
                acumulador += prod
                a_str = formatear_numero(A[i][k], modo)
                b_str = formatear_numero(B[k][j], modo)
                terminos_texto.append(f"({a_str})·({b_str})")
            
            acumulador_redondeado = round(acumulador, 9)
            fila_C.append(acumulador_redondeado)
            
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


@dataclass
class ResultadoProductoMatrizVector:
    """Resultado del cálculo Ax."""
    vector_resultado: Vector
    desglose_filas: List[str]
    combinacion_columnas: str


def multiplicar_matriz_vector(A: Matriz, x: Vector, modo: str = "fraccion") -> ResultadoProductoMatrizVector:
    """Calcula b = A · x con (Ax)_i = Σⱼ A_ij·xⱼ, equivalente a x₁a₁ + ... + xₙaₙ.
    Recibe A (m×n), x ∈ ℝⁿ y modo; devuelve el vector, el desglose por fila y la combinación de columnas."""
    if not A or not A[0]:
        raise ValueError("La matriz A no puede estar vacía.")
    if not x:
        raise ValueError("El vector x no puede estar vacío.")
    
    m = len(A)
    n = len(A[0])
    
    # Ax requiere x ∈ ℝⁿ: una componente por cada columna de A.
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
    """Resuelve Ax = b aplicando Gauss-Jordan a la matriz aumentada [A | b] de m × (n+1).
    Recibe A, b ∈ ℝᵐ y modo; devuelve la clasificación, la solución y los pasos de Gauss."""
    if not A or not A[0]:
        raise ValueError("La matriz A no puede estar vacía.")
    if not b:
        raise ValueError("El vector b no puede estar vacío.")
    
    m = len(A)
    n = len(A[0])
    
    # b debe pertenecer a ℝᵐ: una entrada por cada ecuación (fila de A).
    if len(b) != m:
        raise ValueError(
            f"Dimensión incompatible en Ax = b: La matriz A tiene {m} filas, "
            f"pero el vector b tiene dimensión {len(b)}. El vector b debe pertenecer a ℝ{a_subindice(m)}."
        )
    
    # Ax = b tiene el mismo conjunto solución que el sistema de matriz aumentada [A | b].
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
    else:
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
        """Primer vector sumado (u), o [] si no hay."""
        return self.vectores[0] if self.vectores else []

    @property
    def v(self) -> Vector:
        """Segundo vector sumado (v), o [] si no existe."""
        return self.vectores[1] if len(self.vectores) > 1 else []

    @property
    def u_mas_v(self) -> Vector:
        """Suma de los vectores (u + v)."""
        return self.suma_vectores

    @property
    def lado_izq_A_u_mas_v(self) -> Vector:
        """Lado izquierdo A(u + v)."""
        return self.lado_izq_A_suma

    @property
    def Au(self) -> Vector:
        """Producto A·u, o [] si no hay."""
        return self.vectores_transformados[0] if self.vectores_transformados else []

    @property
    def Av(self) -> Vector:
        """Producto A·v, o [] si no existe."""
        return self.vectores_transformados[1] if len(self.vectores_transformados) > 1 else []

    @property
    def lado_der_Au_mas_Av(self) -> Vector:
        """Lado derecho Au + Av."""
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
    """Verifica A(u + v) = Au + Av (o la versión con k vectores) comparando ambos lados.
    Recibe A, dos vectores o una lista de vectores y modo; devuelve ambos lados, el desglose y si se cumple."""
    if not A or not A[0]:
        raise ValueError("La matriz A no puede estar vacía.")
    m = len(A)
    n = len(A[0])

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

    suma_vecs: Vector = [0.0] * n
    for vec in vectores:
        for i in range(n):
            suma_vecs[i] = round(suma_vecs[i] + vec[i], 9)

    res_A_suma = multiplicar_matriz_vector(A, suma_vecs, modo=modo)
    lado_izq = res_A_suma.vector_resultado

    res_A_vecs = [multiplicar_matriz_vector(A, vec, modo=modo) for vec in vectores]
    lado_der: Vector = [0.0] * m
    for r in res_A_vecs:
        for i in range(m):
            lado_der[i] = round(lado_der[i] + r.vector_resultado[i], 9)

    # Tolerancia y no ==: el redondeo a 9 decimales deja diferencias mínimas entre ambos lados.
    se_cumple = all(abs(izq - der) < 1e-7 for izq, der in zip(lado_izq, lado_der))

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
    """Verifica A(cu) = c(Au) para una matriz A, un vector u y un escalar c.
    Devuelve ambos lados, el desglose paso a paso y si se cumple."""
    if not A or not A[0]:
        raise ValueError("La matriz A no puede estar vacía.")
    m = len(A)
    n = len(A[0])
    if len(u) != n:
        raise ValueError(
            f"Dimensión incompatible: La matriz A tiene {n} columnas, pero el vector {nombre_vector} tiene {len(u)} componentes."
        )

    c_fmt = formatear_numero(c, modo)

    cu = [round(c * ui, 9) for ui in u]
    res_A_cu = multiplicar_matriz_vector(A, cu, modo=modo)
    lado_izq = res_A_cu.vector_resultado

    res_Au = multiplicar_matriz_vector(A, u, modo=modo)
    c_Au = [round(c * aui, 9) for aui in res_Au.vector_resultado]

    # Tolerancia y no ==: el redondeo a 9 decimales deja diferencias mínimas entre ambos lados.
    se_cumple = all(abs(izq - der) < 1e-7 for izq, der in zip(lado_izq, c_Au))

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
    """Verifica A(c₁v₁ + ... + cₖvₖ) = c₁(Av₁) + ... + cₖ(Avₖ) para k ≥ 2 vectores.
    Recibe A, vectores, escalares y modo; devuelve ambos lados, el desglose y si se cumple."""
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

    comb_vec: Vector = [0.0] * n
    for c_val, vec in zip(escalares, vectores):
        for i in range(n):
            comb_vec[i] = round(comb_vec[i] + c_val * vec[i], 9)

    res_A_comb = multiplicar_matriz_vector(A, comb_vec, modo=modo)
    lado_izq = res_A_comb.vector_resultado

    res_A_vecs = [multiplicar_matriz_vector(A, vec, modo=modo) for vec in vectores]
    vecs_escalados: List[Vector] = []
    for c_val, r in zip(escalares, res_A_vecs):
        v_esc = [round(c_val * comp, 9) for comp in r.vector_resultado]
        vecs_escalados.append(v_esc)

    lado_der: Vector = [0.0] * m
    for v_esc in vecs_escalados:
        for i in range(m):
            lado_der[i] = round(lado_der[i] + v_esc[i], 9)

    # Tolerancia y no ==: el redondeo a 9 decimales deja diferencias mínimas entre ambos lados.
    se_cumple = all(abs(izq - der) < 1e-7 for izq, der in zip(lado_izq, lado_der))

    pasos: List[str] = []
    pasos.append("======================================================================")
    pasos.append("  PRINCIPIO DE SUPERPOSICIÓN / LINEALIDAD GENERAL DEL PRODUCTO Ax")
    pasos.append("======================================================================\n")
    comb_formula = " + ".join([f"({formatear_numero(c, modo)})·{nom}" for c, nom in zip(escalares, nombres)])
    der_formula = " + ".join([f"({formatear_numero(c, modo)})·(A·{nom})" for c, nom in zip(escalares, nombres)])
    pasos.append(f"Teorema General: Para una matriz A de {m}×{n}, {k} vectores en ℝ{a_subindice(n)} y sus escalares:")
    pasos.append(f"  A( {comb_formula} ) = {der_formula}\n")

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


def trasponer_matriz(A: Matriz) -> Matriz:
    """Devuelve Aᵀ (n × m) con (Aᵀ)ᵢⱼ = Aⱼᵢ a partir de una matriz A de m × n."""
    if not A or not A[0]:
        raise ValueError("La matriz no puede estar vacía.")
    m = len(A)
    n = len(A[0])
    return [[A[i][j] for i in range(m)] for j in range(n)]


@dataclass
class ResultadoInversionMatriz:
    """Resultado del cálculo de la matriz inversa mediante [A | I] → [I | A⁻¹]."""
    es_invertible: bool
    matriz_original: Matriz
    matriz_inversa: Optional[Matriz]
    matriz_aumentada_inicial: Matriz
    matriz_aumentada_final: Matriz
    pasos: List[str]
    explicacion: str


def invertir_matriz(A: Matriz, modo: str = "fraccion") -> ResultadoInversionMatriz:
    """Calcula A⁻¹ reduciendo [A | I] a [I | A⁻¹] con Gauss-Jordan; A debe ser cuadrada.
    Devuelve ResultadoInversionMatriz (invertible solo si el bloque izquierdo llega a I) con los pasos."""
    if not A or not A[0]:
        raise ValueError("La matriz no puede estar vacía.")
    n = len(A)
    for i, fila in enumerate(A):
        if len(fila) != n:
            raise ValueError(
                f"La matriz no es cuadrada: Fila {i+1} tiene {len(fila)} columnas pero A tiene {n} filas. "
                f"Solo las matrices cuadradas pueden tener matriz inversa."
            )

    aumentada: Matriz = []
    for i in range(n):
        fila = [float(val) for val in A[i]]
        for j in range(n):
            fila.append(1.0 if i == j else 0.0)
        aumentada.append(fila)

    aum_inicial = [fila[:] for fila in aumentada]
    pasos: List[str] = []
    pasos.append(f"1. Matriz cuadrada A de {n}×{n}. Se construye la matriz aumentada [A | I_{n}]:")

    def fmt_aum(mat: Matriz) -> str:
        """Formatea [A | I] como texto alineado, con una barra entre ambos bloques."""
        s = ""
        for row in mat:
            izq = "  ".join(f"{formatear_numero(x, modo):>8}" for x in row[:n])
            der = "  ".join(f"{formatear_numero(x, modo):>8}" for x in row[n:])
            s += f"  [ {izq} | {der} ]\n"
        return s

    pasos.append(fmt_aum(aumentada))

    rango = 0
    paso_num = 1
    for col in range(n):
        # Pivoteo parcial: el mayor |valor| reduce el error de redondeo y evita pivotes casi nulos.
        max_fila = rango
        max_val = abs(aumentada[rango][col]) if rango < n else 0.0
        for f in range(rango + 1, n):
            if abs(aumentada[f][col]) > max_val:
                max_val = abs(aumentada[f][col])
                max_fila = f

        if max_val < 1e-10:
            # Sin pivote (|valor| ≈ 0): se omite la columna y el rango quedará incompleto.
            continue

        # Intercambio de filas: lleva el pivote elegido a la posición (rango, col).
        if max_fila != rango:
            aumentada[rango], aumentada[max_fila] = aumentada[max_fila], aumentada[rango]
            pasos.append(f">> Paso {paso_num}: Fila {rango+1} ↔ Fila {max_fila+1} (Intercambio de filas por pivote)")
            pasos.append(fmt_aum(aumentada))
            paso_num += 1

        pivote = aumentada[rango][col]
        if abs(pivote - 1.0) > 1e-10:
            aumentada[rango] = [round(x / pivote, 9) for x in aumentada[rango]]
            p_fmt = formatear_numero(pivote, modo)
            pasos.append(f">> Paso {paso_num}: Fila {rango+1} → (1/{p_fmt}) · Fila {rango+1} (Normalizar pivote a 1)")
            pasos.append(fmt_aum(aumentada))
            paso_num += 1

        for f in range(n):
            if f != rango and abs(aumentada[f][col]) > 1e-10:
                factor = aumentada[f][col]
                aumentada[f] = [round(aumentada[f][c] - factor * aumentada[rango][c], 9) for c in range(2 * n)]
                f_fmt = formatear_numero(factor, modo)
                signo = "-" if factor > 0 else "+"
                f_abs_fmt = formatear_numero(abs(factor), modo)
                pasos.append(f">> Paso {paso_num}: Fila {f+1} → Fila {f+1} {signo} {f_abs_fmt} · Fila {rango+1} (Crear cero)")
                pasos.append(fmt_aum(aumentada))
                paso_num += 1

        rango += 1

    # A es invertible solo si el bloque izquierdo llegó a Iₙ (tolerancia por redondeo).
    es_identidad = True
    for i in range(n):
        for j in range(n):
            esperado = 1.0 if i == j else 0.0
            if abs(aumentada[i][j] - esperado) > 1e-7:
                es_identidad = False
                break
        if not es_identidad:
            break

    if es_identidad:
        inversa = [[aumentada[i][n + j] for j in range(n)] for i in range(n)]
        explicacion = (
            f"✓ LA MATRIZ ES INVERTIBLE (RANGO COMPLETO = {n}).\n"
            f"La forma escalonada reducida del lado izquierdo es la matriz identidad I_{n}.\n"
            f"Por tanto, el bloque derecho corresponde exactamente a la matriz inversa A⁻¹."
        )
        return ResultadoInversionMatriz(
            es_invertible=True,
            matriz_original=A,
            matriz_inversa=inversa,
            matriz_aumentada_inicial=aum_inicial,
            matriz_aumentada_final=aumentada,
            pasos=pasos,
            explicacion=explicacion
        )
    else:
        explicacion = (
            f"✗ LA MATRIZ ES SINGULAR (NO INVERTIBLE).\n"
            f"El rango por filas es {rango} < {n}. Al reducir [A | I], el lado izquierdo no alcanzó "
            f"la matriz identidad I_{n} (surgieron filas de ceros o variables libres).\n"
            f"Por el Teorema Fundamental de la Matriz Invertible, det(A) = 0 y no existe A⁻¹."
        )
        return ResultadoInversionMatriz(
            es_invertible=False,
            matriz_original=A,
            matriz_inversa=None,
            matriz_aumentada_inicial=aum_inicial,
            matriz_aumentada_final=aumentada,
            pasos=pasos,
            explicacion=explicacion
        )


@dataclass
class ResultadoDeterminante:
    """Resultado del cálculo del determinante de una matriz cuadrada."""
    matriz: Matriz
    orden: int
    determinante: float
    es_invertible: bool
    pasos: List[str]
    explicacion: str


def calcular_determinante(A: Matriz, modo: str = "fraccion") -> ResultadoDeterminante:
    """Calcula det(A) por triangulación gaussiana: det = (-1)^k · Π uᵢᵢ, con k intercambios de fila.
    Usa fórmula directa en 1×1 y 2×2; devuelve ResultadoDeterminante con pasos y diagnóstico."""
    if not A or not A[0]:
        raise ValueError("La matriz no puede estar vacía.")
    n = len(A)
    for i, fila in enumerate(A):
        if len(fila) != n:
            raise ValueError(f"La matriz no es cuadrada: tiene {n} filas y {len(fila)} columnas en fila {i+1}.")

    U = [fila[:] for fila in A]
    swaps = 0
    pasos: List[str] = []
    pasos.append(f"Cálculo del determinante de matriz A de orden {n}×{n} por triangulación:")

    def fmt_mat(mat: Matriz) -> str:
        """Formatea una matriz como texto alineado, una fila por línea."""
        return "".join("  [ " + "  ".join(f"{formatear_numero(x, modo):>8}" for x in row) + " ]\n" for row in mat)

    pasos.append(fmt_mat(U))

    # 1×1 y 2×2 se resuelven con fórmula directa, sin triangular.
    if n == 1:
        val = U[0][0]
        pasos.append(f"Matriz 1×1: det(A) = {formatear_numero(val, modo)}")
        return ResultadoDeterminante(
            matriz=A, orden=1, determinante=val, es_invertible=abs(val) > 1e-10,
            pasos=pasos,
            explicacion=f"det(A) = {formatear_numero(val, modo)}. {'Invertible' if abs(val) > 1e-10 else 'Singular'}."
        )

    if n == 2:
        val = U[0][0] * U[1][1] - U[0][1] * U[1][0]
        a11_s = formatear_numero(U[0][0], modo)
        a22_s = formatear_numero(U[1][1], modo)
        a12_s = formatear_numero(U[0][1], modo)
        a21_s = formatear_numero(U[1][0], modo)
        pasos.append(f"Fórmula 2×2: det(A) = (a₁₁ · a₂₂) − (a₁₂ · a₂₁)")
        pasos.append(f"det(A) = ({a11_s} · {a22_s}) − ({a12_s} · {a21_s}) = {formatear_numero(val, modo)}")
        return ResultadoDeterminante(
            matriz=A, orden=2, determinante=val, es_invertible=abs(val) > 1e-10,
            pasos=pasos,
            explicacion=f"det(A) = {formatear_numero(val, modo)}."
        )

    det_cero = False
    for col in range(n):
        # Mayor |pivote| (pivoteo parcial); si es ≈ 0 la columna no tiene pivote y det(A) = 0.
        pivot_row = col
        max_val = abs(U[col][col])
        for r in range(col + 1, n):
            if abs(U[r][col]) > max_val:
                max_val = abs(U[r][col])
                pivot_row = r

        if max_val < 1e-10:
            det_cero = True
            pasos.append(f"Columna {col+1}: Todos los elementos bajo la diagonal son cero. La matriz es singular.")
            break

        if pivot_row != col:
            # Cada intercambio de filas multiplica det(A) por -1; se cuenta en swaps.
            U[col], U[pivot_row] = U[pivot_row], U[col]
            swaps += 1
            pasos.append(f"Intercambio Fila {col+1} ↔ Fila {pivot_row+1} (el determinante cambia de signo por (-1)):")
            pasos.append(fmt_mat(U))

        # Sumar múltiplos de la fila pivote no altera det(A).
        piv = U[col][col]
        for r in range(col + 1, n):
            if abs(U[r][col]) > 1e-10:
                factor = U[r][col] / piv
                U[r] = [round(U[r][c] - factor * U[col][c], 9) for c in range(n)]
                pasos.append(f"Fila {r+1} → Fila {r+1} − ({formatear_numero(factor, modo)})·Fila {col+1}")

    if det_cero:
        det = 0.0
    else:
        prod_diagonal = 1.0
        diag_terms = []
        for i in range(n):
            prod_diagonal *= U[i][i]
            diag_terms.append(formatear_numero(U[i][i], modo))
        # U triangular superior: det(U) = Π uᵢᵢ y det(A) = (-1)^swaps · det(U).
        signo_swaps = (-1) ** swaps
        det = round(signo_swaps * prod_diagonal, 9)
        pasos.append(f"\nMatriz triangular superior resultante:\n{fmt_mat(U)}")
        pasos.append(f"det(A) = (-1)^{swaps} · ({' · '.join(diag_terms)}) = {formatear_numero(det, modo)}")

    es_inv = abs(det) > 1e-10
    expl = (
        f"det(A) = {formatear_numero(det, modo)}.\n"
        f"Diagnóstico: {'A es invertible (no singular), tiene columnas L.I. y rango máximo.' if es_inv else 'A no es invertible (singular), sus columnas son L.D. y det(A) = 0.'}"
    )

    return ResultadoDeterminante(
        matriz=A, orden=n, determinante=det, es_invertible=es_inv,
        pasos=pasos, explicacion=expl
    )


from modulos.modulo_matrices import (
    crear_matriz as crear_matriz_frac,
    inversa_adjunta as inv_adj_frac,
    inversa_gauss_jordan as inv_gj_frac,
    determinante_cofactores as det_cof_frac,
    determinante_sarrus as det_sar_frac,
    determinante_triangulacion as det_tri_frac,
    verificar_propiedad_inversa_de_inversa as v_prop_inv_inv,
    verificar_propiedad_inversa_del_producto as v_prop_inv_prod,
    verificar_propiedad_inversa_de_traspuesta as v_prop_inv_tras,
    verificar_propiedad_determinante_de_inversa as v_prop_det_inv,
    verificar_propiedades_operaciones_fila_det as v_prop_ops_fila,
    verificar_propiedad_matriz_triangular as v_prop_triang,
    matriz_a_cadena, matriz_cofactores as mat_cof_frac, matriz_adjunta as mat_adj_frac
)


def invertir_matriz_adjunta(A: Matriz, modo: str = "fraccion") -> ResultadoInversionMatriz:
    """Calcula A⁻¹ = (1/det(A))·adj(A) con fracciones exactas; recibe A y devuelve ResultadoInversionMatriz."""
    A_frac = crear_matriz_frac(A)
    res = inv_adj_frac(A_frac)
    
    inversa_float = None
    if res.es_invertible and res.matriz_inversa is not None:
        inversa_float = [[float(val) for val in row] for row in res.matriz_inversa]
    
    expl = (
        "✓ MATRIZ INVERTIBLE (det ≠ 0). Inversa calculada por la matriz adjunta y verificada con A · A⁻¹ = I."
        if res.es_invertible else
        "✗ MATRIZ SINGULAR: det(A) = 0. No se puede invertir por fórmula de la adjunta."
    )
    
    return ResultadoInversionMatriz(
        es_invertible=res.es_invertible,
        matriz_original=A,
        matriz_inversa=inversa_float,
        matriz_aumentada_inicial=[],
        matriz_aumentada_final=[],
        pasos=res.pasos,
        explicacion=expl
    )


def calcular_determinante_cofactores_core(A: Matriz, modo: str = "fraccion") -> ResultadoDeterminante:
    """Calcula det(A) por expansión de cofactores (Laplace) con fracciones; devuelve ResultadoDeterminante."""
    A_frac = crear_matriz_frac(A)
    det_val, pasos = det_cof_frac(A_frac)
    det_float = float(det_val)
    es_inv = abs(det_float) > 1e-10
    expl = f"det(A) = {det_val}. {'Invertible' if es_inv else 'Singular'}."
    return ResultadoDeterminante(
        matriz=A, orden=len(A), determinante=det_float, es_invertible=es_inv,
        pasos=pasos, explicacion=expl
    )


def calcular_determinante_sarrus_core(A: Matriz, modo: str = "fraccion") -> ResultadoDeterminante:
    """Calcula det(A) de una matriz 3×3 con la regla de Sarrus; devuelve ResultadoDeterminante."""
    A_frac = crear_matriz_frac(A)
    det_val, pasos = det_sar_frac(A_frac)
    det_float = float(det_val)
    es_inv = abs(det_float) > 1e-10
    expl = f"det(A) = {det_val} (Regla de Sarrus). {'Invertible' if es_inv else 'Singular'}."
    return ResultadoDeterminante(
        matriz=A, orden=3, determinante=det_float, es_invertible=es_inv,
        pasos=pasos, explicacion=expl
    )

