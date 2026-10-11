import re

with open("src/ui/matrix_ops_view.py", "r", encoding="utf-8") as f:
    content = f.read()

method_to_add = """
    def _calc_prop_ab_inv(self):
        \"\"\"Comprueba y documenta paso a paso la propiedad (AB)⁻¹ = B⁻¹ A⁻¹.\"\"\"
        modo = self.get_modo_numero()
        try:
            A = self._leer_matriz_entries(self.entries_A)
            B = self._leer_matriz_entries(self.entries_B)
        except ValueError as e:
            self._log_ops(f"❌ Error de entrada: {e}\\n" + "-"*40, limpiar=False)
            return

        mA, nA = len(A), len(A[0])
        mB, nB = len(B), len(B[0])
        
        lineas = ["\\n" + "═"*50]
        lineas.append(">> PROPIEDAD: Inversa del Producto Matricial (AB)⁻¹ = B⁻¹A⁻¹")
        lineas.append("═"*50)
        
        if mA != nA or mB != nB or mA != mB:
            lineas.append("❌ CONDICIÓN FALLIDA: Ambas matrices deben ser cuadradas y del mismo orden para evaluar esta propiedad.")
            self._log_ops("\\n".join(lineas), limpiar=False)
            return
            
        from src.core.exact_math import crear_matriz, multiplicar_matrices, inversa_gauss_jordan, son_matrices_iguales
        
        A_f = crear_matriz(A)
        B_f = crear_matriz(B)
        
        lineas.append("\\n--- PASO 1: Calcular A × B ---")
        AB = multiplicar_matrices(A_f, B_f)
        from src.core.domain import desencapsular_matriz
        lineas.append(f"Matriz resultante AB ({mA}×{mA}):\\n{self._fmt_mat(desencapsular_matriz(AB), modo)}")
        
        lineas.append("\\n--- PASO 2: Calcular la Inversa de (A × B) ---")
        res_AB = inversa_gauss_jordan(AB)
        if not res_AB.es_invertible:
            lineas.append("❌ La matriz AB no es invertible (determinante 0). No se puede continuar la demostración.")
            self._log_ops("\\n".join(lineas), limpiar=False)
            return
            
        lado_izquierdo = res_AB.matriz_inversa
        lineas.append(f"Inversa calculada (AB)⁻¹:\\n{self._fmt_mat(desencapsular_matriz(lado_izquierdo), modo)}")
        
        lineas.append("\\n--- PASO 3: Calcular la Inversa de A y B por separado ---")
        res_A = inversa_gauss_jordan(A_f)
        res_B = inversa_gauss_jordan(B_f)
        
        if not res_A.es_invertible or not res_B.es_invertible:
            lineas.append("❌ Una de las matrices (A o B) no es invertible. La propiedad requiere que ambas lo sean.")
            self._log_ops("\\n".join(lineas), limpiar=False)
            return
            
        A_inv = res_A.matriz_inversa
        B_inv = res_B.matriz_inversa
        lineas.append(f"Matriz A⁻¹:\\n{self._fmt_mat(desencapsular_matriz(A_inv), modo)}")
        lineas.append(f"Matriz B⁻¹:\\n{self._fmt_mat(desencapsular_matriz(B_inv), modo)}")
        
        lineas.append("\\n--- PASO 4: Multiplicar B⁻¹ × A⁻¹ ---")
        lineas.append("(Nota: El orden se invierte según la propiedad)")
        lado_derecho = multiplicar_matrices(B_inv, A_inv)
        lineas.append(f"Matriz resultante B⁻¹A⁻¹:\\n{self._fmt_mat(desencapsular_matriz(lado_derecho), modo)}")
        
        lineas.append("\\n--- CONCLUSIÓN ---")
        son_iguales = son_matrices_iguales(lado_izquierdo, lado_derecho)
        if son_iguales:
            lineas.append("✅ (AB)⁻¹ y B⁻¹A⁻¹ son IDÉNTICAS.")
            lineas.append("La propiedad queda demostrada paso a paso.")
            self._mostrar_resultado_ranura("AB", "Propiedad (AB)⁻¹", desencapsular_matriz(lado_izquierdo))
        else:
            lineas.append("❌ Las matrices resultantes no coinciden (esto no debería ocurrir).")
            
        self._log_ops("\\n".join(lineas), limpiar=False)
"""

old_log_ops = """        self.txt_res_ops.configure(state="disabled")"""

new_content = content.replace(old_log_ops, old_log_ops + "\n" + method_to_add, 1)

with open("src/ui/matrix_ops_view.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("Patch applied to add _calc_prop_ab_inv")
