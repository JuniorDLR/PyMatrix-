"""Punto de entrada principal para PyMatrix.

Permite ejecutar la aplicación directamente usando:
    python main.py
o mediante:
    python "Programa 2_Grupox.py"
"""
import sys
import os

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Asegurar que el directorio raíz del proyecto esté en el PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ui.app import main

if __name__ == "__main__":
    main()
