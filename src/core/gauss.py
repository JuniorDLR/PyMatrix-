"""
Eliminación de Gauss y Gauss-Jordan con pivoteo parcial; detecta columnas pivote.
Clasifica el sistema (única, infinitas o sin solución) y genera los pasos de la reducción.
Tema de clase: sistemas de ecuaciones lineales, formas REF y RREF.
Elaborado por: Grupo x
"""
import copy
from .domain import (
    Matriz, PasoGauss, ResultadoSistema, 
    SolucionUnica, SolucionInfinita, SinSolucion,
    Termino, ExpresionParametrica, SolucionGeneral,
    formatear_fraccion
)


def copiar_matriz(m: Matriz) -> Matriz:
    """Devuelve una copia independiente de la matriz para no alterar la original."""
    return [fila[:] for fila in m]


def a_rref(matriz_ref: Matriz, columnas_pivote: list[int]) -> Matriz:
    """Convierte una matriz REF en RREF: pivotes a 1 y ceros sobre cada pivote.

    Recibe la matriz escalonada y las columnas pivote; devuelve una matriz nueva en RREF.
    """
    matriz = copiar_matriz(matriz_ref)
    filas = len(matriz)
    columnas = len(matriz[0]) if filas > 0 else 0
    num_vars = columnas - 1
    
    # Encontrar el par (fila, col) exacto donde cada columna pivote es la entrada principal
    pivotes: list[tuple[int, int]] = []
    for r in range(filas):
        for c in range(num_vars):
            if abs(matriz[r][c]) > 1e-10:
                if c in columnas_pivote:
                    pivotes.append((r, c))
                break
    
    # De abajo hacia arriba: así cada eliminación no deshace ceros ya logrados
    for pivot_row, pivot_col in reversed(pivotes):
        pivote_val = matriz[pivot_row][pivot_col]
        if abs(pivote_val - 1.0) > 1e-10 and abs(pivote_val) > 1e-10:
            for j in range(columnas):
                matriz[pivot_row][j] /= pivote_val
        matriz[pivot_row][pivot_col] = 1.0
        
        for r in range(filas):
            if r != pivot_row and abs(matriz[r][pivot_col]) > 1e-10:
                factor = matriz[r][pivot_col]
                for j in range(columnas):
                    matriz[r][j] -= factor * matriz[pivot_row][j]
                matriz[r][pivot_col] = 0.0
    
    return matriz


def extraer_variables(matriz_rref: Matriz) -> tuple[list[int], list[int]]:
    """Identifica variables básicas (columnas pivote) y libres de una matriz RREF.

    Devuelve la tupla (vars_basicas, vars_libres) con índices desde 0.
    """
    filas = len(matriz_rref)
    columnas = len(matriz_rref[0]) if filas > 0 else 0
    num_variables = columnas - 1
    
    columnas_pivote = []
    for r in range(filas):
        for c in range(num_variables):
            if abs(matriz_rref[r][c]) > 1e-10:
                if abs(matriz_rref[r][c] - 1.0) < 1e-10:
                    # Un pivote válido en RREF es 1 y el resto de su columna es 0
                    if all(abs(matriz_rref[rr][c]) < 1e-10 for rr in range(filas) if rr != r):
                        columnas_pivote.append(c)
                break  # Solo el primer no nulo de la fila puede ser pivote
    
    vars_basicas = sorted(columnas_pivote)
    vars_libres = [j for j in range(num_variables) if j not in columnas_pivote]
    
    return vars_basicas, vars_libres


def parametrizar(matriz_rref: Matriz, vars_basicas: list[int], vars_libres: list[int]) -> dict[int, ExpresionParametrica]:
    """Expresa cada variable básica en función de las libres, despejando desde la RREF.

    Devuelve {índice_variable: ExpresionParametrica} para todas las variables (básicas y libres).
    """
    filas = len(matriz_rref)
    columnas = len(matriz_rref[0]) if filas > 0 else 0
    num_variables = columnas - 1
    
    expresiones: dict[int, ExpresionParametrica] = {}
    
    for var_b in vars_basicas:
        fila_pivote = None
        for r in range(filas):
            # Es fila pivote si var_b es el primer no nulo de la fila r
            for c in range(num_variables):
                if abs(matriz_rref[r][c]) > 1e-10:
                    if c == var_b and abs(matriz_rref[r][c] - 1.0) < 1e-10:
                        fila_pivote = r
                    break
            if fila_pivote is not None:
                break
        
        if fila_pivote is None:
            expresiones[var_b] = ExpresionParametrica(0.0, ())
            continue
        
        const = matriz_rref[fila_pivote][-1]
        terminos = []
        
        # Signo negativo: al pasar x_libre al lado derecho cambia de signo
        for var_l in vars_libres:
            coef = -matriz_rref[fila_pivote][var_l]
            if abs(coef) > 1e-10:
                terminos.append(Termino(round(coef, 9), var_l))
        
        expresiones[var_b] = ExpresionParametrica(round(const, 9), tuple(terminos))
    
    # Una variable libre se representa a sí misma: x = 1·x
    for var_l in vars_libres:
        expresiones[var_l] = ExpresionParametrica(0.0, (Termino(1.0, var_l),))
    
    return expresiones


def resolver_gauss(matriz_inicial: Matriz) -> tuple[list[PasoGauss], ResultadoSistema, SolucionGeneral | None]:
    """Eliminación de Gauss (forma escalonada REF) y sustitución hacia atrás.

    Recibe la matriz aumentada m x (n+1); devuelve (pasos, clasificación del sistema, SolucionGeneral o None).
    """
    pasos: list[PasoGauss] = []
    matriz = copiar_matriz(matriz_inicial)
    filas = len(matriz)
    columnas = len(matriz[0]) if filas > 0 else 0
    
    pasos.append(PasoGauss("Matriz Aumentada Inicial", copiar_matriz(matriz)))
    
    # Se valida antes de operar: con matriz vacía no hay filas/columnas que indexar
    if filas == 0 or columnas == 0:
        return pasos, SinSolucion(mensaje="La matriz está vacía."), None
    
    pivote_fila = 0
    pivote_col = 0
    columnas_pivote: list[int] = []
    
    while pivote_fila < filas and pivote_col < columnas - 1:
        # Pivoteo parcial: el mayor valor absoluto como pivote reduce el error numérico
        max_fila = pivote_fila
        for i in range(pivote_fila + 1, filas):
            if abs(matriz[i][pivote_col]) > abs(matriz[max_fila][pivote_col]):
                max_fila = i
        
        # Sin pivote posible en esta columna (≈0): no hay pivote aquí, se pasa a la siguiente
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
        pivote_val = matriz[pivote_fila][pivote_col]
        for i in range(pivote_fila + 1, filas):
            factor = matriz[i][pivote_col] / pivote_val
            if abs(factor) > 1e-10:
                for j in range(pivote_col, columnas):
                    matriz[i][j] -= factor * matriz[pivote_fila][j]
                hubo_cambios = True
                
        if hubo_cambios:
            pasos.append(PasoGauss(
                f"Eliminación hacia abajo: Ceros bajo el pivote (Fila {pivote_fila+1}, Columna {pivote_col+1})", 
                copiar_matriz(matriz)
            ))
        
        columnas_pivote.append(pivote_col)
        pivote_fila += 1
        pivote_col += 1
    
    matriz_ref = copiar_matriz(matriz)
    pasos.append(PasoGauss(
        "Forma Escalonada por Filas (REF) - Escalera de Gauss alcanzada", 
        copiar_matriz(matriz_ref)
    ))
    
    # Una fila [0 ... 0 | k] con k ≠ 0 equivale a 0 = k: sistema inconsistente
    for i in range(filas):
        todo_cero = True
        for j in range(columnas - 1):
            if abs(matriz[i][j]) > 1e-10:
                todo_cero = False
                break
        if todo_cero and abs(matriz[i][-1]) > 1e-10:
            return pasos, SinSolucion(mensaje="El sistema no tiene solución (fila inconsistente 0 = k)."), None
    
    num_variables = columnas - 1
    filas_no_nulas = sum(1 for i in range(filas) 
                         if any(abs(matriz[i][j]) > 1e-10 for j in range(num_variables)))
    
    # La RREF solo se usa internamente para parametrizar la solución general
    matriz_rref = a_rref(matriz_ref, columnas_pivote)
    vars_basicas, vars_libres = extraer_variables(matriz_rref)
    expresiones = parametrizar(matriz_rref, vars_basicas, vars_libres)
    
    # Menos pivotes que variables: quedan variables libres (infinitas soluciones)
    if len(columnas_pivote) < num_variables or filas_no_nulas < num_variables:
        resultado_inf = SolucionInfinita(variables_libres=vars_libres)
        solucion_general = SolucionGeneral(
            tipo="Consistente Indeterminado",
            variables_basicas=expresiones,
            variables_libres=tuple(vars_libres),
            matriz_rref=matriz_rref,
            matriz_ref=matriz_ref
        )
        return pasos, resultado_inf, solucion_general
    
    # Pivote en cada variable: se despeja desde la última fila hacia arriba
    solucion = [0.0] * num_variables
    for i in range(num_variables - 1, -1, -1):
        suma = matriz[i][-1]
        for j in range(i + 1, num_variables):
            suma -= matriz[i][j] * solucion[j]
        
        pivote = matriz[i][i]
        # Se detiene si falta pivote: dividir entre ~0 no es válido
        if abs(pivote) < 1e-10:
            return pasos, SinSolucion(mensaje="El sistema no tiene solución única (pivote nulo en sustitución)."), None
        
        solucion[i] = suma / pivote
    
    # "+ 0.0" convierte -0.0 en 0.0 para que no se muestre "-0"
    solucion = [round(x, 9) + 0.0 for x in solucion]
    resultado_u = SolucionUnica(variables=solucion)
    
    solucion_general = SolucionGeneral(
        tipo="Consistente Determinado",
        variables_basicas=expresiones,
        variables_libres=tuple(vars_libres),
        matriz_rref=matriz_rref,
        matriz_ref=matriz_ref
    )
    return pasos, resultado_u, solucion_general


def resolver_gauss_jordan(matriz_inicial: Matriz) -> tuple[list[PasoGauss], ResultadoSistema, SolucionGeneral | None]:
    """Eliminación de Gauss-Jordan: REF hacia adelante, pivotes a 1 y ceros arriba (RREF).

    Recibe la matriz aumentada m x (n+1); devuelve (pasos, clasificación del sistema, SolucionGeneral o None).
    """
    pasos: list[PasoGauss] = []
    matriz = copiar_matriz(matriz_inicial)
    filas = len(matriz)
    columnas = len(matriz[0]) if filas > 0 else 0
    
    pasos.append(PasoGauss("Matriz Aumentada Inicial", copiar_matriz(matriz)))
    
    # Se valida antes de operar: con matriz vacía no hay filas/columnas que indexar
    if filas == 0 or columnas == 0:
        return pasos, SinSolucion(mensaje="La matriz está vacía."), None
    
    pivote_fila = 0
    pivote_col = 0
    pivotes_encontrados: list[tuple[int, int]] = []  # (fila, col)
    
    while pivote_fila < filas and pivote_col < columnas - 1:
        # Pivoteo parcial: el mayor valor absoluto como pivote reduce el error numérico
        max_fila = pivote_fila
        for i in range(pivote_fila + 1, filas):
            if abs(matriz[i][pivote_col]) > abs(matriz[max_fila][pivote_col]):
                max_fila = i
        
        # Sin pivote posible en esta columna (≈0): se pasa a la siguiente
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
        piv_val = matriz[pivote_fila][pivote_col]
        for i in range(pivote_fila + 1, filas):
            factor = matriz[i][pivote_col] / piv_val
            if abs(factor) > 1e-10:
                for j in range(pivote_col, columnas):
                    matriz[i][j] -= factor * matriz[pivote_fila][j]
                hubo_cambios = True
                
        if hubo_cambios:
            pasos.append(PasoGauss(
                f"Eliminación hacia abajo: Ceros bajo el pivote en Columna {pivote_col+1}", 
                copiar_matriz(matriz)
            ))
        
        pivotes_encontrados.append((pivote_fila, pivote_col))
        pivote_fila += 1
        pivote_col += 1
    
    matriz_ref = copiar_matriz(matriz)
    pasos.append(PasoGauss(
        "Forma Escalonada por Filas (REF) - Escalera de Gauss alcanzada", 
        copiar_matriz(matriz_ref)
    ))
    
    # Una fila [0 ... 0 | k] con k ≠ 0 equivale a 0 = k: se detiene antes de reducir más
    for i in range(filas):
        todo_cero = True
        for j in range(columnas - 1):
            if abs(matriz[i][j]) > 1e-10:
                todo_cero = False
                break
        if todo_cero and abs(matriz[i][-1]) > 1e-10:
            return pasos, SinSolucion(mensaje="El sistema no tiene solución (fila inconsistente 0 = k)."), None
    
    # De abajo hacia arriba: así cada eliminación no deshace ceros ya logrados
    for p_idx, (r_piv, c_piv) in enumerate(reversed(pivotes_encontrados)):
        pivote_val = matriz[r_piv][c_piv]
        
        if abs(pivote_val - 1.0) > 1e-10 and abs(pivote_val) > 1e-10:
            for j in range(columnas):
                matriz[r_piv][j] /= pivote_val
            matriz[r_piv][c_piv] = 1.0  # Evita residuos como 0.9999999999
            pasos.append(PasoGauss(
                f"Normalización: Fila {r_piv+1} dividida por su pivote ({formatear_fraccion(pivote_val)}) para obtener 1",
                copiar_matriz(matriz)
            ))
        elif abs(pivote_val - 1.0) <= 1e-10:
            matriz[r_piv][c_piv] = 1.0
        
        hubo_arriba = False
        for r_up in range(r_piv):
            factor = matriz[r_up][c_piv]
            if abs(factor) > 1e-10:
                for j in range(columnas):
                    matriz[r_up][j] -= factor * matriz[r_piv][j]
                matriz[r_up][c_piv] = 0.0  # Limpiar posible residuo flotante
                hubo_arriba = True
        
        if hubo_arriba:
            pasos.append(PasoGauss(
                f"Eliminación hacia arriba: Ceros sobre el pivote (Fila {r_piv+1}, Columna {c_piv+1})",
                copiar_matriz(matriz)
            ))
    
    matriz_rref = copiar_matriz(matriz)
    pasos.append(PasoGauss(
        "Forma Escalonada Reducida (RREF) - Gauss-Jordan Final", 
        copiar_matriz(matriz_rref)
    ))
    columnas_pivote = [c for (_, c) in pivotes_encontrados]
    num_variables = columnas - 1
    
    vars_basicas, vars_libres = extraer_variables(matriz_rref)
    expresiones = parametrizar(matriz_rref, vars_basicas, vars_libres)
    
    # Menos pivotes que variables: quedan variables libres (infinitas soluciones)
    filas_no_nulas = sum(1 for i in range(filas) 
                         if any(abs(matriz_rref[i][j]) > 1e-10 for j in range(num_variables)))
    
    if len(columnas_pivote) < num_variables or filas_no_nulas < num_variables:
        resultado_inf = SolucionInfinita(variables_libres=vars_libres)
        solucion_general = SolucionGeneral(
            tipo="Consistente Indeterminado",
            variables_basicas=expresiones,
            variables_libres=tuple(vars_libres),
            matriz_rref=matriz_rref,
            matriz_ref=matriz_ref
        )
        return pasos, resultado_inf, solucion_general
    
    # En RREF con pivote en cada variable, la solución es la última columna
    solucion = [0.0] * num_variables
    for r in range(min(filas, num_variables)):
        solucion[r] = round(matriz_rref[r][-1], 9) + 0.0
    
    resultado_u = SolucionUnica(variables=solucion)
    solucion_general = SolucionGeneral(
        tipo="Consistente Determinado",
        variables_basicas=expresiones,
        variables_libres=tuple(vars_libres),
        matriz_rref=matriz_rref,
        matriz_ref=matriz_ref
    )
    return pasos, resultado_u, solucion_general


def verificar_solucion(matriz_original: Matriz, solucion: list[float]) -> bool:
    """Devuelve True si la solución satisface todas las ecuaciones de la matriz original."""
    # Tolerancia 1e-3 en vez de ==: la solución viene redondeada y el float acumula error
    for fila in matriz_original:
        suma = 0.0
        for j in range(len(solucion)):
            suma += fila[j] * solucion[j]
        if abs(suma - fila[-1]) > 1e-3:
            return False
    return True