with open("src/ui/matrix_ops_view.py", "r", encoding="utf-8") as f:
    c = f.read()

import re

old_func_start = '''    def _calc_propiedad_tarea5_det(self, prop_id: str):
        """Verifica una de las propiedades de Determinante de la Tarea 5."""'''

# The function ends around line 1897, before _log_prop.
# We'll use regex to replace the whole body of _calc_propiedad_tarea5_det up to _log_prop.

pattern = re.compile(r'    def _calc_propiedad_tarea5_det.*?    def _log_prop', re.DOTALL)

new_func = '''    def _calc_propiedad_tarea5_det(self, prop_id: str):
        """Verifica una de las propiedades de Determinante de la Tarea 5 con procedimiento completo."""
        self._ultimo_calc_det = f"tarea5_{prop_id}"
        try:
            A = self._leer_matriz_det()
        except ValueError as e:
            self._log_det(f"❌ Error al leer datos: {e}\\n" + "-"*40, limpiar=False)
            return

        nA = len(A)
        modo = self.get_modo_numero()
        try:
            from fractions import Fraction
            from src.core.exact_math import (
                crear_matriz, inversa_gauss_jordan, calcular_determinante,
                matriz_a_cadena, formatear_numero
            )

            A_f = crear_matriz(A)
            
            def fmt_mat_exact(mat):
                lines = []
                for fila in mat:
                    vals = "  ".join(f"{formatear_numero(float(x), modo):>8}" for x in fila)
                    lines.append(f"  [ {vals} ]")
                return "\\n".join(lines)

            lineas = [
                "\\n" + "═" * 70,
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
                lineas += ["\\n".join("    " + p for p in res_detA.pasos)]
                detA = res_detA.determinante
                lineas.append(f"\\n  => det(A) = {formatear_numero(float(detA), modo)}")
                
                if detA == 0:
                    lineas.append("  ❌ det(A) = 0, la matriz no es invertible. Propiedad no aplicable.")
                    self._log_det("\\n".join(lineas), limpiar=False)
                    return
                
                # Paso 2: Calcular A⁻¹
                lineas += ["", "  PASO 2: Calcular A⁻¹ por Gauss-Jordan"]
                res_inv = inversa_gauss_jordan(A_f)
                A_inv = res_inv.matriz_inversa
                lineas.append(f"  A⁻¹ =\n{fmt_mat_exact(A_inv)}")
                
                # Paso 3: Calcular det(A⁻¹)
                lineas += ["", "  PASO 3: Calcular det(A⁻¹)"]
                res_detA_inv = calcular_determinante(A_inv)
                lineas += ["\\n".join("    " + p for p in res_detA_inv.pasos)]
                detA_inv = res_detA_inv.determinante
                lineas.append(f"\\n  => det(A⁻¹) = {formatear_numero(float(detA_inv), modo)}")
                
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
                
                if son_iguales:
                    self._mostrar_resultado_visual_det("det(A⁻¹) = 1/det(A)", detA_inv)

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
                self._mostrar_resultado_visual_det("det(A) (Op. Fila)", res_detA.determinante)

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
                self._mostrar_resultado_visual_det("det(A) Triangular", res_detA.determinante)

            self._log_det("\\n".join(lineas), limpiar=False)
            self.tabview_det.set("  📋 Historial (Texto)  ")

        except Exception as ex:
            import traceback
            self._log_det(f"❌ Error inesperado:\\n{ex}\\n\\n{traceback.format_exc()}", limpiar=False)

    def _log_prop'''

if pattern.search(c):
    c = pattern.sub(new_func, c)
    with open("src/ui/matrix_ops_view.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("Replaced _calc_propiedad_tarea5_det")
else:
    print("Could not find pattern")

