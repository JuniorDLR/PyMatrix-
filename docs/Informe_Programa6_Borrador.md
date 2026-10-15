# Informe Programa 6 — Grupo [número]

## Portada (completar)

Universidad Americana · Facultad de Ingeniería y Arquitectura · Álgebra Lineal (MTM0120)  
Programa 6: Factorización LU y solución de sistemas Ax=b  
Docente: [nombre] · Carrera: [carrera] · Grupo: [número]  
Integrantes: [nombres y apellidos] · Fecha: [fecha de entrega]

## Explicación algorítmica (texto para 1–2 páginas)

La solución se integró en la calculadora gráfica PyMatrix. El módulo `modulos/modulo_lu.py` expone funciones puras del núcleo `src/core/lu.py`, mientras que la vista `src/ui/lu_view.py` recibe matrices escritas o pegadas por el usuario, presenta las operaciones de fila y comparte el Banco de Matrices existente. No se creó un programa separado de consola. Se admiten matrices A de m×n con entradas enteras, decimales o fraccionarias; sus dimensiones se deducen del texto y los cálculos se realizan con `Fraction` para mantener exactitud.

Para obtener A=L·U, se inicia con L=Iₘ y U=A. En cada columna pivote se aplican únicamente reemplazos de fila hacia abajo. Si el pivote está en la fila j y se elimina la entrada de la fila i, el multiplicador es lᵢⱼ=Uᵢₖ/Uⱼₖ y la operación es Fᵢ←Fᵢ−lᵢⱼFⱼ. El multiplicador se guarda en L antes de modificar U. Así L queda triangular inferior con unos en su diagonal y U queda escalonada. Una columna sin entrada pivote se omite; si hay un cero en la posición pivote y una entrada no nula debajo que exigiría intercambio, se detiene la factorización y se informa que se requiere pivoteo parcial P·A=L·U. El programa no atribuye a una factorización sin permutaciones un resultado que no le corresponde.

Terminada la reducción, se usa el producto matricial ya disponible para calcular L·U y se compara cada entrada con A. El resultado y la comprobación se muestran junto con todos los multiplicadores y estados de L y U. El mismo procedimiento sirve para matrices rectangulares, con L de tamaño m×m y U de tamaño m×n.

Cuando A es cuadrada y U tiene todos sus pivotes diagonales no nulos, la ecuación Ax=b se transforma en L(Ux)=b. Primero se obtiene y resolviendo Ly=b por sustitución hacia adelante: yᵢ=(bᵢ−Σⱼ₌₁ⁱ⁻¹Lᵢⱼyⱼ)/Lᵢᵢ. La interfaz muestra la reducción de la matriz aumentada [L|b] hasta [I|y]. Luego se resuelve Ux=y por sustitución hacia atrás: xᵢ=(yᵢ−Σⱼ₌ᵢ₊₁ⁿUᵢⱼxⱼ)/Uᵢᵢ. Se muestra [U|y] hasta [I|x]. Finalmente se calcula A·x con la función matricial existente y se compara exactamente con b. Para matrices rectangulares o con un pivote diagonal nulo, se explica por qué este procedimiento no da una solución única.

Los resultados intermedios se pasan directamente de una función a otra: A→(L,U)→y→x→A·x. El usuario no vuelve a ingresar L, U ni y. El verificador de propiedades, accesible desde la interfaz y desde `teoremas/verificador_matrices.py`, calcula por separado ambos miembros de las igualdades solicitadas de transposición, operaciones, inversa y determinante. Valida dimensiones e invertibilidad, y comunica “Se cumple” o “No se cumple” cuando la igualdad está definida.

Como comprobación de clase puede usarse A=[[3,−7,−2],[−3,5,1],[6,−4,0]] y b=[−7,5,2]ᵀ. El programa obtiene L=[[1,0,0],[−1,1,0],[2,−5,1]], U=[[3,−7,−2],[0,−2,−1],[0,0,−1]], y=[−7,−2,6]ᵀ y x=[3,4,−6]ᵀ. Las verificaciones L·U=A y A·x=b son exactas.

## Evidencia de uso (opcional)

La guía pide portada y explicación algorítmica; no exige explícitamente capturas. Para la defensa individual conviene anexar dos capturas legibles: una factorización rectangular con L·U=A y una resolución cuadrada que muestre y, x y A·x=b. Una tercera captura del aviso de pivoteo, si hay espacio, demuestra el manejo correcto de un caso no aplicable. Las capturas no deben sustituir la explicación de 1–2 páginas.
