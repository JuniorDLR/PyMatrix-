"""Operaciones aritméticas entre matrices: suma, resta, producto escalar y multiplicación.
Tema de clase: álgebra matricial y compatibilidad de dimensiones (Sesión 9).
Las funciones de cálculo no usan input() ni print(); devuelven resultados numéricos y pasos.
Elaborado por: Grupo x"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Union, Any
from fractions import Fraction

from src.core.domain import Matriz, formatear_numero, formatear_fraccion, a_subindice
from src.core.gauss import resolver_gauss_jordan, copiar_matriz, PasoGauss, SolucionUnica, SolucionInfinita, SinSolucion, SolucionGeneral
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

def trasponer_matriz(A: Matriz) -> Matriz:
    """Devuelve Aᵀ (n × m) con (Aᵀ)ᵢⱼ = Aⱼᵢ a partir de una matriz A de m × n."""
    if not A or not A[0]:
        raise ValueError("La matriz no puede estar vacía.")
    m = len(A)
    n = len(A[0])
    return [[A[i][j] for i in range(m)] for j in range(n)]

