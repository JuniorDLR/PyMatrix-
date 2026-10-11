import re

with open("src/ui/matrix_ops_view.py", "r", encoding="utf-8") as f:
    content = f.read()

# For Inversa: Add clear button in _setup_tab_inv
old_inv_title = """        ctk.CTkLabel(
            right, text="📋 Desarrollo Matemático",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=("#38bdf8", "#38bdf8")
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 6))"""

new_inv_title = """        top_right = ctk.CTkFrame(right, fg_color="transparent")
        top_right.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))
        ctk.CTkLabel(
            top_right, text="📋 Historial de Desarrollo Matemático",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=("#38bdf8", "#38bdf8")
        ).pack(side="left")
        ctk.CTkButton(top_right, text="🗑️ Limpiar", width=80, command=self._limpiar_historial_inv, fg_color=("#ef4444", "#b91c1c")).pack(side="right")"""

content = content.replace(old_inv_title, new_inv_title)

# For Determinantes: Add clear button in _setup_tab_det
old_det_title = """        ctk.CTkLabel(
            right, text="📋 Desarrollo Matemático (Determinante)",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=("#38bdf8", "#38bdf8")
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 6))"""

new_det_title = """        top_right_det = ctk.CTkFrame(right, fg_color="transparent")
        top_right_det.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))
        ctk.CTkLabel(
            top_right_det, text="📋 Historial de Desarrollo Matemático (Determinante)",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=("#38bdf8", "#38bdf8")
        ).pack(side="left")
        ctk.CTkButton(top_right_det, text="🗑️ Limpiar", width=80, command=self._limpiar_historial_det, fg_color=("#ef4444", "#b91c1c")).pack(side="right")"""

content = content.replace(old_det_title, new_det_title)

# Replace all `limpiar=True` with `limpiar=False`
content = content.replace("limpiar=True", "limpiar=False")

# Add the methods
methods = """
    def _limpiar_historial_inv(self):
        self.txt_res_inv.configure(state="normal")
        self.txt_res_inv.delete("1.0", "end")
        self.txt_res_inv.configure(state="disabled")

    def _limpiar_historial_det(self):
        self.txt_res_det.configure(state="normal")
        self.txt_res_det.delete("1.0", "end")
        self.txt_res_det.configure(state="disabled")
"""

# Insert methods at end of file (inside MatrixOpsView class, so it needs correct indentation)
# Since MatrixOpsView is the main class, we can just find the end of the file and append it.
# Wait, let's inject it before the very end. Actually, appending to the file is fine if the class is the last thing.
content += methods

with open("src/ui/matrix_ops_view.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Patch clear buttons applied")
