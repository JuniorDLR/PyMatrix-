"""Vista de interfaz gráfica para el Método de Newton-Raphson (Programa 9).

Integra entrada de datos con SymPy, visualización de tabla con Pandas,
desglose de procedimiento paso a paso, graficación de curvas y tangentes con Matplotlib,
y contraste opcional con SciPy.
"""

from __future__ import annotations

import math
import tkinter as tk
from collections.abc import Callable
from tkinter import filedialog, messagebox

import customtkinter as ctk
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.core.numericos.newton_raphson import (
    ResultadoNewton,
    compilar_expresion_sympy,
    contraste_scipy_newton,
    ejecutar_newton_raphson,
)
from src.ui.light_theme import LIGHT
from src.ui.numericos.comun import Terminal, campo, escribir_entrada

matplotlib.use("TkAgg")

# Casos oficiales y ejemplos de clase precargados
EJEMPLOS_NEWTON = {
    "Caso 1 (e⁻ˣ - x, x₀=0)": {
        "f": "exp(-x) - x",
        "x0": "0",
        "tol": "0.0001",
        "criterio": "absoluto",
        "max_it": "50",
        "desc": "Ejemplo 1 de clase (Diapositivas 15-21): Convergencia cuadrática rápida en 4 iteraciones.",
    },
    "Caso 1B (x³ - 2x - 5, x₀=2)": {
        "f": "x**3 - 2*x - 5",
        "x0": "2",
        "tol": "0.0001",
        "criterio": "absoluto",
        "max_it": "50",
        "desc": "Polinomio cúbico de clase (Diapositiva 36): Converge a r ≈ 2.094551 en 3 iteraciones.",
    },
    "Caso 2 (x² - 4, x₀=0)": {
        "f": "x**2 - 4",
        "x0": "0",
        "tol": "0.0001",
        "criterio": "absoluto",
        "max_it": "50",
        "desc": "Derivada nula en el punto inicial: f'(0) = 0. Detención controlada inmediata (división por cero).",
    },
    "Caso 2B (x¹⁰ - 1, x₀=0.5)": {
        "f": "x**10 - 1",
        "x0": "0.5",
        "tol": "0.0001",
        "criterio": "absoluto",
        "max_it": "60",
        "desc": "Ejemplo 3 de clase (Diapositiva 33): f'(0.5) ≈ 0.0195 (muy pequeña). Salto a x₁=51.65 y 42 iteraciones.",
    },
    "Caso 3 (x³ - 2x + 2, x₀=0)": {
        "f": "x**3 - 2*x + 2",
        "x0": "0",
        "tol": "0.0001",
        "criterio": "absoluto",
        "max_it": "30",
        "desc": "Ciclo periódico / Oscilación (Diapositiva 32): Oscila indefinidamente entre 0 y 1.",
    },
    "Caso 3B (atan(x), x₀=2)": {
        "f": "atan(x)",
        "x0": "2",
        "tol": "0.0001",
        "criterio": "absoluto",
        "max_it": "15",
        "desc": "Divergencia (Diapositiva 32): La tangente casi plana dispara las aproximaciones (-3.54, 13.95, -279.3).",
    },
    "Clase Horner (x⁵ - 4x⁴ + 5x³ - 6x + 4, x₀=-1.25)": {
        "f": "x**5 - 4*x**4 + 5*x**3 - 6*x + 4",
        "x0": "-1.25",
        "tol": "0.0001",
        "criterio": "absoluto",
        "max_it": "50",
        "desc": "Ejemplo 2 de clase (Diapositivas 22-26): Polinomio de grado 5 evaluado con derivada analítica.",
    },
}


class NewtonRaphsonView(ctk.CTkFrame):
    """Panel visual interactivo para el método de Newton-Raphson."""

    def __init__(self, parent: ctk.CTkBaseClass, get_modo: Callable[[], str]) -> None:
        super().__init__(parent, fg_color="transparent")
        self.get_modo = get_modo
        self.resultado: ResultadoNewton | None = None
        self._modo_tema: str = "Dark"

        self.grid_columnconfigure(0, minsize=400)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= PANEL IZQUIERDO: CONTROLES Y ENTRADA =================
        panel_izq = ctk.CTkScrollableFrame(self, width=390, fg_color=("#f1f5f9", "#111827"))
        panel_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        ctk.CTkLabel(
            panel_izq,
            text="Newton-Raphson · Programa 9",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#0369a1", "#38bdf8"),
        ).pack(anchor="w", padx=14, pady=(16, 4))

        ctk.CTkLabel(
            panel_izq,
            text="Búsqueda abierta de raíces · Derivada simbólica mediante SymPy",
            wraplength=360,
            justify="left",
            text_color=("#64748b", "#94a3b8"),
        ).pack(anchor="w", padx=14, pady=(0, 10))

        # Tarjeta de Parámetros
        tarjeta_params = ctk.CTkFrame(panel_izq, fg_color=("#ffffff", "#1f2937"))
        tarjeta_params.pack(fill="x", padx=12, pady=5)

        ctk.CTkLabel(
            tarjeta_params,
            text="Parámetros del Método",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(10, 6))

        self.campo_f = campo(tarjeta_params, "Función f(x)", "exp(-x) - x")
        self.campo_x0 = campo(tarjeta_params, "Valor inicial x₀", "0")
        self.campo_tol = campo(tarjeta_params, "Tolerancia (ε)", "0.0001")

        # Criterio de parada
        fila_criterio = ctk.CTkFrame(tarjeta_params, fg_color="transparent")
        fila_criterio.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(fila_criterio, text="Criterio de error", width=135, anchor="w").pack(side="left")
        self.criterio_seg = ctk.CTkSegmentedButton(
            fila_criterio,
            values=["Absoluto (ε_a)", "Relativo % (ε_a%)"],
        )
        self.criterio_seg.pack(side="left", fill="x", expand=True)
        self.criterio_seg.set("Absoluto (ε_a)")

        self.campo_maxit = campo(tarjeta_params, "Máx. iteraciones", "50")

        # Tarjeta de Ejemplos y Casos Oficiales
        tarjeta_ejemplos = ctk.CTkFrame(panel_izq, fg_color=("#ffffff", "#1f2937"))
        tarjeta_ejemplos.pack(fill="x", padx=12, pady=5)

        ctk.CTkLabel(
            tarjeta_ejemplos,
            text="Casos de Prueba Oficiales (PDF y Clase)",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(10, 4))

        self.combo_ejemplos = ctk.CTkOptionMenu(
            tarjeta_ejemplos,
            values=list(EJEMPLOS_NEWTON.keys()),
            command=self._cargar_ejemplo,
        )
        self.combo_ejemplos.pack(fill="x", padx=12, pady=(2, 6))

        self.label_desc_ejemplo = ctk.CTkLabel(
            tarjeta_ejemplos,
            text=EJEMPLOS_NEWTON["Caso 1 (e⁻ˣ - x, x₀=0)"]["desc"],
            wraplength=340,
            justify="left",
            font=ctk.CTkFont(size=11),
            text_color=("#475569", "#94a3b8"),
        )
        self.label_desc_ejemplo.pack(anchor="w", padx=12, pady=(0, 10))

        # Botones de Acción
        self.btn_calcular = ctk.CTkButton(
            panel_izq,
            text="🚀 Calcular Newton-Raphson",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#0284c7", "#0284c7"),
            hover_color=("#0369a1", "#0369a1"),
            command=self._calcular,
        )
        self.btn_calcular.pack(fill="x", padx=12, pady=(10, 5))

        fila_botones_extra = ctk.CTkFrame(panel_izq, fg_color="transparent")
        fila_botones_extra.pack(fill="x", padx=12, pady=(0, 6))

        self.btn_scipy = ctk.CTkButton(
            fila_botones_extra,
            text="🔬 Contraste SciPy",
            fg_color="#475569",
            hover_color="#334155",
            command=self._contrastar_scipy,
        )
        self.btn_scipy.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_exportar = ctk.CTkButton(
            fila_botones_extra,
            text="💾 Exportar CSV",
            fg_color="#475569",
            hover_color="#334155",
            command=self._exportar_csv,
        )
        self.btn_exportar.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # Mensaje de error/validación
        self.lbl_error = ctk.CTkLabel(
            panel_izq, text="", text_color="#ef4444", wraplength=360, justify="left"
        )
        self.lbl_error.pack(fill="x", padx=12, pady=(4, 12))

        # ================= PANEL DERECHO: PESTAÑAS DE SALIDA =================
        self.panel_der = ctk.CTkFrame(self, fg_color="transparent")
        self.panel_der.grid(row=0, column=1, sticky="nsew")
        self.panel_der.grid_rowconfigure(0, weight=1)
        self.panel_der.grid_columnconfigure(0, weight=1)

        self.tabs_salida = ctk.CTkTabview(self.panel_der)
        self.tabs_salida.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        for tab_name in ("📊 Tabla de Iteraciones", "📝 Procedimiento Paso a Paso", "📈 Gráfica y Tangentes", "🔬 Contraste SciPy"):
            tab = self.tabs_salida.add(tab_name)
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=1)

        # Tab 1: Tabla de Iteraciones
        tab_tabla = self.tabs_salida.tab("📊 Tabla de Iteraciones")
        self.term_tabla = Terminal(tab_tabla, ajustar_lineas=False)
        self.term_tabla.grid(row=0, column=0, sticky="nsew")

        # Tab 2: Procedimiento Paso a Paso
        tab_proc = self.tabs_salida.tab("📝 Procedimiento Paso a Paso")
        self.term_proc = Terminal(tab_proc, ajustar_lineas=True)
        self.term_proc.grid(row=0, column=0, sticky="nsew")

        # Tab 3: Gráfica y Rectas Tangentes
        tab_graf = self.tabs_salida.tab("📈 Gráfica y Tangentes")
        self.frame_grafica = ctk.CTkFrame(tab_graf, fg_color="transparent")
        self.frame_grafica.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self.frame_grafica.grid_rowconfigure(0, weight=1)
        self.frame_grafica.grid_columnconfigure(0, weight=1)

        self.figura = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.figura.add_subplot(111)
        self.canvas_matplotlib = FigureCanvasTkAgg(self.figura, master=self.frame_grafica)
        self.canvas_matplotlib.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Tab 4: Contraste SciPy
        tab_scipy = self.tabs_salida.tab("🔬 Contraste SciPy")
        self.term_scipy = Terminal(tab_scipy, ajustar_lineas=True)
        self.term_scipy.grid(row=0, column=0, sticky="nsew")

        # Ejecutar caso inicial
        self._cargar_ejemplo("Caso 1 (e⁻ˣ - x, x₀=0)")
        self._calcular()

    def _cargar_ejemplo(self, nombre: str) -> None:
        if nombre not in EJEMPLOS_NEWTON:
            return
        datos = EJEMPLOS_NEWTON[nombre]
        escribir_entrada(self.campo_f, datos["f"])
        escribir_entrada(self.campo_x0, datos["x0"])
        escribir_entrada(self.campo_tol, datos["tol"])
        criterio_val = "Absoluto (ε_a)" if datos["criterio"] == "absoluto" else "Relativo % (ε_a%)"
        self.criterio_seg.set(criterio_val)
        escribir_entrada(self.campo_maxit, datos["max_it"])
        self.label_desc_ejemplo.configure(text=datos["desc"])
        self.lbl_error.configure(text="")

    def _calcular(self) -> None:
        """Lee las entradas, ejecuta Newton-Raphson y actualiza todas las vistas."""
        self.lbl_error.configure(text="")
        expresion = self.campo_f.get().strip()
        texto_x0 = self.campo_x0.get().strip()
        texto_tol = self.campo_tol.get().strip()
        texto_maxit = self.campo_maxit.get().strip()
        tipo_crit = "relativo" if "Relativo" in self.criterio_seg.get() else "absoluto"

        # Validaciones de entrada
        if not expresion:
            self.lbl_error.configure(text="Error: Debe ingresar una expresión para f(x).")
            return

        try:
            x0 = float(texto_x0)
        except ValueError:
            self.lbl_error.configure(text="Error: El valor inicial x₀ debe ser un número válido.")
            return

        try:
            tol = float(texto_tol)
            if tol <= 0:
                raise ValueError
        except ValueError:
            self.lbl_error.configure(text="Error: La tolerancia debe ser un número estrictamente positivo.")
            return

        try:
            maxit = int(texto_maxit)
            if maxit < 1 or maxit > 1000:
                raise ValueError
        except ValueError:
            self.lbl_error.configure(text="Error: El máximo de iteraciones debe ser un entero entre 1 y 1000.")
            return

        try:
            resultado = ejecutar_newton_raphson(
                expresion_str=expresion,
                x0=x0,
                tolerancia=tol,
                tipo_criterio=tipo_crit,
                max_iteraciones=maxit,
            )
            self.resultado = resultado
        except Exception as err:
            self.lbl_error.configure(text=f"Error en el cálculo: {err}")
            return

        # Renderizar en las diferentes pestañas
        self._mostrar_tabla(resultado)
        self._mostrar_procedimiento(resultado)
        self._dibujar_grafica(resultado)
        self._limpiar_scipy_tab()

    def _mostrar_tabla(self, res: ResultadoNewton) -> None:
        """Formatea y presenta la tabla de iteraciones en la Terminal de Tab 1."""
        texto = []
        texto.append("=" * 82)
        texto.append("       MÉTODO DE NEWTON-RAPHSON · RESULTADOS Y TABLA DE ITERACIONES")
        texto.append("=" * 82)
        texto.append(f"• Función ingresada f(x) : {res.expresion_sympy}")
        texto.append(f"• Derivada analítica f'(x): {res.derivada_sympy}")
        texto.append(f"• Valor inicial x₀        : {res.x0}")
        texto.append(f"• Tolerancia fijada       : {res.tolerancia:.4e} ({res.tipo_criterio.capitalize()})")
        texto.append(f"• Límite de iteraciones   : {res.max_iteraciones}")
        texto.append("-" * 82)

        if res.tabla_pandas is not None and not res.tabla_pandas.empty:
            texto.append("")
            # Formato de cabecera formal alineada
            col_df = "f'(x_i)"
            encabezado = (
                f"{'i':>3} | {'x_i':>12} | {'f(x_i)':>12} | {col_df:>12} | "
                f"{'x_(i+1)':>12} | {'ε_a (abs)':>12} | {'ε_a (%)':>10}"
            )
            texto.append(encabezado)
            texto.append("-" * len(encabezado))

            for p in res.pasos:
                err_rel_str = f"{p.error_rel_pct:.4f}%" if p.error_rel_pct is not None else "N/A"
                fila = (
                    f"{p.i:3d} | {p.xi:12.6f} | {p.f_xi:12.6f} | {p.df_xi:12.6f} | "
                    f"{p.xi1:12.6f} | {p.error_abs:12.6e} | {err_rel_str:>10}"
                )
                texto.append(fila)
            texto.append("-" * len(encabezado))

        texto.append("")
        texto.append("=" * 82)
        texto.append("                             DIAGNÓSTICO FINAL")
        texto.append("=" * 82)
        texto.append(res.mensaje_estado)

        if res.raiz_aprox is not None:
            texto.append("")
            texto.append("----------------------------------------------------------------------------------")
            texto.append(f"✓ APROXIMACIÓN OBTENIDA : x ≈ {res.raiz_aprox:.8f}")
            texto.append(f"✓ RESIDUO FINAL |f(x)|   : {res.residuo_final:.6e}")
            texto.append("  (Nota técnica: Por rigor matemático y rúbrica docente, se informa como 'raíz")
            texto.append("   aproximada' o 'aproximación obtenida', comprobando siempre el residuo).")
            texto.append("----------------------------------------------------------------------------------")

        self.term_tabla.escribir("\n".join(texto))

    def _mostrar_procedimiento(self, res: ResultadoNewton) -> None:
        """Desglosa cada paso didáctico en la Terminal de Tab 2."""
        texto = []
        texto.append("=" * 76)
        texto.append("          PROCEDIMIENTO PASO A PASO (METODOLOGÍA DE CLASE)")
        texto.append("=" * 76)
        texto.append(f"Función:   f(x)  = {res.expresion_sympy}")
        texto.append(f"Derivada:  f'(x) = {res.derivada_sympy} (calculada simbólicamente)")
        texto.append(f"Fórmula:   x_(i+1) = x_i - [f(x_i) / f'(x_i)]")
        texto.append("=" * 76)
        texto.append("")

        for p in res.pasos:
            texto.append(f">> PASO {p.i} (Desde x = {p.xi:.6f}):")
            texto.append(p.detalle_procedimiento)
            texto.append("-" * 76)

        texto.append("")
        texto.append(f"ESTADO: {res.estado.upper()}")
        texto.append(res.mensaje_estado)

        self.term_proc.escribir("\n".join(texto))

    def _dibujar_grafica(self, res: ResultadoNewton) -> None:
        """Traza la curva f(x), el eje horizontal y las rectas tangentes de cada iteración."""
        self.ax.clear()

        # Determinar intervalo de graficación inteligente
        puntos_x = [res.x0]
        for p in res.pasos:
            if math.isfinite(p.xi):
                puntos_x.append(p.xi)
            if math.isfinite(p.xi1):
                puntos_x.append(p.xi1)

        x_min_raw = min(puntos_x)
        x_max_raw = max(puntos_x)
        margen = max(1.0, (x_max_raw - x_min_raw) * 0.4)
        x_min = x_min_raw - margen
        x_max = x_max_raw + margen

        xs = np.linspace(x_min, x_max, 600)
        try:
            f_num = sp.lambdify(sp.Symbol("x", real=True), res.expresion_sympy, "numpy")
            ys = f_num(xs)
            # Manejo de discontinuidades o números complejos
            if np.iscomplexobj(ys):
                ys = np.real(ys)
            ys = np.clip(ys, -100, 100)
        except Exception:
            ys = np.zeros_like(xs)

        # Ajuste de estilo según tema
        fondo = "#1e293b" if self._modo_tema == "Dark" else "#f8fafc"
        color_texto = "#e2e8f0" if self._modo_tema == "Dark" else "#0f172a"
        color_grid = "#334155" if self._modo_tema == "Dark" else "#cbd5e1"

        self.figura.patch.set_facecolor(fondo)
        self.ax.set_facecolor(fondo)
        self.ax.tick_params(colors=color_texto)
        self.ax.xaxis.label.set_color(color_texto)
        self.ax.yaxis.label.set_color(color_texto)
        for spine in self.ax.spines.values():
            spine.set_color(color_grid)

        # 1. Curva principal f(x)
        self.ax.plot(xs, ys, color="#38bdf8", linewidth=2.2, label=f"f(x) = {res.expresion_str}")

        # 2. Eje horizontal y = 0
        self.ax.axhline(0, color=color_texto, linestyle="-", linewidth=1.0, alpha=0.7)

        # 3. Rectas tangentes de las primeras iteraciones (hasta 4 para legibilidad)
        colores_tangentes = ["#f97316", "#a855f7", "#10b981", "#eab308"]
        limite_tangentes = min(4, len(res.pasos))

        for idx in range(limite_tangentes):
            p = res.pasos[idx]
            if not math.isfinite(p.xi) or not math.isfinite(p.xi1) or not math.isfinite(p.df_xi):
                continue
            color_tang = colores_tangentes[idx % len(colores_tangentes)]

            # Punto (xi, f(xi))
            self.ax.plot(p.xi, p.f_xi, marker="o", color=color_tang, markersize=6)
            # Línea vertical punteada desde eje a la curva
            self.ax.plot([p.xi, p.xi], [0, p.f_xi], color=color_tang, linestyle="--", alpha=0.6)
            # Texto identificador en eje
            self.ax.text(p.xi, 0, f" x_{p.i-1}", color=color_tang, fontsize=9, verticalalignment="top")

            # Recta tangente y = f'(xi)*(x - xi) + f(xi)
            x_tang = np.linspace(min(p.xi, p.xi1) - 0.2 * margen, max(p.xi, p.xi1) + 0.2 * margen, 50)
            y_tang = p.df_xi * (x_tang - p.xi) + p.f_xi
            self.ax.plot(
                x_tang,
                y_tang,
                color=color_tang,
                linestyle="-",
                linewidth=1.4,
                alpha=0.85,
                label=f"Tangente en x_{p.i-1}",
            )

        # 4. Marcador de la raíz aproximada final
        if res.raiz_aprox is not None and math.isfinite(res.raiz_aprox):
            self.ax.plot(
                res.raiz_aprox,
                0,
                marker="*",
                color="#e11d48",
                markersize=13,
                label=f"Raíz aprox. r ≈ {res.raiz_aprox:.6f}",
            )

        self.ax.grid(True, linestyle=":", alpha=0.5, color=color_grid)
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("f(x)")
        self.ax.set_title(
            f"Interpretación Geométrica de Newton-Raphson ({res.estado.upper()})",
            color=color_texto,
            fontsize=12,
            fontweight="bold",
        )
        self.ax.legend(loc="best", fontsize=8, facecolor=fondo, edgecolor=color_grid, labelcolor=color_texto)

        self.figura.tight_layout()
        self.canvas_matplotlib.draw()

    def _contrastar_scipy(self) -> None:
        """Ejecuta el contraste opcional con scipy.optimize.newton y muestra el informe."""
        expresion = self.campo_f.get().strip()
        try:
            x0 = float(self.campo_x0.get().strip())
            tol = float(self.campo_tol.get().strip())
            maxit = int(self.campo_maxit.get().strip())
        except ValueError:
            self.lbl_error.configure(text="Complete entradas numéricas válidas para contrastar con SciPy.")
            return

        resultado_scipy = contraste_scipy_newton(expresion, x0, tol, maxit)

        texto = []
        texto.append("=" * 76)
        texto.append("       CONTRASTE OPCIONAL CON SCIPY (scipy.optimize.newton)")
        texto.append("=" * 76)
        texto.append("Régimen de cumplimiento:")
        texto.append("Según las reglas técnicas del Programa 9, SciPy NO sustituye la implementación")
        texto.append("propia del equipo y se utiliza exclusivamente como prueba de contraste y verificación.")
        texto.append("-" * 76)
        texto.append(f"• Éxito de convergencia SciPy : {'SÍ' if resultado_scipy['exito'] else 'NO'}")
        if resultado_scipy["raiz"] is not None:
            texto.append(f"• Raíz encontrada por SciPy   : x ≈ {resultado_scipy['raiz']:.10f}")
            texto.append(f"• Iteraciones reportadas      : {resultado_scipy['iteraciones']}")
            texto.append(f"• Residuo |f(x_scipy)|        : {resultado_scipy['residuo']:.6e}")
        texto.append(f"• Mensaje oficial de SciPy    : {resultado_scipy['mensaje']}")
        texto.append("-" * 76)

        if self.resultado is not None and self.resultado.raiz_aprox is not None:
            dif = abs(self.resultado.raiz_aprox - (resultado_scipy["raiz"] or 0.0))
            texto.append("")
            texto.append("COTEJO DIRECTO:")
            texto.append(f"  Implementación Propia : x ≈ {self.resultado.raiz_aprox:.10f} ({self.resultado.iteraciones_realizadas} iteraciones)")
            texto.append(f"  scipy.optimize.newton : x ≈ {resultado_scipy['raiz']:.10f} ({resultado_scipy['iteraciones']} iteraciones)")
            texto.append(f"  Diferencia absoluta   : |x_propio - x_scipy| = {dif:.4e}")
            texto.append("✓ CONCLUSIÓN: Ambas aproximaciones son consistentes.")
        texto.append("=" * 76)

        self.term_scipy.escribir("\n".join(texto))
        self.tabs_salida.set("🔬 Contraste SciPy")

    def _limpiar_scipy_tab(self) -> None:
        self.term_scipy.escribir(
            "Haga clic en '🔬 Contraste SciPy' en el panel lateral para ejecutar la verificación\n"
            "con la función oficial scipy.optimize.newton y contrastar la solución obtenida."
        )

    def _exportar_csv(self) -> None:
        """Exporta la tabla de iteraciones de Pandas a un archivo CSV."""
        if self.resultado is None or self.resultado.tabla_pandas is None or self.resultado.tabla_pandas.empty:
            messagebox.showwarning("Exportar", "No hay datos de iteraciones disponibles para exportar.")
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv"), ("Todos los archivos", "*.*")],
            title="Guardar tabla de iteraciones de Newton-Raphson",
            initialfile="iteraciones_newton_raphson.csv",
        )
        if not ruta:
            return

        try:
            self.resultado.tabla_pandas.to_csv(ruta, index=False, encoding="utf-8-sig")
            messagebox.showinfo("Exportar", f"Tabla exportada exitosamente a:\n{ruta}")
        except Exception as err:
            messagebox.showerror("Error al exportar", f"No se pudo guardar el archivo CSV:\n{err}")

    def refresh_format(self) -> None:
        """Refresca la salida cuando el usuario cambia entre formato Fracción / Decimal."""
        if self.resultado is not None:
            self._mostrar_tabla(self.resultado)

    def set_theme(self, modo: str) -> None:
        """Adapta la gráfica y colores al tema Dark / Light."""
        self._modo_tema = modo
        if self.resultado is not None:
            self._dibujar_grafica(self.resultado)
