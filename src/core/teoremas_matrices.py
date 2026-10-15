"""Verificador exacto de propiedades matriciales exigidas en la Tarea 6.

Calcula ambos miembros con las funciones existentes y devuelve datos, sin E/S.
Elaborado por: Grupo x.
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from src.core.exact_math import (
    MatrizF,
    crear_matriz,
    determinante_triangulacion,
    inversa_gauss_jordan,
    matriz_identidad,
    multiplicar_escalar,
    multiplicar_matrices,
    parsear_fraccion,
    son_matrices_iguales,
    sumar_matrices,
    trasponer_matriz,
    validar_matriz_cuadrada,
)


ValorTeorema = MatrizF | Fraction


@dataclass(frozen=True)
class EspecificacionTeorema:
    """Identifica una igualdad y las entradas adicionales necesarias para evaluarla."""

    clave: str
    categoria: str
    formula: str
    entradas: tuple[str, ...]


TEOREMAS = (
    EspecificacionTeorema("doble_traspuesta", "Operaciones", "(Aᵀ)ᵀ = A", ()),
    EspecificacionTeorema("traspuesta_suma", "Operaciones", "(A+B)ᵀ = Aᵀ+Bᵀ", ("B",)),
    EspecificacionTeorema("traspuesta_escalar", "Operaciones", "(kA)ᵀ = kAᵀ", ("k",)),
    EspecificacionTeorema("traspuesta_producto", "Operaciones", "(AB)ᵀ = BᵀAᵀ", ("B",)),
    EspecificacionTeorema("distributiva", "Operaciones", "A(B+C) = AB+AC", ("B", "C")),
    EspecificacionTeorema("asociativa", "Operaciones", "(AB)C = A(BC)", ("B", "C")),
    EspecificacionTeorema("doble_inversa", "Inversa", "(A⁻¹)⁻¹ = A", ()),
    EspecificacionTeorema("inversa_producto", "Inversa", "(AB)⁻¹ = B⁻¹A⁻¹", ("B",)),
    EspecificacionTeorema("inversa_traspuesta", "Inversa", "(Aᵀ)⁻¹ = (A⁻¹)ᵀ", ()),
    EspecificacionTeorema("identidad_inversa", "Inversa", "A·A⁻¹ = I", ()),
    EspecificacionTeorema("det_traspuesta", "Determinante", "det(Aᵀ) = det(A)", ()),
    EspecificacionTeorema("det_producto", "Determinante", "det(AB) = det(A)det(B)", ("B",)),
    EspecificacionTeorema("det_inversa", "Determinante", "det(A⁻¹) = 1/det(A)", ()),
    EspecificacionTeorema("det_escalar", "Determinante", "det(kA) = kⁿdet(A)", ("k",)),
    EspecificacionTeorema("det_intercambio", "Determinante", "det(F₁↔F₂) = −det(A)", ()),
    EspecificacionTeorema("det_reemplazo", "Determinante", "det(F₁←F₁+kF₂) = det(A)", ("k",)),
    EspecificacionTeorema("det_fila_escalar", "Determinante", "det(F₁←kF₁) = k·det(A)", ("k",)),
    EspecificacionTeorema("det_triangular", "Determinante", "det(A triangular) = ∏aᵢᵢ", ()),
)

_POR_CLAVE = {teorema.clave: teorema for teorema in TEOREMAS}


@dataclass(frozen=True)
class ResultadoTeorema:
    """Guarda ambos miembros, resultados intermedios y el diagnóstico exacto."""

    especificacion: EspecificacionTeorema
    izquierdo: ValorTeorema
    derecho: ValorTeorema
    se_cumple: bool
    intermedios: list[tuple[str, ValorTeorema]]


def _inversa(matriz: MatrizF, nombre: str) -> MatrizF:
    """Obtiene la inversa o informa que la propiedad no está definida."""

    resultado = inversa_gauss_jordan(matriz)
    if not resultado.es_invertible or resultado.matriz_inversa is None:
        raise ValueError(f"{nombre} es singular; la inversa de esta propiedad no está definida.")
    return resultado.matriz_inversa


def _det(matriz: MatrizF) -> Fraction:
    """Calcula el determinante exacto con la implementación ya existente."""

    return determinante_triangulacion(matriz)[0]


def verificar_teorema(
    clave: str,
    datos_a: list[list[Any]],
    datos_b: list[list[Any]] | None = None,
    datos_c: list[list[Any]] | None = None,
    escalar: Any | None = None,
) -> ResultadoTeorema:
    """Calcula ambos miembros de una igualdad y devuelve su comparación exacta."""

    if clave not in _POR_CLAVE:
        raise ValueError(f"Propiedad desconocida: {clave}.")
    especificacion = _POR_CLAVE[clave]
    A = crear_matriz(datos_a)
    B = crear_matriz(datos_b) if datos_b is not None else None
    C = crear_matriz(datos_c) if datos_c is not None else None
    k = parsear_fraccion(escalar) if escalar is not None else None
    for nombre, valor in (("B", B), ("C", C), ("k", k)):
        if nombre in especificacion.entradas and valor is None:
            raise ValueError(f"La propiedad {especificacion.formula} requiere {nombre}.")
    if "B" in especificacion.entradas:
        assert B is not None
    if "C" in especificacion.entradas:
        assert C is not None
    if "k" in especificacion.entradas:
        assert k is not None
    intermedios: list[tuple[str, ValorTeorema]] = []

    if clave == "doble_traspuesta":
        AT = trasponer_matriz(A)
        intermedios.append(("Aᵀ", AT))
        izquierdo, derecho = trasponer_matriz(AT), A
    elif clave == "traspuesta_suma":
        AB_suma = sumar_matrices(A, B)
        intermedios.append(("A+B", AB_suma))
        izquierdo = trasponer_matriz(AB_suma)
        derecho = sumar_matrices(trasponer_matriz(A), trasponer_matriz(B))
    elif clave == "traspuesta_escalar":
        kA = multiplicar_escalar(k, A)
        intermedios.append(("kA", kA))
        izquierdo = trasponer_matriz(kA)
        derecho = multiplicar_escalar(k, trasponer_matriz(A))
    elif clave == "traspuesta_producto":
        AB = multiplicar_matrices(A, B)
        intermedios.append(("AB", AB))
        izquierdo = trasponer_matriz(AB)
        derecho = multiplicar_matrices(trasponer_matriz(B), trasponer_matriz(A))
    elif clave == "distributiva":
        BC_suma = sumar_matrices(B, C)
        intermedios.append(("B+C", BC_suma))
        izquierdo = multiplicar_matrices(A, BC_suma)
        derecho = sumar_matrices(multiplicar_matrices(A, B), multiplicar_matrices(A, C))
    elif clave == "asociativa":
        AB = multiplicar_matrices(A, B)
        BC = multiplicar_matrices(B, C)
        intermedios.extend((("AB", AB), ("BC", BC)))
        izquierdo = multiplicar_matrices(AB, C)
        derecho = multiplicar_matrices(A, BC)
    elif clave == "doble_inversa":
        A_inv = _inversa(A, "A")
        intermedios.append(("A⁻¹", A_inv))
        izquierdo, derecho = _inversa(A_inv, "A⁻¹"), A
    elif clave == "inversa_producto":
        validar_matriz_cuadrada(A, "inversa del producto")
        validar_matriz_cuadrada(B, "inversa del producto")
        AB = multiplicar_matrices(A, B)
        intermedios.append(("AB", AB))
        izquierdo = _inversa(AB, "AB")
        derecho = multiplicar_matrices(_inversa(B, "B"), _inversa(A, "A"))
    elif clave == "inversa_traspuesta":
        A_inv = _inversa(A, "A")
        intermedios.append(("A⁻¹", A_inv))
        izquierdo = _inversa(trasponer_matriz(A), "Aᵀ")
        derecho = trasponer_matriz(A_inv)
    elif clave == "identidad_inversa":
        A_inv = _inversa(A, "A")
        intermedios.append(("A⁻¹", A_inv))
        izquierdo, derecho = multiplicar_matrices(A, A_inv), matriz_identidad(len(A))
    elif clave == "det_traspuesta":
        izquierdo, derecho = _det(trasponer_matriz(A)), _det(A)
    elif clave == "det_producto":
        validar_matriz_cuadrada(A, "determinante del producto")
        validar_matriz_cuadrada(B, "determinante del producto")
        AB = multiplicar_matrices(A, B)
        intermedios.append(("AB", AB))
        izquierdo, derecho = _det(AB), _det(A) * _det(B)
    elif clave == "det_inversa":
        A_inv = _inversa(A, "A")
        det_A = _det(A)
        intermedios.extend((("A⁻¹", A_inv), ("det(A)", det_A)))
        izquierdo, derecho = _det(A_inv), Fraction(1) / det_A
    elif clave == "det_escalar":
        orden = validar_matriz_cuadrada(A, "det(kA)")
        kA = multiplicar_escalar(k, A)
        det_a = _det(A)
        intermedios.extend((("kA", kA), ("det(A)", det_a)))
        izquierdo, derecho = _det(kA), k ** orden * det_a
    elif clave in {"det_intercambio", "det_reemplazo", "det_fila_escalar"}:
        orden = validar_matriz_cuadrada(A, "operación de fila y determinante")
        if orden < 2 and clave != "det_fila_escalar":
            raise ValueError("Esta operación requiere al menos dos filas.")
        if clave == "det_fila_escalar" and k == 0:
            raise ValueError("Para una operación elemental de escala, k debe ser distinto de cero.")
        modificada = [fila[:] for fila in A]
        if clave == "det_intercambio":
            modificada[0], modificada[1] = modificada[1], modificada[0]
            esperado = -_det(A)
        elif clave == "det_reemplazo":
            modificada[0] = [modificada[0][j] + k * modificada[1][j] for j in range(orden)]
            esperado = _det(A)
        else:
            modificada[0] = [k * valor for valor in modificada[0]]
            esperado = k * _det(A)
        intermedios.append(("A después de la operación de fila", modificada))
        izquierdo, derecho = _det(modificada), esperado
    else:
        orden = validar_matriz_cuadrada(A, "determinante triangular")
        es_superior = all(A[i][j] == 0 for i in range(orden) for j in range(i))
        es_inferior = all(A[i][j] == 0 for i in range(orden) for j in range(i + 1, orden))
        if not (es_superior or es_inferior):
            raise ValueError("A debe ser triangular superior o inferior para esta propiedad.")
        producto_diagonal = Fraction(1)
        for i in range(orden):
            producto_diagonal *= A[i][i]
        izquierdo, derecho = _det(A), producto_diagonal

    se_cumple = (son_matrices_iguales(izquierdo, derecho)
                 if isinstance(izquierdo, list) else izquierdo == derecho)
    return ResultadoTeorema(especificacion, izquierdo, derecho, se_cumple, intermedios)
