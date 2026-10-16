"""Vista gráfica de factorización LU y resolución de sistemas de la sesión 12."""

from fractions import Fraction
from typing import Any

import customtkinter as ctk

from src.core.domain import formatear_numero, a_subindice
from src.core.exact_math import MatrizF, matriz_identidad, parsear_fraccion
from modulos.modulo_lu import ResultadoLU, ResultadoSistemaLU, factorizar_lu, resolver_sistema_lu


class LUView(ctk.CTkFrame):
    """Muestra LU y la solución de Ax=b, con entradas y salida desplazables."""

    def __init__(self, master: Any, get_modo_numero, banco_matrices: dict, **kwargs: Any):
        """Recibe el formato global y el mismo banco de matrices de la vista existente."""

        super().__init__(master, **kwargs)
        self.get_modo_numero = get_modo_numero
        self.banco_matrices = banco_matrices
        self._resultado_lu: ResultadoLU | None = None
        self._resultado_sistema: ResultadoSistemaLU | None = None
        self._aviso: str | None = None
        self.grid_columnconfigure(0, weight=0, minsize=370)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Construye cuadrículas editables y conserva la terminal de procedimiento."""

        self.entrada_scroll = ctk.CTkScrollableFrame(
            self, width=350, fg_color=("#f1f5f9", "#111827"), corner_radius=0
        )
        entrada = self.entrada_scroll
        entrada.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        ctk.CTkLabel(entrada, text="Factorización LU de Matriz A",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=14, pady=(14, 8))

        tamanio = ctk.CTkFrame(entrada, fg_color=("#ffffff", "#1f2937"), corner_radius=10)
        tamanio.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkLabel(tamanio, text="Dimensiones", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, columnspan=4, sticky="w", padx=12, pady=(10, 6)
        )
        ctk.CTkLabel(tamanio, text="Filas (m):").grid(row=1, column=0, padx=(12, 2))
        self.entry_m = ctk.CTkEntry(tamanio, width=45, justify="center")
        self.entry_m.grid(row=1, column=1, padx=2)
        self.entry_m.insert(0, "3")
        ctk.CTkLabel(tamanio, text="Columnas (n):").grid(row=1, column=2, padx=(7, 2))
        self.entry_n = ctk.CTkEntry(tamanio, width=45, justify="center")
        self.entry_n.grid(row=1, column=3, padx=(2, 12))
        self.entry_n.insert(0, "3")
        ctk.CTkButton(tamanio, text="Generar", height=28, command=self._generar_grid).grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=(12, 4), pady=(10, 12)
        )
        ctk.CTkButton(tamanio, text="Ejemplo", height=28, command=self._cargar_ejemplo,
                      fg_color="#475569", hover_color="#334155").grid(
            row=2, column=2, columnspan=2, sticky="ew", padx=(4, 12), pady=(10, 12)
        )

        matriz_panel = ctk.CTkFrame(entrada, fg_color=("#ffffff", "#1f2937"), corner_radius=10)
        matriz_panel.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(matriz_panel, text="Matriz A", font=ctk.CTkFont(size=12, weight="bold")).pack(
            anchor="w", padx=12, pady=(10, 3)
        )
        self.grid_scroll_a = ctk.CTkScrollableFrame(matriz_panel, orientation="horizontal",
                                                     fg_color="transparent", height=140)
        self.grid_scroll_a.pack(fill="x", padx=8, pady=(0, 8))
        self.frame_grid_a = ctk.CTkFrame(self.grid_scroll_a, fg_color="transparent")
        self.frame_grid_a.pack(anchor="w")
        self.entries_a: list[list[ctk.CTkEntry]] = []

        banco = ctk.CTkFrame(entrada, fg_color=("#ffffff", "#1f2937"), corner_radius=10)
        banco.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(banco, text="Banco de matrices", font=ctk.CTkFont(size=12, weight="bold")).pack(
            anchor="w", padx=12, pady=(10, 4)
        )
        banco_fila = ctk.CTkFrame(banco, fg_color="transparent")
        banco_fila.pack(fill="x", padx=12, pady=(0, 10))
        self.menu_banco = ctk.CTkOptionMenu(banco_fila, values=["(Banco vacío)"], width=115)
        self.menu_banco.pack(side="left", fill="x", expand=True, padx=(0, 4))
        ctk.CTkButton(banco_fila, text="↻", width=30, command=self.actualizar_banco).pack(side="left", padx=2)
        ctk.CTkButton(banco_fila, text="Cargar en A", width=85, command=self._cargar_banco).pack(
            side="left", padx=(2, 0)
        )

        vector_panel = ctk.CTkFrame(entrada, fg_color=("#ffffff", "#1f2937"), corner_radius=10)
        vector_panel.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(vector_panel, text="Vector de términos independientes b (m componentes):",
                     wraplength=310, justify="left", font=ctk.CTkFont(size=12, weight="bold")).pack(
            anchor="w", padx=12, pady=(10, 4)
        )
        self.frame_grid_b = ctk.CTkFrame(vector_panel, fg_color="transparent")
        self.frame_grid_b.pack(anchor="w", padx=12, pady=(0, 10))
        self.entries_b: list[ctk.CTkEntry] = []

        ctk.CTkButton(entrada, text="1. Factorizar A = LU", command=self._factorizar,
                      height=36, font=ctk.CTkFont(weight="bold"), fg_color="#0284c7",
                      hover_color="#0369a1").pack(fill="x", padx=12, pady=(10, 3))
        ctk.CTkButton(entrada, text="2. Resolver Ax=b con LU", command=self._resolver,
                      height=36, font=ctk.CTkFont(weight="bold"), fg_color="#059669",
                      hover_color="#047857").pack(
            fill="x", padx=12, pady=3
        )
        ctk.CTkLabel(
            entrada, text="Si un pivote es cero, se intercambian filas y se verifica P·A = L·U.",
            wraplength=310, justify="left", text_color=("gray35", "gray75"),
        ).pack(anchor="w", padx=14, pady=(8, 8))
        guardar = ctk.CTkFrame(entrada, fg_color="transparent")
        guardar.pack(fill="x", padx=12, pady=(0, 20))
        self.btn_guardar_l = ctk.CTkButton(guardar, text="Guardar L", state="disabled",
                                          command=lambda: self._guardar_factor("L"), width=110)
        self.btn_guardar_l.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.btn_guardar_u = ctk.CTkButton(guardar, text="Guardar U", state="disabled",
                                          command=lambda: self._guardar_factor("U"), width=110)
        self.btn_guardar_u.pack(side="left", fill="x", expand=True, padx=(4, 0))

        salida = ctk.CTkFrame(self)
        salida.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        salida.grid_columnconfigure(0, weight=1)
        salida.grid_rowconfigure(1, weight=1)
        encabezado = ctk.CTkFrame(salida, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 0))
        ctk.CTkLabel(encabezado, text="Procedimiento y comprobación",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        ctk.CTkButton(encabezado, text="Limpiar", width=70, command=self._limpiar_salida,
                      fg_color=("#dc2626", "#b91c1c"), hover_color=("#b91c1c", "#991b1b")).pack(side="right")
        self.salida = ctk.CTkTextbox(salida, font=ctk.CTkFont(family="Consolas", size=12), wrap="none")
        self.salida.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.salida.configure(state="disabled")
        self.actualizar_banco()
        self._generar_grid()

    def _generar_grid(self) -> None:
        """Crea las celdas de A y b para dimensiones positivas y manejables."""

        try:
            m, n = int(self.entry_m.get()), int(self.entry_n.get())
            if not 1 <= m <= 30 or not 1 <= n <= 30:
                raise ValueError
        except ValueError:
            self._mostrar_error("Las dimensiones deben ser enteros entre 1 y 30.")
            return
        for marco in (self.frame_grid_a, self.frame_grid_b):
            for widget in marco.winfo_children():
                widget.destroy()
        self.grid_scroll_a.configure(height=36 + 33 * m)
        ctk.CTkLabel(self.frame_grid_a, text="", width=32).grid(row=0, column=0)
        for j in range(n):
            ctk.CTkLabel(self.frame_grid_a, text=f"Col {a_subindice(j+1)}", width=44,
                         text_color=("#0284c7", "#38bdf8")).grid(row=0, column=j+1, padx=2)
        self.entries_a = []
        for i in range(m):
            ctk.CTkLabel(self.frame_grid_a, text=f"F{a_subindice(i+1)}", width=32).grid(row=i+1, column=0, padx=2)
            fila = []
            for j in range(n):
                entrada = ctk.CTkEntry(self.frame_grid_a, width=44, height=28, justify="center")
                entrada.grid(row=i+1, column=j+1, padx=2, pady=2)
                fila.append(entrada)
            self.entries_a.append(fila)
        self.entries_b = []
        for i in range(m):
            ctk.CTkLabel(self.frame_grid_b, text=f"b{a_subindice(i+1)}", width=30).grid(row=i, column=0, padx=(0, 4))
            entrada = ctk.CTkEntry(self.frame_grid_b, width=60, height=28, justify="center")
            entrada.grid(row=i, column=1, pady=2)
            self.entries_b.append(entrada)

    def _cargar_ejemplo(self) -> None:
        """Carga un sistema 3×3 invertible sin pivotes nulos."""

        self._poner_dimensiones(3, 3)
        self._generar_grid()
        for i, fila in enumerate(((2, 1, -1), (1, 3, 2), (1, 0, 2))):
            for j, valor in enumerate(fila):
                self.entries_a[i][j].insert(0, str(valor))
        for entrada, valor in zip(self.entries_b, (8, 13, 7)):
            entrada.insert(0, str(valor))

    def _poner_dimensiones(self, m: int, n: int) -> None:
        for entrada, valor in ((self.entry_m, m), (self.entry_n, n)):
            entrada.delete(0, "end")
            entrada.insert(0, str(valor))

    def _poner_matriz_a(self, matriz: list[list[Any]]) -> None:
        if not matriz or not matriz[0] or any(len(fila) != len(matriz[0]) for fila in matriz):
            raise ValueError("La matriz A debe ser rectangular y no vacía.")
        if len(matriz) > 30 or len(matriz[0]) > 30:
            raise ValueError("La cuadrícula admite como máximo 30 filas y 30 columnas.")
        self._poner_dimensiones(len(matriz), len(matriz[0]))
        self._generar_grid()
        for i, fila in enumerate(matriz):
            for j, valor in enumerate(fila):
                self.entries_a[i][j].insert(0, str(valor))


    def _leer_matriz_a(self) -> MatrizF:
        try:
            m, n = int(self.entry_m.get()), int(self.entry_n.get())
        except ValueError as error:
            raise ValueError("Corrija las dimensiones de A y pulse Generar.") from error
        if len(self.entries_a) != m or any(len(fila) != n for fila in self.entries_a):
            raise ValueError("Las dimensiones de A cambiaron; pulse Generar antes de calcular.")
        matriz: MatrizF = []
        for i, fila in enumerate(self.entries_a, start=1):
            valores = []
            for j, entrada in enumerate(fila, start=1):
                texto = entrada.get().strip()
                if not texto:
                    raise ValueError(f"Ingrese A[{i},{j}].")
                try:
                    valores.append(parsear_fraccion(texto))
                except (ValueError, ZeroDivisionError) as error:
                    raise ValueError(f"A[{i},{j}] no es un número válido: '{texto}'.") from error
            matriz.append(valores)
        return matriz

    def actualizar_banco(self) -> None:
        """Actualiza los nombres disponibles en el banco compartido."""

        nombres = sorted(self.banco_matrices) or ["(Banco vacío)"]
        self.menu_banco.configure(values=nombres)
        self.menu_banco.set(nombres[0])

    def _cargar_banco(self) -> None:
        """Copia una matriz guardada a la cuadrícula A sin modificar el banco."""

        nombre = self.menu_banco.get()
        if nombre not in self.banco_matrices:
            self._mostrar_error("Seleccione una matriz guardada; actualice primero el Banco.")
            return
        try:
            self._poner_matriz_a(self.banco_matrices[nombre])
        except ValueError as error:
            self._mostrar_error(f"Matriz '{nombre}': {error}")

    def _guardar_factor(self, nombre_factor: str) -> None:
        """Guarda L o U con un nombre elegido por el usuario en el banco existente."""

        if self._resultado_lu is None:
            return
        dialogo = ctk.CTkInputDialog(title=f"Guardar {nombre_factor}", text="Nombre de la matriz en el Banco:")
        nombre = dialogo.get_input()
        if nombre is None:
            return
        nombre = nombre.strip()
        if not nombre:
            self._mostrar_error("Escriba un nombre para guardar la matriz.")
            return
        if nombre in self.banco_matrices:
            self._mostrar_error(f"El nombre '{nombre}' ya existe en el Banco. Elija otro.")
            return
        matriz = self._resultado_lu.matriz_l if nombre_factor == "L" else self._resultado_lu.matriz_u
        self.banco_matrices[nombre] = [fila[:] for fila in matriz]
        self.actualizar_banco()
        self._aviso = f"Matriz {nombre_factor} guardada como '{nombre}'."
        self._mostrar_resultado()

    def _factorizar(self) -> None:
        """Factoriza A desde la cuadrícula sin requerir b."""

        self._resultado_lu = None
        self._resultado_sistema = None
        self._aviso = None
        self._cambiar_guardado("disabled")
        try:
            matriz = self._leer_matriz_a()
            self._resultado_lu = factorizar_lu(matriz)
        except ValueError as error:
            self._mostrar_error(str(error))
            return
        if self._resultado_lu.es_correcta:
            self._cambiar_guardado("normal")
        else:
            self._aviso = "Falló la comprobación exacta L·U = P·A; los factores no se guardarán."
        self._mostrar_resultado()

    def _resolver(self) -> None:
        """Encadena A→LU→y→x y conserva los factores si el sistema no es resoluble."""

        self._factorizar()
        if self._resultado_lu is None:
            return
        try:
            vector_b = []
            for i, entrada in enumerate(self.entries_b):
                val_str = entrada.get().strip()
                if not val_str:
                    raise ValueError(f"Ingrese la componente b{a_subindice(i+1)} del vector b.")
                vector_b.append(parsear_fraccion(val_str))
            if len(vector_b) != len(self._resultado_lu.matriz_a):
                raise ValueError(f"El vector b necesita {len(self._resultado_lu.matriz_a)} componentes; tiene {len(vector_b)}.")
            self._resultado_sistema = resolver_sistema_lu(self._resultado_lu, vector_b)
        except (ValueError, ZeroDivisionError) as error:
            self._aviso = f"No se resolvió Ax=b: {error}"
        self._mostrar_resultado()

    def _cambiar_guardado(self, estado: str) -> None:
        """Activa el guardado únicamente cuando L y U están verificadas."""

        self.btn_guardar_l.configure(state=estado)
        self.btn_guardar_u.configure(state=estado)

    def _mostrar_error(self, mensaje: str) -> None:
        """Comunica errores de entrada o de la factorización en la salida visible."""

        self._escribir(f"❌ {mensaje}")

    def _limpiar_salida(self) -> None:
        """Limpia el historial visible sin borrar los datos introducidos."""

        self._escribir("")

    def _escribir(self, texto: str) -> None:
        """Sustituye el texto del procedimiento."""

        self.salida.configure(state="normal")
        self.salida.delete("1.0", "end")
        self.salida.insert("1.0", texto)
        self.salida.configure(state="disabled")

    def _formatear_matriz(self, matriz: MatrizF) -> str:
        """Alinea columnas conservando fracciones exactas o decimales de lectura."""

        modo = self.get_modo_numero()
        textos = [[formatear_numero(valor, modo) for valor in fila] for fila in matriz]
        anchos = [max(len(fila[j]) for fila in textos) for j in range(len(textos[0]))]
        return "\n".join("[ " + "  ".join(valor.rjust(anchos[j]) for j, valor in enumerate(fila)) + " ]"
                         for fila in textos)

    def _formatear_vector(self, vector: list[Fraction]) -> str:
        """Formatea un vector columna según el modo numérico global."""

        return self._formatear_matriz([[valor] for valor in vector])

    def _lineas_sustitucion(
        self,
        matriz: MatrizF,
        derecha: list[Fraction],
        resultados: list[Fraction],
        variable: str,
        hacia_atras: bool,
    ) -> list[str]:
        """Explica cada incógnita usando solo los valores ya calculados."""

        modo = self.get_modo_numero()
        n = len(resultados)
        lineas: list[str] = []
        filas = range(n - 1, -1, -1) if hacia_atras else range(n)
        for i in filas:
            columnas = range(i, n) if hacia_atras else range(i + 1)
            conocidas = range(i + 1, n) if hacia_atras else range(i)
            ecuacion = " + ".join(
                f"({formatear_numero(matriz[i][j], modo)})·{variable}{a_subindice(j + 1)}"
                for j in columnas if matriz[i][j] != 0
            )
            sustituidos = [
                f"({formatear_numero(matriz[i][j], modo)})·({formatear_numero(resultados[j], modo)})"
                for j in conocidas if matriz[i][j] != 0
            ]
            suma = sum((matriz[i][j] * resultados[j] for j in conocidas), Fraction(0))
            lado_derecho = formatear_numero(derecha[i], modo)
            suma_texto = formatear_numero(suma, modo)
            diagonal = formatear_numero(matriz[i][i], modo)
            valor = formatear_numero(resultados[i], modo)
            lineas.extend([
                "",
                f"  Fila {i + 1}: {ecuacion} = {lado_derecho}",
                f"  Valores ya obtenidos: {' + '.join(sustituidos)} = {suma_texto}"
                if sustituidos else "  Aún no hay incógnitas resueltas; la suma conocida es 0.",
                f"  {variable}{a_subindice(i + 1)} = ({lado_derecho} - {suma_texto}) / ({diagonal}) = {valor}",
            ])
        return lineas

    def _mostrar_resultado(self) -> None:
        """Reconstruye la salida completa desde los resultados exactos almacenados."""

        factores = self._resultado_lu
        if factores is None:
            return
        m, n = len(factores.matriz_a), len(factores.matriz_a[0])
        hay_permutacion = factores.matriz_p != matriz_identidad(m)
        lineas = [f"FACTORIZACIÓN LU · A de {m}×{n}", "=" * 42,
                  "A =", self._formatear_matriz(factores.matriz_a), "",
                  "PASO 1 · Reducción de filas",
                  "Con intercambio de filas: P·A = L·U" if hay_permutacion else "Sin permutaciones: A = L·U"]
        for numero, paso in enumerate(factores.pasos, start=1):
            lineas.extend(["", f"{numero}. {paso.descripcion}"])
            if hay_permutacion:
                lineas.extend(["P =", self._formatear_matriz(paso.matriz_p)])
            lineas.extend(["L =", self._formatear_matriz(paso.matriz_l),
                           "U =", self._formatear_matriz(paso.matriz_u)])
        lineas.append("")
        if hay_permutacion:
            lineas.extend(["PASO 2 · Comprobación P·A = L·U",
                           "P·A =", self._formatear_matriz(factores.producto_pa)])
        else:
            lineas.append("PASO 2 · Comprobación A = L·U")
        lineas.extend(["L·U =", self._formatear_matriz(factores.producto_lu),
                       f"{'✓ Se cumple' if factores.es_correcta else '✗ No se cumple'}: "
                       f"{'P·A' if hay_permutacion else 'A'} "
                       f"{'=' if factores.es_correcta else '≠'} L·U."])

        sistema = self._resultado_sistema
        if sistema is not None:
            lineas.extend(["", "=" * 42,
                           "PASO 3 · Sustitución hacia adelante: L·y = P·b" if hay_permutacion
                           else "PASO 3 · Sustitución hacia adelante: L·y = b",
                           "L =", self._formatear_matriz(factores.matriz_l),
                           "b =", self._formatear_vector(sistema.vector_b)])
            if hay_permutacion:
                lineas.extend(["P·b (mismo intercambio de filas) =",
                               self._formatear_vector(sistema.vector_pb)])
            lineas.extend(self._lineas_sustitucion(
                factores.matriz_l, sistema.vector_pb, sistema.vector_y, "y", hacia_atras=False
            ))
            lineas.extend(["", "Vector intermedio y =", self._formatear_vector(sistema.vector_y),
                           "", "PASO 4 · Sustitución hacia atrás: U·x = y",
                           "U =", self._formatear_matriz(factores.matriz_u),
                           "y =", self._formatear_vector(sistema.vector_y)])
            lineas.extend(self._lineas_sustitucion(
                factores.matriz_u, sistema.vector_y, sistema.vector_x, "x", hacia_atras=True
            ))
            lineas.extend(["", "Solución x =", self._formatear_vector(sistema.vector_x),
                           "", "PASO 5 · Comprobación A·x = b"])
            modo = self.get_modo_numero()
            for i, fila in enumerate(factores.matriz_a):
                productos = [
                    f"({formatear_numero(coeficiente, modo)})·({formatear_numero(sistema.vector_x[j], modo)})"
                    for j, coeficiente in enumerate(fila)
                ]
                valores = [
                    f"({formatear_numero(coeficiente * sistema.vector_x[j], modo)})"
                    for j, coeficiente in enumerate(fila)
                ]
                obtenido = formatear_numero(sistema.producto_ax[i], modo)
                esperado = formatear_numero(sistema.vector_b[i], modo)
                coincide = sistema.producto_ax[i] == sistema.vector_b[i]
                lineas.extend([
                    "",
                    f"  Fila {i + 1}: {' + '.join(productos)}",
                    f"          = {' + '.join(valores)} = {obtenido}",
                    f"          b{a_subindice(i + 1)} = {esperado}  {'✓ coincide' if coincide else '✗ no coincide'}",
                ])
            lineas.extend(["", "A·x =", self._formatear_vector(sistema.producto_ax),
                           "b =", self._formatear_vector(sistema.vector_b),
                           "✓ Comprobación exacta: A·x = b." if sistema.es_correcta
                           else "✗ No se cumple: A·x ≠ b."])
        if self._aviso:
            lineas.extend(["", f"⚠ {self._aviso}"])
        self._escribir("\n".join(lineas))

    def refresh_format(self) -> None:
        """Actualiza la representación sin perder la exactitud de A, L, U, b, y o x."""

        self._mostrar_resultado()
