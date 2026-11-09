"""Descomposición y conversión explicada entre bases 10 y 2."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Termino:
    digito: int
    base: int
    exponente: int
    aporte: int


@dataclass(frozen=True)
class ConversionPosicional:
    origen: int
    entrada: str
    valor: int
    decimal: str
    binario: str
    terminos_decimales: tuple[Termino, ...]
    terminos_binarios: tuple[Termino, ...]
    divisiones: tuple[tuple[int, int, int], ...]


def _terminos(digitos: str, base: int) -> tuple[Termino, ...]:
    return tuple(
        Termino(int(digito), base, exponente, int(digito) * base ** exponente)
        for exponente, digito in zip(range(len(digitos) - 1, -1, -1), digitos)
    )


def convertir_posicional(texto: str, base_origen: int) -> ConversionPosicional:
    """Conserva el signo y muestra cada potencia, incluidos los ceros."""
    if base_origen not in (2, 10):
        raise ValueError("La base de origen debe ser 10 o 2.")
    entrada = texto.strip()
    patron = r"[+-]?[01]+" if base_origen == 2 else r"[+-]?[0-9]+"
    if len(entrada) > 128 or re.fullmatch(patron, entrada) is None:
        raise ValueError(f"Escribe un entero válido de hasta 128 dígitos en base {base_origen}.")
    digitos = entrada.lstrip("+-").lstrip("0") or "0"
    if base_origen == 10:
        magnitud = int(digitos)
    else:
        magnitud = sum(int(digito) * 2 ** exponente
                       for exponente, digito in zip(
                           range(len(digitos) - 1, -1, -1), digitos))
    divisiones: list[tuple[int, int, int]] = []
    cociente = magnitud
    bits: list[str] = []
    if cociente == 0:
        bits.append("0")
    while cociente > 0:
        siguiente, resto = divmod(cociente, 2)
        divisiones.append((cociente, siguiente, resto))
        bits.append(str(resto))
        cociente = siguiente
    binario = "".join(reversed(bits))
    decimal = str(magnitud)
    signo = -1 if entrada.startswith("-") and magnitud else 1
    return ConversionPosicional(
        base_origen, entrada, signo * magnitud,
        ("-" if signo < 0 else "") + decimal,
        ("-" if signo < 0 else "") + binario,
        _terminos(decimal, 10), _terminos(binario, 2), tuple(divisiones),
    )
