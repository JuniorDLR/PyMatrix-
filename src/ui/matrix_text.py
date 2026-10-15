"""Lectura de matrices pegadas como texto para las vistas de PyMatrix.

Admite filas por Enter o punto y coma y números enteros, decimales o fracciones.
Elaborado por: Grupo x.
"""

import re

from src.core.exact_math import MatrizF, crear_matriz, parsear_fraccion


def leer_matriz_texto(texto: str, nombre: str = "A") -> MatrizF:
    """Interpreta filas separadas por saltos o ';', y columnas por espacios, tabuladores o comas."""

    contenido = texto.strip()
    if not contenido:
        raise ValueError(f"Ingrese la matriz {nombre} antes de calcular.")
    if contenido.count("[") != contenido.count("]") or contenido.count("(") != contenido.count(")"):
        raise ValueError(f"La matriz {nombre} tiene corchetes o paréntesis incompletos.")
    contenido = re.sub(r"\]\s*,\s*\[", "\n", contenido).replace(";", "\n")
    filas = []
    for numero_fila, linea in enumerate(contenido.splitlines(), start=1):
        linea = linea.strip().strip("[]() ")
        if linea:
            if re.search(r",\s*,|^,|,$", linea):
                raise ValueError(f"La matriz {nombre} tiene una celda vacía en la fila {numero_fila}.")
            valores = [valor for valor in re.split(r"[,\s]+", linea) if valor]
            fila = []
            for numero_columna, valor in enumerate(valores, start=1):
                try:
                    fila.append(parsear_fraccion(valor))
                except (ValueError, TypeError, ZeroDivisionError) as error:
                    raise ValueError(
                        f"Matriz {nombre}, fila {numero_fila}, columna {numero_columna}: "
                        f"'{valor}' no es un número válido."
                    ) from error
            filas.append(fila)
    return crear_matriz(filas)


def leer_vector_texto(texto: str, longitud: int) -> list:
    """Lee b como fila o columna y exige exactamente `longitud` entradas.

    Acepta tanto vector fila ('1/2 3') como vector columna ('1/2\\n3').
    """
    if not texto.strip():
        raise ValueError("Ingrese el vector b para resolver Ax=b.")
    matriz = leer_matriz_texto(texto)
    if len(matriz) == 1:
        vector = list(matriz[0])
    elif all(len(fila) == 1 for fila in matriz):
        vector = [fila[0] for fila in matriz]
    else:
        raise ValueError("Escriba b como un vector fila o columna, sin columnas adicionales.")
    if len(vector) != longitud:
        raise ValueError(f"El vector b necesita {longitud} componentes; recibió {len(vector)}.")
    return vector
