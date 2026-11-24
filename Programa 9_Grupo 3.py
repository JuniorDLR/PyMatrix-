"""Programa 9 - Calculadora de Álgebra Lineal (PyMatrix).

Actividades de Programación en Python · Tercer Corte Evaluativo (Valor: 15 puntos)
Método abierto: Búsqueda de raíces por Newton-Raphson.
Facultad de Ingeniería y Arquitectura (FIA) - Universidad Americana (UAM)
Asignatura: Álgebra Lineal (MTM0120)
Docente: José Andrés Munguía Cortez
Grupo: Grupo 3 (De La Rocha - Armengol)
"""

import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Asegurar que el directorio raíz del proyecto esté en el PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ui.app import main

if __name__ == "__main__":
    # Inicia la suite completa integrada abriendo directamente el módulo de Newton-Raphson
    main(modulo_inicial="numericos")
