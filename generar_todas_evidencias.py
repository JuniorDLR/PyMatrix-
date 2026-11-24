"""Genera todas las capturas de pantalla de evidencia requeridas para el informe del Programa 9."""

import ctypes
import os
import sys
import time

sys.path.insert(0, os.path.abspath("."))

from PIL import ImageGrab
from src.ui.app import App

os.makedirs("evidencias", exist_ok=True)

user32 = ctypes.windll.user32
hdesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
if hdesk:
    user32.SetThreadDesktop(hdesk)

app = App(modulo_inicial="inicio")
app.state("zoomed")
app.update_idletasks()
app.update()
time.sleep(0.8)


def snap(filename: str):
    app.update_idletasks()
    app.update()
    time.sleep(0.6)
    img = ImageGrab.grab(all_screens=True)
    img.save(os.path.join("evidencias", filename), "PNG")
    print(f"✓ Guardado: evidencias/{filename}")


# 1. Evidencia de integración: Menú Principal / Dashboard
app._show_module("inicio")
snap("01_integracion_menu_principal.png")

# 2. Navegar a Métodos Numéricos -> Newton-Raphson
app._show_module("numericos")
view = app.numericos_view.newton

# Caso 1: Convergencia (Tabla)
view._cargar_ejemplo("Caso 1 (e⁻ˣ - x, x₀=0)")
view._calcular()
view.tabs_salida.set("📊 Tabla de Iteraciones")
snap("02_caso1_convergencia_tabla.png")

# Caso 1: Gráfica con Tangentes
view.tabs_salida.set("📈 Gráfica y Tangentes")
snap("03_caso1_convergencia_grafica.png")

# Caso 1: Procedimiento Paso a Paso
view.tabs_salida.set("📝 Procedimiento Paso a Paso")
snap("04_caso1_convergencia_procedimiento.png")

# Contraste SciPy
view._contrastar_scipy()
snap("05_caso1_contraste_scipy.png")

# Caso 2: Derivada nula (x^2 - 4, x0=0)
view._cargar_ejemplo("Caso 2 (x² - 4, x₀=0)")
view._calcular()
view.tabs_salida.set("📊 Tabla de Iteraciones")
snap("06_caso2_derivada_nula.png")

# Caso 3: Oscilación periódica (x^3 - 2x + 2, x0=0)
view._cargar_ejemplo("Caso 3 (x³ - 2x + 2, x₀=0)")
view._calcular()
view.tabs_salida.set("📊 Tabla de Iteraciones")
snap("07_caso3_oscilacion_no_convergencia.png")

app.destroy()
if hdesk:
    user32.CloseDesktop(hdesk)

print("¡Todas las evidencias generadas con éxito!")
