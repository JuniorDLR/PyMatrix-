"""
Módulo de Interfaz Gráfica para Operaciones Matriciales y Ecuaciones Matriciales (PyMatrix).

Proporciona vistas interactivas para:
1. Operaciones básicas con matrices: A + B, A - B, c·A, A · B.
2. Producto matriz-vector A · x con desglose por filas y como combinación de columnas.
3. Resolución de la ecuación matricial Ax = b mediante [A | b] → Gauss-Jordan.
"""

import random
from typing import List, Optional
import customtkinter as ctk

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
    """Panel principal para operaciones matriciales y ecuaciones Ax = b."""

    def __init__(self, master, get_modo_numero_cb, **kwargs):
        super().__init__(master, **kwargs)
        self.get_modo_numero = get_modo_numero_cb
        self._ultimo_calc_ops = None
        self._ultimo_calc_axb = None
        self._ultimo_calc_prop = None
        self._ultimo_calc_inv = None   # "traspuesta" | "inversa"
        self._ultimo_calc_det = None   # "determinante"

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._setup_ui()

    def _setup_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

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
        """Refresca entradas y salidas cuando cambia el formato global (Fracción/Decimal)."""
        modo = self.get_modo_numero()

        def _convertir(entry):
            try:
                if entry is not None and entry.winfo_exists():
                    val = entry.get()
                    nuevo = convertir_texto_a_modo(val, modo)
                    if nuevo != val:
                        entry.delete(0, "end")
                        entry.insert(0, nuevo)
            except Exception:
                pass

        # Tab 1: Operaciones
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

        # Tab 2: Ax = b
        if hasattr(self, "entries_axb"):
            for fila in self.entries_axb:
                for e in fila:
                    _convertir(e)

        # Tab 3: Propiedades Ax
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

        # Tab 4: Traspuesta e Inversa
        if hasattr(self, "entries_inv"):
            for fila in self.entries_inv:
                for e in fila:
                    _convertir(e)

        # Tab 5: Determinantes
        if hasattr(self, "entries_det"):
            for fila in self.entries_det:
                for e in fila:
                    _convertir(e)

        # Refrescar salidas calculadas activas
        if self._ultimo_calc_ops:
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
        if self._ultimo_calc_det == "determinante":
            self._calc_determinante()


    # =========================================================================
    # SUB-PESTAÑA 1: OPERACIONES BÁSICAS CON MATRICES
    # =========================================================================
    def _setup_tab_ops(self):
        tab = self.tab_ops
        tab.grid_columnconfigure(0, weight=0)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # Panel izquierdo: Entrada de matrices
        left = ctk.CTkFrame(tab, width=500, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left.grid_propagate(False)
        left.grid_columnconfigure(0, weight=1)

        # Controles de dimensión
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

        # Scroll con cuadrículas de A y B
        self.scroll_ops = ctk.CTkScrollableFrame(left, height=170)
        self.scroll_ops.pack(fill="both", expand=True, padx=14, pady=4)

        # Botones de operación (exactamente las 4 operaciones requeridas)
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


        # Panel derecho: resultados
        right = ctk.CTkFrame(tab, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            right, text="📋 Procedimiento Paso a Paso",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=("#38bdf8", "#38bdf8")
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 6))

        self.txt_res_ops = ctk.CTkTextbox(right, font=ctk.CTkFont(family="Consolas", size=12), wrap="word")
        self.txt_res_ops.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.txt_res_ops.configure(state="disabled")


        # Variables internas
        self.entries_A: List[List[ctk.CTkEntry]] = []
        self.entries_B: List[List[ctk.CTkEntry]] = []
        self._generar_matrices_ops()

    def _generar_matrices_ops(self):
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

        # Título A
        ctk.CTkLabel(
            self.scroll_ops, text=f"Matriz A  ({mA} × {nA})",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=("#38bdf8", "#38bdf8")
        ).pack(anchor="w", pady=(4, 2))
        self._crear_grid_matriz(self.scroll_ops, mA, nA, self.entries_A, color_col_last=False)

        ctk.CTkLabel(self.scroll_ops, text="").pack(pady=4)

        # Título B
        ctk.CTkLabel(
            self.scroll_ops, text=f"Matriz B  ({mB} × {nB})",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=("#34d399", "#34d399")
        ).pack(anchor="w", pady=(4, 2))
        self._crear_grid_matriz(self.scroll_ops, mB, nB, self.entries_B, color_col_last=False)

    def _crear_grid_matriz(self, parent, m: int, n: int,
                           entries_dest: List[List[ctk.CTkEntry]],
                           color_col_last: bool = True):
        """Crea una cuadrícula m × n de CTkEntry dentro de parent."""
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
        mat: Matriz = []
        for i, row in enumerate(entries):
            fila = []
            for j, e in enumerate(row):
                val_str = e.get().strip()
                try:
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
        ejemplos = [
            # Slide 9: Suma/Resta de matrices 2x2
            {
                "mA": 2, "nA": 2, "mB": 2, "nB": 2,
                "A": [[1, -4], [0, 3]],
                "B": [[2, 3], [-7, 5]],
                "c": 3, "desc": "Diapositiva 9: Suma/Resta de matrices 2×2"
            },
            # Producto matricial A (2x3) x B (3x2)
            {
                "mA": 2, "nA": 3, "mB": 3, "nB": 2,
                "A": [[1, 2, -1], [0, -5, 3]],
                "B": [[4, 1], [3, 0], [7, 2]],
                "c": 2, "desc": "Producto Matricial A(2×3) × B(3×2) — Desglose de sumas de productos"
            },
            # Slide 7 Ej: A (3x3) x B (3x3)
            {
                "mA": 3, "nA": 3, "mB": 3, "nB": 3,
                "A": [[2, 3, 4], [1, -2, 0], [3, 1, -1]],
                "B": [[1, 0, 2], [3, -1, 0], [0, 4, 1]],
                "cA": -1, "cB": 2,
                "desc": "Matrices 3×3: Compara A×B vs B×A (Demostración de No Conmutatividad)"
            },
            # Dimensiones compatibles en una sola dirección
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

        self._log_ops(f"🎲 Ejemplo cargado: {ej['desc']}\nSeleccione la operación a realizar.", limpiar=True)

    def _calc_op(self, op: str):
        self._ultimo_calc_ops = op
        modo = self.get_modo_numero()
        try:
            A = self._leer_matriz_entries(self.entries_A)
            B = self._leer_matriz_entries(self.entries_B)
            c_str = self.entry_ops_c.get().strip() if hasattr(self, "entry_ops_c") else "2"
            c = float(c_str) if "/" not in c_str else float(c_str.split("/")[0]) / float(c_str.split("/")[1])
        except ValueError as e:
            self._log_ops(f"❌ Error de entrada: {e}", limpiar=True)
            return

        mA, nA = len(A), len(A[0])
        mB, nB = len(B), len(B[0])
        c_fmt = formatear_numero(c, modo)
        lineas = []

        try:
            if op == "suma":
                R = sumar_matrices(A, B)
                lineas.append(">> SUMA DE MATRICES: A + B")
                lineas.append(f"Condición de Dimensión: Ambas matrices deben ser del mismo orden (m × n).")
                lineas.append(f"  Dimensión de A: {mA}×{nA}  |  Dimensión de B: {mB}×{nB}  → {'✓ Mismas dimensiones' if (mA==mB and nA==nB) else '✗ Incompatibles'}")
                lineas.append(f"\nA ({mA}×{nA}):\n{self._fmt_mat(A, modo)}")
                lineas.append(f"B ({mB}×{nB}):\n{self._fmt_mat(B, modo)}")
                lineas.append("Procedimiento: C_ij = A_ij + B_ij para cada posición.")
                lineas.append(f"\nResultado C = A + B ({mA}×{nA}):\n{self._fmt_mat(R, modo)}")
                from modulos.modulo_matrices import crear_matriz, analizar_suma_matrices
                A_f = crear_matriz(A); B_f = crear_matriz(B); R_f = crear_matriz(R)
                lineas.append("\n" + "\n".join(analizar_suma_matrices(A_f, B_f, R_f)))

            elif op in ("resta", "resta_AB"):
                R = restar_matrices(A, B)
                lineas.append(">> RESTA DE MATRICES: A − B")
                lineas.append(f"Condición de Dimensión: Ambas matrices deben ser del mismo orden (m × n).")
                lineas.append(f"  Dimensión de A: {mA}×{nA}  |  Dimensión de B: {mB}×{nB}  → {'✓ Mismas dimensiones' if (mA==mB and nA==nB) else '✗ Incompatibles'}")
                lineas.append(f"\nA ({mA}×{nA}):\n{self._fmt_mat(A, modo)}")
                lineas.append(f"B ({mB}×{nB}):\n{self._fmt_mat(B, modo)}")
                lineas.append("Procedimiento: C_ij = A_ij − B_ij para cada posición.")
                lineas.append(f"\nResultado C = A − B ({mA}×{nA}):\n{self._fmt_mat(R, modo)}")
                from modulos.modulo_matrices import crear_matriz, analizar_resta_matrices
                A_f = crear_matriz(A); B_f = crear_matriz(B); R_f = crear_matriz(R)
                lineas.append("\n" + "\n".join(analizar_resta_matrices(A_f, B_f, R_f)))

            elif op in ("escalar", "esc_A"):
                R = multiplicar_matriz_escalar(c, A)
                lineas.append(f">> MULTIPLICACIÓN DE MATRIZ POR UN ESCALAR: {c_fmt} · A")
                lineas.append(f"\nEscalar c = {c_fmt}")
                lineas.append(f"Matriz A ({mA}×{nA}):\n{self._fmt_mat(A, modo)}")
                lineas.append("Procedimiento: (c·A)_ij = c · A_ij entrada por entrada.")
                lineas.append(f"\nResultado {c_fmt}·A ({mA}×{nA}):\n{self._fmt_mat(R, modo)}")
                from modulos.modulo_matrices import crear_matriz, parsear_fraccion, analizar_escalar_matriz
                A_f = crear_matriz(A); R_f = crear_matriz(R); c_f = parsear_fraccion(c)
                lineas.append("\n" + "\n".join(analizar_escalar_matriz(c_f, A_f, R_f)))

            elif op in ("multiplicacion", "prod_AB"):
                res = multiplicar_matrices(A, B, modo=modo)
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
                from modulos.modulo_matrices import crear_matriz, analizar_producto_matricial
                A_f = crear_matriz(A); B_f = crear_matriz(B); C_f = crear_matriz(res.matriz_resultado)
                lineas.append("\n" + "\n".join(analizar_producto_matricial(A_f, B_f, C_f)))

        except ValueError as e:
            lineas = [f"❌ Error de cálculo: {e}"]

        self._log_ops("\n".join(lineas), limpiar=True)


    def _fmt_mat(self, mat: Matriz, modo: str) -> str:
        s = ""
        for fila in mat:
            s += "  [ " + "  ".join([f"{formatear_numero(x, modo):>8}" for x in fila]) + " ]\n"
        return s

    def _log_ops(self, texto: str, limpiar: bool = False):
        self.txt_res_ops.configure(state="normal")
        if limpiar:
            self.txt_res_ops.delete("1.0", "end")
        self.txt_res_ops.insert("end", texto + "\n")
        self.txt_res_ops.configure(state="disabled")

    # =========================================================================
    # SUB-PESTAÑA 2: ECUACIÓN MATRICIAL Ax = b
    # =========================================================================
    def _setup_tab_axb(self):
        tab = self.tab_axb
        tab.grid_columnconfigure(0, weight=0)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # Panel izquierdo
        left = ctk.CTkFrame(tab, width=460, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left.grid_propagate(False)
        left.grid_columnconfigure(0, weight=1)

        # Controles
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

        # Grid de [A | b]
        self.scroll_axb = ctk.CTkScrollableFrame(left, height=250)
        self.scroll_axb.pack(fill="both", expand=True, padx=14, pady=4)

        # Dos botones: Calcular Ax y Resolver Ax = b
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

        # Panel derecho: Resultados
        right = ctk.CTkFrame(tab, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            right, text="📐 Resultado y Procedimiento Algebraico",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=("#38bdf8", "#38bdf8")
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 6))

        self.txt_res_axb = ctk.CTkTextbox(right, font=ctk.CTkFont(family="Consolas", size=12), wrap="word")
        self.txt_res_axb.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.txt_res_axb.configure(state="disabled")


        # Estado interno
        self.entries_axb: List[List[ctk.CTkEntry]] = []
        self._generar_axb()

    def _generar_axb(self):
        try:
            m = max(1, min(8, int(self.entry_axb_m.get())))
            n = max(1, min(8, int(self.entry_axb_n.get())))
        except ValueError:
            return

        for w in self.scroll_axb.winfo_children():
            w.destroy()
        self.entries_axb = []

        # Cabecera
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
            # Columna b
            eb = ctk.CTkEntry(
                row_f, width=55, height=26, justify="center",
                fg_color=("#ffe4e6", "#3f1a24"), text_color=("#be123c", "#fca5a5")
            )
            eb.pack(side="left", padx=(6, 2))
            eb.insert(0, "0")
            fila_entries.append(eb)
            self.entries_axb.append(fila_entries)

    def _leer_axb(self):
        """Lee la cuadrícula y devuelve (A, b)."""
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
        ejemplos = [
            # Slide 4: A(2x3), x dado, calcular Ax
            {
                "m": 2, "n": 3,
                "A": [[1, 2, -1], [0, -5, 3]],
                "b": [3, 6],
                "desc": "Diapositiva 4: A(2×3), b=[3, 6] → resolver Ax = b"
            },
            # Slide 5: A(3x2), x=[4, 7], b=[-13, 32, -6]
            {
                "m": 3, "n": 2,
                "A": [[2, -3], [8, 0], [-5, 2]],
                "b": [-13, 32, -6],
                "desc": "Diapositiva 5: A(3×2), b=[-13, 32, -6] → resolución Ax = b"
            },
            # Sistema con solución única 3x3
            {
                "m": 3, "n": 3,
                "A": [[2, 1, -1], [-3, -1, 2], [-2, 1, 2]],
                "b": [8, -11, -3],
                "desc": "Sistema 3×3 Solución Única — clásico (x₁=2, x₂=3, x₃=-1)"
            },
            # Slide 7 Ej: Inconsistente
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

        self._log_axb(f"🎲 Ejemplo cargado: {ej['desc']}\nPresione 'Resolver Ax = b'.", limpiar=True)

    def _calcular_ax(self):
        """Calcula el producto A·x usando el vector b como x."""
        self._ultimo_calc_axb = "ax"
        modo = self.get_modo_numero()
        try:
            A, x = self._leer_axb()
        except ValueError as e:
            self._log_axb(f"❌ {e}", limpiar=True)
            return

        m, n = len(A), len(A[0])
        try:
            res = multiplicar_matriz_vector(A, x, modo=modo)
        except ValueError as e:
            self._log_axb(f"❌ {e}", limpiar=True)
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
        self._log_axb("\n".join(lineas), limpiar=True)

    def _resolver_axb(self):
        self._ultimo_calc_axb = "axb"
        modo = self.get_modo_numero()
        try:
            A, b = self._leer_axb()
        except ValueError as e:
            self._log_axb(f"❌ {e}", limpiar=True)
            return

        m, n = len(A), len(A[0])
        try:
            res = resolver_ecuacion_matricial(A, b, modo=modo)
        except ValueError as e:
            self._log_axb(f"❌ {e}", limpiar=True)
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
            for num_p, paso in enumerate(res.pasos_gauss[1:], 1):
                lineas.append(f">> Paso {num_p}: {paso.descripcion}")
                lineas.append(self._fmt_mat_aumentada(paso.matriz_estado, modo))

        lineas.extend([
            "--- 3. FORMA ESCALONADA REDUCIDA (RREF) ---",
            self._fmt_mat_aumentada(res.matriz_rref, modo),
            "--- 4. CLASIFICACIÓN Y SOLUCIÓN ---",
            res.resumen_explicativo
        ])
        self._log_axb("\n".join(lineas), limpiar=True)


    def _fmt_mat_aumentada(self, mat: Matriz, modo: str) -> str:
        s = ""
        for fila in mat:
            coefs = fila[:-1]
            ti = fila[-1]
            coefs_str = "  ".join([f"{formatear_numero(x, modo):>8}" for x in coefs])
            s += f"  [ {coefs_str} | {formatear_numero(ti, modo):>8} ]\n"
        return s

    def _log_axb(self, texto: str, limpiar: bool = False):
        self.txt_res_axb.configure(state="normal")
        if limpiar:
            self.txt_res_axb.delete("1.0", "end")
        self.txt_res_axb.insert("end", texto + "\n")
        self.txt_res_axb.configure(state="disabled")

    # =========================================================================
    # SUB-PESTAÑA 3: PROPIEDADES DEL PRODUCTO MATRIZ-VECTOR Ax
    # =========================================================================
    def _setup_tab_propiedades(self):
        tab = self.tab_props
        tab.grid_columnconfigure(0, weight=0)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # ── Panel izquierdo ────────────────────────────────────────────────
        left = ctk.CTkFrame(tab, width=470, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left.grid_propagate(False)
        left.grid_columnconfigure(0, weight=1)

        # Encabezado teórico
        ctk.CTkLabel(
            left,
            text="Propiedades del Producto Matriz-Vector  A·x",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("gray20", "gray90"),
        ).pack(anchor="w", padx=14, pady=(10, 2))
        ctk.CTkLabel(
            left,
            text="Teorema: Si A es m×n, u, v (o k vectores) están en ℝⁿ, y c es un escalar:\n"
                 "   a) A(u + v) = Au + Av  [o generalizado a k vectores]\n"
                 "   b) A(cu) = c(Au)\n"
                 "   c) Principio de Linealidad General: A(∑ cᵢvᵢ) = ∑ cᵢ(Avᵢ)",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
            justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 6))

        # Controles de dimensión (m filas, n columnas, k vectores)
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

        # Botones Generar / Asignación Diap. 10 / Ejemplo
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

        # Scrollable frame para A y para los vectores
        self.scroll_prop = ctk.CTkScrollableFrame(left, height=250)
        self.scroll_prop.pack(fill="both", expand=True, padx=14, pady=4)

        # Botones de verificación de teoremas
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

        self.btn_verif_sesiones10_11 = ctk.CTkButton(
            btns_p,
            text="🔬 Propiedades Sesiones 10 y 11 (Inversas y Determinantes)",
            command=self._calc_propiedades_sesiones_10_11,
            fg_color=("#ea580c", "#c2410c"),
            hover_color=("#c2410c", "#9a3412"),
            font=ctk.CTkFont(size=11, weight="bold"),
            height=32,
        )
        self.btn_verif_sesiones10_11.grid(row=2, column=0, columnspan=2, padx=2, pady=(4, 2), sticky="ew")

        # ── Panel derecho: Resultados ──────────────────────────────────────
        right = ctk.CTkFrame(tab, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            right,
            text="🔬 Demostración y Verificación Paso a Paso",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("gray20", "#38bdf8"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 6))

        self.txt_res_prop = ctk.CTkTextbox(
            right, font=ctk.CTkFont(family="Consolas", size=12), wrap="word"
        )
        self.txt_res_prop.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.txt_res_prop.configure(state="disabled")

        # Estado interno
        self.entries_prop_A: List[List[ctk.CTkEntry]] = []
        self.entries_prop_vecs: List[List[ctk.CTkEntry]] = []  # [componente_i][vector_j]
        self.entries_prop_c: List[ctk.CTkEntry] = []            # [vector_j]
        self._generar_prop()

    def _generar_prop(self):
        """Genera las cuadrículas de A (m×n), y de k vectores en ℝⁿ con sus escalares."""
        try:
            m = max(1, min(10, int(self.entry_prop_m.get().strip())))
            n = max(1, min(10, int(self.entry_prop_n.get().strip())))
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

        # Actualizar textos de botones según la cantidad de vectores
        if hasattr(self, "btn_verif_aditiva"):
            if es_dos:
                self.btn_verif_aditiva.configure(text="✓ Verificar A(u+v) = Au+Av")
                self.btn_verif_escalar.configure(text="✓ Verificar A(cu) = c(Au)")
            else:
                self.btn_verif_aditiva.configure(text=f"✓ Verificar A({' + '.join(nombres)})")
                self.btn_verif_escalar.configure(text=f"✓ Verificar A(c₁·v₁) = c₁(A·v₁)")

        # ── 1. Matriz A ──
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

        # ── 2. Vectores y Escalares ──
        sec_title = f"2. Vectores en ℝ{a_subindice(n)} y Escalares ({k} vectores):" if not es_dos else f"2. Vectores u, v en ℝ{a_subindice(n)} y Escalares:"
        ctk.CTkLabel(
            self.scroll_prop,
            text=sec_title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#38bdf8", "#38bdf8")
        ).pack(anchor="w", pady=(10, 2))

        # Cabecera de nombres de vectores
        hdr_vecs = ctk.CTkFrame(self.scroll_prop, fg_color="transparent")
        hdr_vecs.pack(fill="x")
        ctk.CTkLabel(hdr_vecs, text="", width=68).pack(side="left")
        for nom in nombres:
            ctk.CTkLabel(
                hdr_vecs, text=nom, width=55, font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("#0284c7", "#38bdf8")
            ).pack(side="left", padx=2)

        # Fila de Escalares cᵢ
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

        # Filas de Componentes
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
        """Lee A, la lista de k vectores y la lista de k escalares.
        Retorna (A: Matriz, vectores: List[Vector], escalares: List[float]).
        """
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
        """Carga exactamente el ejercicio de la Diapositiva 10:
        A = [[2, 5], [3, 1]], u = [4, -1], v = [-3, 5], c = 2.
        """
        self.entry_prop_m.delete(0, "end"); self.entry_prop_m.insert(0, "2")
        self.entry_prop_n.delete(0, "end"); self.entry_prop_n.insert(0, "2")
        self.entry_prop_k.delete(0, "end"); self.entry_prop_k.insert(0, "2")
        self._generar_prop()

        # Matriz A
        mat_A = [[2, 5], [3, 1]]
        for i in range(2):
            for j in range(2):
                self.entries_prop_A[i][j].delete(0, "end")
                self.entries_prop_A[i][j].insert(0, str(mat_A[i][j]))

        # Escalares (c = 2)
        self.entries_prop_c[0].delete(0, "end"); self.entries_prop_c[0].insert(0, "2")
        self.entries_prop_c[1].delete(0, "end"); self.entries_prop_c[1].insert(0, "3")

        # Vectores u = [4, -1], v = [-3, 5]
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
        self._log_prop(msg, limpiar=True)

    def _cargar_ejemplo_prop(self):
        """Carga ejemplos adaptables: 2 vectores en R^2, 3 vectores en R^3, 2 vectores en R^3, etc."""
        ejemplos = [
            # Caso 1: Diapositiva 10 (2x2, 2 vecs en R^2)
            {
                "m": 2, "n": 2, "k": 2,
                "A": [[2, 5], [3, 1]],
                "vecs": [[4, -1], [-3, 5]],
                "cs": [2, 3],
                "desc": "Diapositiva 10: A(2×2), u=[4, -1]ᵀ, v=[-3, 5]ᵀ en ℝ²"
            },
            # Caso 2: 3 vectores en R^3 con A(3x3)
            {
                "m": 3, "n": 3, "k": 3,
                "A": [[1, 2, 0], [0, 3, -1], [2, 1, 1]],
                "vecs": [[1, -1, 2], [2, 0, 1], [-1, 3, 0]],
                "cs": [2, -1, 3],
                "desc": "General: 3 vectores en ℝ³ con matriz A(3×3) y escalares [2, -1, 3]"
            },
            # Caso 3: Matriz rectangular 2x3 con 3 vectores en R^3
            {
                "m": 2, "n": 3, "k": 3,
                "A": [[1, 2, -1], [0, -5, 3]],
                "vecs": [[4, 3, 7], [1, 0, -2], [2, -1, 1]],
                "cs": [1, 2, -1],
                "desc": "Rectangular A(2×3) (Slide 4) con 3 vectores en ℝ³"
            },
            # Caso 4: Matriz rectangular 3x2 con 2 vectores en R^2
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

        self._log_prop(f"🎲 Ejemplo cargado: {ej['desc']}\nSeleccione una propiedad para verificar el teorema.", limpiar=True)

    def _calc_propiedad_aditiva(self):
        """Calcula y muestra la verificación de la propiedad aditiva/distributiva."""
        self._ultimo_calc_prop = "aditiva"
        modo = self.get_modo_numero()
        try:
            A, vecs, _ = self._leer_prop()
        except ValueError as e:
            self._log_prop(f"❌ {e}", limpiar=True)
            return

        try:
            resultado = verificar_propiedad_aditiva_ax(A, vecs, modo=modo)
        except ValueError as e:
            self._log_prop(f"❌ {e}", limpiar=True)
            return

        self._log_prop("\n".join(resultado.desglose_pasos), limpiar=True)

    def _calc_propiedad_escalar(self):
        """Calcula y muestra la verificación de A(cu) = c(Au) para el primer vector."""
        self._ultimo_calc_prop = "escalar"
        modo = self.get_modo_numero()
        try:
            A, vecs, escalares = self._leer_prop()
        except ValueError as e:
            self._log_prop(f"❌ {e}", limpiar=True)
            return

        k = len(vecs)
        nom = "u" if k == 2 else "v₁"
        c_val = escalares[0]
        u_vec = vecs[0]

        try:
            resultado = verificar_propiedad_escalar_ax(A, u_vec, c_val, modo=modo, nombre_vector=nom)
        except ValueError as e:
            self._log_prop(f"❌ {e}", limpiar=True)
            return

        self._log_prop("\n".join(resultado.desglose_pasos), limpiar=True)

    def _calc_linealidad_general(self):
        """Calcula y muestra la verificación del principio de superposición / linealidad general."""
        self._ultimo_calc_prop = "linealidad"
        modo = self.get_modo_numero()
        try:
            A, vecs, escalares = self._leer_prop()
        except ValueError as e:
            self._log_prop(f"❌ {e}", limpiar=True)
            return

        try:
            resultado = verificar_linealidad_general_ax(A, vecs, escalares, modo=modo)
        except ValueError as e:
            self._log_prop(f"❌ {e}", limpiar=True)
            return

        self._log_prop("\n".join(resultado.desglose_pasos), limpiar=True)

    def _calc_propiedades_sesiones_10_11(self):
        """Verifica sistemáticamente las 6 propiedades clave de inversas y determinantes (Sesiones 10 y 11)."""
        self._ultimo_calc_prop = "sesiones10_11"
        try:
            A, vecs, escalares = self._leer_prop()
        except ValueError as e:
            self._log_prop(f"❌ {e}", limpiar=True)
            return

        mA, nA = len(A), len(A[0])
        if mA != nA:
            self._log_prop("❌ Para verificar las propiedades de Sesiones 10 y 11, la matriz A debe ser cuadrada (m = n).", limpiar=True)
            return

        from fractions import Fraction
        from modulos.modulo_matrices import (
            crear_matriz, verificar_propiedad_inversa_de_inversa,
            verificar_propiedad_inversa_del_producto, verificar_propiedad_inversa_de_traspuesta,
            verificar_propiedad_determinante_de_inversa, verificar_propiedades_operaciones_fila_det,
            verificar_propiedad_matriz_triangular
        )

        A_f = crear_matriz(A)
        # Matriz B auxiliar para el producto (AB)⁻¹ = B⁻¹A⁻¹
        B_f = [[Fraction(1 if i == j else 2, 1) for j in range(nA)] for i in range(nA)]

        lineas = [
            "═" * 70,
            "  VERIFICADOR DE PROPIEDADES ALGEBRAICAS — SESIONES 10 Y 11",
            "═" * 70,
            ""
        ]

        p1 = verificar_propiedad_inversa_de_inversa(A_f)
        lineas += [f"1. {p1.nombre} [{p1.formula}]:", f"   {p1.explicacion}", f"   Estado: {'✓ SE CUMPLE IDENTICAMENTE' if p1.se_cumple else '✗ NO SE CUMPLE'}\n"]

        p2 = verificar_propiedad_inversa_del_producto(A_f, B_f)
        lineas += [f"2. {p2.nombre} [{p2.formula}]:", f"   {p2.explicacion}", f"   Estado: {'✓ SE CUMPLE IDENTICAMENTE' if p2.se_cumple else '✗ NO SE CUMPLE'}\n"]

        p3 = verificar_propiedad_inversa_de_traspuesta(A_f)
        lineas += [f"3. {p3.nombre} [{p3.formula}]:", f"   {p3.explicacion}", f"   Estado: {'✓ SE CUMPLE IDENTICAMENTE' if p3.se_cumple else '✗ NO SE CUMPLE'}\n"]

        p4 = verificar_propiedad_determinante_de_inversa(A_f)
        lineas += [f"4. {p4.nombre} [{p4.formula}]:", f"   {p4.lado_izquierdo_str}  vs  {p4.lado_derecho_str}", f"   Estado: {'✓ SE CUMPLE IDENTICAMENTE' if p4.se_cumple else '✗ NO SE CUMPLE'}\n"]

        lineas += ["5. Efectos de Operaciones Elementales de Fila en det(A):"]
        for p in verificar_propiedades_operaciones_fila_det(A_f):
            lineas += [f"   • {p.nombre} [{p.formula}]: {'✓ VERIFICADO' if p.se_cumple else '✗ DISCREPANCIA'}"]
        lineas += [""]

        p6 = verificar_propiedad_matriz_triangular(A_f)
        lineas += [f"6. {p6.nombre} [{p6.formula}]:", f"   {p6.lado_izquierdo_str}", f"   {p6.lado_derecho_str}", f"   Estado: {'✓ SE CUMPLE IDENTICAMENTE' if p6.se_cumple else '✗ NO SE CUMPLE'}\n"]

        lineas += ["═" * 70, "✓ Todas las propiedades evaluadas con exactitud racional.", "═" * 70]
        self._log_prop("\n".join(lineas), limpiar=True)


    def _log_prop(self, texto: str, limpiar: bool = False):
        self.txt_res_prop.configure(state="normal")
        if limpiar:
            self.txt_res_prop.delete("1.0", "end")
        self.txt_res_prop.insert("end", texto + "\n")
        self.txt_res_prop.configure(state="disabled")


    # =========================================================================
    # SUB-PESTAÑA 4: TRASPUESTA E INVERSA
    # =========================================================================
    def _setup_tab_inv(self):
        """Panel para calcular la traspuesta Aᵀ y la inversa A⁻¹ de una matriz."""
        tab = self.tab_inv
        tab.grid_columnconfigure(0, weight=0)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # --- Panel izquierdo: Entrada ---
        left = ctk.CTkFrame(tab, width=420, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left.grid_propagate(False)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            left, text="🔄 Traspuesta e Inversa de Matriz A",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#7c3aed", "#a78bfa")
        ).pack(anchor="w", padx=14, pady=(14, 4))

        # Dimensiones
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

        # Botones Generar / Ejemplo
        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=4)
        ctk.CTkButton(btn_row, text="Generar", width=80, command=self._generar_grid_inv).pack(side="left", padx=2)
        ctk.CTkButton(
            btn_row, text="🎲 Ejemplo", width=90, command=self._cargar_ejemplo_inv,
            fg_color=("#475569", "#374151"), hover_color=("#334155", "#4b5563")
        ).pack(side="left", padx=4)

        # Grid de la matriz A
        self.scroll_inv = ctk.CTkScrollableFrame(left, height=200)
        self.scroll_inv.pack(fill="both", expand=True, padx=14, pady=4)
        self.entries_inv: List[List[ctk.CTkEntry]] = []
        self._generar_grid_inv()

        # Botones de operación
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

        # Nota
        ctk.CTkLabel(
            left,
            text="Nota: La inversa requiere matriz cuadrada n×n.",
            font=ctk.CTkFont(size=11), text_color=("gray50", "gray60")
        ).pack(anchor="w", padx=14, pady=(0, 8))

        # --- Panel derecho: Resultados ---
        right = ctk.CTkFrame(tab, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            right, text="📋 Procedimiento Paso a Paso",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=("#38bdf8", "#38bdf8")
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 6))

        self.txt_res_inv = ctk.CTkTextbox(right, font=ctk.CTkFont(family="Consolas", size=12), wrap="word")
        self.txt_res_inv.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.txt_res_inv.configure(state="disabled")

    def _generar_grid_inv(self):
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
        """Carga el ejemplo canónico de traspuesta/inversa 3×3."""
        self.entry_inv_n.delete(0, "end"); self.entry_inv_n.insert(0, "3")
        self.entry_inv_m.delete(0, "end"); self.entry_inv_m.insert(0, "3")
        self._generar_grid_inv()
        vals = [[1, 2, 0], [-1, 3, 2], [2, 0, -1]]
        for i, fila in enumerate(vals):
            for j, v in enumerate(fila):
                self.entries_inv[i][j].delete(0, "end")
                self.entries_inv[i][j].insert(0, str(v))

    def _leer_matriz_inv(self):
        """Lee la matriz A desde la grilla del tab Inversa."""
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
                    fila.append(Fraction(txt))
                except Exception:
                    try:
                        fila.append(Fraction(float(txt)))
                    except Exception:
                        raise ValueError(f"Valor inválido en A[{i+1},{j+1}]: '{txt}'")
            A.append(fila)
        return [[float(x) for x in fila] for fila in A]

    def _calc_traspuesta(self):
        self._ultimo_calc_inv = "traspuesta"
        modo = self.get_modo_numero()
        try:
            A = self._leer_matriz_inv()
        except ValueError as e:
            self._log_inv(f"❌ {e}", limpiar=True)
            return

        AT = trasponer_matriz(A)
        n_orig = len(A)
        m_orig = len(A[0])
        n_new  = len(AT)
        m_new  = len(AT[0])

        def fmt_mat(mat, rows, cols):
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
        from modulos.modulo_matrices import crear_matriz, analizar_transposicion_matriz
        A_f = crear_matriz(A); AT_f = crear_matriz(AT)
        lineas.append("\n" + "\n".join(analizar_transposicion_matriz(A_f, AT_f)))
        self._log_inv("\n".join(lineas), limpiar=True)

    def _calc_inversa(self):
        self._ultimo_calc_inv = "inversa"
        modo = self.get_modo_numero()
        try:
            A = self._leer_matriz_inv()
        except ValueError as e:
            self._log_inv(f"❌ {e}", limpiar=True)
            return

        n = len(A)
        if n != len(A[0]):
            self._log_inv("❌ La inversa solo está definida para matrices cuadradas (n×n).", limpiar=True)
            return

        try:
            res = invertir_matriz(A, modo=modo)
        except ValueError as e:
            self._log_inv(f"❌ {e}", limpiar=True)
            return

        lineas = ["═" * 60, "  INVERSA DE MATRIZ  A⁻¹  (Gauss-Jordan)", "═" * 60, ""]
        lineas += res.pasos
        lineas += ["", res.explicacion, "", "═" * 60]

        if res.es_invertible and res.matriz_inversa:
            def fmt_mat(mat):
                lines = []
                for fila in mat:
                    row_str = "  ".join(f"{formatear_numero(x, modo):>10}" for x in fila)
                    lines.append(f"  [ {row_str} ]")
                return "\n".join(lines)
            lineas += ["", f"  A⁻¹  ({n} × {n}):", fmt_mat(res.matriz_inversa)]

            # Comprobación automática obligatoria: A · A⁻¹ = I
            from modulos.modulo_matrices import crear_matriz, multiplicar_matrices, matriz_identidad, son_matrices_iguales, matriz_a_cadena
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

        self._log_inv("\n".join(lineas), limpiar=True)

    def _calc_inversa_adjunta(self):
        """Calcula la matriz inversa A⁻¹ mediante la fórmula de la matriz adjunta."""
        self._ultimo_calc_inv = "inversa_adjunta"
        modo = self.get_modo_numero()
        try:
            A = self._leer_matriz_inv()
        except ValueError as e:
            self._log_inv(f"❌ {e}", limpiar=True)
            return

        n = len(A)
        if n != len(A[0]):
            self._log_inv("❌ La inversa solo está definida para matrices cuadradas (n×n).", limpiar=True)
            return

        from modulos.modulo_matrices import crear_matriz, inversa_adjunta, matriz_a_cadena
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
        self._log_inv("\n".join(lineas), limpiar=True)

    def _log_inv(self, texto: str, limpiar: bool = False):
        self.txt_res_inv.configure(state="normal")
        if limpiar:
            self.txt_res_inv.delete("1.0", "end")
        self.txt_res_inv.insert("end", texto + "\n")
        self.txt_res_inv.configure(state="disabled")


    # =========================================================================
    # SUB-PESTAÑA 5: DETERMINANTES
    # =========================================================================
    def _setup_tab_det(self):
        """Panel para calcular el determinante det(A) paso a paso."""
        tab = self.tab_det
        tab.grid_columnconfigure(0, weight=0)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # --- Panel izquierdo: Entrada ---
        left = ctk.CTkFrame(tab, width=420, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left.grid_propagate(False)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            left, text="📊 Determinante de Matriz Cuadrada A",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#ea580c", "#fb923c")
        ).pack(anchor="w", padx=14, pady=(14, 4))

        # Dimensión n×n
        dim_frame = ctk.CTkFrame(left, fg_color="transparent")
        dim_frame.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(dim_frame, text="Orden n (n×n):").pack(side="left")
        self.entry_det_n = ctk.CTkEntry(dim_frame, width=52, justify="center")
        self.entry_det_n.pack(side="left", padx=(4, 0))
        self.entry_det_n.insert(0, "3")

        # Botones Generar / Ejemplo
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

        # Grid de la matriz A
        self.scroll_det = ctk.CTkScrollableFrame(left, height=220)
        self.scroll_det.pack(fill="both", expand=True, padx=14, pady=4)
        self.entries_det: List[List[ctk.CTkEntry]] = []
        self._generar_grid_det()

        # Botones de cálculo de determinante
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

        # --- Panel derecho: Resultados ---
        right = ctk.CTkFrame(tab, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            right, text="📋 Procedimiento Paso a Paso",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=("#38bdf8", "#38bdf8")
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 6))

        self.txt_res_det = ctk.CTkTextbox(right, font=ctk.CTkFont(family="Consolas", size=12), wrap="word")
        self.txt_res_det.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.txt_res_det.configure(state="disabled")

    def _generar_grid_det(self):
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
        """Ejemplo 3×3 con det = -14."""
        self.entry_det_n.delete(0, "end"); self.entry_det_n.insert(0, "3")
        self._generar_grid_det()
        vals = [[1, 2, 3], [4, 5, 6], [7, 2, 9]]
        for i, fila in enumerate(vals):
            for j, v in enumerate(fila):
                self.entries_det[i][j].delete(0, "end")
                self.entries_det[i][j].insert(0, str(v))

    def _cargar_ejemplo_det_2x2(self):
        """Ejemplo 2×2: A = [[3,-2],[4,1]] → det = 11."""
        self.entry_det_n.delete(0, "end"); self.entry_det_n.insert(0, "2")
        self._generar_grid_det()
        vals = [[3, -2], [4, 1]]
        for i, fila in enumerate(vals):
            for j, v in enumerate(fila):
                self.entries_det[i][j].delete(0, "end")
                self.entries_det[i][j].insert(0, str(v))

    def _leer_matriz_det(self):
        """Lee la matriz cuadrada desde la grilla del tab Determinante."""
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
        self._ultimo_calc_det = "determinante"
        modo = self.get_modo_numero()
        try:
            A = self._leer_matriz_det()
        except ValueError as e:
            self._log_det(f"❌ {e}", limpiar=True)
            return

        try:
            res = calcular_determinante(A, modo=modo)
        except ValueError as e:
            self._log_det(f"❌ {e}", limpiar=True)
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

        veredicto = "✅ La matriz ES INVERTIBLE  (det ≠ 0)" if res.es_invertible \
                    else "❌ La matriz NO ES INVERTIBLE  (det = 0, es singular)"
        lineas += ["", veredicto]

        self._log_det("\n".join(lineas), limpiar=True)

    def _log_det(self, texto: str, limpiar: bool = False):
        self.txt_res_det.configure(state="normal")
        if limpiar:
            self.txt_res_det.delete("1.0", "end")
        self.txt_res_det.insert("end", texto + "\n")
        self.txt_res_det.configure(state="disabled")

    def _calc_det_cofactores(self):
        """Calcula el determinante mediante expansión por cofactores (Laplace)."""
        self._ultimo_calc_det = "cofactores"
        modo = self.get_modo_numero()
        try:
            A = self._leer_matriz_det()
        except ValueError as e:
            self._log_det(f"❌ {e}", limpiar=True)
            return

        from modulos.modulo_matrices import crear_matriz, determinante_cofactores
        A_f = crear_matriz(A)
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
        self._log_det("\n".join(lineas), limpiar=True)

    def _calc_det_sarrus(self):
        """Calcula el determinante para matriz 3×3 mediante la regla de Sarrus."""
        self._ultimo_calc_det = "sarrus"
        modo = self.get_modo_numero()
        try:
            A = self._leer_matriz_det()
        except ValueError as e:
            self._log_det(f"❌ {e}", limpiar=True)
            return

        if len(A) != 3 or len(A[0]) != 3:
            self._log_det("❌ La Regla de Sarrus es aplicable exclusivamente a matrices de 3×3.", limpiar=True)
            return

        from modulos.modulo_matrices import crear_matriz, determinante_sarrus
        A_f = crear_matriz(A)
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
        self._log_det("\n".join(lineas), limpiar=True)


