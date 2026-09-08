from fractions import Fraction
from dataclasses import dataclass, field
from typing import Literal

# Alias de tipo: matriz aumentada m x (n+1) donde la última columna son términos independientes
Matriz = list[list[float]]

SUB_DIGITOS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def a_subindice(num: int) -> str:
    """Convierte un número entero a su representación en caracteres de subíndice Unicode (ej. 1 -> '₁', 12 -> '₁₂')."""
    return str(num).translate(SUB_DIGITOS)



def formatear_fraccion(valor: float, max_denom: int = 2000) -> str:
    """Convierte cualquier valor float a su representación exacta en fracción irreducible.
    
    Usa la librería estándar de Python (fractions.Fraction).
    Si el valor es entero (ej. 3.0, -2.0, 0.0), retorna '3', '-2', '0'.
    Si el valor es decimal (ej. 0.5, 1.6667), retorna '1/2', '5/3'.
    
    Args:
        valor: Número en punto flotante
        max_denom: Denominador máximo para aproximaciones (2000 evita fracciones raras como 16667/10000)
        
    Returns:
        Cadena con la fracción (ej. '3/4', '-7/2', '5')
    """
    if abs(valor) < 1e-10:
        return "0"
    
    # Redondear a 9 decimales para limpiar residuos infinitesimales de coma flotante
    val_redondeado = round(valor, 9)
    f = Fraction(val_redondeado).limit_denominator(max_denom)
    
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def formatear_decimal(valor: float, max_decimales: int = 4) -> str:
    """Convierte un valor float a su representación en formato decimal legible.
    
    Si el valor es entero (ej. 3.0, -2.0, 0.0), retorna '3', '-2', '0'.
    Si el valor es decimal, redondea hasta max_decimales y elimina ceros redundantes.
    
    Args:
        valor: Número en punto flotante
        max_decimales: Cantidad máxima de cifras decimales (por defecto 4)
        
    Returns:
        Cadena con el número en formato decimal (ej. '0.5', '1.3333', '-2')
    """
    if abs(valor) < 1e-10:
        return "0"
    
    val_redondeado = round(valor, max_decimales)
    if abs(val_redondeado - round(val_redondeado)) < 1e-10:
        return str(int(round(val_redondeado)))
    
    return f"{val_redondeado:.{max_decimales}f}".rstrip("0").rstrip(".")


def formatear_numero(valor: float, modo: str = "fraccion", max_decimales: int = 4) -> str:
    """Formatea un número según el modo activo: 'fraccion' o 'decimal'.
    
    Args:
        valor: Número en punto flotante
        modo: 'fraccion' para fracciones irreducibles, 'decimal' para números decimales
        max_decimales: Decimales para el modo decimal
        
    Returns:
        Representación en cadena formateada
    """
    if modo == "decimal":
        return formatear_decimal(valor, max_decimales)
    return formatear_fraccion(valor)


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
    Ejemplo: X1 = 2/3 + 3/4*X2 - 1/2*X4
    
    Atributos:
        constante: Término independiente
        terminos: Tupla de Termino (coef * variable_libre)
    """
    constante: float
    terminos: tuple[Termino, ...] = field(default_factory=tuple)
    
    def a_string(self, var_names: list[str] | None = None, modo: str = "fraccion") -> str:
        """Convierte la expresión a string legible en fracciones o decimales.
        
        Args:
            var_names: Nombres opcionales para variables libres (ej: ["X1", "X2", "X3", "X4"])
            modo: 'fraccion' o 'decimal'
            
        Returns:
            String formateado: "2/3 + 3/4·X2 - 1/2·X4" o "X2 (libre)"
        """
        if not self.terminos and abs(self.constante) < 1e-10:
            return "0"
        
        # Caso variable libre pura: constante=0 y único término con coef=1
        if abs(self.constante) < 1e-10 and len(self.terminos) == 1 and abs(self.terminos[0].coef - 1.0) < 1e-10:
            idx = self.terminos[0].var_libre_idx
            var_name = var_names[idx] if var_names and idx < len(var_names) else f"t{a_subindice(idx+1)}"
            return f"{var_name} (libre)"
        
        parts = []
        # Parte constante (término independiente)
        if abs(self.constante) > 1e-10:
            parts.append(formatear_numero(self.constante, modo))
        
        # Parte parametrica: coeficiente * variable_libre
        for t in self.terminos:
            if var_names and t.var_libre_idx < len(var_names):
                var_name = var_names[t.var_libre_idx]
            else:
                var_name = f"t{a_subindice(t.var_libre_idx+1)}"
            
            coef_val = t.coef
            coef_abs_str = formatear_numero(abs(coef_val), modo)
            
            if abs(coef_val - 1.0) < 1e-10:
                parts.append(f"+ {var_name}")
            elif abs(coef_val - (-1.0)) < 1e-10:
                parts.append(f"- {var_name}")
            elif coef_val > 0:
                parts.append(f"+ {coef_abs_str}·{var_name}")
            else:
                parts.append(f"- {coef_abs_str}·{var_name}")
        
        if not parts:
            return "0"
        
        # Primer término sin el '+' inicial si lo tiene
        first = parts[0]
        if first.startswith("+ "):
            first = first[2:]
            
        result = first
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
    
    def a_strings(self, num_variables: int, modo: str = "fraccion") -> list[str]:
        """Genera lista de ecuaciones formateadas para todas las variables.
        
        Args:
            num_variables: Total de variables (n)
            modo: 'fraccion' o 'decimal'
            
        Returns:
            Lista de strings: ["X1 = 2 + 3·X2", "X2 = X2 (libre)", ...]
        """
        var_names = [f"x{a_subindice(i+1)}" for i in range(num_variables)]
        lines = []
        
        for i in range(num_variables):
            if i in self.variables_basicas:
                expr = self.variables_basicas[i]
                lines.append(f"{var_names[i]} = {expr.a_string(var_names, modo=modo)}")
            elif i in self.variables_libres:
                lines.append(f"{var_names[i]} = {var_names[i]} (libre)")
        return lines