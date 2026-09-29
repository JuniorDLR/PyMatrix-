"""
Utilidades auxiliares para la interfaz de consola CLI de la Calculadora de Álgebra Lineal.
Soporta entrada y formateo bidireccional de fracciones y decimales en todos los módulos.
"""

from typing import List, Tuple
from src.core.domain import formatear_numero, Matriz


def leer_numero(prompt: str) -> float:
    """Lee un número desde la consola. Acepta enteros, decimales ('0.5') o fracciones ('1/2', '-3/4')."""
    while True:
        entrada = input(prompt).strip()
        if not entrada:
            print("  ⚠️ La entrada no puede estar vacía. Intente de nuevo.")
            continue
        try:
            if "/" in entrada:
                partes = entrada.split("/")
                if len(partes) == 2:
                    num = float(partes[0].strip())
                    den = float(partes[1].strip())
                    if den == 0:
                        print("  ❌ Error: División por cero en la fracción. Ingrese un denominador válido.")
                        continue
                    return num / den
                else:
                    print("  ❌ Formato de fracción inválido. Use 'numerador/denominador' (ej. 3/4).")
                    continue
            return float(entrada)
        except ValueError:
            print(f"  ❌ Entrada no válida '{entrada}'. Ingrese un entero, decimal (ej. 2.5) o fracción (ej. 1/3).")


def leer_entero_positivo(prompt: str, min_val: int = 1, max_val: int = 10) -> int:
    """Solicita un entero en el rango [min_val, max_val]."""
    while True:
        try:
            val = int(input(prompt).strip())
            if min_val <= val <= max_val:
                return val
            print(f"  ⚠️ Ingrese un valor entre {min_val} y {max_val}.")
        except ValueError:
            print("  ❌ Debe ingresar un número entero válido.")


def imprimir_matriz(matriz: Matriz, modo: str = "fraccion") -> None:
    """Imprime una matriz formateada con alineación visual de columnas."""
    for fila in matriz:
        elementos = "  ".join(f"{formatear_numero(c, modo):>8}" for c in fila)
        print(f"  [ {elementos} ]")


def imprimir_matriz_aumentada(matriz: Matriz, modo: str = "fraccion") -> None:
    """Imprime una matriz aumentada [A | b] con la barra separadora."""
    for fila in matriz:
        coefs = fila[:-1]
        ti = fila[-1]
        coefs_str = "  ".join(f"{formatear_numero(c, modo):>8}" for c in coefs)
        print(f"  [ {coefs_str} | {formatear_numero(ti, modo):>8} ]")


def pausar() -> None:
    """Pausa la ejecución en consola hasta que el usuario presione ENTER."""
    input("\nPresione [ENTER] para continuar...")
