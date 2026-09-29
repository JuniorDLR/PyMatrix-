"""
UNIVERSIDAD AMERICANA (UAM)
Facultad de Ingeniería y Arquitectura (FIA)
Asignatura: Álgebra Lineal (MTM0120)

PROGRAMA 4: Calculadora Integrada de Álgebra Lineal — PyMatrix

Punto de entrada para ejecutar la calculadora completa, que integra:
  1. Sistemas de ecuaciones lineales con eliminación de Gauss y Gauss-Jordan.
  2. Operaciones con vectores, combinación lineal e independencia lineal.
  3. Operaciones matriciales, producto matriz-vector y resolución de Ax = b.
  4. Pestañas de teoremas fundamentales en cada módulo.
"""

import os
import sys


if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (OSError, ValueError):
        pass

# Permite importar el paquete src al ejecutar este archivo desde otra carpeta.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ui.app import App


def main():
    """Inicia la calculadora integrada de Álgebra Lineal."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
