"""
Módulo de Álgebra Vectorial en ℝⁿ para PyMatrix.

Contiene la lógica matemática para:
1. Operaciones básicas con vectores (suma, resta, producto escalar, producto punto, norma).
2. Evaluación computacional de Combinación Lineal:
   Determina si un vector b es combinación lineal de {v₁, v₂, ..., vₖ}
   mediante el sistema aumentado [v₁ v₂ ... vₖ | b] resuelto con Gauss-Jordan.
3. Evaluación de Independencia / Dependencia Lineal:
   Aplica teoremas de inspección directa (vector cero, k > n, vectores proporcionales)
   y resuelve el sistema homogéneo [v₁ v₂ ... vₖ | 0] hallando la relación de dependencia si aplica.

RESTRICCIÓN DIDÁCTICA:
Implementado estrictamente con Python estándar (listas, bucles, condicionales).
Prohibido el uso de NumPy o SciPy.
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

# Alias de tipo para vector en ℝⁿ: lista de números flotantes
Vector = List[float]


# =========================================================================
# 1. OPERACIONES BÁSICAS CON VECTORES EN ℝⁿ
# =========================================================================

def validar_mismas_dimensiones(u: Vector, v: Vector, nombre_op: str = "operación") -> None:
    """Verifica que dos vectores pertenezcan al mismo espacio ℝⁿ.
    
    Procedimiento algebraico:
    La adición y sustracción vectorial solo están definidas para vectores del mismo orden.
    Si u ∈ ℝⁿ y v ∈ ℝᵐ con n ≠ m, la operación no está definida.
    
    Raises:
        ValueError: Si las dimensiones no coinciden o están vacíos.
    """
    if not u or not v:
        raise ValueError("Los vectores no pueden estar vacíos.")
    if len(u) != len(v):
        raise ValueError(
            f"Error de dimensión en {nombre_op}: El vector u tiene dimensión {len(u)} "
            f"y el vector v tiene dimensión {len(v)}. Ambos deben pertenecer al mismo ℝⁿ."
        )


def sumar_vectores(u: Vector, v: Vector) -> Vector:
    """Calcula la suma vectorial u + v en ℝⁿ.
    
    Procedimiento algebraico:
    (u + v)ᵢ = uᵢ + vᵢ  para todo i ∈ {1, 2, ..., n}.
    Se suman las entradas homólogas una a una.
    """
    validar_mismas_dimensiones(u, v, "suma de vectores")
    resultado: Vector = []
    for i in range(len(u)):
        resultado.append(round(u[i] + v[i], 9))
    return resultado


def restar_vectores(u: Vector, v: Vector) -> Vector:
    """Calcula la resta vectorial u - v en ℝⁿ.
    
    Procedimiento algebraico:
    u - v = u + (-1)·v.
    (u - v)ᵢ = uᵢ - vᵢ  para todo i ∈ {1, 2, ..., n}.
    """
    validar_mismas_dimensiones(u, v, "resta de vectores")
    resultado: Vector = []
    for i in range(len(u)):
        resultado.append(round(u[i] - v[i], 9))
    return resultado


def multiplicar_vector_escalar(c: float, v: Vector) -> Vector:
    """Calcula el múltiplo escalar c·v en ℝⁿ.
    
    Procedimiento algebraico:
    Dado c ∈ ℝ y v ∈ ℝⁿ:
    (c·v)ᵢ = c · vᵢ  para todo i ∈ {1, 2, ..., n}.
    Cada coordenada del vector se escala por el factor c.
    """
    if not v:
        raise ValueError("El vector no puede estar vacío.")
    resultado: Vector = []
    for componente in v:
        resultado.append(round(c * componente, 9))
    return resultado


def sumar_multiples_vectores(vectores: List[Vector]) -> Vector:
    """Calcula la suma acumulada de k vectores en ℝⁿ: v₁ + v₂ + ... + vₖ.
    
    Procedimiento algebraico:
    (v₁ + v₂ + ... + vₖ)ᵢ = ∑_{j=1}^{k} v_{j, i} para cada componente i.
    """
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
    """Calcula la resta sucesiva de k vectores en ℝⁿ: v₁ - v₂ - ... - vₖ.
    
    Procedimiento algebraico:
    (v₁ - v₂ - ... - vₖ)ᵢ = v_{1, i} - ∑_{j=2}^{k} v_{j, i}.
    """
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
    """Calcula la combinación lineal c₁v₁ + c₂v₂ + ... + cₖvₖ en ℝⁿ.
    
    Procedimiento algebraico:
    Cada vector vⱼ se escala por cⱼ y se suman las componentes correspondientes:
    (c₁v₁ + ... + cₖvₖ)ᵢ = ∑_{j=1}^{k} (cⱼ · v_{j, i}).
    """
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
    """Calcula el producto escalar (producto punto) u · v.
    
    Procedimiento algebraico:
    u · v = u₁v₁ + u₂v₂ + ... + uₙvₙ = ∑ (uᵢ · vᵢ).
    Regla fundamental utilizada en la regla fila-vector para Ax.
    """
    validar_mismas_dimensiones(u, v, "producto punto")
    suma = 0.0
    for i in range(len(u)):
        suma += u[i] * v[i]
    return round(suma, 9)


def norma_vector(v: Vector) -> float:
    """Calcula la norma euclidiana (magnitud o longitud) del vector ||v||.
    
    Procedimiento algebraico:
    ||v|| = √(v · v) = √(v₁² + v₂² + ... + vₙ²).
    Calculada usando operaciones estándar (raíz cuadrada con exponente 0.5 o math.sqrt).
    """
    if not v:
        raise ValueError("El vector no puede estar vacío.")
    suma_cuadrados = sum(x * x for x in v)
    return round(math.sqrt(suma_cuadrados), 6)


def son_proporcionales_2_vectores(u: Vector, v: Vector) -> Tuple[bool, Optional[float]]:
    """Verifica si dos vectores son múltiplos escalares el uno del otro (u = c·v o v = c·u).
    
    Procedimiento algebraico:
    En ℝⁿ, dos vectores {u, v} son linealmente dependientes si y solo si
    uno es múltiplo del otro (u = k·v).
    """
    validar_mismas_dimensiones(u, v, "proporcionalidad")
    # Caso vector nulo: siempre proporcional
    if all(abs(x) < 1e-10 for x in u) or all(abs(x) < 1e-10 for x in v):
        return True, 0.0
    
    escalar: Optional[float] = None
    for ui, vi in zip(u, v):
        if abs(vi) < 1e-10:
            if abs(ui) > 1e-10:
                return False, None
        else:
            k = ui / vi
            if escalar is None:
                escalar = k
            elif abs(k - escalar) > 1e-6:
                return False, None
    return True, escalar


# =========================================================================
# 2. COMBINACIÓN LINEAL EN ℝⁿ
# =========================================================================

@dataclass
class ResultadoCombinacionLineal:
    """Resultado del análisis de si un vector b es combinación lineal de {v₁, ..., vₖ}.
    
    Atributos:
        es_combinacion: True si el sistema es consistente (determinado o indeterminado).
        tipo_solucion: "Solución Única", "Infinitas Soluciones" o "Inconsistente".
        pesos: Lista de pesos c₁, c₂, ..., cₖ si la solución es única.
        solucion_general: Instancia con la parametrización si hay infinitas soluciones.
        matriz_aumentada_inicial: Matriz [v₁ v₂ ... vₖ | b].
        matriz_rref: Matriz final en RREF.
        pasos_gauss: Lista con los pasos de reducción.
        explicacion: Texto explicativo con la expresión algebraica obtenida.
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
    """Evalúa si el vector b puede generarse como combinación lineal del conjunto de vectores {v₁, ..., vₖ}.
    
    Procedimiento algebraico (Teorema de la Ecuación Vectorial):
    La ecuación vectorial:
        c₁v₁ + c₂v₂ + ... + cₖvₖ = b
    equivale al sistema lineal con matriz aumentada donde los vectores vᵢ
    forman las columnas y b forma el término independiente:
        [ v₁  v₂  ...  vₖ | b ]
    
    El vector b es combinación lineal si y solo si el sistema lineal es CONSISTENTE
    (posee solución única o infinitas soluciones). Si es inconsistente (0 = k con k ≠ 0),
    b NO es combinación lineal.
    """
    if not vectores:
        raise ValueError("Debe proporcionar al menos un vector en el conjunto generador.")
    
    dim = len(vectores[0])
    for idx, v in enumerate(vectores):
        if len(v) != dim:
            raise ValueError(f"El vector v{idx+1} tiene dimensión {len(v)}, pero se esperaba {dim}.")
    if len(b) != dim:
        raise ValueError(f"El vector objetivo b tiene dimensión {len(b)}, pero los vectores están en ℝ{a_subindice(dim)}.")
    
    k = len(vectores)  # Número de vectores (columnas de coeficientes)
    
    # Construcción de la matriz aumentada [v₁ v₂ ... vₖ | b] de dimensión dim x (k + 1)
    matriz_aum: Matriz = []
    for fila_idx in range(dim):
        fila = [vectores[col_idx][fila_idx] for col_idx in range(k)]
        fila.append(b[fila_idx])
        matriz_aum.append(fila)
    
    # Resolver mediante Gauss-Jordan implementado en src/core/gauss.py
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
        # Formatear la combinación explícita: b = c₁v₁ + c₂v₂ + ... + cₖvₖ
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
        
    else:  # SolucionInfinita
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


# =========================================================================
# 3. INDEPENDENCIA Y DEPENDENCIA LINEAL EN ℝⁿ
# =========================================================================

@dataclass
class ResultadoIndependenciaLineal:
    """Resultado del análisis de dependencia o independencia lineal de {v₁, ..., vₖ}.
    
    Atributos:
        es_linealmente_independiente: True si solo admite la solución trivial c₁=c₂=...=cₖ=0.
        criterio_utilizado: Descripción del teorema o reducción aplicada.
        relacion_dependencia: Si son L.D., ecuación no trivial c₁v₁ + ... + cₖvₖ = 0.
        matriz_homogenea_inicial: Matriz [v₁ v₂ ... vₖ | 0].
        matriz_rref: Matriz homogénea en RREF.
        pasos_gauss: Pasos de reducción.
        explicacion: Resumen teórico-algebraico del resultado.
    """
    es_linealmente_independiente: bool
    criterio_utilizado: str
    relacion_dependencia: Optional[str]
    matriz_homogenea_inicial: Matriz
    matriz_rref: Matriz
    pasos_gauss: List[PasoGauss]
    explicacion: str


def evaluar_independencia_lineal(vectores: List[Vector], modo: str = "fraccion") -> ResultadoIndependenciaLineal:
    """Determina si un conjunto de vectores {v₁, v₂, ..., vₖ} en ℝⁿ es Linealmente Independiente (L.I.) o Dependiente (L.D.).
    
    Procedimiento algebraico:
    1. Teoremas de Inspección Directa (Diapositivas de la asignatura):
       a. Si el conjunto contiene al vector cero 0̄, es LINEALMENTE DEPENDIENTE.
       b. Si el número de vectores k supera la dimensión n (k > n en ℝⁿ), es LINEALMENTE DEPENDIENTE
          (más incógnitas que ecuaciones garantizan al menos una variable libre).
       c. Si hay exactamente 2 vectores y uno es múltiplo escalar del otro, son LINEALMENTE DEPENDIENTES.
    
    2. Reducción Matricial General:
       Se plantea la ecuación homogénea c₁v₁ + c₂v₂ + ... + cₖvₖ = 0̄.
       Se construye la matriz aumentada [v₁ v₂ ... vₖ | 0] y se reduce mediante Gauss-Jordan.
       - Si NO hay variables libres: únicamente la solución trivial c₁ = c₂ = ... = cₖ = 0.
         Por tanto, los vectores son LINEALMENTE INDEPENDIENTES.
       - Si HAY variables libres: existen infinitas soluciones no triviales.
         Por tanto, los vectores son LINEALMENTE DEPENDIENTES.
         Se extrae una relación de dependencia explícita asignando un valor no nulo a la variable libre.
    """
    if not vectores:
        raise ValueError("Debe proporcionar al menos un vector para analizar.")
    
    k = len(vectores)       # Número de vectores
    dim = len(vectores[0])  # Dimensión n del espacio ℝⁿ
    
    for idx, v in enumerate(vectores):
        if len(v) != dim:
            raise ValueError(f"El vector v{idx+1} tiene dimensión {len(v)}, pero el primero tiene {dim}.")
    
    # -------------------------------------------------------------
    # Paso 0: Construcción de la matriz homogénea [v₁ ... vₖ | 0]
    # -------------------------------------------------------------
    matriz_homogenea: Matriz = []
    for r in range(dim):
        fila = [vectores[c][r] for c in range(k)]
        fila.append(0.0)
        matriz_homogenea.append(fila)
    
    pasos, res, sol_gen = resolver_gauss_jordan(matriz_homogenea)
    matriz_rref = sol_gen.matriz_rref if sol_gen else pasos[-1].matriz_estado
    
    # -------------------------------------------------------------
    # Inspección 1: Vector cero en el conjunto
    # -------------------------------------------------------------
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
    
    # -------------------------------------------------------------
    # Inspección 2: Más vectores que entradas (k > n en ℝⁿ)
    # -------------------------------------------------------------
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
    
    # -------------------------------------------------------------
    # Inspección 3: Conjunto de dos vectores proporcionales
    # -------------------------------------------------------------
    if k == 2:
        es_prop, escalar = son_proporcionales_2_vectores(vectores[0], vectores[1])
        if es_prop and escalar is not None:
            # v₁ = escalar · v₂  =>  v₁ - escalar·v₂ = 0
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
    
    # -------------------------------------------------------------
    # Criterio General: Solución del sistema homogéneo por Gauss-Jordan
    # -------------------------------------------------------------
    if isinstance(res, SolucionUnica):
        # Única solución trivial c₁ = c₂ = ... = cₖ = 0
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
        # Existen variables libres: Linealmente Dependiente
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
    """Calcula una relación no trivial explícita c₁v₁ + c₂v₂ + ... + cₖvₖ = 0.
    
    Procedimiento:
    Asigna un valor entero conveniente (ej. 1 o m.c.d.) a la primera variable libre
    y 0 a las demás si hubiera varias, calculando los valores exactos resultantes para las variables básicas.
    """
    if not sol_gen or not sol_gen.variables_libres:
        return "c₁v₁ + ... + cₖvₖ = 0 (solución no trivial existente)"
    
    # Asignamos valor 1.0 a la primera variable libre
    var_libre_elegida = sol_gen.variables_libres[0]
    valores = {var_libre_elegida: 1.0}
    for vl in sol_gen.variables_libres[1:]:
        valores[vl] = 0.0
    
    # Evaluamos cada variable básica
    coeficientes = [0.0] * total_vars
    coeficientes[var_libre_elegida] = 1.0
    
    for var_b, expr in sol_gen.variables_basicas.items():
        val = expr.constante
        for term in expr.terminos:
            val += term.coef * valores.get(term.var_libre_idx, 0.0)
        coeficientes[var_b] = round(val, 9)
    
    # Construir cadena c₁v₁ + c₂v₂ + ... = 0
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
    
    # Ensamblar quitando signo '+' inicial
    primer_signo, primer_termino = partes[0]
    res_str = primer_termino if primer_signo == "+" else f"-{primer_termino}"
    for sig, term in partes[1:]:
        res_str += f" {sig} {term}"
    
    return f"{res_str} = 0̄"
