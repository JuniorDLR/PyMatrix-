"""
Punto de entrada del Programa 4: abre la calculadora integrada PyMatrix.
Temas de clase: Gauss-Jordan, vectores, operaciones matriciales, Ax = b y teoremas clave.
Elaborado por: Grupo x
"""

import os
import sys

# La consola de Windows puede no usar UTF-8 y fallaría con los símbolos matemáticos.
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (OSError, ValueError):
        pass

# Permite importar el paquete src al ejecutar este archivo desde otra carpeta.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ui.app import App


def main():
    """Crea la ventana principal con todos los módulos y arranca la interfaz."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
