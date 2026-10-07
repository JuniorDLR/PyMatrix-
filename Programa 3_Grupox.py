"""
Punto de entrada del Programa 3: abre PyMatrix directamente en el módulo de vectores.
Temas de clase: vectores en Rn, combinación lineal, independencia lineal y Ax = b.
Restricción del curso: solo Python estándar, sin NumPy ni SciPy.
Elaborado por: Grupo x
"""

import sys
import os

# La consola de Windows puede no usar UTF-8 y fallaría con los símbolos matemáticos.
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Permite importar el paquete src al ejecutar este archivo desde otra carpeta.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ui.app import App


def main():
    """Abre la calculadora y muestra de inicio el módulo de vectores."""
    app = App()
    # Se difiere con after() para que la ventana exista antes de cambiar de módulo.
    app.after(100, lambda: app._show_module("vectores"))
    app.mainloop()


if __name__ == "__main__":
    main()
