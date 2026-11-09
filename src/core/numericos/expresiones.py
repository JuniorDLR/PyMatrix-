"""Evaluación controlada de funciones reales de una variable."""

import ast
import math
from dataclasses import dataclass


FUNCIONES = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "exp": math.exp, "log": math.log, "sqrt": math.sqrt, "abs": abs,
}
CONSTANTES = {"pi": math.pi, "e": math.e}
OPERADORES = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)
UNARIOS = (ast.UAdd, ast.USub)


def numero_real(texto: str, nombre: str) -> float:
    """Acepta decimales y fracciones finitas sin ejecutar expresiones."""
    from fractions import Fraction

    try:
        valor = float(Fraction(texto.strip()))
    except (ValueError, ZeroDivisionError, OverflowError) as error:
        raise ValueError(f"{nombre} debe ser un número finito o una fracción válida.") from error
    if not math.isfinite(valor):
        raise ValueError(f"{nombre} debe ser finito.")
    return valor


def _validar(nodo: ast.AST) -> None:
    if isinstance(nodo, ast.Expression):
        _validar(nodo.body)
    elif isinstance(nodo, ast.Constant):
        try:
            finito = type(nodo.value) in (int, float) and math.isfinite(float(nodo.value))
        except OverflowError:
            finito = False
        if not finito:
            raise ValueError("Solo se permiten constantes numéricas finitas.")
    elif isinstance(nodo, ast.Name):
        if nodo.id not in {"x", *CONSTANTES}:
            raise ValueError(f"El nombre '{nodo.id}' no está permitido.")
    elif isinstance(nodo, ast.BinOp) and isinstance(nodo.op, OPERADORES):
        _validar(nodo.left)
        _validar(nodo.right)
    elif isinstance(nodo, ast.UnaryOp) and isinstance(nodo.op, UNARIOS):
        _validar(nodo.operand)
    elif isinstance(nodo, ast.Call):
        if not isinstance(nodo.func, ast.Name) or nodo.func.id not in FUNCIONES:
            raise ValueError("Función no permitida. Usa sin, cos, tan, exp, log, sqrt o abs.")
        if len(nodo.args) != 1 or nodo.keywords:
            raise ValueError("Cada función requiere un solo argumento.")
        _validar(nodo.args[0])
    else:
        raise ValueError("Expresión no permitida. Usa x, números, +, -, *, /, ** y funciones autorizadas.")


def _evaluar(nodo: ast.AST, x: float) -> float:
    try:
        if isinstance(nodo, ast.Constant):
            valor = float(nodo.value)
        elif isinstance(nodo, ast.Name):
            valor = x if nodo.id == "x" else CONSTANTES[nodo.id]
        elif isinstance(nodo, ast.UnaryOp):
            operando = _evaluar(nodo.operand, x)
            valor = operando if isinstance(nodo.op, ast.UAdd) else -operando
        elif isinstance(nodo, ast.Call):
            try:
                valor = float(FUNCIONES[nodo.func.id](_evaluar(nodo.args[0], x)))
            except ValueError as error:
                raise ValueError(f"La función no está definida en x={x:.10g}.") from error
        elif isinstance(nodo, ast.BinOp):
            izquierda = _evaluar(nodo.left, x)
            derecha = _evaluar(nodo.right, x)
            if isinstance(nodo.op, ast.Add):
                valor = izquierda + derecha
            elif isinstance(nodo.op, ast.Sub):
                valor = izquierda - derecha
            elif isinstance(nodo.op, ast.Mult):
                valor = izquierda * derecha
            elif isinstance(nodo.op, ast.Div):
                valor = izquierda / derecha
            else:
                if abs(derecha) > 64:
                    raise ValueError("El exponente debe estar entre -64 y 64.")
                valor = izquierda ** derecha
                if isinstance(valor, complex):
                    raise ValueError("La función no es real en este punto.")
        else:
            raise ValueError("Expresión no permitida.")
    except (ArithmeticError, OverflowError) as error:
        raise ValueError(f"La función no está definida en x={x:.10g}.") from error
    if not math.isfinite(valor):
        raise ValueError(f"La función no es finita en x={x:.10g}.")
    return valor


def _factores_denominador(nodo: ast.AST) -> tuple[ast.AST, ...]:
    """Conserva factores que pueden anular un denominador sin cambiar la función."""
    if isinstance(nodo, ast.BinOp) and isinstance(nodo.op, ast.Mult):
        return _factores_denominador(nodo.left) + _factores_denominador(nodo.right)
    if isinstance(nodo, ast.BinOp) and isinstance(nodo.op, ast.Pow):
        return _factores_denominador(nodo.left)
    return (nodo,)


def _guardas(arbol: ast.AST) -> tuple[ast.AST, ...]:
    guardas: list[ast.AST] = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.BinOp) and isinstance(nodo.op, ast.Div):
            guardas.extend(_factores_denominador(nodo.right))
        if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name) and nodo.func.id == "tan":
            guardas.append(ast.Call(func=ast.Name(id="cos", ctx=ast.Load()), args=nodo.args, keywords=[]))
    return tuple(guardas)


def _continua_global(nodo: ast.AST) -> bool:
    """Certifica expresiones construidas solo con operaciones continuas en R."""
    if isinstance(nodo, ast.Expression):
        return _continua_global(nodo.body)
    if isinstance(nodo, (ast.Constant, ast.Name)):
        return True
    if isinstance(nodo, ast.UnaryOp):
        return _continua_global(nodo.operand)
    if isinstance(nodo, ast.BinOp):
        if isinstance(nodo.op, (ast.Add, ast.Sub, ast.Mult)):
            return _continua_global(nodo.left) and _continua_global(nodo.right)
        if isinstance(nodo.op, ast.Pow):
            return (
                isinstance(nodo.right, ast.Constant)
                and type(nodo.right.value) is int
                and nodo.right.value >= 0
                and _continua_global(nodo.left)
            )
        return False
    if isinstance(nodo, ast.Call):
        return nodo.func.id in {"sin", "cos", "exp", "abs"} and _continua_global(nodo.args[0])
    return False


@dataclass(frozen=True)
class FuncionReal:
    expresion: str
    arbol: ast.Expression
    guardas: tuple[ast.AST, ...]
    continuidad_global: bool

    def evaluar(self, x: float) -> float:
        if not math.isfinite(x):
            raise ValueError("x debe ser finito.")
        return _evaluar(self.arbol.body, x)

    def barrera_entre(self, a: float, b: float) -> bool:
        """Separa puntos si un denominador o coseno de tan cruza cero."""
        for guarda in self.guardas:
            try:
                fa, fb = _evaluar(guarda, a), _evaluar(guarda, b)
            except ValueError:
                return True
            if fa == 0 or fb == 0 or (fa < 0 < fb) or (fb < 0 < fa):
                return True
        return False

    def verificar_intervalo(self, a: float, b: float, muestras: int = 1024) -> None:
        """Descarta discontinuidades observables; la continuidad general no es decidible aquí."""
        previo = a
        self.evaluar(a)
        for indice in range(1, muestras + 1):
            actual = a + (b - a) * indice / muestras
            self.evaluar(actual)
            if self.barrera_entre(previo, actual):
                raise ValueError("Hay una discontinuidad o asíntota en el intervalo; elige otro.")
            previo = actual


def compilar_funcion(texto: str) -> FuncionReal:
    """Compila una expresión AST con lista blanca; nunca ejecuta eval()."""
    expresion = texto.strip()
    if not expresion or len(expresion) > 256:
        raise ValueError("Escribe una función de hasta 256 caracteres.")
    if "^" in expresion:
        raise ValueError("Usa ** para potencias; ^ no significa potencia en Python.")
    try:
        arbol = ast.parse(expresion, mode="eval")
    except SyntaxError as error:
        raise ValueError("La función está mal escrita; revisa paréntesis y operadores.") from error
    if sum(1 for _ in ast.walk(arbol)) > 80:
        raise ValueError("La función es demasiado compleja.")
    _validar(arbol)
    return FuncionReal(expresion, arbol, _guardas(arbol), _continua_global(arbol))
