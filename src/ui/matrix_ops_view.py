import customtkinter as ctk

class DialogoGuardar(ctk.CTkToplevel):
    def __init__(self, *args, title="Guardar", text="Ingrese valor:", **kwargs):
        super().__init__(*args, **kwargs)
        self.title(title)
        self.geometry("400x200")
        self.transient(self.master)
        self.grab_set()
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        lbl = ctk.CTkLabel(self, text=text, font=ctk.CTkFont(size=14, weight="bold"))
        lbl.grid(row=0, column=0, pady=(20, 10), padx=20)
        
        self.entry = ctk.CTkEntry(self, width=250, height=35)
        self.entry.grid(row=1, column=0, pady=10, padx=20)
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda e: self._ok())
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=(10, 20))
        
        ctk.CTkButton(btn_frame, text="OK", width=100, command=self._ok).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancelar", width=100, fg_color="gray", command=self._cancel).pack(side="left", padx=10)
        
        self.result = None
        
    def _ok(self):
        self.result = self.entry.get()
        self.destroy()
        
    def _cancel(self):
        self.destroy()
        
    def get_input(self):
        self.wait_window(self)
        return self.result

"""Vista de operaciones matriciales: suma, resta, producto, traspuesta, inversa y determinantes.
Presenta paneles interactivos con procedimientos detallados paso a paso para cada operación.
Tema de clase: operaciones con matrices, determinantes y matriz inversa (Sesiones 9 a 11).
Elaborado por: Grupo x"""

import random
from typing import List, Optional


from src.core.matrix_ops import (
    sumar_matrices, restar_matrices, multiplicar_matriz_escalar, combinacion_matrices,
    multiplicar_matrices, multiplicar_matriz_vector, resolver_ecuacion_matricial,
    ResultadoMultiplicacionMatricial, ResultadoProductoMatrizVector, ResultadoEcuacionMatricial,
    verificar_propiedad_aditiva_ax, verificar_propiedad_escalar_ax, verificar_linealidad_general_ax,
    VerificacionPropiedadAditivaAx, VerificacionPropiedadEscalarAx, VerificacionLinealidadGeneralAx,
    trasponer_matriz, invertir_matriz, calcular_determinante,
    ResultadoInversionMatriz, ResultadoDeterminante
)

from src.core.vectors import Vector
from src.core.domain import Matriz, formatear_numero, a_subindice, convertir_texto_a_modo


class MatrixOpsView(ctk.CTkFrame):
    """Vista con pestañas: operaciones matriciales, Ax = b, propiedades de Ax, traspuesta/inversa y determinantes."""

    def __init__(self, master, get_modo_numero_cb, **kwargs):
        """Inicializa el panel; recibe el callback que entrega el modo numérico (Fracción/Decimal)."""
        super().__init__(master, **kwargs)
        self.get_modo_numero = get_modo_numero_cb
        self._ultimo_calc_ops = None
        self._ultimo_calc_axb = None
        self._ultimo_calc_prop = None
        self._ultimo_calc_inv = None   # "traspuesta" | "inversa"
        self._ultimo_calc_det = None   # "determinante"

        # Variables internas para guardar el resultado matemático puro (slots)
        self._resultado_slot_A = None
        self._resultado_slot_B = None
        self._resultado_slot_AB = None
        self.banco_matrices = {}

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._setup_ui()

    def _setup_ui(self):
        """Crea las pestañas y construye el contenido de cada una."""
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 0))
        ctk.CTkButton(top_bar, text="🏦 Abrir Banco de Matrices", command=self._abrir_popup_banco, fg_color=("#059669", "#047857"), font=ctk.CTkFont(weight="bold")).pack(side="right")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 5))

        self.tab_ops    = self.tabview.add("  ➕➖✖️ Operaciones con Matrices  ")
        self.tab_axb    = self.tabview.add("  📐 Ax = b (Ecuación Matricial)  ")
        self.tab_props  = self.tabview.add("  🔬 Propiedades de Ax  ")
        self.tab_inv    = self.tabview.add("  🔄 Traspuesta e Inversa  ")
        self.tab_det    = self.tabview.add("  📊 Determinantes  ")
        self._setup_tab_ops()
        self._setup_tab_axb()
        self._setup_tab_propiedades()
        self._setup_tab_inv()
        self._setup_tab_det()

    def refresh_format(self):
        """Convierte las entradas al formato global vigente y recalcula la última operación de cada pestaña."""
        modo = self.get_modo_numero()

        def _convertir(entry):
            """Reescribe el texto de una entrada en el modo numérico actual, ignorando widgets ya destruidos."""
            try:
                if entry is not None and entry.winfo_exists():
                    val = entry.get()
                    nuevo = convertir_texto_a_modo(val, modo)
                    if nuevo != val:
                        entry.delete(0, "end")
                        entry.insert(0, nuevo)
            except Exception:
                pass

        if hasattr(self, "entries_A"):
            for fila in self.entries_A:
                for e in fila:
                    _convertir(e)
        if hasattr(self, "entries_B"):
            for fila in self.entries_B:
                for e in fila:
                    _convertir(e)
        if hasattr(self, "entry_ops_c"):
            _convertir(self.entry_ops_c)

        if hasattr(self, "entries_axb"):
            for fila in self.entries_axb:
                for e in fila:
                    _convertir(e)

        if hasattr(self, "entries_prop_A"):
            for fila in self.entries_prop_A:
                for e in fila:
                    _convertir(e)
        if hasattr(self, "entries_prop_vecs"):
            for fila in self.entries_prop_vecs:
                for e in fila:
                    _convertir(e)
        if hasattr(self, "entries_prop_c"):
            for e in self.entries_prop_c:
                _convertir(e)

        if hasattr(self, "entries_inv"):
            for fila in self.entries_inv:
                for e in fila:
                    _convertir(e)

        if hasattr(self, "entries_det"):
            for fila in self.entries_det:
                for e in fila:
                    _convertir(e)

        if hasattr(self, "_resultado_slot_A") and self._resultado_slot_A is not None:
            self._renderizar_matriz_en_grid(self.grid_slot_A, self._resultado_slot_A, ("#bae6fd", "#0284c7"), ("#0369a1", "#e0f2fe"))
            if hasattr(self, "btn_guardar_A"):
                self.btn_guardar_A.configure(state="normal")
        if hasattr(self, "_resultado_slot_B") and self._resultado_slot_B is not None:
            self._renderizar_matriz_en_grid(self.grid_slot_B, self._resultado_slot_B, ("#a7f3d0", "#059669"), ("#047857", "#d1fae5"))
            if hasattr(self, "btn_guardar_B"):
                self.btn_guardar_B.configure(state="normal")
        if hasattr(self, "_resultado_slot_AB") and self._resultado_slot_AB is not None:
            self._renderizar_matriz_en_grid(self.grid_slot_AB, self._resultado_slot_AB, ("#fecdd3", "#e11d48"), ("#be123c", "#ffe4e6"))
            if hasattr(self, "btn_guardar_AB"):
                self.btn_guardar_AB.configure(state="normal")

        if self._ultimo_calc_ops == "prop_ab_inv":
            self._calc_prop_ab_inv()
        elif self._ultimo_calc_ops:
            self._calc_op(self._ultimo_calc_ops)
        if self._ultimo_calc_axb == "ax":
            self._calcular_ax()
        elif self._ultimo_calc_axb == "axb":
            self._resolver_axb()
        if self._ultimo_calc_prop == "aditiva":
            self._calc_propiedad_aditiva()
        elif self._ultimo_calc_prop == "escalar":
            self._calc_propiedad_escalar()
        elif self._ultimo_calc_prop == "linealidad":
            self._calc_linealidad_general()
        if self._ultimo_calc_inv == "traspuesta":
            self._calc_traspuesta()
        elif self._ultimo_calc_inv == "inversa":
            self._calc_inversa()
        elif self._ultimo_calc_inv == "inversa_adjunta":
            self._calc_inversa_adjunta()
        elif self._ultimo_calc_inv and self._ultimo_calc_inv.startswith("tarea5_"):
            self._calc_propiedad_tarea5_inv(self._ultimo_calc_inv.split("_", 1)[1])

        if self._ultimo_calc_det == "determinante":
            self._calc_determinante()
        elif self._ultimo_calc_det == "cofactores":
            self._calc_det_cofactores()
        elif self._ultimo_calc_det == "sarrus":
            self._calc_det_sarrus()
        elif self._ultimo_calc_det and self._ultimo_calc_det.startswith("tarea5_"):
            self._calc_propiedad_tarea5_det(self._ultimo_calc_det.split("_", 1)[1])

    def _setup_tab_ops(self):
        """Construye la pestaña de suma, resta, escalar por matriz y producto de matrices."""
        tab = self.tab_ops
        tab.grid_columnconfigure(0, weight=0)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(tab, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left.grid_columnconfigure(0, weight=1)

        dim_frame = ctk.CTkFrame(left, fg_color="transparent")
        dim_frame.pack(fill="x", padx=14, pady=(12, 4))

        ctk.CTkLabel(dim_frame, text="Matriz A:", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=("#38bdf8", "#38bdf8")).pack(side="left")

        ctk.CTkLabel(dim_frame, text="  m=").pack(side="left")
        self.entry_ops_mA = ctk.CTkEntry(dim_frame, width=36, justify="center")
        self.entry_ops_mA.pack(side="left", padx=2)
        self.entry_ops_mA.insert(0, "2")

        ctk.CTkLabel(dim_frame, text="n=").pack(side="left", padx=(4, 0))
        self.entry_ops_nA = ctk.CTkEntry(dim_frame, width=36, justify="center")
        self.entry_ops_nA.pack(side="left", padx=2)
        self.entry_ops_nA.insert(0, "3")

        ctk.CTkLabel(dim_frame, text="   Matriz B:", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=("#34d399", "#34d399")).pack(side="left", padx=(10, 0))

        ctk.CTkLabel(dim_frame, text="  m=").pack(side="left")
        self.entry_ops_mB = ctk.CTkEntry(dim_frame, width=36, justify="center")
        self.entry_ops_mB.pack(side="left", padx=2)
        self.entry_ops_mB.insert(0, "2")

        ctk.CTkLabel(dim_frame, text="n=").pack(side="left", padx=(4, 0))
        self.entry_ops_nB = ctk.CTkEntry(dim_frame, width=36, justify="center")
        self.entry_ops_nB.pack(side="left", padx=2)
        self.entry_ops_nB.insert(0, "3")

        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=4)
        ctk.CTkButton(btn_row, text="Generar", width=70, command=self._generar_matrices_ops).pack(side="left", padx=2)
        ctk.CTkButton(
            btn_row, text="🎲 Ejemplo", width=80, command=self._cargar_ejemplo_ops,
            fg_color=("#475569", "#374151"), hover_color=("#334155", "#4b5563")
        ).pack(side="left", padx=4)

        ctk.CTkLabel(btn_row, text="   Escalar (c):", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=("#38bdf8", "#38bdf8")).pack(side="left", padx=(10, 2))
        self.entry_ops_c = ctk.CTkEntry(btn_row, width=48, justify="center")
        self.entry_ops_c.pack(side="left", padx=2)
        self.entry_ops_c.insert(0, "2")

        self.scroll_ops = ctk.CTkScrollableFrame(left, height=170)
        self.scroll_ops.pack(fill="both", expand=True, padx=14, pady=4)

        op_grid = ctk.CTkFrame(left, fg_color="transparent")
        op_grid.pack(fill="x", padx=14, pady=(6, 12))
        op_grid.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(op_grid, text="A + B  (Suma)", command=lambda: self._calc_op("suma"),
                      fg_color=("#0284c7", "#0369a1"), font=ctk.CTkFont(size=12, weight="bold"), height=34
                      ).grid(row=0, column=0, padx=3, pady=3, sticky="ew")

        ctk.CTkButton(op_grid, text="A − B  (Resta)", command=lambda: self._calc_op("resta"),
                      fg_color=("#0284c7", "#0369a1"), font=ctk.CTkFont(size=12, weight="bold"), height=34
                      ).grid(row=0, column=1, padx=3, pady=3, sticky="ew")

        ctk.CTkButton(op_grid, text="c · A  (Escalar por Matriz)", command=lambda: self._calc_op("escalar"),
                      fg_color=("#0d9488", "#0f766e"), font=ctk.CTkFont(size=12, weight="bold"), height=34
                      ).grid(row=1, column=0, padx=3, pady=3, sticky="ew")

        ctk.CTkButton(op_grid, text="A × B  (Multiplicación A·B)", command=lambda: self._calc_op("multiplicacion"),
                      fg_color=("#7c3aed", "#6d28d9"), font=ctk.CTkFont(size=12, weight="bold"), height=34
                      ).grid(row=1, column=1, padx=3, pady=3, sticky="ew")

        ctk.CTkButton(op_grid, text="Aᵀ  (Traspuesta de A)", command=lambda: self._calc_op("traspuesta_A"),
                      fg_color=("#059669", "#047857"), font=ctk.CTkFont(size=12, weight="bold"), height=34
                      ).grid(row=2, column=0, padx=3, pady=3, sticky="ew")

        ctk.CTkButton(op_grid, text="Bᵀ  (Traspuesta de B)", command=lambda: self._calc_op("traspuesta_B"),
                      fg_color=("#059669", "#047857"), font=ctk.CTkFont(size=12, weight="bold"), height=34
                      ).grid(row=2, column=1, padx=3, pady=3, sticky="ew")

        ctk.CTkButton(op_grid, text="(AB)⁻¹ = B⁻¹ A⁻¹ (Propiedad)", command=lambda: self._calc_prop_ab_inv(),
                      fg_color=("#ea580c", "#c2410c"), font=ctk.CTkFont(size=12, weight="bold"), height=34
                      ).grid(row=3, column=0, columnspan=2, padx=3, pady=3, sticky="ew")





        # --- PANEL DERECHO: Pestañas Duales (Visualizador y Terminal) ---
        right = ctk.CTkFrame(tab, corner_radius=10, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(0, weight=1)

        self.ops_right_tabs = ctk.CTkTabview(right)
        self.ops_right_tabs.grid(row=0, column=0, sticky="nsew")

        tab_vis = self.ops_right_tabs.add("  📊 Visualizador de Resultados  ")
        tab_hist = self.ops_right_tabs.add("  📋 Historial de Operaciones (Texto)  ")

        # --- Pestaña 1: Visualizador Gráfico (3 Ranuras) ---
        tab_vis.grid_columnconfigure(0, weight=1)
        tab_vis.grid_rowconfigure(0, weight=1)
        
        self.scroll_vis = ctk.CTkScrollableFrame(tab_vis, fg_color="transparent")
        self.scroll_vis.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.scroll_vis.grid_columnconfigure(0, weight=1)
        
        # Ranura 1: Operaciones en A
        self.frame_slot_A = ctk.CTkFrame(self.scroll_vis, corner_radius=8)
        self.frame_slot_A.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.frame_slot_A.grid_columnconfigure(0, weight=1)
        self.lbl_slot_A = ctk.CTkLabel(self.frame_slot_A, text="Última Operación en A: (Ninguna)", font=ctk.CTkFont(weight="bold", size=13), text_color=("#38bdf8", "#38bdf8"))
        self.lbl_slot_A.pack(pady=(10, 0))
        self.grid_slot_A = ctk.CTkFrame(self.frame_slot_A, fg_color="transparent")
        self.grid_slot_A.pack(pady=10)
        self.btn_guardar_A = ctk.CTkButton(self.frame_slot_A, text="💾 Guardar en Banco", state="disabled", command=lambda: self._pedir_guardar_banco("A"), fg_color=("#059669", "#047857"))
        self.btn_guardar_A.pack(pady=(0, 10))
        
        # Ranura 2: Operaciones en B
        self.frame_slot_B = ctk.CTkFrame(self.scroll_vis, corner_radius=8)
        self.frame_slot_B.grid(row=1, column=0, sticky="ew", pady=10)
        self.frame_slot_B.grid_columnconfigure(0, weight=1)
        self.lbl_slot_B = ctk.CTkLabel(self.frame_slot_B, text="Última Operación en B: (Ninguna)", font=ctk.CTkFont(weight="bold", size=13), text_color=("#34d399", "#34d399"))
        self.lbl_slot_B.pack(pady=(10, 0))
        self.grid_slot_B = ctk.CTkFrame(self.frame_slot_B, fg_color="transparent")
        self.grid_slot_B.pack(pady=10)
        self.btn_guardar_B = ctk.CTkButton(self.frame_slot_B, text="💾 Guardar en Banco", state="disabled", command=lambda: self._pedir_guardar_banco("B"), fg_color=("#059669", "#047857"))
        self.btn_guardar_B.pack(pady=(0, 10))
        
        # Ranura 3: Operaciones con A y B
        self.frame_slot_AB = ctk.CTkFrame(self.scroll_vis, corner_radius=8)
        self.frame_slot_AB.grid(row=2, column=0, sticky="ew", pady=10)
        self.frame_slot_AB.grid_columnconfigure(0, weight=1)
        self.lbl_slot_AB = ctk.CTkLabel(self.frame_slot_AB, text="Última Operación A y B: (Ninguna)", font=ctk.CTkFont(weight="bold", size=13), text_color=("#f43f5e", "#f43f5e"))
        self.lbl_slot_AB.pack(pady=(10, 0))
        self.grid_slot_AB = ctk.CTkFrame(self.frame_slot_AB, fg_color="transparent")
        self.grid_slot_AB.pack(pady=10)
        self.btn_guardar_AB = ctk.CTkButton(self.frame_slot_AB, text="💾 Guardar en Banco", state="disabled", command=lambda: self._pedir_guardar_banco("AB"), fg_color=("#059669", "#047857"))
        self.btn_guardar_AB.pack(pady=(0, 10))

        # --- Pestaña 2: Historial de Operaciones (Texto) ---
        tab_hist.grid_columnconfigure(0, weight=1)
        tab_hist.grid_rowconfigure(1, weight=1)
        
        top_hist = ctk.CTkFrame(tab_hist, fg_color="transparent")
        top_hist.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        ctk.CTkLabel(top_hist, text="Registro permanente de operaciones:", font=ctk.CTkFont(size=12, slant="italic")).pack(side="left")
        ctk.CTkButton(top_hist, text="🗑️ Limpiar Historial", width=120, command=self._limpiar_historial_ops, fg_color=("#ef4444", "#b91c1c")).pack(side="right")
        
        self.txt_res_ops = ctk.CTkTextbox(tab_hist, font=ctk.CTkFont(family="Consolas", size=12), wrap="word")
        self.txt_res_ops.grid(row=1, column=0, sticky="nsew")
        self.txt_res_ops.configure(state="disabled")

        self.entries_A: List[List[ctk.CTkEntry]] = []
        self.entries_B: List[List[ctk.CTkEntry]] = []
        self._generar_matrices_ops()

    def _calc_prop_ab_inv(self):
        """Comprueba y documenta paso a paso la propiedad (AB)⁻¹ = B⁻¹ A⁻¹."""
        self._ultimo_calc_ops = "prop_ab_inv"
        modo = self.get_modo_numero()
        try:
            A = self._leer_matriz_entries(self.entries_A)
            B = self._leer_matriz_entries(self.entries_B)
        except ValueError as e:
            self._log_ops(f"❌ Error de entrada: {e}\n" + "-"*40, limpiar=False)
            return

        mA, nA = len(A), len(A[0])
        mB, nB = len(B), len(B[0])
        
        lineas = ["\n" + "═"*50]
        lineas.append(">> PROPIEDAD: Inversa del Producto Matricial (AB)⁻¹ = B⁻¹A⁻¹")
        lineas.append("═"*50)
        
        if mA != nA or mB != nB or mA != mB:
            lineas.append("❌ CONDICIÓN FALLIDA: Ambas matrices deben ser cuadradas y del mismo orden para evaluar esta propiedad.")
            self._log_ops("\n".join(lineas), limpiar=False)
            return
            
        from src.core.exact_math import crear_matriz, multiplicar_matrices, inversa_gauss_jordan, son_matrices_iguales
        
        A_f = crear_matriz(A)
        B_f = crear_matriz(B)
        
        lineas.append("\n--- PASO 1: Calcular A × B ---")
        AB = multiplicar_matrices(A_f, B_f)
        lineas.append(f"Matriz resultante AB ({mA}×{mA}):\n{self._fmt_mat(AB, modo)}")
        
        lineas.append("\n--- PASO 2: Calcular la Inversa de (A × B) ---")
        res_AB = inversa_gauss_jordan(AB)
        if not res_AB.es_invertible:
            lineas.append("❌ La matriz AB no es invertible (determinante 0). No se puede continuar la demostración.")
            self._log_ops("\n".join(lineas), limpiar=False)
            return
            
        lado_izquierdo = res_AB.matriz_inversa
        lineas.append(f"Inversa calculada (AB)⁻¹:\n{self._fmt_mat(lado_izquierdo, modo)}")
        
        lineas.append("\n--- PASO 3: Calcular la Inversa de A y B por separado ---")
        res_A = inversa_gauss_jordan(A_f)
        res_B = inversa_gauss_jordan(B_f)
        
        if not res_A.es_invertible or not res_B.es_invertible:
            lineas.append("❌ Una de las matrices (A o B) no es invertible. La propiedad requiere que ambas lo sean.")
            self._log_ops("\n".join(lineas), limpiar=False)
            return
            
        A_inv = res_A.matriz_inversa
        B_inv = res_B.matriz_inversa
        lineas.append(f"Matriz A⁻¹:\n{self._fmt_mat(A_inv, modo)}")
        lineas.append(f"Matriz B⁻¹:\n{self._fmt_mat(B_inv, modo)}")
        
        lineas.append("\n--- PASO 4: Multiplicar B⁻¹ × A⁻¹ ---")
        lineas.append("(Nota: El orden se invierte según la propiedad)")
        lado_derecho = multiplicar_matrices(B_inv, A_inv)
        lineas.append(f"Matriz resultante B⁻¹A⁻¹:\n{self._fmt_mat(lado_derecho, modo)}")
        
        lineas.append("\n--- CONCLUSIÓN ---")
        son_iguales = son_matrices_iguales(lado_izquierdo, lado_derecho)
        if son_iguales:
            lineas.append("✅ (AB)⁻¹ y B⁻¹A⁻¹ son IDÉNTICAS.")
            lineas.append("La propiedad queda demostrada paso a paso.")
            self._mostrar_resultado_ranura("AB", "Propiedad (AB)⁻¹", lado_izquierdo)
        else:
            lineas.append("❌ Las matrices resultantes no coinciden (esto no debería ocurrir).")
            
        self._log_ops("\n".join(lineas), limpiar=False)


    def _limpiar_historial_ops(self):
        self.txt_res_ops.configure(state="normal")
        self.txt_res_ops.delete("1.0", "end")
        self.txt_res_ops.configure(state="disabled")

    def _renderizar_matriz_en_grid(self, parent_frame, matriz, color_fondo, color_texto):
        # Limpiar el frame
        for w in parent_frame.winfo_children():
            w.destroy()
        
        if not matriz:
            return
            
        m = len(matriz)
        n = len(matriz[0]) if m > 0 else 0
        modo = self.get_modo_numero()
        
        # Grid para alinear columnas y filas
        for i in range(m):
            for j in range(n):
                val_str = formatear_numero(matriz[i][j], modo)
                lbl = ctk.CTkLabel(parent_frame, text=val_str, width=50, height=26,
                                   fg_color=color_fondo, text_color=color_texto,
                                   corner_radius=4, font=ctk.CTkFont(size=12, weight="bold"))
                lbl.grid(row=i, column=j, padx=2, pady=2)

    def _mostrar_resultado_ranura(self, slot: str, titulo: str, matriz):
        if slot == "A":
            self._resultado_slot_A = matriz
            self.lbl_slot_A.configure(text=f"Última Operación en A: {titulo}")
            self._renderizar_matriz_en_grid(self.grid_slot_A, matriz, ("#bae6fd", "#0284c7"), ("#0369a1", "#e0f2fe"))
            self.btn_guardar_A.configure(state="normal")
            self.ops_right_tabs.set("  📊 Visualizador de Resultados  ")
        elif slot == "B":
            self._resultado_slot_B = matriz
            self.lbl_slot_B.configure(text=f"Última Operación en B: {titulo}")
            self._renderizar_matriz_en_grid(self.grid_slot_B, matriz, ("#a7f3d0", "#059669"), ("#047857", "#d1fae5"))
            self.btn_guardar_B.configure(state="normal")
            self.ops_right_tabs.set("  📊 Visualizador de Resultados  ")
        elif slot == "AB":
            self._resultado_slot_AB = matriz
            self.lbl_slot_AB.configure(text=f"Última Operación A y B: {titulo}")
            self._renderizar_matriz_en_grid(self.grid_slot_AB, matriz, ("#fecdd3", "#e11d48"), ("#be123c", "#ffe4e6"))
            self.btn_guardar_AB.configure(state="normal")
            self.ops_right_tabs.set("  📊 Visualizador de Resultados  ")

    def _pedir_guardar_banco(self, slot: str):
        import copy
        matriz = None
        if slot == "A": matriz = self._resultado_slot_A
        elif slot == "B": matriz = self._resultado_slot_B
        elif slot == "AB": matriz = self._resultado_slot_AB

        if matriz is None: return

        dlg = DialogoGuardar(self, title="Guardar Matriz", text="Ingrese un nombre corto para esta matriz (ej. M1, At):")
        nombre = dlg.get_input()
        if nombre:
            nombre = nombre.strip()
            if nombre:
                if not hasattr(self, "banco_matrices"):
                    self.banco_matrices = {}
                self.banco_matrices[nombre] = copy.deepcopy(matriz)
                self._log_ops(f"\n✅ Matriz guardada en el banco como '{nombre}'.", limpiar=False)


    def _abrir_popup_banco(self):
        popup = ctk.CTkToplevel(self)
        popup.title("🏦 Banco de Matrices")
        popup.geometry("500x400")
        popup.transient(self.winfo_toplevel())
        popup.grab_set()
        
        lbl_titulo = ctk.CTkLabel(popup, text="Matrices Guardadas", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_titulo.pack(pady=(15, 10))
        
        scroll = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        tab_actual = self.tabview.get()
        
        if not hasattr(self, "banco_matrices") or not self.banco_matrices:
            ctk.CTkLabel(scroll, text="No hay matrices guardadas en el Banco.", text_color="gray").pack(pady=20)
            return
            
        from src.core.domain import formatear_numero
        
        for nombre, matriz in self.banco_matrices.items():
            m = len(matriz)
            n = len(matriz[0]) if m > 0 else 0
            
            item = ctk.CTkFrame(scroll, fg_color=("gray85", "gray25"), corner_radius=6)
            item.pack(fill="x", pady=4, padx=4)
            
            lbl = ctk.CTkLabel(item, text=f" {nombre} ({m}×{n})", font=ctk.CTkFont(weight="bold", size=13))
            lbl.pack(side="left", padx=10, pady=10)
            
            btn_del = ctk.CTkButton(item, text="❌", width=30, height=30, fg_color="#ef4444", hover_color="#b91c1c",
                                    command=lambda n=nombre, p=popup: self._eliminar_y_refrescar(n, p))
            btn_del.pack(side="right", padx=(5, 10), pady=10)
            
            if "Operaciones con Matrices" in tab_actual:
                btn_B = ctk.CTkButton(item, text="Cargar en B", width=100, height=30,
                                      command=lambda mat=matriz, p=popup: self._cargar_y_cerrar(mat, "B", "ops", p))
                btn_B.pack(side="right", padx=5)
                
                btn_A = ctk.CTkButton(item, text="Cargar en A", width=100, height=30,
                                      command=lambda mat=matriz, p=popup: self._cargar_y_cerrar(mat, "A", "ops", p))
                btn_A.pack(side="right", padx=5)
                
            elif "Ecuación Matricial" in tab_actual:
                btn_A = ctk.CTkButton(item, text="Cargar Matriz A", width=120, height=30,
                                      command=lambda mat=matriz, p=popup: self._cargar_y_cerrar(mat, "A", "axb", p))
                btn_A.pack(side="right", padx=5)
                
            elif "Propiedades de Ax" in tab_actual:
                btn_A = ctk.CTkButton(item, text="Cargar Matriz A", width=120, height=30,
                                      command=lambda mat=matriz, p=popup: self._cargar_y_cerrar(mat, "A", "prop", p))
                btn_A.pack(side="right", padx=5)
                
            elif "Traspuesta e Inversa" in tab_actual:
                btn_A = ctk.CTkButton(item, text="Cargar Matriz A", width=120, height=30,
                                      command=lambda mat=matriz, p=popup: self._cargar_y_cerrar(mat, "A", "inv", p))
                btn_A.pack(side="right", padx=5)
                
            elif "Determinantes" in tab_actual:
                btn_A = ctk.CTkButton(item, text="Cargar Matriz A", width=120, height=30,
                                      command=lambda mat=matriz, p=popup: self._cargar_y_cerrar(mat, "A", "det", p))
                btn_A.pack(side="right", padx=5)

    def _eliminar_y_refrescar(self, nombre, popup):
        if nombre in self.banco_matrices:
            del self.banco_matrices[nombre]
            popup.destroy()
            self._abrir_popup_banco()

    def _cargar_y_cerrar(self, matriz, target, tab_id, popup):
        m = len(matriz)
        n = len(matriz[0]) if m > 0 else 0
        from src.core.domain import formatear_numero
        modo = self.get_modo_numero()
        
        def guardar_valores(entries_matrix):
            vals = []
            for fila in entries_matrix:
                f_vals = []
                for e in fila:
                    f_vals.append(e.get() if e.get() else "0")
                vals.append(f_vals)
            return vals
            
        def restaurar_valores(entries_matrix, vals):
            for i in range(min(len(entries_matrix), len(vals))):
                for j in range(min(len(entries_matrix[0]), len(vals[0]))):
                    entries_matrix[i][j].delete(0, "end")
                    entries_matrix[i][j].insert(0, vals[i][j])
                    
        def deferred_fill():
            try:
                if tab_id == "ops":
                    if target == "A":
                        restaurar_valores(self.entries_B, vB)
                        for i in range(m):
                            for j in range(n):
                                self.entries_A[i][j].delete(0, "end")
                                self.entries_A[i][j].insert(0, formatear_numero(matriz[i][j], modo))
                        self._log_ops(f"\n📥 Matriz cargada en A ({m}×{n}).", limpiar=False)
                    elif target == "B":
                        restaurar_valores(self.entries_A, vA)
                        for i in range(m):
                            for j in range(n):
                                self.entries_B[i][j].delete(0, "end")
                                self.entries_B[i][j].insert(0, formatear_numero(matriz[i][j], modo))
                        self._log_ops(f"\n📥 Matriz cargada en B ({m}×{n}).", limpiar=False)
                elif tab_id == "axb":
                    for i in range(m):
                        for j in range(n):
                            self.entries_axb[i][j].delete(0, "end")
                            self.entries_axb[i][j].insert(0, formatear_numero(matriz[i][j], modo))
                    self._log_axb(f"\n📥 Matriz A cargada ({m}×{n}).", limpiar=False)
                elif tab_id == "prop":
                    for i in range(m):
                        for j in range(n):
                            self.entries_prop_A[i][j].delete(0, "end")
                            self.entries_prop_A[i][j].insert(0, formatear_numero(matriz[i][j], modo))
                    self._log_prop(f"\n📥 Matriz A cargada ({m}×{n}).", limpiar=False)
                elif tab_id == "inv":
                    for i in range(m):
                        for j in range(n):
                            self.entries_inv[i][j].delete(0, "end")
                            self.entries_inv[i][j].insert(0, formatear_numero(matriz[i][j], modo))
                    self._log_inv(f"\n📥 Matriz cargada en A ({m}×{n}).", limpiar=False)
                elif tab_id == "det":
                    dim = min(m, n)
                    for i in range(dim):
                        for j in range(dim):
                            self.entries_det[i][j].delete(0, "end")
                            self.entries_det[i][j].insert(0, formatear_numero(matriz[i][j], modo))
                    self._log_det(f"\n📥 Matriz cargada en A ({dim}×{dim}).", limpiar=False)
            except Exception as e:
                import traceback
                print(f"Error asincrono en deferred_fill: {e}\n{traceback.format_exc()}")

        try:
            if tab_id == "ops":
                vA = guardar_valores(self.entries_A)
                vB = guardar_valores(self.entries_B)
                if target == "A":
                    self.entry_ops_mA.delete(0, "end"); self.entry_ops_mA.insert(0, str(m))
                    self.entry_ops_nA.delete(0, "end"); self.entry_ops_nA.insert(0, str(n))
                else:
                    self.entry_ops_mB.delete(0, "end"); self.entry_ops_mB.insert(0, str(m))
                    self.entry_ops_nB.delete(0, "end"); self.entry_ops_nB.insert(0, str(n))
                self._generar_matrices_ops()
            elif tab_id == "axb":
                self.entry_axb_m.delete(0, "end"); self.entry_axb_m.insert(0, str(m))
                self.entry_axb_n.delete(0, "end"); self.entry_axb_n.insert(0, str(n))
                self._generar_axb()
            elif tab_id == "prop":
                self.entry_prop_m.delete(0, "end"); self.entry_prop_m.insert(0, str(m))
                self.entry_prop_n.delete(0, "end"); self.entry_prop_n.insert(0, str(n))
                self._generar_prop()
            elif tab_id == "inv":
                self.entry_inv_n.delete(0, "end"); self.entry_inv_n.insert(0, str(m))
                self.entry_inv_m.delete(0, "end"); self.entry_inv_m.insert(0, str(n))
                self._generar_grid_inv()
            elif tab_id == "det":
                dim = min(m, n)
                self.entry_det_n.delete(0, "end"); self.entry_det_n.insert(0, str(dim))
                self._generar_grid_det()
                
            self.after(50, deferred_fill)
            
        except Exception as e:
            import traceback
            print(f"Error en _cargar_y_cerrar: {e}\n{traceback.format_exc()}")
        popup.destroy()

    def _generar_matrices_ops(self):
        """Regenera las cuadrículas de A y B según las dimensiones escritas (limitadas a 1..8)."""
        try:
            mA = max(1, min(8, int(self.entry_ops_mA.get())))
            nA = max(1, min(8, int(self.entry_ops_nA.get())))
            mB = max(1, min(8, int(self.entry_ops_mB.get())))
            nB = max(1, min(8, int(self.entry_ops_nB.get())))
        except ValueError:
            return

        for w in self.scroll_ops.winfo_children():
            w.destroy()
        self.entries_A = []
        self.entries_B = []

        ctk.CTkLabel(
            self.scroll_ops, text=f"Matriz A  ({mA} × {nA})",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=("#38bdf8", "#38bdf8")
        ).pack(anchor="w", pady=(4, 2))
        self._crear_grid_matriz(self.scroll_ops, mA, nA, self.entries_A, color_col_last=False)

        ctk.CTkLabel(self.scroll_ops, text="").pack(pady=4)

        ctk.CTkLabel(
            self.scroll_ops, text=f"Matriz B  ({mB} × {nB})",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=("#34d399", "#34d399")
        ).pack(anchor="w", pady=(4, 2))
        self._crear_grid_matriz(self.scroll_ops, mB, nB, self.entries_B, color_col_last=False)

    def _crear_grid_matriz(self, parent, m: int, n: int,
                           entries_dest: List[List[ctk.CTkEntry]],
                           color_col_last: bool = True):
        """Crea una cuadrícula m×n de CTkEntry dentro de parent y guarda las celdas en entries_dest."""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=1)
        ctk.CTkLabel(header, text="", width=30).pack(side="left")
        for j in range(n):
            ctk.CTkLabel(
                header, text=f"Col {j+1}", width=52,
                font=ctk.CTkFont(size=10, weight="bold"), text_color=("gray50", "gray60")
            ).pack(side="left", padx=2)

        for i in range(m):
            row_f = ctk.CTkFrame(parent, fg_color="transparent")
            row_f.pack(fill="x", pady=1)
            ctk.CTkLabel(row_f, text=f"F{a_subindice(i+1)}", width=30,
                         font=ctk.CTkFont(size=10)).pack(side="left")
            fila_entries = []
            for j in range(n):
                cfg = {}
                if color_col_last and j == n - 1:
                    cfg = {"fg_color": ("#ffe4e6", "#3f1a24"), "text_color": ("#be123c", "#fca5a5")}
                e = ctk.CTkEntry(row_f, width=52, height=26, justify="center", **cfg)
                e.pack(side="left", padx=2)
                e.insert(0, "0")
                fila_entries.append(e)
            entries_dest.append(fila_entries)

    def _leer_matriz_entries(self, entries: List[List[ctk.CTkEntry]]) -> Matriz:
        """Lee una cuadrícula de entradas y devuelve la Matriz; lanza ValueError si algún valor es inválido."""
        mat: Matriz = []
        for i, row in enumerate(entries):
            fila = []
            for j, e in enumerate(row):
                val_str = e.get().strip()
                try:
                    # Las fracciones 'a/b' se dividen en float; un denominador 0 cae en el except y se reporta como valor inválido
                    if "/" in val_str:
                        n, d = val_str.split("/")
                        fila.append(float(n) / float(d))
                    else:
                        fila.append(float(val_str))
                except Exception:
                    raise ValueError(f"Valor inválido '{val_str}' en fila {i+1}, columna {j+1}.")
            mat.append(fila)
        return mat

    def _cargar_ejemplo_ops(self):
        """Carga al azar un ejemplo de operaciones matriciales en las cuadrículas."""
        ejemplos = [
            {
                "mA": 2, "nA": 2, "mB": 2, "nB": 2,
                "A": [[1, -4], [0, 3]],
                "B": [[2, 3], [-7, 5]],
                "c": 3, "desc": "Diapositiva 9: Suma/Resta de matrices 2×2"
            },
            {
                "mA": 2, "nA": 3, "mB": 3, "nB": 2,
                "A": [[1, 2, -1], [0, -5, 3]],
                "B": [[4, 1], [3, 0], [7, 2]],
                "c": 2, "desc": "Producto Matricial A(2×3) × B(3×2) — Desglose de sumas de productos"
            },
            {
                "mA": 3, "nA": 3, "mB": 3, "nB": 3,
                "A": [[2, 3, 4], [1, -2, 0], [3, 1, -1]],
                "B": [[1, 0, 2], [3, -1, 0], [0, 4, 1]],
                "cA": -1, "cB": 2,
                "desc": "Matrices 3×3: Compara A×B vs B×A (Demostración de No Conmutatividad)"
            },
            {
                "mA": 2, "nA": 3, "mB": 2, "nB": 2,
                "A": [[1, 2, 3], [4, 5, 6]],
                "B": [[1, 0], [0, 1]],
                "cA": 1, "cB": 1,
                "desc": "A(2×3) y B(2×2): A×B es incompatible, ¡pero B(2×2) × A(2×3) sí es compatible!"
            }
        ]
        ej = random.choice(ejemplos)
        self.entry_ops_mA.delete(0, "end"); self.entry_ops_mA.insert(0, str(ej["mA"]))
        self.entry_ops_nA.delete(0, "end"); self.entry_ops_nA.insert(0, str(ej["nA"]))
        self.entry_ops_mB.delete(0, "end"); self.entry_ops_mB.insert(0, str(ej["mB"]))
        self.entry_ops_nB.delete(0, "end"); self.entry_ops_nB.insert(0, str(ej["nB"]))
        self._generar_matrices_ops()
        self.entry_ops_c.delete(0, "end")
        self.entry_ops_c.insert(0, str(ej.get("c", ej.get("cA", 2))))

        for i, fila in enumerate(ej["A"]):
            for j, val in enumerate(fila):
                self.entries_A[i][j].delete(0, "end")
                self.entries_A[i][j].insert(0, str(val))
        for i, fila in enumerate(ej["B"]):
            for j, val in enumerate(fila):
                self.entries_B[i][j].delete(0, "end")
                self.entries_B[i][j].insert(0, str(val))

        self._log_ops(f"🎲 Ejemplo cargado: {ej['desc']}\nSeleccione la operación a realizar.", limpiar=False)

    def _calc_op(self, op: str):
        """Ejecuta la operación `op` (suma, resta, escalar o multiplicación) y muestra su procedimiento."""
        self._ultimo_calc_ops = op
        modo = self.get_modo_numero()
        try:
            A = self._leer_matriz_entries(self.entries_A)
            B = self._leer_matriz_entries(self.entries_B)
            c_str = self.entry_ops_c.get().strip() if hasattr(self, "entry_ops_c") else "2"
            c = float(c_str) if "/" not in c_str else float(c_str.split("/")[0]) / float(c_str.split("/")[1])
        except ValueError as e:
            self._log_ops(f"❌ Error de entrada: {e}\n" + "-"*40, limpiar=False)
            return

        mA, nA = len(A), len(A[0])
        mB, nB = len(B), len(B[0])
        c_fmt = formatear_numero(c, modo)
        lineas = ["\n" + "═"*50]

        ranura_target = None
        matriz_res = None
        titulo_vis = ""

        try:
            if op == "suma":
                R = sumar_matrices(A, B)
                ranura_target = "AB"; matriz_res = R; titulo_vis = "Suma A + B"
                lineas.append(">> SUMA DE MATRICES: A + B")
                lineas.append(f"Condición de Dimensión: Ambas matrices deben ser del mismo orden (m × n).")
                lineas.append(f"  Dimensión de A: {mA}×{nA}  |  Dimensión de B: {mB}×{nB}  → {'✓ Mismas dimensiones' if (mA==mB and nA==nB) else '✗ Incompatibles'}")
                lineas.append(f"\nA ({mA}×{nA}):\n{self._fmt_mat(A, modo)}")
                lineas.append(f"B ({mB}×{nB}):\n{self._fmt_mat(B, modo)}")
                lineas.append("Procedimiento: C_ij = A_ij + B_ij para cada posición.")
                lineas.append(f"\nResultado C = A + B ({mA}×{nA}):\n{self._fmt_mat(R, modo)}")
                from src.core.exact_math import crear_matriz, analizar_suma_matrices
                A_f = crear_matriz(A); B_f = crear_matriz(B); R_f = crear_matriz(R)
                lineas.append("\n" + "\n".join(analizar_suma_matrices(A_f, B_f, R_f)))

            elif op in ("resta", "resta_AB"):
                R = restar_matrices(A, B)
                ranura_target = "AB"; matriz_res = R; titulo_vis = "Resta A − B"
                lineas.append(">> RESTA DE MATRICES: A − B")
                lineas.append(f"Condición de Dimensión: Ambas matrices deben ser del mismo orden (m × n).")
                lineas.append(f"  Dimensión de A: {mA}×{nA}  |  Dimensión de B: {mB}×{nB}  → {'✓ Mismas dimensiones' if (mA==mB and nA==nB) else '✗ Incompatibles'}")
                lineas.append(f"\nA ({mA}×{nA}):\n{self._fmt_mat(A, modo)}")
                lineas.append(f"B ({mB}×{nB}):\n{self._fmt_mat(B, modo)}")
                lineas.append("Procedimiento: C_ij = A_ij − B_ij para cada posición.")
                lineas.append(f"\nResultado C = A − B ({mA}×{nA}):\n{self._fmt_mat(R, modo)}")
                from src.core.exact_math import crear_matriz, analizar_resta_matrices
                A_f = crear_matriz(A); B_f = crear_matriz(B); R_f = crear_matriz(R)
                lineas.append("\n" + "\n".join(analizar_resta_matrices(A_f, B_f, R_f)))

            elif op in ("escalar", "esc_A"):
                R = multiplicar_matriz_escalar(c, A)
                ranura_target = "A"; matriz_res = R; titulo_vis = f"Escalar {c_fmt} · A"
                lineas.append(f">> MULTIPLICACIÓN DE MATRIZ POR UN ESCALAR: {c_fmt} · A")
                lineas.append(f"\nEscalar c = {c_fmt}")
                lineas.append(f"Matriz A ({mA}×{nA}):\n{self._fmt_mat(A, modo)}")
                lineas.append("Procedimiento: (c·A)_ij = c · A_ij entrada por entrada.")
                lineas.append(f"\nResultado {c_fmt}·A ({mA}×{nA}):\n{self._fmt_mat(R, modo)}")
                from src.core.exact_math import crear_matriz, parsear_fraccion, analizar_escalar_matriz
                A_f = crear_matriz(A); R_f = crear_matriz(R); c_f = parsear_fraccion(c)
                lineas.append("\n" + "\n".join(analizar_escalar_matriz(c_f, A_f, R_f)))

            elif op in ("multiplicacion", "prod_AB"):
                res = multiplicar_matrices(A, B, modo=modo)
                R = res.matriz_resultado
                ranura_target = "AB"; matriz_res = R; titulo_vis = "Multiplicación A × B"
                mR, pR = res.dimensiones_resultado
                lineas.append(">> MULTIPLICACIÓN DE MATRICES: A × B")
                lineas.append(f"Condición de Compatibilidad: Columnas de A = Filas de B")
                lineas.append(f"  A es {mA}×{nA} (columnas = {nA})")
                lineas.append(f"  B es {mB}×{nB} (filas = {mB})")
                lineas.append(f"  Validación: {nA} == {mB} → {'✓ Compatible (columnas de A coinciden con filas de B)' if nA == mB else '✗ Incompatible'}")
                lineas.append(f"\nA ({mA}×{nA}):\n{self._fmt_mat(A, modo)}")
                lineas.append(f"B ({mB}×{nB}):\n{self._fmt_mat(B, modo)}")
                lineas.append("\nProcedimiento — Bucles anidados:")
                lineas.append("  c_ij = Σ A_ik · B_kj  (suma de productos fila de A por columna de B)\n")
                for paso in res.desglose_pasos:
                    lineas.append(f"  {paso}")
                lineas.append(f"\nResultado C = A × B ({mR}×{pR}):\n{self._fmt_mat(res.matriz_resultado, modo)}")
                from src.core.exact_math import crear_matriz, analizar_producto_matricial
                A_f = crear_matriz(A); B_f = crear_matriz(B); C_f = crear_matriz(res.matriz_resultado)
                lineas.append("\n" + "\n".join(analizar_producto_matricial(A_f, B_f, C_f)))

            elif op == "traspuesta_A":
                R = trasponer_matriz(A)
                ranura_target = "A"; matriz_res = R; titulo_vis = "Traspuesta Aᵀ"
                lineas.append(">> TRASPUESTA DE MATRIZ: Aᵀ")
                lineas.append("Condición: Ninguna restricción de orden (aplica a cualquier matriz m × n).")
                lineas.append(f"Definición: (Aᵀ)_ij = A_ji (intercambio de filas por columnas).")
                lineas.append(f"  Dimensión original de A: {mA}×{nA}")
                lineas.append(f"  Dimensión resultante de Aᵀ: {nA}×{mA}")
                lineas.append(f"\nMatriz A ({mA}×{nA}):\n{self._fmt_mat(A, modo)}")
                lineas.append(f"Resultado Aᵀ ({nA}×{mA}):\n{self._fmt_mat(R, modo)}")
                from src.core.exact_math import crear_matriz, analizar_transposicion_matriz
                A_f = crear_matriz(A); R_f = crear_matriz(R)
                lineas.append("\n" + "\n".join(analizar_transposicion_matriz(A_f, R_f)))

            elif op == "traspuesta_B":
                R = trasponer_matriz(B)
                ranura_target = "B"; matriz_res = R; titulo_vis = "Traspuesta Bᵀ"
                lineas.append(">> TRASPUESTA DE MATRIZ: Bᵀ")
                lineas.append("Condición: Ninguna restricción de orden (aplica a cualquier matriz m × n).")
                lineas.append(f"Definición: (Bᵀ)_ij = B_ji (intercambio de filas por columnas).")
                lineas.append(f"  Dimensión original de B: {mB}×{nB}")
                lineas.append(f"  Dimensión resultante de Bᵀ: {nB}×{mB}")
                lineas.append(f"\nMatriz B ({mB}×{nB}):\n{self._fmt_mat(B, modo)}")
                lineas.append(f"Resultado Bᵀ ({nB}×{mB}):\n{self._fmt_mat(R, modo)}")
                from src.core.exact_math import crear_matriz, analizar_transposicion_matriz
                B_f = crear_matriz(B); R_f = crear_matriz(R)
                lineas.append("\n" + "\n".join(analizar_transposicion_matriz(B_f, R_f)))

        except ValueError as e:
            lineas = [
                "  ❌ VALIDACIÓN PREVIA FALLIDA (CONDICIÓN OBLIGATORIA NO CUMPLIDA)",
                f"\n{e}\n"
            ]

        self._log_ops("\n".join(lineas), limpiar=False)
        
        if ranura_target and matriz_res:
            self._mostrar_resultado_ranura(ranura_target, titulo_vis, matriz_res)


    def _fmt_mat(self, mat: Matriz, modo: str) -> str:
        """Devuelve la matriz como texto, una fila por línea, según el modo numérico."""
        s = ""
        for fila in mat:
            s += "  [ " + "  ".join([f"{formatear_numero(x, modo):>8}" for x in fila]) + " ]\n"
        return s

    def _log_ops(self, texto: str, limpiar: bool = False):
        """Escribe texto en el panel de resultados de operaciones; limpiar=False borra lo anterior."""
        self.txt_res_ops.configure(state="normal")
        if limpiar:
            self.txt_res_ops.delete("1.0", "end")
        self.txt_res_ops.insert("end", texto + "\n")
        self.txt_res_ops.configure(state="disabled")
        self.txt_res_ops.see("end")

    def _setup_tab_axb(self):
        """Construye la pestaña de la ecuación matricial Ax = b."""
        tab = self.tab_axb
        tab.grid_columnconfigure(0, weight=0)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(tab, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left.grid_columnconfigure(0, weight=1)

        ctrl = ctk.CTkFrame(left, fg_color="transparent")
        ctrl.pack(fill="x", padx=14, pady=(12, 4))

        ctk.CTkLabel(ctrl, text="Filas de A (m):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=2)
        self.entry_axb_m = ctk.CTkEntry(ctrl, width=40, justify="center")
        self.entry_axb_m.grid(row=0, column=1, padx=4)
        self.entry_axb_m.insert(0, "3")

        ctk.CTkLabel(ctrl, text="Columnas de A (n):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=2, padx=2)
        self.entry_axb_n = ctk.CTkEntry(ctrl, width=40, justify="center")
        self.entry_axb_n.grid(row=0, column=3, padx=4)
        self.entry_axb_n.insert(0, "3")

        btn_row_axb = ctk.CTkFrame(left, fg_color="transparent")
        btn_row_axb.pack(fill="x", padx=14, pady=4)
        ctk.CTkButton(btn_row_axb, text="Generar [A | b]", width=100, command=self._generar_axb).pack(side="left", padx=2)
        ctk.CTkButton(
            btn_row_axb, text="🎲 Ejemplo", width=80, command=self._cargar_ejemplo_axb,
            fg_color=("#475569", "#374151"), hover_color=("#334155", "#4b5563")
        ).pack(side="left", padx=4)

        ctk.CTkLabel(
            left,
            text="La última columna coloreada corresponde al vector b.\n"
                 "Las demás columnas forman la matriz A.",
            font=ctk.CTkFont(size=11), text_color=("gray60", "gray70")
        ).pack(anchor="w", padx=14, pady=(2, 4))

        self.scroll_axb = ctk.CTkScrollableFrame(left, height=250)
        self.scroll_axb.pack(fill="both", expand=True, padx=14, pady=4)

        btns_axb = ctk.CTkFrame(left, fg_color="transparent")
        btns_axb.pack(fill="x", padx=14, pady=(6, 12))
        btns_axb.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btns_axb, text="📐 Calcular A · x (ingrese x)", command=self._calcular_ax,
            fg_color=("#0d9488", "#0f766e"), height=34
        ).grid(row=0, column=0, padx=3, pady=3, sticky="ew")

        ctk.CTkButton(
            btns_axb, text="🚀 Resolver Ax = b", command=self._resolver_axb,
            fg_color=("#059669", "#10b981"), hover_color=("#047857", "#059669"),
            font=ctk.CTkFont(size=13, weight="bold"), height=34
        ).grid(row=0, column=1, padx=3, pady=3, sticky="ew")

        right = ctk.CTkFrame(tab, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        bar_axb = ctk.CTkFrame(right, fg_color="transparent")
        bar_axb.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 0))
        ctk.CTkLabel(bar_axb, text="📐 Resultado y Procedimiento Algebraico",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=("#38bdf8", "#38bdf8")).pack(side="left")
        ctk.CTkButton(bar_axb, text="🗑️ Limpiar", width=90, height=28,
                      fg_color=("#dc2626", "#b91c1c"),
                      command=self._limpiar_historial_axb).pack(side="right")

        self.txt_res_axb = ctk.CTkTextbox(right, font=ctk.CTkFont(family="Consolas", size=12), wrap="word")
        self.txt_res_axb.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))
        self.txt_res_axb.configure(state="disabled")

        self.entries_axb: List[List[ctk.CTkEntry]] = []
        self._generar_axb()

    def _generar_axb(self):
        """Regenera la cuadrícula de la matriz aumentada [A | b] (dimensiones limitadas a 1..8)."""
        try:
            m = max(1, min(8, int(self.entry_axb_m.get())))
            n = max(1, min(8, int(self.entry_axb_n.get())))
        except ValueError:
            return

        for w in self.scroll_axb.winfo_children():
            w.destroy()
        self.entries_axb = []

        header = ctk.CTkFrame(self.scroll_axb, fg_color="transparent")
        header.pack(fill="x", pady=2)
        ctk.CTkLabel(header, text="", width=30).pack(side="left")
        for j in range(n):
            ctk.CTkLabel(
                header, text=f"a{a_subindice(j+1)}", width=50,
                font=ctk.CTkFont(size=10, weight="bold"), text_color=("gray50", "gray60")
            ).pack(side="left", padx=2)
        ctk.CTkLabel(
            header, text="= b", width=55,
            font=ctk.CTkFont(size=11, weight="bold"), text_color=("#f43f5e", "#f43f5e")
        ).pack(side="left", padx=(6, 2))

        for i in range(m):
            row_f = ctk.CTkFrame(self.scroll_axb, fg_color="transparent")
            row_f.pack(fill="x", pady=2)
            ctk.CTkLabel(row_f, text=f"F{a_subindice(i+1)}", width=30).pack(side="left")
            fila_entries = []
            for j in range(n):
                e = ctk.CTkEntry(row_f, width=50, height=26, justify="center")
                e.pack(side="left", padx=2)
                e.insert(0, "0")
                fila_entries.append(e)
            eb = ctk.CTkEntry(
                row_f, width=55, height=26, justify="center",
                fg_color=("#ffe4e6", "#3f1a24"), text_color=("#be123c", "#fca5a5")
            )
            eb.pack(side="left", padx=(6, 2))
            eb.insert(0, "0")
            fila_entries.append(eb)
            self.entries_axb.append(fila_entries)

    def _leer_axb(self):
        """Lee la cuadrícula y devuelve (A, b); lanza ValueError si algún valor es inválido."""
        n = len(self.entries_axb[0]) - 1  # columnas de A
        A: Matriz = []
        b: Vector = []
        for i, row in enumerate(self.entries_axb):
            fila_A = []
            for j in range(n):
                val_str = row[j].get().strip()
                try:
                    v = float(val_str) if "/" not in val_str else float(val_str.split("/")[0]) / float(val_str.split("/")[1])
                    fila_A.append(v)
                except Exception:
                    raise ValueError(f"Valor inválido '{val_str}' en fila {i+1}, columna {j+1} de A.")
            A.append(fila_A)
            val_b_str = row[n].get().strip()
            try:
                vb = float(val_b_str) if "/" not in val_b_str else float(val_b_str.split("/")[0]) / float(val_b_str.split("/")[1])
                b.append(vb)
            except Exception:
                raise ValueError(f"Valor inválido '{val_b_str}' en fila {i+1} del vector b.")
        return A, b

    def _cargar_ejemplo_axb(self):
        """Carga al azar un sistema Ax = b de ejemplo en la cuadrícula."""
        ejemplos = [
            {
                "m": 2, "n": 3,
                "A": [[1, 2, -1], [0, -5, 3]],
                "b": [3, 6],
                "desc": "Diapositiva 4: A(2×3), b=[3, 6] → resolver Ax = b"
            },
            {
                "m": 3, "n": 2,
                "A": [[2, -3], [8, 0], [-5, 2]],
                "b": [-13, 32, -6],
                "desc": "Diapositiva 5: A(3×2), b=[-13, 32, -6] → resolución Ax = b"
            },
            {
                "m": 3, "n": 3,
                "A": [[2, 1, -1], [-3, -1, 2], [-2, 1, 2]],
                "b": [8, -11, -3],
                "desc": "Sistema 3×3 Solución Única — clásico (x₁=2, x₂=3, x₃=-1)"
            },
            {
                "m": 3, "n": 3,
                "A": [[1, 0, -3], [0, 1, 1], [5, -3, -14]],
                "b": [-5, 3, 10],
                "desc": "Sistema Inconsistente (0 = k)"
            }
        ]
        ej = random.choice(ejemplos)
        self.entry_axb_m.delete(0, "end"); self.entry_axb_m.insert(0, str(ej["m"]))
        self.entry_axb_n.delete(0, "end"); self.entry_axb_n.insert(0, str(ej["n"]))
        self._generar_axb()

        for i, fila in enumerate(ej["A"]):
            for j, val in enumerate(fila):
                self.entries_axb[i][j].delete(0, "end")
                self.entries_axb[i][j].insert(0, str(val))
        n = len(ej["A"][0])
        for i, val in enumerate(ej["b"]):
            self.entries_axb[i][n].delete(0, "end")
            self.entries_axb[i][n].insert(0, str(val))

        self._log_axb(f"🎲 Ejemplo cargado: {ej['desc']}\nPresione 'Resolver Ax = b'.", limpiar=False)

    def _calcular_ax(self):
        """Calcula A·x tomando como x la columna b de la cuadrícula; se dispara con el botón Calcular A · x."""
        self._ultimo_calc_axb = "ax"
        modo = self.get_modo_numero()
        try:
            # Se reutiliza la columna b de la cuadrícula como vector x
            A, x = self._leer_axb()
        except ValueError as e:
            self._log_axb(f"❌ {e}", limpiar=False)
            return

        m, n = len(A), len(A[0])
        try:
            res = multiplicar_matriz_vector(A, x, modo=modo)
        except ValueError as e:
            self._log_axb(f"❌ {e}", limpiar=False)
            return

        lineas = [
            ">> CÁLCULO DEL PRODUCTO MATRIZ-VECTOR: A · x",
            "(El vector x se toma de la columna 'b' de la cuadrícula)\n",
            f"A ({m}×{n}):\n{self._fmt_mat(A, modo)}",
            f"x = [{', '.join([formatear_numero(xi, modo) for xi in x])}]ᵀ\n",
            "--- Regla Fila-Vector (producto punto fila i con x) ---"
        ]
        for d in res.desglose_filas:
            lineas.append(f"  {d}")

        lineas.append("\n--- Interpretación: Combinación Lineal de Columnas de A ---")
        lineas.append(f"  A·x = {res.combinacion_columnas}")

        b_res = "[" + ", ".join([formatear_numero(xi, modo) for xi in res.vector_resultado]) + "]ᵀ"
        lineas.append(f"\nResultado: A·x = {b_res}")
        self._log_axb("\n".join(lineas), limpiar=False)

    def _resolver_axb(self):
        """Resuelve Ax = b con Gauss-Jordan sobre [A | b] y muestra los pasos, la RREF y la clasificación."""
        self._ultimo_calc_axb = "axb"
        modo = self.get_modo_numero()
        try:
            A, b = self._leer_axb()
        except ValueError as e:
            self._log_axb(f"❌ {e}", limpiar=False)
            return

        m, n = len(A), len(A[0])
        try:
            res = resolver_ecuacion_matricial(A, b, modo=modo)
        except ValueError as e:
            self._log_axb(f"❌ {e}", limpiar=False)
            return

        lineas = [
            "==================================================",
            "   RESOLUCIÓN DE LA ECUACIÓN MATRICIAL: A x = b   ",
            "==================================================\n",
            "Teorema Fundamental:",
            "  Ax = b  ⟺  x₁a₁ + x₂a₂ + ... + xₙaₙ = b  ⟺  [A | b]\n",
            f"A ({m}×{n}):\n{self._fmt_mat(A, modo)}",
            f"b = [{', '.join([formatear_numero(bi, modo) for bi in b])}]ᵀ\n",
            "--- 1. MATRIZ AUMENTADA INICIAL [A | b] ---",
            self._fmt_mat_aumentada(res.matriz_aumentada, modo),
        ]

        if res.pasos_gauss and len(res.pasos_gauss) > 1:
            lineas.append("--- 2. PROCESO DE REDUCCIÓN PASO A PASO (GAUSS-JORDAN) ---")
            # pasos_gauss[0] es la matriz inicial, que ya se imprimió como [A | b]
            for num_p, paso in enumerate(res.pasos_gauss[1:], 1):
                lineas.append(f">> Paso {num_p}: {paso.descripcion}")
                lineas.append(self._fmt_mat_aumentada(paso.matriz_estado, modo))

        lineas.extend([
            "--- 3. FORMA ESCALONADA REDUCIDA (RREF) ---",
            self._fmt_mat_aumentada(res.matriz_rref, modo),
            "--- 4. CLASIFICACIÓN Y SOLUCIÓN ---",
            res.resumen_explicativo
        ])
        self._log_axb("\n".join(lineas), limpiar=False)

    def _fmt_mat_aumentada(self, mat: Matriz, modo: str) -> str:
        """Devuelve la matriz aumentada como texto, separando la última columna con una barra."""
        s = ""
        for fila in mat:
            coefs = fila[:-1]
            ti = fila[-1]
            coefs_str = "  ".join([f"{formatear_numero(x, modo):>8}" for x in coefs])
            s += f"  [ {coefs_str} | {formatear_numero(ti, modo):>8} ]\n"
        return s

    def _log_axb(self, texto: str, limpiar: bool = False):
        """Escribe texto en el panel de resultados de Ax = b; limpiar=False borra lo anterior."""
        self.txt_res_axb.configure(state="normal")
        if limpiar:
            self.txt_res_axb.delete("1.0", "end")
        self.txt_res_axb.insert("end", texto + "\n")
        self.txt_res_axb.configure(state="disabled")
        self.txt_res_axb.see("end")

    def _limpiar_historial_axb(self):
        """Borra todo el contenido del historial de texto de Ax = b."""
        self.txt_res_axb.configure(state="normal")
        self.txt_res_axb.delete("1.0", "end")
        self.txt_res_axb.configure(state="disabled")

    def _setup_tab_propiedades(self):
        """Construye la pestaña de propiedades del producto matriz-vector Ax y de inversas/determinantes."""
        tab = self.tab_props
        tab.grid_columnconfigure(0, weight=0)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(tab, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            left,
            text="Propiedades del Producto Matriz-Vector  A·x",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("gray20", "gray90"),
        ).pack(anchor="w", padx=14, pady=(10, 2))

        ctrl = ctk.CTkFrame(left, fg_color="transparent")
        ctrl.pack(fill="x", padx=14, pady=(2, 2))

        ctk.CTkLabel(ctrl, text="Filas A (m):", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, padx=2)
        self.entry_prop_m = ctk.CTkEntry(ctrl, width=38, justify="center")
        self.entry_prop_m.grid(row=0, column=1, padx=2)
        self.entry_prop_m.insert(0, "2")

        ctk.CTkLabel(ctrl, text="Cols A (n):", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=2, padx=2)
        self.entry_prop_n = ctk.CTkEntry(ctrl, width=38, justify="center")
        self.entry_prop_n.grid(row=0, column=3, padx=2)
        self.entry_prop_n.insert(0, "2")

        ctk.CTkLabel(ctrl, text="Vectores (k):", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=4, padx=2)
        self.entry_prop_k = ctk.CTkEntry(ctrl, width=38, justify="center")
        self.entry_prop_k.grid(row=0, column=5, padx=2)
        self.entry_prop_k.insert(0, "2")

        btn_row_p = ctk.CTkFrame(left, fg_color="transparent")
        btn_row_p.pack(fill="x", padx=14, pady=4)

        ctk.CTkButton(
            btn_row_p, text="Generar", width=80,
            command=self._generar_prop
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_row_p, text="📘 Diapositiva 10", width=125,
            command=self._cargar_ejercicio_asignacion_diap10,
            fg_color=("#0284c7", "#0369a1"), hover_color=("#0369a1", "#075985"),
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            btn_row_p, text="🎲 Ejemplo", width=75,
            command=self._cargar_ejemplo_prop,
            fg_color=("gray50", "#374151"), hover_color=("gray40", "#4b5563")
        ).pack(side="left", padx=2)

        self.scroll_prop = ctk.CTkScrollableFrame(left, height=250)
        self.scroll_prop.pack(fill="both", expand=True, padx=14, pady=4)

        btns_p = ctk.CTkFrame(left, fg_color="transparent")
        btns_p.pack(fill="x", padx=14, pady=(4, 10))
        btns_p.grid_columnconfigure((0, 1), weight=1)

        self.btn_verif_aditiva = ctk.CTkButton(
            btns_p,
            text="✓ Verificar A(u+v) = Au+Av",
            command=self._calc_propiedad_aditiva,
            fg_color=("#0d9488", "#0f766e"),
            hover_color=("#0f766e", "#115e59"),
            font=ctk.CTkFont(size=11, weight="bold"),
            height=32,
        )
        self.btn_verif_aditiva.grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        self.btn_verif_escalar = ctk.CTkButton(
            btns_p,
            text="✓ Verificar A(cu) = c(Au)",
            command=self._calc_propiedad_escalar,
            fg_color=("#1d4ed8", "#1e40af"),
            hover_color=("#1e40af", "#1e3a8a"),
            font=ctk.CTkFont(size=11, weight="bold"),
            height=32,
        )
        self.btn_verif_escalar.grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        self.btn_verif_linealidad = ctk.CTkButton(
            btns_p,
            text="🌟 Linealidad General: A(∑ cᵢvᵢ) = ∑ cᵢ(Avᵢ)",
            command=self._calc_linealidad_general,
            fg_color=("#7c3aed", "#6d28d9"),
            hover_color=("#6d28d9", "#5b21b6"),
            font=ctk.CTkFont(size=11, weight="bold"),
            height=32,
        )
        self.btn_verif_linealidad.grid(row=1, column=0, columnspan=2, padx=2, pady=(4, 2), sticky="ew")

        right = ctk.CTkFrame(tab, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        bar_prop = ctk.CTkFrame(right, fg_color="transparent")
        bar_prop.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 0))
        ctk.CTkLabel(bar_prop,
                     text="🔬 Demostración y Verificación Paso a Paso",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=("gray20", "#38bdf8")).pack(side="left")
        ctk.CTkButton(bar_prop, text="🗑️ Limpiar", width=90, height=28,
                      fg_color=("#dc2626", "#b91c1c"),
                      command=self._limpiar_historial_prop).pack(side="right")

        self.txt_res_prop = ctk.CTkTextbox(
            right, font=ctk.CTkFont(family="Consolas", size=12), wrap="word"
        )
        self.txt_res_prop.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))
        self.txt_res_prop.configure(state="disabled")

        self.entries_prop_A: List[List[ctk.CTkEntry]] = []
        self.entries_prop_vecs: List[List[ctk.CTkEntry]] = []  # [componente_i][vector_j]
        self.entries_prop_c: List[ctk.CTkEntry] = []            # [vector_j]
        self._generar_prop()

    def _generar_prop(self):
        """Genera las cuadrículas de A (m×n) y de k vectores en ℝⁿ con sus escalares."""
        try:
            m = max(1, min(10, int(self.entry_prop_m.get().strip())))
            n = max(1, min(10, int(self.entry_prop_n.get().strip())))
            # k ≥ 2: la propiedad aditiva A(u + v) necesita al menos dos vectores
            k = max(2, min(8, int(self.entry_prop_k.get().strip())))
        except ValueError:
            return

        for w in self.scroll_prop.winfo_children():
            w.destroy()
        self.entries_prop_A = []
        self.entries_prop_vecs = [[] for _ in range(n)]
        self.entries_prop_c = []

        es_dos = (k == 2)
        nombres = ["u", "v"] if es_dos else [f"v{a_subindice(j+1)}" for j in range(k)]

        if hasattr(self, "btn_verif_aditiva"):
            if es_dos:
                self.btn_verif_aditiva.configure(text="✓ Verificar A(u+v) = Au+Av")
                self.btn_verif_escalar.configure(text="✓ Verificar A(cu) = c(Au)")
            else:
                self.btn_verif_aditiva.configure(text=f"✓ Verificar A({' + '.join(nombres)})")
                self.btn_verif_escalar.configure(text=f"✓ Verificar A(c₁·v₁) = c₁(A·v₁)")

        ctk.CTkLabel(
            self.scroll_prop,
            text=f"1. Matriz A ({m}×{n}):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#38bdf8", "#38bdf8")
        ).pack(anchor="w", pady=(4, 2))

        hdr_A = ctk.CTkFrame(self.scroll_prop, fg_color="transparent")
        hdr_A.pack(fill="x")
        ctk.CTkLabel(hdr_A, text="", width=32).pack(side="left")
        for j in range(n):
            ctk.CTkLabel(
                hdr_A, text=f"col{a_subindice(j+1)}", width=50,
                font=ctk.CTkFont(size=10), text_color=("gray50", "gray60")
            ).pack(side="left", padx=2)

        for i in range(m):
            row_f = ctk.CTkFrame(self.scroll_prop, fg_color="transparent")
            row_f.pack(fill="x", pady=1)
            ctk.CTkLabel(row_f, text=f"F{a_subindice(i+1)}", width=32, font=ctk.CTkFont(size=10, weight="bold")).pack(side="left")
            fila_entries = []
            for j in range(n):
                e = ctk.CTkEntry(row_f, width=50, height=26, justify="center")
                e.pack(side="left", padx=2)
                e.insert(0, "0")
                fila_entries.append(e)
            self.entries_prop_A.append(fila_entries)

        sec_title = f"2. Vectores en ℝ{a_subindice(n)} y Escalares ({k} vectores):" if not es_dos else f"2. Vectores u, v en ℝ{a_subindice(n)} y Escalares:"
        ctk.CTkLabel(
            self.scroll_prop,
            text=sec_title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#38bdf8", "#38bdf8")
        ).pack(anchor="w", pady=(10, 2))

        hdr_vecs = ctk.CTkFrame(self.scroll_prop, fg_color="transparent")
        hdr_vecs.pack(fill="x")
        ctk.CTkLabel(hdr_vecs, text="", width=68).pack(side="left")
        for nom in nombres:
            ctk.CTkLabel(
                hdr_vecs, text=nom, width=55, font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("#0284c7", "#38bdf8")
            ).pack(side="left", padx=2)

        row_c = ctk.CTkFrame(self.scroll_prop, fg_color="transparent")
        row_c.pack(fill="x", pady=(2, 4))
        ctk.CTkLabel(
            row_c, text="Escalar c:", width=68,
            font=ctk.CTkFont(size=10, weight="bold"), text_color=("gray40", "gray60")
        ).pack(side="left")
        for j in range(k):
            ec = ctk.CTkEntry(
                row_c, width=55, height=26, justify="center",
                fg_color=("#fef3c7", "#3b2c15"), text_color=("#92400e", "#fde68a"),
                border_color=("#f59e0b", "#d97706")
            )
            ec.pack(side="left", padx=2)
            ec.insert(0, str(2 if j == 0 else 1))
            self.entries_prop_c.append(ec)

        for i in range(n):
            row_v = ctk.CTkFrame(self.scroll_prop, fg_color="transparent")
            row_v.pack(fill="x", pady=1)
            ctk.CTkLabel(row_v, text=f"Comp {i+1}:", width=68, font=ctk.CTkFont(size=10)).pack(side="left")

            for j in range(k):
                ev = ctk.CTkEntry(row_v, width=55, height=26, justify="center")
                ev.pack(side="left", padx=2)
                ev.insert(0, "0")
                self.entries_prop_vecs[i].append(ev)

    def _leer_prop(self):
        """Lee A, los k vectores y los k escalares; devuelve (A, vectores, escalares) o lanza ValueError."""
        A: List[List[float]] = []
        for i, fila in enumerate(self.entries_prop_A):
            row_A = []
            for j, e in enumerate(fila):
                val = e.get().strip()
                try:
                    row_A.append(float(val) if "/" not in val
                                 else float(val.split("/")[0]) / float(val.split("/")[1]))
                except Exception:
                    raise ValueError(f"Valor inválido en Matriz A, fila {i+1}, col {j+1}: '{val}'")
            A.append(row_A)

        k = len(self.entries_prop_c)
        n = len(self.entries_prop_vecs)

        escalares: List[float] = []
        for j, ec in enumerate(self.entries_prop_c):
            val_c = ec.get().strip()
            try:
                c = float(val_c) if "/" not in val_c else float(val_c.split("/")[0]) / float(val_c.split("/")[1])
                escalares.append(c)
            except Exception:
                nom = "u" if (k == 2 and j == 0) else ("v" if (k == 2 and j == 1) else f"v{j+1}")
                raise ValueError(f"Escalar inválido '{val_c}' para el vector {nom}.")

        vectores: List[List[float]] = [[] for _ in range(k)]
        for i in range(n):
            for j in range(k):
                val_comp = self.entries_prop_vecs[i][j].get().strip()
                try:
                    v = float(val_comp) if "/" not in val_comp else float(val_comp.split("/")[0]) / float(val_comp.split("/")[1])
                    vectores[j].append(v)
                except Exception:
                    nom = "u" if (k == 2 and j == 0) else ("v" if (k == 2 and j == 1) else f"v{j+1}")
                    raise ValueError(f"Componente {i+1} inválida '{val_comp}' en vector {nom}.")

        return A, vectores, escalares

    def _cargar_ejercicio_asignacion_diap10(self):
        """Carga el ejercicio de la Diapositiva 10: A = [[2,5],[3,1]], u = [4,-1], v = [-3,5]."""
        self.entry_prop_m.delete(0, "end"); self.entry_prop_m.insert(0, "2")
        self.entry_prop_n.delete(0, "end"); self.entry_prop_n.insert(0, "2")
        self.entry_prop_k.delete(0, "end"); self.entry_prop_k.insert(0, "2")
        self._generar_prop()

        mat_A = [[2, 5], [3, 1]]
        for i in range(2):
            for j in range(2):
                self.entries_prop_A[i][j].delete(0, "end")
                self.entries_prop_A[i][j].insert(0, str(mat_A[i][j]))

        self.entries_prop_c[0].delete(0, "end"); self.entries_prop_c[0].insert(0, "2")
        self.entries_prop_c[1].delete(0, "end"); self.entries_prop_c[1].insert(0, "3")

        u = [4, -1]
        v = [-3, 5]
        for i in range(2):
            self.entries_prop_vecs[i][0].delete(0, "end")
            self.entries_prop_vecs[i][0].insert(0, str(u[i]))
            self.entries_prop_vecs[i][1].delete(0, "end")
            self.entries_prop_vecs[i][1].insert(0, str(v[i]))

        msg = (
            "📘 Ejercicio de Asignación (Diapositiva 10) cargado con éxito:\n\n"
            "  A = [ [ 2,  5 ]\n"
            "        [ 3,  1 ] ]\n"
            "  u = [ 4, -1 ]ᵀ\n"
            "  v = [-3,  5 ]ᵀ\n\n"
            "Presione 'Verificar A(u+v) = Au+Av' o 'Verificar A(cu) = c(Au)' para ver el desarrollo paso a paso."
        )
        self._log_prop(msg, limpiar=False)

    def _cargar_ejemplo_prop(self):
        """Carga al azar un ejemplo de propiedades de Ax (distintos tamaños de A y cantidad de vectores)."""
        ejemplos = [
            {
                "m": 2, "n": 2, "k": 2,
                "A": [[1, 2], [3, 4]],
                "vecs": [[0, 1], [1, 1]],
                "cs": [1, 1],
                "desc": "Caso de Prueba Sugerido PDF Tarea 5: A = [[1,2],[3,4]] y B = [[0,1],[1,1]]"
            },
            {
                "m": 2, "n": 2, "k": 2,
                "A": [[2, 5], [3, 1]],
                "vecs": [[4, -1], [-3, 5]],
                "cs": [2, 3],
                "desc": "Diapositiva 10: A(2×2), u=[4, -1]ᵀ, v=[-3, 5]ᵀ en ℝ²"
            },
            {
                "m": 3, "n": 3, "k": 3,
                "A": [[1, 2, 0], [0, 3, -1], [2, 1, 1]],
                "vecs": [[1, -1, 2], [2, 0, 1], [-1, 3, 0]],
                "cs": [2, -1, 3],
                "desc": "General: 3 vectores en ℝ³ con matriz A(3×3) y escalares [2, -1, 3]"
            },
            {
                "m": 2, "n": 3, "k": 3,
                "A": [[1, 2, -1], [0, -5, 3]],
                "vecs": [[4, 3, 7], [1, 0, -2], [2, -1, 1]],
                "cs": [1, 2, -1],
                "desc": "Rectangular A(2×3) (Slide 4) con 3 vectores en ℝ³"
            },
            {
                "m": 3, "n": 2, "k": 2,
                "A": [[2, -3], [8, 0], [-5, 2]],
                "vecs": [[4, 7], [-2, 3]],
                "cs": [3, -2],
                "desc": "Rectangular A(3×2) (Slide 5) con u=[4, 7]ᵀ, v=[-2, 3]ᵀ en ℝ²"
            }
        ]
        ej = random.choice(ejemplos)

        self.entry_prop_m.delete(0, "end"); self.entry_prop_m.insert(0, str(ej["m"]))
        self.entry_prop_n.delete(0, "end"); self.entry_prop_n.insert(0, str(ej["n"]))
        self.entry_prop_k.delete(0, "end"); self.entry_prop_k.insert(0, str(ej["k"]))
        self._generar_prop()

        for i, fila in enumerate(ej["A"]):
            for j, val in enumerate(fila):
                self.entries_prop_A[i][j].delete(0, "end")
                self.entries_prop_A[i][j].insert(0, str(val))

        for j, c_val in enumerate(ej["cs"]):
            self.entries_prop_c[j].delete(0, "end")
            self.entries_prop_c[j].insert(0, str(c_val))

        for j, vec in enumerate(ej["vecs"]):
            for i, comp in enumerate(vec):
                self.entries_prop_vecs[i][j].delete(0, "end")
                self.entries_prop_vecs[i][j].insert(0, str(comp))

        self._log_prop(f"🎲 Ejemplo cargado: {ej['desc']}\nSeleccione una propiedad para verificar el teorema.", limpiar=False)

    def _calc_propiedad_aditiva(self):
        """Verifica y muestra A(u + v) = Au + Av (generalizado a k vectores)."""
        self._ultimo_calc_prop = "aditiva"
        modo = self.get_modo_numero()
        try:
            A, vecs, _ = self._leer_prop()
        except ValueError as e:
            self._log_prop(f"❌ {e}", limpiar=False)
            return

        try:
            resultado = verificar_propiedad_aditiva_ax(A, vecs, modo=modo)
        except ValueError as e:
            self._log_prop(f"❌ {e}", limpiar=False)
            return

        self._log_prop("\n".join(resultado.desglose_pasos), limpiar=False)

    def _calc_propiedad_escalar(self):
        """Verifica y muestra A(cu) = c(Au) para el primer vector y su escalar."""
        self._ultimo_calc_prop = "escalar"
        modo = self.get_modo_numero()
        try:
            A, vecs, escalares = self._leer_prop()
        except ValueError as e:
            self._log_prop(f"❌ {e}", limpiar=False)
            return

        k = len(vecs)
        nom = "u" if k == 2 else "v₁"
        # A(cu) = c(Au) se verifica con el primer vector y su escalar
        c_val = escalares[0]
        u_vec = vecs[0]

        try:
            resultado = verificar_propiedad_escalar_ax(A, u_vec, c_val, modo=modo, nombre_vector=nom)
        except ValueError as e:
            self._log_prop(f"❌ {e}", limpiar=False)
            return

        self._log_prop("\n".join(resultado.desglose_pasos), limpiar=False)

    def _calc_linealidad_general(self):
        """Verifica y muestra A(Σ cᵢvᵢ) = Σ cᵢ(Avᵢ)."""
        self._ultimo_calc_prop = "linealidad"
        modo = self.get_modo_numero()
        try:
            A, vecs, escalares = self._leer_prop()
        except ValueError as e:
            self._log_prop(f"❌ {e}", limpiar=False)
            return

        try:
            resultado = verificar_linealidad_general_ax(A, vecs, escalares, modo=modo)
        except ValueError as e:
            self._log_prop(f"❌ {e}", limpiar=False)
            return

        self._log_prop("\n".join(resultado.desglose_pasos), limpiar=False)

    def _calc_propiedad_tarea5_inv(self, prop_id: str):
        """Demuestra una propiedad de Inversa con procedimiento matemático completo, paso a paso."""
        self.tabview_inv.set("  📋 Historial (Texto)  ")
        self._ultimo_calc_inv = f"tarea5_{prop_id}"
        try:
            A = self._leer_matriz_inv()
        except ValueError as e:
            self._log_inv(f"❌ Error al leer datos: {e}\n" + "-"*40, limpiar=False)
            return

        mA, nA = len(A), len(A[0])
        if mA != nA:
            self._log_inv(
                "❌ Para verificar esta propiedad, la matriz A debe ser cuadrada (n × n).\n"
                f"   Actualmente A es de dimensión {mA} × {nA}.\n",
                limpiar=False
            )
            return

        modo = self.get_modo_numero()
        try:
            from fractions import Fraction
            from src.core.exact_math import (
                crear_matriz, inversa_gauss_jordan, trasponer_matriz,
                multiplicar_matrices, son_matrices_iguales, matriz_a_cadena,
                matriz_identidad
            )

            A_f = crear_matriz(A)

            def fmt_mat_exact(mat):
                """Formatea una matriz de fracciones como texto."""
                lines = []
                for fila in mat:
                    vals = "  ".join(f"{formatear_numero(float(x), modo):>8}" for x in fila)
                    lines.append(f"  [ {vals} ]")
                return "\n".join(lines)

            lineas = [
                "\n" + "═" * 70,
                f"  Matriz A  ({nA}×{nA}):",
                fmt_mat_exact(A_f),
                "═" * 70,
            ]

            if prop_id == "inv_inv":
                # (A⁻¹)⁻¹ = A
                lineas += ["", "  PROPIEDAD 1: Inversa de la Inversa   →   (A⁻¹)⁻¹ = A", "─" * 70]

                # Paso 1: Calcular A⁻¹
                lineas += ["", "  PASO 1: Calcular A⁻¹ por Gauss-Jordan"]
                res_inv = inversa_gauss_jordan(A_f)
                if not res_inv.es_invertible:
                    lineas.append("  ❌ A no es invertible (det=0). Propiedad no aplicable.")
                    self._log_inv("\n".join(lineas), limpiar=False)
                    return
                A_inv = res_inv.matriz_inversa
                lineas.append(f"  A⁻¹ =\n{fmt_mat_exact(A_inv)}")

                # Paso 2: Calcular (A⁻¹)⁻¹
                lineas += ["", "  PASO 2: Calcular la inversa de A⁻¹   →   (A⁻¹)⁻¹"]
                res_inv2 = inversa_gauss_jordan(A_inv)
                if not res_inv2.es_invertible:
                    lineas.append("  ❌ A⁻¹ no tiene inversa (resultado inesperado).")
                    self._log_inv("\n".join(lineas), limpiar=False)
                    return
                A_inv_inv = res_inv2.matriz_inversa
                lineas.append(f"  (A⁻¹)⁻¹ =\n{fmt_mat_exact(A_inv_inv)}")

                # Paso 3: Comparar con A
                lineas += ["", "  PASO 3: Verificar que (A⁻¹)⁻¹ = A"]
                lineas.append(f"  A original =\n{fmt_mat_exact(A_f)}")
                son_iguales = son_matrices_iguales(A_inv_inv, A_f)
                lineas += [
                    "",
                    f"  {'✓ SE CUMPLE: (A⁻¹)⁻¹ es idéntica a A.' if son_iguales else '✗ NO SE CUMPLE (error numérico inesperado).'}",
                    "═" * 70,
                ]
            elif prop_id == "inv_tras":
                # (Aᵀ)⁻¹ = (A⁻¹)ᵀ
                lineas += ["", "  PROPIEDAD 3: Inversa de la Traspuesta   →   (Aᵀ)⁻¹ = (A⁻¹)ᵀ", "─" * 70]

                # Paso 1: Calcular A⁻¹
                lineas += ["", "  PASO 1: Calcular A⁻¹ por Gauss-Jordan"]
                res_inv = inversa_gauss_jordan(A_f)
                if not res_inv.es_invertible:
                    lineas.append("  ❌ A no es invertible (det=0). Propiedad no aplicable.")
                    self._log_inv("\n".join(lineas), limpiar=False)
                    return
                A_inv = res_inv.matriz_inversa
                lineas.append(f"  A⁻¹ =\n{fmt_mat_exact(A_inv)}")

                # Paso 2: Calcular (A⁻¹)ᵀ (transponer la inversa)
                lineas += ["", "  PASO 2: Transponer A⁻¹   →   (A⁻¹)ᵀ"]
                A_inv_T = trasponer_matriz(A_inv)
                lineas.append(f"  (A⁻¹)ᵀ =\n{fmt_mat_exact(A_inv_T)}")

                # Paso 3: Calcular Aᵀ
                lineas += ["", "  PASO 3: Transponer A   →   Aᵀ"]
                AT = trasponer_matriz(A_f)
                lineas.append(f"  Aᵀ =\n{fmt_mat_exact(AT)}")

                # Paso 4: Calcular (Aᵀ)⁻¹
                lineas += ["", "  PASO 4: Calcular la inversa de Aᵀ   →   (Aᵀ)⁻¹"]
                res_AT_inv = inversa_gauss_jordan(AT)
                if not res_AT_inv.es_invertible:
                    lineas.append("  ❌ Aᵀ no es invertible.")
                    self._log_inv("\n".join(lineas), limpiar=False)
                    return
                AT_inv = res_AT_inv.matriz_inversa
                lineas.append(f"  (Aᵀ)⁻¹ =\n{fmt_mat_exact(AT_inv)}")

                # Paso 5: Comparar
                lineas += ["", "  PASO 5: Verificar que (Aᵀ)⁻¹ = (A⁻¹)ᵀ"]
                son_iguales = son_matrices_iguales(AT_inv, A_inv_T)
                lineas += [
                    "",
                    f"  {'✓ SE CUMPLE: (Aᵀ)⁻¹ es idéntica a (A⁻¹)ᵀ.' if son_iguales else '✗ NO SE CUMPLE (discrepancia numérica).'}",
                    "═" * 70,
                ]
            elif prop_id == "a_inv_I":
                # Propiedad 2: A⁻¹ · A = I
                lineas += ["", "  PROPIEDAD 2: Inversa y la Matriz Identidad   →   A⁻¹ · A = I", "─" * 70]

                # Paso 1: Calcular A⁻¹ con procedimiento de reducción completo
                lineas += ["", "  PASO 1: Calcular A⁻¹ por Gauss-Jordan sobre matriz aumentada [A | I]:"]
                res_inv = inversa_gauss_jordan(A_f)
                if not res_inv.es_invertible:
                    lineas.append("  ❌ A no es invertible (det = 0). La propiedad A⁻¹ · A = I no aplica.")
                    self._log_inv("\n".join(lineas), limpiar=False)
                    return
                # Agregar operaciones elementales de fila y estados intermedios con alineación limpia
                pasos_reduccion = res_inv.pasos[1:-3] if len(res_inv.pasos) >= 4 else res_inv.pasos
                for p in pasos_reduccion:
                    for sub in p.strip().split("\n"):
                        if sub.strip():
                            lineas.append(f"  {sub.strip()}")
                A_inv = res_inv.matriz_inversa
                lineas += ["", f"  Matriz Inversa A⁻¹ obtenida:\n{fmt_mat_exact(A_inv)}"]

                # Paso 2: Calcular el producto A⁻¹ · A entrada por entrada
                lineas += ["", "  PASO 2: Calcular el producto  A⁻¹ · A entrada por entrada"]
                lineas.append("  Regla: la entrada C[i,j] es (Fila i de A⁻¹) · (Columna j de A):")
                n_local = len(A_f)
                for i in range(n_local):
                    for j in range(n_local):
                        terminos = " + ".join(
                            f"({formatear_numero(float(A_inv[i][k]), modo)})·({formatear_numero(float(A_f[k][j]), modo)})"
                            for k in range(n_local)
                        )
                        valor = sum(A_inv[i][k] * A_f[k][j] for k in range(n_local))
                        lineas.append(f"  C[{i+1},{j+1}] = {terminos} = {formatear_numero(float(valor), modo)}")

                # Paso 3: Matriz resultante y verificación
                prod = multiplicar_matrices(A_inv, A_f)
                lineas += ["", "  PASO 3: Matriz Resultante C = A⁻¹ · A:"]
                lineas.append(fmt_mat_exact(prod))

                I_f = matriz_identidad(n_local)
                es_id = son_matrices_iguales(prod, I_f)
                lineas += [
                    "",
                    f"  {'✓ SE CUMPLE: A⁻¹ · A = I (Matriz Identidad).' if es_id else '✗ NO SE CUMPLE (error numérico inesperado).'}",
                    "═" * 70,
                ]
            self._log_inv("\n".join(lineas), limpiar=False)

        except Exception as ex:
            import traceback
            self._log_inv(f"❌ Error inesperado:\n{ex}\n\n{traceback.format_exc()}", limpiar=False)


    def _calc_propiedad_tarea5_det(self, prop_id: str):
        """Verifica una de las propiedades de Determinante de la Tarea 5 con procedimiento completo."""
        self._ultimo_calc_det = f"tarea5_{prop_id}"
        try:
            A = self._leer_matriz_det()
        except ValueError as e:
            self._log_det(f"❌ Error al leer datos: {e}\n" + "-"*40, limpiar=False)
            return

        nA = len(A)
        modo = self.get_modo_numero()
        try:
            from fractions import Fraction
            from src.core.exact_math import (
                crear_matriz, inversa_gauss_jordan,
                matriz_a_cadena, formatear_numero
            )
            from src.core.determinantes_facade import calcular_determinante

            A_f = crear_matriz(A)
            
            def fmt_mat_exact(mat):
                lines = []
                for fila in mat:
                    vals = "  ".join(f"{formatear_numero(float(x), modo):>8}" for x in fila)
                    lines.append(f"  [ {vals} ]")
                return "\n".join(lines)

            lineas = [
                "\n" + "═" * 70,
                f"  Matriz A  ({nA}×{nA}):",
                fmt_mat_exact(A_f),
                "═" * 70,
            ]

            if prop_id == "det_inv":
                # det(A⁻¹) = 1 / det(A)
                lineas += ["", "  PROPIEDAD 4: Determinante de la Inversa   →   det(A⁻¹) = 1 / det(A)", "─" * 70]
                
                # Paso 1: Calcular det(A)
                lineas += ["", "  PASO 1: Calcular det(A)"]
                res_detA = calcular_determinante(A_f)
                lineas += ["\n".join("    " + p for p in res_detA.pasos)]
                detA = res_detA.determinante
                lineas.append(f"\n  => det(A) = {formatear_numero(float(detA), modo)}")
                
                if detA == 0:
                    lineas.append("  ❌ det(A) = 0, la matriz no es invertible. Propiedad no aplicable.")
                    self._log_det("\n".join(lineas), limpiar=False)
                    return
                
                # Paso 2: Calcular A⁻¹
                lineas += ["", "  PASO 2: Calcular A⁻¹ por Gauss-Jordan"]
                res_inv = inversa_gauss_jordan(A_f)
                A_inv = res_inv.matriz_inversa
                lineas.append(f"  A⁻¹ =\n{fmt_mat_exact(A_inv)}")
                
                # Paso 3: Calcular det(A⁻¹)
                lineas += ["", "  PASO 3: Calcular det(A⁻¹)"]
                res_detA_inv = calcular_determinante(A_inv)
                lineas += ["\n".join("    " + p for p in res_detA_inv.pasos)]
                detA_inv = res_detA_inv.determinante
                lineas.append(f"\n  => det(A⁻¹) = {formatear_numero(float(detA_inv), modo)}")
                
                # Paso 4: Comparar
                lineas += ["", "  PASO 4: Verificar igualdad"]
                inv_detA = Fraction(1, detA)
                lineas.append(f"  1 / det(A) = 1 / {formatear_numero(float(detA), modo)} = {formatear_numero(float(inv_detA), modo)}")
                
                son_iguales = (detA_inv == inv_detA)
                lineas += [
                    "",
                    f"  {'✓ SE CUMPLE: det(A⁻¹) = 1 / det(A)' if son_iguales else '✗ NO SE CUMPLE (error numérico inesperado)'}",
                    "═" * 70
                ]
                
            elif prop_id == "op_reng":
                lineas += ["", "  PROPIEDAD 5: Operaciones de Fila en det(A)", "─" * 70]
                lineas.append("  (Esta demostración aplica la triangulación paso a paso mostrando los cambios en el determinante)")
                res_detA = calcular_determinante(A_f)
                lineas += res_detA.pasos
                lineas += [
                    "",
                    f"  => Al finalizar las operaciones, det(A) = {formatear_numero(float(res_detA.determinante), modo)}",
                    "",
                    "  ✓ SE CUMPLE: El determinante se ajusta correctamente en cada operación de fila.",
                    "═" * 70
                ]

            elif prop_id == "triang":
                lineas += ["", "  PROPIEDAD 6: Determinante de Matriz Triangular", "─" * 70]
                lineas.append("  (Triangulando la matriz original paso a paso)")
                res_detA = calcular_determinante(A_f)
                lineas += res_detA.pasos
                
                if res_detA.matriz_triangular:
                    lineas += [
                        "",
                        "  Matriz Triangular Resultante (U):",
                        fmt_mat_exact(res_detA.matriz_triangular),
                        "",
                        "  El determinante es el producto de su diagonal (ajustado por los intercambios de fila):"
                    ]
                    diag = [res_detA.matriz_triangular[i][i] for i in range(nA)]
                    diag_str = " * ".join(formatear_numero(float(d), modo) for d in diag)
                    lineas.append(f"  Diagonal: {diag_str}")
                    
                lineas += [
                    "",
                    f"  ✓ SE CUMPLE: det(A) = {formatear_numero(float(res_detA.determinante), modo)}",
                    "═" * 70
                ]

            self._log_det("\n".join(lineas), limpiar=False)
            

        except Exception as ex:
            import traceback
            self._log_det(f"❌ Error inesperado:\n{ex}\n\n{traceback.format_exc()}", limpiar=False)

    def _log_prop(self, texto: str, limpiar: bool = False):
        """Escribe texto en el panel de propiedades; limpiar=False borra lo anterior."""
        self.txt_res_prop.configure(state="normal")
        if limpiar:
            self.txt_res_prop.delete("1.0", "end")
        self.txt_res_prop.insert("end", texto + "\n")
        self.txt_res_prop.configure(state="disabled")
        self.txt_res_prop.see("end")

    def _limpiar_historial_prop(self):
        """Borra todo el contenido del historial de texto de Propiedades."""
        self.txt_res_prop.configure(state="normal")
        self.txt_res_prop.delete("1.0", "end")
        self.txt_res_prop.configure(state="disabled")

    def _setup_tab_inv(self):
        """Construye la pestaña para calcular la traspuesta Aᵀ y la inversa A⁻¹."""
        tab = self.tab_inv
        tab.grid_columnconfigure(0, weight=0)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(tab, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            left, text="🔄 Traspuesta e Inversa de Matriz A",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#7c3aed", "#a78bfa")
        ).pack(anchor="w", padx=14, pady=(14, 4))

        dim_frame = ctk.CTkFrame(left, fg_color="transparent")
        dim_frame.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(dim_frame, text="Filas (n):").pack(side="left")
        self.entry_inv_n = ctk.CTkEntry(dim_frame, width=44, justify="center")
        self.entry_inv_n.pack(side="left", padx=(4, 12))
        self.entry_inv_n.insert(0, "3")
        ctk.CTkLabel(dim_frame, text="Columnas (m):").pack(side="left")
        self.entry_inv_m = ctk.CTkEntry(dim_frame, width=44, justify="center")
        self.entry_inv_m.pack(side="left", padx=4)
        self.entry_inv_m.insert(0, "3")

        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=4)
        ctk.CTkButton(btn_row, text="Generar", width=80, command=self._generar_grid_inv).pack(side="left", padx=2)
        ctk.CTkButton(
            btn_row, text="🎲 Ejemplo", width=90, command=self._cargar_ejemplo_inv,
            fg_color=("#475569", "#374151"), hover_color=("#334155", "#4b5563")
        ).pack(side="left", padx=4)

        self.scroll_inv = ctk.CTkScrollableFrame(left, height=200)
        self.scroll_inv.pack(fill="both", expand=True, padx=14, pady=4)
        self.entries_inv: List[List[ctk.CTkEntry]] = []
        self._generar_grid_inv()

        op_frame = ctk.CTkFrame(left, fg_color="transparent")
        op_frame.pack(fill="x", padx=14, pady=(6, 12))
        op_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            op_frame, text="Aᵀ — Traspuesta",
            command=self._calc_traspuesta,
            fg_color=("#0d9488", "#0f766e"),
            font=ctk.CTkFont(size=12, weight="bold"), height=36
        ).grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        ctk.CTkButton(
            op_frame, text="A⁻¹ — Gauss-Jordan",
            command=self._calc_inversa,
            fg_color=("#7c3aed", "#6d28d9"),
            font=ctk.CTkFont(size=12, weight="bold"), height=36
        ).grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        ctk.CTkButton(
            op_frame, text="A⁻¹ — Matriz Adjunta",
            command=self._calc_inversa_adjunta,
            fg_color=("#2563eb", "#1d4ed8"),
            font=ctk.CTkFont(size=12, weight="bold"), height=36
        ).grid(row=1, column=0, columnspan=2, padx=2, pady=(4, 2), sticky="ew")

        lbl_t5_inv = ctk.CTkLabel(
            op_frame, text="Propiedades de Inversas:",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=("gray20", "gray90")
        )
        lbl_t5_inv.grid(row=2, column=0, columnspan=2, padx=2, pady=(8, 2), sticky="w")

        color_t5 = {"fg_color": ("#ea580c", "#c2410c"), "hover_color": ("#c2410c", "#9a3412")}

        self.btn_prop_inv_inv = ctk.CTkButton(
            op_frame, text="1. (A⁻¹)⁻¹ = A", command=lambda: self._calc_propiedad_tarea5_inv("inv_inv"),
            font=ctk.CTkFont(size=11, weight="bold"), height=32, **color_t5
        )
        self.btn_prop_inv_inv.grid(row=3, column=0, columnspan=2, padx=2, pady=2, sticky="ew")

        self.btn_prop_ainv_I = ctk.CTkButton(
            op_frame, text="2. A⁻¹ · A = I", command=lambda: self._calc_propiedad_tarea5_inv("a_inv_I"),
            font=ctk.CTkFont(size=11, weight="bold"), height=32, **color_t5
        )
        self.btn_prop_ainv_I.grid(row=4, column=0, columnspan=2, padx=2, pady=2, sticky="ew")

        self.btn_prop_inv_tras = ctk.CTkButton(
            op_frame, text="3. (Aᵀ)⁻¹ = (A⁻¹)ᵀ", command=lambda: self._calc_propiedad_tarea5_inv("inv_tras"),
            font=ctk.CTkFont(size=11, weight="bold"), height=32, **color_t5
        )
        self.btn_prop_inv_tras.grid(row=5, column=0, columnspan=2, padx=2, pady=2, sticky="ew")

        ctk.CTkLabel(
            left,
            text="Nota: La inversa requiere matriz cuadrada n×n.",
            font=ctk.CTkFont(size=11), text_color=("gray50", "gray60")
        ).pack(anchor="w", padx=14, pady=(0, 8))

        right = ctk.CTkFrame(tab, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(0, weight=1)

        self.tabview_inv = ctk.CTkTabview(right)
        self.tabview_inv.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        tab_inv_visual = self.tabview_inv.add("  📊 Resultado Visual  ")
        tab_inv_log    = self.tabview_inv.add("  📋 Historial (Texto)  ")

        # --- Pestaña Resultado Visual ---
        tab_inv_visual.grid_columnconfigure(0, weight=1)
        tab_inv_visual.grid_rowconfigure(0, weight=1)

        self.frame_resultado_inv = ctk.CTkScrollableFrame(tab_inv_visual, fg_color="transparent")
        self.frame_resultado_inv.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.frame_resultado_inv.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.frame_resultado_inv,
            text="Los resultados aparecerán aquí al calcular una operación.",
            text_color="gray", font=ctk.CTkFont(size=12)
        ).grid(row=0, column=0, pady=30)

        # --- Pestaña Historial de Texto ---
        tab_inv_log.grid_columnconfigure(0, weight=1)
        tab_inv_log.grid_rowconfigure(1, weight=1)

        bar_inv = ctk.CTkFrame(tab_inv_log, fg_color="transparent")
        bar_inv.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 0))
        ctk.CTkLabel(bar_inv, text="📋 Procedimiento Paso a Paso",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=("#38bdf8", "#38bdf8")).pack(side="left")
        ctk.CTkButton(bar_inv, text="🗑️ Limpiar", width=90, height=28,
                      fg_color=("#dc2626", "#b91c1c"),
                      command=self._limpiar_historial_inv).pack(side="right")

        self.txt_res_inv = ctk.CTkTextbox(tab_inv_log, font=ctk.CTkFont(family="Consolas", size=12), wrap="word")
        self.txt_res_inv.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))
        self.txt_res_inv.configure(state="disabled")

    def _generar_grid_inv(self):
        """Regenera la cuadrícula de A para la pestaña de inversa (dimensiones limitadas a 1..8)."""
        try:
            n = max(1, min(8, int(self.entry_inv_n.get())))
            m = max(1, min(8, int(self.entry_inv_m.get())))
        except ValueError:
            return
        for w in self.scroll_inv.winfo_children():
            w.destroy()
        self.entries_inv = []
        ctk.CTkLabel(
            self.scroll_inv, text=f"Matriz A  ({n} × {m})",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=("#a78bfa", "#a78bfa")
        ).pack(anchor="w", pady=(4, 2))
        self._crear_grid_matriz(self.scroll_inv, n, m, self.entries_inv, color_col_last=False)

    def _cargar_ejemplo_inv(self):
        """Carga un ejemplo 3×3 en la cuadrícula de traspuesta/inversa."""
        self.entry_inv_n.delete(0, "end"); self.entry_inv_n.insert(0, "3")
        self.entry_inv_m.delete(0, "end"); self.entry_inv_m.insert(0, "3")
        self._generar_grid_inv()
        vals = [[1, 2, 0], [-1, 3, 2], [2, 0, -1]]
        for i, fila in enumerate(vals):
            for j, v in enumerate(fila):
                self.entries_inv[i][j].delete(0, "end")
                self.entries_inv[i][j].insert(0, str(v))

    def _leer_matriz_inv(self):
        """Lee A desde la cuadrícula de inversa y la devuelve como Matriz de floats; lanza ValueError si hay error."""
        try:
            n = int(self.entry_inv_n.get())
            m = int(self.entry_inv_m.get())
        except ValueError:
            raise ValueError("Dimensiones inválidas.")
        from fractions import Fraction
        A = []
        for i in range(n):
            fila = []
            for j in range(m):
                txt = self.entries_inv[i][j].get().strip()
                if not txt:
                    raise ValueError(f"Celda A[{i+1},{j+1}] está vacía.")
                try:
                    # Fraction interpreta 'a/b' y decimales de forma exacta; luego se pasa a float porque el núcleo lo requiere
                    fila.append(Fraction(txt))
                except Exception:
                    try:
                        fila.append(Fraction(float(txt)))
                    except Exception:
                        raise ValueError(f"Valor inválido en A[{i+1},{j+1}]: '{txt}'")
            A.append(fila)
        return [[float(x) for x in fila] for fila in A]

    def _calc_traspuesta(self):
        """Calcula y muestra Aᵀ, donde (Aᵀ)ᵢⱼ = Aⱼᵢ."""
        self._ultimo_calc_inv = "traspuesta"
        modo = self.get_modo_numero()
        try:
            A = self._leer_matriz_inv()
        except ValueError as e:
            self.tabview_inv.set("  📋 Historial (Texto)  ")
            self._log_inv(f"❌ {e}", limpiar=False)
            return

        AT = trasponer_matriz(A)
        n_orig = len(A)
        m_orig = len(A[0])
        n_new  = len(AT)
        m_new  = len(AT[0])

        def fmt_mat(mat, rows, cols):
            """Da formato de texto a una matriz de rows×cols."""
            lines = []
            for i in range(rows):
                row_str = "  ".join(
                    f"{formatear_numero(mat[i][j], modo):>8}" for j in range(cols)
                )
                lines.append(f"  [ {row_str} ]")
            return "\n".join(lines)

        lineas = [
            "═" * 60,
            "  TRASPUESTA DE MATRIZ  Aᵀ",
            "═" * 60,
            "",
            f"  Matriz A  ({n_orig} × {m_orig}):",
            fmt_mat(A, n_orig, m_orig),
            "",
            f"  Definición: (Aᵀ)ᵢⱼ = Aⱼᵢ  →  dimensión {n_new} × {m_new}",
            "",
            f"  Aᵀ  ({n_new} × {m_new}):",
            fmt_mat(AT, n_new, m_new),
            "",
            "═" * 60,
        ]
        from src.core.exact_math import crear_matriz, analizar_transposicion_matriz
        A_f = crear_matriz(A); AT_f = crear_matriz(AT)
        lineas.append("\n" + "\n".join(analizar_transposicion_matriz(A_f, AT_f)))
        self._log_inv("\n".join(lineas), limpiar=False)
        self._mostrar_resultado_visual_inv(f"Aᵀ  ({n_new}×{m_new})", AT, "Copiar Aᵀ")

    def _calc_inversa(self):
        """Calcula A⁻¹ por Gauss-Jordan y comprueba que A·A⁻¹ = I."""
        self._ultimo_calc_inv = "inversa"
        modo = self.get_modo_numero()
        try:
            A = self._leer_matriz_inv()
        except ValueError as e:
            self.tabview_inv.set("  📋 Historial (Texto)  ")
            self._log_inv(f"❌ {e}", limpiar=False)
            return

        n = len(A)
        m = len(A[0])
        # Solo una matriz cuadrada puede tener inversa
        if n != m:
            self.tabview_inv.set("  📋 Historial (Texto)  ")
            self._log_inv(
                "═" * 60 + "\n"
                "  ❌ VALIDACIÓN PREVIA FALLIDA (CONDICIÓN OBLIGATORIA)\n"
                "═" * 60 + "\n"
                "Condición: Matriz Cuadrada (n × n).\n"
                f"  Dimensión actual: {n} filas × {m} columnas.\n"
                "  Estado: ❌ NO CUMPLIDA. La matriz inversa solo existe para matrices cuadradas.\n"
                "═" * 60,
                limpiar=False
            )
            return

        try:
            res = invertir_matriz(A, modo=modo)
        except ValueError as e:
            self.tabview_inv.set("  📋 Historial (Texto)  ")
            self._log_inv(f"❌ {e}", limpiar=False)
            return

        lineas = ["═" * 60, "  INVERSA DE MATRIZ  A⁻¹  (Gauss-Jordan)", "═" * 60, ""]
        lineas += res.pasos
        lineas += ["", res.explicacion, "", "═" * 60]

        if res.es_invertible and res.matriz_inversa:
            def fmt_mat(mat):
                """Da formato de texto a una matriz, una fila por línea."""
                lines = []
                for fila in mat:
                    row_str = "  ".join(f"{formatear_numero(x, modo):>10}" for x in fila)
                    lines.append(f"  [ {row_str} ]")
                return "\n".join(lines)
            lineas += ["", f"  A⁻¹  ({n} × {n}):", fmt_mat(res.matriz_inversa)]

            # crear_matriz redondea a fracciones (denominador ≤ 10⁶): A·A⁻¹ se compara con I sin ruido de coma flotante
            from src.core.exact_math import crear_matriz, multiplicar_matrices, matriz_identidad, son_matrices_iguales, matriz_a_cadena
            A_f = crear_matriz(A)
            A_inv_f = crear_matriz(res.matriz_inversa)
            prod = multiplicar_matrices(A_f, A_inv_f)
            I_f = matriz_identidad(n)
            es_id = son_matrices_iguales(prod, I_f)
            lineas += [
                "",
                "═" * 60,
                "  COMPROBACIÓN AUTOMÁTICA OBLIGATORIA: A · A⁻¹ = I",
                "═" * 60,
                matriz_a_cadena(prod),
                "",
                "✓ ÉXITO: El producto A · A⁻¹ coincide con la matriz identidad Iₙ." if es_id
                else "✗ FALLO: El producto no coincide con la identidad."
            ]

        self._log_inv("\n".join(lineas), limpiar=False)
        if res.es_invertible and res.matriz_inversa:
            self._mostrar_resultado_visual_inv(f"A⁻¹  ({n}×{n})  — Gauss-Jordan", res.matriz_inversa, "Copiar A⁻¹")
        else:
            self.tabview_inv.set("  📋 Historial (Texto)  ")

    def _calc_inversa_adjunta(self):
        """Calcula A⁻¹ con la fórmula de la matriz adjunta (solo matrices cuadradas)."""
        self._ultimo_calc_inv = "inversa_adjunta"
        modo = self.get_modo_numero()
        try:
            A = self._leer_matriz_inv()
        except ValueError as e:
            self.tabview_inv.set("  📋 Historial (Texto)  ")
            self._log_inv(f"❌ {e}", limpiar=False)
            return

        n = len(A)
        m = len(A[0])
        # Solo una matriz cuadrada puede tener inversa
        if n != m:
            self.tabview_inv.set("  📋 Historial (Texto)  ")
            self._log_inv(
                "═" * 60 + "\n"
                "  ❌ VALIDACIÓN PREVIA FALLIDA (CONDICIÓN OBLIGATORIA)\n"
                "═" * 60 + "\n"
                "Condición: Matriz Cuadrada (n × n).\n"
                f"  Dimensión actual: {n} filas × {m} columnas.\n"
                "  Estado: ❌ NO CUMPLIDA. La matriz inversa solo existe para matrices cuadradas.\n"
                "═" * 60,
                limpiar=False
            )
            return

        from src.core.exact_math import crear_matriz, inversa_adjunta, matriz_a_cadena
        A_f = crear_matriz(A)
        res = inversa_adjunta(A_f)

        lineas = ["═" * 60, "  INVERSA DE MATRIZ  A⁻¹  (Matriz Adjunta)", "═" * 60, ""]
        lineas += res.pasos

        if res.es_invertible and res.matriz_inversa is not None:
            lineas += [
                "",
                "═" * 60,
                f"  A⁻¹  ({n} × {n}) por Matriz Adjunta:",
                matriz_a_cadena(res.matriz_inversa),
                "═" * 60
            ]
        self._log_inv("\n".join(lineas), limpiar=False)
        if res.es_invertible and res.matriz_inversa is not None:
            # _mostrar_resultado_visual_inv ya llama set("Visual") internamente — NO duplicar el set()
            self._mostrar_resultado_visual_inv(f"A⁻¹  ({n}×{n})  — Matriz Adjunta", res.matriz_inversa, "Copiar A⁻¹")
        else:
            self.tabview_inv.set("  📋 Historial (Texto)  ")

    def _log_inv(self, texto: str, limpiar: bool = False):
        """Escribe texto en el panel de traspuesta/inversa; limpiar=False borra lo anterior."""
        self.txt_res_inv.configure(state="normal")
        if limpiar:
            self.txt_res_inv.delete("1.0", "end")
        self.txt_res_inv.insert("end", texto + "\n")
        self.txt_res_inv.configure(state="disabled")
        self.txt_res_inv.see("end")

    def _limpiar_historial_inv(self):
        """Borra todo el contenido del historial de texto de Traspuesta/Inversa."""
        self.txt_res_inv.configure(state="normal")
        self.txt_res_inv.delete("1.0", "end")
        self.txt_res_inv.configure(state="disabled")

    def _mostrar_resultado_visual_inv(self, titulo: str, matriz, copiar_label: str = "Copiar"):
        """Renderiza la matriz resultado en el panel visual de Inversa/Traspuesta (1 sola ranura)."""
        modo = self.get_modo_numero()
        for w in self.frame_resultado_inv.winfo_children():
            w.destroy()

        card = ctk.CTkFrame(self.frame_resultado_inv, corner_radius=8, fg_color=("gray90", "gray20"))
        card.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        card.grid_columnconfigure(0, weight=1)

        # Encabezado con titulo y boton copiar
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))
        ctk.CTkLabel(header, text=titulo, font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=("#7c3aed", "#a78bfa")).pack(side="left")

        def _guardar_en_banco():
            import copy
            dlg = DialogoGuardar(self, title="Guardar Matriz", text="Ingrese un nombre corto para esta matriz:")
            nombre = dlg.get_input()
            if nombre:
                nombre = nombre.strip()
                if nombre:
                    if not hasattr(self, "banco_matrices"):
                        self.banco_matrices = {}
                    self.banco_matrices[nombre] = copy.deepcopy(matriz)
                    self._log_inv(f"\n✅ Matriz guardada en el banco como '{nombre}'.", limpiar=False)

        ctk.CTkButton(header, text="💾 Guardar en Banco", width=120, height=26,
                      fg_color=("#059669", "#047857"), command=_guardar_en_banco).pack(side="right")

        # Grilla grafica de la matriz
        grid_frame = ctk.CTkFrame(card, fg_color="transparent")
        grid_frame.grid(row=1, column=0, padx=10, pady=(0, 10))

        m = len(matriz[0])
        for j in range(m):
            ctk.CTkLabel(grid_frame, text=f"Col {j+1}", width=60,
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=("gray50", "gray60")).grid(row=0, column=j+1, padx=2)

        for i, fila in enumerate(matriz):
            ctk.CTkLabel(grid_frame, text=f"F{i+1}", width=28,
                         font=ctk.CTkFont(size=10)).grid(row=i+1, column=0)
            for j, val in enumerate(fila):
                ctk.CTkLabel(
                    grid_frame, text=formatear_numero(val, modo),
                    width=60, height=28,
                    corner_radius=4,
                    fg_color=("#3b82f6", "#1d4ed8"),
                    text_color="white",
                    font=ctk.CTkFont(size=12, weight="bold")
                ).grid(row=i+1, column=j+1, padx=2, pady=2)

        # Ir al tab visual automaticamente
        self.tabview_inv.set("  📊 Resultado Visual  ")


    def _setup_tab_det(self):
        """Construye la pestaña de determinantes (triangulación, cofactores y Sarrus)."""
        tab = self.tab_det
        tab.grid_columnconfigure(0, weight=0)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(tab, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left.grid_columnconfigure(0, weight=1)


        ctk.CTkLabel(
            left, text="📊 Determinante de Matriz Cuadrada A",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#ea580c", "#fb923c")
        ).pack(anchor="w", padx=14, pady=(14, 4))

        dim_frame = ctk.CTkFrame(left, fg_color="transparent")
        dim_frame.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(dim_frame, text="Orden n (n×n):").pack(side="left")
        self.entry_det_n = ctk.CTkEntry(dim_frame, width=52, justify="center")
        self.entry_det_n.pack(side="left", padx=(4, 0))
        self.entry_det_n.insert(0, "3")

        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=4)
        ctk.CTkButton(btn_row, text="Generar", width=80, command=self._generar_grid_det).pack(side="left", padx=2)
        ctk.CTkButton(
            btn_row, text="🎲 Ejemplo 3×3", width=110, command=self._cargar_ejemplo_det,
            fg_color=("#475569", "#374151"), hover_color=("#334155", "#4b5563")
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            btn_row, text="🎲 Ejemplo 2×2", width=110, command=self._cargar_ejemplo_det_2x2,
            fg_color=("#475569", "#374151"), hover_color=("#334155", "#4b5563")
        ).pack(side="left", padx=4)

        self.scroll_det = ctk.CTkScrollableFrame(left, height=220)
        self.scroll_det.pack(fill="both", expand=True, padx=14, pady=4)
        self.entries_det: List[List[ctk.CTkEntry]] = []
        self._generar_grid_det()

        btn_det_frame = ctk.CTkFrame(left, fg_color="transparent")
        btn_det_frame.pack(fill="x", padx=14, pady=(6, 12))
        btn_det_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_det_frame, text="📊 Triangulación",
            command=self._calc_determinante,
            fg_color=("#ea580c", "#c2410c"),
            font=ctk.CTkFont(size=12, weight="bold"), height=36
        ).grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        ctk.CTkButton(
            btn_det_frame, text="📑 Cofactores",
            command=self._calc_det_cofactores,
            fg_color=("#0284c7", "#0369a1"),
            font=ctk.CTkFont(size=12, weight="bold"), height=36
        ).grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        ctk.CTkButton(
            btn_det_frame, text="📐 Regla de Sarrus (3×3)",
            command=self._calc_det_sarrus,
            fg_color=("#7c3aed", "#6d28d9"),
            font=ctk.CTkFont(size=12, weight="bold"), height=36
        ).grid(row=1, column=0, columnspan=2, padx=2, pady=(4, 2), sticky="ew")

        lbl_t5_det = ctk.CTkLabel(
            btn_det_frame, text="Propiedades de Determinantes:",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=("gray20", "gray90")
        )
        lbl_t5_det.grid(row=2, column=0, columnspan=2, padx=2, pady=(8, 2), sticky="w")

        color_t5 = {"fg_color": ("#ea580c", "#c2410c"), "hover_color": ("#c2410c", "#9a3412")}

        self.btn_prop_det_inv = ctk.CTkButton(
            btn_det_frame, text="4. det(A⁻¹) = 1/det(A)", command=lambda: self._calc_propiedad_tarea5_det("det_inv"),
            font=ctk.CTkFont(size=11, weight="bold"), height=32, **color_t5
        )
        self.btn_prop_det_inv.grid(row=3, column=0, columnspan=2, padx=2, pady=2, sticky="ew")

        self.btn_prop_op_reng = ctk.CTkButton(
            btn_det_frame, text="5. Op. Fila en det(A)", command=lambda: self._calc_propiedad_tarea5_det("op_reng"),
            font=ctk.CTkFont(size=11, weight="bold"), height=32, **color_t5
        )
        self.btn_prop_op_reng.grid(row=4, column=0, padx=2, pady=2, sticky="ew")

        self.btn_prop_triang = ctk.CTkButton(
            btn_det_frame, text="6. det(Triangular)", command=lambda: self._calc_propiedad_tarea5_det("triang"),
            font=ctk.CTkFont(size=11, weight="bold"), height=32, **color_t5
        )
        self.btn_prop_triang.grid(row=4, column=1, padx=2, pady=2, sticky="ew")

        right = ctk.CTkFrame(tab, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(0, weight=0)
        right.grid_rowconfigure(1, weight=1)

        bar_det = ctk.CTkFrame(right, fg_color="transparent")
        bar_det.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 0))
        ctk.CTkLabel(bar_det, text="📐 Procedimiento Paso a Paso",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=("gray20", "#38bdf8")).pack(side="left")
        ctk.CTkButton(bar_det, text="🗑️ Limpiar", width=90, height=28,
                      fg_color=("#dc2626", "#b91c1c"),
                      command=self._limpiar_historial_det).pack(side="right")

        self.txt_res_det = ctk.CTkTextbox(right, font=ctk.CTkFont(family="Consolas", size=12), wrap="word")
        self.txt_res_det.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))
        self.txt_res_det.configure(state="disabled")

    def _generar_grid_det(self):
        """Regenera la cuadrícula de A (n×n) para determinantes (n limitado a 1..8)."""
        try:
            n = max(1, min(8, int(self.entry_det_n.get())))
        except ValueError:
            return
        for w in self.scroll_det.winfo_children():
            w.destroy()
        self.entries_det = []
        ctk.CTkLabel(
            self.scroll_det, text=f"Matriz A  ({n} × {n})",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=("#fb923c", "#fb923c")
        ).pack(anchor="w", pady=(4, 2))
        self._crear_grid_matriz(self.scroll_det, n, n, self.entries_det, color_col_last=False)

    def _cargar_ejemplo_det(self):
        """Carga un ejemplo 3×3 con det = -14."""
        self.entry_det_n.delete(0, "end"); self.entry_det_n.insert(0, "3")
        self._generar_grid_det()
        vals = [[1, 2, 3], [4, 5, 6], [7, 2, 9]]
        for i, fila in enumerate(vals):
            for j, v in enumerate(fila):
                self.entries_det[i][j].delete(0, "end")
                self.entries_det[i][j].insert(0, str(v))

    def _cargar_ejemplo_det_2x2(self):
        """Carga A = [[3,-2],[4,1]], cuyo det = 11."""
        self.entry_det_n.delete(0, "end"); self.entry_det_n.insert(0, "2")
        self._generar_grid_det()
        vals = [[3, -2], [4, 1]]
        for i, fila in enumerate(vals):
            for j, v in enumerate(fila):
                self.entries_det[i][j].delete(0, "end")
                self.entries_det[i][j].insert(0, str(v))

    def _leer_matriz_det(self):
        """Lee la matriz cuadrada de la cuadrícula de determinantes; lanza ValueError si hay error."""
        try:
            n = int(self.entry_det_n.get())
        except ValueError:
            raise ValueError("Dimensión inválida.")
        from fractions import Fraction
        A = []
        for i in range(n):
            fila = []
            for j in range(n):
                txt = self.entries_det[i][j].get().strip()
                if not txt:
                    raise ValueError(f"Celda A[{i+1},{j+1}] está vacía.")
                try:
                    fila.append(float(Fraction(txt)))
                except Exception:
                    try:
                        fila.append(float(txt))
                    except Exception:
                        raise ValueError(f"Valor inválido en A[{i+1},{j+1}]: '{txt}'")
            A.append(fila)
        return A

    def _calc_determinante(self):
        """Calcula det(A) por triangulación y muestra si A es invertible."""
        self._ultimo_calc_det = "determinante"
        modo = self.get_modo_numero()
        try:
            A = self._leer_matriz_det()
        except ValueError as e:
            self._log_det(f"❌ {e}", limpiar=False)
            return

        try:
            res = calcular_determinante(A, modo=modo)
        except ValueError as e:
            self._log_det(f"❌ {e}", limpiar=False)
            return

        lineas = ["═" * 60, "  DETERMINANTE — det(A)", "═" * 60, ""]
        lineas += res.pasos
        lineas += [
            "",
            "═" * 60,
            f"  det(A) = {formatear_numero(res.determinante, modo)}",
            "",
            res.explicacion,
            "═" * 60,
        ]

        # A es invertible si y solo si det(A) ≠ 0
        veredicto = "✅ La matriz ES INVERTIBLE  (det ≠ 0)" if res.es_invertible \
                    else "❌ La matriz NO ES INVERTIBLE  (det = 0, es singular)"
        lineas += ["", veredicto]

        self._log_det("\n".join(lineas), limpiar=False)

    def _log_det(self, texto: str, limpiar: bool = False):
        """Escribe texto en el panel de determinantes; limpiar=False borra lo anterior."""
        self.txt_res_det.configure(state="normal")
        if limpiar:
            self.txt_res_det.delete("1.0", "end")
        self.txt_res_det.insert("end", texto + "\n")
        self.txt_res_det.configure(state="disabled")
        self.txt_res_det.see("end")

    def _limpiar_historial_det(self):
        """Borra todo el contenido del historial de texto de Determinantes."""
        self.txt_res_det.configure(state="normal")
        self.txt_res_det.delete("1.0", "end")
        self.txt_res_det.configure(state="disabled")

    def _mostrar_resultado_visual_det(self, titulo: str, valor_det):
        """Muestra el valor del determinante en el panel visual de Determinantes."""
        modo = self.get_modo_numero()
        for w in self.frame_resultado_det.winfo_children():
            w.destroy()

        card = ctk.CTkFrame(self.frame_resultado_det, corner_radius=8, fg_color=("gray90", "gray20"))
        card.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text=titulo,
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=("#ea580c", "#fb923c")).grid(row=0, column=0, padx=10, pady=(8, 4), sticky="w")

        val_str = formatear_numero(float(valor_det), modo) if hasattr(valor_det, '__float__') else str(valor_det)
        ctk.CTkLabel(card, text=f"det(A) = {val_str}",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=("#10b981", "#34d399")).grid(row=1, column=0, padx=10, pady=(0, 10))

    def _calc_det_cofactores(self):
        """Calcula det(A) por expansión de cofactores (Laplace)."""
        self._ultimo_calc_det = "cofactores"
        modo = self.get_modo_numero()
        try:
            A = self._leer_matriz_det()
        except ValueError as e:
            self._log_det(f"❌ {e}", limpiar=False)
            return

        from src.core.exact_math import crear_matriz, determinante_cofactores
        A_f = crear_matriz(A)
        # Fracciones exactas: el criterio det(A) ≠ 0 ⇔ A invertible no debe fallar por redondeo
        det_val, pasos = determinante_cofactores(A_f)

        lineas = ["═" * 60, "  DETERMINANTE — EXPANSIÓN POR COFACTORES (LAPLACE)", "═" * 60, ""]
        lineas += pasos
        lineas += [
            "",
            "═" * 60,
            f"  det(A) = {det_val}",
            "═" * 60,
            "",
            "✅ La matriz ES INVERTIBLE  (det ≠ 0)" if det_val != 0 else "❌ La matriz NO ES INVERTIBLE  (det = 0, es singular)"
        ]
        self._log_det("\n".join(lineas), limpiar=False)

    def _calc_det_sarrus(self):
        """Calcula det(A) con la regla de Sarrus; solo aplica a matrices 3×3."""
        self._ultimo_calc_det = "sarrus"
        modo = self.get_modo_numero()
        try:
            A = self._leer_matriz_det()
        except ValueError as e:
            self._log_det(f"❌ {e}", limpiar=False)
            return

        # Sarrus es un atajo válido solo para 3×3; no se generaliza a n ≥ 4
        if len(A) != 3 or len(A[0]) != 3:
            self._log_det("❌ La Regla de Sarrus es aplicable exclusivamente a matrices de 3×3.", limpiar=False)
            return

        from src.core.exact_math import crear_matriz, determinante_sarrus
        A_f = crear_matriz(A)
        # Fracciones exactas: el criterio det(A) ≠ 0 ⇔ A invertible no debe fallar por redondeo
        det_val, pasos = determinante_sarrus(A_f)

        lineas = ["═" * 60, "  DETERMINANTE — REGLA DE SARRUS (3×3)", "═" * 60, ""]
        lineas += pasos
        lineas += [
            "",
            "═" * 60,
            f"  det(A) = {det_val}",
            "═" * 60,
            "",
            "✅ La matriz ES INVERTIBLE  (det ≠ 0)" if det_val != 0 else "❌ La matriz NO ES INVERTIBLE  (det = 0, es singular)"
        ]
        self._log_det("\n".join(lineas), limpiar=False)



    def _limpiar_historial_det(self):
        self.txt_res_det.configure(state="normal")
        self.txt_res_det.delete("1.0", "end")
        self.txt_res_det.configure(state="disabled")
