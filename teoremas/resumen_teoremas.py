"""
MÓDULO DE TEOREMAS Y FUNDAMENTOS CLAVE DE ÁLGEBRA LINEAL
Universidad Americana (UAM) - Facultad de Ingeniería y Arquitectura (FIA)
Asignatura: Álgebra Lineal (MTM0120)

Despliega de forma resumida, rigurosa y didáctica los teoremas analizados
en las clases magistrales para cada uno de los 4 módulos del Programa 4.
"""

def teoremas_sistemas() -> str:
    return """
======================================================================
 📘 TEOREMAS CLAVE — MÓDULO 1: SISTEMAS DE ECUACIONES LINEALES (SEL)
======================================================================

1. TEOREMA DE OPERACIONES ELEMENTALES POR FILAS:
   Las tres operaciones elementales:
     a) Intercambiar dos filas (Fi ↔ Fj).
     b) Multiplicar una fila por un escalar c ≠ 0 (Fi → c·Fi).
     c) Sumar a una fila un múltiplo de otra (Fi → Fi + k·Fj).
   producen un sistema equivalente, lo que significa que el conjunto
   solución no se altera.

2. TEOREMA DE ROUCHÉ–FROBENIUS (CRITERIO DE COMPATIBILIDAD):
   Sea [A | b] la matriz aumentada del sistema con n incógnitas:
     • Inconsistente (Sin Solución): rango(A) < rango([A | b]).
       Surge una fila de la forma [ 0 0 ... 0 | k ] con k ≠ 0 (contradicción 0 = k).
     • Consistente Determinado (Solución Única): rango(A) = rango([A | b]) = n.
       Cada columna contiene un pivote; no existen variables libres.
     • Consistente Indeterminado (Infinitas Soluciones): rango(A) = rango([A | b]) = r < n.
       Existen (n - r) variables libres que actúan como parámetros independientes.

3. TEOREMA DE SISTEMAS HOMOGÉNEOS (Ax = 0):
   • Todo sistema homogéneo es consistente, pues siempre admite al menos
     la solución trivial x₁ = x₂ = ... = xₙ = 0.
   • El sistema Ax = 0 tiene soluciones no triviales (infinitas) si y solo si
     el número de incógnitas supera el número de pivotes (existen variables libres).
   • Si A es una matriz m × n con m < n (más incógnitas que ecuaciones),
     entonces Ax = 0 tiene infinitas soluciones no triviales.
======================================================================
"""


def teoremas_vectores() -> str:
    return """
======================================================================
 📘 TEOREMAS CLAVE — MÓDULO 2: VECTORES E INDEPENDENCIA LINEAL
======================================================================

1. TEOREMA DE INDEPENDENCIA LINEAL (DEFINICIÓN FUNDAMENTAL):
   Un conjunto de k vectores {v₁, v₂, ..., vₖ} en ℝⁿ es LINEALMENTE
   INDEPENDIENTE (L.I.) si y solo si la única solución a la ecuación
   vectorial homogénea:
       c₁v₁ + c₂v₂ + ... + cₖvₖ = 0̄
   es la solución trivial c₁ = c₂ = ... = cₖ = 0 (sin variables libres).

2. TEOREMA DEL SISTEMA HOMOGÉNEO Y COLUMNAS:
   Al formar la matriz A = [v₁  v₂  ...  vₖ] con los vectores como columnas:
     • Los vectores son L.I. si y solo si Ax = 0 tiene únicamente la solución trivial.
     • En la forma escalonada reducida (RREF), cada una de las k columnas
       debe contener una posición pivote (número de pivotes = k).
     • Si alguna columna carece de pivote, surge al menos una variable libre,
       lo cual garantiza que el conjunto es LINEALMENTE DEPENDIENTE (L.D.).

3. TEOREMAS Y CRITERIOS RÁPIDOS POR INSPECCIÓN:
   a) Criterio de dos vectores: Un conjunto de 2 vectores {u, v} es L.D.
      si y solo si uno es múltiplo escalar del otro (u = c·v).
   b) Teorema del Vector Cero: Todo conjunto que contenga al vector cero 0̄
      es automáticamente L.D., pues 1·0̄ + 0·v₁ + ... = 0̄.
   c) Teorema de p > n: Cualquier conjunto de p vectores en ℝⁿ con p > n
      (más vectores que entradas por vector) es OBLIGATORIAMENTE L.D.
      (no pueden existir más de n pivotes en ℝⁿ).
   d) Caracterización de conjuntos L.D.: Un conjunto {v₁, ..., vₖ} es L.D.
      si y solo si al menos uno de los vectores se puede escribir como
      combinación lineal de los demás.

4. TEOREMA DE COMBINACIÓN LINEAL Y ESPACIO GENERADOR:
   Un vector b pertenece al subespacio generado Gen{v₁, ..., vₖ} si y solo
   si el sistema [v₁  v₂  ...  vₖ | b] es consistente (tiene solución).
======================================================================
"""


def teoremas_matrices() -> str:
    return """
======================================================================
 📘 TEOREMAS CLAVE — MÓDULO 3: ÁLGEBRA DE MATRICES E INVERSA
======================================================================

1. PROPIEDADES DEL PRODUCTO MATRIZ-VECTOR (LINEALIDAD):
   Si A es una matriz m × n, u, v ∈ ℝⁿ y c es un escalar real:
     a) Propiedad Aditiva / Distributiva:
        A(u + v) = Au + Av
        Generalización: A(v₁ + v₂ + ... + vₖ) = Av₁ + Av₂ + ... + Avₖ
     b) Propiedad de Homogeneidad Escalar:
        A(cu) = c(Au)
     c) Principio de Linealidad General (Superposición):
        A(c₁v₁ + c₂v₂ + ... + cₖvₖ) = c₁(Av₁) + c₂(Av₂) + ... + cₖ(Avₖ)

2. MULTIPLICACIÓN MATRICIAL:
   • Para calcular A · B, el número de columnas de A debe ser igual
     al número de filas de B (A_{m×n} y B_{n×p} produce C_{m×p}).
   • En general, el producto matricial NO es conmutativo: A·B ≠ B·A.
   • Propiedades válidas:
       - Asociativa: A(BC) = (AB)C
       - Distributiva: A(B + C) = AB + AC
       - Traspuesta de producto: (AB)ᵀ = Bᵀ Aᵀ

3. TEOREMA DE LA MATRIZ INVERTIBLE (TMI):
   Para una matriz cuadrada A de n × n, las siguientes proposiciones son EQUIVALENTES:
     1. A es una matriz invertible (existe A⁻¹ tal que A·A⁻¹ = A⁻¹·A = Iₙ).
     2. A es equivalente por filas a la matriz identidad Iₙ.
     3. A tiene n posiciones pivote (rango completo = n).
     4. La ecuación homogénea Ax = 0 tiene únicamente la solución trivial.
     5. Las columnas de A son linealmente independientes.
     6. Las columnas de A generan a ℝⁿ.
     7. det(A) ≠ 0.

4. ALGORITMO DE INVERSIÓN POR GAUSS-JORDAN:
   Se plantea la matriz aumentada [ A | Iₙ ]. Se aplican operaciones
   elementales por fila hasta transformar el bloque izquierdo en Iₙ:
       [ A | Iₙ ]  →  [ Iₙ | A⁻¹ ]
   Si surge una fila de ceros a la izquierda, A es singular (no invertible).
======================================================================
"""


def teoremas_determinantes() -> str:
    return """
======================================================================
 📘 TEOREMAS CLAVE — MÓDULO 4: DETERMINANTES Y PROPIEDADES
======================================================================

1. PROPIEDADES FUNDAMENTALES DEL DETERMINANTE:
   Sea A una matriz cuadrada de n × n:
     • det(Iₙ) = 1.
     • det(Aᵀ) = det(A) (el determinante de la traspuesta es idéntico).
     • det(A · B) = det(A) · det(B) (el determinante del producto es el producto de determinantes).
     • det(c · A) = cⁿ · det(A) (al multiplicar la matriz por c, cada fila aporta un factor c).
     • Si A es invertible: det(A⁻¹) = 1 / det(A).

2. EFECTO DE LAS OPERACIONES ELEMENTALES:
   • Intercambio de dos filas: multiplica el determinante por -1.
   • Multiplicación de una fila por escalar k: multiplica el determinante por k.
   • Sumar a una fila un múltiplo de otra fila: NO cambia el determinante.

3. CASOS EN QUE EL DETERMINANTE ES CERO (det(A) = 0):
   • Si A tiene una fila o columna completamente de ceros.
   • Si dos filas (o columnas) son iguales o proporcionales.
   • Si una fila es combinación lineal de las demás.
   • En todos estos casos, las columnas son L.D. y la matriz es singular.

4. CÁLCULO MEDIANTE TRIANGULACIÓN (GAUSS):
   Si A se reduce a una matriz triangular superior U mediante r intercambios
   de filas y sumas de múltiplos de filas, entonces:
       det(A) = (-1)ʳ · (u₁₁ · u₂₂ · ... · uₙₙ)
   El determinante es el producto de los elementos de la diagonal principal.
======================================================================
"""


def resumen_general() -> str:
    return f"""
======================================================================
 🎓 RESUMEN TEÓRICO INTEGRADO DEL CURSO DE ÁLGEBRA LINEAL (MTM0120)
======================================================================
{teoremas_sistemas()}
{teoremas_vectores()}
{teoremas_matrices()}
{teoremas_determinantes()}
======================================================================
"""
