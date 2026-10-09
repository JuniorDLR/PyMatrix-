"""Verificación computacional de propiedades del producto matriz-vector Ax.
Tema de clase: propiedades algebraicas de transformaciones matriciales (Sesión 8).
Comprueba aditividad A(u+v) = Au + Av, homogeneidad A(cu) = c(Au) y linealidad general.
Elaborado por: Grupo x"""

from src.core.ecuaciones_ax import multiplicar_matriz_vector
from src.core.operaciones_basicas import multiplicar_matriz_escalar, sumar_matrices, combinacion_matrices
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Union, Any
from fractions import Fraction

from src.core.domain import Matriz, formatear_numero, formatear_fraccion, a_subindice
from src.core.gauss import resolver_gauss_jordan, copiar_matriz, PasoGauss, SolucionUnica, SolucionInfinita, SinSolucion, SolucionGeneral
from src.core.vectors import Vector

@dataclass
class VerificacionPropiedadAditivaAx:
    """Demostración y verificación paso a paso de A(u + v) = Au + Av (o para k vectores)."""
    vectores: List[Vector]
    suma_vectores: Vector
    lado_izq_A_suma: Vector
    vectores_transformados: List[Vector]
    lado_der_suma_transformados: Vector
    se_cumple: bool
    desglose_pasos: List[str]

    @property
    def u(self) -> Vector:
        """Primer vector sumado (u), o [] si no hay."""
        return self.vectores[0] if self.vectores else []

    @property
    def v(self) -> Vector:
        """Segundo vector sumado (v), o [] si no existe."""
        return self.vectores[1] if len(self.vectores) > 1 else []

    @property
    def u_mas_v(self) -> Vector:
        """Suma de los vectores (u + v)."""
        return self.suma_vectores

    @property
    def lado_izq_A_u_mas_v(self) -> Vector:
        """Lado izquierdo A(u + v)."""
        return self.lado_izq_A_suma

    @property
    def Au(self) -> Vector:
        """Producto A·u, o [] si no hay."""
        return self.vectores_transformados[0] if self.vectores_transformados else []

    @property
    def Av(self) -> Vector:
        """Producto A·v, o [] si no existe."""
        return self.vectores_transformados[1] if len(self.vectores_transformados) > 1 else []

    @property
    def lado_der_Au_mas_Av(self) -> Vector:
        """Lado derecho Au + Av."""
        return self.lado_der_suma_transformados

@dataclass
class VerificacionPropiedadEscalarAx:
    """Demostración y verificación paso a paso de A(cu) = c(Au)."""
    c: float
    u: Vector
    c_u: Vector
    lado_izq_A_cu: Vector
    Au: Vector
    lado_der_c_Au: Vector
    se_cumple: bool
    desglose_pasos: List[str]

@dataclass
class VerificacionLinealidadGeneralAx:
    """Demostración y verificación de A(c₁v₁ + ... + cₖvₖ) = c₁(Av₁) + ... + cₖ(Avₖ)."""
    vectores: List[Vector]
    escalares: List[float]
    comb_lineal_vectores: Vector
    lado_izq_A_comb: Vector
    vectores_transformados: List[Vector]
    vectores_escalados_transformados: List[Vector]
    lado_der_suma_escalados: Vector
    se_cumple: bool
    desglose_pasos: List[str]

def verificar_propiedad_aditiva_ax(
    A: Matriz,
    u_o_vectores: Union[Vector, List[Vector]],
    v: Optional[Vector] = None,
    modo: str = "fraccion"
) -> VerificacionPropiedadAditivaAx:
    """Verifica A(u + v) = Au + Av (o la versión con k vectores) comparando ambos lados.
    Recibe A, dos vectores o una lista de vectores y modo; devuelve ambos lados, el desglose y si se cumple."""
    if not A or not A[0]:
        raise ValueError("La matriz A no puede estar vacía.")
    m = len(A)
    n = len(A[0])

    if v is not None:
        vectores: List[Vector] = [u_o_vectores, v]  # type: ignore
    elif isinstance(u_o_vectores, list) and u_o_vectores and isinstance(u_o_vectores[0], list):
        vectores = u_o_vectores  # type: ignore
    else:
        raise ValueError("Debe ingresar al menos dos vectores para verificar la propiedad distributiva.")

    k = len(vectores)
    if k < 2:
        raise ValueError("Se requieren al menos 2 vectores para verificar la propiedad aditiva.")

    for idx, vec in enumerate(vectores):
        if len(vec) != n:
            raise ValueError(
                f"Dimensión incompatible: La matriz A tiene {n} columnas, pero el vector {idx+1} "
                f"tiene {len(vec)} componentes. Todos los vectores deben pertenecer a ℝ{a_subindice(n)}."
            )

    es_caso_dos = (k == 2)
    nombres = ["u", "v"] if es_caso_dos else [f"v{a_subindice(j+1)}" for j in range(k)]

    suma_vecs: Vector = [0.0] * n
    for vec in vectores:
        for i in range(n):
            suma_vecs[i] = round(suma_vecs[i] + vec[i], 9)

    res_A_suma = multiplicar_matriz_vector(A, suma_vecs, modo=modo)
    lado_izq = res_A_suma.vector_resultado

    res_A_vecs = [multiplicar_matriz_vector(A, vec, modo=modo) for vec in vectores]
    lado_der: Vector = [0.0] * m
    for r in res_A_vecs:
        for i in range(m):
            lado_der[i] = round(lado_der[i] + r.vector_resultado[i], 9)

    # Tolerancia y no ==: el redondeo a 9 decimales deja diferencias mínimas entre ambos lados.
    se_cumple = all(abs(izq - der) < 1e-7 for izq, der in zip(lado_izq, lado_der))

    pasos: List[str] = []
    pasos.append("======================================================================")
    if es_caso_dos:
        pasos.append("  PROPIEDAD a) DEL PRODUCTO MATRIZ-VECTOR: A(u + v) = Au + Av")
    else:
        formula_str = " + ".join(nombres)
        formula_der = " + ".join([f"A{nom}" for nom in nombres])
        pasos.append(f"  PROPIEDAD DISTRIBUTIVA GENERALIZADA: A({formula_str}) = {formula_der}")
    pasos.append("======================================================================\n")
    pasos.append(f"Teorema: Si A es una matriz de {m}×{n} y los {k} vectores pertenecen a ℝ{a_subindice(n)},")
    pasos.append("la multiplicación matriz-vector se distribuye sobre la suma de vectores.\n")

    expr_izq = "A(u + v)" if es_caso_dos else f"A({' + '.join(nombres)})"
    pasos.append(f"--- [1] DESARROLLO DEL LADO IZQUIERDO: {expr_izq} ---")
    for nom, vec in zip(nombres, vectores):
        v_str = "[" + ", ".join([formatear_numero(x, modo) for x in vec]) + "]ᵀ"
        pasos.append(f"  Vector {nom} = {v_str}")

    pasos.append(f"\n  Paso 1.1: Sumar vectores w = {' + '.join(nombres)} componente a componente:")
    for i in range(n):
        sumandos = " + ".join([f"({formatear_numero(vec[i], modo)})" for vec in vectores])
        pasos.append(f"    w{a_subindice(i+1)} = {sumandos} = {formatear_numero(suma_vecs[i], modo)}")
    suma_str = "[" + ", ".join([formatear_numero(x, modo) for x in suma_vecs]) + "]ᵀ"
    pasos.append(f"  Vector suma = {suma_str}\n")

    pasos.append(f"  Paso 1.2: Multiplicar A por el vector suma:")
    for linea in res_A_suma.desglose_filas:
        pasos.append(f"    {linea}")
    izq_str = "[" + ", ".join([formatear_numero(x, modo) for x in lado_izq]) + "]ᵀ"
    pasos.append(f"  => Vector L.I. = {expr_izq} = {izq_str}\n")

    expr_der = "Au + Av" if es_caso_dos else " + ".join([f"A{nom}" for nom in nombres])
    pasos.append(f"--- [2] DESARROLLO DEL LADO DERECHO: {expr_der} ---")
    for j, (nom, r) in enumerate(zip(nombres, res_A_vecs)):
        pasos.append(f"  Paso 2.{j+1}: Multiplicar A · {nom}:")
        for linea in r.desglose_filas:
            pasos.append(f"    {linea}")
        nom_r_str = "[" + ", ".join([formatear_numero(x, modo) for x in r.vector_resultado]) + "]ᵀ"
        pasos.append(f"    A · {nom} = {nom_r_str}\n")

    pasos.append(f"  Paso 2.{k+1}: Sumar los vectores transformados ({expr_der}):")
    for i in range(m):
        sumandos_der = " + ".join([f"({formatear_numero(r.vector_resultado[i], modo)})" for r in res_A_vecs])
        pasos.append(f"    Fila {i+1}: {sumandos_der} = {formatear_numero(lado_der[i], modo)}")
    der_str = "[" + ", ".join([formatear_numero(x, modo) for x in lado_der]) + "]ᵀ"
    pasos.append(f"  => Vector L.D. = {expr_der} = {der_str}\n")

    pasos.append("--- [3] CONCLUSIÓN Y VERIFICACIÓN TEÓRICA ---")
    pasos.append(f"  Lado Izquierdo {expr_izq} = {izq_str}")
    pasos.append(f"  Lado Derecho   {expr_der} = {der_str}")
    if se_cumple:
        pasos.append("\n  ✓ ¡PROPIEDAD VERIFICADA CON ÉXITO!")
        pasos.append(f"    Se cumple idénticamente que {expr_izq} = {expr_der} para cada componente.")
    else:
        pasos.append("\n  ✗ Discrepancia encontrada en la verificación numérica.")

    return VerificacionPropiedadAditivaAx(
        vectores=vectores,
        suma_vectores=suma_vecs,
        lado_izq_A_suma=lado_izq,
        vectores_transformados=[r.vector_resultado for r in res_A_vecs],
        lado_der_suma_transformados=lado_der,
        se_cumple=se_cumple,
        desglose_pasos=pasos
    )

def verificar_propiedad_escalar_ax(
    A: Matriz,
    u: Vector,
    c: float,
    modo: str = "fraccion",
    nombre_vector: str = "u"
) -> VerificacionPropiedadEscalarAx:
    """Verifica A(cu) = c(Au) para una matriz A, un vector u y un escalar c.
    Devuelve ambos lados, el desglose paso a paso y si se cumple."""
    if not A or not A[0]:
        raise ValueError("La matriz A no puede estar vacía.")
    m = len(A)
    n = len(A[0])
    if len(u) != n:
        raise ValueError(
            f"Dimensión incompatible: La matriz A tiene {n} columnas, pero el vector {nombre_vector} tiene {len(u)} componentes."
        )

    c_fmt = formatear_numero(c, modo)

    cu = [round(c * ui, 9) for ui in u]
    res_A_cu = multiplicar_matriz_vector(A, cu, modo=modo)
    lado_izq = res_A_cu.vector_resultado

    res_Au = multiplicar_matriz_vector(A, u, modo=modo)
    c_Au = [round(c * aui, 9) for aui in res_Au.vector_resultado]

    # Tolerancia y no ==: el redondeo a 9 decimales deja diferencias mínimas entre ambos lados.
    se_cumple = all(abs(izq - der) < 1e-7 for izq, der in zip(lado_izq, c_Au))

    pasos: List[str] = []
    pasos.append("======================================================================")
    pasos.append(f"  PROPIEDAD b) DEL PRODUCTO MATRIZ-VECTOR: A(c·{nombre_vector}) = c(A·{nombre_vector})")
    pasos.append("======================================================================\n")
    pasos.append(f"Teorema: Si A es una matriz de {m}×{n}, {nombre_vector} está en ℝ{a_subindice(n)}, y c = {c_fmt} es un escalar,")
    pasos.append("el escalar puede operar antes o después de la multiplicación matriz-vector.\n")

    pasos.append(f"--- [1] DESARROLLO DEL LADO IZQUIERDO: A(c·{nombre_vector}) ---")
    u_str = "[" + ", ".join([formatear_numero(x, modo) for x in u]) + "]ᵀ"
    cu_str = "[" + ", ".join([formatear_numero(x, modo) for x in cu]) + "]ᵀ"
    pasos.append(f"  Vector {nombre_vector} = {u_str}")
    pasos.append(f"  Escalar c = {c_fmt}")
    pasos.append(f"  Paso 1.1: Multiplicar escalar por vector w = c · {nombre_vector}:")
    for i, (ui, c_ui) in enumerate(zip(u, cu)):
        pasos.append(f"    w{a_subindice(i+1)} = ({c_fmt}) · ({formatear_numero(ui, modo)}) = {formatear_numero(c_ui, modo)}")
    pasos.append(f"  Vector escalado (c·{nombre_vector}) = {cu_str}\n")

    pasos.append(f"  Paso 1.2: Multiplicar A por el vector escalado (c·{nombre_vector}):")
    for linea in res_A_cu.desglose_filas:
        pasos.append(f"    {linea}")
    izq_str = "[" + ", ".join([formatear_numero(x, modo) for x in lado_izq]) + "]ᵀ"
    pasos.append(f"  => Vector L.I. = A(c·{nombre_vector}) = {izq_str}\n")

    pasos.append(f"--- [2] DESARROLLO DEL LADO DERECHO: c(A·{nombre_vector}) ---")
    pasos.append(f"  Paso 2.1: Multiplicar A · {nombre_vector}:")
    for linea in res_Au.desglose_filas:
        pasos.append(f"    {linea}")
    Au_str = "[" + ", ".join([formatear_numero(x, modo) for x in res_Au.vector_resultado]) + "]ᵀ"
    pasos.append(f"    A · {nombre_vector} = {Au_str}\n")

    pasos.append(f"  Paso 2.2: Multiplicar el resultado A·{nombre_vector} por el escalar c = {c_fmt}:")
    for i, (au_i, c_au_i) in enumerate(zip(res_Au.vector_resultado, c_Au)):
        pasos.append(f"    Fila {i+1}: ({c_fmt}) · ({formatear_numero(au_i, modo)}) = {formatear_numero(c_au_i, modo)}")
    der_str = "[" + ", ".join([formatear_numero(x, modo) for x in c_Au]) + "]ᵀ"
    pasos.append(f"  => Vector L.D. = c(A·{nombre_vector}) = {der_str}\n")

    pasos.append("--- [3] CONCLUSIÓN Y VERIFICACIÓN TEÓRICA ---")
    pasos.append(f"  Lado Izquierdo A(c·{nombre_vector}) = {izq_str}")
    pasos.append(f"  Lado Derecho   c(A·{nombre_vector}) = {der_str}")
    if se_cumple:
        pasos.append("\n  ✓ ¡PROPIEDAD VERIFICADA CON ÉXITO!")
        pasos.append(f"    Se cumple idénticamente que A(c·{nombre_vector}) = c(A·{nombre_vector}) para cada componente.")
    else:
        pasos.append("\n  ✗ Discrepancia encontrada en la verificación numérica.")

    return VerificacionPropiedadEscalarAx(
        c=c, u=u, c_u=cu,
        lado_izq_A_cu=lado_izq,
        Au=res_Au.vector_resultado,
        lado_der_c_Au=c_Au,
        se_cumple=se_cumple,
        desglose_pasos=pasos
    )

def verificar_linealidad_general_ax(
    A: Matriz,
    vectores: List[Vector],
    escalares: List[float],
    modo: str = "fraccion"
) -> VerificacionLinealidadGeneralAx:
    """Verifica A(c₁v₁ + ... + cₖvₖ) = c₁(Av₁) + ... + cₖ(Avₖ) para k ≥ 2 vectores.
    Recibe A, vectores, escalares y modo; devuelve ambos lados, el desglose y si se cumple."""
    if not A or not A[0]:
        raise ValueError("La matriz A no puede estar vacía.")
    m = len(A)
    n = len(A[0])
    k = len(vectores)
    if k != len(escalares):
        raise ValueError(f"Debe haber igual número de vectores ({k}) que de escalares ({len(escalares)}).")
    if k < 2:
        raise ValueError("Se requieren al menos 2 vectores para la combinación lineal general.")

    for idx, vec in enumerate(vectores):
        if len(vec) != n:
            raise ValueError(f"El vector v{idx+1} tiene {len(vec)} componentes, pero la matriz A tiene {n} columnas.")

    nombres = ["u", "v"] if k == 2 else [f"v{a_subindice(j+1)}" for j in range(k)]

    comb_vec: Vector = [0.0] * n
    for c_val, vec in zip(escalares, vectores):
        for i in range(n):
            comb_vec[i] = round(comb_vec[i] + c_val * vec[i], 9)

    res_A_comb = multiplicar_matriz_vector(A, comb_vec, modo=modo)
    lado_izq = res_A_comb.vector_resultado

    res_A_vecs = [multiplicar_matriz_vector(A, vec, modo=modo) for vec in vectores]
    vecs_escalados: List[Vector] = []
    for c_val, r in zip(escalares, res_A_vecs):
        v_esc = [round(c_val * comp, 9) for comp in r.vector_resultado]
        vecs_escalados.append(v_esc)

    lado_der: Vector = [0.0] * m
    for v_esc in vecs_escalados:
        for i in range(m):
            lado_der[i] = round(lado_der[i] + v_esc[i], 9)

    # Tolerancia y no ==: el redondeo a 9 decimales deja diferencias mínimas entre ambos lados.
    se_cumple = all(abs(izq - der) < 1e-7 for izq, der in zip(lado_izq, lado_der))

    pasos: List[str] = []
    pasos.append("======================================================================")
    pasos.append("  PRINCIPIO DE SUPERPOSICIÓN / LINEALIDAD GENERAL DEL PRODUCTO Ax")
    pasos.append("======================================================================\n")
    comb_formula = " + ".join([f"({formatear_numero(c, modo)})·{nom}" for c, nom in zip(escalares, nombres)])
    der_formula = " + ".join([f"({formatear_numero(c, modo)})·(A·{nom})" for c, nom in zip(escalares, nombres)])
    pasos.append(f"Teorema General: Para una matriz A de {m}×{n}, {k} vectores en ℝ{a_subindice(n)} y sus escalares:")
    pasos.append(f"  A( {comb_formula} ) = {der_formula}\n")

    pasos.append("--- [1] DESARROLLO DEL LADO IZQUIERDO: A( ∑ cᵢ vᵢ ) ---")
    for nom, c_val, vec in zip(nombres, escalares, vectores):
        v_str = "[" + ", ".join([formatear_numero(x, modo) for x in vec]) + "]ᵀ"
        pasos.append(f"  Vector {nom} = {v_str}  (Escalar c = {formatear_numero(c_val, modo)})")

    pasos.append("\n  Paso 1.1: Calcular la combinación lineal de los vectores w = ∑ cᵢ vᵢ:")
    for i in range(n):
        sumandos = " + ".join([f"({formatear_numero(c, modo)})·({formatear_numero(v[i], modo)})" for c, v in zip(escalares, vectores)])
        pasos.append(f"    w{a_subindice(i+1)} = {sumandos} = {formatear_numero(comb_vec[i], modo)}")
    comb_str = "[" + ", ".join([formatear_numero(x, modo) for x in comb_vec]) + "]ᵀ"
    pasos.append(f"  Vector combinación lineal w = {comb_str}\n")

    pasos.append("  Paso 1.2: Multiplicar A por el vector combinación lineal:")
    for linea in res_A_comb.desglose_filas:
        pasos.append(f"    {linea}")
    izq_str = "[" + ", ".join([formatear_numero(x, modo) for x in lado_izq]) + "]ᵀ"
    pasos.append(f"  => Vector L.I. = A( ∑ cᵢ vᵢ ) = {izq_str}\n")

    pasos.append("--- [2] DESARROLLO DEL LADO DERECHO: ∑ cᵢ (A · vᵢ) ---")
    for j, (nom, c_val, r, v_esc) in enumerate(zip(nombres, escalares, res_A_vecs, vecs_escalados)):
        pasos.append(f"  Paso 2.{j+1}a: Multiplicar A · {nom}:")
        nom_r_str = "[" + ", ".join([formatear_numero(x, modo) for x in r.vector_resultado]) + "]ᵀ"
        pasos.append(f"    A · {nom} = {nom_r_str}")
        pasos.append(f"  Paso 2.{j+1}b: Escalar por c = {formatear_numero(c_val, modo)}:")
        esc_str = "[" + ", ".join([formatear_numero(x, modo) for x in v_esc]) + "]ᵀ"
        pasos.append(f"    {formatear_numero(c_val, modo)} · (A·{nom}) = {esc_str}\n")

    pasos.append(f"  Paso 2.{k+1}: Sumar los vectores escalados resultantes:")
    for i in range(m):
        sumandos_der = " + ".join([f"({formatear_numero(ve[i], modo)})" for ve in vecs_escalados])
        pasos.append(f"    Fila {i+1}: {sumandos_der} = {formatear_numero(lado_der[i], modo)}")
    der_str = "[" + ", ".join([formatear_numero(x, modo) for x in lado_der]) + "]ᵀ"
    pasos.append(f"  => Vector L.D. = ∑ cᵢ (A · vᵢ) = {der_str}\n")

    pasos.append("--- [3] CONCLUSIÓN Y VERIFICACIÓN TEÓRICA ---")
    pasos.append(f"  Lado Izquierdo A( ∑ cᵢ vᵢ )  = {izq_str}")
    pasos.append(f"  Lado Derecho   ∑ cᵢ (A · vᵢ) = {der_str}")
    if se_cumple:
        pasos.append("\n  ✓ ¡PROPIEDAD DE LINEALIDAD GENERAL VERIFICADA CON ÉXITO!")
        pasos.append("    La transformación matricial preserva exactamente las combinaciones lineales.")
    else:
        pasos.append("\n  ✗ Discrepancia encontrada en la verificación numérica.")

    return VerificacionLinealidadGeneralAx(
        vectores=vectores,
        escalares=escalares,
        comb_lineal_vectores=comb_vec,
        lado_izq_A_comb=lado_izq,
        vectores_transformados=[r.vector_resultado for r in res_A_vecs],
        vectores_escalados_transformados=vecs_escalados,
        lado_der_suma_escalados=lado_der,
        se_cumple=se_cumple,
        desglose_pasos=pasos
    )

