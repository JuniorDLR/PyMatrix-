with open("src/ui/matrix_ops_view.py", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Hook visual into _calc_determinante after self._log_det call
old1 = '        self._log_det("\\n".join(lineas), limpiar=False)\n\n    def _log_det'
new1 = '        self._log_det("\\n".join(lineas), limpiar=False)\n        self._mostrar_resultado_visual_det("det(A) — Triangulación", res.determinante)\n        self.tabview_det.set("  📋 Historial (Texto)  ")\n\n    def _log_det'
count1 = c.count(old1)
print(f"old1 occurrences: {count1}")
if count1 == 1:
    c = c.replace(old1, new1)

# 2. Hook visual into _calc_det_cofactores
old2 = '        self._log_det("\\n".join(lineas), limpiar=False)\n\n    def _calc_det_sarrus'
new2 = '        self._log_det("\\n".join(lineas), limpiar=False)\n        self._mostrar_resultado_visual_det("det(A) — Cofactores (Laplace)", det_val)\n        self.tabview_det.set("  📋 Historial (Texto)  ")\n\n    def _calc_det_sarrus'
count2 = c.count(old2)
print(f"old2 occurrences: {count2}")
if count2 == 1:
    c = c.replace(old2, new2)

# 3. Hook visual into _calc_det_sarrus  
old3 = '        self._log_det("\\n".join(lineas), limpiar=False)\n\n    def _limpiar_historial_inv'
new3 = '        self._log_det("\\n".join(lineas), limpiar=False)\n        self._mostrar_resultado_visual_det("det(A) — Sarrus (3×3)", det_val)\n        self.tabview_det.set("  📋 Historial (Texto)  ")\n\n    def _limpiar_historial_inv'
count3 = c.count(old3)
print(f"old3 occurrences: {count3}")
if count3 == 1:
    c = c.replace(old3, new3)

# 4. Remove the duplicate _limpiar_historial_inv that was left at the bottom (from patch_cargar.py old logic)
old4 = '''    def _limpiar_historial_inv(self):
        self.txt_res_inv.configure(state="normal")
        self.txt_res_inv.delete("1.0", "end")
        self.txt_res_inv.configure(state="disabled")'''
if old4 in c:
    c = c.replace(old4, "")
    print("Removed duplicate _limpiar_historial_inv")

with open("src/ui/matrix_ops_view.py", "w", encoding="utf-8") as f:
    f.write(c)

print("Done")
