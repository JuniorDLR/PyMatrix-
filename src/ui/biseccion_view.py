"""Vista del método de bisección de la sesión 19."""

import tkinter as tk
from fractions import Fraction
from typing import Callable

import customtkinter as ctk

from src.core.biseccion import ResultadoBiseccion, biseccion
from src.core.domain import formatear_numero
from src.ui.light_theme import LIGHT


class BiseccionView(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, get_modo_numero: Callable[[], str]):
        super().__init__(master, fg_color="transparent")
        self.get_modo_numero = get_modo_numero
        self.resultado: ResultadoBiseccion | None = None
        self.grid_columnconfigure(0, minsize=380)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.entrada = ctk.CTkScrollableFrame(self, width=350, fg_color=("#f1f5f9", "#111827"))
        self.entrada.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(self.entrada, text="Método de bisección", font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=("#0369a1", "#38bdf8")).pack(anchor="w", padx=14, pady=(16, 4))
        ctk.CTkLabel(self.entrada, text="f(x) = aₙxⁿ + ··· + a₁x + a₀",
                     text_color=("#475569", "#94a3b8")).pack(anchor="w", padx=14, pady=(0, 12))

        polinomio = self._tarjeta("Polinomio")
        fila_grado = ctk.CTkFrame(polinomio, fg_color="transparent")
        fila_grado.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(fila_grado, text="Grado:").pack(side="left")
        self.grado = ctk.CTkEntry(fila_grado, width=50, justify="center")
        self.grado.pack(side="left", padx=8)
        self.grado.insert(0, "4")
        ctk.CTkButton(fila_grado, text="Generar", width=75, command=self._generar_coeficientes).pack(side="left")
        self.coef_scroll = ctk.CTkScrollableFrame(polinomio, orientation="horizontal", height=83,
                                                   fg_color="transparent")
        self.coef_scroll.pack(fill="x", padx=8, pady=(0, 8))
        self.coef_frame = ctk.CTkFrame(self.coef_scroll, fg_color="transparent")
        self.coef_frame.pack(anchor="w")
        self.coef_entries: list[ctk.CTkEntry] = []

        intervalo = self._tarjeta("Intervalo y tolerancia")
        self.xl = self._campo(intervalo, "Límite inferior xₗ", "0.55")
        self.xu = self._campo(intervalo, "Límite superior xᵤ", "1.1")
        self.tolerancia = self._campo(intervalo, "Tolerancia E (ancho)", "0.0001")

        control = self._tarjeta("Criterio de ejecución")
        self.modo = ctk.CTkSegmentedButton(control, values=["Hasta E", "N iteraciones"])
        self.modo.pack(fill="x", padx=10, pady=(0, 8))
        self.modo.set("Hasta E")
        self.cantidad = self._campo(control, "Iteraciones N (modo manual)", "5")
        ctk.CTkLabel(control, text="Se muestra εₐ y el ancho en cada paso.\n"
                     "El modo Hasta E usa el ancho actualizado.", justify="left",
                     text_color=("#475569", "#94a3b8")).pack(anchor="w", padx=10, pady=(0, 10))

        ejemplos = ctk.CTkFrame(self.entrada, fg_color="transparent")
        ejemplos.pack(fill="x", padx=12, pady=(8, 4))
        ctk.CTkButton(ejemplos, text="Ejemplo de clase", command=self._ejemplo_clase,
                      fg_color="#475569").pack(side="left", fill="x", expand=True, padx=(0, 3))
        ctk.CTkButton(ejemplos, text="Ejercicio 1", command=self._ejercicio,
                      fg_color="#475569").pack(side="left", fill="x", expand=True, padx=(3, 0))
        ctk.CTkButton(self.entrada, text="Calcular bisección", height=38, command=self._calcular,
                      fg_color="#0284c7", hover_color="#0369a1",
                      font=ctk.CTkFont(weight="bold")).pack(fill="x", padx=12, pady=(4, 10))
        self.error_label = ctk.CTkLabel(self.entrada, text="", text_color="#ef4444", wraplength=320)
        self.error_label.pack(fill="x", padx=12, pady=(0, 12))

        salida = ctk.CTkFrame(self, fg_color=(LIGHT["card_alt"], "#1f2937"))
        salida.grid(row=0, column=1, sticky="nsew", padx=(0, 5), pady=5)
        salida.grid_rowconfigure(1, weight=1)
        salida.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(salida, text="Iteraciones y comprobación", font=ctk.CTkFont(size=17, weight="bold"),
                     anchor="w").grid(row=0, column=0, sticky="ew", padx=14, pady=10)
        texto_frame = ctk.CTkFrame(salida, fg_color="transparent")
        texto_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        texto_frame.grid_rowconfigure(0, weight=1)
        texto_frame.grid_columnconfigure(0, weight=1)
        self.texto = tk.Text(texto_frame, wrap="none", font=("Consolas", 15), relief="flat",
                             background="#111827", foreground="#e2e8f0", insertbackground="#e2e8f0",
                             padx=14, pady=12, spacing1=2, spacing3=2)
        self.texto.grid(row=0, column=0, sticky="nsew")
        vertical = ctk.CTkScrollbar(texto_frame, command=self.texto.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ctk.CTkScrollbar(texto_frame, orientation="horizontal", command=self.texto.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.texto.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set, state="disabled")
        self.set_theme(ctk.get_appearance_mode())
        self._generar_coeficientes()
        self._ejemplo_clase()

    def _tarjeta(self, titulo: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.entrada, fg_color=("#ffffff", "#1f2937"), corner_radius=10)
        frame.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(frame, text=titulo, font=ctk.CTkFont(size=13, weight="bold")).pack(
            anchor="w", padx=10, pady=(10, 6))
        return frame

    def _campo(self, parent: ctk.CTkFrame, etiqueta: str, valor: str) -> ctk.CTkEntry:
        fila = ctk.CTkFrame(parent, fg_color="transparent")
        fila.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(fila, text=etiqueta, width=175, anchor="w").pack(side="left")
        entrada = ctk.CTkEntry(fila, width=110)
        entrada.pack(side="left", fill="x", expand=True)
        entrada.insert(0, valor)
        return entrada

    def _generar_coeficientes(self) -> None:
        try:
            grado = int(self.grado.get())
            if not 1 <= grado <= 12:
                raise ValueError
        except ValueError:
            self.error_label.configure(text="El grado debe ser un entero entre 1 y 12.") if hasattr(self, "error_label") else None
            return
        anteriores = [entrada.get() for entrada in self.coef_entries]
        for widget in self.coef_frame.winfo_children():
            widget.destroy()
        self.coef_entries = []
        for indice, exponente in enumerate(range(grado, -1, -1)):
            celda = ctk.CTkFrame(self.coef_frame, fg_color="transparent")
            celda.grid(row=0, column=indice, padx=3)
            ctk.CTkLabel(celda, text=f"a{exponente}").pack()
            entrada = ctk.CTkEntry(celda, width=72, justify="center")
            entrada.pack()
            entrada.insert(0, anteriores[indice] if indice < len(anteriores) else "0")
            self.coef_entries.append(entrada)
        if hasattr(self, "error_label"):
            self.error_label.configure(text="")

    def _cargar(self, grado: int, coeficientes: tuple[str, ...], xl: str, xu: str, manual: bool) -> None:
        self.grado.delete(0, "end")
        self.grado.insert(0, str(grado))
        self._generar_coeficientes()
        for entrada, valor in zip(self.coef_entries, coeficientes):
            entrada.delete(0, "end")
            entrada.insert(0, valor)
        for entrada, valor in ((self.xl, xl), (self.xu, xu), (self.tolerancia, "0.0001")):
            entrada.delete(0, "end")
            entrada.insert(0, valor)
        self.modo.set("N iteraciones" if manual else "Hasta E")
        self.resultado = None
        self._escribir("")

    def _ejemplo_clase(self) -> None:
        self._cargar(4, ("1", "-5", "0.5", "-11", "10"), "0.55", "1.1", False)

    def _ejercicio(self) -> None:
        self._cargar(3, ("1", "0", "-4", "-1"), "2", "3", True)

    def _calcular(self) -> None:
        try:
            cantidad = None
            if self.modo.get() == "N iteraciones":
                cantidad = int(self.cantidad.get())
            self.resultado = biseccion(
                [entrada.get() for entrada in self.coef_entries], self.xl.get(), self.xu.get(),
                self.tolerancia.get(), iteraciones=cantidad, max_iteraciones=1000,
            )
        except (ValueError, TypeError) as error:
            self.resultado = None
            self.error_label.configure(text=str(error))
            self._escribir("")
            return
        self.error_label.configure(text="")
        self.refresh_format()

    def _escribir(self, contenido: str) -> None:
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", contenido)
        if contenido:
            self.texto.tag_add("titulo", "1.0", "1.end")
            for indice, linea in enumerate(contenido.splitlines(), start=1):
                if linea.startswith(("Raíz aproximada", "Parada:", "¿Ancho actualizado", "Cota del error")):
                    self.texto.tag_add("resultado", f"{indice}.0", f"{indice}.end")
        self.texto.configure(state="disabled")

    def set_theme(self, mode: str) -> None:
        if mode == "Light":
            self.texto.configure(background=LIGHT["raised"], foreground=LIGHT["ink"],
                                 insertbackground="#172b45", selectbackground="#bfdbfe")
            self.texto.tag_configure("titulo", foreground="#075985", font=("Consolas", 15, "bold"))
            self.texto.tag_configure("resultado", foreground="#047857", font=("Consolas", 15, "bold"))
        else:
            self.texto.configure(background="#111827", foreground="#e2e8f0",
                                 insertbackground="#e2e8f0", selectbackground="#334155")
            self.texto.tag_configure("titulo", foreground="#e2e8f0", font=("Consolas", 15))
            self.texto.tag_configure("resultado", foreground="#e2e8f0", font=("Consolas", 15))

    def refresh_format(self) -> None:
        if self.resultado is None:
            return
        resultado = self.resultado
        modo = self.get_modo_numero()

        def fmt(valor: Fraction, decimales: int = 8) -> str:
            return formatear_numero(valor, modo, max_decimales=decimales)

        lineas = [
            "MÉTODO DE BISECCIÓN · SESIÓN 19",
            f"Tolerancia E = {fmt(resultado.tolerancia)}",
            f"Iteraciones estimadas para ancho < E: {resultado.iteraciones_estimadas}",
            "",
            "i | x_l | x_u | x_r | f(x_l) | f(x_u) | f(x_r) | ε_a (%) | ancho antes | ancho después",
            "-" * 112,
        ]
        for paso in resultado.pasos:
            error = "—" if paso.error_relativo is None else fmt(100 * paso.error_relativo, 6)
            lineas.append(" | ".join((
                str(paso.iteracion), fmt(paso.xl), fmt(paso.xu), fmt(paso.xr),
                fmt(paso.f_xl), fmt(paso.f_xu), fmt(paso.f_xr), error,
                fmt(paso.ancho_inicial), fmt(paso.ancho_final),
            )))
            relacion = paso.f_xl * paso.f_xr
            if relacion == 0:
                decision = "f(x_l)·f(x_r) = 0; raíz exacta."
            elif relacion < 0:
                decision = f"f(x_l)·f(x_r) < 0; x_u ← x_r; nuevo intervalo [{fmt(paso.nuevo_xl)}, {fmt(paso.nuevo_xu)}]."
            else:
                decision = f"f(x_l)·f(x_r) > 0; x_l ← x_r; nuevo intervalo [{fmt(paso.nuevo_xl)}, {fmt(paso.nuevo_xu)}]."
            lineas.append("    " + decision)
        lineas.extend(("", f"Raíz aproximada x_r = {fmt(resultado.raiz, 10)}",
                       f"Parada: {resultado.motivo}."))
        if resultado.pasos:
            ultimo = resultado.pasos[-1]
            lineas.append(f"¿Ancho actualizado < E? {'Sí' if ultimo.ancho_final < resultado.tolerancia else 'No'} "
                          f"({fmt(ultimo.ancho_final)} < {fmt(resultado.tolerancia)}).")
            cota = Fraction(0) if ultimo.f_xr == 0 else ultimo.ancho_final
            lineas.append(f"Cota del error absoluto de x_r: ≤ {fmt(cota, 10)}.")
        self._escribir("\n".join(lineas))
