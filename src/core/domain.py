from dataclasses import dataclass, field
from typing import Literal

# Tipo alias para nuestra matriz
Matriz = list[list[float]]

@dataclass(frozen=True)
class PasoGauss:
    """Representa un paso intermedio en la reducción de Gauss."""
    descripcion: str
    matriz_estado: Matriz

@dataclass(frozen=True)
class SolucionUnica:
    tipo: Literal["Consistente Determinado"] = "Consistente Determinado"
    variables: list[float] = field(default_factory=list)

@dataclass(frozen=True)
class SolucionInfinita:
    tipo: Literal["Consistente Indeterminado"] = "Consistente Indeterminado"
    variables_libres: list[int] = field(default_factory=list)

@dataclass(frozen=True)
class SinSolucion:
    tipo: Literal["Inconsistente"] = "Inconsistente"
    mensaje: str = "El sistema no tiene solución (0 = k)."

ResultadoSistema = SolucionUnica | SolucionInfinita | SinSolucion
