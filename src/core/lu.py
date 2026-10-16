"""Factorización LU exacta y resolución de sistemas de la sesión 12.

Las funciones reciben datos y devuelven matrices y pasos; no realizan entrada ni salida.
Elaborado por: Grupo x.
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from src.core.exact_math import (
    MatrizF,
    crear_matriz,
    matriz_identidad,
    multiplicar_matrices,
    parsear_fraccion,
    son_matrices_iguales,
)


@dataclass(frozen=True)
class PasoFactorizacionLU:
    """Guarda una operación elemental y los estados de P, L y U."""

    descripcion: str
    matriz_p: MatrizF
    matriz_l: MatrizF
    matriz_u: MatrizF


@dataclass(frozen=True)
class ResultadoLU:
    """Contiene la permutación, los factores exactos y su comprobación."""

    matriz_a: MatrizF
    matriz_p: MatrizF
    matriz_l: MatrizF
    matriz_u: MatrizF
    producto_pa: MatrizF
    producto_lu: MatrizF
    es_correcta: bool
    pasos: list[PasoFactorizacionLU]


@dataclass(frozen=True)
class PasoSistemaLU:
    """Guarda una sustitución u operación y el estado de su matriz aumentada."""

    descripcion: str
    matriz_aumentada: MatrizF


@dataclass(frozen=True)
class ResultadoSistemaLU:
    """Contiene y, x, los pasos de ambas etapas y la comprobación A·x=b."""

    factores: ResultadoLU
    vector_b: list[Fraction]
    vector_pb: list[Fraction]
    vector_y: list[Fraction]
    vector_x: list[Fraction]
    producto_ax: list[Fraction]
    es_correcta: bool
    pasos_adelante: list[PasoSistemaLU]
    pasos_atras: list[PasoSistemaLU]


def factorizar_lu(datos: list[list[Any]]) -> ResultadoLU:
    """Obtiene P·A=L·U para A de m×n y registra intercambios y reemplazos."""

    # Convierte las entradas a fracciones exactas y prepara P=L=I, U=A.
    matriz_a = crear_matriz(datos)
    m, n = len(matriz_a), len(matriz_a[0])
    matriz_p = matriz_identidad(m)
    matriz_l = matriz_identidad(m)
    matriz_u = [fila[:] for fila in matriz_a]
    pasos: list[PasoFactorizacionLU] = []

    def registrar_paso(descripcion: str) -> None:
        pasos.append(PasoFactorizacionLU(
            descripcion,
            [fila[:] for fila in matriz_p],
            [fila[:] for fila in matriz_l],
            [fila[:] for fila in matriz_u],
        ))

    registrar_paso("Matriz inicial A; P = Iₘ, L = Iₘ y U = A.")
    fila_pivote = 0

    # Busca un pivote no nulo; los intercambios se registran también en P y en L ya calculada.
    for columna in range(n):
        if fila_pivote == m:
            break
        pivote = matriz_u[fila_pivote][columna]
        if pivote == 0:
            fila_intercambio = next(
                (fila for fila in range(fila_pivote + 1, m) if matriz_u[fila][columna] != 0),
                None,
            )
            if fila_intercambio is None:
                registrar_paso(f"Columna {columna + 1} sin pivote: se continúa con la siguiente columna.")
                continue
            matriz_u[fila_pivote], matriz_u[fila_intercambio] = (
                matriz_u[fila_intercambio], matriz_u[fila_pivote]
            )
            matriz_p[fila_pivote], matriz_p[fila_intercambio] = (
                matriz_p[fila_intercambio], matriz_p[fila_pivote]
            )
            for j in range(fila_pivote):
                matriz_l[fila_pivote][j], matriz_l[fila_intercambio][j] = (
                    matriz_l[fila_intercambio][j], matriz_l[fila_pivote][j]
                )
            registrar_paso(
                f"Pivote nulo en columna {columna + 1}: "
                f"F{fila_pivote + 1} ↔ F{fila_intercambio + 1}; "
                "se intercambian las mismas filas en P y los multiplicadores previos de L."
            )
            pivote = matriz_u[fila_pivote][columna]

        # Guarda cada multiplicador en L y aplica el reemplazo de fila en U.
        for fila in range(fila_pivote + 1, m):
            if matriz_u[fila][columna] == 0:
                continue
            multiplicador = matriz_u[fila][columna] / pivote
            # El índice de L identifica la fila pivote, aunque U omita columnas sin pivote.
            matriz_l[fila][fila_pivote] = multiplicador
            for j in range(columna, n):
                matriz_u[fila][j] -= multiplicador * matriz_u[fila_pivote][j]
            registrar_paso(
                f"F{fila + 1} ← F{fila + 1} − ({multiplicador})·F{fila_pivote + 1}; "
                f"L[{fila + 1},{fila_pivote + 1}] = {multiplicador}."
            )
        fila_pivote += 1

    # Comprueba exactamente que los factores reconstruyan A con sus filas permutadas.
    producto_pa = multiplicar_matrices(matriz_p, matriz_a)
    producto_lu = multiplicar_matrices(matriz_l, matriz_u)
    return ResultadoLU(
        matriz_a, matriz_p, matriz_l, matriz_u, producto_pa, producto_lu,
        son_matrices_iguales(producto_lu, producto_pa), pasos,
    )


def resolver_sistema_lu(factores: ResultadoLU, datos_b: list[Any]) -> ResultadoSistemaLU:
    """Resuelve A·x=b mediante L·y=P·b y U·x=y con factores cuadrados."""

    # Verifica que LU sea aplicable y que A tenga solución única por este método.
    matriz_a, matriz_l, matriz_u = factores.matriz_a, factores.matriz_l, factores.matriz_u
    n = len(matriz_a)
    if len(matriz_a[0]) != n:
        raise ValueError("La resolución por sustitución LU requiere una matriz A cuadrada.")
    if not factores.es_correcta:
        raise ValueError("No se puede resolver: la verificación L·U = P·A falló.")
    if len(datos_b) != n:
        raise ValueError(f"El vector b debe contener {n} componentes; recibió {len(datos_b)}.")
    vector_b = [parsear_fraccion(valor) for valor in datos_b]
    if any(matriz_u[i][i] == 0 for i in range(n)):
        raise ValueError("U tiene un pivote diagonal nulo: A no tiene solución única por LU.")
    vector_pb = [fila[0] for fila in multiplicar_matrices(
        factores.matriz_p, [[valor] for valor in vector_b]
    )]

    # Resuelve L·y=P·b desde la primera fila hacia abajo y registra cada estado.
    aumentada_l = [matriz_l[i][:] + [vector_pb[i]] for i in range(n)]
    pasos_adelante = [PasoSistemaLU("Inicio de [L | P·b].", [r[:] for r in aumentada_l])]
    vector_y: list[Fraction] = []
    for i in range(n):
        suma = sum((matriz_l[i][j] * vector_y[j] for j in range(i)), Fraction(0))
        valor_y = (vector_pb[i] - suma) / matriz_l[i][i]
        vector_y.append(valor_y)
        pasos_adelante.append(PasoSistemaLU(
            f"y{i + 1} = ((P·b){i + 1} − Σ L[{i + 1},j]·yj) / L[{i + 1},{i + 1}] "
            f"= ({vector_pb[i]} − {suma}) / {matriz_l[i][i]} = {valor_y}.",
            [r[:] for r in aumentada_l],
        ))
        for fila in range(i + 1, n):
            multiplicador = aumentada_l[fila][i]
            if multiplicador == 0:
                continue
            for j in range(n + 1):
                aumentada_l[fila][j] -= multiplicador * aumentada_l[i][j]
            pasos_adelante.append(PasoSistemaLU(
                f"F{fila + 1} ← F{fila + 1} − ({multiplicador})·F{i + 1}.",
                [r[:] for r in aumentada_l],
            ))

    # Resuelve U·x=y desde la última fila hacia arriba y registra las operaciones.
    aumentada_u = [matriz_u[i][:] + [vector_y[i]] for i in range(n)]
    pasos_atras = [PasoSistemaLU("Inicio de [U | y].", [r[:] for r in aumentada_u])]
    vector_x = [Fraction(0) for _ in range(n)]
    for i in range(n - 1, -1, -1):
        suma = sum((matriz_u[i][j] * vector_x[j] for j in range(i + 1, n)), Fraction(0))
        valor_x = (vector_y[i] - suma) / matriz_u[i][i]
        vector_x[i] = valor_x
        pasos_atras.append(PasoSistemaLU(
            f"x{i + 1} = (y{i + 1} − Σ U[{i + 1},j]·xj) / U[{i + 1},{i + 1}] "
            f"= ({vector_y[i]} − {suma}) / {matriz_u[i][i]} = {valor_x}.",
            [r[:] for r in aumentada_u],
        ))
        pivote = aumentada_u[i][i]
        aumentada_u[i] = [valor / pivote for valor in aumentada_u[i]]
        pasos_atras.append(PasoSistemaLU(
            f"F{i + 1} ← F{i + 1} / ({pivote}).", [r[:] for r in aumentada_u],
        ))
        for fila in range(i):
            multiplicador = aumentada_u[fila][i]
            if multiplicador == 0:
                continue
            for j in range(n + 1):
                aumentada_u[fila][j] -= multiplicador * aumentada_u[i][j]
            pasos_atras.append(PasoSistemaLU(
                f"F{fila + 1} ← F{fila + 1} − ({multiplicador})·F{i + 1}.",
                [r[:] for r in aumentada_u],
            ))

    # Sustituye x en la ecuación original para confirmar la solución obtenida.
    producto_ax_matriz = multiplicar_matrices(matriz_a, [[valor] for valor in vector_x])
    producto_ax = [fila[0] for fila in producto_ax_matriz]
    return ResultadoSistemaLU(
        factores, vector_b, vector_pb, vector_y, vector_x, producto_ax,
        producto_ax == vector_b, pasos_adelante, pasos_atras,
    )
