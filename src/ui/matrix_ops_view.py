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
    ResultadoMultiplicacionMatricial, ResultadoProductoMatrizVector, ResultadoEcuacionMatricial
)

from src.core.vectors import Vector
from src.core.domain import Matriz, formatear_numero, a_subindice


class MatrixOpsView(ctk.CTkFrame):
    """Panel principal para operaciones matriciales y ecuaciones Ax = b."""

    def __init__(self, master, get_modo_numero_cb, **kwargs):
        super().__init__(master, **kwargs)
        self.get_modo_numero = get_modo_numero_cb

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._setup_ui()

    def _setup_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.tab_ops = self.tabview.add("  ➕➖✖️ Operaciones con Matrices  ")
        self.tab_axb = self.tabview.add("  📐 Ax = b (Ecuación Matricial)  ")

        self._setup_tab_ops()
        self._setup_tab_axb()

    def refresh_format(self):
        """Refresca salidas cuando cambia el formato global."""
        pass

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

            elif op in ("resta", "resta_AB"):
                R = restar_matrices(A, B)
                lineas.append(">> RESTA DE MATRICES: A − B")
                lineas.append(f"Condición de Dimensión: Ambas matrices deben ser del mismo orden (m × n).")
                lineas.append(f"  Dimensión de A: {mA}×{nA}  |  Dimensión de B: {mB}×{nB}  → {'✓ Mismas dimensiones' if (mA==mB and nA==nB) else '✗ Incompatibles'}")
                lineas.append(f"\nA ({mA}×{nA}):\n{self._fmt_mat(A, modo)}")
                lineas.append(f"B ({mB}×{nB}):\n{self._fmt_mat(B, modo)}")
                lineas.append("Procedimiento: C_ij = A_ij − B_ij para cada posición.")
                lineas.append(f"\nResultado C = A − B ({mA}×{nA}):\n{self._fmt_mat(R, modo)}")

            elif op in ("escalar", "esc_A"):
                R = multiplicar_matriz_escalar(c, A)
                lineas.append(f">> MULTIPLICACIÓN DE MATRIZ POR UN ESCALAR: {c_fmt} · A")
                lineas.append(f"\nEscalar c = {c_fmt}")
                lineas.append(f"Matriz A ({mA}×{nA}):\n{self._fmt_mat(A, modo)}")
                lineas.append("Procedimiento: (c·A)_ij = c · A_ij entrada por entrada.")
                lineas.append(f"\nResultado {c_fmt}·A ({mA}×{nA}):\n{self._fmt_mat(R, modo)}")

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
