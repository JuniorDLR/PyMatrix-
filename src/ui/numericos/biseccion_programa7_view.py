"""Interfaz de la bisección oficial del Programa 7."""

import threading
from queue import Empty, SimpleQueue
from collections.abc import Callable

import customtkinter as ctk

from src.core.numericos.biseccion import Resultado, biseccion_programa7, contraste_scipy
from src.ui.numericos.comun import Terminal, campo, escribir_entrada, formato


class BiseccionPrograma7View(ctk.CTkFrame):
    def __init__(
        self, parent: ctk.CTkBaseClass, get_modo: Callable[[], str],
        on_resultado: Callable[[Resultado], None], on_grafica: Callable[[], None],
    ) -> None:
        super().__init__(parent, fg_color="transparent")
        self.get_modo = get_modo
        self.on_resultado = on_resultado
        self.on_grafica = on_grafica
        self.resultado: Resultado | None = None
        self._comparacion: tuple[float, float] | str | None = None
        self._trabajos: SimpleQueue[tuple[int, tuple[float, float] | str]] = SimpleQueue()
        self.grid_columnconfigure(0, minsize=380)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        entrada = ctk.CTkScrollableFrame(self, width=350, fg_color=("#f1f5f9", "#111827"))
        entrada.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(entrada, text="Bisección · Programa 7",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=("#0369a1", "#38bdf8")).pack(anchor="w", padx=14, pady=(16, 4))
        ctk.CTkLabel(entrada, text="Expresión segura: x, **, sin, cos, tan, exp, log, sqrt, abs",
                     wraplength=330, justify="left").pack(anchor="w", padx=14, pady=(0, 12))
        datos = ctk.CTkFrame(entrada, fg_color=("#ffffff", "#1f2937"))
        datos.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(datos, text="Función e intervalo",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=12, pady=(12, 6))
        self.funcion = campo(datos, "f(x)", "x**3 - 2*x - 5")
        self.a = campo(datos, "Límite a", "2")
        self.b = campo(datos, "Límite b", "3")
        self.tolerancia = campo(datos, "Tolerancia E", "0.0001")
        self.maximo = campo(datos, "Máx. iteraciones", "100")
        ctk.CTkLabel(datos, text="Eᵦ = (b−a)/2 antes de actualizar; parada si Eᵦ ≤ E.",
                     wraplength=320, justify="left",
                     text_color=("#475569", "#94a3b8")).pack(anchor="w", padx=12, pady=(6, 12))

        ejemplos = ctk.CTkFrame(entrada, fg_color="transparent")
        ejemplos.pack(fill="x", padx=12, pady=6)
        for texto, expresion, a, b in (
            ("Cúbica", "x**3 - 2*x - 5", "2", "3"),
            ("Coseno", "cos(x) - x", "0", "1"),
            ("Dominio", "1/x", "-1", "1"),
        ):
            ctk.CTkButton(
                ejemplos, text=texto, width=80, fg_color="#475569",
                command=lambda f=expresion, l=a, u=b: self._ejemplo(f, l, u),
            ).pack(side="left", fill="x", expand=True, padx=3)
        ctk.CTkButton(entrada, text="Calcular bisección", height=38,
                      command=self._calcular).pack(fill="x", padx=12, pady=(4, 6))
        self.boton_grafica = ctk.CTkButton(
            entrada, text="Ver gráfica de esta función", fg_color="#475569",
            command=self.on_grafica, state="disabled",
        )
        self.boton_grafica.pack(fill="x", padx=12, pady=(0, 6))
        self.error = ctk.CTkLabel(entrada, text="", text_color="#ef4444",
                                  wraplength=320, justify="left")
        self.error.pack(fill="x", padx=12, pady=(0, 14))

        salida = ctk.CTkFrame(self, fg_color=("#ffffff", "#1f2937"))
        salida.grid(row=0, column=1, sticky="nsew", padx=(0, 5), pady=5)
        salida.grid_rowconfigure(1, weight=1)
        salida.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(salida, text="Tabla y comprobación",
                     font=ctk.CTkFont(size=17, weight="bold")).grid(
                         row=0, column=0, sticky="w", padx=14, pady=10)
        self.terminal = Terminal(salida)
        self.terminal.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.terminal.escribir("Introduce una función continua y calcula sus iteraciones.")

    def _ejemplo(self, expresion: str, a: str, b: str) -> None:
        for entrada, texto in ((self.funcion, expresion), (self.a, a), (self.b, b)):
            escribir_entrada(entrada, texto)
        self.error.configure(text="")

    def _calcular(self) -> None:
        try:
            texto_maximo = self.maximo.get().strip()
            if not texto_maximo.isascii() or not texto_maximo.isdigit():
                raise ValueError("El máximo de iteraciones debe ser un entero positivo.")
            maximo = int(texto_maximo)
            resultado = biseccion_programa7(
                self.funcion.get(), self.a.get(), self.b.get(),
                self.tolerancia.get(), maximo,
            )
        except (ValueError, TypeError) as error:
            self.resultado = None
            self.error.configure(text=str(error))
            self.boton_grafica.configure(state="disabled")
            self.terminal.escribir("")
            return
        self.resultado = resultado
        self.error.configure(text="")
        self.boton_grafica.configure(state="normal")
        self.on_resultado(resultado)
        self._comparacion = "Calculando contraste con SciPy..."
        self.refresh_format()
        threading.Thread(target=self._comparar, args=(resultado,), daemon=True).start()
        self.after(100, self._revisar_contraste)

    def _comparar(self, resultado: Resultado) -> None:
        try:
            contraste: tuple[float, float] | str = contraste_scipy(resultado)
        except ValueError as error:
            contraste = str(error)
        except (ImportError, RuntimeError, OverflowError) as error:
            contraste = f"SciPy no pudo contrastar este caso: {error}"
        self._trabajos.put((id(resultado), contraste))

    def _revisar_contraste(self) -> None:
        if self.resultado is None:
            return
        while True:
            try:
                identificador, contraste = self._trabajos.get_nowait()
            except Empty:
                self.after(100, self._revisar_contraste)
                return
            if identificador == id(self.resultado):
                self._comparacion = contraste
                self.refresh_format()
                return

    def refresh_format(self) -> None:
        resultado = self.resultado
        if resultado is None:
            return
        modo = self.get_modo()
        fmt = lambda valor: formato(valor, modo)
        lineas = [
            f"f(x) = {resultado.funcion.expresion}",
            f"Intervalo inicial [{fmt(resultado.inicial_a)}, {fmt(resultado.inicial_b)}]",
            f"E = {fmt(resultado.tolerancia)}; Nmáx = {resultado.max_iteraciones}",
            f"n mínimo teórico = {resultado.teoricas}; ejecutadas = {len(resultado.pasos)}",
            "Se registran a y b ANTES de actualizar el intervalo.",
            "Se muestreó el dominio; el cambio de signo por sí solo no prueba continuidad.",
            "",
            " k | a | b | xr | f(a) | f(b) | f(xr) | Eᵦ | Eₐ aprox. | εₐ (%)",
            "-" * 112,
        ]
        for paso in resultado.pasos:
            error_abs = "—" if paso.error_absoluto is None else fmt(paso.error_absoluto)
            error_rel = (
                "—" if paso.k == 1 else
                "No definido" if paso.error_relativo is None else fmt(paso.error_relativo * 100)
            )
            lineas.append(" | ".join((
                str(paso.k), fmt(paso.a), fmt(paso.b), fmt(paso.xr),
                fmt(paso.fa), fmt(paso.fb), fmt(paso.fr), fmt(paso.eb),
                error_abs, error_rel,
            )))
            if paso.nuevo_a != paso.a:
                lineas.append("     f(a)·f(xr)>0 → a ← xr")
            elif paso.nuevo_b != paso.b:
                lineas.append("     f(a)·f(xr)<0 → b ← xr")
        lineas.extend((
            "", f"Raíz aproximada xr = {fmt(resultado.raiz)}",
            f"f(xr) = {fmt(resultado.funcion.evaluar(float(resultado.raiz)))}",
            f"Parada: {resultado.motivo}.",
            "Tolerancia: " + (
                "satisfecha." if resultado.cumplio_tolerancia else
                "sin garantía por límite de iteraciones o precisión."
            ),
        ))
        if resultado.pasos:
            lineas.append(f"Cota Eᵦ del último paso = {fmt(resultado.pasos[-1].eb)}.")
        if isinstance(self._comparacion, tuple):
            raiz_scipy, diferencia = self._comparacion
            lineas.append(f"SciPy bisect = {fmt(raiz_scipy)}; diferencia absoluta = {fmt(diferencia)}.")
        elif self._comparacion:
            lineas.append(str(self._comparacion))
        lineas.append("f(x) se evalúa con float; en Fracción, ≈ indica una aproximación racional.")
        self.terminal.escribir("\n".join(lineas))

    def set_theme(self, modo: str) -> None:
        self.terminal.set_theme(modo)
