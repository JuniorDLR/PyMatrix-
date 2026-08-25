# Importamos sys y path para asegurar que los imports de módulos locales (src) funcionen bien.
import sys
import os

# Aseguramos que el directorio actual esté en la ruta para importaciones absolutas
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importamos nuestra aplicación principal desde el módulo UI construido con customtkinter
from src.ui.app import App

def main():
    # Paso 1: Instanciar la aplicación
    # La clase App extiende de ctk.CTk y configura la ventana inicial, 
    # botones y caja de texto para los resultados.
    app = App()
    
    # Paso 2: Ejecutar el bucle principal (Main Loop) de la interfaz gráfica.
    # Esto mantendrá la ventana abierta esperando las interacciones del usuario.
    app.mainloop()

# Verificamos si este archivo se está ejecutando directamente y no importado.
if __name__ == "__main__":
    main()
