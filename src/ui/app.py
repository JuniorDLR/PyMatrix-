import customtkinter as ctk
from src.core.gauss import resolver_gauss, verificar_solucion
from src.core.domain import SolucionUnica, SolucionInfinita, SinSolucion, SolucionGeneral
from src.ui.matrix_canvas import MatrixCanvas, PlaybackControls, create_matrix_steps_from_gauss


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PyMatrix - Calculadora de Álgebra Lineal")
        self.geometry("1300x850")
        self.minsize(1100, 700)
        
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.matriz_inicial = None
        self.pasos_gauss = None
        self.resultado = None
        self.solucion_general: SolucionGeneral | None = None
        self.matriz_entries: list[list[ctk.CTkEntry]] = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_top_bar()
        self._create_main_split()
        self._create_bottom_results()
    
    def _create_top_bar(self):
        top_frame = ctk.CTkFrame(self, height=70, corner_radius=0)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_propagate(False)
        
        # Título a la izquierda
        title_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        self.lbl_title = ctk.CTkLabel(
            title_frame, 
            text="PyMatrix: Gauss-Jordan", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.lbl_title.pack(anchor="w")
        
        self.lbl_subtitle = ctk.CTkLabel(
            title_frame,
            text="Visualización paso a paso • RREF • Solución parametrizada",
            font=ctk.CTkFont(size=11),
            text_color="gray70"
        )
        self.lbl_subtitle.pack(anchor="w")
        
        # Controles de dimensión en el centro
        dims_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        dims_frame.grid(row=0, column=1, sticky="ew", padx=20)
        dims_frame.grid_columnconfigure(6, weight=1)
        
        ctk.CTkLabel(dims_frame, text="Ecuaciones (m):", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=(0, 5))
        self.entry_m = ctk.CTkEntry(dims_frame, width=55, height=30)
        self.entry_m.grid(row=0, column=1, padx=5)
        self.entry_m.insert(0, "3")
        
        ctk.CTkLabel(dims_frame, text="Variables (n):", font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=(15, 5))
        self.entry_n = ctk.CTkEntry(dims_frame, width=55, height=30)
        self.entry_n.grid(row=0, column=3, padx=5)
        self.entry_n.insert(0, "3")
        
        self.btn_generar = ctk.CTkButton(
            dims_frame, text="Generar Matriz", command=self.generar_matriz,
            font=ctk.CTkFont(size=12, weight="bold"), height=30, width=130
        )
        self.btn_generar.grid(row=0, column=4, padx=15)
        
        self.btn_ejemplo = ctk.CTkButton(
            dims_frame, text="Ejemplo", command=self.cargar_ejemplo,
            fg_color="#555", hover_color="#666", height=30, width=90
        )
        self.btn_ejemplo.grid(row=0, column=5, padx=5)
        
        # Botón resolver a la derecha (inicialmente oculto)
        self.btn_resolver_top = ctk.CTkButton(
            dims_frame, text="Resolver Sistema", command=self.resolver,
            fg_color="green", hover_color="darkgreen", font=ctk.CTkFont(size=12, weight="bold"), 
            height=30, width=140
        )
        self.btn_resolver_top.grid(row=0, column=6, padx=15, sticky="e")
        self.btn_resolver_top.grid_remove()
    
    def _create_main_split(self):
        # Panel izquierdo: Input Matrix (ancho fijo ~380px)
        self.left_panel = ctk.CTkFrame(self, width=380, corner_radius=0)
        self.left_panel.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.left_panel.grid_propagate(False)
        self.left_panel.grid_rowconfigure(1, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # Header del panel izquierdo
        left_header = ctk.CTkFrame(self.left_panel, fg_color="transparent", height=40)
        left_header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        left_header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(left_header, text="MATRIZ DE ENTRADA", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, sticky="w")
        
        # Área scrollable para la matriz de entrada
        self.input_scroll = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.input_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.input_scroll.grid_columnconfigure(0, weight=1)
        
        # Placeholder inicial
        self.input_placeholder = ctk.CTkLabel(
            self.input_scroll, 
            text="Ingrese dimensiones y presione\n\"Generar Matriz\" para comenzar",
            font=ctk.CTkFont(size=13),
            text_color="gray60"
        )
        self.input_placeholder.grid(row=0, column=0, pady=60)
        
        # Panel derecho: Visualización + Texto (expandible)
        self.right_panel = ctk.CTkFrame(self, corner_radius=0)
        self.right_panel.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        self.tabview = ctk.CTkTabview(self.right_panel)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.tab_visual = self.tabview.add("  Visualización  ")
        self.tab_visual.grid_columnconfigure(0, weight=1)
        self.tab_visual.grid_rowconfigure(0, weight=1)
        
        self.tab_text = self.tabview.add("  Detalle Texto  ")
        self.tab_text.grid_columnconfigure(0, weight=1)
        self.tab_text.grid_rowconfigure(0, weight=1)
        
        self._setup_visual_tab()
        self._setup_text_tab()
    
    def _setup_visual_tab(self):
        # Canvas ocupa todo el espacio
        self.matrix_canvas = MatrixCanvas(self.tab_visual)
        self.matrix_canvas.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Controles de reproducción en overlay inferior
        self.playback_controls = PlaybackControls(self.tab_visual, self.matrix_canvas)
        self.playback_controls.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 10))
    
    def _setup_text_tab(self):
        self.txt_resultados = ctk.CTkTextbox(
            self.tab_text, 
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="none"
        )
        self.txt_resultados.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.txt_resultados.configure(state="disabled")
    
    def _create_bottom_results(self):
        self.results_frame = ctk.CTkFrame(self, height=160, corner_radius=0)
        self.results_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        self.results_frame.grid_propagate(False)
        self.results_frame.grid_columnconfigure(0, weight=1)
        
        # Header con toggle
        results_header = ctk.CTkFrame(self.results_frame, fg_color="transparent", height=40)
        results_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 0))
        results_header.grid_columnconfigure(0, weight=1)
        
        self.lbl_resultado_title = ctk.CTkLabel(
            results_header, text="RESULTADO FINAL", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_resultado_title.grid(row=0, column=0, sticky="w")
        
        self.btn_toggle_results = ctk.CTkButton(
            results_header, text="▲ Ocultar", width=80, height=26,
            font=ctk.CTkFont(size=11), command=self._toggle_results
        )
        self.btn_toggle_results.grid(row=0, column=1, sticky="e")
        
        self.txt_resultado_final = ctk.CTkTextbox(
            self.results_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word"
        )
        self.txt_resultado_final.grid(row=1, column=0, sticky="nsew", padx=20, pady=(5, 15))
        self.txt_resultado_final.configure(state="disabled")
        self.results_frame.grid_rowconfigure(1, weight=1)
        
        self._results_visible = True
    
    def _toggle_results(self):
        if self._results_visible:
            self.results_frame.grid_remove()
            self.btn_toggle_results.configure(text="▼ Mostrar")
        else:
            self.results_frame.grid()
            self.btn_toggle_results.configure(text="▲ Ocultar")
        self._results_visible = not self._results_visible
    
    def generar_matriz(self):
        try:
            m = int(self.entry_m.get())
            n = int(self.entry_n.get())
        except ValueError:
            self._log_text("Error: Por favor, ingrese números enteros válidos para m y n.\n")
            return
            
        if m <= 0 or n <= 0:
            self._log_text("Error: Las dimensiones deben ser mayores que 0.\n")
            return
            
        for widget in self.input_scroll.winfo_children():
            widget.destroy()
            
        self.matriz_entries = []
        self.input_placeholder = None
        
        self._create_input_grid(m, n)
        
        self.btn_resolver_top.grid()
        
        self._log_text(f"Matriz de {m}x{n} generada. Ingrese coeficientes y presione Resolver.\n")
        self._clear_results()
    
    def _create_input_grid(self, m: int, n: int):
        # Header de columnas
        header_frame = ctk.CTkFrame(self.input_scroll, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Etiqueta vacía para alinear con "R1"
        ctk.CTkLabel(header_frame, text="", width=35).grid(row=0, column=0, padx=3)
        
        for j in range(n + 1):
            if j < n:
                lbl = ctk.CTkLabel(header_frame, text=f"X{j+1}", font=ctk.CTkFont(size=11, weight="bold"), width=55, text_color=("gray20", "gray80"))
            else:
                lbl = ctk.CTkLabel(header_frame, text="=", font=ctk.CTkFont(size=14, weight="bold"), width=55, text_color="#ff6b6b")
            lbl.grid(row=0, column=j+1, padx=3)
        
        # Filas de la matriz
        for i in range(m):
            row_frame = ctk.CTkFrame(self.input_scroll, fg_color="transparent")
            row_frame.grid(row=i+1, column=0, sticky="ew", pady=3)
            row_frame.grid_columnconfigure(0, weight=1)
            
            fila_entries = []
            
            lbl_row = ctk.CTkLabel(row_frame, text=f"R{i+1}", width=35, font=ctk.CTkFont(size=11, weight="bold"), text_color=("gray30", "gray70"))
            lbl_row.grid(row=0, column=0, padx=3)
            
            for j in range(n + 1):
                entry = ctk.CTkEntry(
                    row_frame, width=55, height=28, justify="center", 
                    font=ctk.CTkFont(size=12), corner_radius=4
                )
                entry.grid(row=0, column=j+1, padx=3)
                entry.insert(0, "0")
                
                # Color diferenciado para columna independiente
                if j == n:
                    entry.configure(fg_color=("#ffebee", "#3e1a1a"), text_color=("#c62828", "#ff6b6b"))
                
                fila_entries.append(entry)
            
            self.matriz_entries.append(fila_entries)
    
    def cargar_ejemplo(self):
        ejemplos = [
            {
                "m": 3, "n": 3,
                "matriz": [
                    [2, 1, -1, 8],
                    [-3, -1, 2, -11],
                    [-2, 1, 2, -3]
                ],
                "desc": "Sistema 3x3 - Solución única (x=2, y=3, z=-1)"
            },
            {
                "m": 3, "n": 4,
                "matriz": [
                    [1, 2, -1, 1, 3],
                    [2, 4, -2, 2, 6],
                    [1, 2, 0, -1, 1]
                ],
                "desc": "Sistema 3x4 - Infinitas soluciones (2 variables libres)"
            },
            {
                "m": 2, "n": 2,
                "matriz": [
                    [1, 2, 3],
                    [2, 4, 7]
                ],
                "desc": "Sistema 2x2 - Sin solución (inconsistente)"
            }
        ]
        
        import random
        ej = random.choice(ejemplos)
        
        self.entry_m.delete(0, "end")
        self.entry_m.insert(0, str(ej["m"]))
        self.entry_n.delete(0, "end")
        self.entry_n.insert(0, str(ej["n"]))
        
        self.generar_matriz()
        
        for i, fila in enumerate(ej["matriz"]):
            for j, val in enumerate(fila):
                if i < len(self.matriz_entries) and j < len(self.matriz_entries[i]):
                    self.matriz_entries[i][j].delete(0, "end")
                    self.matriz_entries[i][j].insert(0, str(val))
        
        self._log_text(f"Ejemplo cargado: {ej['desc']}\n")
    
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
    
    def _format_matriz(self, matriz) -> str:
        salida = ""
        for fila in matriz:
            coefs = fila[:-1]
            ti = fila[-1]
            coefs_str = "  ".join([f"{c:9.3f}" for c in coefs])
            salida += f"[ {coefs_str} | {ti:9.3f} ]\n"
        return salida
    
    def _log_text(self, texto: str, limpiar: bool = False):
        self.txt_resultados.configure(state="normal")
        if limpiar:
            self.txt_resultados.delete("1.0", "end")
        self.txt_resultados.insert("end", texto + "\n")
        self.txt_resultados.configure(state="disabled")
        self.txt_resultados.yview("end")
    
    def _clear_results(self):
        self.txt_resultado_final.configure(state="normal")
        self.txt_resultado_final.delete("1.0", "end")
        self.txt_resultado_final.configure(state="disabled")
    
    def _show_final_result(self, texto: str):
        self.txt_resultado_final.configure(state="normal")
        self.txt_resultado_final.delete("1.0", "end")
        self.txt_resultado_final.insert("end", texto)
        self.txt_resultado_final.configure(state="disabled")
    
    def resolver(self):
        try:
            matriz_inicial = self.leer_matriz_interfaz()
        except ValueError as e:
            self._log_text(f"Error: {e}")
            return
            
        self.matriz_inicial = matriz_inicial
        self._log_text("--- INICIANDO RESOLUCIÓN DE GAUSS---\n", limpiar=True)
        
        self.pasos_gauss, self.resultado, self.solucion_general = resolver_gauss(matriz_inicial, return_rref=True)
        
        steps_visual = create_matrix_steps_from_gauss(self.pasos_gauss, matriz_inicial)
        self.matrix_canvas.load_steps(steps_visual)
        
        for paso in self.pasos_gauss:
            self._log_text(f">> {paso.descripcion}:")
            self._log_text(self._format_matriz(paso.matriz_estado), limpiar=False)
        
        self._log_text("--- RESULTADO ---", limpiar=False)
        self._log_text(f"Clasificación: {self.resultado.tipo}", limpiar=False)
        
        resultado_texto = self._format_resultado_final()
        self._show_final_result(resultado_texto)
        self._log_text(resultado_texto, limpiar=False)
        
        self.tabview.set("  Visualización  ")
    
    def _format_resultado_final(self) -> str:
        lines = []
        lines.append(f"Clasificación: {self.resultado.tipo}")
        lines.append("")
        
        if isinstance(self.resultado, SinSolucion):
            lines.append(self.resultado.mensaje)
            lines.append("")
            lines.append("El sistema es INCONSISTENTE.")
            lines.append("La forma escalonada revela una fila: [0 0 ... 0 | k] con k ≠ 0")
            
        elif isinstance(self.resultado, SolucionInfinita):
            vars_libres = [f"X{j+1}" for j in self.resultado.variables_libres]
            vars_basicas = [f"X{j+1}" for j in range(len(self.matriz_inicial[0]) - 1) if j not in self.resultado.variables_libres]
            
            lines.append(f"Variables básicas: {', '.join(vars_basicas) if vars_basicas else 'Ninguna'}")
            lines.append(f"Variables libres:  {', '.join(vars_libres) if vars_libres else 'Ninguna'}")
            lines.append("")
            lines.append("El sistema tiene INFINITAS SOLUCIONES.")
            
            if self.solucion_general:
                lines.append("Solución general (parametrizada):")
                for eq in self.solucion_general.a_strings(len(self.matriz_inicial[0]) - 1):
                    lines.append(f"  {eq}")
            
        elif isinstance(self.resultado, SolucionUnica):
            vars_str = ", ".join([f"X{i+1} = {v}" for i, v in enumerate(self.resultado.variables)])
            lines.append(f"Solución única: {vars_str}")
            lines.append("")
            
            es_correcta = verificar_solucion(self.matriz_inicial, self.resultado.variables)
            if es_correcta:
                lines.append("Verificación: La solución cumple el sistema original")
            else:
                lines.append("Verificación: La solución NO cumple (revisar precisión)")
        
        return "\n".join(lines)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()