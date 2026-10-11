import re

with open("src/ui/matrix_ops_view.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace _calc_propiedad_tarea5_inv to show step-by-step

old_calc_inv = """    def _calc_propiedad_tarea5_inv(self, prop_id: str):
        \"\"\"Verifica una de las propiedades de Inversa de la Tarea 5.\"\"\"
        self._ultimo_calc_inv = f"tarea5_{prop_id}"
        try:
            A = self._leer_matriz_inv()
        except ValueError as e:
            self._log_inv(f"❌ Error al leer datos: {e}", limpiar=True)
            return

        mA, nA = len(A), len(A[0])
        if mA != nA:
            self._log_inv(
                "❌ Para verificar esta propiedad, la matriz A debe ser cuadrada (n × n).\\n"
                f"   Actualmente A es de dimensión {mA} × {nA}.\\n",
                limpiar=True
            )
            return

        try:
            from fractions import Fraction
            from src.core.exact_math import (
                crear_matriz, verificar_propiedad_inversa_de_inversa,
                verificar_propiedad_inversa_del_producto, verificar_propiedad_inversa_de_traspuesta,
                matriz_a_cadena
            )

            A_f = crear_matriz(A)
            
            lineas = [
                "═" * 70,
                f"Matriz A ({nA}×{nA}):",
                matriz_a_cadena(A_f),
                "─" * 70,
                ""
            ]

            if prop_id == "inv_inv":
                p = verificar_propiedad_inversa_de_inversa(A_f)
                lineas += [f"Propiedad 1: {p.nombre} [{p.formula}]", f"Explicación:\\n{p.explicacion}", f"\\nEstado: {'✓ SE CUMPLE' if p.se_cumple else '✗ NO SE CUMPLE'}"]

            elif prop_id == "inv_prod":
                # Como no leemos vectores en esta pestaña, creamos una B_f estándar invertible
                B_f = [[Fraction(1 if i == j else 2, 1) for j in range(nA)] for i in range(nA)]
                lineas.insert(4, f"Matriz B Auxiliar ({nA}×{nA}):")
                lineas.insert(5, matriz_a_cadena(B_f))
                
                p = verificar_propiedad_inversa_del_producto(A_f, B_f)
                lineas += [f"Propiedad 2: {p.nombre} [{p.formula}]", f"Explicación:\\n{p.explicacion}", f"\\nEstado: {'✓ SE CUMPLE' if p.se_cumple else '✗ NO SE CUMPLE'}"]

            elif prop_id == "inv_tras":
                p = verificar_propiedad_inversa_de_traspuesta(A_f)
                lineas += [f"Propiedad 3: {p.nombre} [{p.formula}]", f"Explicación:\\n{p.explicacion}", f"\\nEstado: {'✓ SE CUMPLE' if p.se_cumple else '✗ NO SE CUMPLE'}"]

            lineas.append("═" * 70)
            self._log_inv("\\n".join(lineas), limpiar=True)

        except Exception as e:
            self._log_inv(f"❌ Ocurrió un error inesperado al procesar las propiedades:\\n{e}", limpiar=True)"""

new_calc_inv = """    def _calc_propiedad_tarea5_inv(self, prop_id: str):
        \"\"\"Verifica propiedades de Inversa mostrando TODO el paso a paso matemático.\"\"\"
        self._ultimo_calc_inv = f"tarea5_{prop_id}"
        try:
            A = self._leer_matriz_inv()
        except ValueError as e:
            self._log_inv(f"❌ Error al leer datos: {e}\\n" + "-"*40, limpiar=False)
            return

        mA, nA = len(A), len(A[0])
        if mA != nA:
            self._log_inv("❌ Para verificar esta propiedad, la matriz A debe ser cuadrada.\\n" + "-"*40, limpiar=False)
            return

        modo = self.get_modo_numero()
        from src.core.exact_math import crear_matriz, inversa_gauss_jordan, trasponer_matriz, son_matrices_iguales
        from src.core.domain import desencapsular_matriz
        
        A_f = crear_matriz(A)
        lineas = ["\\n" + "═" * 60]

        try:
            if prop_id == "inv_inv":
                lineas.append(">> PROPIEDAD: Inversa de la Inversa  (A⁻¹)⁻¹ = A")
                lineas.append("═" * 60)
                lineas.append(f"\\nMatriz Original A ({nA}×{nA}):\\n{self._fmt_mat(A, modo)}")
                
                lineas.append("\\n--- PASO 1: Calcular la Inversa de A (A⁻¹) ---")
                res_A = inversa_gauss_jordan(A_f)
                if not res_A.es_invertible:
                    lineas.append("❌ La matriz A no es invertible (determinante = 0). Propiedad no aplicable.")
                    self._log_inv("\\n".join(lineas), limpiar=False)
                    return
                A_inv = res_A.matriz_inversa
                lineas.append(f"Matriz A⁻¹ calculada:\\n{self._fmt_mat(desencapsular_matriz(A_inv), modo)}")
                
                lineas.append("\\n--- PASO 2: Calcular la Inversa de la matriz obtenida (A⁻¹)⁻¹ ---")
                res_A_inv = inversa_gauss_jordan(A_inv)
                A_inv_inv = res_A_inv.matriz_inversa
                lineas.append(f"Matriz resultante (A⁻¹)⁻¹:\\n{self._fmt_mat(desencapsular_matriz(A_inv_inv), modo)}")
                
                lineas.append("\\n--- CONCLUSIÓN ---")
                if son_matrices_iguales(A_f, A_inv_inv):
                    lineas.append("✅ La matriz (A⁻¹)⁻¹ es IDÉNTICA a la Matriz Original A.")
                else:
                    lineas.append("❌ Las matrices no coinciden.")
                lineas.append("═" * 60)

            elif prop_id == "inv_prod":
                lineas.append(">> INFO: Esta propiedad fue movida a la pestaña 'Operaciones con Matrices'.")
                
            elif prop_id == "inv_tras":
                lineas.append(">> PROPIEDAD: Inversa de la Traspuesta  (Aᵀ)⁻¹ = (A⁻¹)ᵀ")
                lineas.append("═" * 60)
                lineas.append(f"\\nMatriz Original A ({nA}×{nA}):\\n{self._fmt_mat(A, modo)}")
                
                lineas.append("\\n--- PASO 1: Calcular la Traspuesta de A (Aᵀ) ---")
                A_t = trasponer_matriz(A_f)
                lineas.append(f"Matriz Aᵀ:\\n{self._fmt_mat(desencapsular_matriz(A_t), modo)}")
                
                lineas.append("\\n--- PASO 2: Calcular la Inversa de (Aᵀ) ---")
                res_At = inversa_gauss_jordan(A_t)
                if not res_At.es_invertible:
                    lineas.append("❌ La matriz no es invertible. Propiedad no aplicable.")
                    self._log_inv("\\n".join(lineas), limpiar=False)
                    return
                lado_izq = res_At.matriz_inversa
                lineas.append(f"Matriz (Aᵀ)⁻¹:\\n{self._fmt_mat(desencapsular_matriz(lado_izq), modo)}")
                
                lineas.append("\\n--- PASO 3: Calcular la Inversa de A (A⁻¹) ---")
                res_A = inversa_gauss_jordan(A_f)
                A_inv = res_A.matriz_inversa
                lineas.append(f"Matriz A⁻¹:\\n{self._fmt_mat(desencapsular_matriz(A_inv), modo)}")
                
                lineas.append("\\n--- PASO 4: Calcular la Traspuesta de A⁻¹ ---")
                lado_der = trasponer_matriz(A_inv)
                lineas.append(f"Matriz (A⁻¹)ᵀ:\\n{self._fmt_mat(desencapsular_matriz(lado_der), modo)}")
                
                lineas.append("\\n--- CONCLUSIÓN ---")
                if son_matrices_iguales(lado_izq, lado_der):
                    lineas.append("✅ La matriz (Aᵀ)⁻¹ es IDÉNTICA a la matriz (A⁻¹)ᵀ.")
                else:
                    lineas.append("❌ Las matrices no coinciden.")
                lineas.append("═" * 60)

            self._log_inv("\\n".join(lineas), limpiar=False)

        except Exception as e:
            self._log_inv(f"❌ Error al procesar: {e}", limpiar=False)"""

content = content.replace(old_calc_inv, new_calc_inv)

with open("src/ui/matrix_ops_view.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied to _calc_propiedad_tarea5_inv")
