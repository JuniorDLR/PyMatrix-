"""Jacobi y Gauss-Seidel con historial, validaciones y comparación."""

from dataclasses import dataclass
import math
from typing import Literal

from src.core.exact_math import parsear_fraccion
from src.core.domain import SolucionUnica
from src.core.gauss import resolver_gauss_jordan


Estado = Literal["tolerancia", "máximo", "posible divergencia", "no finito"]


@dataclass(frozen=True)
class PasoIterativo:
    numero: int
    valores: tuple[float, ...]
    error: float
    residuo: float


@dataclass(frozen=True)
class ResultadoIterativo:
    metodo: str
    pasos: tuple[PasoIterativo, ...]
    estado: Estado

    @property
    def solucion(self) -> tuple[float, ...]:
        return self.pasos[-1].valores if self.pasos else ()


@dataclass(frozen=True)
class ComparacionIterativa:
    matriz: tuple[tuple[float, ...], ...]
    vector: tuple[float, ...]
    inicial: tuple[float, ...]
    orden_filas: tuple[int, ...]
    dominante: bool
    criterio: Literal["infinito", "euclidiana"]
    jacobi: ResultadoIterativo
    seidel: ResultadoIterativo
    referencia: tuple[float, ...] | None


def _numero(texto: str, nombre: str) -> float:
    try:
        numero = float(parsear_fraccion(texto.strip()))
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as error:
        raise ValueError(f"{nombre} debe ser un número finito o fracción válida.") from error
    if not math.isfinite(numero):
        raise ValueError(f"{nombre} debe ser finito.")
    return numero


def _dominante(matriz: tuple[tuple[float, ...], ...]) -> bool:
    return all(
        abs(fila[i]) > sum(abs(valor) for j, valor in enumerate(fila) if j != i)
        for i, fila in enumerate(matriz)
    )


def _orden(matriz: tuple[tuple[float, ...], ...], estricto: bool) -> tuple[int, ...] | None:
    """Empareja cada columna diagonal con una fila distinta, sin cambiar variables."""
    n = len(matriz)
    opciones = []
    for columna in range(n):
        candidatas = []
        for fila in range(n):
            pivote = abs(matriz[fila][columna])
            otros = sum(abs(matriz[fila][j]) for j in range(n) if j != columna)
            if pivote > 0 and (not estricto or pivote > otros):
                candidatas.append(fila)
        opciones.append(sorted(candidatas, key=lambda fila: fila != columna))
    asignadas = [-1] * n

    def buscar(columna: int, usadas: set[int]) -> bool:
        for fila in opciones[columna]:
            if fila in usadas:
                continue
            usadas.add(fila)
            if asignadas[fila] == -1 or buscar(asignadas[fila], usadas):
                asignadas[fila] = columna
                return True
        return False

    if not all(buscar(columna, set()) for columna in range(n)):
        return None
    return tuple(asignadas.index(columna) for columna in range(n))


def _residuo(matriz: tuple[tuple[float, ...], ...], vector: tuple[float, ...], x: tuple[float, ...]) -> float:
    return max(abs(sum(a * valor for a, valor in zip(fila, x)) - b)
               for fila, b in zip(matriz, vector))


def _iterar(metodo: str, matriz: tuple[tuple[float, ...], ...], vector: tuple[float, ...],
            inicial: tuple[float, ...], tolerancia: float, maximo: int,
            criterio: Literal["infinito", "euclidiana"]) -> ResultadoIterativo:
    previo = inicial
    pasos: list[PasoIterativo] = []
    crecimientos = 0
    for numero in range(1, maximo + 1):
        actual = list(previo)
        try:
            for i, fila in enumerate(matriz):
                suma = sum(fila[j] * (actual[j] if metodo == "Gauss-Seidel" and j < i else previo[j])
                           for j in range(len(fila)) if j != i)
                actual[i] = (vector[i] - suma) / fila[i]
            if not all(math.isfinite(valor) for valor in actual):
                return ResultadoIterativo(metodo, tuple(pasos), "no finito")
            valores = tuple(actual)
            cambios = tuple(nuevo - viejo for nuevo, viejo in zip(valores, previo))
            error = max(abs(cambio) for cambio in cambios) if criterio == "infinito" else math.hypot(*cambios)
            residuo = _residuo(matriz, vector, valores)
        except (ArithmeticError, OverflowError):
            return ResultadoIterativo(metodo, tuple(pasos), "no finito")
        if not math.isfinite(error) or not math.isfinite(residuo):
            return ResultadoIterativo(metodo, tuple(pasos), "no finito")
        pasos.append(PasoIterativo(numero, valores, error, residuo))
        if error <= tolerancia:
            return ResultadoIterativo(metodo, tuple(pasos), "tolerancia")
        if len(pasos) > 1 and error > pasos[-2].error * 1.5 and residuo > pasos[-2].residuo * 1.5:
            crecimientos += 1
        else:
            crecimientos = 0
        if crecimientos >= 3:
            return ResultadoIterativo(metodo, tuple(pasos), "posible divergencia")
        previo = valores
    return ResultadoIterativo(metodo, tuple(pasos), "máximo")


def comparar_metodos(matriz_texto: list[list[str]], vector_texto: list[str],
                     inicial_texto: list[str], tolerancia_texto: str, maximo_texto: str,
                     reordenar: bool = True,
                     criterio: Literal["infinito", "euclidiana"] = "infinito") -> ComparacionIterativa:
    if criterio not in ("infinito", "euclidiana"):
        raise ValueError("La norma debe ser infinito o euclidiana.")
    n = len(matriz_texto)
    if not 1 <= n <= 10 or any(len(fila) != n for fila in matriz_texto):
        raise ValueError("A debe ser cuadrada, de orden entre 1 y 10.")
    if len(vector_texto) != n or len(inicial_texto) != n:
        raise ValueError("b y x⁽⁰⁾ deben tener exactamente una entrada por fila de A.")
    matriz = tuple(tuple(_numero(valor, f"A[{i+1},{j+1}]") for j, valor in enumerate(fila))
                   for i, fila in enumerate(matriz_texto))
    vector = tuple(_numero(valor, f"b[{i+1}]") for i, valor in enumerate(vector_texto))
    inicial = tuple(_numero(valor, f"x⁽⁰⁾[{i+1}]") for i, valor in enumerate(inicial_texto))
    tolerancia = _numero(tolerancia_texto, "La tolerancia")
    if tolerancia <= 0:
        raise ValueError("La tolerancia debe ser positiva.")
    texto_maximo = maximo_texto.strip()
    if (not texto_maximo.isascii() or not texto_maximo.isdigit()
            or len(texto_maximo) > 4 or not 1 <= int(texto_maximo) <= 1000):
        raise ValueError("El máximo de iteraciones debe ser un entero entre 1 y 1000.")
    maximo = int(texto_maximo)
    orden = tuple(range(n))
    if reordenar:
        mejor = _orden(matriz, True)
        if mejor is None and any(matriz[i][i] == 0 for i in range(n)):
            mejor = _orden(matriz, False)
        if mejor is not None:
            orden = mejor
    if any(matriz[orden[i]][i] == 0 for i in range(n)):
        raise ValueError("Hay ceros en la diagonal y no se encontró un reordenamiento válido de filas.")
    matriz_ordenada = tuple(matriz[i] for i in orden)
    vector_ordenado = tuple(vector[i] for i in orden)
    jacobi = _iterar("Jacobi", matriz_ordenada, vector_ordenado, inicial, tolerancia, maximo, criterio)
    seidel = _iterar("Gauss-Seidel", matriz_ordenada, vector_ordenado, inicial, tolerancia, maximo, criterio)
    try:
        aumentada = [list(fila) + [b] for fila, b in zip(matriz_ordenada, vector_ordenado)]
        _, solucion, _ = resolver_gauss_jordan(aumentada)
        referencia = tuple(float(valor) for valor in solucion.variables) if isinstance(solucion, SolucionUnica) else None
    except (ValueError, ArithmeticError, OverflowError):
        referencia = None
    return ComparacionIterativa(matriz_ordenada, vector_ordenado, inicial, orden,
                               _dominante(matriz_ordenada), criterio, jacobi, seidel, referencia)
