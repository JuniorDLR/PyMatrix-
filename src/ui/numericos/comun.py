"""Controles y formato compartidos por las cuatro opciones numéricas."""

import math
import tkinter as tk
from fractions import Fraction

import customtkinter as ctk

from src.core.domain import formatear_numero
from src.ui.light_theme import LIGHT


def formato(valor: Fraction | float, modo: str, cifras: int = 10) -> str:
    if isinstance(valor, Fraction):
        return formatear_numero(valor, modo, max_decimales=cifras)
    if not math.isfinite(valor):
        return str(valor)
    if modo == "fraccion":
        aproximacion = Fraction(valor).limit_denominator(1_000_000)
        return f"≈{aproximacion}"
    return f"{valor:.{cifras}g}"


def campo(parent: ctk.CTkBaseClass, titulo: str, valor: str) -> ctk.CTkEntry:
    fila = ctk.CTkFrame(parent, fg_color="transparent")
    fila.pack(fill="x", padx=12, pady=5)
    ctk.CTkLabel(fila, text=titulo, width=135, anchor="w").pack(side="left")
    entrada = ctk.CTkEntry(fila)
    entrada.pack(side="left", fill="x", expand=True)
    entrada.insert(0, valor)
    return entrada


def escribir_entrada(entrada: ctk.CTkEntry, texto: str) -> None:
    entrada.delete(0, "end")
    entrada.insert(0, texto)


class Terminal(ctk.CTkFrame):
    """Área de procedimiento con scroll en ambas direcciones."""

    def __init__(self, parent: ctk.CTkBaseClass, *, ajustar_lineas: bool = False) -> None:
        super().__init__(parent, fg_color=(LIGHT["card_alt"], "#1f2937"))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.texto = tk.Text(
            self, wrap="word" if ajustar_lineas else "none",
            font=("Consolas", 15), relief="flat",
            padx=12, pady=12, background="#111827", foreground="#e2e8f0",
            insertbackground="#e2e8f0",
        )
        self.texto.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=(8, 0))
        vertical = ctk.CTkScrollbar(self, command=self.texto.yview)
        vertical.grid(row=0, column=1, sticky="ns", padx=(0, 4), pady=(8, 0))
        if ajustar_lineas:
            self.texto.configure(yscrollcommand=vertical.set, state="disabled")
        else:
            horizontal = ctk.CTkScrollbar(self, orientation="horizontal", command=self.texto.xview)
            horizontal.grid(row=1, column=0, sticky="ew", padx=(8, 0), pady=(0, 4))
            self.texto.configure(
                yscrollcommand=vertical.set, xscrollcommand=horizontal.set, state="disabled",
            )
        self.set_theme(ctk.get_appearance_mode())

    def escribir(self, contenido: str) -> None:
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", contenido)
        self.texto.configure(state="disabled")

    def set_theme(self, modo: str) -> None:
        if modo == "Light":
            self.texto.configure(
                background=LIGHT["raised"], foreground=LIGHT["ink"],
                insertbackground=LIGHT["ink"], selectbackground="#bfdbfe",
            )
        else:
            self.texto.configure(
                background="#111827", foreground="#e2e8f0",
                insertbackground="#e2e8f0", selectbackground="#334155",
            )
