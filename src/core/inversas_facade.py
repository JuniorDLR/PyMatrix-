from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Union, Any
from fractions import Fraction

from src.core.domain import Matriz, formatear_numero, formatear_fraccion, a_subindice
from src.core.gauss import resolver_gauss_jordan, copiar_matriz, PasoGauss, SolucionUnica, SolucionInfinita, SinSolucion, SolucionGeneral
from src.core.vectors import Vector

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

