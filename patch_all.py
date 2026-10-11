import re

with open("src/ui/matrix_ops_view.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Custom Dialog for "Guardar Matriz" instead of CTkInputDialog
custom_dialog_code = """
class DialogoGuardar(ctk.CTkToplevel):
    def __init__(self, *args, title="Guardar", text="Ingrese valor:", **kwargs):
        super().__init__(*args, **kwargs)
        self.title(title)
        self.geometry("400x200")
        self.transient(self.master)
        self.grab_set()
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        lbl = ctk.CTkLabel(self, text=text, font=ctk.CTkFont(size=14, weight="bold"))
        lbl.grid(row=0, column=0, pady=(20, 10), padx=20)
        
        self.entry = ctk.CTkEntry(self, width=250, height=35)
        self.entry.grid(row=1, column=0, pady=10, padx=20)
        self.entry.focus_set()
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=(10, 20))
        
        ctk.CTkButton(btn_frame, text="OK", width=100, command=self._ok).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancelar", width=100, fg_color="gray", command=self._cancel).pack(side="left", padx=10)
        
        self.result = None
        
    def _ok(self):
        self.result = self.entry.get()
        self.destroy()
        
    def _cancel(self):
        self.destroy()
        
    def get_input(self):
        self.wait_window(self)
        return self.result

"""

if "class DialogoGuardar" not in content:
    content = "import customtkinter as ctk\n" + custom_dialog_code + content.replace("import customtkinter as ctk", "")

# Replace CTkInputDialog with DialogoGuardar
content = content.replace(
    'dialog = ctk.CTkInputDialog(text="Ingrese un nombre corto para esta matriz (ej. M1, A):", title="Guardar Matriz")',
    'dialog = DialogoGuardar(self, text="Ingrese un nombre corto para esta matriz (ej. M1, A):", title="Guardar Matriz")'
)

# 2. Fix _cargar_y_cerrar using .after()
new_cargar_code = """    def _cargar_y_cerrar(self, matriz, target, tab_id, popup):
        m = len(matriz)
        n = len(matriz[0]) if m > 0 else 0
        from src.core.domain import formatear_numero
        modo = self.get_modo_numero()
        
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
                    
        def deferred_fill():
            try:
                if tab_id == "ops":
                    if target == "A":
                        restaurar_valores(self.entries_B, vB)
                        for i in range(m):
                            for j in range(n):
                                self.entries_A[i][j].delete(0, "end")
                                self.entries_A[i][j].insert(0, formatear_numero(matriz[i][j], modo))
                        self._log_ops(f"\\n📥 Matriz cargada en A ({m}×{n}).", limpiar=False)
                    elif target == "B":
                        restaurar_valores(self.entries_A, vA)
                        for i in range(m):
                            for j in range(n):
                                self.entries_B[i][j].delete(0, "end")
                                self.entries_B[i][j].insert(0, formatear_numero(matriz[i][j], modo))
                        self._log_ops(f"\\n📥 Matriz cargada en B ({m}×{n}).", limpiar=False)
                elif tab_id == "axb":
                    for i in range(m):
                        for j in range(n):
                            self.entries_axb_A[i][j].delete(0, "end")
                            self.entries_axb_A[i][j].insert(0, formatear_numero(matriz[i][j], modo))
                elif tab_id == "prop":
                    for i in range(m):
                        for j in range(n):
                            self.entries_prop_A[i][j].delete(0, "end")
                            self.entries_prop_A[i][j].insert(0, formatear_numero(matriz[i][j], modo))
                elif tab_id == "inv":
                    for i in range(m):
                        for j in range(m):
                            if j < n:
                                self.entries_inv[i][j].delete(0, "end")
                                self.entries_inv[i][j].insert(0, formatear_numero(matriz[i][j], modo))
                elif tab_id == "det":
                    for i in range(m):
                        for j in range(m):
                            if j < n:
                                self.entries_det[i][j].delete(0, "end")
                                self.entries_det[i][j].insert(0, formatear_numero(matriz[i][j], modo))
            except Exception as e:
                import traceback
                self._log_ops(f"Error asincrono: {e}\\n{traceback.format_exc()}", limpiar=False)

        try:
            if tab_id == "ops":
                vA = guardar_valores(self.entries_A)
                vB = guardar_valores(self.entries_B)
                if target == "A":
                    self.entry_ops_mA.delete(0, "end"); self.entry_ops_mA.insert(0, str(m))
                    self.entry_ops_nA.delete(0, "end"); self.entry_ops_nA.insert(0, str(n))
                else:
                    self.entry_ops_mB.delete(0, "end"); self.entry_ops_mB.insert(0, str(m))
                    self.entry_ops_nB.delete(0, "end"); self.entry_ops_nB.insert(0, str(n))
                self._generar_matrices_ops()
            elif tab_id == "axb":
                self.entry_axb_m.delete(0, "end"); self.entry_axb_m.insert(0, str(m))
                self.entry_axb_n.delete(0, "end"); self.entry_axb_n.insert(0, str(n))
                self._generar_matriz_axb()
            elif tab_id == "prop":
                self.entry_prop_m.delete(0, "end"); self.entry_prop_m.insert(0, str(m))
                self.entry_prop_n.delete(0, "end"); self.entry_prop_n.insert(0, str(n))
                self._generar_matriz_prop()
            elif tab_id == "inv":
                self.entry_inv_n.delete(0, "end"); self.entry_inv_n.insert(0, str(m))
                self._generar_matriz_inv()
            elif tab_id == "det":
                self.entry_det_n.delete(0, "end"); self.entry_det_n.insert(0, str(m))
                self._generar_matriz_det()
                
            self.after(50, deferred_fill)
            
        except Exception as e:
            pass
        popup.destroy()"""

# Replace the entire old _cargar_y_cerrar logic
old_func_regex = r"    def _cargar_y_cerrar\(self, matriz, target, tab_id, popup\):.*?        popup\.destroy\(\)"
content = re.sub(old_func_regex, new_cargar_code, content, flags=re.DOTALL)

with open("src/ui/matrix_ops_view.py", "w", encoding="utf-8") as f:
    f.write(content)
