"""
UNIVERSIDAD AMERICANA (UAM)
Facultad de Ingeniería y Arquitectura (FIA)
Asignatura: Álgebra Lineal (MTM0120)

PROGRAMA 4: Calculadora de Álgebra Lineal (Módulo II: Vectores e Independencia Lineal)
Proyecto Integrador — Segundo Corte

Cumple con todos los requerimientos del Programa 4:
  1. Arquitectura Modular Profesional con paquetes modulos/ y teoremas/.
  2. Logotipos de consola (ASCII Art) exactos para cada módulo.
  3. Opción '0. Ver Teoremas Clave del Módulo' en todos los módulos.
  4. Evaluación de Independencia Lineal (L.I. o L.D.) mediante reducción por filas
     de la matriz de columnas en el sistema homogéneo Ax = 0, conteo explícito de
     posiciones pivote y variables libres, y veredicto teórico.
  5. Soporte bidireccional de fracciones y decimales en todos los módulos.
  6. Acceso dual: Menú interactivo de consola CLI y/o Interfaz Gráfica (GUI CustomTkinter).
"""

import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (OSError, ValueError):
        pass

# Asegurar que el directorio raíz esté en sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import menu_principal


def main():
    """Punto de entrada principal para el Programa 4."""
    # Si se pasa el argumento --gui, lanza directamente la interfaz gráfica
    if "--gui" in sys.argv:
        try:
            from src.ui.app import App
            app = App()
            app.mainloop()
        except Exception as e:
            print(f"Error al iniciar GUI: {e}")
            menu_principal()
    else:
        # Por defecto ejecuta el Menú Principal Modular de consola CLI
        menu_principal()


if __name__ == "__main__":
    main()
