# Guía Paso a Paso para el Examen de Álgebra con PyMatrix

Aquí tienes exactamente qué escribir en la calculadora y qué poner en papel para los tres ejercicios. No hay ninguna ecuación química oculta en este examen, todo es álgebra lineal pura.

---

## Ejercicio I: Propiedad Distributiva $A(u + v) = Au + Av$ (8 pts)

Este ejercicio requiere que escribas en papel el paso a paso. La calculadora de PyMatrix te dará todo el texto exacto que debes copiar.

### ¿Qué hacer en la calculadora?
1. Abre la calculadora gráfica (Opción 10 del menú de consola).
2. Ve a la pestaña **"Ax = b & Propiedades"**.
3. Baja hasta la sección **"Verificación de Propiedades (A, vectores, escalares)"**.
4. Configura las dimensiones:
   - Matriz A: **2** filas, **2** columnas.
   - Número de vectores ($k$): **2**.
   - Tamaño de vectores: **2** filas.
5. Ingresa los datos:
   - **Matriz A:**
     - Fila 1: `3`, `-2`
     - Fila 2: `4`, `1`
   - **Vectores:**
     - Vector 1 ($u$): `2`, `-1`
     - Vector 2 ($v$): `1`, `3`
6. Haz clic en el botón verde **`A(u + v) = Au + Av`**.
7. **En tu papel:** Copia exactamente el procedimiento de 5 pasos que te mostrará la pantalla negra a la derecha. La calculadora primero sumará $u+v$, luego lo multiplicará por $A$, luego calculará $Au$ y $Av$ por separado, los sumará, y concluirá que ambos lados de la ecuación dan como resultado `[22, 7]`.

---

## Ejercicio II: Escribir el sistema $Ax = b$ (10 pts)

Este ejercicio es puramente teórico, no necesitas la calculadora. Debes hacerlo **a mano en el papel**.

### ¿Qué escribir en el examen?
Te piden que identifiques las tres partes del sistema $3x_1 + 2x_2 - x_3 = 5$, etc. 
Copia esto textualmente en tu papel:

**1. Matriz de coeficientes ($A$):**
$$
A = \begin{bmatrix} 
3 & 2 & -1 \\ 
-1 & 0 & 4 \\ 
0 & 2 & 3 
\end{bmatrix}
$$
*(Ojo: en la segunda ecuación no hay $x_2$, por lo que ponemos un 0).*

**2. Vector incógnita ($x$):**
$$
x = \begin{bmatrix} 
x_1 \\ 
x_2 \\ 
x_3 
\end{bmatrix}
$$

**3. Vector de términos independientes ($b$):**
$$
b = \begin{bmatrix} 
5 \\ 
2 \\ 
-1 
\end{bmatrix}
$$

**4. Forma Matricial Final ($Ax = b$):**
$$
\begin{bmatrix} 
3 & 2 & -1 \\ 
-1 & 0 & 4 \\ 
0 & 2 & 3 
\end{bmatrix}
\begin{bmatrix} 
x_1 \\ 
x_2 \\ 
x_3 
\end{bmatrix}
=
\begin{bmatrix} 
5 \\ 
2 \\ 
-1 
\end{bmatrix}
$$

---

## Ejercicio III: Producto Matriz-Vector (12 pts)

### ¿Qué hacer en la calculadora? (Parte a)
1. Ve a la pestaña **"Ax = b & Propiedades"**.
2. En la primera sección superior (**"Producto Matriz-Vector (Ax) y Sistema Ax = b"**), configura:
   - Matriz A: **3** filas, **3** columnas.
   - Vector x/b: **3** filas.
3. Ingresa los valores:
   - **Matriz A:**
     - Fila 1: `1`, `2`, `0`
     - Fila 2: `-1`, `3`, `2`
     - Fila 3: `2`, `0`, `-1`
   - **Vector x:** `2`, `-1`, `3`
4. Haz clic en **"Calcular A·x"**.
5. **En tu examen (para el inciso a):** Escribe el resultado numérico que te arroja la app:
   $$b = \begin{bmatrix} 0 \\ 1 \\ 1 \end{bmatrix}$$

### Respuestas para b) y c) (Escribir en papel)
Copia esto en tu examen para ganar los puntos teóricos:

**b) Explica si el resultado puede expresarse como una combinación lineal de las columnas:**
> **Sí.** Por definición algebraica, el producto de una matriz por un vector columna siempre equivale a una combinación lineal de los vectores columna de dicha matriz, donde los escalares (pesos) son las componentes del vector por el que se multiplica.

**c) Escribe explícitamente esa combinación lineal:**
*(Aquí solo debes agarrar cada columna de $A$ y multiplicarla por los números de $v$).* Escribe lo siguiente:
$$
2 \begin{bmatrix} 1 \\ -1 \\ 2 \end{bmatrix} - 1 \begin{bmatrix} 2 \\ 3 \\ 0 \end{bmatrix} + 3 \begin{bmatrix} 0 \\ 2 \\ -1 \end{bmatrix} = \begin{bmatrix} 0 \\ 1 \\ 1 \end{bmatrix}
$$
