"""
Módulo de Interfaz Gráfica para Vectores en ℝⁿ (PyMatrix).

Proporciona vistas interactivas para:
1. Operaciones básicas con vectores (u + v, u - v, c·u, producto punto, normas).
2. Evaluación computacional de Combinación Lineal con reducción a RREF.
3. Evaluación de Independencia y Dependencia Lineal con detección de teoremas
   por inspección directa y deducción de relaciones no triviales.
"""

import random
from typing import List, Optional, Tuple
import customtkinter as ctk

from src.core.vectors import (
    Vector, sumar_vectores, restar_vectores, multiplicar_vector_escalar,
    sumar_multiples_vectores, restar_multiples_vectores, combinacion_lineal_ponderada,
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
    # =========================================================================
    # SUB-PESTAÑA 1: OPERACIONES BÁSICAS CON VECTORES (k VECTORES Y ESCALARES)
    # =========================================================================
    def _setup_tab_basicas(self):
        tab = self.tab_basicas
        tab.grid_columnconfigure(0, weight=0)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo: Controles y entradas
        left_frame = ctk.CTkFrame(tab, width=460, corner_radius=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left_frame.grid_propagate(False)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Controles de Dimensión (n) y Cantidad de Vectores (k)
        dim_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        dim_frame.pack(fill="x", padx=12, pady=(10, 4))
        
        ctk.CTkLabel(dim_frame, text="Dimensión (n):", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=(0, 2))
        self.entry_basicas_n = ctk.CTkEntry(dim_frame, width=38, justify="center")
        self.entry_basicas_n.pack(side="left", padx=2)
        self.entry_basicas_n.insert(0, "3")
        
        ctk.CTkLabel(dim_frame, text="Vectores (k):", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=(6, 2))
        self.entry_basicas_k = ctk.CTkEntry(dim_frame, width=38, justify="center")
        self.entry_basicas_k.pack(side="left", padx=2)
        self.entry_basicas_k.insert(0, "3")
        
        btn_crear_basicas = ctk.CTkButton(
            dim_frame, text="Generar", width=65, command=self._generar_entradas_basicas
        )
        btn_crear_basicas.pack(side="left", padx=4)
        
        btn_ejemplo_b = ctk.CTkButton(
            dim_frame, text="🎲 Ejemplo", width=75, command=self._cargar_ejemplo_basicas,
            fg_color=("#475569", "#374151"), hover_color=("#334155", "#4b5563")
        )
        btn_ejemplo_b.pack(side="left", padx=4)
        
        lbl_hint = ctk.CTkLabel(
            left_frame, 
            text="Cada vector vⱼ tiene su propio escalar cⱼ en la primera fila de la cuadrícula:",
            font=ctk.CTkFont(size=11), text_color=("gray60", "gray70")
        )
        lbl_hint.pack(anchor="w", padx=14, pady=(2, 4))
        
        # Scrollable frame para los vectores v₁ ... vₖ y sus escalares
        self.scroll_basicas = ctk.CTkScrollableFrame(left_frame, height=210)
        self.scroll_basicas.pack(fill="both", expand=True, padx=12, pady=4)
        
        # Fila de selección de producto punto v_i · v_j
        dot_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        dot_frame.pack(fill="x", padx=12, pady=(4, 2))
        ctk.CTkLabel(dot_frame, text="Producto Punto:", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=(0, 4))
        self.combo_dot_1 = ctk.CTkOptionMenu(dot_frame, values=["v₁", "v₂", "v₃"], width=70)
        self.combo_dot_1.pack(side="left", padx=2)
        ctk.CTkLabel(dot_frame, text="·", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=2)
        self.combo_dot_2 = ctk.CTkOptionMenu(dot_frame, values=["v₁", "v₂", "v₃"], width=70)
        self.combo_dot_2.pack(side="left", padx=2)
        ctk.CTkButton(
            dot_frame, text="Calcular vᵢ · vⱼ", width=120, command=self._calc_producto_punto_par,
            fg_color=("#7c3aed", "#6d28d9")
        ).pack(side="left", padx=(6, 2))
        
        # Botones de Operación
        btn_grid = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_grid.pack(fill="x", padx=12, pady=(4, 10))
        btn_grid.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(
            btn_grid, text="c₁v₁ + ... + cₖvₖ  (Ponderada)", command=lambda: self._calc_basica("comb_ponderada"),
            fg_color=("#059669", "#10b981"), font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        
        ctk.CTkButton(
            btn_grid, text="v₁ + ... + vₖ  (Suma de todos)", command=lambda: self._calc_basica("suma_todos"),
            fg_color=("#0284c7", "#0369a1"), font=ctk.CTkFont(size=11)
        ).grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        
        ctk.CTkButton(
            btn_grid, text="v₁ − v₂ − ...  (Resta sucesiva)", command=lambda: self._calc_basica("resta_todos"),
            fg_color=("#0284c7", "#0369a1"), font=ctk.CTkFont(size=11)
        ).grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        
        ctk.CTkButton(
            btn_grid, text="cᵢ · vᵢ  (Escalar a cada vector)", command=lambda: self._calc_basica("escalar_todos"),
            fg_color=("#0d9488", "#0f766e"), font=ctk.CTkFont(size=11)
        ).grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        
        ctk.CTkButton(
            btn_grid, text="||vᵢ||  (Normas de todos)", command=lambda: self._calc_basica("normas_todos"),
            fg_color=("#b45309", "#92400e"), font=ctk.CTkFont(size=11)
        ).grid(row=2, column=0, padx=2, pady=2, sticky="ew")
        
        ctk.CTkButton(
            btn_grid, text="Todos los Productos Punto", command=lambda: self._calc_basica("puntos_todos"),
            fg_color=("#6d28d9", "#5b21b6"), font=ctk.CTkFont(size=11)
        ).grid(row=2, column=1, padx=2, pady=2, sticky="ew")
        
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
        
        self.entries_escalares_basicas: List[ctk.CTkEntry] = []
        self.entries_grid_basicas: List[List[ctk.CTkEntry]] = []
        self._generar_entradas_basicas()

    def _generar_entradas_basicas(self):
        try:
            n = int(self.entry_basicas_n.get().strip())
            k = int(self.entry_basicas_k.get().strip())
        except ValueError:
            return
        n = max(1, min(10, n))
        k = max(1, min(8, k))
        
        for w in self.scroll_basicas.winfo_children():
            w.destroy()
        
        self.entries_escalares_basicas = []
        self.entries_grid_basicas = []
        
        # Actualizar opciones de producto punto
        nombres_vecs = [f"v{a_subindice(j+1)}" for j in range(k)]
        if hasattr(self, "combo_dot_1"):
            self.combo_dot_1.configure(values=nombres_vecs)
            self.combo_dot_1.set(nombres_vecs[0])
            self.combo_dot_2.configure(values=nombres_vecs)
            self.combo_dot_2.set(nombres_vecs[1 if k > 1 else 0])
        
        # Cabecera
        header = ctk.CTkFrame(self.scroll_basicas, fg_color="transparent")
        header.pack(fill="x", pady=2)
        ctk.CTkLabel(header, text="Vector", width=80, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left")
        for j in range(k):
            ctk.CTkLabel(
                header, text=f"v{a_subindice(j+1)}", width=55,
                font=ctk.CTkFont(size=11, weight="bold"), text_color=("#38bdf8", "#38bdf8")
            ).pack(side="left", padx=2)
            
        # Fila de Escalares individuales
        row_esc = ctk.CTkFrame(self.scroll_basicas, fg_color="transparent")
        row_esc.pack(fill="x", pady=(2, 6))
        ctk.CTkLabel(
            row_esc, text="Escalar cⱼ:", width=80,
            font=ctk.CTkFont(size=11, weight="bold"), text_color=("#fbbf24", "#f59e0b")
        ).pack(side="left")
        
        for j in range(k):
            esc_e = ctk.CTkEntry(
                row_esc, width=55, height=28, justify="center",
                fg_color=("#fef3c7", "#451a03"), text_color=("#b45309", "#fde68a"),
                border_color=("#f59e0b", "#d97706")
            )
            esc_e.pack(side="left", padx=2)
            esc_e.insert(0, str(j + 1))  # Por defecto 1, 2, 3...
            self.entries_escalares_basicas.append(esc_e)
            
        # Filas de Componentes
        for i in range(n):
            fila = ctk.CTkFrame(self.scroll_basicas, fg_color="transparent")
            fila.pack(fill="x", pady=2)
            ctk.CTkLabel(fila, text=f"Comp {i+1}:", width=80).pack(side="left")
            
            fila_entries = []
            for j in range(k):
                e = ctk.CTkEntry(fila, width=55, height=28, justify="center")
                e.pack(side="left", padx=2)
                e.insert(0, "0")
                fila_entries.append(e)
            self.entries_grid_basicas.append(fila_entries)

    def _leer_vectores_y_escalares_basicas(self) -> Tuple[List[Vector], List[float]]:
        n = len(self.entries_grid_basicas)
        k = len(self.entries_escalares_basicas)
        
        escalares: List[float] = []
        for j, e_c in enumerate(self.entries_escalares_basicas):
            val_c_str = e_c.get().strip()
            try:
                c = float(val_c_str) if "/" not in val_c_str else float(val_c_str.split("/")[0]) / float(val_c_str.split("/")[1])
                escalares.append(c)
            except Exception:
                raise ValueError(f"Escalar no numérico '{val_c_str}' para el vector v{j+1}.")
                
        vectores: List[Vector] = [[] for _ in range(k)]
        for i in range(n):
            for j in range(k):
                val_str = self.entries_grid_basicas[i][j].get().strip()
                try:
                    v = float(val_str) if "/" not in val_str else float(val_str.split("/")[0]) / float(val_str.split("/")[1])
                    vectores[j].append(v)
                except Exception:
                    raise ValueError(f"Valor no numérico '{val_str}' en componente {i+1} de v{j+1}.")
                    
        return vectores, escalares

    def _cargar_ejemplo_basicas(self):
        ejemplos = [
            # Caso 1: 3 vectores en R^3 con escalares 2, -1, 3
            {
                "n": 3, "k": 3,
                "vectores": [[1, 2, -1], [3, 0, 2], [-1, 4, 1]],
                "escalares": [2, -1, 3],
                "desc": "3 vectores en ℝ³ con escalares individuales (c₁=2, c₂=-1, c₃=3)"
            },
            # Caso 2: Slide 4 Ej 4 (2 vectores en R^2 con escalares 4 y -3)
            {
                "n": 2, "k": 2,
                "vectores": [[1, -2], [2, -5]],
                "escalares": [4, -3],
                "desc": "Diapositiva 4 Ej 4: 4u + (-3)v (u=[1, -2], v=[2, -5])"
            },
            # Caso 3: 4 vectores en R^3 con escalares 1, 2, -2, 1
            {
                "n": 3, "k": 4,
                "vectores": [[2, 1, 0], [0, 3, -1], [1, 2, 4], [-2, 0, 1]],
                "escalares": [1, 2, -2, 1],
                "desc": "4 vectores en ℝ³ con escalares propios [1, 2, -2, 1]"
            },
            # Caso 4: Slide 23 Ej I (3 vectores en R^3)
            {
                "n": 3, "k": 3,
                "vectores": [[3, 2, -4], [-6, 1, 7], [1, -1, 2]],
                "escalares": [2, 3, -1],
                "desc": "Diapositiva 23 Ej I ampliado a 3 vectores"
            }
        ]
        ej = random.choice(ejemplos)
        self.entry_basicas_n.delete(0, "end")
        self.entry_basicas_n.insert(0, str(ej["n"]))
        self.entry_basicas_k.delete(0, "end")
        self.entry_basicas_k.insert(0, str(ej["k"]))
        self._generar_entradas_basicas()
        
        n, k = ej["n"], ej["k"]
        for j in range(k):
            self.entries_escalares_basicas[j].delete(0, "end")
            self.entries_escalares_basicas[j].insert(0, str(ej["escalares"][j]))
            for i in range(n):
                self.entries_grid_basicas[i][j].delete(0, "end")
                self.entries_grid_basicas[i][j].insert(0, str(ej["vectores"][j][i]))
        
        self._log_basicas(f"🎲 Ejemplo cargado: {ej['desc']}\nSeleccione la operación deseada.", limpiar=True)

    def _calc_producto_punto_par(self):
        """Calcula el producto punto v_i · v_j entre los dos vectores seleccionados en los OptionMenu."""
        modo = self.get_modo_numero()
        try:
            vectores, _ = self._leer_vectores_y_escalares_basicas()
        except ValueError as e:
            self._log_basicas(f"❌ Error de entrada: {e}", limpiar=True)
            return
            
        k = len(vectores)
        str_1 = self.combo_dot_1.get()
        str_2 = self.combo_dot_2.get()
        
        # Extraer índice 0-based
        idx_1 = 0
        idx_2 = 1 if k > 1 else 0
        for j in range(k):
            if f"v{a_subindice(j+1)}" == str_1 or f"v{j+1}" == str_1:
                idx_1 = j
            if f"v{a_subindice(j+1)}" == str_2 or f"v{j+1}" == str_2:
                idx_2 = j
                
        u = vectores[idx_1]
        v = vectores[idx_2]
        pp = producto_punto(u, v)
        
        u_str = "[" + ", ".join([formatear_numero(x, modo) for x in u]) + "]ᵀ"
        v_str = "[" + ", ".join([formatear_numero(x, modo) for x in v]) + "]ᵀ"
        
        lineas = [
            f">> PRODUCTO PUNTO ENTRE PARES: {str_1} · {str_2}",
            f"  {str_1} = {u_str}",
            f"  {str_2} = {v_str}\n",
            "Regla: u · v = ∑ uᵢ · vᵢ (suma de los productos de entradas homólogas)"
        ]
        terminos = [f"({formatear_numero(ui, modo)})·({formatear_numero(vi, modo)})" for ui, vi in zip(u, v)]
        lineas.append(f"  Desarrollo: {' + '.join(terminos)}")
        lineas.append(f"\nResultado escalar: {str_1} · {str_2} = {formatear_numero(pp, modo)}")
        self._log_basicas("\n".join(lineas), limpiar=True)

    def _calc_basica(self, op_tipo: str):
        modo = self.get_modo_numero()
        try:
            vectores, escalares = self._leer_vectores_y_escalares_basicas()
        except ValueError as e:
            self._log_basicas(f"❌ Error de entrada: {e}", limpiar=True)
            return
        
        n = len(vectores[0])
        k = len(vectores)
        
        lineas = []
        lineas.append(f"• Vectores y escalares en ℝ{a_subindice(n)} ({k} vectores):")
        for j, (vec, c) in enumerate(zip(vectores, escalares)):
            vec_fmt = "[" + ", ".join([formatear_numero(x, modo) for x in vec]) + "]ᵀ"
            lineas.append(f"    v{a_subindice(j+1)} = {vec_fmt}  |  Escalar c{a_subindice(j+1)} = {formatear_numero(c, modo)}")
        lineas.append("")
        
        if op_tipo == "comb_ponderada":
            res = combinacion_lineal_ponderada(escalares, vectores)
            eq_formula = " + ".join([f"c{a_subindice(j+1)}·v{a_subindice(j+1)}" for j in range(k)])
            eq_valores = " + ".join([f"({formatear_numero(c, modo)})·v{a_subindice(j+1)}" for j, c in enumerate(escalares)])
            lineas.append(f">> COMBINACIÓN LINEAL PONDERADA: {eq_formula}")
            lineas.append(f"Expresión: {eq_valores}\n")
            lineas.append("Procedimiento coordenada a coordenada:")
            for i in range(n):
                terminos_i = [f"({formatear_numero(c, modo)})·({formatear_numero(v[i], modo)})" for c, v in zip(escalares, vectores)]
                lineas.append(f"  Comp {i+1}: {' + '.join(terminos_i)} = {formatear_numero(res[i], modo)}")
            res_str = "[" + ", ".join([formatear_numero(x, modo) for x in res]) + "]ᵀ"
            lineas.append(f"\nResultado del vector resultante: {res_str}")
            
        elif op_tipo == "suma_todos":
            res = sumar_multiples_vectores(vectores)
            eq_formula = " + ".join([f"v{a_subindice(j+1)}" for j in range(k)])
            lineas.append(f">> SUMA DE TODOS LOS VECTORES: {eq_formula}")
            lineas.append("Regla: (∑ vⱼ)ᵢ = ∑ v_{j, i} (sumar coordenadas homólogas)\n")
            for i in range(n):
                terminos_i = [f"({formatear_numero(v[i], modo)})" for v in vectores]
                lineas.append(f"  Comp {i+1}: {' + '.join(terminos_i)} = {formatear_numero(res[i], modo)}")
            res_str = "[" + ", ".join([formatear_numero(x, modo) for x in res]) + "]ᵀ"
            lineas.append(f"\nResultado: ∑ vⱼ = {res_str}")
            
        elif op_tipo == "resta_todos":
            res = restar_multiples_vectores(vectores)
            eq_formula = f"v₁" + "".join([f" − v{a_subindice(j+1)}" for j in range(1, k)])
            lineas.append(f">> RESTA SUCESIVA DE VECTORES: {eq_formula}")
            lineas.append("Regla: restar sucesivamente cada vector a partir del primero v₁\n")
            for i in range(n):
                terminos_i = f"({formatear_numero(vectores[0][i], modo)})" + "".join([f" − ({formatear_numero(vectores[j][i], modo)})" for j in range(1, k)])
                lineas.append(f"  Comp {i+1}: {terminos_i} = {formatear_numero(res[i], modo)}")
            res_str = "[" + ", ".join([formatear_numero(x, modo) for x in res]) + "]ᵀ"
            lineas.append(f"\nResultado: {eq_formula} = {res_str}")
            
        elif op_tipo == "escalar_todos":
            lineas.append(">> MULTIPLICACIÓN DE CADA VECTOR POR SU PROPIO ESCALAR (cⱼ · vⱼ)")
            lineas.append("Regla: cada coordenada se multiplica por el escalar propio del vector:\n")
            for j, (v, c) in enumerate(zip(vectores, escalares)):
                c_fmt = formatear_numero(c, modo)
                v_scaled = multiplicar_vector_escalar(c, v)
                desglose = [f"{c_fmt}·({formatear_numero(x, modo)})" for x in v]
                res_v = "[" + ", ".join([formatear_numero(x, modo) for x in v_scaled]) + "]ᵀ"
                lineas.append(f"  • {c_fmt} · v{a_subindice(j+1)} = [ {', '.join(desglose)} ]ᵀ = {res_v}")
                
        elif op_tipo == "normas_todos":
            lineas.append(">> NORMAS EUCLIDIANAS (LONGITUDES O MAGNITUDES ||vⱼ||)")
            lineas.append("Regla: ||v|| = √(∑ vᵢ²) para cada vector:\n")
            for j, v in enumerate(vectores):
                nv = norma_vector(v)
                sq_terms = " + ".join([f"({formatear_numero(x, modo)})²" for x in v])
                lineas.append(f"  • ||v{a_subindice(j+1)}|| = √({sq_terms}) = {nv}")
                
        elif op_tipo == "puntos_todos":
            lineas.append(">> TODOS LOS PRODUCTOS PUNTO ENTRE PARES DE VECTORES (vᵢ · vⱼ)")
            lineas.append("Regla: vᵢ · vⱼ = ∑ v_{i,m} · v_{j,m}\n")
            for i_idx in range(k):
                for j_idx in range(i_idx, k):
                    pp = producto_punto(vectores[i_idx], vectores[j_idx])
                    etiq = f"v{a_subindice(i_idx+1)} · v{a_subindice(j_idx+1)}"
                    if i_idx == j_idx:
                        lineas.append(f"  • {etiq} = ||v{a_subindice(i_idx+1)}||² = {formatear_numero(pp, modo)}")
                    else:
                        lineas.append(f"  • {etiq} = {formatear_numero(pp, modo)}")
                        
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
