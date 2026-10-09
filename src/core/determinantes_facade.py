from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Union, Any
from fractions import Fraction

from src.core.domain import Matriz, formatear_numero, formatear_fraccion, a_subindice
from src.core.gauss import resolver_gauss_jordan, copiar_matriz, PasoGauss, SolucionUnica, SolucionInfinita, SinSolucion, SolucionGeneral
from src.core.vectors import Vector

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

