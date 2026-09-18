"""
UNIVERSIDAD AMERICANA (UAM)
Facultad de Ingeniería y Arquitectura (FIA)
Asignatura: Álgebra Lineal (MTM0120)

PROGRAMA 3: Módulo de Vectores en ℝⁿ, Operaciones Matriciales y Ecuaciones Matriciales
Proyecto Integrador: Calculadora de Álgebra Lineal — PyMatrix

Funcionalidades implementadas:
  1. Operaciones básicas con vectores en ℝⁿ:
       u + v, u - v, c·u, c·v, u·v (producto punto), ||u|| y ||v|| (normas)
  2. Combinación Lineal: evalúa si b ∈ Gen{v₁, ..., vₖ} usando [v₁ ... vₖ | b] → Gauss-Jordan
  3. Independencia / Dependencia Lineal: inspección directa y sistema homogéneo [v | 0]
  4. Suma y Resta de Matrices: A ± B con validación de dimensiones m × n
  5. Multiplicación por Escalar: c · A
  6. Multiplicación Matricial A · B: con desglose del triple bucle for/for/for
  7. Producto Matriz-Vector A · x: regla fila-vector y combinación lineal de columnas
  8. Ecuación Matricial A x = b: resolución mediante [A | b] con Gauss-Jordan

RESTRICCIÓN TÉCNICA (contrato didáctico):
  Solo Python estándar: listas, bucles, condicionales y funciones propias.
  Prohibido NumPy, SciPy o funciones de álgebra avanzada de math.
"""

import sys
import os

# Asegurar codificación UTF-8 en salida estándar para caracteres Unicode
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Asegurar que el directorio raíz del proyecto esté en PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ui.app import App


def main():
    """Punto de entrada principal del Programa 3 — Vectores y Operaciones Matriciales."""
    app = App()
    # Abrir directamente en el módulo de Vectores al iniciar
    app.after(100, lambda: app._show_module("vectores"))
    app.mainloop()


if __name__ == "__main__":
    main()
