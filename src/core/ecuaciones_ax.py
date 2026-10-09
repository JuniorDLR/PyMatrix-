from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Union, Any
from fractions import Fraction

from src.core.domain import Matriz, formatear_numero, formatear_fraccion, a_subindice
from src.core.gauss import resolver_gauss_jordan, copiar_matriz, PasoGauss, SolucionUnica, SolucionInfinita, SinSolucion, SolucionGeneral
from src.core.vectors import Vector

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

