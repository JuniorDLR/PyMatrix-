import copy
from .domain import Matriz, PasoGauss, ResultadoSistema, SolucionUnica, SolucionInfinita, SinSolucion

def copiar_matriz(m: Matriz) -> Matriz:
    """Devuelve una copia profunda de la matriz usando listas por comprensión."""
    return [fila[:] for fila in m]

def resolver_gauss(matriz_inicial: Matriz) -> tuple[list[PasoGauss], ResultadoSistema]:
    """
    Realiza la eliminación por filas de Gauss y devuelve los pasos intermedios y el resultado.
    """
    pasos = []
    matriz = copiar_matriz(matriz_inicial)
    filas = len(matriz)
    columnas = len(matriz[0]) if filas > 0 else 0
    
    pasos.append(PasoGauss("Matriz Aumentada Inicial", copiar_matriz(matriz)))
    
    if filas == 0 or columnas == 0:
        return pasos, SinSolucion()
    
    # Eliminación hacia adelante (hacer ceros debajo de la diagonal principal)
    pivote_fila = 0
    pivote_col = 0
    
    while pivote_fila < filas and pivote_col < columnas - 1:
        # Buscar el pivote máximo en la columna actual
        max_fila = pivote_fila
        for i in range(pivote_fila + 1, filas):
            if abs(matriz[i][pivote_col]) > abs(matriz[max_fila][pivote_col]):
                max_fila = i
        
        # Si el mayor es casi 0, no hay pivote en esta columna (pasamos a la siguiente)
        if abs(matriz[max_fila][pivote_col]) < 1e-10:
            pivote_col += 1
            continue
            
        # Intercambiar la fila actual con la del pivote máximo (si es diferente)
        if max_fila != pivote_fila:
            matriz[pivote_fila], matriz[max_fila] = matriz[max_fila], matriz[pivote_fila]
            pasos.append(PasoGauss(
                f"Pivoteo: Intercambio de fila {pivote_fila+1} con fila {max_fila+1}", 
                copiar_matriz(matriz)
            ))
        
        # Hacer ceros en todas las filas debajo del pivote
        hubo_cambios = False
        for i in range(pivote_fila + 1, filas):
            factor = matriz[i][pivote_col] / matriz[pivote_fila][pivote_col]
            if abs(factor) > 1e-10:
                # Restamos el factor multiplicado por la fila del pivote
                for j in range(pivote_col, columnas):
                    matriz[i][j] -= factor * matriz[pivote_fila][j]
                hubo_cambios = True
                
        if hubo_cambios:
            pasos.append(PasoGauss(
                f"Eliminación: Ceros generados usando la fila {pivote_fila+1} como pivote", 
                copiar_matriz(matriz)
            ))
            
        pivote_fila += 1
        pivote_col += 1
        
    # --- Clasificación del Sistema ---
    
    # 1. Comprobar Inconsistencia: una fila tiene puros 0s en variables, pero un término independiente no nulo
    for i in range(filas):
        todo_cero = True
        for j in range(columnas - 1):
            if abs(matriz[i][j]) > 1e-10:
                todo_cero = False
                break
        if todo_cero and abs(matriz[i][-1]) > 1e-10:
            return pasos, SinSolucion()
            
    # 2. Comprobar Infinitas Soluciones (Consistente Indeterminado)
    # Ocurre si hay más variables que ecuaciones válidas, o al menos una columna no tiene pivote
    columnas_pivote = set()
    filas_no_nulas = 0
    for i in range(filas):
        todo_cero = True
        for j in range(columnas - 1):
            if abs(matriz[i][j]) > 1e-10:
                columnas_pivote.add(j)
                todo_cero = False
                break
        if not todo_cero:
            filas_no_nulas += 1
            
    num_variables = columnas - 1
    if len(columnas_pivote) < num_variables or filas_no_nulas < num_variables:
        vars_libres = [j for j in range(num_variables) if j not in columnas_pivote]
        return pasos, SolucionInfinita(variables_libres=vars_libres)
        
    # 3. Sustitución hacia atrás (Consistente Determinado / Única)
    # Empezamos desde la última ecuación válida hacia la primera
    solucion = [0.0] * num_variables
    for i in range(num_variables - 1, -1, -1):
        suma = matriz[i][-1]
        for j in range(i + 1, num_variables):
            suma -= matriz[i][j] * solucion[j]
        
        # Evitar divisiones por ceros extremadamente pequeños que puedan surgir por flotantes
        pivote = matriz[i][i]
        if abs(pivote) < 1e-10:
             return pasos, SinSolucion() # Ocurre en casos anómalos de flotantes
             
        solucion[i] = suma / pivote
        
    # Redondear y arreglar -0.0
    solucion = [round(x, 4) + 0.0 for x in solucion]
        
    return pasos, SolucionUnica(variables=solucion)

def verificar_solucion(matriz_original: Matriz, solucion: list[float]) -> bool:
    """
    Sustituye la lista de soluciones en el sistema de ecuaciones original para verificar la igualdad.
    Retorna True si todas las ecuaciones se cumplen con tolerancia.
    """
    for fila in matriz_original:
        suma = 0.0
        for j in range(len(solucion)):
            suma += fila[j] * solucion[j]
        # Evaluamos con una tolerancia para compensar el error de punto flotante
        if abs(suma - fila[-1]) > 1e-3:
            return False
    return True
