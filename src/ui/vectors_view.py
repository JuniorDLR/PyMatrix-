"""
Módulo de Interfaz Gráfica para Vectores en ℝⁿ (PyMatrix).

Proporciona vistas interactivas para:
1. Operaciones básicas con vectores (u + v, u - v, c·u, producto punto, normas).
2. Evaluación computacional de Combinación Lineal con reducción a RREF.
3. Evaluación de Independencia y Dependencia Lineal con detección de teoremas
   por inspección directa y deducción de relaciones no triviales.
"""

import random
from typing import List, Optional
import customtkinter as ctk

from src.core.vectors import (
    Vector, sumar_vectores, restar_vectores, multiplicar_vector_escalar,
    producto_punto, norma_vector, evaluar_combinacion_lineal,
    evaluar_independencia_lineal, ResultadoCombinacionLineal, ResultadoIndependenciaLineal
)
from src.core.domain import formatear_numero, a_subindice


class VectorsView(ctk.CTkFrame):
    """Panel principal para el módulo de vectores en ℝⁿ."""
    
    def __init__(self, master, get_modo_numero_cb, **kwargs):
        super().__init__(master, **kwargs)
        self.get_modo_numero = get_modo_numero_cb
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._setup_ui()
        
    def _setup_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # 3 Sub-pestañas especializadas
        self.tab_basicas = self.tabview.add("  ➕ Operaciones Básicas  ")
        self.tab_comb = self.tabview.add("  🔗 Combinación Lineal  ")
        self.tab_indep = self.tabview.add("  ⚖️ Independencia Lineal  ")
        
        self._setup_tab_basicas()
        self._setup_tab_comb()
        self._setup_tab_indep()
        
    def refresh_format(self):
        """Refresca las salidas de texto cuando el usuario cambia el formato global (Fracción/Decimal)."""
        pass

    # =========================================================================
    # SUB-PESTAÑA 1: OPERACIONES BÁSICAS
    # =========================================================================
    def _setup_tab_basicas(self):
        tab = self.tab_basicas
        tab.grid_columnconfigure(0, weight=0)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo: Controles y entradas
        left_frame = ctk.CTkFrame(tab, width=420, corner_radius=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left_frame.grid_propagate(False)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Dimensión
        dim_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        dim_frame.pack(fill="x", padx=14, pady=(12, 6))
        
        ctk.CTkLabel(
            dim_frame, text="Dimensión del espacio (n en ℝⁿ):", font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(0, 8))
        
        self.entry_basicas_n = ctk.CTkEntry(dim_frame, width=48, justify="center")
        self.entry_basicas_n.pack(side="left", padx=4)
        self.entry_basicas_n.insert(0, "3")
        
        btn_crear_basicas = ctk.CTkButton(
            dim_frame, text="Generar", width=70, command=self._generar_entradas_basicas
        )
        btn_crear_basicas.pack(side="left", padx=4)
        
        btn_ejemplo_b = ctk.CTkButton(
            dim_frame, text="🎲 Ejemplo", width=75, command=self._cargar_ejemplo_basicas,
            fg_color=("#475569", "#374151"), hover_color=("#334155", "#4b5563")
        )
        btn_ejemplo_b.pack(side="left", padx=4)
        
        # Scrollable frame para los vectores u y v
        self.scroll_basicas = ctk.CTkScrollableFrame(left_frame, height=220)
        self.scroll_basicas.pack(fill="both", expand=True, padx=14, pady=6)
        
        # Escalar c
        esc_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        esc_frame.pack(fill="x", padx=14, pady=6)
        ctk.CTkLabel(esc_frame, text="Escalar (c):", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 6))
        self.entry_escalar = ctk.CTkEntry(esc_frame, width=65, justify="center")
        self.entry_escalar.pack(side="left", padx=4)
        self.entry_escalar.insert(0, "5")
        
        # Botones de Operación
        btn_grid = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_grid.pack(fill="x", padx=14, pady=(8, 12))
        btn_grid.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(btn_grid, text="u + v  (Suma)", command=lambda: self._calc_basica("suma"),
                      fg_color=("#0284c7", "#0369a1")).grid(row=0, column=0, padx=3, pady=3, sticky="ew")
        ctk.CTkButton(btn_grid, text="u - v  (Resta)", command=lambda: self._calc_basica("resta"),
                      fg_color=("#0284c7", "#0369a1")).grid(row=0, column=1, padx=3, pady=3, sticky="ew")
        ctk.CTkButton(btn_grid, text="c · u  (Escalar u)", command=lambda: self._calc_basica("esc_u"),
                      fg_color=("#0d9488", "#0f766e")).grid(row=1, column=0, padx=3, pady=3, sticky="ew")
        ctk.CTkButton(btn_grid, text="c · v  (Escalar v)", command=lambda: self._calc_basica("esc_v"),
                      fg_color=("#0d9488", "#0f766e")).grid(row=1, column=1, padx=3, pady=3, sticky="ew")
        ctk.CTkButton(btn_grid, text="u · v  (Producto Punto)", command=lambda: self._calc_basica("punto"),
                      fg_color=("#7c3aed", "#6d28d9")).grid(row=2, column=0, padx=3, pady=3, sticky="ew")
        ctk.CTkButton(btn_grid, text="||u|| y ||v||  (Normas)", command=lambda: self._calc_basica("normas"),
                      fg_color=("#b45309", "#92400e")).grid(row=2, column=1, padx=3, pady=3, sticky="ew")
        
        # Panel derecho: Registro de resultados
        right_frame = ctk.CTkFrame(tab, corner_radius=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        
        lbl_res_b = ctk.CTkLabel(
            right_frame, text="📋 Procedimiento Algebraico y Resultados",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=("#38bdf8", "#38bdf8")
        )
        lbl_res_b.grid(row=0, column=0, sticky="w", padx=16, pady=(12, 6))
        
        self.txt_res_basicas = ctk.CTkTextbox(right_frame, font=ctk.CTkFont(family="Consolas", size=12), wrap="word")
        self.txt_res_basicas.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.txt_res_basicas.configure(state="disabled")
        
        self.entries_u: List[ctk.CTkEntry] = []
        self.entries_v: List[ctk.CTkEntry] = []
        self._generar_entradas_basicas()

    def _generar_entradas_basicas(self):
        try:
            n = int(self.entry_basicas_n.get().strip())
        except ValueError:
            return
        n = max(1, min(12, n))
        
        for w in self.scroll_basicas.winfo_children():
            w.destroy()
        
        self.entries_u = []
        self.entries_v = []
        
        # Cabecera
        header = ctk.CTkFrame(self.scroll_basicas, fg_color="transparent")
        header.pack(fill="x", pady=2)
        ctk.CTkLabel(header, text="Componente", width=80, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left")
        ctk.CTkLabel(header, text="Vector u", width=120, font=ctk.CTkFont(size=11, weight="bold"), text_color=("#38bdf8", "#38bdf8")).pack(side="left", padx=4)
        ctk.CTkLabel(header, text="Vector v", width=120, font=ctk.CTkFont(size=11, weight="bold"), text_color=("#34d399", "#34d399")).pack(side="left", padx=4)
        
        for i in range(n):
            fila = ctk.CTkFrame(self.scroll_basicas, fg_color="transparent")
            fila.pack(fill="x", pady=2)
            
            ctk.CTkLabel(fila, text=f"Entrada {i+1}:", width=80).pack(side="left")
            eu = ctk.CTkEntry(fila, width=110, justify="center")
            eu.pack(side="left", padx=4)
            eu.insert(0, "0")
            self.entries_u.append(eu)
            
            ev = ctk.CTkEntry(fila, width=110, justify="center")
            ev.pack(side="left", padx=4)
            ev.insert(0, "0")
            self.entries_v.append(ev)

    def _leer_vector_entries(self, entries: List[ctk.CTkEntry]) -> Vector:
        res: Vector = []
        for i, e in enumerate(entries):
            val_str = e.get().strip()
            try:
                # Permite ingresar fracciones como "3/2" o enteros/flotantes
                if "/" in val_str:
                    num, den = val_str.split("/")
                    res.append(float(num) / float(den))
                else:
                    res.append(float(val_str))
            except Exception:
                raise ValueError(f"Valor no numérico '{val_str}' en la componente {i+1}.")
        return res

    def _cargar_ejemplo_basicas(self):
        ejemplos = [
            # Slide 4: u = [1, -2], v = [2, 5], c = 5
            {"n": 2, "u": [1, -2], "v": [2, 5], "c": 5, "desc": "Ejemplo Diapositiva 4 (u=[1, -2], v=[2, 5], c=5)"},
            # Slide 4 Ej 4: u = [1, -2], v = [2, -5], c = -3
            {"n": 2, "u": [1, -2], "v": [2, -5], "c": -3, "desc": "Ejemplo Diapositiva 4 Ej 4 (u=[1, -2], v=[2, -5], c=-3)"},
            # Slide 10: u = [4, -1], v = [-3, 5], c = 3
            {"n": 2, "u": [4, -1], "v": [-3, 5], "c": 3, "desc": "Ejemplo Diapositiva 10 (u=[4, -1], v=[-3, 5])"},
            # Slide 13 Ej 1: u = [-1, 2], v = [-3, -1], c = -2
            {"n": 2, "u": [-1, 2], "v": [-3, -1], "c": -2, "desc": "Diapositiva 13 Ej 1 (u=[-1, 2], v=[-3, -1])"},
            # Slide 23: u = [3, 2, -4], v = [-6, 1, 7], c = 2
            {"n": 3, "u": [3, 2, -4], "v": [-6, 1, 7], "c": 2, "desc": "Diapositiva 23 Ej I (u=[3, 2, -4], v=[-6, 1, 7])"}
        ]
        ej = random.choice(ejemplos)
        self.entry_basicas_n.delete(0, "end")
        self.entry_basicas_n.insert(0, str(ej["n"]))
        self._generar_entradas_basicas()
        
        for i, val in enumerate(ej["u"]):
            self.entries_u[i].delete(0, "end")
            self.entries_u[i].insert(0, str(val))
        for i, val in enumerate(ej["v"]):
            self.entries_v[i].delete(0, "end")
            self.entries_v[i].insert(0, str(val))
        self.entry_escalar.delete(0, "end")
        self.entry_escalar.insert(0, str(ej["c"]))
        
        self._log_basicas(f"🎲 Ejemplo cargado: {ej['desc']}\nPresione cualquiera de los botones de operación.", limpiar=True)

    def _calc_basica(self, op_tipo: str):
        modo = self.get_modo_numero()
        try:
            u = self._leer_vector_entries(self.entries_u)
            v = self._leer_vector_entries(self.entries_v)
            c_str = self.entry_escalar.get().strip()
            c = float(c_str) if "/" not in c_str else (float(c_str.split("/")[0]) / float(c_str.split("/")[1]))
        except ValueError as e:
            self._log_basicas(f"❌ Error de entrada: {e}", limpiar=True)
            return
        
        u_str = "[" + ", ".join([formatear_numero(x, modo) for x in u]) + "]ᵀ"
        v_str = "[" + ", ".join([formatear_numero(x, modo) for x in v]) + "]ᵀ"
        c_fmt = formatear_numero(c, modo)
        
        lineas = []
        lineas.append(f"Vectores en ℝ{a_subindice(len(u))}:")
        lineas.append(f"  u = {u_str}")
        lineas.append(f"  v = {v_str}")
        lineas.append(f"  c = {c_fmt}\n")
        
        if op_tipo == "suma":
            res = sumar_vectores(u, v)
            lineas.append(">> OPERACIÓN: SUMA DE VECTORES (u + v)")
            lineas.append("Regla: (u + v)ᵢ = uᵢ + vᵢ (sumar coordenadas correspondientes)")
            for i in range(len(u)):
                lineas.append(f"  Entrada {i+1}: ({formatear_numero(u[i], modo)}) + ({formatear_numero(v[i], modo)}) = {formatear_numero(res[i], modo)}")
            lineas.append(f"\nResultado: u + v = [{', '.join([formatear_numero(x, modo) for x in res])}]ᵀ")
            
        elif op_tipo == "resta":
            res = restar_vectores(u, v)
            lineas.append(">> OPERACIÓN: RESTA DE VECTORES (u - v)")
            lineas.append("Regla: (u - v)ᵢ = uᵢ - vᵢ (restar coordenadas correspondientes)")
            for i in range(len(u)):
                lineas.append(f"  Entrada {i+1}: ({formatear_numero(u[i], modo)}) - ({formatear_numero(v[i], modo)}) = {formatear_numero(res[i], modo)}")
            lineas.append(f"\nResultado: u - v = [{', '.join([formatear_numero(x, modo) for x in res])}]ᵀ")
            
        elif op_tipo == "esc_u":
            res = multiplicar_vector_escalar(c, u)
            lineas.append(f">> OPERACIÓN: MULTIPLICACIÓN POR ESCALAR (c · u con c = {c_fmt})")
            lineas.append("Regla: (c·u)ᵢ = c · uᵢ (escalar cada coordenada)")
            for i in range(len(u)):
                lineas.append(f"  Entrada {i+1}: {c_fmt} · ({formatear_numero(u[i], modo)}) = {formatear_numero(res[i], modo)}")
            lineas.append(f"\nResultado: {c_fmt}·u = [{', '.join([formatear_numero(x, modo) for x in res])}]ᵀ")
            
        elif op_tipo == "esc_v":
            res = multiplicar_vector_escalar(c, v)
            lineas.append(f">> OPERACIÓN: MULTIPLICACIÓN POR ESCALAR (c · v con c = {c_fmt})")
            lineas.append("Regla: (c·v)ᵢ = c · vᵢ (escalar cada coordenada)")
            for i in range(len(v)):
                lineas.append(f"  Entrada {i+1}: {c_fmt} · ({formatear_numero(v[i], modo)}) = {formatear_numero(res[i], modo)}")
            lineas.append(f"\nResultado: {c_fmt}·v = [{', '.join([formatear_numero(x, modo) for x in res])}]ᵀ")
            
        elif op_tipo == "punto":
            pp = producto_punto(u, v)
            lineas.append(">> OPERACIÓN: PRODUCTO PUNTO (u · v)")
            lineas.append("Regla: u · v = u₁v₁ + u₂v₂ + ... + uₙvₙ")
            term_str = " + ".join([f"({formatear_numero(ui, modo)})·({formatear_numero(vi, modo)})" for ui, vi in zip(u, v)])
            lineas.append(f"  Desarrollo: {term_str}")
            lineas.append(f"\nResultado escalar: u · v = {formatear_numero(pp, modo)}")
            
        elif op_tipo == "normas":
            nu = norma_vector(u)
            nv = norma_vector(v)
            lineas.append(">> OPERACIÓN: NORMAS EUCLIDIANAS (LONGITUD O MAGNITUD)")
            lineas.append("Regla: ||v|| = √(∑ vᵢ²)")
            u_sq_str = " + ".join([f"({formatear_numero(x, modo)})²" for x in u])
            v_sq_str = " + ".join([f"({formatear_numero(x, modo)})²" for x in v])
            lineas.append(f"  ||u|| = √({u_sq_str}) = {nu}")
            lineas.append(f"  ||v|| = √({v_sq_str}) = {nv}")
            
        self._log_basicas("\n".join(lineas), limpiar=True)

    def _log_basicas(self, texto: str, limpiar: bool = False):
        self.txt_res_basicas.configure(state="normal")
        if limpiar:
            self.txt_res_basicas.delete("1.0", "end")
        self.txt_res_basicas.insert("end", texto + "\n")
        self.txt_res_basicas.configure(state="disabled")

    # =========================================================================
    # SUB-PESTAÑA 2: COMBINACIÓN LINEAL
    # =========================================================================
    def _setup_tab_comb(self):
        tab = self.tab_comb
        tab.grid_columnconfigure(0, weight=0)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo
        left = ctk.CTkFrame(tab, width=440, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left.grid_propagate(False)
        left.grid_columnconfigure(0, weight=1)
        
        ctrl_frame = ctk.CTkFrame(left, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=14, pady=(12, 6))
        
        ctk.CTkLabel(ctrl_frame, text="Dimensión (n):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=2)
        self.entry_comb_n = ctk.CTkEntry(ctrl_frame, width=40, justify="center")
        self.entry_comb_n.grid(row=0, column=1, padx=4)
        self.entry_comb_n.insert(0, "3")
        
        ctk.CTkLabel(ctrl_frame, text="Vectores (k):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=2, padx=2)
        self.entry_comb_k = ctk.CTkEntry(ctrl_frame, width=40, justify="center")
        self.entry_comb_k.grid(row=0, column=3, padx=4)
        self.entry_comb_k.insert(0, "2")
        
        ctk.CTkButton(ctrl_frame, text="Generar", width=65, command=self._generar_grid_comb).grid(row=0, column=4, padx=4)
        
        btn_ejemplo_c = ctk.CTkButton(
            ctrl_frame, text="🎲 Ejemplo", width=75, command=self._cargar_ejemplo_comb,
            fg_color=("#475569", "#374151"), hover_color=("#334155", "#4b5563")
        )
        btn_ejemplo_c.grid(row=0, column=5, padx=4)
        
        lbl_info = ctk.CTkLabel(
            left, text="Ingrese los vectores {v₁, ..., vₖ} y el vector objetivo b a evaluar:",
            font=ctk.CTkFont(size=11), text_color=("gray60", "gray70")
        )
        lbl_info.pack(anchor="w", padx=14, pady=(4, 2))
        
        self.scroll_comb = ctk.CTkScrollableFrame(left, height=270)
        self.scroll_comb.pack(fill="both", expand=True, padx=14, pady=6)
        
        btn_eval_comb = ctk.CTkButton(
            left, text="🚀 Evaluar Combinación Lineal", command=self._evaluar_comb,
            fg_color=("#059669", "#10b981"), hover_color=("#047857", "#059669"),
            font=ctk.CTkFont(size=13, weight="bold"), height=36
        )
        btn_eval_comb.pack(fill="x", padx=14, pady=(6, 12))
        
        # Panel derecho: Resultados
        right = ctk.CTkFrame(tab, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)
        
        lbl_res_c = ctk.CTkLabel(
            right, text="🎯 Diagnóstico y Matriz Aumentada [v₁ ... vₖ | b]",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=("#38bdf8", "#38bdf8")
        )
        lbl_res_c.grid(row=0, column=0, sticky="w", padx=16, pady=(12, 6))
        
        self.txt_res_comb = ctk.CTkTextbox(right, font=ctk.CTkFont(family="Consolas", size=12), wrap="word")
        self.txt_res_comb.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.txt_res_comb.configure(state="disabled")

        
        self.grid_entries_comb: List[List[ctk.CTkEntry]] = []
        self._generar_grid_comb()

    def _generar_grid_comb(self):
        try:
            n = int(self.entry_comb_n.get().strip())
            k = int(self.entry_comb_k.get().strip())
        except ValueError:
            return
        n = max(1, min(10, n))
        k = max(1, min(10, k))
        
        for w in self.scroll_comb.winfo_children():
            w.destroy()
        
        self.grid_entries_comb = []
        
        # Cabecera
        header = ctk.CTkFrame(self.scroll_comb, fg_color="transparent")
        header.pack(fill="x", pady=2)
        ctk.CTkLabel(header, text="Fila", width=36).pack(side="left")
        
        for j in range(k):
            ctk.CTkLabel(
                header, text=f"v{a_subindice(j+1)}", width=52,
                font=ctk.CTkFont(size=11, weight="bold"), text_color=("#38bdf8", "#38bdf8")
            ).pack(side="left", padx=2)
            
        ctk.CTkLabel(
            header, text="= b", width=55,
            font=ctk.CTkFont(size=11, weight="bold"), text_color=("#f43f5e", "#f43f5e")
        ).pack(side="left", padx=(6, 2))
        
        # Filas
        for i in range(n):
            row_frame = ctk.CTkFrame(self.scroll_comb, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            ctk.CTkLabel(row_frame, text=f"F{a_subindice(i+1)}", width=36).pack(side="left")
            
            fila_entries = []
            for j in range(k):
                e = ctk.CTkEntry(row_frame, width=52, height=28, justify="center")
                e.pack(side="left", padx=2)
                e.insert(0, "0")
                fila_entries.append(e)
                
            # Entrada para b
            eb = ctk.CTkEntry(
                row_frame, width=55, height=28, justify="center",
                fg_color=("#ffe4e6", "#3f1a24"), text_color=("#be123c", "#fca5a5")
            )
            eb.pack(side="left", padx=(6, 2))
            eb.insert(0, "0")
            fila_entries.append(eb)
            
            self.grid_entries_comb.append(fila_entries)

    def _cargar_ejemplo_comb(self):
        ejemplos = [
            # Slide 11: a1 = [1, -2, -5], a2 = [2, 5, 6], b = [7, 4, -3] -> Combinación Lineal única (c1=3, c2=2)
            {
                "n": 3, "k": 2,
                "vectores": [[1, -2, -5], [2, 5, 6]],
                "b": [7, 4, -3],
                "desc": "Diapositiva 11: a₁=[1, -2, -5], a₂=[2, 5, 6], b=[7, 4, -3] (Solución Única: c₁=3, c₂=2)"
            },
            # Slide 15 Ej 13: A columnas y b = [3, -7, -3]
            {
                "n": 3, "k": 3,
                "vectores": [[1, 0, -2], [-4, 3, 8], [2, 5, -4]],
                "b": [3, -7, -3],
                "desc": "Diapositiva 15 Ej 13: Columnas de A y b=[3, -7, -3]"
            },
            # Slide 16 IV: Minería v1=[30, 600], v2=[40, 380], b=[240, 2824]
            {
                "n": 2, "k": 2,
                "vectores": [[30, 600], [40, 380]],
                "b": [240, 2824],
                "desc": "Diapositiva 16 Ej IV: Problema de Minas (Cobre y Plata)"
            },
            # Ejemplo Inconsistente (Sin solución)
            {
                "n": 3, "k": 2,
                "vectores": [[1, 2, 3], [2, 4, 6]],
                "b": [1, 1, 5],
                "desc": "Ejemplo Inconsistente: b no está en el generado de v₁ y v₂"
            }
        ]
        ej = random.choice(ejemplos)
        self.entry_comb_n.delete(0, "end")
        self.entry_comb_n.insert(0, str(ej["n"]))
        self.entry_comb_k.delete(0, "end")
        self.entry_comb_k.insert(0, str(ej["k"]))
        self._generar_grid_comb()
        
        n, k = ej["n"], ej["k"]
        for i in range(n):
            for j in range(k):
                val = ej["vectores"][j][i]
                self.grid_entries_comb[i][j].delete(0, "end")
                self.grid_entries_comb[i][j].insert(0, str(val))
            val_b = ej["b"][i]
            self.grid_entries_comb[i][k].delete(0, "end")
            self.grid_entries_comb[i][k].insert(0, str(val_b))
            
        self._log_comb(f"🎲 Ejemplo cargado: {ej['desc']}\nPresione 'Evaluar Combinación Lineal'.", limpiar=True)

    def _evaluar_comb(self):
        modo = self.get_modo_numero()
        n = len(self.grid_entries_comb)
        k = len(self.grid_entries_comb[0]) - 1
        
        try:
            vectores: List[Vector] = [[] for _ in range(k)]
            b: Vector = []
            for i in range(n):
                for j in range(k):
                    val_str = self.grid_entries_comb[i][j].get().strip()
                    val = float(val_str) if "/" not in val_str else float(val_str.split("/")[0]) / float(val_str.split("/")[1])
                    vectores[j].append(val)
                val_b_str = self.grid_entries_comb[i][k].get().strip()
                val_b = float(val_b_str) if "/" not in val_b_str else float(val_b_str.split("/")[0]) / float(val_b_str.split("/")[1])
                b.append(val_b)
        except Exception as e:
            self._log_comb(f"❌ Error al leer valores de la cuadrícula: {e}", limpiar=True)
            return
        
        resultado = evaluar_combinacion_lineal(vectores, b, modo=modo)
        
        # Formatear reporte completo
        lineas = []
        lineas.append("==================================================")
        lineas.append("  EVALUACIÓN DE COMBINACIÓN LINEAL EN ℝⁿ")
        lineas.append("==================================================\n")
        
        lineas.append(f"• Conjunto generador de {k} vectores en ℝ{a_subindice(n)}:")
        for j, vec in enumerate(vectores):
            vec_fmt = "[" + ", ".join([formatear_numero(x, modo) for x in vec]) + "]ᵀ"
            lineas.append(f"    v{a_subindice(j+1)} = {vec_fmt}")
        b_fmt = "[" + ", ".join([formatear_numero(x, modo) for x in b]) + "]ᵀ"
        lineas.append(f"• Vector objetivo b = {b_fmt}\n")
        
        lineas.append("--- 1. MATRIZ AUMENTADA INICIAL [v₁ ... vₖ | b] ---")
        lineas.append(self._formatear_matriz(resultado.matriz_aumentada_inicial, modo))
        
        # Proceso de reducción paso a paso
        if resultado.pasos_gauss and len(resultado.pasos_gauss) > 1:
            lineas.append("--- 2. PROCESO DE RESOLUCIÓN PASO A PASO (GAUSS-JORDAN) ---")
            for num_p, paso in enumerate(resultado.pasos_gauss[1:], 1):
                lineas.append(f">> Paso {num_p}: {paso.descripcion}")
                lineas.append(self._formatear_matriz(paso.matriz_estado, modo))
        
        lineas.append("--- 3. MATRIZ EN FORMA ESCALONADA (RREF) ---")
        lineas.append(self._formatear_matriz(resultado.matriz_rref, modo))
        
        lineas.append("--- 4. DIAGNÓSTICO ALGEBRAICO Y CONCLUSIÓN ---")
        if not resultado.es_combinacion:
            # Buscar la fila inconsistente del tipo [0 0 ... 0 | k] con k != 0
            fila_inconsistente = None
            val_k_str = "k"
            mat_final = resultado.matriz_rref
            for idx_f, fila in enumerate(mat_final):
                coefs = fila[:-1]
                ti = fila[-1]
                if all(abs(c) < 1e-10 for c in coefs) and abs(ti) > 1e-10:
                    fila_inconsistente = idx_f + 1
                    val_k_str = formatear_numero(ti, modo)
                    break
            
            lineas.append("🔴 RESULTADO: EL VECTOR b NO ES COMBINACIÓN LINEAL.")
            lineas.append("")
            if fila_inconsistente is not None:
                lineas.append(f"⚠️ DETECCIÓN DE INCONSISTENCIA EN LA FILA {fila_inconsistente}:")
                eq_terms = " + ".join([f"0·c{a_subindice(j+1)}" for j in range(k)])
                lineas.append(f"   Ecuación: {eq_terms} = {val_k_str}")
                lineas.append(f"   Forma reducida: 0 = {val_k_str}  (¡CONTRADICCIÓN MATEMÁTICA!)")
                lineas.append("")
                lineas.append("• ¿Cómo se llega a esta conclusión paso a paso?")
                lineas.append(f"  1. Se planteó la ecuación vectorial c₁v₁ + ... + c{a_subindice(k)}v{a_subindice(k)} = b.")
                lineas.append(f"  2. Se construyó la matriz aumentada [v₁ ... v{a_subindice(k)} | b] y se aplicaron operaciones elementales de fila.")
                lineas.append(f"  3. En la Fila {fila_inconsistente}, todos los coeficientes de los vectores se anularon (sumaron 0), mientras que el término independiente resultó ser {val_k_str} ≠ 0.")
                lineas.append(f"  4. La igualdad '0 = {val_k_str}' es falsa e imposible de satisfacer para cualquier valor real de los escalares cᵢ.")
                lineas.append("")
                lineas.append("• Conclusión Teórica (Teorema de Existencia):")
                lineas.append("  Al ser el sistema lineal inconsistente (sin solución), no existen escalares que permitan formar el vector b.")
                lineas.append(f"  Por lo tanto, el vector b NO pertenece al subespacio generado por los vectores dados (b ∉ Gen{{v₁, ..., v{a_subindice(k)}}}).")
            else:
                lineas.append(resultado.explicacion)
        elif resultado.pesos is not None:
            pesos = resultado.pesos
            terminos_comb = []
            for i, p in enumerate(pesos):
                p_str = formatear_numero(p, modo)
                terminos_comb.append(f"({p_str})·v{a_subindice(i+1)}")
            ecuacion = "b = " + " + ".join(terminos_comb)
            
            lineas.append("🟢 RESULTADO: EL VECTOR b SÍ ES COMBINACIÓN LINEAL ÚNICA.")
            lineas.append("")
            lineas.append("• Ecuación vectorial obtenida:")
            lineas.append(f"  {ecuacion}\n")
            lineas.append("• Valores de los pesos (escalares):")
            for i, p in enumerate(pesos):
                lineas.append(f"  c{a_subindice(i+1)} = {formatear_numero(p, modo)}")
            lineas.append("")
            lineas.append("• Justificación:")
            lineas.append("  Al reducir la matriz a RREF, cada columna de coeficientes tiene un pivote único y no surge ninguna contradicción, garantizando una solución consistente determinada.")
        else:
            lineas.append("🟡 RESULTADO: EL VECTOR b SÍ ES COMBINACIÓN LINEAL (INFINITAS MANERAS).")
            lineas.append("")
            lineas.append(resultado.explicacion)
        
        self._log_comb("\n".join(lineas), limpiar=True)


    def _log_comb(self, texto: str, limpiar: bool = False):
        self.txt_res_comb.configure(state="normal")
        if limpiar:
            self.txt_res_comb.delete("1.0", "end")
        self.txt_res_comb.insert("end", texto + "\n")
        self.txt_res_comb.configure(state="disabled")

    # =========================================================================
    # SUB-PESTAÑA 3: INDEPENDENCIA LINEAL
    # =========================================================================
    def _setup_tab_indep(self):
        tab = self.tab_indep
        tab.grid_columnconfigure(0, weight=0)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo
        left = ctk.CTkFrame(tab, width=440, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left.grid_propagate(False)
        left.grid_columnconfigure(0, weight=1)
        
        ctrl_frame = ctk.CTkFrame(left, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=14, pady=(12, 6))
        
        ctk.CTkLabel(ctrl_frame, text="Dimensión (n):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=2)
        self.entry_indep_n = ctk.CTkEntry(ctrl_frame, width=40, justify="center")
        self.entry_indep_n.grid(row=0, column=1, padx=4)
        self.entry_indep_n.insert(0, "3")
        
        ctk.CTkLabel(ctrl_frame, text="Vectores (k):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=2, padx=2)
        self.entry_indep_k = ctk.CTkEntry(ctrl_frame, width=40, justify="center")
        self.entry_indep_k.grid(row=0, column=3, padx=4)
        self.entry_indep_k.insert(0, "3")
        
        ctk.CTkButton(ctrl_frame, text="Generar", width=65, command=self._generar_grid_indep).grid(row=0, column=4, padx=4)
        
        btn_ejemplo_i = ctk.CTkButton(
            ctrl_frame, text="🎲 Ejemplo", width=75, command=self._cargar_ejemplo_indep,
            fg_color=("#475569", "#374151"), hover_color=("#334155", "#4b5563")
        )
        btn_ejemplo_i.grid(row=0, column=5, padx=4)
        
        lbl_info = ctk.CTkLabel(
            left, text="Ingrese los vectores a evaluar para independencia/dependencia:",
            font=ctk.CTkFont(size=11), text_color=("gray60", "gray70")
        )
        lbl_info.pack(anchor="w", padx=14, pady=(4, 2))
        
        self.scroll_indep = ctk.CTkScrollableFrame(left, height=270)
        self.scroll_indep.pack(fill="both", expand=True, padx=14, pady=6)
        
        btn_eval_indep = ctk.CTkButton(
            left, text="🔍 Evaluar Independencia Lineal", command=self._evaluar_indep,
            fg_color=("#0284c7", "#0369a1"), hover_color=("#0369a1", "#075985"),
            font=ctk.CTkFont(size=13, weight="bold"), height=36
        )
        btn_eval_indep.pack(fill="x", padx=14, pady=(6, 12))
        
        # Panel derecho: Diagnóstico
        right = ctk.CTkFrame(tab, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)
        
        lbl_res_i = ctk.CTkLabel(
            right, text="⚖️ Análisis de Independencia y Relación de Dependencia",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=("#38bdf8", "#38bdf8")
        )
        lbl_res_i.grid(row=0, column=0, sticky="w", padx=16, pady=(12, 6))
        
        self.txt_res_indep = ctk.CTkTextbox(right, font=ctk.CTkFont(family="Consolas", size=12), wrap="word")
        self.txt_res_indep.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.txt_res_indep.configure(state="disabled")

        
        self.grid_entries_indep: List[List[ctk.CTkEntry]] = []
        self._generar_grid_indep()

    def _generar_grid_indep(self):
        try:
            n = int(self.entry_indep_n.get().strip())
            k = int(self.entry_indep_k.get().strip())
        except ValueError:
            return
        n = max(1, min(10, n))
        k = max(1, min(10, k))
        
        for w in self.scroll_indep.winfo_children():
            w.destroy()
        
        self.grid_entries_indep = []
        
        header = ctk.CTkFrame(self.scroll_indep, fg_color="transparent")
        header.pack(fill="x", pady=2)
        ctk.CTkLabel(header, text="Fila", width=36).pack(side="left")
        
        for j in range(k):
            ctk.CTkLabel(
                header, text=f"v{a_subindice(j+1)}", width=55,
                font=ctk.CTkFont(size=11, weight="bold"), text_color=("#38bdf8", "#38bdf8")
            ).pack(side="left", padx=2)
            
        for i in range(n):
            row_frame = ctk.CTkFrame(self.scroll_indep, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            ctk.CTkLabel(row_frame, text=f"F{a_subindice(i+1)}", width=36).pack(side="left")
            
            fila_entries = []
            for j in range(k):
                e = ctk.CTkEntry(row_frame, width=55, height=28, justify="center")
                e.pack(side="left", padx=2)
                e.insert(0, "0")
                fila_entries.append(e)
            self.grid_entries_indep.append(fila_entries)

    def _cargar_ejemplo_indep(self):
        ejemplos = [
            # Slide 12: v1=[1, -2, 3], v2=[2, -2, 0], v3=[0, 1, 7] -> Linealmente Independientes
            {
                "n": 3, "k": 3,
                "vectores": [[1, -2, 3], [2, -2, 0], [0, 1, 7]],
                "desc": "Diapositiva 12 Ej 1: v₁=[1, -2, 3], v₂=[2, -2, 0], v₃=[0, 1, 7] (Linealmente Independientes)"
            },
            # Slide 15: v1=[1, -3, 0], v2=[3, 0, 4], v3=[11, -6, 12] -> Linealmente Dependientes
            {
                "n": 3, "k": 3,
                "vectores": [[1, -3, 0], [3, 0, 4], [11, -6, 12]],
                "desc": "Diapositiva 15 Ej 2: v₁=[1, -3, 0], v₂=[3, 0, 4], v₃=[11, -6, 12] (Linealmente Dependientes)"
            },
            # Slide 17: v1=[1, 2, 3], v2=[4, 5, 6], v3=[2, 1, 0] -> Linealmente Dependientes
            {
                "n": 3, "k": 3,
                "vectores": [[1, 2, 3], [4, 5, 6], [2, 1, 0]],
                "desc": "Diapositiva 17 Ej 3: Conjunto L.D. con relación no trivial"
            },
            # Slide 20: v1=[3, 1], v2=[6, 2] -> L.D. por múltiplos escalares
            {
                "n": 2, "k": 2,
                "vectores": [[3, 1], [6, 2]],
                "desc": "Diapositiva 20: v₁=[3, 1], v₂=[6, 2] (L.D. por múltiplos escalares)"
            },
            # Slide 22: 4 vectores en R^3 (p > n)
            {
                "n": 3, "k": 4,
                "vectores": [[1, 7, 6], [0, 0, 9], [3, 1, 5], [4, 1, 8]],
                "desc": "Diapositiva 22: Teorema p > n (4 vectores en ℝ³)"
            },
            # Slide 22: Contiene vector cero
            {
                "n": 3, "k": 3,
                "vectores": [[2, 3, 5], [0, 0, 0], [1, 1, 8]],
                "desc": "Diapositiva 22: Conjunto que contiene al vector cero"
            }
        ]
        ej = random.choice(ejemplos)
        self.entry_indep_n.delete(0, "end")
        self.entry_indep_n.insert(0, str(ej["n"]))
        self.entry_indep_k.delete(0, "end")
        self.entry_indep_k.insert(0, str(ej["k"]))
        self._generar_grid_indep()
        
        n, k = ej["n"], ej["k"]
        for i in range(n):
            for j in range(k):
                val = ej["vectores"][j][i]
                self.grid_entries_indep[i][j].delete(0, "end")
                self.grid_entries_indep[i][j].insert(0, str(val))
                
        self._log_indep(f"🎲 Ejemplo cargado: {ej['desc']}\nPresione 'Evaluar Independencia Lineal'.", limpiar=True)

    def _evaluar_indep(self):
        modo = self.get_modo_numero()
        n = len(self.grid_entries_indep)
        k = len(self.grid_entries_indep[0])
        
        try:
            vectores: List[Vector] = [[] for _ in range(k)]
            for i in range(n):
                for j in range(k):
                    val_str = self.grid_entries_indep[i][j].get().strip()
                    val = float(val_str) if "/" not in val_str else float(val_str.split("/")[0]) / float(val_str.split("/")[1])
                    vectores[j].append(val)
        except Exception as e:
            self._log_indep(f"❌ Error al leer valores de la cuadrícula: {e}", limpiar=True)
            return
            
        resultado = evaluar_independencia_lineal(vectores, modo=modo)
        
        lineas = []
        lineas.append("==================================================")
        lineas.append("  ANÁLISIS DE INDEPENDENCIA Y DEPENDENCIA LINEAL")
        lineas.append("==================================================\n")
        
        lineas.append(f"• Conjunto de {k} vectores en ℝ{a_subindice(n)}:")
        for j, vec in enumerate(vectores):
            vec_fmt = "[" + ", ".join([formatear_numero(x, modo) for x in vec]) + "]ᵀ"
            lineas.append(f"    v{a_subindice(j+1)} = {vec_fmt}")
        lineas.append("")
        
        lineas.append("--- 1. MATRIZ DEL SISTEMA HOMOGÉNEO [v₁ ... vₖ | 0] ---")
        lineas.append(self._formatear_matriz(resultado.matriz_homogenea_inicial, modo))
        
        # Proceso de reducción paso a paso si se resolvió por Gauss-Jordan
        if resultado.pasos_gauss and len(resultado.pasos_gauss) > 1:
            lineas.append("--- 2. PROCESO DE RESOLUCIÓN PASO A PASO (GAUSS-JORDAN) ---")
            for num_p, paso in enumerate(resultado.pasos_gauss[1:], 1):
                lineas.append(f">> Paso {num_p}: {paso.descripcion}")
                lineas.append(self._formatear_matriz(paso.matriz_estado, modo))
        
        lineas.append("--- 3. MATRIZ EN FORMA ESCALONADA REDUCIDA (RREF) ---")
        lineas.append(self._formatear_matriz(resultado.matriz_rref, modo))
        
        lineas.append("--- 4. DIAGNÓSTICO Y CONCLUSIÓN ---")
        estado_badge = "✅ LINEALMENTE INDEPENDIENTE" if resultado.es_linealmente_independiente else "⚠️ LINEALMENTE DEPENDIENTE"
        lineas.append(f"Resultado: {estado_badge}")
        lineas.append(f"Criterio / Justificación: {resultado.criterio_utilizado}\n")
        lineas.append(resultado.explicacion)
        
        if not resultado.es_linealmente_independiente and resultado.relacion_dependencia:
            lineas.append(f"\nRelación no trivial verificable:\n  {resultado.relacion_dependencia}")
            
        self._log_indep("\n".join(lineas), limpiar=True)


    def _log_indep(self, texto: str, limpiar: bool = False):
        self.txt_res_indep.configure(state="normal")
        if limpiar:
            self.txt_res_indep.delete("1.0", "end")
        self.txt_res_indep.insert("end", texto + "\n")
        self.txt_res_indep.configure(state="disabled")

    def _formatear_matriz(self, matriz, modo: str) -> str:
        salida = ""
        for fila in matriz:
            coefs = fila[:-1]
            ti = fila[-1]
            coefs_str = "  ".join([f"{formatear_numero(c, modo):>8}" for c in coefs])
            salida += f"  [ {coefs_str} | {formatear_numero(ti, modo):>8} ]\n"
        return salida
