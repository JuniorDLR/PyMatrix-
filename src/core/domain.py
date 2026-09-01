from dataclasses import dataclass, field
from typing import Literal

# Alias de tipo: matriz aumentada m x (n+1) donde la última columna son términos independientes
Matriz = list[list[float]]


@dataclass(frozen=True)
class PasoGauss:
    """Representa un estado intermedio durante la eliminación de Gauss-Jordan.
    
    Atributos:
        descripcion: Texto legible de la operación realizada (ej: "Pivoteo: Intercambio fila 1 con 2")
        matriz_estado: Copia profunda de la matriz en ese momento
    """
    descripcion: str
    matriz_estado: Matriz


@dataclass(frozen=True)
class SolucionUnica:
    """Sistema consistente determinado: exactamente una solución.
    
    Atributos:
        tipo: Etiqueta fija "Consistente Determinado"
        variables: Lista con los valores de X1, X2, ..., Xn
    """
    tipo: Literal["Consistente Determinado"] = "Consistente Determinado"
    variables: list[float] = field(default_factory=list)


@dataclass(frozen=True)
class SolucionInfinita:
    """Sistema consistente indeterminado: infinitas soluciones.
    
    Atributos:
        tipo: Etiqueta fija "Consistente Indeterminado"
        variables_libres: Índices 0-based de las variables que son parámetros libres
    """
    tipo: Literal["Consistente Indeterminado"] = "Consistente Indeterminado"
    variables_libres: list[int] = field(default_factory=list)


@dataclass(frozen=True)
class SinSolucion:
    """Sistema inconsistente: no tiene solución (0 = k con k ≠ 0).
    
    Atributos:
        tipo: Etiqueta fija "Inconsistente"
        mensaje: Explicación legible del por qué no hay solución
    """
    tipo: Literal["Inconsistente"] = "Inconsistente"
    mensaje: str = "El sistema no tiene solución (0 = k)."


# Union type para el resultado de la clasificación del sistema
ResultadoSistema = SolucionUnica | SolucionInfinita | SinSolucion


@dataclass(frozen=True)
class Termino:
    """Un término de la forma: coeficiente * variable_libre.
    
    Atributos:
        coef: Coeficiente numérico (ej: 3, -1.5)
        var_libre_idx: Índice 0-based de la variable libre (ej: 1 para X2)
    """
    coef: float
    var_libre_idx: int


@dataclass(frozen=True)
class ExpresionParametrica:
    """Expresión algebraica completa: constante + suma(términos).
    
    Representa una variable básica en función de las variables libres.
    Ejemplo: X1 = 2 + 3*X2 - 1*X4  →  constante=2, terminos=[(3, X2), (-1, X4)]
    
    Atributos:
        constante: Término independiente (ej: 2)
        terminos: Tupla de Termino (coef * variable_libre)
    """
    constante: float
    terminos: tuple[Termino, ...] = field(default_factory=tuple)
    
    def a_string(self, var_names: list[str] | None = None) -> str:
        """Convierte la expresión a string legible.
        
        Args:
            var_names: Nombres opcionales para variables libres (ej: ["X1", "X2", "X3", "X4"])
            
        Returns:
            String formateado: "2 + 3·X2 - 1·X4" o "X2" si es variable libre pura
        """
        if not self.terminos and self.constante == 0:
            return "0"
        
        parts = []
        # Parte constante (término independiente)
        if self.constante != 0:
            parts.append(f"{self.constante:.4g}".rstrip('.'))
        
        # Parte parametrica: coeficiente * variable_libre
        for t in self.terminos:
            if var_names and t.var_libre_idx < len(var_names):
                var_name = var_names[t.var_libre_idx]
            else:
                var_name = f"t{t.var_libre_idx+1}"
            
            coef_str = f"{t.coef:.4g}".rstrip('.')
            # Formateo bonito: ±1 se omite, signos explícitos
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
        
        # Unir: primer término sin signo +, resto con espacios
        result = parts[0]
        for p in parts[1:]:
            result += f" {p}"
        return result


@dataclass(frozen=True)
class SolucionGeneral:
    """Solución completa parametrizada del sistema (válida para los 3 casos).
    
    Contiene toda la información para reconstruir la solución:
    - Variables básicas expresadas en términos de variables libres
    - Matriz RREF (forma escalonada reducida por filas)
    - Matriz REF (forma escalonada, antes de ceros arriba)
    
    Atributos:
        tipo: Clasificación del sistema
        variables_basicas: Dict {idx_variable: ExpresionParametrica}
        variables_libres: Tupla de índices 0-based de variables libres
        matriz_rref: Matriz en Forma Escalonada Reducida (RREF)
        matriz_ref: Matriz en Forma Escalonada (REF, solo ceros abajo)
    """
    tipo: Literal["Consistente Determinado", "Consistente Indeterminado", "Inconsistente"]
    variables_basicas: dict[int, ExpresionParametrica]
    variables_libres: tuple[int, ...]
    matriz_rref: Matriz
    matriz_ref: Matriz
    
    def a_strings(self, num_variables: int) -> list[str]:
        """Genera lista de ecuaciones formateadas para todas las variables.
        
        Args:
            num_variables: Total de variables (n)
            
        Returns:
            Lista de strings: ["X1 = 2 + 3·X2", "X2 = X2 (libre)", ...]
        """
        var_names = [f"X{i+1}" for i in range(num_variables)]
        lines = []
        
        for i in range(num_variables):
            if i in self.variables_basicas:
                expr = self.variables_basicas[i]
                lines.append(f"{var_names[i]} = {expr.a_string(var_names)}")
            elif i in self.variables_libres:
                lines.append(f"{var_names[i]} = {var_names[i]} (libre)")
        
        return lines