"""Implementación del Método de Newton-Raphson para búsqueda de raíces.

Programa 9 - Calculadora de Álgebra Lineal (PyMatrix)
Docente: José Andrés Munguía Cortez - FIA UAM
Librerías autorizadas: SymPy (derivación simbólica), NumPy (evaluación numérica),
Pandas (organización tabular) y SciPy (contraste opcional).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd
import sympy as sp

# Símbolo estándar de la variable independiente
X_SYM = sp.Symbol("x", real=True)

# Umbral predeterminado de derivada nula / crítica
TOL_DERIVADA_DEFAULT = 1e-12

EstadoProceso = Literal[
    "convergencia",
    "derivada_nula",
    "derivada_cercana_cero",
    "max_iteraciones",
    "no_finito",
    "oscilacion_detectada",
    "error_evaluacion",
]


@dataclass(frozen=True)
class PasoNewton:
    """Representa una iteración individual del algoritmo de Newton-Raphson."""

    i: int
    xi: float
    f_xi: float
    df_xi: float
    xi1: float
    error_abs: float
    error_rel_pct: float | None
    residuo_i: float
    detalle_procedimiento: str


@dataclass
class ResultadoNewton:
    """Resultado global de la ejecución del método de Newton-Raphson."""

    expresion_str: str
    expresion_sympy: sp.Expr
    derivada_sympy: sp.Expr
    derivada_str: str
    x0: float
    tolerancia: float
    tipo_criterio: Literal["absoluto", "relativo"]
    max_iteraciones: int
    tol_derivada: float
    pasos: list[PasoNewton] = field(default_factory=list)
    raiz_aprox: float | None = None
    residuo_final: float | None = None
    iteraciones_realizadas: int = 0
    estado: EstadoProceso = "max_iteraciones"
    mensaje_estado: str = ""
    tabla_pandas: pd.DataFrame | None = None
    contraste_scipy: dict | None = None

    @property
    def convergio(self) -> bool:
        return self.estado == "convergencia"


def compilar_expresion_sympy(expresion_str: str) -> tuple[sp.Expr, sp.Expr]:
    """Interpreta la función f(x) y calcula su derivada analítica f'(x) mediante SymPy.

    Valida que la expresión solo dependa de la variable 'x' o constantes,
    y que sea matemáticamente analizable.
    """
    texto = expresion_str.strip()
    if not texto:
        raise ValueError("Debe ingresar una expresión para f(x).")

    # Mapeo de nombres comunes en español o atajos habituales
    transformaciones_locales = {
        "sen": sp.sin,
        "tg": sp.tan,
        "ln": sp.log,
        "e": sp.E,
        "pi": sp.pi,
        "PI": sp.pi,
        "x": X_SYM,
    }

    try:
        f_expr = sp.sympify(texto, locals=transformaciones_locales)
    except Exception as err:
        raise ValueError(
            f"Error al interpretar la expresión matemática '{texto}': {err}"
        ) from err

    # Validar que los símbolos libres no contengan variables ajenas a 'x'
    simbolos_libres = f_expr.free_symbols
    simbolos_no_x = {s for s in simbolos_libres if s.name != "x"}
    if simbolos_no_x:
        nombres = ", ".join(s.name for s in simbolos_no_x)
        raise ValueError(
            f"La función contiene variables o símbolos no autorizados: {nombres}. "
            "Únicamente se permite la variable 'x' y constantes matemáticas (e, pi)."
        )

    # Cálculo analítico de la primera derivada mediante SymPy
    try:
        df_expr = sp.diff(f_expr, X_SYM)
    except Exception as err:
        raise ValueError(
            f"No fue posible calcular la derivada simbólica de la función: {err}"
        ) from err

    return f_expr, df_expr


def evaluar_sympy(expr: sp.Expr, valor_x: float) -> float:
    """Evalúa numéricamente una expresión SymPy en un punto x dado de forma robusta."""
    try:
        res = expr.subs(X_SYM, valor_x).evalf()
        val = float(res)
    except Exception as err:
        raise ValueError(
            f"Fallo al evaluar la expresión en x = {valor_x}: {err}"
        ) from err

    if not math.isfinite(val):
        raise ValueError(f"La evaluación en x = {valor_x} produjo un valor no finito ({val}).")

    return val


def ejecutar_newton_raphson(
    expresion_str: str,
    x0: float,
    tolerancia: float = 1e-4,
    tipo_criterio: Literal["absoluto", "relativo"] = "absoluto",
    max_iteraciones: int = 50,
    tol_derivada: float = TOL_DERIVADA_DEFAULT,
) -> ResultadoNewton:
    """Ejecuta el algoritmo iterativo de Newton-Raphson conforme a las pautas de clase.

    Parámetros:
        expresion_str: Expresión matemática en formato SymPy (ej: 'exp(-x) - x')
        x0: Valor inicial de la aproximación
        tolerancia: Tolerancia de convergencia
        tipo_criterio: 'absoluto' (|xi+1 - xi| < tol) o 'relativo' (|xi+1 - xi|/|xi+1| * 100 < tol)
        max_iteraciones: Límite de iteraciones permitidas
        tol_derivada: Umbral para declarar derivada nula o críticamente cercana a cero

    Retorna:
        ResultadoNewton con el historial completo, tabla pandas, gráficas y estado.
    """
    # Validaciones previas ("Fail-Fast")
    if not math.isfinite(x0):
        raise ValueError("El valor inicial x0 debe ser un número real finito.")
    if tolerancia <= 0 or not math.isfinite(tolerancia):
        raise ValueError("La tolerancia debe ser un número positivo y finito.")
    if max_iteraciones < 1 or max_iteraciones > 1000:
        raise ValueError("El número máximo de iteraciones debe estar entre 1 y 1000.")

    f_sym, df_sym = compilar_expresion_sympy(expresion_str)
    derivada_str = str(df_sym)

    resultado = ResultadoNewton(
        expresion_str=expresion_str,
        expresion_sympy=f_sym,
        derivada_sympy=df_sym,
        derivada_str=derivada_str,
        x0=x0,
        tolerancia=tolerancia,
        tipo_criterio=tipo_criterio,
        max_iteraciones=max_iteraciones,
        tol_derivada=tol_derivada,
    )

    pasos: list[PasoNewton] = []
    x_actual = float(x0)
    historial_x: list[float] = [x_actual]

    for it in range(1, max_iteraciones + 1):
        # 1. Evaluación de f(xi)
        try:
            f_val = evaluar_sympy(f_sym, x_actual)
        except Exception as err:
            resultado.estado = "error_evaluacion"
            resultado.mensaje_estado = f"Error al evaluar f(x) en x_{it-1} = {x_actual}: {err}"
            break

        # 2. Evaluación de f'(xi)
        try:
            df_val = evaluar_sympy(df_sym, x_actual)
        except Exception as err:
            resultado.estado = "error_evaluacion"
            resultado.mensaje_estado = f"Error al evaluar f'(x) en x_{it-1} = {x_actual}: {err}"
            break

        # 3. Validación de derivada nula o cercana a cero (Sad Path)
        if df_val == 0.0:
            resultado.estado = "derivada_nula"
            resultado.mensaje_estado = (
                f"Proceso detenido en iteración {it}: La derivada analítica f'({x_actual}) es exactamente cero. "
                "La recta tangente es totalmente horizontal y no intersecta el eje x (división por cero indefinida)."
            )
            # Guardamos el intento fallido
            pasos.append(
                PasoNewton(
                    i=it,
                    xi=x_actual,
                    f_xi=f_val,
                    df_xi=df_val,
                    xi1=float("nan"),
                    error_abs=float("nan"),
                    error_rel_pct=None,
                    residuo_i=abs(f_val),
                    detalle_procedimiento=(
                        f"Iteración {it}: x_{it} = {x_actual:.6f}\n"
                        f"1) f(x_{it}) = {f_val:.6e}\n"
                        f"2) f'(x_{it}) = 0.000000 (DERIVADA NULA)\n"
                        "3) Fallo: No se puede dividir entre cero. Proceso abortado."
                    ),
                )
            )
            break

        if abs(df_val) < tol_derivada:
            resultado.estado = "derivada_cercana_cero"
            resultado.mensaje_estado = (
                f"Proceso detenido en iteración {it}: La derivada analítica |f'({x_actual})| = {abs(df_val):.3e} "
                f"es menor al umbral crítico ({tol_derivada:.1e}). Una pendiente casi plana provocaría un salto "
                "descontrolado fuera del dominio de convergencia."
            )
            pasos.append(
                PasoNewton(
                    i=it,
                    xi=x_actual,
                    f_xi=f_val,
                    df_xi=df_val,
                    xi1=float("nan"),
                    error_abs=float("nan"),
                    error_rel_pct=None,
                    residuo_i=abs(f_val),
                    detalle_procedimiento=(
                        f"Iteración {it}: x_{it} = {x_actual:.6f}\n"
                        f"1) f(x_{it}) = {f_val:.6e}\n"
                        f"2) f'(x_{it}) = {df_val:.6e} (|f'| < {tol_derivada:.1e})\n"
                        "3) Fallo: Pendiente casi nula. Salto inestable evitado."
                    ),
                )
            )
            break

        # 4. Cálculo de la nueva aproximación x_{i+1} = x_i - f(x_i)/f'(x_i)
        paso_dx = f_val / df_val
        x_siguiente = x_actual - paso_dx

        # 5. Control de valores no finitos (Overflow / NaN)
        if not math.isfinite(x_siguiente):
            resultado.estado = "no_finito"
            resultado.mensaje_estado = (
                f"Proceso detenido en iteración {it}: La aproximación x_{it+1} divergió a un valor no finito ({x_siguiente})."
            )
            break

        # 6. Cálculo del error aproximado
        error_abs = abs(x_siguiente - x_actual)
        if x_siguiente != 0.0:
            error_rel_pct = abs((x_siguiente - x_actual) / x_siguiente) * 100.0
        else:
            # Tratamiento seguro si x_{i+1} es 0 (evitar división por cero)
            error_rel_pct = None

        residuo_siguiente = abs(evaluar_sympy(f_sym, x_siguiente))

        # 7. Redacción didáctica del procedimiento (según formato de diapositivas 18-19)
        detalle = (
            f"Iteración {it}: x_i = {x_actual:.6f}\n"
            f"1) Evaluar función:   f(x_i)  = {f_val:.6f}\n"
            f"2) Evaluar derivada:  f'(x_i) = {df_val:.6f}\n"
            f"3) Aplicar fórmula:   x_(i+1) = {x_actual:.6f} - ({f_val:.6f}) / ({df_val:.6f}) = {x_siguiente:.6f}\n"
            f"4) Error absoluto:    ε_a = |{x_siguiente:.6f} - {x_actual:.6f}| = {error_abs:.6e}\n"
        )
        if error_rel_pct is not None:
            detalle += f"   Error relativo %:  ε_a(%) = {error_rel_pct:.4f}%\n"

        # 8. Verificación de Criterio de Parada
        cumple_tolerancia = False
        if tipo_criterio == "absoluto":
            cumple_tolerancia = error_abs < tolerancia
            detalle += f"5) ¿Detener? {error_abs:.4e} {'<' if cumple_tolerancia else '>'} {tolerancia:.4e} → {'SÍ: converge' if cumple_tolerancia else 'NO: continuar'}"
        else:
            if error_rel_pct is not None:
                cumple_tolerancia = error_rel_pct < tolerancia
                detalle += f"5) ¿Detener? {error_rel_pct:.4f}% {'<' if cumple_tolerancia else '>'} {tolerancia:.4f}% → {'SÍ: converge' if cumple_tolerancia else 'NO: continuar'}"
            else:
                cumple_tolerancia = error_abs < tolerancia
                detalle += f"5) ¿Detener? (x_(i+1)=0, evaluando absoluto) {error_abs:.4e} {'<' if cumple_tolerancia else '>'} {tolerancia:.4e} → {'SÍ: converge' if cumple_tolerancia else 'NO: continuar'}"

        paso_obj = PasoNewton(
            i=it,
            xi=x_actual,
            f_xi=f_val,
            df_xi=df_val,
            xi1=x_siguiente,
            error_abs=error_abs,
            error_rel_pct=error_rel_pct,
            residuo_i=residuo_siguiente,
            detalle_procedimiento=detalle,
        )
        pasos.append(paso_obj)

        if cumple_tolerancia:
            resultado.estado = "convergencia"
            resultado.raiz_aprox = x_siguiente
            resultado.residuo_final = residuo_siguiente
            resultado.iteraciones_realizadas = it
            resultado.mensaje_estado = (
                f"El método convergió exitosamente en {it} iteraciones.\n"
                f"• Raíz aproximada: x ≈ {x_siguiente:.8f}\n"
                f"• Error alcanzado: ε_a = {error_abs:.4e}"
                + (f" ({error_rel_pct:.4f}%)" if error_rel_pct is not None else "")
                + f"\n• Residuo |f(x_aprox)|: {residuo_siguiente:.4e} (cercano a 0)"
            )
            break

        # Detección de ciclos u oscilaciones (ej: x^3 - 2x + 2 oscilando entre 0 y 1)
        # Revisamos si x_siguiente ya apareció en el historial cercano
        for prev_idx, prev_x in enumerate(historial_x):
            if abs(x_siguiente - prev_x) < 1e-10 and (len(historial_x) - prev_idx) >= 2:
                resultado.estado = "oscilacion_detectada"
                resultado.raiz_aprox = x_siguiente
                resultado.residuo_final = residuo_siguiente
                resultado.iteraciones_realizadas = it
                resultado.mensaje_estado = (
                    f"Se detectó un ciclo u oscilación en la iteración {it}.\n"
                    f"El valor x_{it+1} = {x_siguiente:.6f} coincide con el valor previo x_{prev_idx} = {prev_x:.6f}.\n"
                    "El método está atrapado en un bucle periódico oscilante y no convergerá a una raíz desde este x0."
                )
                break

        if resultado.estado == "oscilacion_detectada":
            break

        x_actual = x_siguiente
        historial_x.append(x_actual)

    else:
        # Se agotaron las iteraciones sin cumplir tolerancia
        resultado.estado = "max_iteraciones"
        resultado.raiz_aprox = x_actual
        resultado.residuo_final = abs(evaluar_sympy(f_sym, x_actual))
        resultado.iteraciones_realizadas = max_iteraciones
        resultado.mensaje_estado = (
            f"Se alcanzó el número máximo permitido de iteraciones ({max_iteraciones}) "
            "sin satisfacer el criterio de convergencia especificado.\n"
            f"Última aproximación alcanzada: x ≈ {x_actual:.8f} con residuo |f(x)| = {resultado.residuo_final:.4e}."
        )

    resultado.pasos = pasos

    # Crear la tabla de Pandas obligatoria por las reglas técnicas
    if pasos:
        datos_tabla = []
        for p in pasos:
            datos_tabla.append({
                "i": p.i,
                "x_i": p.xi,
                "f(x_i)": p.f_xi,
                "f'(x_i)": p.df_xi,
                "x_(i+1)": p.xi1,
                "Error Absoluto (ε_a)": p.error_abs,
                "Error Relativo (%)": p.error_rel_pct if p.error_rel_pct is not None else np.nan,
                "Residuo |f(x_(i+1))|": p.residuo_i,
            })
        resultado.tabla_pandas = pd.DataFrame(datos_tabla)

    return resultado


def contraste_scipy_newton(
    expresion_str: str,
    x0: float,
    tolerancia: float = 1e-4,
    max_iteraciones: int = 50,
) -> dict:
    """Ejecuta scipy.optimize.newton ÚNICAMENTE como contraste opcional.

    Nota de cumplimiento docente: Esta función NO sustituye la implementación
    propia del equipo; sirve para verificar y contrastar en la interfaz.
    """
    import scipy.optimize as opt

    f_sym, df_sym = compilar_expresion_sympy(expresion_str)
    f_num = sp.lambdify(X_SYM, f_sym, "numpy")
    df_num = sp.lambdify(X_SYM, df_sym, "numpy")

    try:
        solucion, res = opt.newton(
            func=f_num,
            x0=x0,
            fprime=df_num,
            tol=tolerancia,
            maxiter=max_iteraciones,
            full_output=True,
            disp=False,
        )
        return {
            "exito": res.converged,
            "raiz": float(solucion),
            "iteraciones": res.iterations,
            "residuo": abs(float(f_num(solucion))),
            "mensaje": "Convergencia confirmada por scipy.optimize.newton"
            if res.converged
            else "SciPy no alcanzó convergencia dentro del límite",
        }
    except Exception as err:
        return {
            "exito": False,
            "raiz": None,
            "iteraciones": 0,
            "residuo": None,
            "mensaje": f"SciPy reportó excepción: {err}",
        }
