import random
from typing import Optional, List
import customtkinter as ctk

from src.core.gauss import resolver_gauss, resolver_gauss_jordan, verificar_solucion
from src.core.domain import (
    SolucionUnica, SolucionInfinita, SinSolucion, SolucionGeneral, 
    formatear_fraccion, formatear_numero, formatear_decimal, a_subindice
)
from src.ui.matrix_canvas import MatrixCanvas, PlaybackControls, create_matrix_steps_from_gauss


class App(ctk.CTk):
    """Ventana principal de la calculadora PyMatrix con soporte para Gauss y Gauss-Jordan."""
    
    def __init__(self):
        super().__init__()

        self.title("PyMatrix - Calculadora de Álgebra Lineal (Gauss & Gauss-Jordan)")
        self.geometry("1360x880")
        self.minsize(1150, 720)
        
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # Variables de estado
        self.matriz_inicial: Optional[List[List[float]]] = None
        self.pasos_gauss = None
        self.resultado = None
        self.solucion_general: Optional[SolucionGeneral] = None
        self.matriz_entries: List[List[ctk.CTkEntry]] = []
        self.metodo_var = ctk.StringVar(value="Gauss-Jordan")
        self.modo_numero = "fraccion"
        self.ultimas_cols_pivote_str = "Ninguna"
        
        self._setup_ui()
    
    def _setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_top_bar()
        self._create_main_split()
        self._create_bottom_conclusion()
        
        # Generar matriz inicial por defecto (3x3)
        self.generar_matriz()
    
    def _create_top_bar(self):
        top_frame = ctk.CTkFrame(self, height=64, corner_radius=0, fg_color=("#1e293b", "#0f172a"))
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_propagate(False)
        
        # Título y logotipo
        title_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        lbl_title = ctk.CTkLabel(
            title_frame, 
            text="PyMatrix 🔢", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#38bdf8", "#38bdf8")
        )
        lbl_title.pack(side="left", padx=(0, 10))
        
        lbl_badge = ctk.CTkLabel(
            title_frame,
            text="v2.0 • Gauss & Gauss-Jordan",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#0284c7", "#0369a1"),
            corner_radius=6,
            text_color="white",
            padx=8,
            pady=2
        )
        lbl_badge.pack(side="left")
        
        # Descripción corta
        lbl_desc = ctk.CTkLabel(
            top_frame,
            text="Resolución interactiva paso a paso con detección automática de consistencia y variables libres",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray70")
        )
        lbl_desc.grid(row=0, column=1, sticky="w", padx=20)
        
        # Controles superiores a la derecha: Formato numérico y Tema
        top_controls = ctk.CTkFrame(top_frame, fg_color="transparent")
        top_controls.grid(row=0, column=2, padx=20)
        
        # Toggle de formato de números: Fracción vs Decimal
        self.btn_formato = ctk.CTkSegmentedButton(
            top_controls,
            values=["Fracción", "Decimal"],
            command=self._change_number_format,
            width=150,
            height=28,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.btn_formato.set("Fracción")
        self.btn_formato.pack(side="left", padx=(0, 10))
        
        # Toggle de tema (Claro / Oscuro)
        theme_btn = ctk.CTkSegmentedButton(
            top_controls,
            values=["Dark", "Light"],
            command=self._change_theme,
            width=110,
            height=28
        )
        theme_btn.set("Dark")
        theme_btn.pack(side="left")
    
    def _change_number_format(self, mode_str: str):
        """Alterna el formato de visualización entre fracciones y decimales."""
        self.modo_numero = "fraccion" if "frac" in mode_str.lower() else "decimal"
        if hasattr(self, "matrix_canvas"):
            self.matrix_canvas.set_number_mode(self.modo_numero)
        
        # Si ya se resolvió un sistema, refrescar la conclusión y el registro textual de inmediato
        if self.resultado is not None and self.matriz_inicial is not None:
            self._update_conclusion_cards(self.ultimas_cols_pivote_str)
            self._refresh_text_log()
    
    def _change_theme(self, mode: str):
        ctk.set_appearance_mode(mode)
        if hasattr(self, "matrix_canvas"):
            self.matrix_canvas._refresh_theme()
    
    def _create_main_split(self):
        # =========================================================================
        # PANEL IZQUIERDO: FLUJO DE ENTRADA Y ACCIÓN (Ancho fijo 410px)
        # =========================================================================
        self.left_panel = ctk.CTkFrame(self, width=410, corner_radius=0, fg_color=("#f1f5f9", "#111827"))
        self.left_panel.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.left_panel.grid_propagate(False)
        self.left_panel.grid_rowconfigure(2, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # --- SECCIÓN 1: DIMENSIONES ---
        sec1_frame = ctk.CTkFrame(self.left_panel, fg_color=("#ffffff", "#1f2937"), corner_radius=10)
        sec1_frame.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))
        sec1_frame.grid_columnconfigure(3, weight=1)
        
        lbl_sec1 = ctk.CTkLabel(
            sec1_frame, 
            text="1. Tamaño del Sistema (m × n)", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#0284c7", "#38bdf8")
        )
        lbl_sec1.grid(row=0, column=0, columnspan=4, sticky="w", padx=12, pady=(10, 6))
        
        ctk.CTkLabel(sec1_frame, text="Ecs (m):", font=ctk.CTkFont(size=12)).grid(row=1, column=0, padx=(12, 4), pady=(0, 10))
        self.entry_m = ctk.CTkEntry(sec1_frame, width=48, height=30, justify="center")
        self.entry_m.grid(row=1, column=1, padx=4, pady=(0, 10))
        self.entry_m.insert(0, "3")
        
        ctk.CTkLabel(sec1_frame, text="Vars (n):", font=ctk.CTkFont(size=12)).grid(row=1, column=2, padx=(10, 4), pady=(0, 10))
        self.entry_n = ctk.CTkEntry(sec1_frame, width=48, height=30, justify="center")
        self.entry_n.grid(row=1, column=3, padx=4, pady=(0, 10))
        self.entry_n.insert(0, "3")
        
        self.btn_generar = ctk.CTkButton(
            sec1_frame, text="Generar", width=75, height=30, command=self.generar_matriz,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.btn_generar.grid(row=1, column=4, padx=4, pady=(0, 10))
        
        self.btn_ejemplo = ctk.CTkButton(
            sec1_frame, text="🎲 Ejemplo", width=80, height=30, command=self.cargar_ejemplo,
            fg_color=("#475569", "#374151"), hover_color=("#334155", "#4b5563"), font=ctk.CTkFont(size=11)
        )
        self.btn_ejemplo.grid(row=1, column=5, padx=(4, 12), pady=(0, 10))
        
        # --- SECCIÓN 2: SELECCIÓN DE MÉTODO ---
        sec2_frame = ctk.CTkFrame(self.left_panel, fg_color=("#ffffff", "#1f2937"), corner_radius=10)
        sec2_frame.grid(row=1, column=0, sticky="ew", padx=14, pady=6)
        sec2_frame.grid_columnconfigure(0, weight=1)
        
        lbl_sec2 = ctk.CTkLabel(
            sec2_frame, 
            text="2. Método de Resolución", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#0284c7", "#38bdf8")
        )
        lbl_sec2.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))
        
        self.method_segmented = ctk.CTkSegmentedButton(
            sec2_frame,
            values=["Gauss", "Gauss-Jordan"],
            variable=self.metodo_var,
            command=self._on_method_changed,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=32
        )
        self.method_segmented.grid(row=1, column=0, sticky="ew", padx=12, pady=(2, 6))
        
        self.lbl_metodo_info = ctk.CTkLabel(
            sec2_frame,
            text="Gauss-Jordan: Reduce a Forma Escalonada Reducida (FERF) con pivotes = 1.",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
            wraplength=370,
            justify="left"
        )
        self.lbl_metodo_info.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 10))
        
        # --- SECCIÓN 3: MATRIZ DE ENTRADA (SCROLLABLE) ---
        sec3_frame = ctk.CTkFrame(self.left_panel, fg_color=("#ffffff", "#1f2937"), corner_radius=10)
        sec3_frame.grid(row=2, column=0, sticky="nsew", padx=14, pady=6)
        sec3_frame.grid_rowconfigure(1, weight=1)
        sec3_frame.grid_columnconfigure(0, weight=1)
        
        lbl_sec3 = ctk.CTkLabel(
            sec3_frame, 
            text="3. Coeficientes y Términos [A | b]", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#0284c7", "#38bdf8")
        )
        lbl_sec3.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))
        
        self.input_scroll = ctk.CTkScrollableFrame(sec3_frame, fg_color="transparent")
        self.input_scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.input_scroll.grid_columnconfigure(0, weight=1)
        
        # --- SECCIÓN 4: BOTÓN RESOLVER ---
        sec4_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        sec4_frame.grid(row=3, column=0, sticky="ew", padx=14, pady=(6, 14))
        sec4_frame.grid_columnconfigure(0, weight=1)
        
        self.btn_resolver = ctk.CTkButton(
            sec4_frame, 
            text="🚀 Resolver Sistema", 
            command=self.resolver,
            fg_color=("#059669", "#10b981"), 
            hover_color=("#047857", "#059669"), 
            font=ctk.CTkFont(size=14, weight="bold"), 
            height=40,
            corner_radius=8
        )
        self.btn_resolver.grid(row=0, column=0, sticky="ew")
        
        # =========================================================================
        # PANEL DERECHO: VISUALIZACIÓN + DETALLE
        # =========================================================================
        self.right_panel = ctk.CTkFrame(self, corner_radius=0, fg_color=("#e2e8f0", "#0b1120"))
        self.right_panel.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        self.tabview = ctk.CTkTabview(self.right_panel)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=12, pady=10)
        
        self.tab_visual = self.tabview.add("  📊 Visualización Paso a Paso  ")
        self.tab_visual.grid_columnconfigure(0, weight=1)
        self.tab_visual.grid_rowconfigure(0, weight=1)
        
        self.tab_text = self.tabview.add("  📝 Detalle de Operaciones (Texto)  ")
        self.tab_text.grid_columnconfigure(0, weight=1)
        self.tab_text.grid_rowconfigure(0, weight=1)
        
        # Visual Tab
        self.matrix_canvas = MatrixCanvas(self.tab_visual)
        self.matrix_canvas.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        
        self.playback_controls = PlaybackControls(self.tab_visual, self.matrix_canvas)
        self.playback_controls.grid(row=1, column=0, sticky="ew", padx=4, pady=(2, 6))
        
        # Text Tab
        self.txt_resultados = ctk.CTkTextbox(
            self.tab_text, 
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="none",
            corner_radius=8
        )
        self.txt_resultados.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.txt_resultados.configure(state="disabled")
    
    def _create_bottom_conclusion(self):
        """Bloque de conclusión y resumen final de la solución."""
        self.results_frame = ctk.CTkFrame(self, height=195, corner_radius=0, fg_color=("#1e293b", "#0f172a"))
        self.results_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        self.results_frame.grid_propagate(False)
        self.results_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.results_frame.grid_rowconfigure(1, weight=1)
        
        # Header de la barra de conclusión
        header_concl = ctk.CTkFrame(self.results_frame, fg_color="transparent", height=28)
        header_concl.grid(row=0, column=0, columnspan=3, sticky="ew", padx=16, pady=(8, 2))
        header_concl.grid_columnconfigure(0, weight=1)
        
        lbl_concl_title = ctk.CTkLabel(
            header_concl, 
            text="🎯 RESUMEN DE LA SOLUCIÓN Y CLASIFICACIÓN", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#38bdf8", "#38bdf8")
        )
        lbl_concl_title.grid(row=0, column=0, sticky="w")
        
        # --- TARJETA 1: CLASIFICACIÓN Y ESTADO ---
        self.card_clasif = ctk.CTkFrame(self.results_frame, fg_color=("#ffffff", "#1e293b"), corner_radius=8)
        self.card_clasif.grid(row=1, column=0, sticky="nsew", padx=(14, 6), pady=(0, 10))
        self.card_clasif.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.card_clasif, 
            text="Tipo de Sistema", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray40", "gray60")
        ).pack(anchor="w", padx=10, pady=(8, 2))
        
        self.lbl_badge_tipo = ctk.CTkLabel(
            self.card_clasif,
            text="Sin resolver",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#475569", "#334155"),
            corner_radius=6,
            text_color="white",
            padx=10,
            pady=4
        )
        self.lbl_badge_tipo.pack(anchor="w", padx=10, pady=4)
        
        self.lbl_desc_clasif = ctk.CTkLabel(
            self.card_clasif,
            text="Ingrese los coeficientes y presione 'Resolver Sistema' para ver el diagnóstico.",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray70"),
            wraplength=260,
            justify="left"
        )
        self.lbl_desc_clasif.pack(anchor="w", padx=10, pady=(2, 8))
        
        # --- TARJETA 2: VARIABLES BÁSICAS Y LIBRES ---
        self.card_vars = ctk.CTkFrame(self.results_frame, fg_color=("#ffffff", "#1e293b"), corner_radius=8)
        self.card_vars.grid(row=1, column=1, sticky="nsew", padx=6, pady=(0, 10))
        self.card_vars.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.card_vars, 
            text="Estructura de Variables", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray40", "gray60")
        ).pack(anchor="w", padx=10, pady=(8, 2))
        
        self.lbl_vars_basicas = ctk.CTkLabel(
            self.card_vars,
            text="• Variables Básicas (Pivotes): —",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color=("#0284c7", "#38bdf8"),
            anchor="w",
            justify="left",
            wraplength=330
        )
        self.lbl_vars_basicas.pack(anchor="w", padx=10, pady=2)
        
        self.lbl_vars_libres = ctk.CTkLabel(
            self.card_vars,
            text="• Variables Libres (Parámetros): —",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=("#d97706", "#fbbf24"),
            anchor="w",
            justify="left",
            wraplength=330
        )
        self.lbl_vars_libres.pack(anchor="w", padx=10, pady=2)
        
        self.lbl_verif_status = ctk.CTkLabel(
            self.card_vars,
            text="• Verificación matemática: —",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
            anchor="w"
        )
        self.lbl_verif_status.pack(anchor="w", padx=10, pady=(2, 6))
        
        # --- TARJETA 3: RESPUESTA FINAL / CONJUNTO SOLUCIÓN ---
        self.card_resp = ctk.CTkFrame(self.results_frame, fg_color=("#ffffff", "#1e293b"), corner_radius=8)
        self.card_resp.grid(row=1, column=2, sticky="nsew", padx=(6, 14), pady=(0, 10))
        self.card_resp.grid_rowconfigure(1, weight=1)
        self.card_resp.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.card_resp, 
            text="Conjunto Solución", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray40", "gray60")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))
        
        self.txt_solucion_display = ctk.CTkTextbox(
            self.card_resp,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="transparent",
            wrap="word",
            activate_scrollbars=True
        )
        self.txt_solucion_display.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 6))
        self.txt_solucion_display.insert("end", "Esperando resolución...")
        self.txt_solucion_display.configure(state="disabled")
    
    def _on_method_changed(self, value: str):
        if value == "Gauss":
            self.lbl_metodo_info.configure(
                text="Gauss: Escalonamiento (REF) con ceros debajo del pivote + Sustitución hacia atrás."
            )
        else:
            self.lbl_metodo_info.configure(
                text="Gauss-Jordan: Reduce a Forma Escalonada Reducida (FERF) con pivotes = 1 y ceros arriba/abajo."
            )
    
    def generar_matriz(self):
        """Genera dinámicamente la cuadrícula de entradas según m y n."""
        try:
            m = int(self.entry_m.get())
            n = int(self.entry_n.get())
        except ValueError:
            self._log_text("Error: Por favor, ingrese números enteros válidos para m y n.\n")
            return
            
        if m <= 0 or n <= 0:
            self._log_text("Error: Las dimensiones deben ser mayores que 0.\n")
            return
        
        if m > 12 or n > 12:
            self._log_text("Aviso: Dimensiones muy grandes pueden exceder el área visual. Máximo recomendado: 10x10.\n")
            
        for widget in self.input_scroll.winfo_children():
            widget.destroy()
            
        self.matriz_entries = []
        self._create_input_grid(m, n)
        
        self._log_text(f"Matriz de {m} ecuaciones × {n} variables generada. Ingrese valores y presione Resolver.\n", limpiar=True)
        self._reset_conclusion()
    
    def _create_input_grid(self, m: int, n: int):
        # Cabecera de columnas
        header_frame = ctk.CTkFrame(self.input_scroll, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        
        ctk.CTkLabel(header_frame, text="", width=32).grid(row=0, column=0, padx=2)
        
        for j in range(n + 1):
            if j < n:
                lbl = ctk.CTkLabel(
                    header_frame, text=f"x{a_subindice(j+1)}", 
                    font=ctk.CTkFont(size=12, weight="bold"), 
                    width=50, 
                    text_color=("#0284c7", "#38bdf8")
                )
            else:
                lbl = ctk.CTkLabel(
                    header_frame, text="= b", 
                    font=ctk.CTkFont(size=12, weight="bold"), 
                    width=50, 
                    text_color=("#e11d48", "#f43f5e")
                )
            lbl.grid(row=0, column=j+1, padx=2)
        
        # Celdas de entrada
        for i in range(m):
            row_frame = ctk.CTkFrame(self.input_scroll, fg_color="transparent")
            row_frame.grid(row=i+1, column=0, sticky="ew", pady=2)
            
            fila_entries = []
            lbl_row = ctk.CTkLabel(
                row_frame, text=f"F{a_subindice(i+1)}", width=32, 
                font=ctk.CTkFont(size=12, weight="bold"), 
                text_color=("gray40", "gray60")
            )
            lbl_row.grid(row=0, column=0, padx=2)
            
            for j in range(n + 1):
                entry = ctk.CTkEntry(
                    row_frame, width=50, height=28, justify="center", 
                    font=ctk.CTkFont(family="Consolas", size=11), corner_radius=4
                )
                entry.grid(row=0, column=j+1, padx=2)
                entry.insert(0, "0")
                
                # Resaltar la columna de términos independientes
                if j == n:
                    entry.configure(
                        fg_color=("#ffe4e6", "#3f1a24"), 
                        text_color=("#be123c", "#fca5a5"),
                        border_color=("#f43f5e", "#be123c")
                    )
                
                fila_entries.append(entry)
            
            self.matriz_entries.append(fila_entries)
    
    def cargar_ejemplo(self):
        """Carga matrices de prueba predefinidas con distintos comportamientos."""
        ejemplos = [
            {
                "m": 3, "n": 3,
                "matriz": [
                    [2, 1, -1, 8],
                    [-3, -1, 2, -11],
                    [-2, 1, 2, -3]
                ],
                "desc": "Sistema 3x3 — Solución Única (X1=2, X2=3, X3=-1)"
            },
            {
                "m": 3, "n": 4,
                "matriz": [
                    [1, 2, -1, 1, 3],
                    [2, 4, -2, 2, 6],
                    [1, 2, 0, -1, 1]
                ],
                "desc": "Sistema 3x4 — Infinitas Soluciones (2 variables libres)"
            },
            {
                "m": 3, "n": 3,
                "matriz": [
                    [1, 1, 1, 2],
                    [0, 1, -1, 1],
                    [1, 2, 0, 5]
                ],
                "desc": "Sistema 3x3 — Sin Solución / Inconsistente (0 = 2)"
            },
            {
                "m": 4, "n": 4,
                "matriz": [
                    [1, 1, 0, 1, 2],
                    [2, 1, -1, 1, 1],
                    [-1, 2, 3, -1, 4],
                    [3, -1, -1, 2, 5]
                ],
                "desc": "Sistema 4x4 — Solución Única (4 variables)"
            }
        ]
        
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
        
        self._log_text(f"🎲 Ejemplo cargado: {ej['desc']}\n")
    
    def leer_matriz_interfaz(self) -> List[List[float]]:
        matriz = []
        for i, fila in enumerate(self.matriz_entries):
            fila_valores = []
            for j, entry in enumerate(fila):
                val_str = entry.get().strip()
                try:
                    val = float(val_str)
                    fila_valores.append(val)
                except ValueError:
                    raise ValueError(f"Valor no numérico '{val_str}' en Fila {i+1}, Columna {j+1}")
            matriz.append(fila_valores)
        return matriz
    
    def _format_matriz(self, matriz) -> str:
        salida = ""
        for fila in matriz:
            coefs = fila[:-1]
            ti = fila[-1]
            coefs_str = "  ".join([f"{formatear_numero(c, self.modo_numero):>8}" for c in coefs])
            salida += f"  [ {coefs_str} | {formatear_numero(ti, self.modo_numero):>8} ]\n"
        return salida
    
    def _log_text(self, texto: str, limpiar: bool = False):
        self.txt_resultados.configure(state="normal")
        if limpiar:
            self.txt_resultados.delete("1.0", "end")
        self.txt_resultados.insert("end", texto + "\n")
        self.txt_resultados.configure(state="disabled")
        self.txt_resultados.yview("end")
    
    def _reset_conclusion(self):
        self.lbl_badge_tipo.configure(text="Sin resolver", fg_color=("#475569", "#334155"))
        self.lbl_desc_clasif.configure(text="Listo para resolver con el método seleccionado.")
        self.lbl_vars_basicas.configure(text="• Variables Básicas (Pivotes): —")
        self.lbl_vars_libres.configure(text="• Variables Libres (Parámetros): —")
        self.lbl_verif_status.configure(text="• Verificación matemática: —", text_color=("gray50", "gray60"))
        
        self.txt_solucion_display.configure(state="normal")
        self.txt_solucion_display.delete("1.0", "end")
        self.txt_solucion_display.insert("end", "Esperando resolución...")
        self.txt_solucion_display.configure(state="disabled")
    
    def resolver(self):
        """Ejecuta el método seleccionado (Gauss o Gauss-Jordan) y actualiza canvas y resumen."""
        try:
            matriz_inicial = self.leer_matriz_interfaz()
        except ValueError as e:
            self._log_text(f"❌ Error de entrada: {e}")
            return
            
        self.matriz_inicial = matriz_inicial
        metodo = self.metodo_var.get()
        num_vars = len(matriz_inicial[0]) - 1
        var_names = [f"x{a_subindice(i+1)}" for i in range(num_vars)]
        
        self._log_text(f"==================================================", limpiar=True)
        self._log_text(f"  EJECUTANDO: {metodo.upper()}")
        self._log_text(f"==================================================\n")
        
        # 1. Ejecutar algoritmo matemático (puramente Python estándar)
        if metodo == "Gauss":
            self.pasos_gauss, self.resultado, self.solucion_general = resolver_gauss(matriz_inicial)
        else:
            self.pasos_gauss, self.resultado, self.solucion_general = resolver_gauss_jordan(matriz_inicial)
        
        # 2. Cargar pasos en el Canvas gráfico con marcado de pivotes y ceros
        steps_visual = create_matrix_steps_from_gauss(self.pasos_gauss, matriz_inicial)
        self.matrix_canvas.load_steps(steps_visual)
        
        # 3. Registrar desarrollo paso a paso en el log textual
        for paso in self.pasos_gauss:
            self._log_text(f">> {paso.descripcion}:")
            self._log_text(self._format_matriz(paso.matriz_estado))
        
        # 4. Mostrar matrices de forma escalonada (REF) y reducida (RREF)
        if self.solucion_general:
            self._log_text("--- 1. FORMA ESCALONADA POR FILAS (REF) [ESCALERA DE GAUSS] ---")
            self._log_text(self._format_matriz(self.solucion_general.matriz_ref))
            if metodo == "Gauss-Jordan":
                self._log_text("--- 2. FORMA ESCALONADA REDUCIDA (RREF) [GAUSS-JORDAN FINAL] ---")
                self._log_text(self._format_matriz(self.solucion_general.matriz_rref))
        else:
            matriz_final = self.pasos_gauss[-1].matriz_estado if self.pasos_gauss else matriz_inicial
            nombre_forma = "FORMA ESCALONADA REDUCIDA (RREF)" if metodo == "Gauss-Jordan" else "FORMA ESCALONADA (REF)"
            self._log_text(f"--- MATRIZ FINAL EN {nombre_forma} ---")
            self._log_text(self._format_matriz(matriz_final))
        
        # 5. Extraer y listar columnas pivote identificadas (1-based para usuario)
        if isinstance(self.resultado, SinSolucion):
            cols_pivote_str = "No aplica (sistema inconsistente)"
            vars_basicas_str = "Ninguna"
            vars_libres_str = "Ninguna"
        elif isinstance(self.resultado, SolucionInfinita):
            vars_libres_idx = self.resultado.variables_libres
            cols_pivote_idx = [j for j in range(num_vars) if j not in vars_libres_idx]
            cols_pivote_1based = [str(j + 1) for j in cols_pivote_idx]
            cols_pivote_str = self._formatear_lista_legible(cols_pivote_1based) if cols_pivote_1based else "Ninguna"
            vars_basicas_str = ", ".join([var_names[j] for j in cols_pivote_idx]) if cols_pivote_idx else "Ninguna"
            vars_libres_str = ", ".join([var_names[j] for j in vars_libres_idx]) if vars_libres_idx else "Ninguna"
        else:  # Solución única
            cols_pivote_1based = [str(j + 1) for j in range(num_vars)]
            cols_pivote_str = self._formatear_lista_legible(cols_pivote_1based)
            vars_basicas_str = ", ".join(var_names) + " (Todas)"
            vars_libres_str = "Ninguna (0 variables libres)"
        
        self._log_text("--- ANÁLISIS DE PIVOTES Y VARIABLES ---")
        self._log_text(f"• Las columnas pivote son: {cols_pivote_str}")
        self._log_text(f"• Variables Básicas: {vars_basicas_str}")
        self._log_text(f"• Variables Libres:  {vars_libres_str}")
        self._log_text(f"• Clasificación:     {self.resultado.tipo}\n")
        
        # 6. Actualizar las tarjetas de conclusión final en la interfaz
        self.ultimas_cols_pivote_str = cols_pivote_str
        self._update_conclusion_cards(cols_pivote_str)
        
        # 7. Cambiar a la pestaña de visualización
        self.tabview.set("  📊 Visualización Paso a Paso  ")
    
    def _refresh_text_log(self):
        """Regenera el registro textual completo con el formato numérico seleccionado (Fracción/Decimal)."""
        if not self.pasos_gauss or self.matriz_inicial is None:
            return
        
        metodo = self.metodo_var.get()
        num_vars = len(self.matriz_inicial[0]) - 1
        var_names = [f"x{a_subindice(i+1)}" for i in range(num_vars)]
        
        self._log_text(f"==================================================", limpiar=True)
        self._log_text(f"  EJECUTANDO: {metodo.upper()} [Modo: {self.modo_numero.capitalize()}]")
        self._log_text(f"==================================================\n")
        
        for paso in self.pasos_gauss:
            self._log_text(f">> {paso.descripcion}:")
            self._log_text(self._format_matriz(paso.matriz_estado))
        
        if self.solucion_general:
            self._log_text("--- 1. FORMA ESCALONADA POR FILAS (REF) [ESCALERA DE GAUSS] ---")
            self._log_text(self._format_matriz(self.solucion_general.matriz_ref))
            if metodo == "Gauss-Jordan":
                self._log_text("--- 2. FORMA ESCALONADA REDUCIDA (RREF) [GAUSS-JORDAN FINAL] ---")
                self._log_text(self._format_matriz(self.solucion_general.matriz_rref))
        else:
            matriz_final = self.pasos_gauss[-1].matriz_estado if self.pasos_gauss else self.matriz_inicial
            nombre_forma = "FORMA ESCALONADA REDUCIDA (RREF)" if metodo == "Gauss-Jordan" else "FORMA ESCALONADA (REF)"
            self._log_text(f"--- MATRIZ FINAL EN {nombre_forma} ---")
            self._log_text(self._format_matriz(matriz_final))
        
        self._log_text("--- ANÁLISIS DE PIVOTES Y VARIABLES ---")
        self._log_text(f"• Las columnas pivote son: {self.ultimas_cols_pivote_str}")
        if self.resultado:
            self._log_text(f"• Clasificación:     {self.resultado.tipo}\n")
    
    def _formatear_lista_legible(self, elementos: list[str]) -> str:
        """Formatea ['1', '2', '4'] en '1, 2 y 4'."""
        if not elementos:
            return "Ninguna"
        if len(elementos) == 1:
            return elementos[0]
        return ", ".join(elementos[:-1]) + " y " + elementos[-1]
    
    def _update_conclusion_cards(self, cols_pivote_str: str):
        """Actualiza las 3 tarjetas inferiores con la información estructurada de la solución."""
        num_vars = len(self.matriz_inicial[0]) - 1
        var_names = [f"x{a_subindice(i+1)}" for i in range(num_vars)]
        
        self.txt_solucion_display.configure(state="normal")
        self.txt_solucion_display.delete("1.0", "end")
        
        if isinstance(self.resultado, SinSolucion):
            # Badge de Inconsistencia (Rojo)
            self.lbl_badge_tipo.configure(
                text="Inconsistente (Sin Solución)", 
                fg_color=("#dc2626", "#ef4444")
            )
            self.lbl_desc_clasif.configure(
                text="El sistema contiene una fila absurda [0 ... 0 | k] con k ≠ 0. Las ecuaciones son incompatibles entre sí."
            )
            self.lbl_vars_basicas.configure(text="• Columnas Pivote: Ninguna válida")
            self.lbl_vars_libres.configure(text="• Variables Básicas/Libres: No aplica (S = ∅)")
            self.lbl_verif_status.configure(
                text="• Verificación: Sistema sin solución posible (S = ∅)",
                text_color=("#ef4444", "#f87171")
            )
            
            self.txt_solucion_display.insert("end", "Conjunto Solución Vacío:\n  S = ∅\n\nNo existen valores para las variables que satisfagan todas las ecuaciones simultáneamente.")
            
        elif isinstance(self.resultado, SolucionInfinita):
            # Badge de Infinitas Soluciones (Ámbar/Amarillo)
            vars_libres_idx = self.resultado.variables_libres
            vars_libres_str = [var_names[j] for j in vars_libres_idx]
            vars_basicas_str = [var_names[j] for j in range(num_vars) if j not in vars_libres_idx]
            
            self.lbl_badge_tipo.configure(
                text="Consistente Indeterminado", 
                fg_color=("#d97706", "#f59e0b")
            )
            self.lbl_desc_clasif.configure(
                text=f"Infinitas soluciones con {len(vars_libres_idx)} variable(s) libre(s) como parámetro(s)."
            )
            
            self.lbl_vars_basicas.configure(
                text=f"• Columnas Pivote: {cols_pivote_str}\n• Básicas: {', '.join(vars_basicas_str) if vars_basicas_str else 'Ninguna'}"
            )
            self.lbl_vars_libres.configure(
                text=f"• Variables Libres: {', '.join(vars_libres_str) if vars_libres_str else 'Ninguna'}"
            )
            self.lbl_verif_status.configure(
                text="• Verificación: Parametrización consistente comprobada ✓",
                text_color=("#10b981", "#34d399")
            )
            
            # Formato de solución general
            lineas_sol = ["Solución General Parametrizada:"]
            if self.solucion_general:
                for eq in self.solucion_general.a_strings(num_vars, modo=self.modo_numero):
                    lineas_sol.append(f"  {eq}")
            else:
                for v in vars_libres_str:
                    lineas_sol.append(f"  {v} ∈ ℝ (libre)")
            
            self.txt_solucion_display.insert("end", "\n".join(lineas_sol))
            
        elif isinstance(self.resultado, SolucionUnica):
            # Badge de Solución Única (Verde)
            self.lbl_badge_tipo.configure(
                text="Consistente Determinado", 
                fg_color=("#16a34a", "#22c55e")
            )
            self.lbl_desc_clasif.configure(
                text="Existe exactamente una solución única para cada variable."
            )
            
            self.lbl_vars_basicas.configure(
                text=f"• Columnas Pivote: {cols_pivote_str}\n• Básicas: {', '.join(var_names)} (Todas)"
            )
            self.lbl_vars_libres.configure(
                text="• Variables Libres: Ninguna (0 variables libres)"
            )
            
            # Verificación numérica
            cumple = verificar_solucion(self.matriz_inicial, self.resultado.variables)
            if cumple:
                self.lbl_verif_status.configure(
                    text="• Verificación: Solución exacta (A·x = b) ✓",
                    text_color=("#10b981", "#34d399")
                )
            else:
                self.lbl_verif_status.configure(
                    text="• Verificación: Diferencia flotante detectada ⚠",
                    text_color=("#f59e0b", "#fbbf24")
                )
            
            lineas_sol = ["Solución Única:"]
            for i, v in enumerate(self.resultado.variables):
                lineas_sol.append(f"  {var_names[i]} = {formatear_numero(v, self.modo_numero)}")
            
            self.txt_solucion_display.insert("end", "\n".join(lineas_sol))
        
        self.txt_solucion_display.configure(state="disabled")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()