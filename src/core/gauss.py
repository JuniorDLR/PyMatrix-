import copy
from .domain import Matriz, PasoGauss, ResultadoSistema, SolucionUnica, SolucionInfinita, SinSolucion, Termino, ExpresionParametrica, SolucionGeneral


def copiar_matriz(m: Matriz) -> Matriz:
    return [fila[:] for fila in m]


def a_rref(matriz_ref: Matriz, columnas_pivote: list[int]) -> Matriz:
    """Paso 5: Ceros arriba + normalizar pivotes a 1 (RREF). Inmutable."""
    matriz = copiar_matriz(matriz_ref)
    filas = len(matriz)
    columnas = len(matriz[0]) if filas > 0 else 0
    
    for pivot_col in reversed(columnas_pivote):
        pivot_row = None
        for r in range(filas):
            if abs(matriz[r][pivot_col]) > 1e-10:
                pivot_row = r
                break
        
        if pivot_row is None:
            continue
        
        pivote_val = matriz[pivot_row][pivot_col]
        if abs(pivote_val - 1.0) > 1e-10:
            for j in range(columnas):
                matriz[pivot_row][j] /= pivote_val
        
        for r in range(filas):
            if r != pivot_row and abs(matriz[r][pivot_col]) > 1e-10:
                factor = matriz[r][pivot_col]
                for j in range(columnas):
                    matriz[r][j] -= factor * matriz[pivot_row][j]
    
    return matriz


def extraer_variables(matriz_rref: Matriz) -> tuple[list[int], list[int]]:
    """Retorna (vars_basicas_idx, vars_libres_idx) desde RREF."""
    filas = len(matriz_rref)
    columnas = len(matriz_rref[0]) if filas > 0 else 0
    num_variables = columnas - 1
    
    columnas_pivote = []
    for r in range(filas):
        for c in range(num_variables):
            if abs(matriz_rref[r][c] - 1.0) < 1e-10:
                es_pivote = True
                for rr in range(filas):
                    if rr != r and abs(matriz_rref[rr][c]) > 1e-10:
                        es_pivote = False
                        break
                if es_pivote:
                    columnas_pivote.append(c)
                break
    
    vars_basicas = sorted(columnas_pivote)
    vars_libres = [j for j in range(num_variables) if j not in columnas_pivote]
    
    return vars_basicas, vars_libres


def parametrizar(matriz_rref: Matriz, vars_basicas: list[int], vars_libres: list[int]) -> dict[int, ExpresionParametrica]:
    """Construye expresiones: x_basica = const + sum(coef * x_libre)."""
    filas = len(matriz_rref)
    columnas = len(matriz_rref[0]) if filas > 0 else 0
    
    expresiones = {}
    
    for var_b in vars_basicas:
        fila_pivote = None
        for r in range(filas):
            if abs(matriz_rref[r][var_b] - 1.0) < 1e-10:
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
        
        const = matriz_rref[fila_pivote][-1]
        terminos = []
        
        for var_l in vars_libres:
            coef = -matriz_rref[fila_pivote][var_l]
            if abs(coef) > 1e-10:
                terminos.append(Termino(round(coef, 4), var_l))
        
        expresiones[var_b] = ExpresionParametrica(round(const, 4), tuple(terminos))
    
    for var_l in vars_libres:
        expresiones[var_l] = ExpresionParametrica(0.0, (Termino(1.0, var_l),))
    
    return expresiones


def resolver_gauss(matriz_inicial: Matriz, return_rref: bool = False):
    """
    Realiza la eliminación por filas de Gauss y devuelve los pasos intermedios y el resultado.
    Si return_rref=True, retorna también la SolucionGeneral con RREF y parametrización.
    """
    pasos = []
    matriz = copiar_matriz(matriz_inicial)
    filas = len(matriz)
    columnas = len(matriz[0]) if filas > 0 else 0
    
    pasos.append(PasoGauss("Matriz Aumentada Inicial", copiar_matriz(matriz)))
    
    if filas == 0 or columnas == 0:
        if return_rref:
            return pasos, SinSolucion(), None
        return pasos, SinSolucion()
    
    pivote_fila = 0
    pivote_col = 0
    columnas_pivote = []
    
    while pivote_fila < filas and pivote_col < columnas - 1:
        max_fila = pivote_fila
        for i in range(pivote_fila + 1, filas):
            if abs(matriz[i][pivote_col]) > abs(matriz[max_fila][pivote_col]):
                max_fila = i
        
        if abs(matriz[max_fila][pivote_col]) < 1e-10:
            pivote_col += 1
            continue
            
        if max_fila != pivote_fila:
            matriz[pivote_fila], matriz[max_fila] = matriz[max_fila], matriz[pivote_fila]
            pasos.append(PasoGauss(
                f"Pivoteo: Intercambio de fila {pivote_fila+1} con fila {max_fila+1}", 
                copiar_matriz(matriz)
            ))
        
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
    filas_no_nulas = sum(1 for i in range(filas) if any(abs(matriz[i][j]) > 1e-10 for j in range(num_variables)))
    
    if len(columnas_pivote) < num_variables or filas_no_nulas < num_variables:
        vars_libres = [j for j in range(num_variables) if j not in columnas_pivote]
        resultado = SolucionInfinita(variables_libres=vars_libres)
        
        if return_rref:
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
    
    solucion = [round(x, 4) + 0.0 for x in solucion]
    resultado = SolucionUnica(variables=solucion)
    
    if return_rref:
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
    for fila in matriz_original:
        suma = 0.0
        for j in range(len(solucion)):
            suma += fila[j] * solucion[j]
        if abs(suma - fila[-1]) > 1e-3:
            return False
    return True