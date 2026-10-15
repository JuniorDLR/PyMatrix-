"""Vista gráfica de las propiedades matriciales requeridas en la Tarea 6."""

from fractions import Fraction
from typing import Any

import customtkinter as ctk

from src.core.domain import formatear_numero, a_subindice
from src.core.exact_math import MatrizF, parsear_fraccion
from teoremas.verificador_matrices import (
    EspecificacionTeorema,
    ResultadoTeorema,
    TEOREMAS,
    verificar_teorema,
)


class TeoremasView(ctk.CTkFrame):
    """Ofrece un verificador exacto con entradas contextuales y salida desplazable."""

    def __init__(self, master: Any, get_modo_numero, banco_matrices: dict, **kwargs: Any):
        """Recibe el formato global y el banco compartido para reutilizar matrices."""

        super().__init__(master, **kwargs)
        self.get_modo_numero = get_modo_numero
        self.banco_matrices = banco_matrices
        self._resultado: ResultadoTeorema | None = None
        self._entradas: dict[str, MatrizF | Fraction] = {}
        self.grid_columnconfigure(0, weight=0, minsize=370)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Organiza selector, entradas y comprobación para una pantalla compacta."""

        panel_izquierdo = ctk.CTkFrame(self, width=360, fg_color=("#f1f5f9", "#111827"),
                                       corner_radius=0)
        panel_izquierdo.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        panel_izquierdo.grid_columnconfigure(0, weight=1)
        panel_izquierdo.grid_rowconfigure(0, weight=1)
        self.entrada_scroll = ctk.CTkScrollableFrame(panel_izquierdo, width=340, fg_color="transparent")
        self.entrada_scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=(5, 0))
        self.entrada_scroll.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.entrada_scroll, text="Verificador de propiedades",
                     font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=6, pady=(8, 6)
        )
        ctk.CTkLabel(self.entrada_scroll, text="Categoría").grid(row=1, column=0, sticky="w", padx=6)
        self.menu_categoria = ctk.CTkOptionMenu(
            self.entrada_scroll, values=["Operaciones", "Inversa", "Determinante"],
            command=self._cambiar_categoria,
        )
        self.menu_categoria.grid(row=2, column=0, sticky="ew", padx=6, pady=(3, 8))
        ctk.CTkLabel(self.entrada_scroll, text="Igualdad a verificar").grid(row=3, column=0, sticky="w", padx=6)
        self.menu_teorema = ctk.CTkOptionMenu(self.entrada_scroll, values=[TEOREMAS[0].formula],
                                             command=self._cambiar_teorema)
        self.menu_teorema.grid(row=4, column=0, sticky="ew", padx=6, pady=(3, 6))
        self.etiqueta_requisitos = ctk.CTkLabel(
            self.entrada_scroll, text="", wraplength=290, justify="left", text_color=("gray35", "gray75")
        )
        self.etiqueta_requisitos.grid(row=5, column=0, sticky="w", padx=6, pady=(0, 4))
        ctk.CTkButton(self.entrada_scroll, text="Ejemplo para esta igualdad",
                      command=self._cargar_ejemplo, height=28, fg_color="#475569",
                      hover_color="#334155").grid(row=6, column=0, sticky="ew", padx=6, pady=(0, 9))

        banco = ctk.CTkFrame(self.entrada_scroll, fg_color=("#ffffff", "#1f2937"), corner_radius=10)
        banco.grid(row=7, column=0, sticky="ew", padx=6, pady=(0, 8))
        ctk.CTkLabel(banco, text="Usar matriz del Banco", font=ctk.CTkFont(size=12, weight="bold")).pack(
            anchor="w", padx=10, pady=(8, 4))
        banco_fila = ctk.CTkFrame(banco, fg_color="transparent")
        banco_fila.pack(fill="x", padx=10, pady=(0, 8))
        self.menu_banco = ctk.CTkOptionMenu(banco_fila, values=["(Banco vacío)"], width=110)
        self.menu_banco.pack(side="left", fill="x", expand=True, padx=(0, 3))
        self.menu_destino = ctk.CTkOptionMenu(banco_fila, values=["A"], width=45)
        self.menu_destino.pack(side="left", padx=2)
        ctk.CTkButton(banco_fila, text="↻", width=28, command=self.actualizar_banco).pack(side="left", padx=2)
        ctk.CTkButton(banco_fila, text="Cargar", width=58, command=self._cargar_banco).pack(side="left", padx=(2, 0))

        self.marcos: dict[str, ctk.CTkFrame] = {}
        self.dimensiones: dict[str, tuple[ctk.CTkEntry, ctk.CTkEntry]] = {}
        self.grids: dict[str, ctk.CTkFrame] = {}
        self.scrolls: dict[str, ctk.CTkScrollableFrame] = {}
        self.entries: dict[str, list[list[ctk.CTkEntry]]] = {}
        for fila, nombre in enumerate(("A", "B", "C"), start=8):
            marco = ctk.CTkFrame(self.entrada_scroll, fg_color=("#ffffff", "#1f2937"), corner_radius=10)
            marco.grid(row=fila, column=0, sticky="ew", padx=6, pady=(0, 7))
            ctk.CTkLabel(marco, text=f"Matriz {nombre}", font=ctk.CTkFont(weight="bold")).pack(
                anchor="w", padx=10, pady=(8, 3))
            controles = ctk.CTkFrame(marco, fg_color="transparent")
            controles.pack(anchor="w", padx=10)
            ctk.CTkLabel(controles, text="m:").pack(side="left")
            entrada_m = ctk.CTkEntry(controles, width=42, justify="center")
            entrada_m.pack(side="left", padx=(2, 6))
            entrada_m.insert(0, "3")
            ctk.CTkLabel(controles, text="n:").pack(side="left")
            entrada_n = ctk.CTkEntry(controles, width=42, justify="center")
            entrada_n.pack(side="left", padx=(2, 6))
            entrada_n.insert(0, "3")
            ctk.CTkButton(controles, text="Generar", width=70, height=26,
                          command=lambda matriz=nombre: self._generar_grid(matriz)).pack(side="left")
            scroll = ctk.CTkScrollableFrame(marco, orientation="horizontal", height=140,
                                             fg_color="transparent")
            scroll.pack(fill="x", padx=6, pady=(2, 8))
            grid = ctk.CTkFrame(scroll, fg_color="transparent")
            grid.pack(anchor="w")
            self.marcos[nombre] = marco
            self.dimensiones[nombre] = (entrada_m, entrada_n)
            self.scrolls[nombre] = scroll
            self.grids[nombre] = grid
            self.entries[nombre] = []
            self._generar_grid(nombre)
        self.marco_k = ctk.CTkFrame(self.entrada_scroll, fg_color=("#ffffff", "#1f2937"),
                                    corner_radius=10)
        self.marco_k.grid(row=11, column=0, sticky="ew", padx=6, pady=(0, 10))
        ctk.CTkLabel(self.marco_k, text="Escalar k", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.entrada_k = ctk.CTkEntry(self.marco_k, placeholder_text="Ej. -3/2")
        self.entrada_k.pack(fill="x", pady=(3, 0))

        ctk.CTkButton(panel_izquierdo, text="Verificar ambos miembros", command=self._verificar,
                      height=36, font=ctk.CTkFont(weight="bold"), fg_color="#0284c7",
                      hover_color="#0369a1").grid(
            row=1, column=0, sticky="ew", padx=11, pady=10
        )

        panel_derecho = ctk.CTkFrame(self)
        panel_derecho.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        panel_derecho.grid_columnconfigure(0, weight=1)
        panel_derecho.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(panel_derecho, text="Cálculo y diagnóstico",
                     font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 0)
        )
        self.salida = ctk.CTkTextbox(panel_derecho, font=ctk.CTkFont(family="Consolas", size=12), wrap="none")
        self.salida.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.salida.configure(state="disabled")
        self.actualizar_banco()
        self._cambiar_categoria("Operaciones")

    def _cambiar_categoria(self, categoria: str) -> None:
        """Filtra las igualdades visibles y selecciona la primera de la categoría."""

        disponibles = [teorema for teorema in TEOREMAS if teorema.categoria == categoria]
        self.menu_teorema.configure(values=[teorema.formula for teorema in disponibles])
        self.menu_teorema.set(disponibles[0].formula)
        self._cambiar_teorema(disponibles[0].formula)

    def _seleccionado(self) -> EspecificacionTeorema:
        """Devuelve la especificación correspondiente a la igualdad seleccionada."""

        formula = self.menu_teorema.get()
        return next(teorema for teorema in TEOREMAS if teorema.formula == formula)

    def _cambiar_teorema(self, _formula: str) -> None:
        """Muestra solo B, C o k cuando el teorema seleccionado los necesita."""

        teorema = self._seleccionado()
        requisitos = ("A",) + teorema.entradas
        self.etiqueta_requisitos.configure(text="Entradas necesarias: " + ", ".join(requisitos))
        for nombre in ("B", "C"):
            if nombre in teorema.entradas:
                self.marcos[nombre].grid()
            else:
                self.marcos[nombre].grid_remove()
        if "k" in teorema.entradas:
            self.marco_k.grid()
        else:
            self.marco_k.grid_remove()
        destinos = ["A"] + [nombre for nombre in ("B", "C") if nombre in teorema.entradas]
        self.menu_destino.configure(values=destinos)
        self.menu_destino.set("A")

    def _generar_grid(self, nombre: str) -> None:
        """Regenera una matriz editable tras validar su orden."""

        entrada_m, entrada_n = self.dimensiones[nombre]
        try:
            m, n = int(entrada_m.get()), int(entrada_n.get())
            if not 1 <= m <= 30 or not 1 <= n <= 30:
                raise ValueError
        except ValueError:
            self._escribir(f"❌ Las dimensiones de {nombre} deben ser enteros entre 1 y 30.")
            return
        marco = self.grids[nombre]
        for widget in marco.winfo_children():
            widget.destroy()
        self.scrolls[nombre].configure(height=35 + 31 * m)
        ctk.CTkLabel(marco, text="", width=28).grid(row=0, column=0)
        for j in range(n):
            ctk.CTkLabel(marco, text=f"C{a_subindice(j+1)}", width=42,
                         text_color=("#0284c7", "#38bdf8")).grid(row=0, column=j+1, padx=2)
        filas = []
        for i in range(m):
            ctk.CTkLabel(marco, text=f"F{a_subindice(i+1)}", width=28).grid(row=i+1, column=0, padx=2)
            fila = []
            for j in range(n):
                celda = ctk.CTkEntry(marco, width=42, height=26, justify="center")
                celda.grid(row=i+1, column=j+1, padx=2, pady=2)
                fila.append(celda)
            filas.append(fila)
        self.entries[nombre] = filas

    def _poner_matriz(self, nombre: str, matriz: list[list[Any]]) -> None:
        """Sincroniza controles de orden y celdas con una matriz válida."""

        if not matriz or not matriz[0] or any(len(fila) != len(matriz[0]) for fila in matriz):
            raise ValueError(f"La matriz {nombre} debe ser rectangular y no vacía.")
        if len(matriz) > 30 or len(matriz[0]) > 30:
            raise ValueError("La cuadrícula admite como máximo 30 filas y 30 columnas.")
        for entrada, dimension in zip(self.dimensiones[nombre], (len(matriz), len(matriz[0]))):
            entrada.delete(0, "end")
            entrada.insert(0, str(dimension))
        self._generar_grid(nombre)
        for i, fila in enumerate(matriz):
            for j, valor in enumerate(fila):
                self.entries[nombre][i][j].insert(0, str(valor))

    def _cargar_ejemplo(self) -> None:
        """Prepara dimensiones compatibles con la igualdad seleccionada."""

        teorema = self._seleccionado()
        A = [[2, 1], [1, 3]]
        B = [[1, 1], [0, 2]]
        C = [[2, 0], [1, 1]]
        if teorema.clave in {"doble_traspuesta", "traspuesta_suma", "traspuesta_escalar"}:
            A = [[1, 2, 3], [4, 5, 6]]
            B = [[2, 0, 1], [1, 3, 4]]
        elif teorema.clave == "traspuesta_producto":
            A = [[1, 2, 0], [0, 1, 3]]
            B = [[2, 1], [0, 2], [1, 0]]
        elif teorema.clave == "distributiva":
            A = [[1, 2, 0], [0, 1, 3]]
            B = [[2, 1], [0, 2], [1, 0]]
            C = [[1, 0], [2, 1], [0, 3]]
        elif teorema.clave == "asociativa":
            A = [[1, 2, 0], [0, 1, 3]]
            B = [[2, 1], [0, 2], [1, 0]]
            C = [[1, 2], [0, 1]]
        elif teorema.clave == "det_triangular":
            A = [[2, 1, -1], [0, 3, 2], [0, 0, 4]]
        self._poner_matriz("A", A)
        if "B" in teorema.entradas:
            self._poner_matriz("B", B)
        if "C" in teorema.entradas:
            self._poner_matriz("C", C)
        if "k" in teorema.entradas:
            self.entrada_k.delete(0, "end")
            self.entrada_k.insert(0, "3/2")

    def _leer_matriz(self, nombre: str) -> MatrizF:
        try:
            m, n = (int(entrada.get()) for entrada in self.dimensiones[nombre])
        except ValueError as error:
            raise ValueError(f"Corrija las dimensiones de {nombre} y pulse Generar.") from error
        if len(self.entries[nombre]) != m or any(len(fila) != n for fila in self.entries[nombre]):
            raise ValueError(f"Las dimensiones de {nombre} cambiaron; pulse Generar antes de verificar.")
        matriz: MatrizF = []
        for i, fila in enumerate(self.entries[nombre], start=1):
            valores = []
            for j, entrada in enumerate(fila, start=1):
                texto = entrada.get().strip()
                if not texto:
                    raise ValueError(f"Ingrese {nombre}[{i},{j}].")
                try:
                    valores.append(parsear_fraccion(texto))
                except (ValueError, ZeroDivisionError) as error:
                    raise ValueError(f"{nombre}[{i},{j}] no es un número válido: '{texto}'.") from error
            matriz.append(valores)
        return matriz

    def actualizar_banco(self) -> None:
        """Sincroniza las matrices guardadas con el selector de esta vista."""

        nombres = sorted(self.banco_matrices) or ["(Banco vacío)"]
        self.menu_banco.configure(values=nombres)
        self.menu_banco.set(nombres[0])

    def _cargar_banco(self) -> None:
        """Carga una matriz guardada en la entrada A, B o C seleccionada."""

        nombre = self.menu_banco.get()
        if nombre not in self.banco_matrices:
            self._escribir("❌ Seleccione una matriz guardada; actualice primero el Banco.")
            return
        try:
            self._poner_matriz(self.menu_destino.get(), self.banco_matrices[nombre])
        except ValueError as error:
            self._escribir(f"❌ {error}")

    def _verificar(self) -> None:
        """Lee solo las entradas necesarias, evalúa ambos miembros y muestra el resultado."""

        teorema = self._seleccionado()
        self._resultado = None
        self._entradas = {}
        try:
            A = self._leer_matriz("A")
            B = self._leer_matriz("B") if "B" in teorema.entradas else None
            C = self._leer_matriz("C") if "C" in teorema.entradas else None
            if "k" in teorema.entradas and not self.entrada_k.get().strip():
                raise ValueError("Ingrese el escalar k para esta propiedad.")
            k = parsear_fraccion(self.entrada_k.get()) if "k" in teorema.entradas else None
            self._resultado = verificar_teorema(teorema.clave, A, B, C, k)
            self._entradas = {"A": A}
            if B is not None:
                self._entradas["B"] = B
            if C is not None:
                self._entradas["C"] = C
            if k is not None:
                self._entradas["k"] = k
        except (ValueError, TypeError, ZeroDivisionError) as error:
            self._escribir(f"❌ No se pudo evaluar {teorema.formula}: {error}")
            return
        self._mostrar_resultado()

    def _formatear_valor(self, valor: MatrizF | Fraction) -> str:
        """Representa una matriz o escalar exacto en el formato global vigente."""

        modo = self.get_modo_numero()
        if isinstance(valor, Fraction):
            return formatear_numero(valor, modo)
        textos = [[formatear_numero(numero, modo) for numero in fila] for fila in valor]
        anchos = [max(len(fila[j]) for fila in textos) for j in range(len(textos[0]))]
        return "\n".join("[ " + "  ".join(numero.rjust(anchos[j]) for j, numero in enumerate(fila))
                         + " ]" for fila in textos)

    def _mostrar_resultado(self) -> None:
        """Muestra datos, resultados intermedios, ambos miembros y diagnóstico."""

        if self._resultado is None:
            return
        resultado = self._resultado
        lineas = [resultado.especificacion.formula, "=" * 42, "ENTRADAS"]
        for nombre, valor in self._entradas.items():
            lineas.extend([f"{nombre} =", self._formatear_valor(valor)])
        if resultado.intermedios:
            lineas.extend(["", "RESULTADOS INTERMEDIOS"])
            for nombre, valor in resultado.intermedios:
                lineas.extend([f"{nombre} =", self._formatear_valor(valor)])
        lineas.extend(["", "MIEMBRO IZQUIERDO", self._formatear_valor(resultado.izquierdo),
                       "", "MIEMBRO DERECHO", self._formatear_valor(resultado.derecho), "",
                       "✓ Se cumple." if resultado.se_cumple else "✗ No se cumple."])
        self._escribir("\n".join(lineas))

    def _escribir(self, texto: str) -> None:
        """Sustituye el diagnóstico visible con información nueva."""

        self.salida.configure(state="normal")
        self.salida.delete("1.0", "end")
        self.salida.insert("1.0", texto)
        self.salida.configure(state="disabled")

    def refresh_format(self) -> None:
        """Actualiza la presentación del último cálculo sin releer ni redondear entradas."""

        self._mostrar_resultado()
