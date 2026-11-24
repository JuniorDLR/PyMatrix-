"""Pruebas unitarias para el módulo de Newton-Raphson (Programa 9)."""

import math
import pytest
import pandas as pd

from src.core.numericos.newton_raphson import (
    compilar_expresion_sympy,
    ejecutar_newton_raphson,
    contraste_scipy_newton,
)


def test_compilar_expresion_valida():
    f_sym, df_sym = compilar_expresion_sympy("x**3 - 2*x - 5")
    assert str(df_sym) == "3*x**2 - 2"


def test_compilar_expresion_con_alias():
    f_sym, df_sym = compilar_expresion_sympy("sen(x) + cos(x)")
    # En SymPy sen -> sin
    assert "cos(x)" in str(df_sym)
    assert "-sin(x)" in str(df_sym) or "sin(x)" in str(df_sym)


def test_compilar_variable_no_permitida():
    with pytest.raises(ValueError, match="símbolos no autorizados"):
        compilar_expresion_sympy("x**2 + y")


def test_compilar_expresion_vacia():
    with pytest.raises(ValueError, match="Debe ingresar una expresión"):
        compilar_expresion_sympy("   ")


def test_caso1_convergencia_exponencial():
    # Ejemplo 1 de clase: exp(-x) - x, x0=0, tol=1e-4
    res = ejecutar_newton_raphson("exp(-x) - x", 0.0, 1e-4)
    assert res.convergio
    assert res.iteraciones_realizadas == 4
    assert round(res.raiz_aprox, 6) == 0.567143
    assert res.residuo_final < 1e-12
    assert isinstance(res.tabla_pandas, pd.DataFrame)
    assert len(res.tabla_pandas) == 4


def test_caso1b_convergencia_polinomio():
    # Ejemplo cúbico: x^3 - 2x - 5, x0=2, tol=1e-4
    res = ejecutar_newton_raphson("x**3 - 2*x - 5", 2.0, 1e-4)
    assert res.convergio
    assert res.iteraciones_realizadas == 3
    assert round(res.raiz_aprox, 6) == 2.094551


def test_caso2_derivada_nula():
    # f(x) = x^2 - 4 con x0 = 0 -> f'(0) = 0
    res = ejecutar_newton_raphson("x**2 - 4", 0.0, 1e-4)
    assert not res.convergio
    assert res.estado == "derivada_nula"
    assert "cero" in res.mensaje_estado.lower()


def test_caso2b_derivada_cercana_cero():
    # f'(x) muy pequeña con umbral
    res = ejecutar_newton_raphson("x**10 - 1", 0.0001, 1e-4, tol_derivada=1e-3)
    assert res.estado == "derivada_cercana_cero"


def test_caso3_oscilacion_ciclo():
    # Diapositiva 32: x^3 - 2x + 2 con x0=0 cicla entre 0 y 1
    res = ejecutar_newton_raphson("x**3 - 2*x + 2", 0.0, 1e-4, max_iteraciones=20)
    assert res.estado == "oscilacion_detectada"
    assert not res.convergio


def test_caso3b_maximo_iteraciones():
    # Con pocas iteraciones permitidas se debe detener por max_iteraciones
    res = ejecutar_newton_raphson("x**3 - 2*x - 5", 2.0, 1e-12, max_iteraciones=2)
    assert res.estado == "max_iteraciones"
    assert res.iteraciones_realizadas == 2


def test_criterio_relativo():
    res = ejecutar_newton_raphson(
        "exp(-x) - x", 0.0, tolerancia=0.01, tipo_criterio="relativo"
    )
    assert res.convergio
    assert res.pasos[-1].error_rel_pct is not None
    assert res.pasos[-1].error_rel_pct < 0.01


def test_contraste_scipy():
    sc = contraste_scipy_newton("exp(-x) - x", 0.0, 1e-4)
    assert sc["exito"]
    assert round(sc["raiz"], 6) == 0.567143
