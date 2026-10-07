"""
Operaciones con vectores en ℝⁿ, combinación lineal e independencia lineal (Gauss-Jordan).
Implementado solo con Python estándar (sin NumPy ni SciPy).
Elaborado por: Grupo x
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import math

from src.core.domain import (
    Matriz, formatear_numero, formatear_fraccion, a_subindice
)
from src.core.gauss import (
    resolver_gauss_jordan, copiar_matriz, PasoGauss,
    SolucionUnica, SolucionInfinita, SinSolucion, SolucionGeneral
)

Vector = List[float]


def validar_mismas_dimensiones(u: Vector, v: Vector, nombre_op: str = "operación") -> None:
    """Verifica que u y v sean no vacíos y del mismo ℝⁿ; lanza ValueError si no.

    La suma y la resta solo están definidas entre vectores de igual dimensión.
    """
    if not u or not v:
        raise ValueError("Los vectores no pueden estar vacíos.")
    if len(u) != len(v):
        raise ValueError(
            f"Error de dimensión en {nombre_op}: El vector u tiene dimensión {len(u)} "
            f"y el vector v tiene dimensión {len(v)}. Ambos deben pertenecer al mismo ℝⁿ."
        )


def sumar_vectores(u: Vector, v: Vector) -> Vector:
    """Calcula u + v sumando componente a componente; devuelve un vector de ℝⁿ."""
    validar_mismas_dimensiones(u, v, "suma de vectores")
    resultado: Vector = []
    for i in range(len(u)):
        resultado.append(round(u[i] + v[i], 9))
    return resultado


def restar_vectores(u: Vector, v: Vector) -> Vector:
    """Calcula u - v componente a componente; devuelve un vector de ℝⁿ."""
    validar_mismas_dimensiones(u, v, "resta de vectores")
    resultado: Vector = []
    for i in range(len(u)):
        resultado.append(round(u[i] - v[i], 9))
    return resultado


def multiplicar_vector_escalar(c: float, v: Vector) -> Vector:
    """Calcula c·v multiplicando cada componente por el escalar c; devuelve un vector de ℝⁿ."""
    if not v:
        raise ValueError("El vector no puede estar vacío.")
    resultado: Vector = []
    for componente in v:
        resultado.append(round(c * componente, 9))
    return resultado


def sumar_multiples_vectores(vectores: List[Vector]) -> Vector:
    """Calcula v₁ + v₂ + ... + vₖ; recibe una lista de vectores de igual dimensión."""
    if not vectores:
        raise ValueError("Debe proporcionar al menos un vector.")
    dim = len(vectores[0])
    for j, v in enumerate(vectores):
        if len(v) != dim:
            raise ValueError(f"El vector v{j+1} tiene dimensión {len(v)}, pero se esperaba {dim}.")
    
    resultado: Vector = [0.0] * dim
    for v in vectores:
        for i in range(dim):
            resultado[i] += v[i]
    return [round(x, 9) for x in resultado]


def restar_multiples_vectores(vectores: List[Vector]) -> Vector:
    """Calcula v₁ - v₂ - ... - vₖ; recibe una lista de vectores de igual dimensión."""
    if not vectores:
        raise ValueError("Debe proporcionar al menos un vector.")
    dim = len(vectores[0])
    for j, v in enumerate(vectores):
        if len(v) != dim:
            raise ValueError(f"El vector v{j+1} tiene dimensión {len(v)}, pero se esperaba {dim}.")
    
    resultado: Vector = list(vectores[0])
    for v in vectores[1:]:
        for i in range(dim):
            resultado[i] -= v[i]
    return [round(x, 9) for x in resultado]


def combinacion_lineal_ponderada(escalares: List[float], vectores: List[Vector]) -> Vector:
    """Calcula c₁v₁ + ... + cₖvₖ; recibe k escalares y k vectores de igual dimensión."""
    if not vectores or not escalares:
        raise ValueError("Debe proporcionar listas no vacías de vectores y escalares.")
    if len(escalares) != len(vectores):
        raise ValueError(
            f"La cantidad de escalares ({len(escalares)}) debe ser igual a la cantidad de vectores ({len(vectores)})."
        )
    dim = len(vectores[0])
    for j, v in enumerate(vectores):
        if len(v) != dim:
            raise ValueError(f"El vector v{j+1} tiene dimensión {len(v)}, pero se esperaba {dim}.")
            
    resultado: Vector = [0.0] * dim
    for c, v in zip(escalares, vectores):
        for i in range(dim):
            resultado[i] += c * v[i]
    return [round(x, 9) for x in resultado]


def producto_punto(u: Vector, v: Vector) -> float:
    """Calcula u · v = Σ uᵢvᵢ; devuelve un escalar (base de la regla fila-vector de Ax)."""
    validar_mismas_dimensiones(u, v, "producto punto")
    suma = 0.0
    for i in range(len(u)):
        suma += u[i] * v[i]
    return round(suma, 9)


def norma_vector(v: Vector) -> float:
    """Calcula la norma euclidiana ||v|| = √(v · v); devuelve un escalar."""
    if not v:
        raise ValueError("El vector no puede estar vacío.")
    suma_cuadrados = sum(x * x for x in v)
    return round(math.sqrt(suma_cuadrados), 6)


def son_proporcionales_2_vectores(u: Vector, v: Vector) -> Tuple[bool, Optional[float]]:
    """Indica si u y v son múltiplos escalares; devuelve (es_proporcional, k) con u = k·v.

    En ℝⁿ, {u, v} es linealmente dependiente si y solo si uno es múltiplo del otro.
    """
    validar_mismas_dimensiones(u, v, "proporcionalidad")
    # El vector nulo es múltiplo de cualquier vector (0·v); se usa tolerancia por el error de punto flotante.
    if all(abs(x) < 1e-10 for x in u) or all(abs(x) < 1e-10 for x in v):
        return True, 0.0
    
    escalar: Optional[float] = None
    for ui, vi in zip(u, v):
        if abs(vi) < 1e-10:
            # Si vi = 0, ui debe ser 0; de lo contrario ningún k cumple ui = k·vi.
            if abs(ui) > 1e-10:
                return False, None
        else:
            k = ui / vi
            if escalar is None:
                escalar = k
            elif abs(k - escalar) > 1e-6:
                return False, None
    return True, escalar


@dataclass
class ResultadoCombinacionLineal:
    """Resultado de evaluar si b es combinación lineal de {v₁, ..., vₖ}.

    Guarda el tipo de solución, los pesos, las matrices inicial y RREF, los pasos y la explicación.
    """
    es_combinacion: bool
    tipo_solucion: str
    pesos: Optional[List[float]]
    solucion_general: Optional[SolucionGeneral]
    matriz_aumentada_inicial: Matriz
    matriz_rref: Matriz
    pasos_gauss: List[PasoGauss]
    explicacion: str


def evaluar_combinacion_lineal(vectores: List[Vector], b: Vector, modo: str = "fraccion") -> ResultadoCombinacionLineal:
    """Decide si b es combinación lineal de {v₁, ..., vₖ}; devuelve un ResultadoCombinacionLineal.

    Resuelve [v₁ ... vₖ | b] por Gauss-Jordan: b es combinación si y solo si el sistema es consistente.
    """
    if not vectores:
        raise ValueError("Debe proporcionar al menos un vector en el conjunto generador.")
    
    dim = len(vectores[0])
    for idx, v in enumerate(vectores):
        if len(v) != dim:
            raise ValueError(f"El vector v{idx+1} tiene dimensión {len(v)}, pero se esperaba {dim}.")
    if len(b) != dim:
        raise ValueError(f"El vector objetivo b tiene dimensión {len(b)}, pero los vectores están en ℝ{a_subindice(dim)}.")
    
    k = len(vectores)
    
    # Los vectores van como columnas para que cᵢ sean las incógnitas del sistema.
    matriz_aum: Matriz = []
    for fila_idx in range(dim):
        fila = [vectores[col_idx][fila_idx] for col_idx in range(k)]
        fila.append(b[fila_idx])
        matriz_aum.append(fila)
    
    pasos, res, sol_gen = resolver_gauss_jordan(matriz_aum)
    matriz_rref = sol_gen.matriz_rref if sol_gen else pasos[-1].matriz_estado
    
    if isinstance(res, SinSolucion):
        explicacion = (
            "El vector b NO se puede generar como combinación lineal de los vectores dados.\n"
            "Justificación algebraica: Al reducir la matriz aumentada [v₁ v₂ ... vₖ | b] a su forma "
            "escalonada reducida (RREF), aparece una fila inconsistente del tipo [0 0 ... 0 | k] con k ≠ 0, "
            "lo que demuestra que el sistema es Incompatible (sin solución)."
        )
        return ResultadoCombinacionLineal(
            es_combinacion=False,
            tipo_solucion="Inconsistente (No es combinación lineal)",
            pesos=None,
            solucion_general=None,
            matriz_aumentada_inicial=matriz_aum,
            matriz_rref=matriz_rref,
            pasos_gauss=pasos,
            explicacion=explicacion
        )
        
    elif isinstance(res, SolucionUnica):
        pesos = res.variables
        terminos_comb = []
        for i, peso in enumerate(pesos):
            peso_str = formatear_numero(peso, modo)
            terminos_comb.append(f"({peso_str})·v{a_subindice(i+1)}")
        ecuacion_comb = "b = " + " + ".join(terminos_comb)
        
        explicacion = (
            "El vector b SÍ es una combinación lineal ÚNICA del conjunto de vectores.\n"
            f"Ecuación vectorial resultante:\n  {ecuacion_comb}\n\n"
            "Pesos (escalares) obtenidos:\n" +
            "\n".join([f"  c{a_subindice(i+1)} = {formatear_numero(p, modo)}" for i, p in enumerate(pesos)])
        )
        return ResultadoCombinacionLineal(
            es_combinacion=True,
            tipo_solucion="Consistente Determinado (Pesos Únicos)",
            pesos=pesos,
            solucion_general=sol_gen,
            matriz_aumentada_inicial=matriz_aum,
            matriz_rref=matriz_rref,
            pasos_gauss=pasos,
            explicacion=explicacion
        )
        
    else:
        vars_libres = res.variables_libres
        lineas_param = sol_gen.a_strings(k, modo=modo) if sol_gen else []
        explicacion = (
            "El vector b SÍ es combinación lineal de los vectores dados, con INFINITAS maneras de representarlo.\n"
            f"El sistema posee {len(vars_libres)} variable(s) libre(s) como parámetro(s).\n\n"
            "Solución general de los pesos cᵢ:\n" +
            "\n".join([f"  {linea.replace('x', 'c')}" for linea in lineas_param])
        )
        return ResultadoCombinacionLineal(
            es_combinacion=True,
            tipo_solucion="Consistente Indeterminado (Infinitas Combinaciones)",
            pesos=None,
            solucion_general=sol_gen,
            matriz_aumentada_inicial=matriz_aum,
            matriz_rref=matriz_rref,
            pasos_gauss=pasos,
            explicacion=explicacion
        )


@dataclass
class ResultadoIndependenciaLineal:
    """Resultado de analizar si {v₁, ..., vₖ} es L.I. o L.D.

    Guarda el criterio usado, la relación de dependencia (si hay), las matrices, los pasos y la explicación.
    """
    es_linealmente_independiente: bool
    criterio_utilizado: str
    relacion_dependencia: Optional[str]
    matriz_homogenea_inicial: Matriz
    matriz_rref: Matriz
    pasos_gauss: List[PasoGauss]
    explicacion: str


def evaluar_independencia_lineal(vectores: List[Vector], modo: str = "fraccion") -> ResultadoIndependenciaLineal:
    """Determina si {v₁, ..., vₖ} en ℝⁿ es L.I. o L.D.; devuelve un ResultadoIndependenciaLineal.

    Aplica inspección directa (vector cero, k > n, dos proporcionales) y si no, resuelve [v₁ ... vₖ | 0].
    """
    if not vectores:
        raise ValueError("Debe proporcionar al menos un vector para analizar.")
    
    k = len(vectores)
    dim = len(vectores[0])
    
    for idx, v in enumerate(vectores):
        if len(v) != dim:
            raise ValueError(f"El vector v{idx+1} tiene dimensión {len(v)}, pero el primero tiene {dim}.")
    
    # Sistema homogéneo: siempre es consistente (c = 0 es solución), solo importa si hay otras.
    matriz_homogenea: Matriz = []
    for r in range(dim):
        fila = [vectores[c][r] for c in range(k)]
        fila.append(0.0)
        matriz_homogenea.append(fila)
    
    pasos, res, sol_gen = resolver_gauss_jordan(matriz_homogenea)
    matriz_rref = sol_gen.matriz_rref if sol_gen else pasos[-1].matriz_estado
    
    # Un conjunto con el vector cero es L.D.: 1·0̄ = 0̄ es una relación no trivial.
    for idx, v in enumerate(vectores):
        if all(abs(comp) < 1e-10 for comp in v):
            rel = f"1·v{a_subindice(idx+1)} = 0"
            explicacion = (
                f"El conjunto es LINEALMENTE DEPENDIENTE por inspección directa.\n"
                f"Teorema: Si un conjunto de vectores contiene al vector cero (0̄), entonces es linealmente dependiente "
                f"(el vector v{a_subindice(idx+1)} es el vector cero).\n"
                f"Relación no trivial inmediata: {rel} (con coeficiente c{a_subindice(idx+1)} = 1 ≠ 0)."
            )
            return ResultadoIndependenciaLineal(
                es_linealmente_independiente=False,
                criterio_utilizado="Teorema del Vector Cero",
                relacion_dependencia=rel,
                matriz_homogenea_inicial=matriz_homogenea,
                matriz_rref=matriz_rref,
                pasos_gauss=pasos,
                explicacion=explicacion
            )
    
    # Con k > n hay más incógnitas que ecuaciones, así que siempre queda una variable libre.
    if k > dim:
        rel = _generar_relacion_dependencia(sol_gen, k, modo)
        explicacion = (
            f"El conjunto es LINEALMENTE DEPENDIENTE por inspección directa.\n"
            f"Teorema: Si un conjunto contiene más vectores ({k}) que entradas en cada vector ({dim}) en ℝ{a_subindice(dim)} (p > n), "
            f"entonces el conjunto es linealmente dependiente porque siempre existen variables libres en el sistema homogéneo.\n\n"
            f"Relación de dependencia no trivial hallada:\n  {rel}"
        )
        return ResultadoIndependenciaLineal(
            es_linealmente_independiente=False,
            criterio_utilizado=f"Teorema p > n ({k} vectores en ℝ{a_subindice(dim)})",
            relacion_dependencia=rel,
            matriz_homogenea_inicial=matriz_homogenea,
            matriz_rref=matriz_rref,
            pasos_gauss=pasos,
            explicacion=explicacion
        )
    
    if k == 2:
        es_prop, escalar = son_proporcionales_2_vectores(vectores[0], vectores[1])
        if es_prop and escalar is not None:
            # v₁ = escalar·v₂  =>  v₁ - escalar·v₂ = 0; el signo depende del signo de escalar.
            k_str = formatear_numero(abs(escalar), modo)
            signo = "-" if escalar >= 0 else "+"
            rel = f"v₁ {signo} {k_str}·v₂ = 0"
            explicacion = (
                f"El conjunto es LINEALMENTE DEPENDIENTE por inspección de 2 vectores.\n"
                f"Teorema: Un conjunto de dos vectores es linealmente dependiente si y solo si al menos uno "
                f"de los vectores es múltiplo escalar del otro.\n"
                f"Aquí: v₁ = ({formatear_numero(escalar, modo)})·v₂.\n"
                f"Relación de dependencia lineal: {rel}"
            )
            return ResultadoIndependenciaLineal(
                es_linealmente_independiente=False,
                criterio_utilizado="Vectores Proporcionales (k = 2)",
                relacion_dependencia=rel,
                matriz_homogenea_inicial=matriz_homogenea,
                matriz_rref=matriz_rref,
                pasos_gauss=pasos,
                explicacion=explicacion
            )
    
    if isinstance(res, SolucionUnica):
        # Sin variables libres solo existe la solución trivial: L.I.
        sol_trivial_str = ", ".join([f"c{a_subindice(i+1)} = 0" for i in range(k)])
        explicacion = (
            "El conjunto de vectores es LINEALMENTE INDEPENDIENTE.\n"
            "Justificación algebraica: Al resolver la ecuación homogénea c₁v₁ + ... + cₖvₖ = 0̄ mediante Gauss-Jordan, "
            "se comprueba que cada columna contiene una posición pivote y no existen variables libres.\n"
            f"Por lo tanto, la ecuación solo admite la solución trivial:\n  {sol_trivial_str}."
        )
        return ResultadoIndependenciaLineal(
            es_linealmente_independiente=True,
            criterio_utilizado="Solución Trivial Única (Gauss-Jordan)",
            relacion_dependencia=None,
            matriz_homogenea_inicial=matriz_homogenea,
            matriz_rref=matriz_rref,
            pasos_gauss=pasos,
            explicacion=explicacion
        )
    else:
        # Variable libre => soluciones no triviales: L.D.
        rel = _generar_relacion_dependencia(sol_gen, k, modo)
        vars_libres_str = ", ".join([f"c{a_subindice(j+1)}" for j in res.variables_libres])
        explicacion = (
            "El conjunto de vectores es LINEALMENTE DEPENDIENTE.\n"
            "Justificación algebraica: El sistema homogéneo posee variables libres (" + vars_libres_str + "), "
            "lo que permite obtener infinitas soluciones no triviales para los escalares cᵢ.\n\n"
            "Una relación de dependencia lineal no trivial entre los vectores es:\n  " + rel
        )
        return ResultadoIndependenciaLineal(
            es_linealmente_independiente=False,
            criterio_utilizado=f"Variables Libres en RREF ({len(res.variables_libres)} variable(s) libre(s))",
            relacion_dependencia=rel,
            matriz_homogenea_inicial=matriz_homogenea,
            matriz_rref=matriz_rref,
            pasos_gauss=pasos,
            explicacion=explicacion
        )


def _generar_relacion_dependencia(sol_gen: Optional[SolucionGeneral], total_vars: int, modo: str = "fraccion") -> str:
    """Construye un texto con una relación no trivial c₁v₁ + ... + cₖvₖ = 0̄.

    Recibe la solución general y el número de variables; fija la primera libre en 1 y las demás en 0.
    """
    if not sol_gen or not sol_gen.variables_libres:
        return "c₁v₁ + ... + cₖvₖ = 0 (solución no trivial existente)"
    
    # Cualquier valor no nulo en una variable libre da una solución no trivial; se elige 1.
    var_libre_elegida = sol_gen.variables_libres[0]
    valores = {var_libre_elegida: 1.0}
    for vl in sol_gen.variables_libres[1:]:
        valores[vl] = 0.0
    
    coeficientes = [0.0] * total_vars
    coeficientes[var_libre_elegida] = 1.0
    
    for var_b, expr in sol_gen.variables_basicas.items():
        val = expr.constante
        for term in expr.terminos:
            val += term.coef * valores.get(term.var_libre_idx, 0.0)
        coeficientes[var_b] = round(val, 9)
    
    partes = []
    for i, c in enumerate(coeficientes):
        if abs(c) > 1e-10:
            c_str = formatear_numero(abs(c), modo)
            v_str = f"v{a_subindice(i+1)}"
            signo = "+" if c > 0 else "-"
            if abs(c - 1.0) < 1e-10:
                partes.append((signo, v_str))
            else:
                partes.append((signo, f"{c_str}·{v_str}"))
    
    if not partes:
        return "0 = 0"
    
    primer_signo, primer_termino = partes[0]
    res_str = primer_termino if primer_signo == "+" else f"-{primer_termino}"
    for sig, term in partes[1:]:
        res_str += f" {sig} {term}"
    
    return f"{res_str} = 0̄"
