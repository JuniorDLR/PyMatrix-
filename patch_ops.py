import re

with open("src/ui/matrix_ops_view.py", "r", encoding="utf-8") as f:
    content = f.read()

# We need to replace the setup for the right panel in _setup_tab_ops

old_right_panel = """        right = ctk.CTkFrame(tab, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            right, text="📋 Procedimiento Paso a Paso",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=("#38bdf8", "#38bdf8")
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 6))

        self.txt_res_ops = ctk.CTkTextbox(right, font=ctk.CTkFont(family="Consolas", size=12), wrap="word")
        self.txt_res_ops.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.txt_res_ops.configure(state="disabled")"""

new_right_panel = """        # --- PANEL DERECHO: Pestañas Duales (Visualizador y Terminal) ---
        right = ctk.CTkFrame(tab, corner_radius=10, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(0, weight=1)

        self.ops_right_tabs = ctk.CTkTabview(right)
        self.ops_right_tabs.grid(row=0, column=0, sticky="nsew")

        tab_vis = self.ops_right_tabs.add("  📊 Visualizador de Resultados  ")
        tab_hist = self.ops_right_tabs.add("  📋 Historial de Operaciones (Texto)  ")

        # --- Pestaña 1: Visualizador Gráfico (3 Ranuras) ---
        tab_vis.grid_columnconfigure(0, weight=1)
        tab_vis.grid_rowconfigure(0, weight=1)
        
        self.scroll_vis = ctk.CTkScrollableFrame(tab_vis, fg_color="transparent")
        self.scroll_vis.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.scroll_vis.grid_columnconfigure(0, weight=1)
        
        # Ranura 1: Operaciones en A
        self.frame_slot_A = ctk.CTkFrame(self.scroll_vis, corner_radius=8)
        self.frame_slot_A.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.frame_slot_A.grid_columnconfigure(0, weight=1)
        self.lbl_slot_A = ctk.CTkLabel(self.frame_slot_A, text="Última Operación en A: (Ninguna)", font=ctk.CTkFont(weight="bold", size=13), text_color=("#38bdf8", "#38bdf8"))
        self.lbl_slot_A.pack(pady=(10, 0))
        self.grid_slot_A = ctk.CTkFrame(self.frame_slot_A, fg_color="transparent")
        self.grid_slot_A.pack(pady=10)
        self.btn_guardar_A = ctk.CTkButton(self.frame_slot_A, text="💾 Guardar en Banco", state="disabled", command=lambda: self._pedir_guardar_banco("A"), fg_color=("#059669", "#047857"))
        self.btn_guardar_A.pack(pady=(0, 10))
        
        # Ranura 2: Operaciones en B
        self.frame_slot_B = ctk.CTkFrame(self.scroll_vis, corner_radius=8)
        self.frame_slot_B.grid(row=1, column=0, sticky="ew", pady=10)
        self.frame_slot_B.grid_columnconfigure(0, weight=1)
        self.lbl_slot_B = ctk.CTkLabel(self.frame_slot_B, text="Última Operación en B: (Ninguna)", font=ctk.CTkFont(weight="bold", size=13), text_color=("#34d399", "#34d399"))
        self.lbl_slot_B.pack(pady=(10, 0))
        self.grid_slot_B = ctk.CTkFrame(self.frame_slot_B, fg_color="transparent")
        self.grid_slot_B.pack(pady=10)
        self.btn_guardar_B = ctk.CTkButton(self.frame_slot_B, text="💾 Guardar en Banco", state="disabled", command=lambda: self._pedir_guardar_banco("B"), fg_color=("#059669", "#047857"))
        self.btn_guardar_B.pack(pady=(0, 10))
        
        # Ranura 3: Operaciones con A y B
        self.frame_slot_AB = ctk.CTkFrame(self.scroll_vis, corner_radius=8)
        self.frame_slot_AB.grid(row=2, column=0, sticky="ew", pady=10)
        self.frame_slot_AB.grid_columnconfigure(0, weight=1)
        self.lbl_slot_AB = ctk.CTkLabel(self.frame_slot_AB, text="Última Operación A y B: (Ninguna)", font=ctk.CTkFont(weight="bold", size=13), text_color=("#f43f5e", "#f43f5e"))
        self.lbl_slot_AB.pack(pady=(10, 0))
        self.grid_slot_AB = ctk.CTkFrame(self.frame_slot_AB, fg_color="transparent")
        self.grid_slot_AB.pack(pady=10)
        self.btn_guardar_AB = ctk.CTkButton(self.frame_slot_AB, text="💾 Guardar en Banco", state="disabled", command=lambda: self._pedir_guardar_banco("AB"), fg_color=("#059669", "#047857"))
        self.btn_guardar_AB.pack(pady=(0, 10))

        # --- Pestaña 2: Historial de Operaciones (Texto) ---
        tab_hist.grid_columnconfigure(0, weight=1)
        tab_hist.grid_rowconfigure(1, weight=1)
        
        top_hist = ctk.CTkFrame(tab_hist, fg_color="transparent")
        top_hist.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        ctk.CTkLabel(top_hist, text="Registro permanente de operaciones:", font=ctk.CTkFont(size=12, slant="italic")).pack(side="left")
        ctk.CTkButton(top_hist, text="🗑️ Limpiar Historial", width=120, command=self._limpiar_historial_ops, fg_color=("#ef4444", "#b91c1c")).pack(side="right")
        
        self.txt_res_ops = ctk.CTkTextbox(tab_hist, font=ctk.CTkFont(family="Consolas", size=12), wrap="word")
        self.txt_res_ops.grid(row=1, column=0, sticky="nsew")
        self.txt_res_ops.configure(state="disabled")
        
        # Variables internas para guardar el resultado matemático puro (slots)
        self._resultado_slot_A = None
        self._resultado_slot_B = None
        self._resultado_slot_AB = None
        
        # Banco de matrices
        if not hasattr(self, "banco_matrices"):
            self.banco_matrices = {}  # dict { nombre: matriz }
"""

content = content.replace(old_right_panel, new_right_panel)

# Also we need to add the Banco de matrices UI on the left panel (at the bottom)
# Currently left panel ends with `op_grid`

old_op_grid = """        ctk.CTkButton(op_grid, text="Bᵀ  (Traspuesta de B)", command=lambda: self._calc_op("traspuesta_B"),
                      fg_color=("#059669", "#047857"), font=ctk.CTkFont(size=12, weight="bold"), height=34
                      ).grid(row=2, column=1, padx=3, pady=3, sticky="ew")"""

new_op_grid = old_op_grid + """

        # --- BANCO DE MATRICES (Panel Izquierdo Inferior) ---
        self.frame_banco = ctk.CTkFrame(left, corner_radius=8)
        self.frame_banco.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        self.frame_banco.grid_columnconfigure(0, weight=1)
        
        lbl_banco = ctk.CTkLabel(self.frame_banco, text="🏦 Banco de Matrices", font=ctk.CTkFont(size=13, weight="bold"))
        lbl_banco.pack(pady=(5, 0))
        
        self.scroll_banco = ctk.CTkScrollableFrame(self.frame_banco, height=100, fg_color="transparent")
        self.scroll_banco.pack(fill="both", expand=True, padx=5, pady=5)
        self.scroll_banco.grid_columnconfigure(0, weight=1)
        
        self._actualizar_banco_ui()
"""

content = content.replace(old_op_grid, new_op_grid)

# Write back
with open("src/ui/matrix_ops_view.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied to setup_tab_ops")
