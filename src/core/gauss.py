import copy
from .domain import (
    Matriz, PasoGauss, ResultadoSistema, 
    SolucionUnica, SolucionInfinita, SinSolucion,
    Termino, ExpresionParametrica, SolucionGeneral
)


def copiar_matriz(m: Matriz) -> Matriz:
    """Copia profunda de una matriz (lista de listas) para inmutabilidad."""
    return [fila[:] for fila in m]


def a_rref(matriz_ref: Matriz, columnas_pivote: list[int]) -> Matriz:
    """Paso 5 del algoritmo Gauss-Jordan: Forma Escalonada Reducida (RREF).
    
    Transforma una matriz en REF (ceros abajo) a RREF:
    1. Normaliza cada pivote a 1 (divide la fila por el pivote)
    2. Elimina hacia ARRIBA: hace ceros sobre cada pivote
    
    Args:
        matriz_ref: Matriz en Forma Escalonada (REF) - ceros debajo de pivotes
        columnas_pivote: Lista de índices de columna donde hay pivotes
        
    Returns:
        Nueva matriz en RREF (pivotes=1, ceros arriba y abajo)
    """
    matriz = copiar_matriz(matriz_ref)
    filas = len(matriz)
    columnas = len(matriz[0]) if filas > 0 else 0
    
    # Procesar pivotes de derecha a izquierda (hacia arriba)
    for pivot_col in reversed(columnas_pivote):
        # Encontrar la fila que tiene el pivote en esta columna
        pivot_row = None
        for r in range(filas):
            if abs(matriz[r][pivot_col]) > 1e-10:
                pivot_row = r
                break
        
        if pivot_row is None:
            continue
        
        # 1. Normalizar pivote a 1
        pivote_val = matriz[pivot_row][pivot_col]
        if abs(pivote_val - 1.0) > 1e-10:
            for j in range(columnas):
                matriz[pivot_row][j] /= pivote_val
        
        # 2. Eliminar hacia arriba: ceros en TODAS las demás filas
        for r in range(filas):
            if r != pivot_row and abs(matriz[r][pivot_col]) > 1e-10:
                factor = matriz[r][pivot_col]
                for j in range(columnas):
                    matriz[r][j] -= factor * matriz[pivot_row][j]
    
    return matriz


def extraer_variables(matriz_rref: Matriz) -> tuple[list[int], list[int]]:
    """Identifica variables básicas y libres desde una matriz en RREF.
    
    En RREF, una variable es BÁSICA si su columna es:
    - Un vector canónico (1 en una fila, 0 en todas las demás)
    Esa fila es la "fila pivote" de esa variable.
    
    Las variables NO básicas son LIBRES (parámetros).
    
    Args:
        matriz_rref: Matriz en Forma Escalonada Reducida
        
    Returns:
        Tupla (vars_basicas_idx, vars_libres_idx) - índices 0-based
    """
    filas = len(matriz_rref)
    columnas = len(matriz_rref[0]) if filas > 0 else 0
    num_variables = columnas - 1  # Excluir columna de términos independientes
    
    columnas_pivote = []
    for r in range(filas):
        for c in range(num_variables):
            # Buscar entradas que sean 1 (candidato a pivote)
            if abs(matriz_rref[r][c] - 1.0) < 1e-10:
                # Verificar que sea vector canónico: ceros en todas las demás filas
                es_pivote = True
                for rr in range(filas):
                    if rr != r and abs(matriz_rref[rr][c]) > 1e-10:
                        es_pivote = False
                        break
                if es_pivote:
                    columnas_pivote.append(c)
                break  # Solo una columna pivote por fila
    
    vars_basicas = sorted(columnas_pivote)
    vars_libres = [j for j in range(num_variables) if j not in columnas_pivote]
    
    return vars_basicas, vars_libres


def parametrizar(matriz_rref: Matriz, vars_basicas: list[int], vars_libres: list[int]) -> dict[int, ExpresionParametrica]:
    """Construye la solución parametrizada: cada variable básica = f(variables libres).
    
    En RREF, cada fila pivote tiene la forma:
        x_basica + sum(coef * x_libre) = termino_independiente
    Despejando:
        x_basica = termino_independiente - sum(coef * x_libre)
    
    Args:
        matriz_rref: Matriz en RREF
        vars_basicas: Índices de variables básicas
        vars_libres: Índices de variables libres
        
    Returns:
        Dict {idx_variable: ExpresionParametrica} para TODAS las variables
        (básicas con su expresión, libres como identidad: x = 1*x)
    """
    filas = len(matriz_rref)
    columnas = len(matriz_rref[0]) if filas > 0 else 0
    
    expresiones = {}
    
    # Variables básicas: leer desde su fila pivote
    for var_b in vars_basicas:
        fila_pivote = None
        for r in range(filas):
            if abs(matriz_rref[r][var_b] - 1.0) < 1e-10:
                # Verificar que sea fila pivote (vector canónico)
                es_pivote = True
                for c in range(columnas - 1):
                    if c != var_b and abs(matriz_rref[r][c]) > 1e-10:
                        es_pivote = False
                        break
                if es_pivote:
                    fila_pivote = r
                    break
        
        if fila_pivote is None:
            expresiones[var_b] = ExpresionParametrica(0.0, ())
            continue
        
        # Término independiente = última columna de la fila pivote
        const = matriz_rref[fila_pivote][-1]
        terminos = []
        
        # Coeficientes de variables libres (con signo negativo al despejar)
        for var_l in vars_libres:
            coef = -matriz_rref[fila_pivote][var_l]
            if abs(coef) > 1e-10:
                terminos.append(Termino(round(coef, 4), var_l))
        
        expresiones[var_b] = ExpresionParametrica(round(const, 4), tuple(terminos))
    
    # Variables libres: identidad x = 1*x
    for var_l in vars_libres:
        expresiones[var_l] = ExpresionParametrica(0.0, (Termino(1.0, var_l),))
    
    return expresiones


def resolver_gauss(matriz_inicial: Matriz, return_rref: bool = False):
    """Algoritmo completo Gauss-Jordan con clasificación de sistemas.
    
    Fases:
    1. Eliminación hacia adelante (REF): pivoteo parcial + ceros debajo
    2. Clasificación: inconsistente / único / infinitas
    3. (Opcional) RREF + parametrización si return_rref=True
    
    Args:
        matriz_inicial: Matriz aumentada m x (n+1)
        return_rref: Si True, retorna también SolucionGeneral con RREF
        
    Returns:
        Si return_rref=False: (pasos, ResultadoSistema)
        Si return_rref=True:  (pasos, ResultadoSistema, SolucionGeneral|None)
    """
    pasos = []
    matriz = copiar_matriz(matriz_inicial)
    filas = len(matriz)
    columnas = len(matriz[0]) if filas > 0 else 0
    
    # Paso 0: Matriz inicial
    pasos.append(PasoGauss("Matriz Aumentada Inicial", copiar_matriz(matriz)))
    
    if filas == 0 or columnas == 0:
        if return_rref:
            return pasos, SinSolucion(), None
        return pasos, SinSolucion()
    
    # === FASE 1: ELIMINACIÓN HACIA ADELANTE (REF) ===
    pivote_fila = 0
    pivote_col = 0
    columnas_pivote = []  # Columnas donde se encontraron pivotes
    
    while pivote_fila < filas and pivote_col < columnas - 1:
        # Pivoteo parcial: buscar máximo en columna actual (estabilidad numérica)
        max_fila = pivote_fila
        for i in range(pivote_fila + 1, filas):
            if abs(matriz[i][pivote_col]) > abs(matriz[max_fila][pivote_col]):
                max_fila = i
        
        # Columna casi nula → no hay pivote aquí, avanzar columna
        if abs(matriz[max_fila][pivote_col]) < 1e-10:
            pivote_col += 1
            continue
            
        # Intercambiar filas si el máximo no está en la fila actual
        if max_fila != pivote_fila:
            matriz[pivote_fila], matriz[max_fila] = matriz[max_fila], matriz[pivote_fila]
            pasos.append(PasoGauss(
                f"Pivoteo: Intercambio de fila {pivote_fila+1} con fila {max_fila+1}", 
                copiar_matriz(matriz)
            ))
        
        # Hacer ceros DEBAJO del pivote (eliminación gaussiana clásica)
        hubo_cambios = False
        for i in range(pivote_fila + 1, filas):
            factor = matriz[i][pivote_col] / matriz[pivote_fila][pivote_col]
            if abs(factor) > 1e-10:
                for j in range(pivote_col, columnas):
                    matriz[i][j] -= factor * matriz[pivote_fila][j]
                hubo_cambios = True
                
        if hubo_cambios:
            pasos.append(PasoGauss(
                f"Eliminación: Ceros generados usando la fila {pivote_fila+1} como pivote", 
                copiar_matriz(matriz)
            ))
        
        columnas_pivote.append(pivote_col)
        pivote_fila += 1
        pivote_col += 1
    
    # === FASE 2: CLASIFICACIÓN DEL SISTEMA (teorema existencia/unicidad) ===
    
    # 1. INCONSISTENTE: fila [0 0 ... 0 | k] con k ≠ 0
    for i in range(filas):
        todo_cero = True
        for j in range(columnas - 1):
            if abs(matriz[i][j]) > 1e-10:
                todo_cero = False
                break
        if todo_cero and abs(matriz[i][-1]) > 1e-10:
            if return_rref:
                return pasos, SinSolucion(), None
            return pasos, SinSolucion()
    
    num_variables = columnas - 1
    filas_no_nulas = sum(1 for i in range(filas) 
                         if any(abs(matriz[i][j]) > 1e-10 for j in range(num_variables)))
    
    # 2. INFINITAS SOLUCIONES: hay variables libres (columnas sin pivote)
    if len(columnas_pivote) < num_variables or filas_no_nulas < num_variables:
        vars_libres = [j for j in range(num_variables) if j not in columnas_pivote]
        resultado = SolucionInfinita(variables_libres=vars_libres)
        
        if return_rref:
            # Completar a RREF y parametrizar
            matriz_rref = a_rref(matriz, columnas_pivote)
            vars_basicas, vars_libres_rref = extraer_variables(matriz_rref)
            expresiones = parametrizar(matriz_rref, vars_basicas, vars_libres_rref)
            
            solucion_general = SolucionGeneral(
                tipo="Consistente Indeterminado",
                variables_basicas=expresiones,
                variables_libres=tuple(vars_libres_rref),
                matriz_rref=matriz_rref,
                matriz_ref=copiar_matriz(matriz)
            )
            return pasos, resultado, solucion_general
        
        return pasos, resultado
    
    # 3. SOLUCIÓN ÚNICA: sustitución hacia atrás (matriz ya es triangular superior)
    solucion = [0.0] * num_variables
    for i in range(num_variables - 1, -1, -1):
        suma = matriz[i][-1]
        for j in range(i + 1, num_variables):
            suma -= matriz[i][j] * solucion[j]
        
        pivote = matriz[i][i]
        if abs(pivote) < 1e-10:
            if return_rref:
                return pasos, SinSolucion(), None
            return pasos, SinSolucion()
        
        solucion[i] = suma / pivote
    
    # Redondear y corregir -0.0
    solucion = [round(x, 4) + 0.0 for x in solucion]
    resultado = SolucionUnica(variables=solucion)
    
    if return_rref:
        # Generar RREF y parametrización también para caso único
        matriz_rref = a_rref(matriz, columnas_pivote)
        vars_basicas, vars_libres_rref = extraer_variables(matriz_rref)
        expresiones = parametrizar(matriz_rref, vars_basicas, vars_libres_rref)
        
        solucion_general = SolucionGeneral(
            tipo="Consistente Determinado",
            variables_basicas=expresiones,
            variables_libres=tuple(vars_libres_rref),
            matriz_rref=matriz_rref,
            matriz_ref=copiar_matriz(matriz)
        )
        return pasos, resultado, solucion_general
    
    return pasos, resultado


def verificar_solucion(matriz_original: Matriz, solucion: list[float]) -> bool:
    """Verifica si una solución cumple el sistema original (compensa error flotante).
    
    Sustituye cada variable en las ecuaciones originales y compara LHS vs RHS
    con tolerancia 1e-3.
    """
    for fila in matriz_original:
        suma = 0.0
        for j in range(len(solucion)):
            suma += fila[j] * solucion[j]
        if abs(suma - fila[-1]) > 1e-3:
            return False
    return True