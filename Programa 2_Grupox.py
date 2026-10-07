"""
Punto de entrada del Programa 2: abre la calculadora gráfica PyMatrix.
Tema de clase: reducción a forma escalonada reducida (Gauss-Jordan) y columnas pivote.
Elaborado por: Grupo x
"""

import sys
import os

# La consola de Windows puede no usar UTF-8 y fallaría con subíndices y flechas.
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Permite importar el paquete src al ejecutar este archivo desde otra carpeta.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ui.app import App


def main():
    """Crea la ventana principal y arranca el ciclo de eventos de la interfaz."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
