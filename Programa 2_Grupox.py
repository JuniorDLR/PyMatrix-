"""
UNIVERSIDAD AMERICANA (UAM)
Facultad de Ingeniería y Arquitectura (FIA)
Asignatura: Álgebra Lineal (MTM0120)

PROGRAMA 2: Reducción a Forma Escalonada Reducida (Gauss-Jordan) e Identificación de Columnas Pivote
Proyecto Integrador: Calculadora de Álgebra Lineal
"""

import sys
import os

# Asegurar codificación UTF-8 en salida estándar para caracteres Unicode (subíndices, flechas)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Asegurar que el directorio actual esté en PYTHONPATH para importaciones de módulos
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ui.app import App


def main():
    """Punto de entrada principal para el Programa 2 (Gauss-Jordan)."""
    # 1. Instanciar la aplicación interactiva de PyMatrix
    app = App()
    
    # 2. Ejecutar el bucle principal de la interfaz gráfica
    app.mainloop()


if __name__ == "__main__":
    main()
