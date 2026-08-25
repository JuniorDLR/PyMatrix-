import customtkinter as ctk
from src.core.gauss import resolver_gauss, verificar_solucion
from src.core.domain import SolucionUnica, SolucionInfinita, SinSolucion

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PyMatrix - Calculadora de Álgebra Lineal")
        self.geometry("900x700")
        
        # Configuración general de estilo
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # Titulo
        self.lbl_title = ctk.CTkLabel(self, text="PyMatrix: Eliminación de Gauss", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_title.pack(pady=15)
        
        # Frame de Dimensiones
        self.frame_dims = ctk.CTkFrame(self)
        self.frame_dims.pack(pady=10, padx=20, fill="x")
        
        self.lbl_eq = ctk.CTkLabel(self.frame_dims, text="Número de Ecuaciones (m):")
        self.lbl_eq.grid(row=0, column=0, padx=10, pady=10)
        self.entry_m = ctk.CTkEntry(self.frame_dims, width=60)
        self.entry_m.grid(row=0, column=1, padx=10, pady=10)
        self.entry_m.insert(0, "3")
        
        self.lbl_var = ctk.CTkLabel(self.frame_dims, text="Número de Variables (n):")
        self.lbl_var.grid(row=0, column=2, padx=10, pady=10)
        self.entry_n = ctk.CTkEntry(self.frame_dims, width=60)
        self.entry_n.grid(row=0, column=3, padx=10, pady=10)
        self.entry_n.insert(0, "3")
        
        self.btn_generar = ctk.CTkButton(self.frame_dims, text="Generar Matriz", command=self.generar_matriz)
        self.btn_generar.grid(row=0, column=4, padx=20, pady=10)
        
        # Contenedor para matriz de entrada (con scroll por si es grande)
        self.scroll_matriz = ctk.CTkScrollableFrame(self, height=200)
        self.scroll_matriz.pack(pady=10, padx=20, fill="x")
        
        self.matriz_entries = []
        
        self.btn_resolver = ctk.CTkButton(self, text="Resolver Sistema", command=self.resolver, fg_color="green", hover_color="darkgreen")
        self.btn_resolver.pack(pady=10)
        self.btn_resolver.configure(state="disabled")
        
        # Área de resultados (Textbox)
        self.txt_resultados = ctk.CTkTextbox(self, width=860, height=200, font=ctk.CTkFont(family="Consolas", size=14))
        self.txt_resultados.pack(pady=10, padx=20, fill="both", expand=True)
        
    def generar_matriz(self):
        try:
            m = int(self.entry_m.get())
            n = int(self.entry_n.get())
        except ValueError:
            self.mostrar_resultado("Error: Por favor, ingrese números enteros válidos para m y n.\n")
            return
            
        if m <= 0 or n <= 0:
            self.mostrar_resultado("Error: Las dimensiones deben ser mayores que 0.\n")
            return
            
        # Limpiar frame matriz previo
        for widget in self.scroll_matriz.winfo_children():
            widget.destroy()
            
        self.matriz_entries = []
        
        # Crear la cuadricula (n variables + 1 independiente)
        for i in range(m):
            fila_entries = []
            for j in range(n + 1):
                # Etiqueta visual (X1, X2... o =)
                if j < n:
                    lbl_txt = f"X{j+1}"
                else:
                    lbl_txt = "="
                    
                entry = ctk.CTkEntry(self.scroll_matriz, width=50, justify="center")
                entry.grid(row=i, column=j*2, padx=5, pady=5)
                entry.insert(0, "0") # Valor por defecto
                
                lbl = ctk.CTkLabel(self.scroll_matriz, text=lbl_txt)
                lbl.grid(row=i, column=j*2+1, padx=2)
                
                fila_entries.append(entry)
            self.matriz_entries.append(fila_entries)
            
        self.btn_resolver.configure(state="normal")
        self.mostrar_resultado(f"Matriz de {m}x{n} generada. Ingrese los coeficientes y presione Resolver.\n")
        
    def leer_matriz_interfaz(self):
        matriz = []
        for i, fila in enumerate(self.matriz_entries):
            fila_valores = []
            for j, entry in enumerate(fila):
                try:
                    val = float(entry.get())
                    fila_valores.append(val)
                except ValueError:
                    raise ValueError(f"Valor inválido en la fila {i+1}, columna {j+1}")
            matriz.append(fila_valores)
        return matriz
        
    def format_matriz(self, matriz) -> str:
        """Formatea la matriz aumentada para mostrarla bonita en texto."""
        salida = ""
        for fila in matriz:
            coefs = fila[:-1]
            ti = fila[-1]
            coefs_str = "  ".join([f"{c:8.3f}" for c in coefs])
            salida += f"[ {coefs_str} | {ti:8.3f} ]\n"
        return salida
        
    def mostrar_resultado(self, texto: str, limpiar: bool = True):
        self.txt_resultados.configure(state="normal")
        if limpiar:
            self.txt_resultados.delete("1.0", "end")
        self.txt_resultados.insert("end", texto + "\n")
        self.txt_resultados.configure(state="disabled")
        self.txt_resultados.yview("end")
        
    def resolver(self):
        try:
            matriz_inicial = self.leer_matriz_interfaz()
        except ValueError as e:
            self.mostrar_resultado(f"Error: {e}")
            return
            
        self.mostrar_resultado("--- INICIANDO RESOLUCIÓN DE GAUSS ---\n", limpiar=True)
        
        pasos, resultado = resolver_gauss(matriz_inicial)
        
        # Imprimir Pasos
        for paso in pasos:
            self.mostrar_resultado(f">> {paso.descripcion}:")
            self.mostrar_resultado(self.format_matriz(paso.matriz_estado), limpiar=False)
            
        # Imprimir Resultado Final
        self.mostrar_resultado("--- RESULTADO ---", limpiar=False)
        self.mostrar_resultado(f"Clasificación: {resultado.tipo}", limpiar=False)
        
        if isinstance(resultado, SinSolucion):
            self.mostrar_resultado(resultado.mensaje, limpiar=False)
            
        elif isinstance(resultado, SolucionInfinita):
            vars_str = ", ".join([f"X{j+1}" for j in resultado.variables_libres])
            if not vars_str:
                vars_str = "No identificadas"
            self.mostrar_resultado(f"El sistema tiene infinitas soluciones.\nVariables libres identificadas: {vars_str}", limpiar=False)
            
        elif isinstance(resultado, SolucionUnica):
            vars_str = ", ".join([f"X{i+1} = {v}" for i, v in enumerate(resultado.variables)])
            self.mostrar_resultado(f"Solución: {vars_str}", limpiar=False)
            
            # Comprobación
            es_correcta = verificar_solucion(matriz_inicial, resultado.variables)
            if es_correcta:
                self.mostrar_resultado("\n[✓] Comprobación Automática: La solución es CORRECTA.", limpiar=False)
            else:
                self.mostrar_resultado("\n[x] Comprobación Automática: La solución NO CUMPLE el sistema (revisar decimales/errores flotantes).", limpiar=False)
