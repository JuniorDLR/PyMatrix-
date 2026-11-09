"""Vista de errores numéricos, float y propagación."""

from collections.abc import Callable

import customtkinter as ctk

from src.core.numericos.errores import (
    TIPOS_ERROR, MedicionError, Propagacion, RepresentacionFloat,
    calcular_errores, calcular_propagacion, representar_float,
)
from src.ui.numericos.comun import Terminal, campo, formato


class ErroresView(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkBaseClass, get_modo: Callable[[], str]) -> None:
        super().__init__(parent, fg_color="transparent")
        self.get_modo = get_modo
        self.medicion: MedicionError | None = None
        self.propagacion: Propagacion | None = None
        self.float_info: RepresentacionFloat | None = None
        self.grid_columnconfigure(0, minsize=350)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        entrada = ctk.CTkScrollableFrame(self, width=340, fg_color=("#f1f5f9", "#111827"))
        entrada.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(entrada, text="Errores numéricos",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=("#0369a1", "#38bdf8")).pack(anchor="w", padx=14, pady=(16, 8))
        ctk.CTkLabel(entrada, text="Precisión, representación y perturbación de primer orden.",
                     wraplength=330, justify="left").pack(anchor="w", padx=14, pady=(0, 12))

        tarjeta_error = ctk.CTkFrame(entrada, fg_color=("#ffffff", "#1f2937"))
        tarjeta_error.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(tarjeta_error, text="Comparar valores",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=12, pady=(12, 6))
        self.verdadero = campo(tarjeta_error, "Verdadero xᵥ", "3.14159265")
        self.aproximado = campo(tarjeta_error, "Aproximado xₐ", "3.14")

        tarjeta_prop = ctk.CTkFrame(entrada, fg_color=("#ffffff", "#1f2937"))
        tarjeta_prop.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(tarjeta_prop, text="Propagación: sin(x) + x²",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=12, pady=(12, 6))
        self.x = campo(tarjeta_prop, "x", "1")
        self.delta = campo(tarjeta_prop, "Δx", "0.01")
        ctk.CTkButton(entrada, text="Calcular y explicar", height=38,
                      command=self._calcular).pack(fill="x", padx=12, pady=(8, 5))
        self.error = ctk.CTkLabel(entrada, text="", text_color="#ef4444",
                                  wraplength=330, justify="left")
        self.error.pack(fill="x", padx=12, pady=(0, 14))

        salida = ctk.CTkFrame(self, fg_color=("#ffffff", "#1f2937"))
        salida.grid(row=0, column=1, sticky="nsew", padx=(0, 5), pady=5)
        salida.grid_rowconfigure(1, weight=1)
        salida.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(salida, text="Procedimiento e interpretación",
                     font=ctk.CTkFont(size=17, weight="bold")).grid(
                         row=0, column=0, sticky="w", padx=14, pady=10)
        self.terminal = Terminal(salida, ajustar_lineas=True)
        self.terminal.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self._calcular()

    def _calcular(self) -> None:
        try:
            medicion = calcular_errores(self.verdadero.get(), self.aproximado.get())
            propagacion = calcular_propagacion(self.x.get(), self.delta.get())
            flotantes = representar_float()
        except (ValueError, OverflowError) as error:
            self.error.configure(text=str(error))
            self.terminal.escribir("")
            return
        self.medicion = medicion
        self.propagacion = propagacion
        self.float_info = flotantes
        self.error.configure(text="")
        self.refresh_format()

    def refresh_format(self) -> None:
        if self.medicion is None or self.propagacion is None or self.float_info is None:
            return
        modo = self.get_modo()
        fmt = lambda valor: formato(valor, modo)
        m, p, f = self.medicion, self.propagacion, self.float_info
        lineas = [
            "REPRESENTACIÓN DE PUNTO FLOTANTE EN ESTE EQUIPO",
            f"0.1 + 0.2 = {f.suma!r}; 0.1 + 0.2 == 0.3 → {f.comparacion}",
            "0.1 y 0.2 no tienen representación binaria finita; el redondeo deja",
            "una suma ligeramente distinta del float usado para 0.3.",
            f"Épsilon de máquina ({f.fuente_epsilon}) = {f.epsilon:.17g}",
            "Distancia entre 1.0 y el siguiente float representable mayor.",
            f"Máximo float ≈ {f.maximo:.5e}; max × 2 → {f.overflow}.",
            f"Mínimo normal ≈ {f.minimo_normal:.5e}; tiny × eps / 4 → {f.underflow}.",
            "Overflow produce un no finito; underflow puede redondear a cero.",
            "Estos resultados describen el tipo float y esta plataforma.",
            "",
            "CÁLCULO DE ERRORES",
            f"xᵥ = {fmt(m.verdadero)}; xₐ = {fmt(m.aproximado)}",
            f"Eₐ = |xᵥ − xₐ| = {fmt(m.absoluto)}",
            "Eᵣ = Eₐ / |xᵥ| = " + (
                "No definido (xᵥ=0)" if m.relativo is None else fmt(m.relativo)
            ),
            "Eᵣ(%) = 100·Eᵣ = " + (
                "No definido (xᵥ=0)" if m.porcentual is None else f"{fmt(m.porcentual)} %"
            ),
            "",
            "PROPAGACIÓN DE PRIMER ORDEN",
            f"f(x)=sin(x)+x²; f′(x)=cos(x)+2x; x={fmt(p.x)}; Δx={fmt(p.delta_x)}",
            f"f(x) = {fmt(p.fx)}; f′(x) = {fmt(p.derivada)}",
            f"Δy aproximado = f′(x)·Δx = {fmt(p.delta_aproximado)}",
            f"Δy real = f(x+Δx)−f(x) = {fmt(p.delta_real)}",
            f"|Δy aproximado − Δy real| = {fmt(p.diferencia)}",
            "La derivada da una aproximación lineal; suele mejorar con |Δx| pequeño.",
            "",
            "TIPOS DE ERROR Y EJEMPLOS",
        ]
        lineas.extend(f"• {nombre}: {descripcion}" for nombre, descripcion in TIPOS_ERROR)
        lineas.append("El truncamiento numérico corta un cálculo; el error de modelo cambia la ecuación.")
        lineas.append("Las funciones trigonométricas y float se muestran como aproximaciones (≈ en Fracción).")
        self.terminal.escribir("\n".join(lineas))

    def set_theme(self, modo: str) -> None:
        self.terminal.set_theme(modo)
