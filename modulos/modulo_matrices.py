"""Módulo III: Operaciones matriciales, determinantes, matriz inversa y propiedades algebraicas.
Tema de clase: álgebra matricial, determinantes e inversas (Sesiones 9 a 11).
Las funciones de cálculo no usan input() ni print(); devuelven datos y validan precondiciones.
Elaborado por: Grupo x"""

from fractions import Fraction
from typing import List, Tuple, Optional, Any, Dict


Matriz = List[List[Any]]


def validar_dimensiones_iguales(A: Matriz, B: Matriz, operacion: str = "operación") -> Tuple[int, int]:
    """Comprueba que A y B tengan las mismas dimensiones m x n y devuelve (m, n).
    Lanza ValueError si alguna está vacía o si sus dimensiones difieren."""
    if not A or not A[0] or not B or not B[0]:
        raise ValueError("Las matrices no pueden estar vacías.")
    m_A, n_A = len(A), len(A[0])
    m_B, n_B = len(B), len(B[0])
    # Suma y resta operan elemento a elemento: requieren idénticas dimensiones.
    if m_A != m_B or n_A != n_B:
        raise ValueError(
            f"Dimensiones incompatibles para {operacion}: A es {m_A}×{n_A} y B es {m_B}×{n_B}."
        )
    return m_A, n_A


def validar_dimensiones_producto(A: Matriz, B: Matriz) -> Tuple[int, int, int]:
    """Comprueba compatibilidad para A·B y devuelve (m, n, p).
    Lanza ValueError si columnas de A no coinciden con filas de B."""
    if not A or not A[0] or not B or not B[0]:
        raise ValueError("Las matrices no pueden estar vacías.")
    m, n_A = len(A), len(A[0])
    n_B, p = len(B), len(B[0])
    # Producto fila por columna: cada fila de A debe tener tantos elementos como cada columna de B.
    if n_A != n_B:
        raise ValueError(
            f"Incompatibilidad de dimensiones para producto: columnas de A ({n_A}) ≠ filas de B ({n_B})."
        )
    return m, n_A, p


def validar_matriz_cuadrada(A: Matriz, operacion: str = "operación") -> int:
    """Comprueba que A sea de orden n x n y devuelve n.
    Lanza ValueError si A no es cuadrada o si alguna fila tiene longitud desigual."""
    if not A or not A[0]:
        raise ValueError("La matriz no puede estar vacía.")
    n = len(A)
    for i, fila in enumerate(A):
        # Determinantes e inversas solo existen para matrices cuadradas.
        if len(fila) != n:
            raise ValueError(
                f"La matriz no es cuadrada para {operacion}: fila {i+1} tiene {len(fila)} columnas y A tiene {n} filas."
            )
    return n


def sumar_matrices(A: Matriz, B: Matriz) -> Matriz:
    """Devuelve C = A + B de dimensión m x p.
    Valida dimensiones compatibles antes de operar."""
    m, n = validar_dimensiones_iguales(A, B, "suma")
    return [[A[i][j] + B[i][j] for j in range(n)] for i in range(m)]


def restar_matrices(A: Matriz, B: Matriz) -> Matriz:
    """Devuelve C = A - B de dimensión m x p.
    Valida dimensiones compatibles antes de operar."""
    m, n = validar_dimensiones_iguales(A, B, "resta")
    return [[A[i][j] - B[i][j] for j in range(n)] for i in range(m)]


def multiplicar_escalar(escalar: Any, A: Matriz) -> Matriz:
    """Devuelve C = c·A multiplicando cada elemento de A por el escalar c.
    A: matriz m x n. escalar: número real o fracción."""
    if not A or not A[0]:
        raise ValueError("La matriz no puede estar vacía.")
    return [[escalar * A[i][j] for j in range(len(A[0]))] for i in range(len(A))]


def producto_matricial(A: Matriz, B: Matriz) -> Matriz:
    """Devuelve A·B (matriz m x p). Requiere columnas de A == filas de B,
    condición que se valida antes de llamar a esta función.
    A: m filas de n elementos. B: n filas de p elementos."""
    m, n, p = validar_dimensiones_producto(A, B)
    resultado = []
    for i in range(m):
        fila = []
        for j in range(p):
            # Elemento (i, j) = fila i de A por columna j de B
            fila.append(sum(A[i][k] * B[k][j] for k in range(n)))
        resultado.append(fila)
    return resultado


def trasponer_matriz(A: Matriz) -> Matriz:
    """Devuelve Aᵀ (matriz n x m) intercambiando filas por columnas.
    A: matriz de m filas y n columnas."""
    if not A or not A[0]:
        raise ValueError("La matriz no puede estar vacía.")
    m, n = len(A), len(A[0])
    return [[A[i][j] for i in range(m)] for j in range(n)]


def obtener_submatriz_menor(A: Matriz, fila_elim: int, col_elim: int) -> Matriz:
    """Devuelve el menor M_ij eliminando la fila fila_elim y columna col_elim.
    Recibe matriz n x n y los índices (base 0) a eliminar."""
    return [
        [A[i][j] for j in range(len(A[0])) if j != col_elim]
        for i in range(len(A)) if i != fila_elim
    ]


def determinante(A: Matriz) -> Any:
    """Calcula det(A) mediante expansión recursiva por cofactores en la fila 1.
    Requiere que A sea cuadrada; devuelve el valor escalar del determinante."""
    n = validar_matriz_cuadrada(A, "determinante")
    if n == 1:
        return A[0][0]
    if n == 2:
        return (A[0][0] * A[1][1]) - (A[0][1] * A[1][0])

    det_total = Fraction(0, 1) if isinstance(A[0][0], Fraction) else 0
    for j in range(n):
        submatriz = obtener_submatriz_menor(A, 0, j)
        # El signo (-1)**j sigue el patrón de cofactores: alterna según la posición de la columna.
        signo = 1 if j % 2 == 0 else -1
        det_total += signo * A[0][j] * determinante(submatriz)
    return det_total


def matriz_cofactores(A: Matriz) -> Matriz:
    """Devuelve la matriz de cofactores C de una matriz cuadrada A.
    Cada elemento es C_ij = (-1)^(i+j) · det(M_ij)."""
    n = validar_matriz_cuadrada(A, "matriz de cofactores")
    if n == 1:
        return [[1]]
    C = []
    for i in range(n):
        fila = []
        for j in range(n):
            submatriz = obtener_submatriz_menor(A, i, j)
            # El signo (-1)**(i+j) alterna signos según fila y columna del cofactor.
            signo = 1 if (i + j) % 2 == 0 else -1
            fila.append(signo * determinante(submatriz))
        C.append(fila)
    return C


def matriz_adjunta(A: Matriz) -> Matriz:
    """Devuelve adj(A) = Cᵀ, la traspuesta de la matriz de cofactores de A.
    A: matriz cuadrada de orden n x n."""
    return trasponer_matriz(matriz_cofactores(A))


def inversa_adjunta(A: Matriz) -> Matriz:
    """Calcula A⁻¹ mediante la fórmula A⁻¹ = (1/det(A)) · adj(A).
    Valida matriz cuadrada y determinante distinto de cero antes de operar."""
    n = validar_matriz_cuadrada(A, "inversa por adjunta")
    det_A = determinante(A)
    # Sin determinante no nulo la matriz es singular y no posee inversa.
    if det_A == 0:
        raise ValueError("La matriz es singular (det = 0): no tiene inversa.")
    adj = matriz_adjunta(A)
    factor = Fraction(1, det_A) if isinstance(det_A, (int, Fraction)) else (1.0 / det_A)
    return multiplicar_escalar(factor, adj)


def inversa_gauss_jordan(A: Matriz) -> Matriz:
    """Calcula A⁻¹ aplicando reducción de Gauss-Jordan sobre [A | I].
    Devuelve la matriz inversa o lanza ValueError si la matriz es singular."""
    n = validar_matriz_cuadrada(A, "inversa por Gauss-Jordan")
    # Construir matriz aumentada [A | I]
    aumentada = []
    for i in range(n):
        fila = [Fraction(A[i][j]) for j in range(n)] + [Fraction(1 if i == j else 0) for j in range(n)]
        aumentada.append(fila)

    for col in range(n):
        # Se intercambian filas si el pivote es 0: sin pivote no se puede eliminar la columna.
        fila_pivote = col
        while fila_pivote < n and aumentada[fila_pivote][col] == 0:
            fila_pivote += 1

        # Sin n pivotes la matriz es singular: se detiene la reducción en lugar de dividir entre 0.
        if fila_pivote == n:
            raise ValueError(f"La matriz es singular: no se encontró pivote en la columna {col + 1}.")

        if fila_pivote != col:
            aumentada[col], aumentada[fila_pivote] = aumentada[fila_pivote], aumentada[col]

        pivote = aumentada[col][col]
        # Normalizar fila pivote para obtener un 1 principal.
        aumentada[col] = [elem / pivote for elem in aumentada[col]]

        # Eliminar entradas en la columna sobre y bajo el pivote actual.
        for fila_idx in range(n):
            if fila_idx != col and aumentada[fila_idx][col] != 0:
                factor = aumentada[fila_idx][col]
                aumentada[fila_idx] = [
                    aumentada[fila_idx][c] - factor * aumentada[col][c]
                    for c in range(2 * n)
                ]

    # Extraer el bloque derecho correspondiente a A⁻¹
    return [[aumentada[i][n + j] for j in range(n)] for i in range(n)]


def verificar_propiedades(A: Matriz, B: Optional[Matriz] = None) -> Dict[str, bool]:
    """Comprueba computacionalmente las propiedades algebraicas de inversas y determinantes.
    Devuelve un diccionario con el estado de cumplimiento de cada propiedad."""
    n = validar_matriz_cuadrada(A, "verificación de propiedades")
    det_A = determinante(A)
    if det_A == 0:
        raise ValueError("Para verificar propiedades de inversas, A debe ser invertible (det ≠ 0).")

    inv_A = inversa_gauss_jordan(A)
    resultados = {}

    # 1. (A^-1)^-1 = A
    inv_inv_A = inversa_gauss_jordan(inv_A)
    resultados["(A^-1)^-1 = A"] = all(
        inv_inv_A[i][j] == A[i][j] for i in range(n) for j in range(n)
    )

    # 2. (A^T)^-1 = (A^-1)^T
    inv_tras_A = inversa_gauss_jordan(trasponer_matriz(A))
    tras_inv_A = trasponer_matriz(inv_A)
    resultados["(A^T)^-1 = (A^-1)^T"] = all(
        inv_tras_A[i][j] == tras_inv_A[i][j] for i in range(n) for j in range(n)
    )

    # 3. det(A^-1) = 1 / det(A)
    det_inv = determinante(inv_A)
    resultados["det(A^-1) = 1/det(A)"] = (det_inv == Fraction(1, det_A))

    # 4. (AB)^-1 = B^-1 A^-1 (si se proporciona B o se usa matriz auxiliar)
    if B is None:
        B = [[Fraction(1 if i == j else 2) for j in range(n)] for i in range(n)]
    if determinante(B) != 0:
        inv_B = inversa_gauss_jordan(B)
        inv_AB = inversa_gauss_jordan(producto_matricial(A, B))
        prod_inv = producto_matricial(inv_B, inv_A)
        resultados["(AB)^-1 = B^-1 A^-1"] = all(
            inv_AB[i][j] == prod_inv[i][j] for i in range(n) for j in range(n)
        )

    return resultados
