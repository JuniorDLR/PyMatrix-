import re

with open("src/ui/matrix_ops_view.py", "r", encoding="utf-8") as f:
    content = f.read()

popup_code = """
    def _abrir_popup_banco(self):
        popup = ctk.CTkToplevel(self)
        popup.title("🏦 Banco de Matrices")
        popup.geometry("500x400")
        popup.transient(self.winfo_toplevel())
        popup.grab_set()
        
        lbl_titulo = ctk.CTkLabel(popup, text="Matrices Guardadas", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_titulo.pack(pady=(15, 10))
        
        scroll = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        tab_actual = self.tabview.get()
        
        if not hasattr(self, "banco_matrices") or not self.banco_matrices:
            ctk.CTkLabel(scroll, text="No hay matrices guardadas en el Banco.", text_color="gray").pack(pady=20)
            return
            
        from src.core.domain import formatear_numero
        
        for nombre, matriz in self.banco_matrices.items():
            m = len(matriz)
            n = len(matriz[0]) if m > 0 else 0
            
            item = ctk.CTkFrame(scroll, fg_color=("gray85", "gray25"), corner_radius=6)
            item.pack(fill="x", pady=4, padx=4)
            
            lbl = ctk.CTkLabel(item, text=f" {nombre} ({m}×{n})", font=ctk.CTkFont(weight="bold", size=13))
            lbl.pack(side="left", padx=10, pady=10)
            
            btn_del = ctk.CTkButton(item, text="❌", width=30, height=30, fg_color="#ef4444", hover_color="#b91c1c",
                                    command=lambda n=nombre, p=popup: self._eliminar_y_refrescar(n, p))
            btn_del.pack(side="right", padx=(5, 10), pady=10)
            
            if "Operaciones con Matrices" in tab_actual:
                btn_B = ctk.CTkButton(item, text="Cargar en B", width=100, height=30,
                                      command=lambda mat=matriz, p=popup: self._cargar_y_cerrar(mat, "B", "ops", p))
                btn_B.pack(side="right", padx=5)
                
                btn_A = ctk.CTkButton(item, text="Cargar en A", width=100, height=30,
                                      command=lambda mat=matriz, p=popup: self._cargar_y_cerrar(mat, "A", "ops", p))
                btn_A.pack(side="right", padx=5)
                
            elif "Ecuación Matricial" in tab_actual:
                btn_A = ctk.CTkButton(item, text="Cargar Matriz A", width=120, height=30,
                                      command=lambda mat=matriz, p=popup: self._cargar_y_cerrar(mat, "A", "axb", p))
                btn_A.pack(side="right", padx=5)
                
            elif "Propiedades de Ax" in tab_actual:
                btn_A = ctk.CTkButton(item, text="Cargar Matriz A", width=120, height=30,
                                      command=lambda mat=matriz, p=popup: self._cargar_y_cerrar(mat, "A", "prop", p))
                btn_A.pack(side="right", padx=5)
                
            elif "Traspuesta e Inversa" in tab_actual:
                btn_A = ctk.CTkButton(item, text="Cargar Matriz A", width=120, height=30,
                                      command=lambda mat=matriz, p=popup: self._cargar_y_cerrar(mat, "A", "inv", p))
                btn_A.pack(side="right", padx=5)
                
            elif "Determinantes" in tab_actual:
                btn_A = ctk.CTkButton(item, text="Cargar Matriz A", width=120, height=30,
                                      command=lambda mat=matriz, p=popup: self._cargar_y_cerrar(mat, "A", "det", p))
                btn_A.pack(side="right", padx=5)

    def _eliminar_y_refrescar(self, nombre, popup):
        if nombre in self.banco_matrices:
            del self.banco_matrices[nombre]
            popup.destroy()
            self._abrir_popup_banco()

    def _cargar_y_cerrar(self, matriz, target, tab_id, popup):
        m = len(matriz)
        n = len(matriz[0]) if m > 0 else 0
        from src.core.domain import formatear_numero
        modo = self.get_modo_numero()
        
        # Guardar las entradas actuales para no perderlas al regenerar
        def guardar_valores(entries_matrix):
            vals = []
            for fila in entries_matrix:
                f_vals = []
                for e in fila:
                    f_vals.append(e.get() if e.get() else "0")
                vals.append(f_vals)
            return vals
            
        def restaurar_valores(entries_matrix, vals):
            for i in range(min(len(entries_matrix), len(vals))):
                for j in range(min(len(entries_matrix[0]), len(vals[0]))):
                    entries_matrix[i][j].delete(0, "end")
                    entries_matrix[i][j].insert(0, vals[i][j])
        
        if tab_id == "ops":
            vA = guardar_valores(self.entries_A)
            vB = guardar_valores(self.entries_B)
            
            if target == "A":
                self.entry_ops_mA.delete(0, "end")
                self.entry_ops_mA.insert(0, str(m))
                self.entry_ops_nA.delete(0, "end")
                self.entry_ops_nA.insert(0, str(n))
                self._generar_matrices_ops()
                restaurar_valores(self.entries_B, vB)  # Restaurar B
                
                # Llenar A
                for i in range(m):
                    for j in range(n):
                        self.entries_A[i][j].delete(0, "end")
                        self.entries_A[i][j].insert(0, formatear_numero(matriz[i][j], modo))
                self._log_ops(f"\\n📥 Matriz cargada en A ({m}×{n}).", limpiar=False)
                
            elif target == "B":
                self.entry_ops_mB.delete(0, "end")
                self.entry_ops_mB.insert(0, str(m))
                self.entry_ops_nB.delete(0, "end")
                self.entry_ops_nB.insert(0, str(n))
                self._generar_matrices_ops()
                restaurar_valores(self.entries_A, vA)  # Restaurar A
                
                # Llenar B
                for i in range(m):
                    for j in range(n):
                        self.entries_B[i][j].delete(0, "end")
                        self.entries_B[i][j].insert(0, formatear_numero(matriz[i][j], modo))
                self._log_ops(f"\\n📥 Matriz cargada en B ({m}×{n}).", limpiar=False)
                
        elif tab_id == "axb":
            self.entry_axb_m.delete(0, "end")
            self.entry_axb_m.insert(0, str(m))
            self.entry_axb_n.delete(0, "end")
            self.entry_axb_n.insert(0, str(n))
            self._generar_matriz_axb()
            for i in range(m):
                for j in range(n):
                    self.entries_axb_A[i][j].delete(0, "end")
                    self.entries_axb_A[i][j].insert(0, formatear_numero(matriz[i][j], modo))
                    
        elif tab_id == "prop":
            self.entry_prop_m.delete(0, "end")
            self.entry_prop_m.insert(0, str(m))
            self.entry_prop_n.delete(0, "end")
            self.entry_prop_n.insert(0, str(n))
            self._generar_matriz_prop()
            for i in range(m):
                for j in range(n):
                    self.entries_prop_A[i][j].delete(0, "end")
                    self.entries_prop_A[i][j].insert(0, formatear_numero(matriz[i][j], modo))
                    
        elif tab_id == "inv":
            self.entry_inv_n.delete(0, "end")
            self.entry_inv_n.insert(0, str(m))
            self._generar_matriz_inv()
            for i in range(m):
                for j in range(m): # Cuadrada en UI pero si es m x n, truncar
                    if j < n:
                        self.entries_inv[i][j].delete(0, "end")
                        self.entries_inv[i][j].insert(0, formatear_numero(matriz[i][j], modo))
            self._log_inv(f"\\n📥 Matriz cargada desde el Banco.", limpiar=False)
                        
        elif tab_id == "det":
            self.entry_det_n.delete(0, "end")
            self.entry_det_n.insert(0, str(m))
            self._generar_matriz_det()
            for i in range(m):
                for j in range(m): # Cuadrada en UI
                    if j < n:
                        self.entries_det[i][j].delete(0, "end")
                        self.entries_det[i][j].insert(0, formatear_numero(matriz[i][j], modo))
            self._log_det(f"\\n📥 Matriz cargada desde el Banco.", limpiar=False)
            
        popup.destroy()
"""

# Replace the old method `_cargar_matriz_en_grid` with `popup_code`
old_method_regex = r"    def _cargar_matriz_en_grid\(self, matriz, target: str\):.*?            self\._log_ops\(f\"\\n📥 Matriz cargada desde el Banco hacia la Matriz B \(\{m\}×\{n\}\)\.\", limpiar=False\)"

content = re.sub(old_method_regex, popup_code, content, flags=re.DOTALL)

with open("src/ui/matrix_ops_view.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Popup logic applied!")
