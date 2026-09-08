import customtkinter as ctk
import tkinter as tk
from typing import List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from src.core.domain import formatear_fraccion, a_subindice


class CellState(Enum):
    NORMAL = "normal"
    PIVOT_CURRENT = "pivot_current"
    PIVOT_NORMALIZED = "pivot_normalized"
    PIVOT_PREVIOUS = "pivot_previous"
    ZERO_NEW = "zero_new"
    ZERO_ABOVE = "zero_above"
    ZERO_EXISTING = "zero_existing"
    ROW_PIVOT = "row_pivot"
    INDEPENDENT = "independent"


@dataclass
class CellStyle:
    bg: str
    fg: str
    font_weight: str = "normal"
    border_color: str = ""
    border_width: int = 0


@dataclass
class MatrixStep:
    matriz: List[List[float]]
    descripcion: str
    pivot_row: int = -1
    pivot_col: int = -1
    is_normalized: bool = False
    zeros_created: List[Tuple[int, int]] = field(default_factory=list)
    zeros_above_created: List[Tuple[int, int]] = field(default_factory=list)
    row_swapped: Optional[Tuple[int, int]] = None
    show_staircase: bool = False


class MatrixCanvas(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.force_staircase = False
        self._theme_colors = self._get_theme_colors()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(
            self,
            bg=self._theme_colors["canvas_bg"],
            highlightthickness=0,
            bd=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        
        self.scroll_y = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.scroll_x = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)


        
        self.steps: List[MatrixStep] = []
        self.current_step = 0
        self.cell_rects: List[List[int]] = []
        self.cell_texts: List[List[int]] = []
        self.cell_states: List[List[CellState]] = []
        
        self.cell_width = 76
        self.cell_height = 42
        self.padding = 12
        self.header_height = 36
        self.row_label_width = 54
        
        self.animation_id = None
        self.is_playing = False
        self.play_speed = 1.0
        
        self.on_step_change: Optional[Callable[[int, MatrixStep], None]] = None
        
        self._bind_events()
        self._setup_fonts()
    
    def _get_theme_colors(self) -> dict:
        mode = ctk.get_appearance_mode()
        if mode == "Dark":
            return {
                "canvas_bg": "#0f172a",
                "cell_normal": "#1e293b",
                "cell_normal_fg": "#f1f5f9",
                "pivot_current": "#1e3a8a",
                "pivot_current_fg": "#93c5fd",
                "pivot_normalized": "#064e3b",
                "pivot_normalized_fg": "#6ee7b7",
                "pivot_previous": "#172554",
                "pivot_previous_fg": "#60a5fa",
                "zero_new": "#134e4a",
                "zero_new_fg": "#5eead4",
                "zero_above": "#312e81",
                "zero_above_fg": "#c4b5fd",
                "zero_existing": "#1e293b",
                "zero_existing_fg": "#64748b",
                "row_pivot": "#1e293b",
                "row_pivot_fg": "#fde047",
                "independent_bg": "#3f1a24",
                "independent_fg": "#fca5a5",
                "header_bg": "#1e293b",
                "header_fg": "#38bdf8",
                "grid_color": "#334155",
                "border_pivot": "#3b82f6",
                "border_normalized": "#10b981",
                "border_zero": "#14b8a6",
                "border_above": "#8b5cf6",
                "border_indep": "#f87171",
                "legend_bg": "#1e293b",
                "legend_fg": "#cbd5e1",
                "staircase": "#f59e0b",
            }
        else:
            return {
                "canvas_bg": "#f8fafc",
                "cell_normal": "#ffffff",
                "cell_normal_fg": "#0f172a",
                "pivot_current": "#dbeafe",
                "pivot_current_fg": "#1d4ed8",
                "pivot_normalized": "#d1fae5",
                "pivot_normalized_fg": "#047857",
                "pivot_previous": "#eff6ff",
                "pivot_previous_fg": "#2563eb",
                "zero_new": "#ccfbf1",
                "zero_new_fg": "#0f766e",
                "zero_above": "#ede9fe",
                "zero_above_fg": "#6d28d9",
                "zero_existing": "#f1f5f9",
                "zero_existing_fg": "#94a3b8",
                "row_pivot": "#fef3c7",
                "row_pivot_fg": "#b45309",
                "independent_bg": "#fee2e2",
                "independent_fg": "#b91c1c",
                "header_bg": "#e2e8f0",
                "header_fg": "#0369a1",
                "grid_color": "#cbd5e1",
                "border_pivot": "#2563eb",
                "border_normalized": "#059669",
                "border_zero": "#0d9488",
                "border_above": "#7c3aed",
                "border_indep": "#dc2626",
                "legend_bg": "#ffffff",
                "legend_fg": "#334155",
                "staircase": "#d97706",
            }
    
    def _setup_fonts(self):
        self.font_normal = ("Consolas", 11)
        self.font_bold = ("Consolas", 11, "bold")
        self.font_header = ("Consolas", 11, "bold")
        self.font_legend = ("Consolas", 9)
    
    def _bind_events(self):
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)
        self.bind("<Map>", lambda e: self._refresh_theme())
    
    def _refresh_theme(self):
        self._theme_colors = self._get_theme_colors()
        self.canvas.configure(bg=self._theme_colors["canvas_bg"])
        if self.steps:
            self.render_step(self.current_step)
    
    def toggle_staircase(self) -> bool:
        self.force_staircase = not self.force_staircase
        if self.steps:
            self.render_step(self.current_step)
        return self.force_staircase

    def _update_scrollbars(self):
        bbox = self.canvas.bbox("all")
        if not bbox:
            self.scroll_x.grid_remove()
            self.scroll_y.grid_remove()
            return
        
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        
        # Mostrar barra horizontal solo si el contenido desborda el ancho visible
        if bbox[2] + 30 > cw and cw > 50:
            self.scroll_x.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 6))
        else:
            self.scroll_x.grid_remove()
            
        # Mostrar barra vertical solo si el contenido desborda la altura visible
        if bbox[3] + 30 > ch and ch > 50:
            self.scroll_y.grid(row=0, column=1, sticky="ns", padx=(0, 6), pady=6)
        else:
            self.scroll_y.grid_remove()
            
        sr_w = max(cw, bbox[2] + 30)
        sr_h = max(ch, bbox[3] + 30)
        self.canvas.configure(scrollregion=(0, 0, sr_w, sr_h))

    def _on_resize(self, event):
        self._update_scrollbars()
    
    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
    
    def load_steps(self, steps: List[MatrixStep]):
        self.steps = steps
        self.current_step = 0
        if steps:
            self.render_step(0)
    
    def render_step(self, step_index: int):
        if not self.steps or step_index >= len(self.steps):
            return
        
        self.current_step = step_index
        step = self.steps[step_index]
        
        self.canvas.delete("all")
        self.cell_rects = []
        self.cell_texts = []
        self.cell_states = []
        
        matriz = step.matriz
        rows = len(matriz)
        cols = len(matriz[0]) if rows > 0 else 0
        num_vars = cols - 1
        
        self.cell_states = [[CellState.NORMAL for _ in range(cols)] for _ in range(rows)]
        
        # 1. Pivote actual
        if step.pivot_row >= 0 and step.pivot_col >= 0:
            if step.is_normalized:
                self.cell_states[step.pivot_row][step.pivot_col] = CellState.PIVOT_NORMALIZED
            else:
                self.cell_states[step.pivot_row][step.pivot_col] = CellState.PIVOT_CURRENT
                
            for c in range(cols):
                if c != step.pivot_col:
                    self.cell_states[step.pivot_row][c] = CellState.ROW_PIVOT
        
        # 2. Ceros nuevos abajo
        for (r, c) in step.zeros_created:
            if self.cell_states[r][c] == CellState.NORMAL:
                self.cell_states[r][c] = CellState.ZERO_NEW
                
        # 3. Ceros nuevos arriba (Gauss-Jordan)
        for (r, c) in step.zeros_above_created:
            if self.cell_states[r][c] == CellState.NORMAL or self.cell_states[r][c] == CellState.ROW_PIVOT:
                self.cell_states[r][c] = CellState.ZERO_ABOVE
        
        # 4. Términos independientes
        for r in range(rows):
            if self.cell_states[r][num_vars] in (CellState.NORMAL, CellState.ROW_PIVOT):
                self.cell_states[r][num_vars] = CellState.INDEPENDENT
        
        # 5. Ceros preexistentes
        for r in range(rows):
            for c in range(cols):
                if self.cell_states[r][c] == CellState.NORMAL:
                    val = matriz[r][c]
                    if abs(val) < 1e-10:
                        self.cell_states[r][c] = CellState.ZERO_EXISTING
        
        self._draw_matrix(matriz, rows, cols, num_vars, step.descripcion, show_staircase=step.show_staircase)
        self._update_scrollbars()
        
        if self.on_step_change:
            self.on_step_change(step_index, step)
    
    def _draw_matrix(self, matriz: List[List[float]], rows: int, cols: int, num_vars: int, descripcion: str, show_staircase: bool = False):
        x_start = self.padding + self.row_label_width
        y_header = self.padding + 34
        y_start = y_header + self.header_height + 2
        
        self._draw_header(descripcion, x_start, y_header, cols, num_vars)
        
        for r in range(rows):
            y = y_start + r * (self.cell_height + 1)
            self._draw_row_label(r, self.padding, y)
            
            for c in range(cols):
                x = x_start + c * (self.cell_width + 1)
                self._draw_cell(r, c, x, y, matriz[r][c])
        
        draw_stair = show_staircase or self.force_staircase
        if draw_stair:
            self._draw_staircase(matriz, rows, cols, num_vars)
            
        self._draw_legend(x_start, y_start + rows * (self.cell_height + 1) + 20, num_vars, show_staircase=draw_stair)

    def _draw_staircase(self, matriz: List[List[float]], rows: int, cols: int, num_vars: int):
        """Dibuja la línea de la escalera (patrón escalonado) con un color ámbar/dorado llamativo."""
        pivotes: List[Tuple[int, int]] = []
        for r in range(rows):
            for c in range(num_vars):
                if abs(matriz[r][c]) > 1e-10:
                    pivotes.append((r, c))
                    break
        
        if not pivotes:
            return
            
        x_start = self.padding + self.row_label_width
        y_header = self.padding + 34
        y_start = y_header + self.header_height + 2
        stair_color = self._theme_colors.get("staircase", "#f59e0b")
        
        points: List[Tuple[int, int]] = []
        first_r, first_c = pivotes[0]
        
        px_first = x_start + first_c * (self.cell_width + 1)
        py_first = y_start + first_r * (self.cell_height + 1)
        
        if first_c > 0:
            points.append((x_start, py_first))
            points.append((px_first, py_first))
        else:
            points.append((px_first, py_first))
            
        for i, (r, c) in enumerate(pivotes):
            px = x_start + c * (self.cell_width + 1)
            py_top = y_start + r * (self.cell_height + 1)
            py_bot = py_top + self.cell_height + 1
            
            # Línea vertical: baja por el lado izquierdo de la celda pivote
            points.append((px, py_bot))
            
            # Línea horizontal: se extiende bajo el pivote hasta la columna del siguiente o fin de vars
            if i + 1 < len(pivotes):
                next_px = x_start + pivotes[i + 1][1] * (self.cell_width + 1)
                points.append((next_px, py_bot))
            else:
                end_px = x_start + num_vars * (self.cell_width + 1)
                points.append((end_px, py_bot))
                
        # Trazar la escalera con línea ancha destacada (ancho=4)
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            self.canvas.create_line(
                p1[0], p1[1], p2[0], p2[1],
                fill=stair_color, width=4, capstyle="round", joinstyle="round"
            )
            
        # Marcadores redondeados en el vértice superior izquierdo de cada escalón
        for (r, c) in pivotes:
            cx = x_start + c * (self.cell_width + 1)
            cy = y_start + r * (self.cell_height + 1)
            self.canvas.create_oval(
                cx - 3, cy - 3, cx + 4, cy + 4,
                fill="#ffffff", outline=stair_color, width=2
            )
    
    def _draw_header(self, descripcion: str, x: int, y: int, cols: int, num_vars: int):
        self.canvas.create_text(
            x, y - 18, text=f"• {descripcion}", anchor="w",
            font=("Consolas", 12, "bold"), fill=self._theme_colors["header_fg"]
        )
        
        for c in range(cols):
            cx = x + c * (self.cell_width + 1) + self.cell_width // 2
            if c < num_vars:
                label = f"x{a_subindice(c+1)}"
                color = self._theme_colors["header_fg"]
            else:
                label = "="
                color = self._theme_colors["independent_fg"]
            
            self.canvas.create_rectangle(
                x + c * (self.cell_width + 1), y,
                x + (c + 1) * (self.cell_width + 1), y + self.header_height,
                fill=self._theme_colors["header_bg"], outline=self._theme_colors["grid_color"]
            )
            self.canvas.create_text(
                cx, y + self.header_height // 2, text=label,
                font=self.font_header, fill=color
            )
        
        sep_x = x + num_vars * (self.cell_width + 1) - 1
        self.canvas.create_line(
            sep_x, y, sep_x, y + self.header_height,
            fill=self._theme_colors["independent_fg"], width=2, dash=(4, 2)
        )
    
    def _draw_row_label(self, row: int, x: int, y: int):
        self.canvas.create_rectangle(
            x, y, x + self.row_label_width, y + self.cell_height,
            fill=self._theme_colors["header_bg"], outline=self._theme_colors["grid_color"]
        )
        self.canvas.create_text(
            x + self.row_label_width // 2, y + self.cell_height // 2,
            text=f"F{a_subindice(row+1)}", font=self.font_bold, fill=self._theme_colors["header_fg"]
        )
    
    def _draw_cell(self, row: int, col: int, x: int, y: int, value: float):
        state = self.cell_states[row][col]
        style = self._get_cell_style(state)
        
        rect = self.canvas.create_rectangle(
            x, y, x + self.cell_width, y + self.cell_height,
            fill=style.bg, outline=style.border_color if style.border_color else self._theme_colors["grid_color"],
            width=style.border_width if style.border_width > 0 else 1
        )
        
        display_val = self._format_value(value)
        text_color = style.fg
        font = self.font_bold if style.font_weight == "bold" else self.font_normal
        
        text = self.canvas.create_text(
            x + self.cell_width // 2, y + self.cell_height // 2,
            text=display_val, font=font, fill=text_color
        )
        
        if len(self.cell_rects) <= row:
            self.cell_rects.append([])
            self.cell_texts.append([])
        self.cell_rects[row].append(rect)
        self.cell_texts[row].append(text)
    
    def _get_cell_style(self, state: CellState) -> CellStyle:
        colors = self._theme_colors
        if state == CellState.PIVOT_CURRENT:
            return CellStyle(colors["pivot_current"], colors["pivot_current_fg"], "bold", colors["border_pivot"], 2)
        elif state == CellState.PIVOT_NORMALIZED:
            return CellStyle(colors["pivot_normalized"], colors["pivot_normalized_fg"], "bold", colors["border_normalized"], 2)
        elif state == CellState.PIVOT_PREVIOUS:
            return CellStyle(colors["pivot_previous"], colors["pivot_previous_fg"], "bold", colors["border_pivot"], 1)
        elif state == CellState.ZERO_NEW:
            return CellStyle(colors["zero_new"], colors["zero_new_fg"], "bold", colors["border_zero"], 2)
        elif state == CellState.ZERO_ABOVE:
            return CellStyle(colors["zero_above"], colors["zero_above_fg"], "bold", colors["border_above"], 2)
        elif state == CellState.ZERO_EXISTING:
            return CellStyle(colors["zero_existing"], colors["zero_existing_fg"], "normal", "", 0)
        elif state == CellState.ROW_PIVOT:
            return CellStyle(colors["row_pivot"], colors["row_pivot_fg"], "bold", "", 0)
        elif state == CellState.INDEPENDENT:
            return CellStyle(colors["independent_bg"], colors["independent_fg"], "bold", colors["border_indep"], 1)
        else:
            return CellStyle(colors["cell_normal"], colors["cell_normal_fg"], "normal", colors["grid_color"], 1)
    
    def _format_value(self, value: float) -> str:
        return formatear_fraccion(value)
    
    def _draw_legend(self, x: int, y: int, num_vars: int, show_staircase: bool = False):
        legends = [
            ("■ Pivote activo (Gauss)", self._theme_colors["pivot_current_fg"]),
            ("■ Pivote normalizado = 1 (Jordan)", self._theme_colors["pivot_normalized_fg"]),
            ("■ Cero bajo pivote (REF)", self._theme_colors["zero_new_fg"]),
            ("■ Cero sobre pivote (RREF)", self._theme_colors["zero_above_fg"]),
            ("■ Fila del pivote", self._theme_colors["row_pivot_fg"]),
            ("■ Término independiente", self._theme_colors["independent_fg"]),
        ]
        if show_staircase:
            legends.insert(0, ("▬▬ Escalera de Gauss (Forma Escalonada)", self._theme_colors["staircase"]))
        
        box_w = 285 if show_staircase else 260
        box_h = len(legends) * 22 + 14
        
        self.canvas.create_rectangle(
            x - 5, y - 5, x + box_w, y + box_h,
            fill=self._theme_colors["legend_bg"], outline=self._theme_colors["grid_color"], width=1
        )
        
        for i, (label, color) in enumerate(legends):
            ly = y + i * 22 + 10
            self.canvas.create_text(x + 12, ly, text=label, anchor="w", font=self.font_legend, fill=color)
    
    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.render_step(self.current_step + 1)
    
    def prev_step(self):
        if self.current_step > 0:
            self.render_step(self.current_step - 1)
    
    def first_step(self):
        self.render_step(0)
    
    def last_step(self):
        self.render_step(len(self.steps) - 1)
    
    def play(self):
        if self.is_playing:
            return
        self.is_playing = True
        self._animate()
    
    def pause(self):
        self.is_playing = False
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
    
    def _animate(self):
        if not self.is_playing or self.current_step >= len(self.steps) - 1:
            self.is_playing = False
            return
        
        self.next_step()
        delay = int(1400 / self.play_speed)
        self.animation_id = self.after(delay, self._animate)
    
    def set_speed(self, speed: float):
        self.play_speed = max(0.25, min(4.0, speed))
    
    def get_current_step_info(self) -> Tuple[int, int, Optional[MatrixStep]]:
        if not self.steps:
            return 0, 0, None
        return self.current_step + 1, len(self.steps), self.steps[self.current_step]


class PlaybackControls(ctk.CTkFrame):
    def __init__(self, master, canvas: MatrixCanvas, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas = canvas
        self._setup_ui()
    
    def _setup_ui(self):
        self.btn_first = ctk.CTkButton(self, text="⏮", width=38, height=32, command=self.canvas.first_step)
        self.btn_first.pack(side="left", padx=2)
        
        self.btn_prev = ctk.CTkButton(self, text="◀", width=38, height=32, command=self.canvas.prev_step)
        self.btn_prev.pack(side="left", padx=2)
        
        self.btn_play = ctk.CTkButton(self, text="▶", width=44, height=32, command=self._toggle_play, fg_color="#0284c7", hover_color="#0369a1")
        self.btn_play.pack(side="left", padx=4)
        
        self.btn_next = ctk.CTkButton(self, text="▶|", width=38, height=32, command=self.canvas.next_step)
        self.btn_next.pack(side="left", padx=2)
        
        self.btn_last = ctk.CTkButton(self, text="⏭", width=38, height=32, command=self.canvas.last_step)
        self.btn_last.pack(side="left", padx=2)
        
        ctk.CTkLabel(self, text="  Velocidad:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(10, 2))
        self.speed_var = ctk.StringVar(value="1.0x")
        self.speed_menu = ctk.CTkOptionMenu(
            self, values=["0.25x", "0.5x", "1.0x", "1.5x", "2.0x", "3.0x"],
            variable=self.speed_var, width=78, height=32, command=self._on_speed_change
        )
        self.speed_menu.pack(side="left", padx=2)
        
        self.step_label = ctk.CTkLabel(self, text="Paso 0 / 0", font=ctk.CTkFont(family="Consolas", size=13, weight="bold"))
        self.step_label.pack(side="left", padx=14)
        
        # Botones de salto directo a Forma Escalonada (REF) y Reducida (RREF)
        self.btn_rref = ctk.CTkButton(
            self, text="🎯 RREF (Final)", width=105, height=30,
            command=self._go_to_rref,
            fg_color=("#059669", "#047857"), hover_color=("#047857", "#065f46"),
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.btn_rref.pack(side="right", padx=3)

        self.btn_ref = ctk.CTkButton(
            self, text="🪜 REF (Escalonada)", width=125, height=30,
            command=self._go_to_ref,
            fg_color=("#d97706", "#b45309"), hover_color=("#b45309", "#92400e"),
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.btn_ref.pack(side="right", padx=3)

        self.btn_toggle_stair = ctk.CTkButton(
            self, text="🪜 Escalera: AUTO", width=110, height=30,
            command=self._toggle_staircase,
            fg_color=("#334155", "#1e293b"), hover_color=("#475569", "#334155"),
            font=ctk.CTkFont(size=11)
        )
        self.btn_toggle_stair.pack(side="right", padx=3)

        self.desc_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12), wraplength=380, anchor="w", justify="left")
        self.desc_label.pack(side="left", padx=8, fill="x", expand=True)
        
        self.canvas.on_step_change = self._on_step_change

    def _go_to_ref(self):
        for idx, step in enumerate(self.canvas.steps):
            if "Forma Escalonada por Filas" in step.descripcion or "(REF)" in step.descripcion:
                self.canvas.render_step(idx)
                return
        self.canvas.first_step()
        
    def _go_to_rref(self):
        self.canvas.last_step()
        
    def _toggle_staircase(self):
        is_on = self.canvas.toggle_staircase()
        self.btn_toggle_stair.configure(
            text=f"🪜 Escalera: {'ON' if is_on else 'OFF'}",
            fg_color=("#b45309", "#d97706") if is_on else ("#334155", "#1e293b")
        )
    
    def _toggle_play(self):
        if self.canvas.is_playing:
            self.canvas.pause()
            self.btn_play.configure(text="▶")
        else:
            self.canvas.play()
            self.btn_play.configure(text="⏸")
    
    def _on_speed_change(self, value: str):
        speed = float(value.replace("x", ""))
        self.canvas.set_speed(speed)
    
    def _on_step_change(self, step_index: int, step: MatrixStep):
        current, total, _ = self.canvas.get_current_step_info()
        self.step_label.configure(text=f"Paso {current} / {total}")
        self.desc_label.configure(text=step.descripcion)
        
        if current == total:
            self.btn_play.configure(text="▶")
            self.canvas.is_playing = False


def create_matrix_steps_from_gauss(pasos_gauss, matriz_original) -> List[MatrixStep]:
    steps = []
    
    for i, paso in enumerate(pasos_gauss):
        matriz = paso.matriz_estado
        desc = paso.descripcion
        
        pivot_row = -1
        pivot_col = -1
        is_normalized = False
        zeros_created = []
        zeros_above_created = []
        
        # Comparación con matriz anterior para detectar ceros creados
        if i > 0:
            prev_m = pasos_gauss[i-1].matriz_estado
            for r in range(len(matriz)):
                for c in range(len(matriz[0]) - 1):
                    if abs(prev_m[r][c]) > 1e-10 and abs(matriz[r][c]) < 1e-10:
                        if "arriba" in desc.lower():
                            zeros_above_created.append((r, c))
                        else:
                            zeros_created.append((r, c))
        
        if "Normalización" in desc:
            is_normalized = True
            parts = desc.split("Fila ")
            if len(parts) > 1:
                try:
                    pivot_row = int(parts[1].split(" ")[0]) - 1
                    for c in range(len(matriz[0]) - 1):
                        if abs(matriz[pivot_row][c] - 1.0) < 1e-10:
                            pivot_col = c
                            break
                except Exception:
                    pass
        elif "Pivoteo" in desc:
            parts = desc.split("fila ")
            if len(parts) > 1:
                try:
                    pivot_row = int(parts[1].split(" ")[0]) - 1
                    for c in range(len(matriz[0]) - 1):
                        if abs(matriz[pivot_row][c]) > 1e-10:
                            pivot_col = c
                            break
                except Exception:
                    pass
        elif "Eliminación hacia arriba" in desc:
            parts = desc.split("Fila ")
            if len(parts) > 1:
                try:
                    pivot_row = int(parts[1].split(",")[0]) - 1
                    col_part = desc.split("Columna ")
                    if len(col_part) > 1:
                        pivot_col = int(col_part[1].replace(")", "").strip()) - 1
                except Exception:
                    pass
        elif "Eliminación" in desc:
            parts = desc.split("Fila ")
            if len(parts) > 1:
                try:
                    pivot_row = int(parts[1].split(",")[0]) - 1
                    col_part = desc.split("Columna ")
                    if len(col_part) > 1:
                        pivot_col = int(col_part[1].replace(")", "").strip()) - 1
                except Exception:
                    pass
            if pivot_row == -1:
                parts2 = desc.split("fila ")
                if len(parts2) > 1:
                    try:
                        pivot_row = int(parts2[1].split(" ")[0]) - 1
                        for c in range(len(matriz[0]) - 1):
                            if abs(matriz[pivot_row][c]) > 1e-10:
                                pivot_col = c
                                break
                    except Exception:
                        pass
        
        show_staircase = (
            "Escalonada" in desc or
            "REF" in desc or
            "RREF" in desc or
            "Escalera" in desc or
            i == len(pasos_gauss) - 1
        )
        
        steps.append(MatrixStep(
            matriz=matriz,
            descripcion=desc,
            pivot_row=pivot_row,
            pivot_col=pivot_col,
            is_normalized=is_normalized,
            zeros_created=zeros_created,
            zeros_above_created=zeros_above_created,
            show_staircase=show_staircase
        ))
    
    return steps