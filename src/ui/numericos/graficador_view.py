"""Graficador de funciones reales con eje, cuadrícula y discontinuidades."""

import math
import tkinter as tk
from collections.abc import Callable

import customtkinter as ctk

from src.core.numericos.biseccion import Resultado
from src.core.numericos.graficador import Grafica, muestrear
from src.ui.light_theme import LIGHT
from src.ui.numericos.comun import campo, escribir_entrada, formato


class GraficadorView(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkBaseClass, get_modo: Callable[[], str]) -> None:
        super().__init__(parent, fg_color="transparent")
        self.get_modo = get_modo
        self.grafica: Grafica | None = None
        self.biseccion: Resultado | None = None
        self.grid_columnconfigure(0, minsize=300)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        entrada = ctk.CTkScrollableFrame(self, width=290, fg_color=("#f1f5f9", "#111827"))
        entrada.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(entrada, text="Graficador de funciones",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=("#0369a1", "#38bdf8")).pack(anchor="w", padx=14, pady=(16, 8))
        ctk.CTkLabel(entrada, text="Funciones seguras · 1201 muestras · cortes de dominio",
                     wraplength=290, anchor="w", justify="left").pack(
                         anchor="w", padx=14, pady=(0, 12))
        tarjeta = ctk.CTkFrame(entrada, fg_color=("#ffffff", "#1f2937"))
        tarjeta.pack(fill="x", padx=12, pady=5)
        self.funcion = campo(tarjeta, "f(x)", "1/x")
        self.x_min = campo(tarjeta, "x_min", "-2")
        self.x_max = campo(tarjeta, "x_max", "2")
        ctk.CTkButton(entrada, text="Graficar", height=38,
                      command=self.graficar).pack(fill="x", padx=12, pady=(8, 5))
        self.boton_biseccion = ctk.CTkButton(
            entrada, text="Usar resultado de Bisección",
            fg_color="#475569", state="disabled", command=self._usar_biseccion,
        )
        self.boton_biseccion.pack(fill="x", padx=12, pady=5)
        self.error = ctk.CTkLabel(entrada, text="", text_color="#ef4444",
                                  wraplength=280, justify="left")
        self.error.pack(fill="x", padx=12, pady=(0, 8))
        self.resumen = ctk.CTkLabel(
            entrada, text="La gráfica separa valores no definidos y asíntotas.",
            wraplength=280, justify="left",
        )
        self.resumen.pack(anchor="w", padx=14, pady=(4, 12))

        panel = ctk.CTkFrame(self, fg_color=("#ffffff", "#1f2937"))
        panel.grid(row=0, column=1, sticky="nsew", padx=(0, 5), pady=5)
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)
        self.titulo = ctk.CTkLabel(panel, text="f(x) = 1/x",
                                   font=ctk.CTkFont(size=17, weight="bold"))
        self.titulo.grid(row=0, column=0, sticky="w", padx=14, pady=10)
        self.canvas = tk.Canvas(panel, highlightthickness=0, background="#0f172a")
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.canvas.bind("<Configure>", lambda _event: self._dibujar(), add="+")
        self.set_theme(ctk.get_appearance_mode())
        self.graficar()

    def cargar_desde_biseccion(self, resultado: Resultado) -> None:
        self.biseccion = resultado
        self.boton_biseccion.configure(state="normal")
        self._usar_biseccion()

    def _usar_biseccion(self) -> None:
        if self.biseccion is None:
            return
        for entrada, texto in (
            (self.funcion, self.biseccion.funcion.expresion),
            (self.x_min, str(self.biseccion.inicial_a)),
            (self.x_max, str(self.biseccion.inicial_b)),
        ):
            escribir_entrada(entrada, texto)
        self.graficar()

    def graficar(self) -> None:
        try:
            self.grafica = muestrear(
                self.funcion.get(), self.x_min.get(), self.x_max.get(),
            )
        except ValueError as error:
            self.grafica = None
            self.error.configure(text=str(error))
            self.canvas.delete("all")
            return
        self.error.configure(text="")
        self.titulo.configure(text=f"f(x) = {self.grafica.funcion.expresion}")
        self._actualizar_resumen()
        self._dibujar()

    def _actualizar_resumen(self) -> None:
        if self.grafica is None:
            return
        raiz = self._raiz_visible()
        detalle = (
            f"{self.grafica.puntos_validos} puntos válidos; "
            f"{self.grafica.puntos_excluidos} excluidos. "
            f"{len(self.grafica.segmentos)} segmento(s)."
        )
        if raiz is not None:
            detalle += (
                f" Raíz ≈ {formato(self.biseccion.raiz, self.get_modo())}; "
                f"se marca el intervalo FINAL "
                f"[{formato(self.biseccion.final_a, self.get_modo())}, "
                f"{formato(self.biseccion.final_b, self.get_modo())}]."
            )
        self.resumen.configure(text=detalle)

    def _raiz_visible(self) -> float | None:
        if self.grafica is None or self.biseccion is None:
            return None
        if self.grafica.funcion.expresion != self.biseccion.funcion.expresion:
            return None
        raiz = float(self.biseccion.raiz)
        return raiz if self.grafica.x_min <= raiz <= self.grafica.x_max else None

    def _dibujar(self) -> None:
        grafica = self.grafica
        if grafica is None:
            return
        canvas = self.canvas
        ancho, alto = canvas.winfo_width(), canvas.winfo_height()
        if ancho < 120 or alto < 120:
            return
        claro = ctk.get_appearance_mode() == "Light"
        fondo = LIGHT["raised"] if claro else "#0f172a"
        tinta = LIGHT["ink"] if claro else "#e2e8f0"
        rejilla = LIGHT["border"] if claro else "#334155"
        curva = LIGHT["primary"] if claro else "#38bdf8"
        raiz_color = LIGHT["red"] if claro else "#f43f5e"
        canvas.configure(background=fondo)
        canvas.delete("all")
        valores = sorted(y for segmento in grafica.segmentos for _, y in segmento)
        inferior = valores[int((len(valores) - 1) * 0.02)]
        superior = valores[int((len(valores) - 1) * 0.98)]
        if inferior == superior:
            inferior -= 1
            superior += 1
        margen = (superior - inferior) * 0.12
        y_min, y_max = inferior - margen, superior + margen
        izquierda, derecha, arriba, abajo = 65, ancho - 20, 35, alto - 52
        if derecha <= izquierda or abajo <= arriba:
            return
        px = lambda x: izquierda + (x - grafica.x_min) / (grafica.x_max - grafica.x_min) * (derecha - izquierda)
        py = lambda y: abajo - (y - y_min) / (y_max - y_min) * (abajo - arriba)
        for indice in range(6):
            x = izquierda + indice * (derecha - izquierda) / 5
            y = arriba + indice * (abajo - arriba) / 5
            canvas.create_line(x, arriba, x, abajo, fill=rejilla)
            canvas.create_line(izquierda, y, derecha, y, fill=rejilla)
            valor_x = grafica.x_min + indice * (grafica.x_max - grafica.x_min) / 5
            valor_y = y_max - indice * (y_max - y_min) / 5
            canvas.create_text(x, abajo + 16, text=f"{valor_x:.3g}", fill=tinta, font=("Segoe UI", 9))
            canvas.create_text(izquierda - 7, y, text=f"{valor_y:.3g}", anchor="e",
                               fill=tinta, font=("Segoe UI", 9))
        if grafica.x_min <= 0 <= grafica.x_max:
            canvas.create_line(px(0), arriba, px(0), abajo, fill=tinta, width=2)
        if y_min <= 0 <= y_max:
            canvas.create_line(izquierda, py(0), derecha, py(0), fill=tinta, width=2)
        canvas.create_text(derecha, alto - 13, text="x", fill=tinta, font=("Segoe UI", 12, "bold"))
        canvas.create_text(15, arriba, text="f(x)", fill=tinta, font=("Segoe UI", 12, "bold"))
        for segmento in grafica.segmentos:
            coordenadas: list[float] = []
            for x, y in segmento:
                coordenadas.extend((px(x), max(-10000, min(10000, py(y)))))
            if len(coordenadas) >= 4:
                canvas.create_line(*coordenadas, fill=curva, width=2)
            elif coordenadas:
                canvas.create_oval(coordenadas[0] - 2, coordenadas[1] - 2,
                                   coordenadas[0] + 2, coordenadas[1] + 2,
                                   fill=curva, outline=curva)
        canvas.create_line(derecha - 120, arriba + 13, derecha - 95, arriba + 13,
                           fill=curva, width=2)
        canvas.create_text(derecha - 88, arriba + 13, text="f(x)", anchor="w",
                           fill=tinta, font=("Segoe UI", 10))
        raiz = self._raiz_visible()
        if raiz is not None and self.biseccion is not None:
            y = grafica.funcion.evaluar(raiz)
            if math.isfinite(y) and y_min <= y <= y_max:
                canvas.create_oval(px(raiz) - 5, py(y) - 5, px(raiz) + 5, py(y) + 5,
                                   fill=raiz_color, outline=tinta, width=1)
            for limite in (self.biseccion.final_a, self.biseccion.final_b):
                x = px(float(limite))
                canvas.create_line(x, arriba, x, abajo, fill=raiz_color, dash=(4, 4))
            canvas.create_text(derecha - 120, arriba + 30, text="● raíz / -- intervalo final",
                               anchor="w", fill=raiz_color, font=("Segoe UI", 10))

    def refresh_format(self) -> None:
        if self.grafica is not None:
            self._actualizar_resumen()
            self._dibujar()

    def set_theme(self, _modo: str) -> None:
        self._dibujar()
