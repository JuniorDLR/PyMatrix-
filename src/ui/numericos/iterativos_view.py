"""Comparación didáctica de Jacobi y Gauss-Seidel del Programa 8."""

from collections.abc import Callable
import math
import tkinter as tk

import customtkinter as ctk

from src.core.numericos.iterativos import ComparacionIterativa, ResultadoIterativo, comparar_metodos
from src.ui.numericos.comun import Terminal, escribir_entrada, formato


EJEMPLOS = {
    "Clase": (
        [["10", "3", "1"], ["5", "-10", "3"], ["1", "3", "10"]],
        ["14", "-5", "14"], ["0", "0", "0"], "0.0001", "100", "Norma 2", True,
    ),
    "Reordenar": (
        [["2", "-6", "-1"], ["-3", "-1", "7"], ["-8", "1", "-2"]],
        ["-38", "-34", "-20"], ["0", "0", "0"], "0.0001", "100", "Norma ∞", True,
    ),
    "No converge": (
        [["1", "2"], ["2", "1"]], ["3", "3"], ["0", "0"],
        "0.0001", "30", "Norma ∞", False,
    ),
}


class IterativosView(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkBaseClass, get_modo: Callable[[], str]) -> None:
        super().__init__(parent, fg_color="transparent")
        self.get_modo = get_modo
        self.resultado: ComparacionIterativa | None = None
        self.grid_columnconfigure(0, minsize=380)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        entrada = ctk.CTkScrollableFrame(self, width=375, fg_color=("#f1f5f9", "#111827"))
        entrada.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(entrada, text="Jacobi y Gauss-Seidel",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=("#0369a1", "#38bdf8")).pack(anchor="w", padx=14, pady=(16, 8))
        ctk.CTkLabel(entrada, text="Compara ambas sucesiones desde el mismo x⁽⁰⁾.",
                     wraplength=340, justify="left").pack(anchor="w", padx=14, pady=(0, 12))

        configuracion = ctk.CTkFrame(entrada, fg_color=("#ffffff", "#1f2937"))
        configuracion.pack(fill="x", padx=12, pady=5)
        fila = ctk.CTkFrame(configuracion, fg_color="transparent")
        fila.pack(fill="x", padx=12, pady=12)
        ctk.CTkLabel(fila, text="Orden n").pack(side="left")
        self.orden = ctk.CTkEntry(fila, width=55)
        self.orden.pack(side="left", padx=8)
        self.orden.insert(0, "3")
        ctk.CTkButton(fila, text="Generar", width=95, command=self._generar).pack(side="left")

        tarjeta_matriz = ctk.CTkFrame(entrada, fg_color=("#ffffff", "#1f2937"))
        tarjeta_matriz.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(tarjeta_matriz, text="Sistema Ax = b e inicio x⁽⁰⁾",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=12, pady=(12, 6))
        self.cuadricula = ctk.CTkScrollableFrame(
            tarjeta_matriz, orientation="horizontal", height=190, fg_color="transparent",
        )
        self.cuadricula.pack(fill="x", padx=12, pady=(0, 12))
        self.a: list[list[ctk.CTkEntry]] = []
        self.b: list[ctk.CTkEntry] = []
        self.x0: list[ctk.CTkEntry] = []

        parametros = ctk.CTkFrame(entrada, fg_color=("#ffffff", "#1f2937"))
        parametros.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(parametros, text="Criterio de parada",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=12, pady=(12, 6))
        self.tolerancia = self._campo(parametros, "Tolerancia E", "0.0001")
        self.maximo = self._campo(parametros, "Máximo k", "100")
        self.norma = ctk.CTkSegmentedButton(parametros, values=["Norma ∞", "Norma 2"])
        self.norma.pack(fill="x", padx=12, pady=7)
        self.norma.set("Norma ∞")
        self.reordenar = ctk.CTkCheckBox(parametros, text="Reordenar filas si ayuda")
        self.reordenar.pack(anchor="w", padx=12, pady=(6, 12))
        self.reordenar.select()

        ctk.CTkButton(entrada, text="Calcular ambos métodos", height=40,
                      command=self._calcular).pack(fill="x", padx=12, pady=(10, 5))
        ejemplos = ctk.CTkFrame(entrada, fg_color="transparent")
        ejemplos.pack(fill="x", padx=12, pady=5)
        for nombre in EJEMPLOS:
            ctk.CTkButton(ejemplos, text=nombre, fg_color="#475569", width=95,
                          command=lambda n=nombre: self._ejemplo(n)).pack(
                              side="left", fill="x", expand=True, padx=2,
                          )
        self.error = ctk.CTkLabel(entrada, text="", text_color="#ef4444",
                                  wraplength=340, justify="left")
        self.error.pack(fill="x", padx=12, pady=(0, 12))

        salida = ctk.CTkTabview(self)
        salida.grid(row=0, column=1, sticky="nsew", padx=(0, 5), pady=5)
        self.terminales: dict[str, Terminal] = {}
        for nombre in ("Resumen", "Jacobi", "Seidel"):
            pagina = salida.add(nombre)
            pagina.grid_rowconfigure(0, weight=1)
            pagina.grid_columnconfigure(0, weight=1)
            terminal = Terminal(pagina, ajustar_lineas=nombre == "Resumen")
            terminal.grid(row=0, column=0, sticky="nsew")
            self.terminales[nombre] = terminal
        grafica = salida.add("Error")
        grafica.grid_rowconfigure(0, weight=1)
        grafica.grid_columnconfigure(0, weight=1)
        self.lienzo = tk.Canvas(grafica, highlightthickness=0)
        self.lienzo.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.lienzo.bind("<Configure>", lambda _evento: self._dibujar())
        self._ejemplo("Clase")

    @staticmethod
    def _campo(parent: ctk.CTkFrame, titulo: str, inicial: str) -> ctk.CTkEntry:
        fila = ctk.CTkFrame(parent, fg_color="transparent")
        fila.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(fila, text=titulo, width=110, anchor="w").pack(side="left")
        campo = ctk.CTkEntry(fila)
        campo.pack(side="left", fill="x", expand=True)
        campo.insert(0, inicial)
        return campo

    def _generar(self) -> None:
        texto = self.orden.get().strip()
        if not texto.isascii() or not texto.isdigit() or len(texto) > 2 or not 1 <= int(texto) <= 10:
            self.error.configure(text="El orden n debe ser un entero entre 1 y 10.")
            return
        n = int(texto)
        for hijo in self.cuadricula.winfo_children():
            hijo.destroy()
        self.a, self.b, self.x0 = [], [], []
        for j in range(n):
            ctk.CTkLabel(self.cuadricula, text=f"x{j+1}", width=65).grid(
                row=0, column=j, padx=4, pady=3,
            )
        ctk.CTkLabel(self.cuadricula, text="b", width=65).grid(row=0, column=n, padx=4)
        ctk.CTkLabel(self.cuadricula, text="x⁽⁰⁾", width=65).grid(row=0, column=n+1, padx=4)
        for i in range(n):
            fila = []
            for j in range(n):
                entrada = ctk.CTkEntry(self.cuadricula, width=65, justify="center")
                entrada.grid(row=i+1, column=j, padx=4, pady=4)
                entrada.insert(0, "0")
                fila.append(entrada)
            self.a.append(fila)
            for columna, destino in ((n, self.b), (n+1, self.x0)):
                entrada = ctk.CTkEntry(self.cuadricula, width=65, justify="center")
                entrada.grid(row=i+1, column=columna, padx=4, pady=4)
                entrada.insert(0, "0")
                destino.append(entrada)
        self.cuadricula.configure(height=min(420, 45 + n * 42))
        self.resultado = None
        self._limpiar_salida()
        self.error.configure(text="")

    def _ejemplo(self, nombre: str) -> None:
        a, b, x0, tolerancia, maximo, norma, reordenar = EJEMPLOS[nombre]
        escribir_entrada(self.orden, str(len(a)))
        self._generar()
        for i, fila in enumerate(a):
            for j, valor in enumerate(fila):
                escribir_entrada(self.a[i][j], valor)
            escribir_entrada(self.b[i], b[i])
            escribir_entrada(self.x0[i], x0[i])
        escribir_entrada(self.tolerancia, tolerancia)
        escribir_entrada(self.maximo, maximo)
        self.norma.set(norma)
        self.reordenar.select() if reordenar else self.reordenar.deselect()
        self._calcular()

    def _limpiar_salida(self) -> None:
        for terminal in self.terminales.values():
            terminal.escribir("")
        self._dibujar()

    def _calcular(self) -> None:
        try:
            self.resultado = comparar_metodos(
                [[entrada.get() for entrada in fila] for fila in self.a],
                [entrada.get() for entrada in self.b],
                [entrada.get() for entrada in self.x0],
                self.tolerancia.get(), self.maximo.get(), bool(self.reordenar.get()),
                "euclidiana" if self.norma.get() == "Norma 2" else "infinito",
            )
        except (ValueError, OverflowError) as error:
            self.resultado = None
            self.error.configure(text=str(error))
            self._limpiar_salida()
            return
        self.error.configure(text="")
        self.refresh_format()

    def refresh_format(self) -> None:
        r = self.resultado
        if r is None:
            return
        fmt = lambda valor: formato(valor, self.get_modo(), 8)
        norma = "||Δx||₂" if r.criterio == "euclidiana" else "||Δx||∞"
        lineas = [
            "COMPARACIÓN DE MÉTODOS ITERATIVOS",
            "A = D + L + U; L y U son las partes estrictamente inferior y superior de A.",
            "Jacobi: x⁽ᵏ⁺¹⁾ = D⁻¹[b − (L+U)x⁽ᵏ⁾]. Usa solo valores de k.",
            "Gauss-Seidel: (D+L)x⁽ᵏ⁺¹⁾ = b − Ux⁽ᵏ⁾. Usa enseguida cada valor nuevo.",
            "",
            f"Orden de filas aplicado: {', '.join(str(i+1) for i in r.orden_filas)}.",
            "A tiene dominancia diagonal estricta." if r.dominante else
            "A no tiene dominancia diagonal estricta; la convergencia no está garantizada.",
            f"Parada para ambos: {norma} ≤ E; residuo informado: ||Ax−b||∞.",
            "",
        ]
        for metodo in (r.jacobi, r.seidel):
            ultimo = metodo.pasos[-1] if metodo.pasos else None
            lineas.append(f"{metodo.metodo.upper()}: {metodo.estado}; {len(metodo.pasos)} iteraciones.")
            if ultimo:
                lineas.append("x ≈ (" + ", ".join(fmt(v) for v in ultimo.valores) + ")")
                lineas.append(f"{norma} = {fmt(ultimo.error)}; ||Ax−b||∞ = {fmt(ultimo.residuo)}")
            else:
                lineas.append("No se obtuvo una iteración finita.")
            lineas.append("")
        if r.jacobi.estado == r.seidel.estado == "tolerancia":
            j, s = len(r.jacobi.pasos), len(r.seidel.pasos)
            lineas.append("Con el mismo criterio, " + (
                "Gauss-Seidel requirió menos iteraciones." if s < j else
                "Jacobi requirió menos iteraciones." if j < s else
                "ambos requirieron el mismo número de iteraciones."
            ))
        else:
            lineas.append("No se comparan velocidades de convergencia porque uno o ambos no alcanzaron E.")
        if r.jacobi.solucion and r.seidel.solucion:
            diferencia_metodos = max(abs(x-y) for x, y in zip(r.jacobi.solucion, r.seidel.solucion))
            lineas.append(f"Diferencia máxima entre las dos aproximaciones: {fmt(diferencia_metodos)}")
        if any(m.pasos and m.pasos[-1].residuo > 10 * m.pasos[-1].error
               for m in (r.jacobi, r.seidel) if m.estado == "tolerancia"):
            lineas.append("Aviso: revise el residuo; un cambio pequeño entre iteraciones no garantiza precisión.")
        if r.referencia is not None:
            lineas.extend(("", "REFERENCIA DIRECTA (Gauss-Jordan propio; solo contraste)",
                           "x* = (" + ", ".join(fmt(v) for v in r.referencia) + ")"))
            for metodo in (r.jacobi, r.seidel):
                if metodo.solucion:
                    diferencia = max(abs(x-y) for x, y in zip(metodo.solucion, r.referencia))
                    lineas.append(f"Diferencia máxima {metodo.metodo}–x*: {fmt(diferencia)}")
        self.terminales["Resumen"].escribir("\n".join(lineas))
        for metodo in (r.jacobi, r.seidel):
            pestaña = "Seidel" if metodo.metodo == "Gauss-Seidel" else "Jacobi"
            self.terminales[pestaña].escribir(self._tabla(metodo, r, norma, fmt))
        self._dibujar()

    @staticmethod
    def _tabla(metodo: ResultadoIterativo, r: ComparacionIterativa,
               norma: str, fmt: Callable[[float], str]) -> str:
        encabezado = ["k".rjust(4)] + [f"x{i+1}".rjust(16) for i in range(len(r.inicial))]
        encabezado += [norma.rjust(16), "||Ax−b||∞".rjust(16)]
        if r.referencia is not None:
            encabezado.append("||x*−x||₂".rjust(16))
        lineas = [metodo.metodo.upper(), " | ".join(encabezado), "-" * (22 + 19 * (len(r.inicial) + 2))]
        inicio = ["0".rjust(4)] + [fmt(v).rjust(16) for v in r.inicial] + ["—".rjust(16), "—".rjust(16)]
        if r.referencia is not None:
            inicio.append(fmt(math.hypot(*(x-y for x, y in zip(r.inicial, r.referencia)))).rjust(16))
        lineas.append(" | ".join(inicio))
        for paso in metodo.pasos:
            celdas = [str(paso.numero).rjust(4)] + [fmt(v).rjust(16) for v in paso.valores]
            celdas += [fmt(paso.error).rjust(16), fmt(paso.residuo).rjust(16)]
            if r.referencia is not None:
                celdas.append(fmt(math.hypot(*(x-y for x, y in zip(paso.valores, r.referencia)))).rjust(16))
            lineas.append(" | ".join(celdas))
        lineas.extend(("", f"Estado: {metodo.estado}.",
                       "Cada fila nueva usa x anterior completo." if metodo.metodo == "Jacobi" else
                       "En cada fila se usan los componentes nuevos ya calculados."))
        if metodo.pasos:
            previo = r.inicial
            primero = metodo.pasos[0]
            lineas.extend(("", "PRIMERA ITERACIÓN, COMPONENTE POR COMPONENTE"))
            for i, fila in enumerate(r.matriz):
                terminos = []
                for j, coef in enumerate(fila):
                    if i == j:
                        continue
                    valor = primero.valores[j] if metodo.metodo == "Gauss-Seidel" and j < i else previo[j]
                    terminos.append(f"({fmt(coef)})·({fmt(valor)})")
                suma = " + ".join(terminos) if terminos else "0"
                lineas.append(f"x{i+1}⁽¹⁾ = [{fmt(r.vector[i])} − ({suma})] / {fmt(fila[i])}"
                              f" = {fmt(primero.valores[i])}")
        return "\n".join(lineas)

    def _dibujar(self) -> None:
        lienzo = self.lienzo
        lienzo.delete("all")
        claro = ctk.get_appearance_mode() == "Light"
        fondo = "#eff6ff" if claro else "#111827"
        tinta = "#172554" if claro else "#e2e8f0"
        lienzo.configure(background=fondo)
        r = self.resultado
        ancho, alto = lienzo.winfo_width(), lienzo.winfo_height()
        if r is None or ancho < 100 or alto < 100:
            lienzo.create_text(24, 24, text="Calcule ambos métodos para ver la gráfica.",
                               anchor="nw", fill=tinta)
            return
        series = [(r.jacobi, "#2563eb" if claro else "#38bdf8"),
                  (r.seidel, "#059669" if claro else "#34d399")]
        puntos = [(paso.numero, math.log10(max(paso.error, 1e-300)))
                  for metodo, _ in series for paso in metodo.pasos if paso.error > 0]
        if not puntos:
            lienzo.create_text(24, 24, text="No hay errores positivos finitos para graficar.",
                               anchor="nw", fill=tinta)
            return
        xmin, xmax = 0, max(k for k, _ in puntos)
        ymin, ymax = min(y for _, y in puntos), max(y for _, y in puntos)
        if ymax == ymin:
            ymax += 1
            ymin -= 1
        x0, y0, x1, y1 = 62, 70, max(64, ancho - 28), max(72, alto - 55)
        lienzo.create_line(x0, y0, x0, y1, x1, y1, fill=tinta, width=2)
        lienzo.create_text(x0, 20, text="Error por iteración (escala log₁₀)",
                           anchor="nw", fill=tinta, font=("Segoe UI", 14, "bold"))
        lienzo.create_text((x0+x1)/2, alto-17, text="Iteración k", fill=tinta)
        for metodo, color in series:
            coordenadas = []
            for paso in metodo.pasos:
                if paso.error <= 0:
                    continue
                x = x0 + (x1-x0) * paso.numero / max(xmax, 1)
                y = y1 - (y1-y0) * (math.log10(max(paso.error, 1e-300))-ymin)/(ymax-ymin)
                coordenadas.extend((x, y))
            if len(coordenadas) >= 4:
                lienzo.create_line(*coordenadas, fill=color, width=2)
            elif coordenadas:
                x, y = coordenadas
                lienzo.create_oval(x-3, y-3, x+3, y+3, fill=color, outline="")
        for i, (metodo, color) in enumerate(series):
            lienzo.create_text(x0 + i*150, 48, text="● " + metodo.metodo,
                               anchor="w", fill=color, font=("Segoe UI", 11, "bold"))
        lienzo.create_text(x0-8, y0, text=f"10^{ymax:.1f}", anchor="e", fill=tinta)
        lienzo.create_text(x0-8, y1, text=f"10^{ymin:.1f}", anchor="e", fill=tinta)
        lienzo.create_text(x1, y1+15, text=str(xmax), anchor="n", fill=tinta)

    def set_theme(self, modo: str) -> None:
        for terminal in self.terminales.values():
            terminal.set_theme(modo)
        self._dibujar()
