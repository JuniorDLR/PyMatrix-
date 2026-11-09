"""Contenedor compacto de las cuatro opciones del Programa 7."""

from collections.abc import Callable

import customtkinter as ctk

from src.core.numericos.biseccion import Resultado
from src.ui.biseccion_view import BiseccionView
from src.ui.numericos.bases_view import BasesView
from src.ui.numericos.biseccion_programa7_view import BiseccionPrograma7View
from src.ui.numericos.errores_view import ErroresView
from src.ui.numericos.graficador_view import GraficadorView


class NumericosView(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkBaseClass, get_modo: Callable[[], str]) -> None:
        super().__init__(parent, fg_color="transparent")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        for nombre in ("Bisección", "Graficador", "Bases 10/2", "Errores"):
            pestaña = self.tabs.add(nombre)
            pestaña.grid_rowconfigure(0, weight=1)
            pestaña.grid_columnconfigure(0, weight=1)

        pagina_biseccion = self.tabs.tab("Bisección")
        pagina_biseccion.grid_rowconfigure(0, weight=0)
        pagina_biseccion.grid_rowconfigure(1, weight=1)
        selector = ctk.CTkSegmentedButton(
            pagina_biseccion, values=["Programa 7", "Sesión 19"],
            command=self._cambiar_modalidad,
        )
        selector.grid(row=0, column=0, sticky="ew", padx=8, pady=(2, 6))
        selector.set("Programa 7")
        self.graficador = GraficadorView(self.tabs.tab("Graficador"), get_modo)
        self.graficador.grid(row=0, column=0, sticky="nsew")
        self.programa7 = BiseccionPrograma7View(
            pagina_biseccion, get_modo,
            on_resultado=self._guardar_resultado,
            on_grafica=lambda: self.tabs.set("Graficador"),
        )
        self.programa7.grid(row=1, column=0, sticky="nsew")
        self.sesion19 = BiseccionView(pagina_biseccion, get_modo)
        self.sesion19.grid(row=1, column=0, sticky="nsew")
        self.sesion19.grid_remove()
        self.bases = BasesView(self.tabs.tab("Bases 10/2"), get_modo)
        self.bases.grid(row=0, column=0, sticky="nsew")
        self.errores = ErroresView(self.tabs.tab("Errores"), get_modo)
        self.errores.grid(row=0, column=0, sticky="nsew")

    def _cambiar_modalidad(self, nombre: str) -> None:
        if nombre == "Sesión 19":
            self.programa7.grid_remove()
            self.sesion19.grid()
        else:
            self.sesion19.grid_remove()
            self.programa7.grid()

    def _guardar_resultado(self, resultado: Resultado) -> None:
        self.graficador.cargar_desde_biseccion(resultado)

    def refresh_format(self) -> None:
        for vista in (self.programa7, self.sesion19, self.graficador, self.bases, self.errores):
            vista.refresh_format()

    def set_theme(self, modo: str) -> None:
        for vista in (self.programa7, self.sesion19, self.graficador, self.bases, self.errores):
            vista.set_theme(modo)
