import re

with open("src/ui/matrix_ops_view.py", "r", encoding="utf-8") as f:
    content = f.read()

old_op_grid_2 = """        ctk.CTkButton(op_grid, text="Bᵀ  (Traspuesta de B)", command=lambda: self._calc_op("traspuesta_B"),
                      fg_color=("#059669", "#047857"), font=ctk.CTkFont(size=12, weight="bold"), height=34
                      ).grid(row=2, column=1, padx=3, pady=3, sticky="ew")"""

new_op_grid_2 = old_op_grid_2 + """

        ctk.CTkButton(op_grid, text="(AB)⁻¹ = B⁻¹ A⁻¹ (Propiedad)", command=lambda: self._calc_prop_ab_inv(),
                      fg_color=("#ea580c", "#c2410c"), font=ctk.CTkFont(size=12, weight="bold"), height=34
                      ).grid(row=3, column=0, columnspan=2, padx=3, pady=3, sticky="ew")
"""

content = content.replace(old_op_grid_2, new_op_grid_2)

# Remove it from _setup_tab_inv:
old_btn_inv = """        ctk.CTkButton(btn_grid, text="(AB)⁻¹ = B⁻¹A⁻¹", command=lambda: self._set_inv_op("tarea5_inversa_producto"),
                      fg_color=("#ea580c", "#c2410c"), font=ctk.CTkFont(size=11, weight="bold"), height=28
                      ).grid(row=1, column=0, padx=2, pady=2, sticky="ew")"""
content = content.replace(old_btn_inv, "")

with open("src/ui/matrix_ops_view.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Patch applied to move property")
