"""
Tipos de datos del dominio (pasos de Gauss, tipos de solución, expresiones paramétricas).
Incluye utilidades para mostrar números como fracciones o decimales.
Tema de clase: sistemas de ecuaciones lineales (Gauss / Gauss-Jordan).
Elaborado por: Grupo x
"""
from fractions import Fraction
from dataclasses import dataclass, field
from typing import Literal

# Matriz aumentada m x (n+1): la última columna son los términos independientes
Matriz = list[list[float]]

SUB_DIGITOS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def a_subindice(num: int) -> str:
    """Convierte un entero a subíndices Unicode (1 -> '₁', 12 -> '₁₂')."""
    return str(num).translate(SUB_DIGITOS)


def formatear_fraccion(valor: float, max_denom: int = 2000) -> str:
    """Convierte un float a fracción irreducible en texto (0.5 -> '1/2', 3.0 -> '3').

    max_denom limita el denominador para evitar fracciones raras como 16667/10000.
    """
    # Tolerancia en vez de == 0: los float acumulan error de redondeo
    if abs(valor) < 1e-10:
        return "0"
    
    # Redondear a 9 decimales para limpiar residuos infinitesimales de coma flotante
    val_redondeado = round(valor, 9)
    f = Fraction(val_redondeado).limit_denominator(max_denom)
    
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def formatear_decimal(valor: float, max_decimales: int = 4) -> str:
    """Convierte un float a decimal legible, redondeado a max_decimales y sin ceros sobrantes.

    Devuelve texto como '0.5', '1.3333' o '-2' (los enteros salen sin punto).
    """
    if abs(valor) < 1e-10:
        return "0"
    
    val_redondeado = round(valor, max_decimales)
    if abs(val_redondeado - round(val_redondeado)) < 1e-10:
        return str(int(round(val_redondeado)))
    
    return f"{val_redondeado:.{max_decimales}f}".rstrip("0").rstrip(".")


def formatear_numero(valor: float, modo: str = "fraccion", max_decimales: int = 4) -> str:
    """Formatea un número según el modo ('fraccion' o 'decimal') y devuelve el texto resultante."""
    if modo == "decimal":
        return formatear_decimal(valor, max_decimales)
    return formatear_fraccion(valor)


def convertir_texto_a_modo(texto: str, modo_destino: str, max_decimales: int = 4) -> str:
    """Convierte un texto numérico (fracción o decimal) al modo destino ('1/2' <-> '0.5').

    Si el texto está vacío o no es convertible, devuelve el texto original sin cambios.
    """
    s = texto.strip()
    if not s:
        return texto
    try:
        if "/" in s:
            partes = s.split("/")
            if len(partes) == 2:
                num = float(partes[0].strip())
                den = float(partes[1].strip())
                # Denominador ~0: la división no está definida, se deja el texto igual
                if abs(den) < 1e-12:
                    return texto
                val = num / den
            else:
                return texto
        else:
            val = float(s)
        return formatear_numero(val, modo=modo_destino, max_decimales=max_decimales)
    except Exception:
        return texto


@dataclass(frozen=True)
class PasoGauss:
    """Estado intermedio de la eliminación: descripcion de la operación y copia de la matriz en ese momento."""
    descripcion: str
    matriz_estado: Matriz


@dataclass(frozen=True)
class SolucionUnica:
    """Sistema consistente determinado: una única solución.

    'variables' guarda los valores de x1, x2, ..., xn.
    """
    tipo: Literal["Consistente Determinado"] = "Consistente Determinado"
    variables: list[float] = field(default_factory=list)


@dataclass(frozen=True)
class SolucionInfinita:
    """Sistema consistente indeterminado: infinitas soluciones.

    'variables_libres' guarda los índices (desde 0) de las variables que actúan como parámetros.
    """
    tipo: Literal["Consistente Indeterminado"] = "Consistente Indeterminado"
    variables_libres: list[int] = field(default_factory=list)


@dataclass(frozen=True)
class SinSolucion:
    """Sistema inconsistente: no tiene solución (aparece una fila 0 = k con k ≠ 0).

    'mensaje' explica en texto por qué no hay solución.
    """
    tipo: Literal["Inconsistente"] = "Inconsistente"
    mensaje: str = "El sistema no tiene solución (0 = k)."


# Union type para el resultado de la clasificación del sistema
ResultadoSistema = SolucionUnica | SolucionInfinita | SinSolucion


@dataclass(frozen=True)
class Termino:
    """Término coef * variable_libre; var_libre_idx es el índice desde 0 de la variable (1 para x2)."""
    coef: float
    var_libre_idx: int


@dataclass(frozen=True)
class ExpresionParametrica:
    """Variable básica expresada como constante + suma de términos de variables libres.

    Ejemplo: x1 = 2/3 + 3/4·x2 - 1/2·x4.
    """
    constante: float
    terminos: tuple[Termino, ...] = field(default_factory=tuple)
    
    def a_string(self, var_names: list[str] | None = None, modo: str = "fraccion") -> str:
        """Devuelve la expresión como texto, ej. '2/3 + 3/4·x2 - 1/2·x4' o 'x2 (libre)'.

        Recibe nombres opcionales de variables (var_names) y el modo ('fraccion' o 'decimal').
        """
        if not self.terminos and abs(self.constante) < 1e-10:
            return "0"
        
        # Caso variable libre pura: constante=0 y único término con coef=1
        if abs(self.constante) < 1e-10 and len(self.terminos) == 1 and abs(self.terminos[0].coef - 1.0) < 1e-10:
            idx = self.terminos[0].var_libre_idx
            var_name = var_names[idx] if var_names and idx < len(var_names) else f"t{a_subindice(idx+1)}"
            return f"{var_name} (libre)"
        
        parts = []
        if abs(self.constante) > 1e-10:
            parts.append(formatear_numero(self.constante, modo))
        
        for t in self.terminos:
            if var_names and t.var_libre_idx < len(var_names):
                var_name = var_names[t.var_libre_idx]
            else:
                var_name = f"t{a_subindice(t.var_libre_idx+1)}"
            
            coef_val = t.coef
            coef_abs_str = formatear_numero(abs(coef_val), modo)
            
            # Coeficientes ±1 se escriben sin el "1·" (convención algebraica)
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
        
        # El primer término no lleva '+' inicial
        first = parts[0]
        if first.startswith("+ "):
            first = first[2:]
            
        result = first
        for p in parts[1:]:
            result += f" {p}"
        return result


@dataclass(frozen=True)
class SolucionGeneral:
    """Solución parametrizada del sistema: tipo, variables básicas {índice: expresión} y libres.

    Guarda además las matrices REF (ceros abajo) y RREF (ceros arriba y abajo).
    """
    tipo: Literal["Consistente Determinado", "Consistente Indeterminado", "Inconsistente"]
    variables_basicas: dict[int, ExpresionParametrica]
    variables_libres: tuple[int, ...]
    matriz_rref: Matriz
    matriz_ref: Matriz
    
    def a_strings(self, num_variables: int, modo: str = "fraccion") -> list[str]:
        """Devuelve una ecuación en texto por variable, ej. ['x₁ = 2 + 3·x₂', 'x₂ = x₂ (libre)'].

        Recibe el total de variables (num_variables) y el modo ('fraccion' o 'decimal').
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