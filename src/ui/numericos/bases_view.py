"""Vista de descomposición posicional en bases 10 y 2."""

from collections.abc import Callable

import customtkinter as ctk

from src.core.numericos.bases import ConversionPosicional, convertir_posicional
from src.core.domain import a_subindice
from src.ui.numericos.comun import Terminal, campo, escribir_entrada


class BasesView(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkBaseClass, get_modo: Callable[[], str]) -> None:
        super().__init__(parent, fg_color="transparent")
        self.get_modo = get_modo
        self.resultado: ConversionPosicional | None = None
        self.grid_columnconfigure(0, minsize=330)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        entrada = ctk.CTkScrollableFrame(self, width=320, fg_color=("#f1f5f9", "#111827"))
        entrada.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(entrada, text="Notación posicional",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=("#0369a1", "#38bdf8")).pack(anchor="w", padx=14, pady=(16, 8))
        ctk.CTkLabel(entrada, text="Cada dígito contribuye dígito × base^posición.",
                     wraplength=300, justify="left").pack(anchor="w", padx=14, pady=(0, 12))
        tarjeta = ctk.CTkFrame(entrada, fg_color=("#ffffff", "#1f2937"))
        tarjeta.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(tarjeta, text="Base de origen",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=12, pady=(12, 6))
        self.base = ctk.CTkSegmentedButton(tarjeta, values=["Base 10", "Base 2"])
        self.base.pack(fill="x", padx=12, pady=6)
        self.base.set("Base 10")
        self.entrada_numero = campo(tarjeta, "Número entero", "84506")
        ctk.CTkButton(entrada, text="Descomponer y convertir", height=38,
                      command=self._calcular).pack(fill="x", padx=12, pady=(8, 6))
        ejemplos = ctk.CTkFrame(entrada, fg_color="transparent")
        ejemplos.pack(fill="x", padx=12, pady=6)
        ctk.CTkButton(ejemplos, text="84506₁₀", fg_color="#475569",
                      command=lambda: self._ejemplo("Base 10", "84506")).pack(
                          side="left", fill="x", expand=True, padx=3)
        ctk.CTkButton(ejemplos, text="11110011₂", fg_color="#475569",
                      command=lambda: self._ejemplo("Base 2", "11110011")).pack(
                          side="left", fill="x", expand=True, padx=3)
        self.error = ctk.CTkLabel(entrada, text="", text_color="#ef4444",
                                  wraplength=300, justify="left")
        self.error.pack(fill="x", padx=12, pady=(0, 12))

        salida = ctk.CTkFrame(self, fg_color=("#ffffff", "#1f2937"))
        salida.grid(row=0, column=1, sticky="nsew", padx=(0, 5), pady=5)
        salida.grid_rowconfigure(1, weight=1)
        salida.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(salida, text="Descomposición paso a paso",
                     font=ctk.CTkFont(size=17, weight="bold")).grid(
                         row=0, column=0, sticky="w", padx=14, pady=10)
        self.terminal = Terminal(salida)
        self.terminal.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self._calcular()

    def _ejemplo(self, base: str, numero: str) -> None:
        self.base.set(base)
        escribir_entrada(self.entrada_numero, numero)
        self._calcular()

    def _calcular(self) -> None:
        try:
            base = 10 if self.base.get() == "Base 10" else 2
            self.resultado = convertir_posicional(self.entrada_numero.get(), base)
        except ValueError as error:
            self.resultado = None
            self.error.configure(text=str(error))
            self.terminal.escribir("")
            return
        self.error.configure(text="")
        self.refresh_format()

    def refresh_format(self) -> None:
        resultado = self.resultado
        if resultado is None:
            return
        signo = "−" if resultado.valor < 0 else ""
        decimal = resultado.decimal.lstrip("-")
        binario = resultado.binario.lstrip("-")
        lineas = [
            f"Origen: base {resultado.origen}. Resultado: base {2 if resultado.origen == 10 else 10}.",
            f"({resultado.entrada}){a_subindice(resultado.origen)} = "
            f"({resultado.binario if resultado.origen == 10 else resultado.decimal})"
            f"{a_subindice(2 if resultado.origen == 10 else 10)}",
            "El signo se conserva; las potencias descomponen la magnitud absoluta.",
            "",
            f"BASE 10: ({decimal})₁₀",
            " + ".join(f"{t.digito}·10^{t.exponente}" for t in resultado.terminos_decimales),
            " = ".join((" + ".join(str(t.aporte) for t in resultado.terminos_decimales),
                        decimal)),
            "",
            f"BASE 2: ({binario})₂",
            " + ".join(f"{t.digito}·2^{t.exponente}" for t in resultado.terminos_binarios),
            " = ".join((" + ".join(str(t.aporte) for t in resultado.terminos_binarios),
                        decimal)),
            "",
            "CONVERSIÓN DECIMAL → BINARIO POR DIVISIONES ENTRE 2",
        ]
        for dividendo, cociente, resto in resultado.divisiones:
            lineas.append(f"{dividendo} ÷ 2 = {cociente}, residuo {resto}")
        if not resultado.divisiones:
            lineas.append("0₁₀ = 0₂")
        lineas.extend(("", f"Residuos leídos de abajo arriba: {signo}{binario}₂",
                       f"Comprobación: {signo}{binario}₂ = {signo}{decimal}₁₀."))
        self.terminal.escribir("\n".join(lineas))

    def set_theme(self, modo: str) -> None:
        self.terminal.set_theme(modo)
