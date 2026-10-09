"""Operaciones matriciales con fracciones exactas: suma, producto, traspuesta, determinantes e inversas.
Tema de clase: álgebra matricial, determinantes, matriz inversa y sus propiedades (sesiones 10 y 11).
Las funciones de cálculo no usan input() ni print(); devuelven datos y textos de pasos.
Elaborado por: Grupo x"""

from fractions import Fraction
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass


MatrizF = List[List[Fraction]]


def parsear_fraccion(valor: Any) -> Fraction:
    """Convierte int, float, str ('3/4', '0.5') o Fraction a Fraction exacta.
    Se usa Fraction y no float para que inversas y determinantes no acumulen error de redondeo."""
    if isinstance(valor, Fraction):
        return valor
    if isinstance(valor, int):
        return Fraction(valor, 1)
    if isinstance(valor, float):
        # Convertir float a string para evitar residuos de coma flotante (ej. 0.1 -> 1/10)
        return Fraction(str(valor)).limit_denominator(1000000)
    if isinstance(valor, str):
        v = valor.strip()
        if "/" in v:
            partes = v.split("/")
            if len(partes) == 2:
                return Fraction(int(partes[0].strip()), int(partes[1].strip()))
        return Fraction(v)
    raise TypeError(f"Tipo no soportado para conversión a Fraction: {type(valor)}")


def crear_matriz(datos: List[List[Any]]) -> MatrizF:
    """Crea una matriz de Fraction a partir de una lista anidada de números.
    Lanza ValueError si está vacía o si sus filas tienen longitudes distintas."""
    if not datos or not datos[0]:
        raise ValueError("La matriz no puede estar vacía.")
    num_cols = len(datos[0])
    matriz: MatrizF = []
    for f_idx, fila in enumerate(datos):
        # Una matriz irregular no está definida: cada fila debe tener las mismas columnas.
        if len(fila) != num_cols:
            raise ValueError(f"Fila {f_idx + 1} tiene longitud irregular ({len(fila)} != {num_cols}).")
        matriz.append([parsear_fraccion(elem) for elem in fila])
    return matriz


def copiar_matriz(A: MatrizF) -> MatrizF:
    """Devuelve una copia de A con filas nuevas, para modificarla sin alterar la original."""
    return [fila[:] for fila in A]


def matriz_identidad(n: int) -> MatrizF:
    """Devuelve la identidad Iₙ (n x n); n debe ser mayor que cero."""
    if n <= 0:
        raise ValueError("El orden n de la matriz identidad debe ser mayor a cero.")
    return [[Fraction(1 if i == j else 0, 1) for j in range(n)] for i in range(n)]


def son_matrices_iguales(A: MatrizF, B: MatrizF) -> bool:
    """Devuelve True si A y B tienen las mismas dimensiones y las mismas entradas."""
    # Con Fraction se compara con ==, sin tolerancia: no hay error de redondeo.
    if len(A) != len(B) or len(A[0]) != len(B[0]):
        return False
    for i in range(len(A)):
        for j in range(len(A[0])):
            if A[i][j] != B[i][j]:
                return False
    return True


def matriz_a_cadena(A: MatrizF, ancho_columna: int = 10) -> str:
    """Devuelve A como texto con corchetes y columnas alineadas a ancho_columna."""
    filas = []
    for fila in A:
        elementos = [f"{str(elem):>{ancho_columna}}" for elem in fila]
        filas.append("[ " + " ".join(elementos) + " ]")
    return "\n".join(filas)


def validar_mismas_dimensiones(A: MatrizF, B: MatrizF, operacion: str = "operación") -> Tuple[int, int]:
    """Comprueba que A y B tengan el mismo orden m x n y devuelve (m, n).
    Lanza ValueError si alguna está vacía o si los órdenes difieren."""
    if not A or not A[0] or not B or not B[0]:
        raise ValueError("Las matrices no pueden estar vacías.")
    m_A, n_A = len(A), len(A[0])
    m_B, n_B = len(B), len(B[0])
    # Suma y resta operan entrada a entrada: sin igual orden no hay pareja para cada entrada.
    if m_A != m_B or n_A != n_B:
        raise ValueError(
            f"Dimensiones incompatibles para {operacion}: A es {m_A}×{n_A} y B es {m_B}×{n_B}. "
            "Ambas matrices deben tener idénticas dimensiones m × n."
        )
    return m_A, n_A


def sumar_matrices(A: MatrizF, B: MatrizF) -> MatrizF:
    """Devuelve C = A + B, con C_ij = A_ij + B_ij. Valida dimensiones antes de operar."""
    m, n = validar_mismas_dimensiones(A, B, "suma de matrices")
    return [[A[i][j] + B[i][j] for j in range(n)] for i in range(m)]


def restar_matrices(A: MatrizF, B: MatrizF) -> MatrizF:
    """Devuelve C = A - B, con C_ij = A_ij - B_ij. Valida dimensiones antes de operar."""
    m, n = validar_mismas_dimensiones(A, B, "resta de matrices")
    return [[A[i][j] - B[i][j] for j in range(n)] for i in range(m)]


def multiplicar_escalar(c: Any, A: MatrizF) -> MatrizF:
    """Devuelve c·A multiplicando cada entrada de A por el escalar c (int, str o Fraction)."""
    if not A or not A[0]:
        raise ValueError("La matriz no puede estar vacía.")
    c_frac = parsear_fraccion(c)
    m, n = len(A), len(A[0])
    return [[c_frac * A[i][j] for j in range(n)] for i in range(m)]


@dataclass
class DetalleProductoMatricial:
    """Resultado del producto A·B: matriz, dimensiones y desglose de cada celda."""
    matriz_resultado: MatrizF
    dimensiones_A: Tuple[int, int]
    dimensiones_B: Tuple[int, int]
    dimensiones_resultado: Tuple[int, int]
    desglose_pasos: List[str]


def multiplicar_matrices(A: MatrizF, B: MatrizF) -> MatrizF:
    """Devuelve A·B (m x p). Requiere columnas de A == filas de B; si no, lanza ValueError.
    A: m filas de n elementos. B: n filas de p elementos."""
    if not A or not A[0] or not B or not B[0]:
        raise ValueError("Ninguna de las matrices puede estar vacía.")
    m = len(A)
    n_A = len(A[0])
    n_B = len(B)
    p = len(B[0])

    # Cada entrada es fila por columna: sin columnas de A == filas de B no hay productos que sumar.
    if n_A != n_B:
        raise ValueError(
            f"Incompatibilidad de dimensiones para el producto: A es {m}×{n_A} y B es {n_B}×{p}. "
            f"El número de columnas de A ({n_A}) debe coincidir con el número de filas de B ({n_B})."
        )

    C: MatrizF = []
    for i in range(m):
        fila: List[Fraction] = []
        for j in range(p):
            # Elemento (i, j) = fila i de A por columna j de B.
            acumulador = Fraction(0, 1)
            for k in range(n_A):
                acumulador += A[i][k] * B[k][j]
            fila.append(acumulador)
        C.append(fila)
    return C


def multiplicar_matrices_explicado(A: MatrizF, B: MatrizF) -> DetalleProductoMatricial:
    """Calcula A·B como multiplicar_matrices y devuelve además el desglose de texto de cada celda
    (DetalleProductoMatricial)."""
    if not A or not A[0] or not B or not B[0]:
        raise ValueError("Ninguna de las matrices puede estar vacía.")
    m, n_A = len(A), len(A[0])
    n_B, p = len(B), len(B[0])

    if n_A != n_B:
        raise ValueError(
            f"Incompatibilidad de dimensiones: A es {m}×{n_A} y B es {n_B}×{p} (columnas de A ≠ filas de B)."
        )

    C: MatrizF = []
    desglose: List[str] = []

    for i in range(m):
        fila: List[Fraction] = []
        for j in range(p):
            acumulador = Fraction(0, 1)
            terminos = []
            for k in range(n_A):
                prod = A[i][k] * B[k][j]
                acumulador += prod
                terminos.append(f"({A[i][k]})·({B[k][j]})")
            fila.append(acumulador)
            expresion = " + ".join(terminos)
            desglose.append(f"C[{i+1},{j+1}] = {expresion} = {acumulador}")
        C.append(fila)

    return DetalleProductoMatricial(
        matriz_resultado=C,
        dimensiones_A=(m, n_A),
        dimensiones_B=(n_B, p),
        dimensiones_resultado=(m, p),
        desglose_pasos=desglose
    )


def trasponer_matriz(A: MatrizF) -> MatrizF:
    """Devuelve Aᵀ (n x m): la fila j de la traspuesta es la columna j de A."""
    if not A or not A[0]:
        raise ValueError("La matriz no puede estar vacía.")
    m, n = len(A), len(A[0])
    return [[A[i][j] for i in range(m)] for j in range(n)]


def validar_matriz_cuadrada(A: MatrizF, operacion: str = "operación") -> int:
    """Comprueba que A sea n x n y devuelve n; lanza ValueError si no lo es.
    Determinantes e inversas solo existen para matrices cuadradas."""
    if not A or not A[0]:
        raise ValueError("La matriz no puede estar vacía.")
    n = len(A)
    for i, fila in enumerate(A):
        if len(fila) != n:
            raise ValueError(
                f"La matriz no es cuadrada para {operacion}: fila {i+1} tiene {len(fila)} columnas y A tiene {n} filas."
            )
    return n


def obtener_submatriz_menor(A: MatrizF, fila_elim: int, col_elim: int) -> MatrizF:
    """Devuelve A sin la fila fila_elim ni la columna col_elim (índices desde 0).
    Es el menor M_ij que usan los cofactores."""
    return [
        [A[i][j] for j in range(len(A[0])) if j != col_elim]
        for i in range(len(A)) if i != fila_elim
    ]


def cofactor(A: MatrizF, i: int, j: int) -> Fraction:
    """Devuelve el cofactor C_ij = (-1)^(i+j) · det(M_ij), con i y j desde 0."""
    sub = obtener_submatriz_menor(A, i, j)
    # El signo (-1)^(i+j) sigue el patrón de cofactores: alterna según la posición.
    signo = Fraction(1 if (i + j) % 2 == 0 else -1, 1)
    det_menor, _ = determinante_cofactores(sub)
    return signo * det_menor


def matriz_cofactores(A: MatrizF) -> MatrizF:
    """Devuelve la matriz C de cofactores de una matriz cuadrada A."""
    n = validar_matriz_cuadrada(A, "matriz de cofactores")
    if n == 1:
        # Para orden 1, el cofactor de [a₁₁] se define convencionalmente como 1
        return [[Fraction(1, 1)]]
    C: MatrizF = []
    for i in range(n):
        fila: List[Fraction] = []
        for j in range(n):
            fila.append(cofactor(A, i, j))
        C.append(fila)
    return C


def matriz_adjunta(A: MatrizF) -> MatrizF:
    """Devuelve adj(A) = Cᵀ, la traspuesta de la matriz de cofactores."""
    C = matriz_cofactores(A)
    return trasponer_matriz(C)


def determinante_cofactores(A: MatrizF) -> Tuple[Fraction, List[str]]:
    """Devuelve (det(A), pasos) expandiendo por cofactores a lo largo de la fila 1.
    A: matriz cuadrada. pasos: lista de textos con el desarrollo."""
    n = validar_matriz_cuadrada(A, "determinante por cofactores")
    pasos: List[str] = []

    # Casos base de la recursión: se detiene en matrices 1x1 y 2x2.
    if n == 1:
        val = A[0][0]
        pasos.append(f"Matriz 1×1: det = A[1,1] = {val}")
        return val, pasos

    if n == 2:
        val = (A[0][0] * A[1][1]) - (A[0][1] * A[1][0])
        pasos.append(f"Fórmula 2×2: ({A[0][0]})·({A[1][1]}) - ({A[0][1]})·({A[1][0]}) = {val}")
        return val, pasos

    det_total = Fraction(0, 1)
    lineas_expansion = []
    for j in range(n):
        elem = A[0][j]
        # El signo (-1)^j sigue el patrón de cofactores: alterna según la posición de la columna.
        signo_num = 1 if (0 + j) % 2 == 0 else -1
        signo_str = "+" if signo_num == 1 else "-"
        sub = obtener_submatriz_menor(A, 0, j)
        det_sub, _ = determinante_cofactores(sub)
        cofac = Fraction(signo_num, 1) * det_sub
        termino = elem * cofac
        det_total += termino
        lineas_expansion.append(
            f"{signo_str} ({elem}) · det(M[1,{j+1}]) = {signo_str} ({elem}) · ({det_sub}) = {termino}"
        )

    pasos.append(f"Expansión por cofactores en la Fila 1 (orden {n}×{n}):")
    pasos.extend([f"  {linea}" for linea in lineas_expansion])
    pasos.append(f"Suma total de cofactores: det(A) = {det_total}")
    return det_total, pasos


def determinante_sarrus(A: MatrizF) -> Tuple[Fraction, List[str]]:
    """Devuelve (det(A), pasos) de una matriz 3x3 con la regla de Sarrus:
    det = suma de diagonales principales - suma de diagonales secundarias."""
    n = validar_matriz_cuadrada(A, "método de Sarrus")
    # Sarrus solo es válida para 3x3; en otros órdenes daría un valor incorrecto.
    if n != 3:
        raise ValueError(f"El método de Sarrus es exclusivo para matrices 3×3 (matriz dada es {n}×{n}).")

    D1 = A[0][0] * A[1][1] * A[2][2]
    D2 = A[0][1] * A[1][2] * A[2][0]
    D3 = A[0][2] * A[1][0] * A[2][1]
    suma_principales = D1 + D2 + D3

    d1 = A[0][2] * A[1][1] * A[2][0]
    d2 = A[0][0] * A[1][2] * A[2][1]
    d3 = A[0][1] * A[1][0] * A[2][2]
    suma_secundarias = d1 + d2 + d3

    det = suma_principales - suma_secundarias

    pasos = [
        "MÉTODO DE SARRUS (Matriz 3×3):",
        "1. Diagonales Principales (+):",
        f"   D₁ = ({A[0][0]})·({A[1][1]})·({A[2][2]}) = {D1}",
        f"   D₂ = ({A[0][1]})·({A[1][2]})·({A[2][0]}) = {D2}",
        f"   D₃ = ({A[0][2]})·({A[1][0]})·({A[2][1]}) = {D3}",
        f"   Suma Diagonales Principales = {suma_principales}",
        "2. Diagonales Secundarias (-):",
        f"   d₁ = ({A[0][2]})·({A[1][1]})·({A[2][0]}) = {d1}",
        f"   d₂ = ({A[0][0]})·({A[1][2]})·({A[2][1]}) = {d2}",
        f"   d₃ = ({A[0][1]})·({A[1][0]})·({A[2][2]}) = {d3}",
        f"   Suma Diagonales Secundarias = {suma_secundarias}",
        f"3. det(A) = ({suma_principales}) - ({suma_secundarias}) = {det}"
    ]
    return det, pasos


def determinante_triangulacion(A: MatrizF) -> Tuple[Fraction, List[str]]:
    """Devuelve (det(A), pasos) reduciendo A a triangular superior.
    det(A) = (-1)^(intercambios) · producto de la diagonal de la triangular."""
    n = validar_matriz_cuadrada(A, "determinante por triangulación")
    U = copiar_matriz(A)
    pasos: List[str] = [f"Reducción a matriz triangular superior (orden {n}×{n}):"]

    swaps = 0
    det_cero = False

    for col in range(n):
        # Se busca un pivote no nulo; si el de la diagonal es 0 se intercambian filas.
        pivote_fila = col
        while pivote_fila < n and U[pivote_fila][col] == Fraction(0, 1):
            pivote_fila += 1

        if pivote_fila == n:
            # Columna completa en ceros bajo la diagonal: det = 0
            det_cero = True
            pasos.append(f"Columna {col+1}: Todos los elementos bajo la diagonal son cero. La matriz es singular.")
            break

        if pivote_fila != col:
            # Cada intercambio cambia el signo de det(A): se cuenta para aplicar (-1)^swaps al final.
            U[col], U[pivote_fila] = U[pivote_fila], U[col]
            swaps += 1
            pasos.append(
                f"Operación elemental: Fila {col+1} ↔ Fila {pivote_fila+1} "
                "(Intercambio de filas: multiplica el determinante por -1)"
            )

        pivote = U[col][col]
        # Eliminar entradas inferiores mediante F_i → F_i - (U[i][col]/pivote)·F_col
        for f in range(col + 1, n):
            if U[f][col] != Fraction(0, 1):
                factor = U[f][col] / pivote
                for c in range(col, n):
                    U[f][c] = U[f][c] - factor * U[col][c]
                pasos.append(
                    f"Operación elemental: Fila {f+1} → Fila {f+1} - ({factor})·Fila {col+1} "
                    "(Reemplazo de fila: preserva el determinante exacto)"
                )

    if det_cero:
        det_final = Fraction(0, 1)
        pasos.append("Al haber una fila o columna nula, det(A) = 0.")
    else:
        producto_diagonal = Fraction(1, 1)
        terminos_diag = []
        for i in range(n):
            producto_diagonal *= U[i][i]
            terminos_diag.append(str(U[i][i]))

        signo_swaps = Fraction((-1) ** swaps, 1)
        det_final = signo_swaps * producto_diagonal
        pasos.append(f"\nMatriz triangular superior resultante U:")
        pasos.append(matriz_a_cadena(U))
        pasos.append(
            f"Fórmula: det(A) = (-1)^{swaps} · ({' · '.join(terminos_diag)}) = {det_final}"
        )

    return det_final, pasos


@dataclass
class ResultadoInversion:
    """Resultado de invertir una matriz: inversa (None si es singular), pasos y comprobación A·A⁻¹ = I."""
    es_invertible: bool
    matriz_inversa: Optional[MatrizF]
    pasos: List[str]
    comprobacion_identidad: bool
    matriz_producto_comprobacion: Optional[MatrizF]


def inversa_gauss_jordan(A: MatrizF) -> ResultadoInversion:
    """Devuelve la inversa de A reduciendo [A | I] a [I | A⁻¹] (ResultadoInversion).
    Si falta un pivote la matriz es singular y se detiene sin inversa."""
    n = validar_matriz_cuadrada(A, "inversa por Gauss-Jordan")
    pasos: List[str] = [f"Cálculo de A⁻¹ por Gauss-Jordan sobre matriz aumentada [A | I_{n}]:"]

    aumentada: MatrizF = []
    for i in range(n):
        fila = [A[i][j] for j in range(n)] + [Fraction(1 if i == j else 0, 1) for j in range(n)]
        aumentada.append(fila)

    def formato_aumentada(M: MatrizF) -> str:
        """Devuelve la matriz aumentada [A | I] como texto, con una barra entre ambos bloques."""
        lineas = []
        for f in M:
            izq = " ".join(f"{str(x):>8}" for x in f[:n])
            der = " ".join(f"{str(x):>8}" for x in f[n:])
            lineas.append(f"  [ {izq} | {der} ]")
        return "\n".join(lineas)

    pasos.append("Estado inicial de [A | I]:")
    pasos.append(formato_aumentada(aumentada))

    for col in range(n):
        pivote_fila = col
        while pivote_fila < n and aumentada[pivote_fila][col] == Fraction(0, 1):
            pivote_fila += 1

        # Sin n pivotes la matriz es singular: se detiene la reducción en lugar de dividir entre 0.
        if pivote_fila == n:
            pasos.append(
                f"\n❌ PROCESO DETENIDO: No se encontró pivote en la columna {col+1}.\n"
                f"La matriz tiene rango < {n}. Por el Teorema de la Matriz Invertible, "
                "la matriz es SINGULAR (no invertible)."
            )
            return ResultadoInversion(
                es_invertible=False,
                matriz_inversa=None,
                pasos=pasos,
                comprobacion_identidad=False,
                matriz_producto_comprobacion=None
            )

        if pivote_fila != col:
            # Se intercambian filas si el pivote es 0: sin pivote no se puede eliminar la columna.
            aumentada[col], aumentada[pivote_fila] = aumentada[pivote_fila], aumentada[col]
            pasos.append(f"Intercambio: Fila {col+1} ↔ Fila {pivote_fila+1}")

        # Normalizar el pivote a 1: F_col → (1 / pivote) · F_col
        pivote = aumentada[col][col]
        if pivote != Fraction(1, 1):
            factor_inv = Fraction(1, 1) / pivote
            aumentada[col] = [elem * factor_inv for elem in aumentada[col]]
            pasos.append(f"Normalizar pivote: Fila {col+1} → ({factor_inv}) · Fila {col+1}")

        for f in range(n):
            # Se anula la columna arriba y abajo del pivote (no solo debajo) para llegar a [I | A⁻¹].
            if f != col and aumentada[f][col] != Fraction(0, 1):
                factor = aumentada[f][col]
                aumentada[f] = [aumentada[f][c] - factor * aumentada[col][c] for c in range(2 * n)]
                pasos.append(f"Eliminar: Fila {f+1} → Fila {f+1} - ({factor}) · Fila {col+1}")

    pasos.append("\nForma reducida final alcanzada [I | A⁻¹]:")
    pasos.append(formato_aumentada(aumentada))

    A_inv: MatrizF = []
    for i in range(n):
        A_inv.append([aumentada[i][n + j] for j in range(n)])

    # Comprobación automática obligatoria: A · A⁻¹ = I
    # Se comprueba A·A⁻¹ = I para detectar cualquier error en la reducción.
    prod = multiplicar_matrices(A, A_inv)
    I = matriz_identidad(n)
    es_identidad = son_matrices_iguales(prod, I)

    pasos.append("\nCOMPROBACIÓN AUTOMÁTICA: A · A⁻¹ = I")
    pasos.append(matriz_a_cadena(prod))
    pasos.append(
        "✓ ÉXITO: El producto A · A⁻¹ es idéntico a la matriz identidad I."
        if es_identidad else "✗ FALLO: El producto no coincide con la identidad."
    )

    return ResultadoInversion(
        es_invertible=True,
        matriz_inversa=A_inv,
        pasos=pasos,
        comprobacion_identidad=es_identidad,
        matriz_producto_comprobacion=prod
    )


def inversa_adjunta(A: MatrizF) -> ResultadoInversion:
    """Devuelve la inversa de A como (1 / det(A)) · adj(A) (ResultadoInversion).
    Si det(A) = 0 la matriz es singular y no hay inversa."""
    n = validar_matriz_cuadrada(A, "inversa por matriz adjunta")
    pasos: List[str] = ["Cálculo de A⁻¹ mediante la Matriz Adjunta: A⁻¹ = (1 / det(A)) · adj(A)"]

    det, pasos_det = determinante_cofactores(A)
    pasos.append(f"1. Cálculo del determinante: det(A) = {det}")

    # Con det(A) = 0 la matriz es singular y la fórmula dividiría entre cero.
    if det == Fraction(0, 1):
        pasos.append(
            "❌ PROCESO DETENIDO: det(A) = 0. No se puede dividir entre cero.\n"
            "Por el Teorema Fundamental, la matriz es SINGULAR y carece de matriz inversa."
        )
        return ResultadoInversion(
            es_invertible=False,
            matriz_inversa=None,
            pasos=pasos,
            comprobacion_identidad=False,
            matriz_producto_comprobacion=None
        )

    C = matriz_cofactores(A)
    pasos.append("\n2. Matriz de Cofactores C:")
    pasos.append(matriz_a_cadena(C))

    adj_A = trasponer_matriz(C)
    pasos.append("\n3. Matriz Adjunta adj(A) = Cᵀ:")
    pasos.append(matriz_a_cadena(adj_A))

    factor_escalar = Fraction(1, 1) / det
    A_inv = multiplicar_escalar(factor_escalar, adj_A)
    pasos.append(f"\n4. A⁻¹ = (1 / {det}) · adj(A):")
    pasos.append(matriz_a_cadena(A_inv))

    # Se comprueba A·A⁻¹ = I para detectar cualquier error en la fórmula.
    prod = multiplicar_matrices(A, A_inv)
    I = matriz_identidad(n)
    es_identidad = son_matrices_iguales(prod, I)

    pasos.append("\nCOMPROBACIÓN AUTOMÁTICA: A · A⁻¹ = I")
    pasos.append(matriz_a_cadena(prod))
    pasos.append(
        "✓ ÉXITO: El producto A · A⁻¹ es idéntico a la matriz identidad I."
        if es_identidad else "✗ FALLO: El producto no coincide con la identidad."
    )

    return ResultadoInversion(
        es_invertible=True,
        matriz_inversa=A_inv,
        pasos=pasos,
        comprobacion_identidad=es_identidad,
        matriz_producto_comprobacion=prod
    )


@dataclass
class ResultadoPropiedad:
    """Resultado de verificar una propiedad: fórmula, ambos lados como texto y si se cumple."""
    nombre: str
    formula: str
    se_cumple: bool
    lado_izquierdo_str: str
    lado_derecho_str: str
    explicacion: str


def verificar_propiedad_inversa_de_inversa(A: MatrizF) -> ResultadoPropiedad:
    """Verifica (A⁻¹)⁻¹ = A; devuelve un ResultadoPropiedad."""
    res1 = inversa_gauss_jordan(A)
    if not res1.es_invertible or res1.matriz_inversa is None:
        return ResultadoPropiedad(
            nombre="Inversa de la inversa",
            formula="(A⁻¹)⁻¹ = A",
            se_cumple=False,
            lado_izquierdo_str="No definida",
            lado_derecho_str=matriz_a_cadena(A),
            explicacion="La matriz A no es invertible."
        )
    A_inv = res1.matriz_inversa
    res2 = inversa_gauss_jordan(A_inv)
    inv_inv = res2.matriz_inversa
    se_cumple = (inv_inv is not None) and son_matrices_iguales(inv_inv, A)
    return ResultadoPropiedad(
        nombre="Inversa de la inversa",
        formula="(A⁻¹)⁻¹ = A",
        se_cumple=se_cumple,
        lado_izquierdo_str=matriz_a_cadena(inv_inv) if inv_inv else "Error",
        lado_derecho_str=matriz_a_cadena(A),
        explicacion="Invertir dos veces una matriz regresa a la matriz original A."
    )


def verificar_propiedad_inversa_del_producto(A: MatrizF, B: MatrizF) -> ResultadoPropiedad:
    """Verifica (AB)⁻¹ = B⁻¹·A⁻¹ para A y B cuadradas del mismo orden; devuelve un ResultadoPropiedad."""
    # AB solo existe e invierte bien si A y B son cuadradas del mismo orden.
    validar_mismas_dimensiones(A, B, "verificación (AB)⁻¹ = B⁻¹A⁻¹")
    validar_matriz_cuadrada(A, "verificación")

    AB = multiplicar_matrices(A, B)
    res_AB = inversa_gauss_jordan(AB)
    lado_izq = res_AB.matriz_inversa

    res_B = inversa_gauss_jordan(B)
    res_A = inversa_gauss_jordan(A)

    if not res_AB.es_invertible or not res_B.es_invertible or not res_A.es_invertible:
        return ResultadoPropiedad(
            nombre="Inversa del producto matricial",
            formula="(AB)⁻¹ = B⁻¹ · A⁻¹",
            se_cumple=False,
            lado_izquierdo_str="No definida",
            lado_derecho_str="No definida",
            explicacion="Al menos una de las matrices A, B o AB es singular."
        )

    B_inv = res_B.matriz_inversa
    A_inv = res_A.matriz_inversa
    assert B_inv is not None and A_inv is not None and lado_izq is not None
    lado_der = multiplicar_matrices(B_inv, A_inv)

    se_cumple = son_matrices_iguales(lado_izq, lado_der)
    return ResultadoPropiedad(
        nombre="Inversa del producto matricial (Orden revertido)",
        formula="(AB)⁻¹ = B⁻¹ · A⁻¹",
        se_cumple=se_cumple,
        lado_izquierdo_str=matriz_a_cadena(lado_izq),
        lado_derecho_str=matriz_a_cadena(lado_der),
        explicacion="La inversa del producto invierte el orden algebraico de los factores."
    )


def verificar_propiedad_inversa_de_traspuesta(A: MatrizF) -> ResultadoPropiedad:
    """Verifica (Aᵀ)⁻¹ = (A⁻¹)ᵀ; devuelve un ResultadoPropiedad."""
    validar_matriz_cuadrada(A, "verificación")
    AT = trasponer_matriz(A)
    res_AT = inversa_gauss_jordan(AT)
    lado_izq = res_AT.matriz_inversa

    res_A = inversa_gauss_jordan(A)
    if not res_A.es_invertible or not res_AT.es_invertible or lado_izq is None or res_A.matriz_inversa is None:
        return ResultadoPropiedad(
            nombre="Inversa de la traspuesta",
            formula="(Aᵀ)⁻¹ = (A⁻¹)ᵀ",
            se_cumple=False,
            lado_izquierdo_str="No definida",
            lado_derecho_str="No definida",
            explicacion="La matriz A no es invertible."
        )

    lado_der = trasponer_matriz(res_A.matriz_inversa)
    se_cumple = son_matrices_iguales(lado_izq, lado_der)
    return ResultadoPropiedad(
        nombre="Inversa de la traspuesta",
        formula="(Aᵀ)⁻¹ = (A⁻¹)ᵀ",
        se_cumple=se_cumple,
        lado_izquierdo_str=matriz_a_cadena(lado_izq),
        lado_derecho_str=matriz_a_cadena(lado_der),
        explicacion="La transposición conmuta con la operación de inversión matricial."
    )


def verificar_propiedad_determinante_de_inversa(A: MatrizF) -> ResultadoPropiedad:
    """Verifica det(A⁻¹) = 1 / det(A); devuelve un ResultadoPropiedad."""
    validar_matriz_cuadrada(A, "verificación")
    det_A, _ = determinante_cofactores(A)
    if det_A == Fraction(0, 1):
        return ResultadoPropiedad(
            nombre="Determinante de la inversa",
            formula="det(A⁻¹) = 1 / det(A)",
            se_cumple=False,
            lado_izquierdo_str="No definido",
            lado_derecho_str="División por cero",
            explicacion="La matriz es singular (det = 0)."
        )

    res_A = inversa_gauss_jordan(A)
    assert res_A.matriz_inversa is not None
    det_A_inv, _ = determinante_cofactores(res_A.matriz_inversa)
    reciproco = Fraction(1, 1) / det_A
    se_cumple = (det_A_inv == reciproco)

    return ResultadoPropiedad(
        nombre="Determinante de la inversa",
        formula="det(A⁻¹) = 1 / det(A)",
        se_cumple=se_cumple,
        lado_izquierdo_str=f"det(A⁻¹) = {det_A_inv}",
        lado_derecho_str=f"1 / det(A) = 1 / ({det_A}) = {reciproco}",
        explicacion="El determinante de la inversa es el inverso multiplicativo de det(A)."
    )


def verificar_propiedades_operaciones_fila_det(A: MatrizF) -> List[ResultadoPropiedad]:
    """Verifica cómo afectan al det(A) el intercambio, el reemplazo y el escalamiento de una fila.
    Devuelve una lista de ResultadoPropiedad (vacía si A es 1x1)."""
    n = validar_matriz_cuadrada(A, "verificación operaciones de fila")
    # Con una sola fila no hay otra fila con la cual intercambiar o combinar.
    if n < 2:
        return []

    det_orig, _ = determinante_cofactores(A)
    resultados = []

    # 1. Intercambio de fila: F₁ ↔ F₂ → det(A') = -det(A)
    A_swap = copiar_matriz(A)
    A_swap[0], A_swap[1] = A_swap[1], A_swap[0]
    det_swap, _ = determinante_cofactores(A_swap)
    resultados.append(ResultadoPropiedad(
        nombre="Efecto de intercambio de filas en det",
        formula="det(F₁ ↔ F₂) = -det(A)",
        se_cumple=(det_swap == -det_orig),
        lado_izquierdo_str=f"det(A_swap) = {det_swap}",
        lado_derecho_str=f"-det(A) = {-det_orig}",
        explicacion="Intercambiar dos filas invierte el signo del determinante."
    ))

    # 2. Reemplazo de fila: F₁ → F₁ + 2·F₂ → det(A') = det(A)
    k_factor = Fraction(2, 1)
    A_reemp = copiar_matriz(A)
    A_reemp[0] = [A_reemp[0][c] + k_factor * A_reemp[1][c] for c in range(n)]
    det_reemp, _ = determinante_cofactores(A_reemp)
    resultados.append(ResultadoPropiedad(
        nombre="Efecto de reemplazo de fila en det",
        formula=f"det(F₁ → F₁ + {k_factor}·F₂) = det(A)",
        se_cumple=(det_reemp == det_orig),
        lado_izquierdo_str=f"det(A_reemp) = {det_reemp}",
        lado_derecho_str=f"det(A) = {det_orig}",
        explicacion="Sumar a una fila un múltiplo escalar de otra preserva el determinante."
    ))

    # 3. Escalamiento de fila: F₁ → k·F₁ → det(A') = k · det(A)
    c_factor = Fraction(3, 1)
    A_esc = copiar_matriz(A)
    A_esc[0] = [c_factor * elem for elem in A_esc[0]]
    det_esc, _ = determinante_cofactores(A_esc)
    esperado_esc = c_factor * det_orig
    resultados.append(ResultadoPropiedad(
        nombre="Efecto de escalamiento de fila en det",
        formula=f"det(F₁ → {c_factor}·F₁) = {c_factor} · det(A)",
        se_cumple=(det_esc == esperado_esc),
        lado_izquierdo_str=f"det(A_esc) = {det_esc}",
        lado_derecho_str=f"{c_factor} · det(A) = {esperado_esc}",
        explicacion="Multiplicar una fila por un escalar c multiplica el determinante por c."
    ))

    return resultados


def verificar_propiedad_matriz_triangular(A: MatrizF) -> ResultadoPropiedad:
    """Verifica que el det de la triangular superior de A sea el producto de su diagonal.
    Devuelve un ResultadoPropiedad."""
    n = validar_matriz_cuadrada(A, "matriz triangular")
    T = [[A[i][j] if j >= i else Fraction(0, 1) for j in range(n)] for i in range(n)]

    prod_diag = Fraction(1, 1)
    terminos = []
    for i in range(n):
        prod_diag *= T[i][i]
        terminos.append(str(T[i][i]))

    # Se compara contra cofactores, que no usan el atajo de la diagonal.
    det_cofac, _ = determinante_cofactores(T)

    se_cumple = (prod_diag == det_cofac)
    return ResultadoPropiedad(
        nombre="Determinante de Matriz Triangular",
        formula="det(T) = ∏ t_{ii} (Producto de la diagonal principal)",
        se_cumple=se_cumple,
        lado_izquierdo_str=f"Producto diagonal = {' · '.join(terminos)} = {prod_diag}",
        lado_derecho_str=f"det por cofactores = {det_cofac}",
        explicacion=(
            f"Matriz triangular:\n{matriz_a_cadena(T)}\n"
            "El determinante de una matriz triangular es exactamente el producto de las entradas en su diagonal principal."
        )
    )


LOGO_ASCII_MODULO_3 = r"""
  ██████╗ ██╗   ██╗███╗   ███╗ █████╗ ████████╗██████╗ ██╗██╗  ██╗
  ██╔══██╗╚██╗ ██╔╝████╗ ████║██╔══██╗╚══██╔══╝██╔══██╗██║╚██╗██╔╝
  ██████╔╝ ╚████╔╝ ██╔████╔██║███████║   ██║   ██████╔╝██║ ╚███╔╝ 
  ██╔═══╝   ╚██╔╝  ██║╚██╔╝██║██╔══██║   ██║   ██╔══██╗██║ ██╔██╗ 
  ██║        ██║   ██║ ╚═╝ ██║██║  ██║   ██║   ██║  ██║██║██╔╝ ██╗
  ╚═╝        ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
       >>> MÓDULO 3: ÁLGEBRA MATRICIAL, DETERMINANTES E INVERSAS <<<
"""

TEOREMAS_MODULO_3 = """
========================================================================================
                      📘 TEOREMAS FUNDAMENTALES DEL MÓDULO 3
========================================================================================

1. TEOREMA DE LA MATRIZ INVERSA (Partes a, b, c):
   Sean A y B matrices invertibles de n × n:
   a) Si A es invertible, entonces A⁻¹ es invertible y:
          (A⁻¹)⁻¹ = A
   b) Si A y B son ambas invertibles, su producto AB es invertible y:
          (AB)⁻¹ = B⁻¹ · A⁻¹
      (Nota: El orden de multiplicación se invierte).
   c) Si A es invertible, su traspuesta Aᵀ es invertible y:
          (Aᵀ)⁻¹ = (A⁻¹)ᵀ

2. TEOREMA DE LA MATRIZ INVERTIBLE (TMI):
   Para una matriz cuadrada A de orden n × n, las siguientes proposiciones son
   lógicamente equivalentes (todas son ciertas o todas son falsas simultáneamente):
   [a] A es una matriz invertible.
   [c] A tiene n posiciones pivote (rango(A) = n).
   [e] Las columnas de A forman un conjunto LINEALMENTE INDEPENDIENTE (L.I.).
   [h] Las columnas de A GENERAN el espacio vectorial ℝⁿ (Gen{col(A)} = ℝⁿ).
   [j] Existe una matriz C de n × n tal que C · A = Iₙ.
   [k] Existe una matriz D de n × n tal que A · D = Iₙ.

3. RELACIÓN ENTRE INVERTIBILIDAD Y DETERMINANTE:
   - Una matriz cuadrada A de n × n es INVERTIBLE si y solo si:
          det(A) ≠ 0
   - Si det(A) = 0, la matriz es SINGULAR (no invertible), sus columnas son L.D.,
     su rango es estrictamente menor a n y el sistema homogéneo A x = 0 posee soluciones
     no triviales (infinitas soluciones).

4. TEOREMA DE LA MATRIZ ADJUNTA:
   Para toda matriz cuadrada invertible A de n × n:
          A · adj(A) = det(A) · Iₙ
   De donde se deduce la fórmula de inversión por cofactores:
          A⁻¹ = (1 / det(A)) · adj(A)
   donde adj(A) = Cᵀ es la matriz transpuesta de los cofactores algebraicos.
========================================================================================
"""


def analizar_suma_matrices(A: MatrizF, B: MatrizF, C: MatrizF) -> List[str]:
    """Devuelve las líneas de texto con el análisis de A + B = C (conmutatividad y estructura)."""
    m, n = len(A), len(A[0])
    lineas = [
        "═" * 70,
        "📊 ANÁLISIS DETALLADO DEL EJERCICIO (SUMA MATRICIAL A + B):",
        "═" * 70,
        f"1. Compatibilidad Espacial: A, B ∈ M_{m}×{n}(ℚ).",
        f"   Ambas matrices comparten orden idéntico ({m} filas y {n} columnas).",
        "   La operación es cerrada en el espacio vectorial M_{m×n}(ℝ)."
    ]
    B_mas_A = sumar_matrices(B, A)
    conmuta = son_matrices_iguales(C, B_mas_A)
    lineas.append(f"2. Verificación de Conmutatividad: A + B == B + A → {'✓ Verificada' if conmuta else '✗ No'} (conmutativa).")

    ceros = sum(1 for i in range(m) for j in range(n) if C[i][j] == Fraction(0, 1))
    lineas.append(f"3. Análisis de Entradas Resultantes: Total de {m*n} celdas calculadas.")
    if ceros > 0:
        lineas.append(f"   • Se detectaron {ceros} posición(es) nula(s) donde A[i,j] y B[i,j] eran opuestos aditivos (A_ij = -B_ij).")
    else:
        lineas.append("   • Ningún elemento resultó en cero (no hubo parejas de opuestos aditivos exactos).")

    if m == n:
        es_sim = son_matrices_iguales(C, trasponer_matriz(C))
        es_diag = all(C[i][j] == Fraction(0, 1) for i in range(m) for j in range(n) if i != j)
        lineas.append(f"4. Clasificación Estructural (Matriz Cuadrada {m}×{n}):")
        lineas.append(f"   • ¿Es Simétrica (C = Cᵀ)?: {'Sí (C[i,j] = C[j,i])' if es_sim else 'No'}.")
        if es_diag:
            lineas.append("   • Estructura especial: Es una matriz DIAGONAL (todas las entradas fuera de la diagonal son 0).")
    else:
        lineas.append(f"4. Clasificación Estructural: Matriz rectangular de dimensión {m}×{n}.")

    lineas.append("═" * 70)
    return lineas


def analizar_resta_matrices(A: MatrizF, B: MatrizF, C: MatrizF) -> List[str]:
    """Devuelve las líneas de texto con el análisis de A - B = C (no conmutatividad y comparación)."""
    m, n = len(A), len(A[0])
    lineas = [
        "═" * 70,
        "📊 ANÁLISIS DETALLADO DEL EJERCICIO (RESTA MATRICIAL A - B):",
        "═" * 70,
        f"1. Compatibilidad Espacial: A, B ∈ M_{m}×{n}(ℚ).",
        "   Definida como la adición con el opuesto aditivo: A - B = A + (-1)·B."
    ]
    B_menos_A = restar_matrices(B, A)
    es_igual_inverso = son_matrices_iguales(C, B_menos_A)
    opuesto = multiplicar_escalar(Fraction(-1, 1), B_menos_A)
    es_antisimetrico = son_matrices_iguales(C, opuesto)
    lineas.append("2. Demostración de No Conmutatividad en este Ejercicio:")
    lineas.append(f"   • ¿A - B == B - A?: {'Sí (caso trivial A=B)' if es_igual_inverso else 'NO (la sustracción no es conmutativa)'}.")
    lineas.append(f"   • Relación Antisimétrica: A - B == -(B - A) → {'✓ Verificada idénticamente' if es_antisimetrico else '✗ Discrepancia'}.")

    mayores = sum(1 for i in range(m) for j in range(n) if A[i][j] > B[i][j])
    menores = sum(1 for i in range(m) for j in range(n) if A[i][j] < B[i][j])
    iguales = sum(1 for i in range(m) for j in range(n) if A[i][j] == B[i][j])
    lineas.append(f"3. Comparación de Magnitudes (A vs B):")
    lineas.append(f"   • En {mayores} celda(s) A[i,j] > B[i,j] (resultado positivo en C).")
    lineas.append(f"   • En {menores} celda(s) A[i,j] < B[i,j] (resultado negativo en C).")
    if iguales > 0:
        lineas.append(f"   • En {iguales} celda(s) A[i,j] == B[i,j] (entradas idénticas que se anularon produciendo cero).")
    lineas.append("═" * 70)
    return lineas


def analizar_escalar_matriz(c: Fraction, A: MatrizF, R: MatrizF) -> List[str]:
    """Devuelve las líneas de texto con el análisis de c·A = R (efecto del escalar y del det)."""
    m, n = len(A), len(A[0])
    lineas = [
        "═" * 70,
        f"📊 ANÁLISIS DETALLADO DEL EJERCICIO (ESCALAMIENTO {c} · A):",
        "═" * 70,
        f"1. Naturaleza y Efecto del Factor Escalar (c = {c}):"
    ]
    if c == Fraction(0, 1):
        lineas.append("   • Escalar Nulo (c = 0): Actúa como elemento absorbente, colapsando la matriz completa a la MATRIZ NULA.")
    elif c > Fraction(0, 1):
        lineas.append("   • Escalar Positivo (c > 0): Preserva estrictamente el signo de todas las entradas originales.")
    else:
        lineas.append("   • Escalar Negativo (c < 0): Invierte el signo de cada una de las entradas de A (reflexión geométrica).")

    if abs(c) > Fraction(1, 1):
        lineas.append(f"   • Dilatación / Amplificación: Las magnitudes aumentaron por un factor de {abs(c)}.")
    elif Fraction(0, 1) < abs(c) < Fraction(1, 1):
        lineas.append(f"   • Contracción / Atenuación: Las magnitudes se redujeron por un factor de {abs(c)}.")
    elif abs(c) == Fraction(1, 1):
        lineas.append("   • Isometría Escalar (|c| = 1): Las magnitudes absolutas permanecen inalteradas.")

    if m == n:
        # Cada una de las m filas se multiplica por c y cada una aporta un factor c al determinante.
        factor_det = c ** m
        lineas.append(f"2. Efecto Teórico en el Determinante (Orden Cuadrado {m}×{n}):")
        lineas.append(f"   • Teorema: det(c · A) = c^{m} · det(A) = ({c})^{m} · det(A) = {factor_det} · det(A).")
        lineas.append(f"   • El 'hipervolumen' transformado se escala por un factor de {factor_det}.")
    else:
        lineas.append(f"2. Dimensión Preservada: La matriz permanece en M_{m}×{n}(ℚ).")

    lineas.append("═" * 70)
    return lineas


def analizar_producto_matricial(A: MatrizF, B: MatrizF, C: MatrizF) -> List[str]:
    """Devuelve las líneas de texto con el análisis de A·B = C (dimensiones y conmutatividad)."""
    m = len(A)
    nA = len(A[0])
    nB = len(B)
    p = len(B[0])

    lineas = [
        "═" * 70,
        "📊 ANÁLISIS DETALLADO DEL EJERCICIO (PRODUCTO MATRICIAL A × B):",
        "═" * 70,
        f"1. Análisis Dimensional y Complejidad Aritmética:",
        f"   • Transformación: ({m} × {nA}) × ({nB} × {p}) ⟶ ({m} × {p}).",
        f"   • La dimensión interna ({nA}) se contrajo mediante suma acumulada de productos.",
        f"   • Total de operaciones elementales ejecutadas: {m * p * nA} multiplicaciones y {m * p * (nA - 1)} sumas."
    ]

    lineas.append("2. Análisis de Conmutatividad (¿Existe y es igual B × A?):")
    # B·A solo existe si las columnas de B (p) igualan las filas de A (m).
    if p != m:
        lineas.append(f"   • B × A NO EXISTE (No está definido): B tiene {p} columnas y A tiene {m} filas ({p} ≠ {m}).")
        lineas.append("   • Esto prueba contundentemente la no conmutatividad estricta de las matrices en este ejercicio.")
    else:
        BA = multiplicar_matrices(B, A)
        if len(BA) != m or len(BA[0]) != p:
            lineas.append(f"   • B × A existe pero tiene tamaño ({p}×{nA}), diferente al tamaño de A × B ({m}×{p}).")
            lineas.append("   • Por tanto, AB ≠ BA debido a dimensiones de salida disjuntas.")
        else:
            conmutan = son_matrices_iguales(C, BA)
            lineas.append(f"   • B × A tiene las mismas dimensiones ({m}×{p}).")
            lineas.append(f"   • ¿AB == BA en este ejercicio?: {'¡Sí conmutan!' if conmutan else 'NO CONMUTAN (AB ≠ BA, caso general)'}.")

    lineas.append("3. Interpretación Estructural:")
    lineas.append("   • Cada fila i de la matriz resultante C es una combinación lineal de las filas de B.")
    lineas.append("   • Cada columna j de la matriz resultante C es una combinación lineal de las columnas de A.")
    lineas.append("═" * 70)
    return lineas


def analizar_transposicion_matriz(A: MatrizF, AT: MatrizF) -> List[str]:
    """Devuelve las líneas de texto con el análisis de Aᵀ (diagonal, simetría e involución)."""
    m, n = len(A), len(A[0])
    lineas = [
        "═" * 70,
        "📊 ANÁLISIS DETALLADO DEL EJERCICIO (TRANSPOSICIÓN Aᵀ):",
        "═" * 70,
        f"1. Mapeo Índices y Dimensión: M_{m}×{n} ⟶ M_{n}×{m}.",
        "   La operación refleja las entradas respecto a la diagonal principal: (Aᵀ)[j,i] = A[i,j]."
    ]

    min_dim = min(m, n)
    diag_fijos = [f"A[{i+1},{i+1}] = {A[i][i]}" for i in range(min_dim)]
    lineas.append(f"2. Elementos Invariantes (Diagonal Principal):")
    lineas.append(f"   • Los elementos sobre la diagonal principal permanecen en sus posiciones: {', '.join(diag_fijos)}.")

    if m == n:
        es_sim = son_matrices_iguales(A, AT)
        A_neg = multiplicar_escalar(Fraction(-1, 1), A)
        es_antisin = son_matrices_iguales(AT, A_neg)
        lineas.append(f"3. Clasificación de Simetría (Matriz Cuadrada {m}×{n}):")
        if es_sim:
            lineas.append("   • ¡LA MATRIZ ES SIMÉTRICA! Satisface idénticamente A = Aᵀ.")
        elif es_antisin:
            lineas.append("   • ¡LA MATRIZ ES ANTISIMÉTRICA! Satisface idénticamente Aᵀ = -A.")
        else:
            lineas.append("   • La matriz no es simétrica ni antisimétrica (caso general).")
    else:
        lineas.append("3. Clasificación: Al ser rectangular (m ≠ n), la matriz nunca puede ser simétrica.")

    ATT = trasponer_matriz(AT)
    lineas.append(f"4. Teorema Involutivo: (Aᵀ)ᵀ = A → {'✓ Verificado rigurosamente' if son_matrices_iguales(ATT, A) else '✗ Error'}.")
    lineas.append("═" * 70)
    return lineas
