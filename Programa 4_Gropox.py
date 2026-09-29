"""Redirección a Programa 4_Grupox.py para corregir error tipográfico."""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from main import menu_principal

if __name__ == "__main__":
    menu_principal()
