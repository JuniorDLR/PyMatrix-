from dataclasses import dataclass, field
from typing import Literal

Matriz = list[list[float]]

@dataclass(frozen=True)
class PasoGauss:
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


@dataclass(frozen=True)
class Termino:
    coef: float
    var_libre_idx: int

@dataclass(frozen=True)
class ExpresionParametrica:
    constante: float
    terminos: tuple[Termino, ...] = field(default_factory=tuple)
    
    def a_string(self, var_names: list[str] | None = None) -> str:
        if not self.terminos and self.constante == 0:
            return "0"
        
        parts = []
        if self.constante != 0:
            parts.append(f"{self.constante:.4g}".rstrip('.'))
        
        for t in self.terminos:
            if var_names and t.var_libre_idx < len(var_names):
                var_name = var_names[t.var_libre_idx]
            else:
                var_name = f"t{t.var_libre_idx+1}"
            
            coef_str = f"{t.coef:.4g}".rstrip('.')
            if coef_str == "1":
                parts.append(f"+ {var_name}")
            elif coef_str == "-1":
                parts.append(f"- {var_name}")
            elif t.coef > 0:
                parts.append(f"+ {coef_str}·{var_name}")
            else:
                parts.append(f"- {abs(t.coef):.4g}·{var_name}")
        
        if not parts:
            return "0"
        
        result = parts[0]
        for p in parts[1:]:
            result += f" {p}"
        return result


@dataclass(frozen=True)
class SolucionGeneral:
    tipo: Literal["Consistente Determinado", "Consistente Indeterminado", "Inconsistente"]
    variables_basicas: dict[int, ExpresionParametrica]
    variables_libres: tuple[int, ...]
    matriz_rref: Matriz
    matriz_ref: Matriz
    
    def a_strings(self, num_variables: int) -> list[str]:
        var_names = [f"X{i+1}" for i in range(num_variables)]
        lines = []
        
        for i in range(num_variables):
            if i in self.variables_basicas:
                expr = self.variables_basicas[i]
                lines.append(f"{var_names[i]} = {expr.a_string(var_names)}")
            elif i in self.variables_libres:
                lines.append(f"{var_names[i]} = {var_names[i]} (libre)")
        
        return lines