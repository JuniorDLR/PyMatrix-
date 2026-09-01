import customtkinter as ctk
import tkinter as tk
from typing import List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import math


class CellState(Enum):
    NORMAL = "normal"
    PIVOT_CURRENT = "pivot_current"
    PIVOT_PREVIOUS = "pivot_previous"
    ZERO_NEW = "zero_new"
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
    zeros_created: List[Tuple[int, int]] = field(default_factory=list)
    row_swapped: Tuple[int, int] = None


class MatrixCanvas(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self._theme_colors = self._get_theme_colors()
        
        self.canvas = tk.Canvas(
            self,
            bg=self._theme_colors["canvas_bg"],
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.scroll_x = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)
        self.scroll_x.pack(fill="x", padx=10, pady=(0, 10))
        self.scroll_y = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side="right", fill="y", padx=(0, 10), pady=10)
        
        self.canvas.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
        
        self.steps: List[MatrixStep] = []
        self.current_step = 0
        self.cell_rects: List[List[int]] = []
        self.cell_texts: List[List[int]] = []
        self.cell_states: List[List[CellState]] = []
        
        self.cell_width = 70
        self.cell_height = 40
        self.padding = 8
        self.header_height = 35
        self.row_label_width = 50
        
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
                "canvas_bg": "#1a1a2e",
                "cell_normal": "#16213e",
                "cell_normal_fg": "#eaeaea",
                "pivot_current": "#0f3460",
                "pivot_current_fg": "#00d9ff",
                "pivot_previous": "#1a1a2e",
                "pivot_previous_fg": "#00d9ff",
                "zero_new": "#0f3460",
                "zero_new_fg": "#00ff88",
                "zero_existing": "#16213e",
                "zero_existing_fg": "#888888",
                "row_pivot": "#0f3460",
                "row_pivot_fg": "#ffd700",
                "independent_bg": "#0f3460",
                "independent_fg": "#ff6b6b",
                "header_bg": "#0f3460",
                "header_fg": "#00d9ff",
                "grid_color": "#2a2a4a",
                "border_pivot": "#00d9ff",
                "border_zero": "#00ff88",
                "legend_bg": "#16213e",
                "legend_fg": "#eaeaea",
            }
        else:
            return {
                "canvas_bg": "#f0f0f5",
                "cell_normal": "#ffffff",
                "cell_normal_fg": "#1a1a2e",
                "pivot_current": "#dbeafe",
                "pivot_current_fg": "#1e40af",
                "pivot_previous": "#eff6ff",
                "pivot_previous_fg": "#1e40af",
                "zero_new": "#dcfce7",
                "zero_new_fg": "#166534",
                "zero_existing": "#f3f4f6",
                "zero_existing_fg": "#9ca3af",
                "row_pivot": "#fef3c7",
                "row_pivot_fg": "#92400e",
                "independent_bg": "#fee2e2",
                "independent_fg": "#dc2626",
                "header_bg": "#dbeafe",
                "header_fg": "#1e40af",
                "grid_color": "#e5e7eb",
                "border_pivot": "#3b82f6",
                "border_zero": "#22c55e",
                "legend_bg": "#f3f4f6",
                "legend_fg": "#1f2937",
            }
    
    def _setup_fonts(self):
        self.font_normal = ("Consolas", 11)
        self.font_bold = ("Consolas", 11, "bold")
        self.font_header = ("Consolas", 10, "bold")
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
    
    def _on_resize(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
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
        
        if step.pivot_row >= 0 and step.pivot_col >= 0:
            self.cell_states[step.pivot_row][step.pivot_col] = CellState.PIVOT_CURRENT
            for c in range(cols):
                if c != step.pivot_col:
                    self.cell_states[step.pivot_row][c] = CellState.ROW_PIVOT
        
        for (r, c) in step.zeros_created:
            if self.cell_states[r][c] == CellState.NORMAL:
                self.cell_states[r][c] = CellState.ZERO_NEW
        
        for r in range(rows):
            if self.cell_states[r][num_vars] == CellState.NORMAL:
                self.cell_states[r][num_vars] = CellState.INDEPENDENT
        
        for r in range(rows):
            for c in range(cols):
                if self.cell_states[r][c] == CellState.NORMAL:
                    val = matriz[r][c]
                    if abs(val) < 1e-10:
                        self.cell_states[r][c] = CellState.ZERO_EXISTING
        
        if step.pivot_row >= 0 and step.pivot_col >= 0:
            for r in range(step.pivot_row):
                if self.cell_states[r][step.pivot_col] == CellState.ZERO_EXISTING:
                    self.cell_states[r][step.pivot_col] = CellState.PIVOT_PREVIOUS
        
        self._draw_matrix(matriz, rows, cols, num_vars, step.descripcion)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        if self.on_step_change:
            self.on_step_change(step_index, step)
    
    def _draw_matrix(self, matriz: List[List[float]], rows: int, cols: int, num_vars: int, descripcion: str):
        x_start = self.padding + self.row_label_width
        y_start = self.padding + self.header_height
        
        self._draw_header(descripcion, x_start, self.padding, cols, num_vars)
        
        for r in range(rows):
            y = y_start + r * (self.cell_height + 1)
            
            self._draw_row_label(r, self.padding, y)
            
            for c in range(cols):
                x = x_start + c * (self.cell_width + 1)
                self._draw_cell(r, c, x, y, matriz[r][c])
        
        self._draw_legend(x_start, y_start + rows * (self.cell_height + 1) + 15, num_vars)
    
    def _draw_header(self, descripcion: str, x: int, y: int, cols: int, num_vars: int):
        self.canvas.create_text(
            x, y - 25, text=descripcion, anchor="w",
            font=("Consolas", 12, "bold"), fill=self._theme_colors["header_fg"]
        )
        
        for c in range(cols):
            cx = x + c * (self.cell_width + 1) + self.cell_width // 2
            if c < num_vars:
                label = f"X{c+1}"
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
            text=f"R{row+1}", font=self.font_bold, fill=self._theme_colors["header_fg"]
        )
    
    def _draw_cell(self, row: int, col: int, x: int, y: int, value: float):
        state = self.cell_states[row][col]
        style = self._get_cell_style(state)
        
        rect = self.canvas.create_rectangle(
            x, y, x + self.cell_width, y + self.cell_height,
            fill=style.bg, outline=style.border_color, width=style.border_width
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
        elif state == CellState.PIVOT_PREVIOUS:
            return CellStyle(colors["pivot_previous"], colors["pivot_previous_fg"], "bold", colors["border_pivot"], 1)
        elif state == CellState.ZERO_NEW:
            return CellStyle(colors["zero_new"], colors["zero_new_fg"], "bold", colors["border_zero"], 2)
        elif state == CellState.ZERO_EXISTING:
            return CellStyle(colors["zero_existing"], colors["zero_existing_fg"], "normal", "", 0)
        elif state == CellState.ROW_PIVOT:
            return CellStyle(colors["row_pivot"], colors["row_pivot_fg"], "bold", "", 0)
        elif state == CellState.INDEPENDENT:
            return CellStyle(colors["independent_bg"], colors["independent_fg"], "bold", "", 0)
        else:
            return CellStyle(colors["cell_normal"], colors["cell_normal_fg"], "normal", colors["grid_color"], 1)
    
    def _format_value(self, value: float) -> str:
        if abs(value) < 1e-10:
            return "0"
        if abs(value - round(value)) < 1e-9:
            return str(int(round(value)))
        return f"{value:.3f}".rstrip('0').rstrip('.')
    
    def _draw_legend(self, x: int, y: int, num_vars: int):
        legends = [
            ("■ Pivote actual", self._theme_colors["pivot_current_fg"]),
            ("■ Pivote previo", self._theme_colors["pivot_previous_fg"]),
            ("■ Cero generado", self._theme_colors["zero_new_fg"]),
            ("■ Cero existente", self._theme_colors["zero_existing_fg"]),
            ("■ Fila pivote", self._theme_colors["row_pivot_fg"]),
            ("■ Término indep.", self._theme_colors["independent_fg"]),
        ]
        
        box_w = 180
        box_h = len(legends) * 22 + 10
        
        self.canvas.create_rectangle(
            x - 5, y - 5, x + box_w, y + box_h,
            fill=self._theme_colors["legend_bg"], outline=self._theme_colors["grid_color"], width=1
        )
        
        for i, (label, color) in enumerate(legends):
            ly = y + i * 22
            self.canvas.create_text(x + 10, ly, text=label, anchor="w", font=self.font_legend, fill=color)
    
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
        delay = int(1500 / self.play_speed)
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
        self.btn_first = ctk.CTkButton(self, text="⏮", width=40, command=self.canvas.first_step)
        self.btn_first.pack(side="left", padx=2)
        
        self.btn_prev = ctk.CTkButton(self, text="◀", width=40, command=self.canvas.prev_step)
        self.btn_prev.pack(side="left", padx=2)
        
        self.btn_play = ctk.CTkButton(self, text="▶", width=40, command=self._toggle_play)
        self.btn_play.pack(side="left", padx=2)
        
        self.btn_next = ctk.CTkButton(self, text="▶", width=40, command=self.canvas.next_step)
        self.btn_next.pack(side="left", padx=2)
        
        self.btn_last = ctk.CTkButton(self, text="⏭", width=40, command=self.canvas.last_step)
        self.btn_last.pack(side="left", padx=2)
        
        ctk.CTkLabel(self, text="  Velocidad:").pack(side="left", padx=(10, 2))
        self.speed_var = ctk.StringVar(value="1.0x")
        self.speed_menu = ctk.CTkOptionMenu(
            self, values=["0.25x", "0.5x", "1.0x", "1.5x", "2.0x", "3.0x", "4.0x"],
            variable=self.speed_var, width=70, command=self._on_speed_change
        )
        self.speed_menu.pack(side="left", padx=2)
        
        self.step_label = ctk.CTkLabel(self, text="Paso 0 / 0", font=("Consolas", 12))
        self.step_label.pack(side="left", padx=20)
        
        self.desc_label = ctk.CTkLabel(self, text="", font=("Consolas", 11), wraplength=400)
        self.desc_label.pack(side="left", padx=10, fill="x", expand=True)
        
        self.canvas.on_step_change = self._on_step_change
    
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
        zeros_created = []
        
        if "Pivoteo" in desc:
            parts = desc.split("fila ")
            if len(parts) > 1:
                try:
                    pivot_row = int(parts[1].split(" ")[0]) - 1
                    for c in range(len(matriz[0])):
                        if abs(matriz[pivot_row][c]) > 1e-10:
                            pivot_col = c
                            break
                except:
                    pass
        elif "Eliminación" in desc:
            parts = desc.split("fila ")
            if len(parts) > 1:
                try:
                    pivot_row = int(parts[1].split(" ")[0]) - 1
                    for c in range(len(matriz[0])):
                        if abs(matriz[pivot_row][c]) > 1e-10:
                            pivot_col = c
                            break
                    
                    if i > 0:
                        prev_matriz = pasos_gauss[i-1].matriz_estado
                        for r in range(pivot_row + 1, len(matriz)):
                            for c in range(pivot_col, len(matriz[0])):
                                if abs(prev_matriz[r][c]) > 1e-10 and abs(matriz[r][c]) < 1e-10:
                                    zeros_created.append((r, c))
                except:
                    pass
        
        steps.append(MatrixStep(
            matriz=matriz,
            descripcion=desc,
            pivot_row=pivot_row,
            pivot_col=pivot_col,
            zeros_created=zeros_created
        ))
    
    return steps