"""
Punto de entrada del Programa 1: abre la calculadora gráfica PyMatrix.
Tema de clase: sistemas de ecuaciones lineales y eliminación de Gauss.
Elaborado por: Grupo x
"""

import sys
import os

# Permite importar el paquete src al ejecutar este archivo desde otra carpeta.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ui.app import App


def main():
    """Crea la ventana principal y arranca el ciclo de eventos de la interfaz."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
