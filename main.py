"""
UNIVERSIDAD AMERICANA (UAM)
Facultad de Ingeniería y Arquitectura (FIA)
Asignatura: Álgebra Lineal (MTM0120)

CALCULADORA DE ÁLGEBRA LINEAL — PROGRAMA 4 (PROYECTO INTEGRADOR)
Menú Principal de la Calculadora Modular

Estructura de Arquitectura Modular:
  • modulos/modulo_sistemas.py      -> Módulo 1: Sistemas de Ecuaciones (SEL)
  • modulos/modulo_vectores.py      -> Módulo 2: Vectores e Independencia Lineal
  • modulos/modulo_matrices.py      -> Módulo 3: Operaciones Matriciales e Inversa
  • modulos/modulo_determinantes.py -> Módulo 4: Determinantes y Propiedades
  • teoremas/resumen_teoremas.py    -> Resumen en pantalla de Teoremas y Fundamentos Clave
"""

import sys
import os

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Asegurar que la raíz del proyecto esté en el path de importaciones
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from modulos.modulo_sistemas import ejecutar_modulo_sistemas
from modulos.modulo_vectores import ejecutar_modulo_vectores
from modulos.modulo_matrices import ejecutar_modulo_matrices
from modulos.modulo_determinantes import ejecutar_modulo_determinantes
from teoremas.resumen_teoremas import resumen_general
from modulos.utilidades_cli import pausar


BANNER_PRINCIPAL = """
======================================================================
       UNIVERSIDAD AMERICANA (UAM) • ÁLGEBRA LINEAL (MTM0120)
       CALCULADORA DE ÁLGEBRA LINEAL — PROGRAMA 4 (MODULAR CLI)
======================================================================
"""


def menu_principal():
    """Menú principal interactivo de la Calculadora de Álgebra Lineal."""
    modo_global = "fraccion"

    while True:
        print(BANNER_PRINCIPAL)
        print(f" Formato numérico global: [{modo_global.upper()}] (Fracciones / Decimales)")
        print("-" * 70)
        print(" 1. Módulo 1: Sistemas de Ecuaciones Lineales (SEL - Gauss y Gauss-Jordan)")
        print(" 2. Módulo 2: Vectores e Independencia Lineal (L.I. / L.D. con reducción por filas)")
        print(" 3. Módulo 3: Álgebra de Matrices, Traspuesta y Matriz Inversa")
        print(" 4. Módulo 4: Determinantes y Propiedades")
        print(" 0. Ver Resumen General de Teoremas del Curso")
        print(" 5. Alternar Formato Numérico Global (Fracción ↔ Decimal)")
        print(" 6. Iniciar Interfaz Gráfica (GUI CustomTkinter)")
        print(" 7. Salir")
        print("-" * 70)

        opcion = input("Seleccione una opción [0-7]: ").strip()

        if opcion == "1":
            modo_global = ejecutar_modulo_sistemas(modo_global)
        elif opcion == "2":
            modo_global = ejecutar_modulo_vectores(modo_global)
        elif opcion == "3":
            modo_global = ejecutar_modulo_matrices(modo_global)
        elif opcion == "4":
            modo_global = ejecutar_modulo_determinantes(modo_global)
        elif opcion == "0":
            print(resumen_general())
            pausar()
        elif opcion == "5":
            modo_global = "decimal" if modo_global == "fraccion" else "fraccion"
            print(f"\n  ✓ Formato global actualizado a: [{modo_global.upper()}]")
            pausar()
        elif opcion == "6":
            print("\nIniciando interfaz gráfica interactiva...")
            try:
                from src.ui.app import App
                app = App()
                app.mainloop()
            except Exception as e:
                print(f"  ❌ No se pudo iniciar la interfaz gráfica: {e}")
                pausar()
        elif opcion == "7":
            print("\n¡Gracias por utilizar la Calculadora de Álgebra Lineal! Hasta pronto.\n")
            break
        else:
            print("  ⚠️ Opción no válida. Ingrese un número entre 0 y 7.")


if __name__ == "__main__":
    menu_principal()
