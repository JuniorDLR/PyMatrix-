import re

with open("src/ui/matrix_ops_view.py", "r", encoding="utf-8") as f:
    content = f.read()

old_calc_det = """    def _calc_propiedad_tarea5_det(self, prop_id: str):
        \"\"\"Verifica una de las propiedades de Determinante de la Tarea 5.\"\"\"
        self._ultimo_calc_det = f"tarea5_{prop_id}"
        try:
            A = self._leer_matriz_det()
        except ValueError as e:
            self._log_det(f"❌ Error al leer datos: {e}", limpiar=True)
            return

        nA = len(A)
        try:
            from fractions import Fraction
            from src.core.exact_math import (
                crear_matriz, verificar_propiedad_determinante_de_inversa, 
                verificar_propiedades_operaciones_fila_det,
                verificar_propiedad_matriz_triangular, matriz_a_cadena
            )
            A_f = crear_matriz(A)
            
            lineas = [
                "═" * 70,
                f"Matriz A ({nA}×{nA}):",
                matriz_a_cadena(A_f),
                "─" * 70,
                ""
            ]

            if prop_id == "det_inv":
                p = verificar_propiedad_determinante_de_inversa(A_f)
                lineas += [f"Propiedad 1: {p.nombre} [{p.formula}]", f"Explicación:\\n{p.explicacion}", f"\\nEstado: {'✓ SE CUMPLE' if p.se_cumple else '✗ NO SE CUMPLE'}"]
                
            elif prop_id == "det_ops":
                ps = verificar_propiedades_operaciones_fila_det(A_f)
                lineas.append("Propiedades de Operaciones Elementales de Fila:")
                for i, p in enumerate(ps, 1):
                    lineas += [f"\\n[{i}] {p.nombre} [{p.formula}]", f"Explicación:\\n{p.explicacion}", f"Estado: {'✓ SE CUMPLE' if p.se_cumple else '✗ NO SE CUMPLE'}"]

            elif prop_id == "det_tri":
                p = verificar_propiedad_matriz_triangular(A_f)
                lineas += [f"Propiedad: {p.nombre} [{p.formula}]", f"Explicación:\\n{p.explicacion}", f"\\nEstado: {'✓ SE CUMPLE' if p.se_cumple else '✗ NO SE CUMPLE'}"]

            lineas.append("═" * 70)
            self._log_det("\\n".join(lineas), limpiar=True)
            
        except Exception as e:
            self._log_det(f"❌ Ocurrió un error inesperado al procesar las propiedades:\\n{e}", limpiar=True)"""


new_calc_det = """    def _calc_propiedad_tarea5_det(self, prop_id: str):
        \"\"\"Verifica propiedades de Determinantes mostrando TODO el paso a paso matemático.\"\"\"
        self._ultimo_calc_det = f"tarea5_{prop_id}"
        try:
            A = self._leer_matriz_det()
        except ValueError as e:
            self._log_det(f"❌ Error al leer datos: {e}\\n" + "-"*40, limpiar=False)
            return

        nA = len(A)
        modo = self.get_modo_numero()
        from src.core.exact_math import crear_matriz, inversa_gauss_jordan, determinante_triangulacion, determinante_sarrus
        from src.core.domain import formatear_numero
        
        A_f = crear_matriz(A)
        lineas = ["\\n" + "═" * 60]

        try:
            if prop_id == "det_inv":
                lineas.append(">> PROPIEDAD: Determinante de la Inversa  det(A⁻¹) = 1 / det(A)")
                lineas.append("═" * 60)
                lineas.append(f"\\nMatriz Original A ({nA}×{nA}):\\n{self._fmt_mat(A, modo)}")
                
                lineas.append("\\n--- PASO 1: Calcular Determinante de A ---")
                det_A, _ = determinante_triangulacion(A_f)
                if det_A == 0:
                    lineas.append("❌ El determinante de A es 0. La matriz no tiene inversa. Propiedad no evaluable.")
                    self._log_det("\\n".join(lineas), limpiar=False)
                    return
                lineas.append(f"det(A) = {det_A}")
                
                lineas.append("\\n--- PASO 2: Calcular 1 / det(A) ---")
                val_esperado = 1 / det_A
                lineas.append(f"1 / det(A) = {val_esperado}")
                
                lineas.append("\\n--- PASO 3: Calcular la Matriz Inversa (A⁻¹) ---")
                res_A = inversa_gauss_jordan(A_f)
                A_inv = res_A.matriz_inversa
                from src.core.domain import desencapsular_matriz
                lineas.append(f"Matriz A⁻¹:\\n{self._fmt_mat(desencapsular_matriz(A_inv), modo)}")
                
                lineas.append("\\n--- PASO 4: Calcular Determinante de A⁻¹ ---")
                det_A_inv, _ = determinante_triangulacion(A_inv)
                lineas.append(f"det(A⁻¹) = {det_A_inv}")
                
                lineas.append("\\n--- CONCLUSIÓN ---")
                if det_A_inv == val_esperado:
                    lineas.append("✅ det(A⁻¹) es IDÉNTICO a 1/det(A).")
                else:
                    lineas.append("❌ Los valores no coinciden.")
                lineas.append("═" * 60)

            elif prop_id == "det_ops":
                lineas.append(">> PROPIEDADES: Operaciones Elementales y Determinantes")
                lineas.append("═" * 60)
                lineas.append(f"\\nMatriz Original A ({nA}×{nA}):\\n{self._fmt_mat(A, modo)}")
                det_A, _ = determinante_triangulacion(A_f)
                lineas.append(f"det(A) original = {det_A}\\n")
                
                lineas.append("--- PROPIEDAD A: Intercambio de Filas det(B) = -det(A) ---")
                if nA >= 2:
                    B_f = [row[:] for row in A_f]
                    B_f[0], B_f[1] = B_f[1], B_f[0]
                    det_B, _ = determinante_triangulacion(B_f)
                    from src.core.domain import desencapsular_matriz
                    lineas.append("Intercambiamos Fila 1 y Fila 2 de A para obtener B:")
                    lineas.append(f"{self._fmt_mat(desencapsular_matriz(B_f), modo)}")
                    lineas.append(f"det(B) = {det_B}")
                    if det_B == -det_A:
                        lineas.append("✅ Se cumple: det(B) = -det(A)")
                else:
                    lineas.append("⚠️ Se requieren al menos 2 filas.")

                lineas.append("\\n--- PROPIEDAD B: Multiplicación de Fila por Escalar k det(C) = k·det(A) ---")
                k = 3
                C_f = [row[:] for row in A_f]
                C_f[0] = [x * k for x in C_f[0]]
                det_C, _ = determinante_triangulacion(C_f)
                lineas.append(f"Multiplicamos Fila 1 por k={k} para obtener C:")
                lineas.append(f"{self._fmt_mat(desencapsular_matriz(C_f), modo)}")
                lineas.append(f"det(C) = {det_C}")
                if det_C == k * det_A:
                    lineas.append(f"✅ Se cumple: det(C) = {k} * det(A) = {k * det_A}")

                lineas.append("═" * 60)

            elif prop_id == "det_tri":
                lineas.append(">> PROPIEDAD: Determinante de Matriz Triangular")
                lineas.append("═" * 60)
                lineas.append(f"\\nMatriz Original A ({nA}×{nA}):\\n{self._fmt_mat(A, modo)}")
                
                # Revisar si ya es triangular
                es_triangular_sup = all(A_f[i][j] == 0 for i in range(nA) for j in range(nA) if i > j)
                es_triangular_inf = all(A_f[i][j] == 0 for i in range(nA) for j in range(nA) if i < j)
                
                if es_triangular_sup or es_triangular_inf:
                    lineas.append("La matriz ya es triangular.")
                else:
                    lineas.append("La matriz original NO es triangular. El determinante de una triangular se calcula multiplicando su diagonal principal.")
                
                diag_prod = 1
                for i in range(nA):
                    diag_prod *= A_f[i][i]
                lineas.append(f"Producto de la diagonal principal: {diag_prod}")
                det_A, _ = determinante_triangulacion(A_f)
                lineas.append(f"Determinante real det(A) = {det_A}")
                if es_triangular_inf or es_triangular_sup:
                    if det_A == diag_prod:
                        lineas.append("✅ Se cumple: det(A) es igual al producto de su diagonal.")
                else:
                    lineas.append("⚠️ Solo se cumple si la matriz es triangular.")
                
                lineas.append("═" * 60)

            self._log_det("\\n".join(lineas), limpiar=False)
            
        except Exception as e:
            self._log_det(f"❌ Error al procesar: {e}", limpiar=False)"""

content = content.replace(old_calc_det, new_calc_det)

# While we're at it, replace limpiar=True with limpiar=False in ALL _log_inv and _log_det functions across the view.
content = content.replace("self._log_inv(f\"❌ Error al leer datos: {e}\", limpiar=True)", "self._log_inv(f\"❌ Error al leer datos: {e}\\n\" + \"-\"*40, limpiar=False)")
content = content.replace("self._log_det(f\"❌ Error al leer datos: {e}\", limpiar=True)", "self._log_det(f\"❌ Error al leer datos: {e}\\n\" + \"-\"*40, limpiar=False)")

# Ensure textboxes are cleared manually, let's look if we have the clear button.
# There is no clear button for Inv and Det tabs. We should add one.

with open("src/ui/matrix_ops_view.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied to _calc_propiedad_tarea5_det")
