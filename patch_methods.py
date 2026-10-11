import re

with open("src/ui/matrix_ops_view.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add new methods at the end of _log_ops

methods_to_add = """
    def _limpiar_historial_ops(self):
        self.txt_res_ops.configure(state="normal")
        self.txt_res_ops.delete("1.0", "end")
        self.txt_res_ops.configure(state="disabled")

    def _renderizar_matriz_en_grid(self, parent_frame, matriz, color_fondo, color_texto):
        # Limpiar el frame
        for w in parent_frame.winfo_children():
            w.destroy()
        
        if not matriz:
            return
            
        m = len(matriz)
        n = len(matriz[0]) if m > 0 else 0
        modo = self.get_modo_numero()
        
        # Grid para alinear columnas y filas
        for i in range(m):
            for j in range(n):
                val_str = formatear_numero(matriz[i][j], modo)
                lbl = ctk.CTkLabel(parent_frame, text=val_str, width=50, height=26,
                                   fg_color=color_fondo, text_color=color_texto,
                                   corner_radius=4, font=ctk.CTkFont(size=12, weight="bold"))
                lbl.grid(row=i, column=j, padx=2, pady=2)

    def _mostrar_resultado_ranura(self, slot: str, titulo: str, matriz):
        if slot == "A":
            self._resultado_slot_A = matriz
            self.lbl_slot_A.configure(text=f"Última Operación en A: {titulo}")
            self._renderizar_matriz_en_grid(self.grid_slot_A, matriz, ("#bae6fd", "#0284c7"), ("#0369a1", "#e0f2fe"))
            self.btn_guardar_A.configure(state="normal")
            self.ops_right_tabs.set("  📊 Visualizador de Resultados  ")
        elif slot == "B":
            self._resultado_slot_B = matriz
            self.lbl_slot_B.configure(text=f"Última Operación en B: {titulo}")
            self._renderizar_matriz_en_grid(self.grid_slot_B, matriz, ("#a7f3d0", "#059669"), ("#047857", "#d1fae5"))
            self.btn_guardar_B.configure(state="normal")
            self.ops_right_tabs.set("  📊 Visualizador de Resultados  ")
        elif slot == "AB":
            self._resultado_slot_AB = matriz
            self.lbl_slot_AB.configure(text=f"Última Operación A y B: {titulo}")
            self._renderizar_matriz_en_grid(self.grid_slot_AB, matriz, ("#fecdd3", "#e11d48"), ("#be123c", "#ffe4e6"))
            self.btn_guardar_AB.configure(state="normal")
            self.ops_right_tabs.set("  📊 Visualizador de Resultados  ")

    def _pedir_guardar_banco(self, slot: str):
        import tkinter.simpledialog as sd
        matriz = None
        if slot == "A": matriz = self._resultado_slot_A
        elif slot == "B": matriz = self._resultado_slot_B
        elif slot == "AB": matriz = self._resultado_slot_AB
        
        if not matriz: return
        
        nombre = sd.askstring("Guardar Matriz", "Ingrese un nombre corto para esta matriz (ej. M1, At):")
        if nombre:
            nombre = nombre.strip()
            if nombre:
                if not hasattr(self, "banco_matrices"):
                    self.banco_matrices = {}
                self.banco_matrices[nombre] = matriz
                self._actualizar_banco_ui()
                self._log_ops(f"\\n✅ Matriz guardada en el banco como '{nombre}'.", limpiar=False)

    def _actualizar_banco_ui(self):
        if not hasattr(self, "scroll_banco"):
            return
            
        for w in self.scroll_banco.winfo_children():
            w.destroy()
            
        if not hasattr(self, "banco_matrices") or not self.banco_matrices:
            ctk.CTkLabel(self.scroll_banco, text="No hay matrices guardadas.", text_color="gray").pack(pady=10)
            return
            
        for nombre, matriz in self.banco_matrices.items():
            m = len(matriz)
            n = len(matriz[0]) if m > 0 else 0
            
            item = ctk.CTkFrame(self.scroll_banco, fg_color=("gray85", "gray25"), corner_radius=6)
            item.pack(fill="x", pady=2, padx=2)
            
            lbl = ctk.CTkLabel(item, text=f" {nombre} ({m}×{n})", font=ctk.CTkFont(weight="bold", size=12))
            lbl.pack(side="left", padx=5)
            
            btn_del = ctk.CTkButton(item, text="❌", width=28, height=24, fg_color="transparent", text_color="#ef4444", hover_color="#fee2e2",
                                    command=lambda n=nombre: self._eliminar_del_banco(n))
            btn_del.pack(side="right", padx=(0, 5))
            
            btn_B = ctk.CTkButton(item, text="Cargar en B", width=80, height=24,
                                  command=lambda mat=matriz: self._cargar_matriz_en_grid(mat, "B"))
            btn_B.pack(side="right", padx=2)
            
            btn_A = ctk.CTkButton(item, text="Cargar en A", width=80, height=24,
                                  command=lambda mat=matriz: self._cargar_matriz_en_grid(mat, "A"))
            btn_A.pack(side="right", padx=2)

    def _eliminar_del_banco(self, nombre: str):
        if nombre in self.banco_matrices:
            del self.banco_matrices[nombre]
            self._actualizar_banco_ui()

    def _cargar_matriz_en_grid(self, matriz, target: str):
        m = len(matriz)
        n = len(matriz[0]) if m > 0 else 0
        
        # Cambiar los inputs de m y n y regenerar los grids
        if target == "A":
            self.entry_ops_mA.delete(0, "end")
            self.entry_ops_mA.insert(0, str(m))
            self.entry_ops_nA.delete(0, "end")
            self.entry_ops_nA.insert(0, str(n))
            self._generar_matrices_ops()
            
            # Llenar datos
            for i in range(m):
                for j in range(n):
                    val_str = formatear_numero(matriz[i][j], self.get_modo_numero())
                    self.entries_A[i][j].delete(0, "end")
                    self.entries_A[i][j].insert(0, val_str)
                    
            self._log_ops(f"\\n📥 Matriz cargada desde el Banco hacia la Matriz A ({m}×{n}).", limpiar=False)
            
        elif target == "B":
            self.entry_ops_mB.delete(0, "end")
            self.entry_ops_mB.insert(0, str(m))
            self.entry_ops_nB.delete(0, "end")
            self.entry_ops_nB.insert(0, str(n))
            self._generar_matrices_ops()
            
            for i in range(m):
                for j in range(n):
                    val_str = formatear_numero(matriz[i][j], self.get_modo_numero())
                    self.entries_B[i][j].delete(0, "end")
                    self.entries_B[i][j].insert(0, val_str)
                    
            self._log_ops(f"\\n📥 Matriz cargada desde el Banco hacia la Matriz B ({m}×{n}).", limpiar=False)

"""

# Insert methods after _log_ops
old_log_ops = """        self.txt_res_ops.configure(state="disabled")"""

new_content = content.replace(old_log_ops, old_log_ops + "\n" + methods_to_add, 1)

with open("src/ui/matrix_ops_view.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("Patch applied to add new methods")
