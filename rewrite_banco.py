import re

with open("src/ui/matrix_ops_view.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove the Banco from the left panel of ops
remove_banco_ui = r"""        # --- BANCO DE MATRICES \(Panel Izquierdo Inferior\) ---
        self\.frame_banco = ctk\.CTkFrame\(left, corner_radius=8\)
        self\.frame_banco\.pack\(fill="both", expand=True, padx=14, pady=\(0, 12\)\)
        self\.frame_banco\.grid_columnconfigure\(0, weight=1\)
        
        lbl_banco = ctk\.CTkLabel\(self\.frame_banco, text="🏦 Banco de Matrices", font=ctk\.CTkFont\(size=13, weight="bold"\)\)
        lbl_banco\.pack\(pady=\(5, 0\)\)
        
        self\.scroll_banco = ctk\.CTkScrollableFrame\(self\.frame_banco, height=100, fg_color="transparent"\)
        self\.scroll_banco\.pack\(fill="both", expand=True, padx=5, pady=5\)
        self\.scroll_banco\.grid_columnconfigure\(0, weight=1\)
        
        self\._actualizar_banco_ui\(\)"""

content = re.sub(remove_banco_ui, "", content)

# 2. In __init__, we need self.banco_matrices
if "self.banco_matrices =" not in content:
    content = content.replace("self._ultimo_calc_det = None", "self._ultimo_calc_det = None\n        self.banco_matrices = {}")

# 3. Add a global button in MatrixOpsView, maybe above the tabview?
# _setup_ui:
add_global_banco = """        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))"""

new_global_banco = """        
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 0))
        ctk.CTkButton(top_bar, text="🏦 Abrir Banco de Matrices", command=self._abrir_popup_banco, fg_color=("#059669", "#047857"), font=ctk.CTkFont(weight="bold")).pack(side="right")
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 5))"""

content = content.replace(add_global_banco, new_global_banco)

# Also need to add rowconfigure in MatrixOpsView
content = content.replace("self.grid_rowconfigure(0, weight=1)", "self.grid_rowconfigure(1, weight=1)")

# 4. Remove old _actualizar_banco_ui and _eliminar_del_banco
old_methods_regex = r"    def _actualizar_banco_ui\(self\):.*?    def _cargar_matriz_en_grid\(self, matriz, target: str\):"
content = re.sub(old_methods_regex, "    def _cargar_matriz_en_grid(self, matriz, target: str):", content, flags=re.DOTALL)

with open("src/ui/matrix_ops_view.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Removed old banco and added global button")
