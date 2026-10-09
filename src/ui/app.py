import customtkinter as ctk
import tkinter as tk
from typing import Dict, List

from src.ui.matrix_canvas import MatrixCanvas, PlaybackControls, create_matrix_steps_from_gauss
from src.core.gauss import resolver_gauss, resolver_gauss_jordan, copiar_matriz, Matriz, SolucionUnica, SolucionInfinita, SinSolucion, SolucionGeneral, PasoGauss
from src.core.domain import formatear_numero, formatear_fraccion, a_subindice
from src.ui.vectors_view import VectorsView
from src.ui.matrix_ops_view import MatrixOpsView

class App(ctk.CTk):
    """
    Ventana principal de PyMatrix con Arquitectura Moderna (Sidebar + Dashboard).
    Navega entre Inicio, Gauss/Jordan, Vectores en ℝⁿ y Operaciones Matriciales.
    """
    
    def __init__(self):
        super().__init__()

        # Configuración de ventana
        self.title("PyMatrix - Calculadora de Álgebra Lineal")
        self.geometry("1100x700")
        self.minsize(900, 600)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Grid principal: 2 columnas (Sidebar y Contenido)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Variables de estado
        self._modo_numero = "fraccion"
        self._modulo_activo = "inicio"
        self._nav_btns: Dict[str, ctk.CTkButton] = {}

        self._setup_ui()
        self._show_module("inicio")

    def _setup_ui(self):
        """Construye el Sidebar, el Topbar del contenido y los paneles de los módulos."""
        
        # ================= SIDEBAR =================
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=("#1f2937", "#0f172a"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1) # Empuja configuraciones abajo

        # Logo
        logo_label = ctk.CTkLabel(self.sidebar, text="PyMatrix 🧮", font=ctk.CTkFont(size=20, weight="bold"), text_color="#38bdf8")
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        # Botones de navegación
        self._nav_btns["inicio"] = self._create_sidebar_btn("🏠 Inicio", "inicio", 1)
        self._nav_btns["gauss"] = self._create_sidebar_btn("📐 Gauss / Jordan", "gauss", 2)
        self._nav_btns["vectores"] = self._create_sidebar_btn("🚀 Vectores en ℝⁿ", "vectores", 3)
        self._nav_btns["matrices"] = self._create_sidebar_btn("🧮 Matrices", "matrices", 4)

        # Configuraciones (Abajo)
        config_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        config_frame.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        ctk.CTkLabel(config_frame, text="Formato:", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.fmt_seg = ctk.CTkSegmentedButton(
            config_frame, 
            values=["Fracción", "Decimal"],
            command=self._change_number_format,
            selected_color="#0284c7",
            selected_hover_color="#0369a1"
        )
        self.fmt_seg.pack(fill="x", pady=(5, 15))
        self.fmt_seg.set("Fracción")

        ctk.CTkLabel(config_frame, text="Tema:", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.theme_seg = ctk.CTkSegmentedButton(
            config_frame,
            values=["Dark", "Light"],
            command=self._change_theme,
            selected_color="#475569",
            selected_hover_color="#334155"
        )
        self.theme_seg.pack(fill="x", pady=(5, 0))
        self.theme_seg.set("Dark")

        # ================= CONTENIDO PRINCIPAL =================
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # Crear paneles de módulos
        self._create_dashboard()
        self._create_gauss_panel()
        
        self.vectores_panel = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        self.vectores_panel.grid_rowconfigure(0, weight=1)
        self.vectores_panel.grid_columnconfigure(0, weight=1)
        self.vectores_view = VectorsView(self.vectores_panel, lambda: self._modo_numero)
        self.vectores_view.grid(row=0, column=0, sticky="nsew")
        
        self.matrices_panel = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        self.matrices_panel.grid_rowconfigure(0, weight=1)
        self.matrices_panel.grid_columnconfigure(0, weight=1)
        self.matrices_view = MatrixOpsView(self.matrices_panel, lambda: self._modo_numero)
        self.matrices_view.grid(row=0, column=0, sticky="nsew")

    def _create_sidebar_btn(self, text: str, modulo: str, row: int) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            self.sidebar, 
            text=text,
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            text_color=("gray20", "gray80"),
            hover_color=("#38bdf8", "#0369a1"),
            command=lambda m=modulo: self._show_module(m)
        )
        btn.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        return btn

    def _create_dashboard(self):
        self.inicio_panel = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        
        header = ctk.CTkLabel(self.inicio_panel, text="¡Bienvenido a PyMatrix!", font=ctk.CTkFont(size=28, weight="bold"))
        header.pack(pady=(40, 10))
        sub = ctk.CTkLabel(self.inicio_panel, text="Selecciona una herramienta matemática para comenzar", text_color="gray")
        sub.pack(pady=(0, 30))

        cards_frame = ctk.CTkFrame(self.inicio_panel, fg_color="transparent")
        cards_frame.pack(expand=True)
        cards_frame.grid_columnconfigure((0, 1), weight=1, uniform="card_col")
        cards_frame.grid_rowconfigure((0, 1), weight=1, uniform="card_row")

        self._create_card(cards_frame, 0, 0, "📐 Sistemas Gauss/Jordan", "Resuelve sistemas lineales Ax=b mostrando el proceso de eliminación paso a paso.", "gauss", "#1d4ed8")
        self._create_card(cards_frame, 0, 1, "🧮 Álgebra de Matrices", "Operaciones básicas (suma, resta, producto), transposición, determinantes e inversas.", "matrices", "#7c3aed")
        self._create_card(cards_frame, 1, 0, "🚀 Vectores en ℝⁿ", "Operaciones básicas, producto punto, combinaciones e independencia lineal.", "vectores", "#0d9488")
        self._create_card(cards_frame, 1, 1, "🔬 Verificador de Propiedades", "Comprobación de teoremas e identidades algebraicas de las Sesiones 10 y 11.", "matrices", "#b45309")

    def _create_card(self, parent, row, col, title, desc, target_module, color):
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color=("#ffffff", "#1e293b"), width=340, height=175)
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        card.pack_propagate(False)
        card.grid_propagate(False)
        
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=15, weight="bold"), text_color=color).pack(pady=(18, 8), padx=16, anchor="w")
        lbl_desc = ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=12), text_color=("gray40", "gray70"), wraplength=300, justify="left")
        lbl_desc.pack(padx=16, anchor="w")
        
        btn = ctk.CTkButton(card, text="Abrir", fg_color=color, hover_color=color, width=95, height=32, font=ctk.CTkFont(size=12, weight="bold"), command=lambda m=target_module: self._show_module(m))
        btn.pack(side="bottom", pady=16, padx=16, anchor="e")

    def _show_module(self, modulo: str):
        self._modulo_activo = modulo
        
        # Actualizar Sidebar
        for key, btn in self._nav_btns.items():
            if key == modulo:
                btn.configure(fg_color=("#38bdf8", "#0284c7"), text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=("gray20", "gray80"))

        # Ocultar todos
        self.inicio_panel.grid_forget()
        self.gauss_panel.grid_forget()
        self.vectores_panel.grid_forget()
        self.matrices_panel.grid_forget()

        # Mostrar activo
        if modulo == "inicio":
            self.inicio_panel.grid(row=0, column=0, sticky="nsew")
        elif modulo == "gauss":
            self.gauss_panel.grid(row=0, column=0, sticky="nsew")
        elif modulo == "vectores":
            self.vectores_panel.grid(row=0, column=0, sticky="nsew")
            self.vectores_view.refresh_format()
        elif modulo == "matrices":
            self.matrices_panel.grid(row=0, column=0, sticky="nsew")
            self.matrices_view.refresh_format()

    def _change_number_format(self, mode_str: str):
        self._modo_numero = "decimal" if mode_str == "Decimal" else "fraccion"
        if hasattr(self, 'vectores_view'):
            self.vectores_view.refresh_format()
        if hasattr(self, 'matrices_view'):
            self.matrices_view.refresh_format()

    def _change_theme(self, mode: str):
        ctk.set_appearance_mode(mode)

    # =========================================================================
    # MÓDULO GAUSS (Se mantiene la lógica funcional, adaptada al nuevo layout)
    # =========================================================================
    def _create_gauss_panel(self):
        self.gauss_panel = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        self.gauss_panel.grid_columnconfigure(0, weight=0, minsize=380)
        self.gauss_panel.grid_columnconfigure(1, weight=1)
        self.gauss_panel.grid_rowconfigure(0, weight=1)
        
        self.left_panel = ctk.CTkScrollableFrame(self.gauss_panel, width=380, corner_radius=0, fg_color=("#f1f5f9", "#111827"))
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.left_panel.grid_rowconfigure(2, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # 1. Tamaño
        sec1_frame = ctk.CTkFrame(self.left_panel, fg_color=("#ffffff", "#1f2937"), corner_radius=10)
        sec1_frame.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))
        sec1_frame.grid_columnconfigure(3, weight=1)
        ctk.CTkLabel(sec1_frame, text="1. Tamaño del Sistema", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, columnspan=4, sticky="w", padx=12, pady=(10, 6))
        
        ctk.CTkLabel(sec1_frame, text="Ecs (m):").grid(row=1, column=0, padx=(12, 2))
        self.entry_m = ctk.CTkEntry(sec1_frame, width=45, justify="center")
        self.entry_m.grid(row=1, column=1, padx=2)
        self.entry_m.insert(0, "3")
        
        ctk.CTkLabel(sec1_frame, text="Vars (n):").grid(row=1, column=2, padx=2)
        self.entry_n = ctk.CTkEntry(sec1_frame, width=45, justify="center")
        self.entry_n.grid(row=1, column=3, padx=(2, 12), sticky="w")
        self.entry_n.insert(0, "3")
        
        btn_frame = ctk.CTkFrame(sec1_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=4, pady=(10, 12), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_frame, text="Generar", width=80, command=self.generar_matriz).grid(row=0, column=0, padx=(12, 4))
        ctk.CTkButton(btn_frame, text="🎲 Ejemplo", width=80, fg_color="#475569", hover_color="#334155", command=self.cargar_ejemplo).grid(row=0, column=1, padx=(4, 12))
        
        # 2. Método
        sec2_frame = ctk.CTkFrame(self.left_panel, fg_color=("#ffffff", "#1f2937"), corner_radius=10)
        sec2_frame.grid(row=1, column=0, sticky="ew", padx=14, pady=6)
        sec2_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(sec2_frame, text="2. Método de Resolución", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 6))
        
        self.metodo_var = tk.StringVar(value="gauss-jordan")
        self.seg_method = ctk.CTkSegmentedButton(sec2_frame, values=["Gauss", "Gauss-Jordan"], variable=self.metodo_var, command=self._on_method_changed)
        self.seg_method.grid(row=1, column=0, sticky="ew", padx=12)
        
        self.lbl_metodo_desc = ctk.CTkLabel(sec2_frame, text="Gauss-Jordan: Reduce a Forma Escalonada Reducida (RREF)", font=ctk.CTkFont(size=10), text_color="gray")
        self.lbl_metodo_desc.grid(row=2, column=0, sticky="w", padx=12, pady=(4, 10))

        # 3. Coeficientes
        sec3_frame = ctk.CTkFrame(self.left_panel, fg_color=("#ffffff", "#1f2937"), corner_radius=10)
        sec3_frame.grid(row=2, column=0, sticky="nsew", padx=14, pady=6)
        sec3_frame.grid_columnconfigure(0, weight=1)
        sec3_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(sec3_frame, text="3. Coeficientes y Términos [A | b]", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 0))
        
        self.input_scroll = ctk.CTkScrollableFrame(sec3_frame, fg_color="transparent", orientation="horizontal")
        self.input_scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        
        # Botón Resolver
        sec4_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        sec4_frame.grid(row=3, column=0, sticky="ew", padx=14, pady=(6, 14))
        sec4_frame.grid_columnconfigure(0, weight=1)
        self.btn_resolver = ctk.CTkButton(sec4_frame, text="🚀 Resolver Sistema", font=ctk.CTkFont(size=14, weight="bold"), fg_color=("#10b981", "#059669"), hover_color=("#059669", "#047857"), height=40, command=self.resolver)
        self.btn_resolver.grid(row=0, column=0, sticky="ew")

        # Right Panel
        self.right_panel = ctk.CTkFrame(self.gauss_panel, corner_radius=0, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_panel.grid_rowconfigure(0, weight=3)
        self.right_panel.grid_rowconfigure(1, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        self.tabview = ctk.CTkTabview(self.right_panel)
        self.tabview.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self.tab_visual = self.tabview.add("📊 Visualización Paso a Paso")
        self.tab_text = self.tabview.add("📝 Detalle de Operaciones (Texto)")
        
        self.tab_visual.grid_columnconfigure(0, weight=1)
        self.tab_visual.grid_rowconfigure(0, weight=1)
        self.tab_text.grid_columnconfigure(0, weight=1)
        self.tab_text.grid_rowconfigure(0, weight=1)

        self.canvas_frame = ctk.CTkFrame(self.tab_visual, corner_radius=10, fg_color=("#0f172a", "#0f172a"))
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")
        self.matrix_canvas = MatrixCanvas(self.canvas_frame)
        self.matrix_canvas.pack(fill="both", expand=True, padx=4, pady=4)
        self.playback_controls = PlaybackControls(self.tab_visual, self.matrix_canvas)
        self.playback_controls.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self.text_log = ctk.CTkTextbox(self.tab_text, font=ctk.CTkFont(family="Consolas", size=13), fg_color=("#f8fafc", "#1e293b"), text_color=("#0f172a", "#f8fafc"), corner_radius=10)
        self.text_log.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.text_log.configure(state="disabled")

        self._create_bottom_conclusion()
        self.generar_matriz()

    def _create_bottom_conclusion(self):
        self.results_frame = ctk.CTkFrame(self.right_panel, corner_radius=10, fg_color=("#ffffff", "#1e293b"))
        self.results_frame.grid(row=1, column=0, sticky="nsew")
        self.results_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.results_frame.grid_rowconfigure(1, weight=1)
        
        header_concl = ctk.CTkFrame(self.results_frame, fg_color="transparent", height=30)
        header_concl.grid(row=0, column=0, columnspan=3, sticky="ew", padx=15, pady=(10, 0))
        ctk.CTkLabel(header_concl, text="🎯 RESUMEN DE LA SOLUCIÓN Y CLASIFICACIÓN", font=ctk.CTkFont(size=12, weight="bold"), text_color=("#0284c7", "#38bdf8")).pack(side="left")

        self.card_clasif = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        self.card_clasif.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        ctk.CTkLabel(self.card_clasif, text="Tipo de Sistema", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.lbl_tipo_badge = ctk.CTkLabel(self.card_clasif, text="Sin resolver", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#475569", text_color="white", corner_radius=6, padx=10, pady=4)
        self.lbl_tipo_badge.pack(anchor="w", pady=(5, 5))
        self.lbl_clasif_desc = ctk.CTkLabel(self.card_clasif, text="Listo para resolver...", font=ctk.CTkFont(size=11), text_color="gray", wraplength=180, justify="left")
        self.lbl_clasif_desc.pack(anchor="w")

        self.card_vars = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        self.card_vars.grid(row=1, column=1, sticky="nsew", padx=15, pady=10)
        ctk.CTkLabel(self.card_vars, text="Estructura de Variables", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.lbl_vars_basicas = ctk.CTkLabel(self.card_vars, text="• Variables Básicas (Pivotes): -", font=ctk.CTkFont(size=11), text_color=("#0284c7", "#38bdf8"), justify="left")
        self.lbl_vars_basicas.pack(anchor="w", pady=(5, 2))
        self.lbl_vars_libres = ctk.CTkLabel(self.card_vars, text="• Variables Libres (Parámetros): -", font=ctk.CTkFont(size=11), text_color=("#d97706", "#fbbf24"), justify="left")
        self.lbl_vars_libres.pack(anchor="w")

        self.card_resp = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        self.card_resp.grid(row=1, column=2, sticky="nsew", padx=15, pady=10)
        ctk.CTkLabel(self.card_resp, text="Conjunto Solución", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.lbl_solucion_final = ctk.CTkLabel(self.card_resp, text="Esperando resolución...", font=ctk.CTkFont(size=12), text_color="gray", justify="left")
        self.lbl_solucion_final.pack(anchor="w", pady=(5, 0))

    def _on_method_changed(self, value: str):
        if value.lower() == "gauss":
            self.lbl_metodo_desc.configure(text="Gauss: Reduce a Forma Escalonada (REF) simple.")
        else:
            self.lbl_metodo_desc.configure(text="Gauss-Jordan: Reduce a Forma Escalonada Reducida (RREF).")

    def generar_matriz(self):
        try:
            m = int(self.entry_m.get())
            n = int(self.entry_n.get())
            if m <= 0 or n <= 0 or m > 12 or n > 12: raise ValueError
        except ValueError:
            self._log_text("❌ Error: Dimensiones deben ser entre 1 y 12.", limpiar=True)
            return

        for widget in self.input_scroll.winfo_children():
            widget.destroy()
            
        self.entries_matriz = []
        header_frame = ctk.CTkFrame(self.input_scroll, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ctk.CTkLabel(header_frame, text="", width=32).grid(row=0, column=0, padx=2)
        
        for j in range(n + 1):
            if j < n:
                ctk.CTkLabel(header_frame, text=f"x{a_subindice(j+1)}", font=ctk.CTkFont(weight="bold"), width=50, text_color=("#0284c7", "#38bdf8")).grid(row=0, column=j+1, padx=2)
            else:
                ctk.CTkLabel(header_frame, text="= b", font=ctk.CTkFont(weight="bold"), width=50, text_color=("#e11d48", "#f43f5e")).grid(row=0, column=j+1, padx=2)
        
        for i in range(m):
            row_frame = ctk.CTkFrame(self.input_scroll, fg_color="transparent")
            row_frame.grid(row=i+1, column=0, sticky="ew", pady=2)
            ctk.CTkLabel(row_frame, text=f"E{a_subindice(i+1)}", width=32, text_color="gray").grid(row=0, column=0, padx=2)
            fila_entries = []
            for j in range(n + 1):
                e = ctk.CTkEntry(row_frame, width=50, justify="center")
                e.grid(row=0, column=j+1, padx=2)
                e.insert(0, "0")
                fila_entries.append(e)
            self.entries_matriz.append(fila_entries)
        
        self.matrix_canvas.load_steps([])
        self._reset_conclusion()
        self._log_text(f"✓ Sistema {m}x{n} generado. Ingrese los coeficientes.", limpiar=True)

    def cargar_ejemplo(self):
        self.entry_m.delete(0, 'end'); self.entry_m.insert(0, "3")
        self.entry_n.delete(0, 'end'); self.entry_n.insert(0, "3")
        self.generar_matriz()
        
        ejemplo = [
            [2,  1, -1,   8],
            [-3, -1, 2, -11],
            [-2,  1, 2,  -3]
        ]
        
        for i, fila in enumerate(ejemplo):
            for j, val in enumerate(fila):
                self.entries_matriz[i][j].delete(0, 'end')
                self.entries_matriz[i][j].insert(0, str(val))
        self._log_text("✓ Ejemplo 3x3 cargado. Presione 'Resolver Sistema'.", limpiar=True)

    def leer_matriz_interfaz(self) -> List[List[float]]:
        matriz_amp = []
        for fila_entries in self.entries_matriz:
            fila_vals = []
            for entry in fila_entries:
                val_str = entry.get().strip()
                if "/" in val_str:
                    num, den = val_str.split("/")
                    fila_vals.append(float(num) / float(den))
                else:
                    fila_vals.append(float(val_str))
            matriz_amp.append(fila_vals)
        return matriz_amp

    def _log_text(self, texto: str, limpiar: bool = False):
        self.text_log.configure(state="normal")
        if limpiar:
            self.text_log.delete("1.0", "end")
        self.text_log.insert("end", texto + "\n")
        self.text_log.configure(state="disabled")
        self.text_log.see("end")

    def _reset_conclusion(self):
        self.lbl_tipo_badge.configure(text="Sin resolver", fg_color="#475569")
        self.lbl_clasif_desc.configure(text="Listo para resolver...")
        self.lbl_vars_basicas.configure(text="• Variables Básicas (Pivotes): -")
        self.lbl_vars_libres.configure(text="• Variables Libres (Parámetros): -")
        self.lbl_solucion_final.configure(text="Esperando resolución...")

    def resolver(self):
        try:
            A_amp = self.leer_matriz_interfaz()
        except ValueError:
            self._log_text("❌ Error: Por favor, ingrese solo números válidos (ej. 2, -1.5, 3/4).", limpiar=True)
            return

        usar_jordan = self.metodo_var.get().lower() != "gauss"
        resolver_fn = resolver_gauss_jordan if usar_jordan else resolver_gauss

        self.matrix_canvas.load_steps([])
        self._log_text("🚀 INICIANDO ELIMINACIÓN GAUSSIANA...\n", limpiar=True)
        self.tabview.set("📊 Visualización Paso a Paso")

        try:
            pasos, clasificacion, sol_gen = resolver_fn(A_amp)

            # Visualización animada
            try:
                steps_visual = create_matrix_steps_from_gauss(pasos, A_amp)
                self.matrix_canvas.load_steps(steps_visual)
                self.matrix_canvas.set_number_mode(self._modo_numero)
            except Exception as e_vis:
                self._log_text(f"⚠ Advertencia visualización: {e_vis}", limpiar=False)

            # Log de texto
            self._refresh_text_log(pasos)

            # Clasificar resultado
            if isinstance(clasificacion, SolucionUnica):
                self.lbl_tipo_badge.configure(text="Solución Única", fg_color=("#10b981", "#059669"))
                self.lbl_clasif_desc.configure(text="Sistema Consistente Determinado.")
                n_vars = len(A_amp[0]) - 1
                self.lbl_vars_basicas.configure(text=f"• Variables básicas: x₁…x{a_subindice(n_vars)}")
                self.lbl_vars_libres.configure(text="• Variables libres: Ninguna")
                sol_str = "\n".join([
                    f"x{a_subindice(i+1)} = {formatear_numero(val, self._modo_numero)}"
                    for i, val in enumerate(clasificacion.variables)
                ])
                self.lbl_solucion_final.configure(text=sol_str)

            elif isinstance(clasificacion, SolucionInfinita):
                self.lbl_tipo_badge.configure(text="∞ Infinitas Soluciones", fg_color=("#d97706", "#d97706"))
                self.lbl_clasif_desc.configure(text="Sistema Consistente Indeterminado.")
                libres = clasificacion.variables_libres
                n_vars = len(A_amp[0]) - 1
                basicas = [i+1 for i in range(n_vars) if i not in libres]
                self.lbl_vars_basicas.configure(text=f"• Básicas: {', '.join(f'x{a_subindice(b)}' for b in basicas)}")
                self.lbl_vars_libres.configure(text=f"• Libres: {', '.join(f'x{a_subindice(l+1)}' for l in libres)}")
                if sol_gen:
                    names = {i: f"t{a_subindice(k+1)}" for k, i in enumerate(sol_gen.variables_libres)}
                    lines = []
                    for idx, expr in sol_gen.variables_basicas.items():
                        parts = [formatear_numero(expr.constante, self._modo_numero)]
                        for t in expr.terminos:
                            coef = formatear_numero(t.coef, self._modo_numero)
                            parts.append(f"{coef}·{names.get(t.var_libre_idx, f't{t.var_libre_idx}')}")
                        lines.append(f"x{a_subindice(idx+1)} = {' + '.join(parts)}")
                    for free_idx in sol_gen.variables_libres:
                        lines.append(f"x{a_subindice(free_idx+1)} = {names[free_idx]} (libre)")
                    self.lbl_solucion_final.configure(text="\n".join(lines))
                else:
                    self.lbl_solucion_final.configure(text="Hay variables libres (ver texto).")

            elif isinstance(clasificacion, SinSolucion):
                self.lbl_tipo_badge.configure(text="Sin Solución", fg_color=("#ef4444", "#dc2626"))
                self.lbl_clasif_desc.configure(text=f"Sistema Inconsistente: {getattr(clasificacion, 'mensaje', '')}")
                self.lbl_vars_basicas.configure(text="• Variables Básicas: -")
                self.lbl_vars_libres.configure(text="• Variables Libres: -")
                self.lbl_solucion_final.configure(text="No existe solución.")

        except Exception as e:
            self._log_text(f"❌ Error al resolver: {e}", limpiar=False)
            import traceback
            self._log_text(traceback.format_exc(), limpiar=False)

    def _refresh_text_log(self, historial: List[PasoGauss]):
        self.text_log.configure(state="normal")
        self.text_log.delete("1.0", "end")
        
        for paso in historial:
            self.text_log.insert("end", f"▶ {paso.descripcion}\n")
            if paso.matriz_estado:
                for fila in paso.matriz_estado:
                    fmt_fila = [formatear_numero(v, self._modo_numero) for v in fila]
                    self.text_log.insert("end", f"   [{', '.join(fmt_fila)}]\n")
                self.text_log.insert("end", "\n")
        
        self.text_log.configure(state="disabled")

    def _formatear_lista_legible(self, elementos: list[str]) -> str:
        if not elementos: return "Ninguna"
        if len(elementos) == 1: return elementos[0]
        return ", ".join(elementos[:-1]) + " y " + elementos[-1]

    def _update_conclusion_cards(self, cols_pivote: List[int]):
        n_vars = len(self.entries_matriz[0]) - 1
        vars_basicas = [f"x{a_subindice(c+1)}" for c in cols_pivote]
        vars_libres = [f"x{a_subindice(c+1)}" for c in range(n_vars) if c not in cols_pivote]
        
        self.lbl_vars_basicas.configure(text=f"• Variables Básicas (Pivotes):\n  {self._formatear_lista_legible(vars_basicas)}")
        self.lbl_vars_libres.configure(text=f"• Variables Libres (Parámetros):\n  {self._formatear_lista_legible(vars_libres)}")

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
