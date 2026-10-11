import re

with open("src/ui/matrix_ops_view.py", "r", encoding="utf-8") as f:
    content = f.read()

# We need to rewrite _calc_op to:
# 1. NOT use limpiar=True
# 2. Add visual separators in the text log
# 3. Call _mostrar_resultado_ranura

old_calc_op = """    def _calc_op(self, op: str):
        \"\"\"Ejecuta la operación `op` (suma, resta, escalar o multiplicación) y muestra su procedimiento.\"\"\"
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
                lineas.append(f"\\nA ({mA}×{nA}):\\n{self._fmt_mat(A, modo)}")
                lineas.append(f"B ({mB}×{nB}):\\n{self._fmt_mat(B, modo)}")
                lineas.append("Procedimiento: C_ij = A_ij + B_ij para cada posición.")
                lineas.append(f"\\nResultado C = A + B ({mA}×{nA}):\\n{self._fmt_mat(R, modo)}")
                # El análisis extra usa fracciones exactas (crear_matriz) para evitar errores de redondeo
                from src.core.exact_math import crear_matriz, analizar_suma_matrices
                A_f = crear_matriz(A); B_f = crear_matriz(B); R_f = crear_matriz(R)
                lineas.append("\\n" + "\\n".join(analizar_suma_matrices(A_f, B_f, R_f)))

            elif op in ("resta", "resta_AB"):
                R = restar_matrices(A, B)
                lineas.append(">> RESTA DE MATRICES: A − B")
                lineas.append(f"Condición de Dimensión: Ambas matrices deben ser del mismo orden (m × n).")
                lineas.append(f"  Dimensión de A: {mA}×{nA}  |  Dimensión de B: {mB}×{nB}  → {'✓ Mismas dimensiones' if (mA==mB and nA==nB) else '✗ Incompatibles'}")
                lineas.append(f"\\nA ({mA}×{nA}):\\n{self._fmt_mat(A, modo)}")
                lineas.append(f"B ({mB}×{nB}):\\n{self._fmt_mat(B, modo)}")
                lineas.append("Procedimiento: C_ij = A_ij − B_ij para cada posición.")
                lineas.append(f"\\nResultado C = A − B ({mA}×{nA}):\\n{self._fmt_mat(R, modo)}")
                from src.core.exact_math import crear_matriz, analizar_resta_matrices
                A_f = crear_matriz(A); B_f = crear_matriz(B); R_f = crear_matriz(R)
                lineas.append("\\n" + "\\n".join(analizar_resta_matrices(A_f, B_f, R_f)))

            elif op in ("escalar", "esc_A"):
                R = multiplicar_matriz_escalar(c, A)
                lineas.append(f">> MULTIPLICACIÓN DE MATRIZ POR UN ESCALAR: {c_fmt} · A")
                lineas.append(f"\\nEscalar c = {c_fmt}")
                lineas.append(f"Matriz A ({mA}×{nA}):\\n{self._fmt_mat(A, modo)}")
                lineas.append("Procedimiento: (c·A)_ij = c · A_ij entrada por entrada.")
                lineas.append(f"\\nResultado {c_fmt}·A ({mA}×{nA}):\\n{self._fmt_mat(R, modo)}")
                from src.core.exact_math import crear_matriz, parsear_fraccion, analizar_escalar_matriz
                A_f = crear_matriz(A); R_f = crear_matriz(R); c_f = parsear_fraccion(c)
                lineas.append("\\n" + "\\n".join(analizar_escalar_matriz(c_f, A_f, R_f)))

            elif op in ("multiplicacion", "prod_AB"):
                res = multiplicar_matrices(A, B, modo=modo)
                mR, pR = res.dimensiones_resultado
                lineas.append(">> MULTIPLICACIÓN DE MATRICES: A × B")
                lineas.append(f"Condición de Compatibilidad: Columnas de A = Filas de B")
                lineas.append(f"  A es {mA}×{nA} (columnas = {nA})")
                lineas.append(f"  B es {mB}×{nB} (filas = {mB})")
                lineas.append(f"  Validación: {nA} == {mB} → {'✓ Compatible (columnas de A coinciden con filas de B)' if nA == mB else '✗ Incompatible'}")
                lineas.append(f"\\nA ({mA}×{nA}):\\n{self._fmt_mat(A, modo)}")
                lineas.append(f"B ({mB}×{nB}):\\n{self._fmt_mat(B, modo)}")
                lineas.append("\\nProcedimiento — Bucles anidados:")
                lineas.append("  c_ij = Σ A_ik · B_kj  (suma de productos fila de A por columna de B)\\n")
                for paso in res.desglose_pasos:
                    lineas.append(f"  {paso}")
                lineas.append(f"\\nResultado C = A × B ({mR}×{pR}):\\n{self._fmt_mat(res.matriz_resultado, modo)}")
                from src.core.exact_math import crear_matriz, analizar_producto_matricial
                A_f = crear_matriz(A); B_f = crear_matriz(B); C_f = crear_matriz(res.matriz_resultado)
                lineas.append("\\n" + "\\n".join(analizar_producto_matricial(A_f, B_f, C_f)))

            elif op == "traspuesta_A":
                R = trasponer_matriz(A)
                lineas.append(">> TRASPUESTA DE MATRIZ: Aᵀ")
                lineas.append("Condición: Ninguna restricción de orden (aplica a cualquier matriz m × n).")
                lineas.append(f"Definición: (Aᵀ)_ij = A_ji (intercambio de filas por columnas).")
                lineas.append(f"  Dimensión original de A: {mA}×{nA}")
                lineas.append(f"  Dimensión resultante de Aᵀ: {nA}×{mA}")
                lineas.append(f"\\nMatriz A ({mA}×{nA}):\\n{self._fmt_mat(A, modo)}")
                lineas.append(f"Resultado Aᵀ ({nA}×{mA}):\\n{self._fmt_mat(R, modo)}")
                from src.core.exact_math import crear_matriz, analizar_transposicion_matriz
                A_f = crear_matriz(A); R_f = crear_matriz(R)
                lineas.append("\\n" + "\\n".join(analizar_transposicion_matriz(A_f, R_f)))

            elif op == "traspuesta_B":
                R = trasponer_matriz(B)
                lineas.append(">> TRASPUESTA DE MATRIZ: Bᵀ")
                lineas.append("Condición: Ninguna restricción de orden (aplica a cualquier matriz m × n).")
                lineas.append(f"Definición: (Bᵀ)_ij = B_ji (intercambio de filas por columnas).")
                lineas.append(f"  Dimensión original de B: {mB}×{nB}")
                lineas.append(f"  Dimensión resultante de Bᵀ: {nB}×{mB}")
                lineas.append(f"\\nMatriz B ({mB}×{nB}):\\n{self._fmt_mat(B, modo)}")
                lineas.append(f"Resultado Bᵀ ({nB}×{mB}):\\n{self._fmt_mat(R, modo)}")
                from src.core.exact_math import crear_matriz, analizar_transposicion_matriz
                B_f = crear_matriz(B); R_f = crear_matriz(R)
                lineas.append("\\n" + "\\n".join(analizar_transposicion_matriz(B_f, R_f)))

        except ValueError as e:
            lineas = [
                "═" * 60,
                "  ❌ VALIDACIÓN PREVIA FALLIDA (CONDICIÓN OBLIGATORIA NO CUMPLIDA)",
                "═" * 60,
                f"\\n{e}\\n",
                "═" * 60
            ]

        self._log_ops("\\n".join(lineas), limpiar=True)"""


new_calc_op = """    def _calc_op(self, op: str):
        \"\"\"Ejecuta la operación `op` (suma, resta, escalar o multiplicación) y muestra su procedimiento.\"\"\"
        self._ultimo_calc_ops = op
        modo = self.get_modo_numero()
        try:
            A = self._leer_matriz_entries(self.entries_A)
            B = self._leer_matriz_entries(self.entries_B)
            c_str = self.entry_ops_c.get().strip() if hasattr(self, "entry_ops_c") else "2"
            c = float(c_str) if "/" not in c_str else float(c_str.split("/")[0]) / float(c_str.split("/")[1])
        except ValueError as e:
            self._log_ops(f"❌ Error de entrada: {e}\\n" + "-"*40, limpiar=False)
            return

        mA, nA = len(A), len(A[0])
        mB, nB = len(B), len(B[0])
        c_fmt = formatear_numero(c, modo)
        lineas = ["\\n" + "═"*50]

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
                lineas.append(f"\\nA ({mA}×{nA}):\\n{self._fmt_mat(A, modo)}")
                lineas.append(f"B ({mB}×{nB}):\\n{self._fmt_mat(B, modo)}")
                lineas.append("Procedimiento: C_ij = A_ij + B_ij para cada posición.")
                lineas.append(f"\\nResultado C = A + B ({mA}×{nA}):\\n{self._fmt_mat(R, modo)}")
                from src.core.exact_math import crear_matriz, analizar_suma_matrices
                A_f = crear_matriz(A); B_f = crear_matriz(B); R_f = crear_matriz(R)
                lineas.append("\\n" + "\\n".join(analizar_suma_matrices(A_f, B_f, R_f)))

            elif op in ("resta", "resta_AB"):
                R = restar_matrices(A, B)
                ranura_target = "AB"; matriz_res = R; titulo_vis = "Resta A − B"
                lineas.append(">> RESTA DE MATRICES: A − B")
                lineas.append(f"Condición de Dimensión: Ambas matrices deben ser del mismo orden (m × n).")
                lineas.append(f"  Dimensión de A: {mA}×{nA}  |  Dimensión de B: {mB}×{nB}  → {'✓ Mismas dimensiones' if (mA==mB and nA==nB) else '✗ Incompatibles'}")
                lineas.append(f"\\nA ({mA}×{nA}):\\n{self._fmt_mat(A, modo)}")
                lineas.append(f"B ({mB}×{nB}):\\n{self._fmt_mat(B, modo)}")
                lineas.append("Procedimiento: C_ij = A_ij − B_ij para cada posición.")
                lineas.append(f"\\nResultado C = A − B ({mA}×{nA}):\\n{self._fmt_mat(R, modo)}")
                from src.core.exact_math import crear_matriz, analizar_resta_matrices
                A_f = crear_matriz(A); B_f = crear_matriz(B); R_f = crear_matriz(R)
                lineas.append("\\n" + "\\n".join(analizar_resta_matrices(A_f, B_f, R_f)))

            elif op in ("escalar", "esc_A"):
                R = multiplicar_matriz_escalar(c, A)
                ranura_target = "A"; matriz_res = R; titulo_vis = f"Escalar {c_fmt} · A"
                lineas.append(f">> MULTIPLICACIÓN DE MATRIZ POR UN ESCALAR: {c_fmt} · A")
                lineas.append(f"\\nEscalar c = {c_fmt}")
                lineas.append(f"Matriz A ({mA}×{nA}):\\n{self._fmt_mat(A, modo)}")
                lineas.append("Procedimiento: (c·A)_ij = c · A_ij entrada por entrada.")
                lineas.append(f"\\nResultado {c_fmt}·A ({mA}×{nA}):\\n{self._fmt_mat(R, modo)}")
                from src.core.exact_math import crear_matriz, parsear_fraccion, analizar_escalar_matriz
                A_f = crear_matriz(A); R_f = crear_matriz(R); c_f = parsear_fraccion(c)
                lineas.append("\\n" + "\\n".join(analizar_escalar_matriz(c_f, A_f, R_f)))

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
                lineas.append(f"\\nA ({mA}×{nA}):\\n{self._fmt_mat(A, modo)}")
                lineas.append(f"B ({mB}×{nB}):\\n{self._fmt_mat(B, modo)}")
                lineas.append("\\nProcedimiento — Bucles anidados:")
                lineas.append("  c_ij = Σ A_ik · B_kj  (suma de productos fila de A por columna de B)\\n")
                for paso in res.desglose_pasos:
                    lineas.append(f"  {paso}")
                lineas.append(f"\\nResultado C = A × B ({mR}×{pR}):\\n{self._fmt_mat(res.matriz_resultado, modo)}")
                from src.core.exact_math import crear_matriz, analizar_producto_matricial
                A_f = crear_matriz(A); B_f = crear_matriz(B); C_f = crear_matriz(res.matriz_resultado)
                lineas.append("\\n" + "\\n".join(analizar_producto_matricial(A_f, B_f, C_f)))

            elif op == "traspuesta_A":
                R = trasponer_matriz(A)
                ranura_target = "A"; matriz_res = R; titulo_vis = "Traspuesta Aᵀ"
                lineas.append(">> TRASPUESTA DE MATRIZ: Aᵀ")
                lineas.append("Condición: Ninguna restricción de orden (aplica a cualquier matriz m × n).")
                lineas.append(f"Definición: (Aᵀ)_ij = A_ji (intercambio de filas por columnas).")
                lineas.append(f"  Dimensión original de A: {mA}×{nA}")
                lineas.append(f"  Dimensión resultante de Aᵀ: {nA}×{mA}")
                lineas.append(f"\\nMatriz A ({mA}×{nA}):\\n{self._fmt_mat(A, modo)}")
                lineas.append(f"Resultado Aᵀ ({nA}×{mA}):\\n{self._fmt_mat(R, modo)}")
                from src.core.exact_math import crear_matriz, analizar_transposicion_matriz
                A_f = crear_matriz(A); R_f = crear_matriz(R)
                lineas.append("\\n" + "\\n".join(analizar_transposicion_matriz(A_f, R_f)))

            elif op == "traspuesta_B":
                R = trasponer_matriz(B)
                ranura_target = "B"; matriz_res = R; titulo_vis = "Traspuesta Bᵀ"
                lineas.append(">> TRASPUESTA DE MATRIZ: Bᵀ")
                lineas.append("Condición: Ninguna restricción de orden (aplica a cualquier matriz m × n).")
                lineas.append(f"Definición: (Bᵀ)_ij = B_ji (intercambio de filas por columnas).")
                lineas.append(f"  Dimensión original de B: {mB}×{nB}")
                lineas.append(f"  Dimensión resultante de Bᵀ: {nB}×{mB}")
                lineas.append(f"\\nMatriz B ({mB}×{nB}):\\n{self._fmt_mat(B, modo)}")
                lineas.append(f"Resultado Bᵀ ({nB}×{mB}):\\n{self._fmt_mat(R, modo)}")
                from src.core.exact_math import crear_matriz, analizar_transposicion_matriz
                B_f = crear_matriz(B); R_f = crear_matriz(R)
                lineas.append("\\n" + "\\n".join(analizar_transposicion_matriz(B_f, R_f)))

        except ValueError as e:
            lineas = [
                "  ❌ VALIDACIÓN PREVIA FALLIDA (CONDICIÓN OBLIGATORIA NO CUMPLIDA)",
                f"\\n{e}\\n"
            ]

        self._log_ops("\\n".join(lineas), limpiar=False)
        
        if ranura_target and matriz_res:
            self._mostrar_resultado_ranura(ranura_target, titulo_vis, matriz_res)
"""

content = content.replace(old_calc_op, new_calc_op)

# Next, we need to modify Property (AB)^-1 = B^-1 A^-1
# Currently it's in `_setup_tab_inv`. The user asked to move it to `_setup_tab_ops`.
# Let's see if we can do that in a separate patch.

with open("src/ui/matrix_ops_view.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied to _calc_op")
