# 🚀 Guía Explicativa: Flujo, Uso y Algoritmos del Programa 3 (PyMatrix v3.0)

---

## 1. 📌 Los Nuevos Módulos y sus Funciones

El programa se expandió integrando dos grandes módulos accesibles desde la barra superior de navegación:

```text
[ MÓDULO: ]  [ 🔢 Sistemas Gauss/Jordan ]  [ ↗ Vectores en ℝⁿ ]  [ ✖ Operaciones Matriciales ]
```

---

### ↗️ Módulo 1: Vectores en $\mathbb{R}^n$
Diseñado para trabajar con vectores de $n$ componentes. Contiene 3 sub-pestañas:

1. **➕ Operaciones Básicas:**
   - **Suma y Resta ($\vec{u} \pm \vec{v}$):** Suma o resta componente a componente.
   - **Producto por Escalar ($c \cdot \vec{u}$ / $c \cdot \vec{v}$):** Multiplica cada componente por un número constante.
   - **Producto Punto ($\vec{u} \cdot \vec{v}$):** Suma el producto de componentes correspondientes, retornando un número escalar.
   - **Norma / Longitud ($\|\vec{u}\|$, $\|\vec{v}\|$):** Calcula la magnitud del vector ($\sqrt{v_1^2 + \dots + v_n^2}$).

2. **🔗 Combinación Lineal:**
   - Evalúa si un vector objetivo $\vec{b}$ se puede formar sumando múltiplos de un conjunto de vectores $\{\vec{v}_1, \vec{v}_2, \dots, \vec{v}_k\}$.
   - Determina si existen los pesos $c_1, c_2, \dots, c_k$ tales que $c_1 \vec{v}_1 + \dots + c_k \vec{v}_k = \vec{b}$.

3. **⚖️ Independencia Lineal (L.I. / L.D.):**
   - Evalúa si los vectores son independientes (ninguno depende de los demás) o dependientes (al menos uno se puede expresar en función de los otros).
   - Si son **Linealmente Dependientes (L.D.)**, el programa genera la **relación de dependencia no trivial** (ejemplo: $2\vec{v}_1 - 3\vec{v}_2 + \vec{v}_3 = \vec{0}$).

---

### ✖️ Módulo 2: Operaciones Matriciales y $Ax = b$
Diseñado para álgebra matricial avanzada. Contiene 2 sub-pestañas:

1. **➕➖✖️ Operaciones con Matrices:**
   - **Suma y Resta ($A \pm B$):** Operaciones posición a posición entre matrices del mismo tamaño.
   - **Multiplicación por Escalar ($c \cdot A$, $c \cdot B$):** Escala todos los elementos de la matriz.
   - **Multiplicación Matricial ($A \cdot B$):** Producto fila por columna entre matriz $A_{m \times n}$ y $B_{n \times p}$, mostrando el desglose algebraico de cada celda.

2. **📐 Ecuación Matricial ($A \cdot x = b$):**
   - **Calcular $A \cdot x$:** Realiza el producto matriz-vector de dos formas: por producto punto de filas y como combinación lineal de las columnas de $A$.
   - **Resolver $A x = b$:** Plantea el sistema matricial completo y encuentra el vector $x$ desconocido.

---

---

## 2. 🕹️ Paso a Paso: Cómo Interactuar con el Programa

### 🔵 Para trabajar con Vectores:
1. **Seleccionar el Módulo:** Haz clic en el botón superior **`↗ Vectores en ℝⁿ`**.
2. **Elegir la Operación:** Selecciona la sub-pestaña deseada (*Operaciones Básicas*, *Combinación Lineal* o *Independencia Lineal*).
3. **Definir Dimensiones:**
   - Ingresa la dimensión $n$ (ej. $3$ para $\mathbb{R}^3$) y la cantidad de vectores $k$.
   - Haz clic en **`Generar`** para crear las casillas de entrada.
4. **Ingresar Datos (o usar Ejemplo):**
   - Puedes escribir fracciones (ej. `3/2`) o decimales directamente.
   - O presionar **`🎲 Ejemplo`** para cargar datos reales de las diapositivas de clase.
5. **Calcular y Revisar:**
   - Presiona el botón de acción (ej. **`🔍 Evaluar Combinación Lineal`**).
   - En el panel derecho de la pantalla aparecerá la respuesta final resaltada con su **explicación algebraico paso a paso**.

---

### 🟣 Para trabajar con Operaciones Matriciales:
1. **Seleccionar el Módulo:** Haz clic en el botón superior **`✖ Operaciones Matriciales`**.
2. **Elegir la Operación:** Entra en *Operaciones con Matrices* o en *Ax = b*.
3. **Establecer Tamaños:** Define filas $m$ y columnas $n$ para la Matriz A y la Matriz B.
4. **Cargar Valores:** Rellena las cuadrículas o presiona **`🎲 Ejemplo`**.
5. **Ejecutar:** Presiona la operación deseada (ej. **`A × B`** o **`🚀 Resolver Ax = b`**) y observa el desglose paso a paso en el panel derecho.

---

---

## 3. 🧠 Algoritmo Interno: ¿Cómo Funciona por Dentro?

El programa utiliza **Python Estándar puro** (listas de listas, sin bibliotecas matemáticas como NumPy), basándose en dos pilares algorítmicos internos:

### A. Reutilización del Motor de Gauss-Jordan (El "Kernel" Matemático)
Para las tareas complejas de **Combinación Lineal**, **Independencia Lineal** y **Ecuaciones $Ax = b$**, el programa no reinventa la rueda. En su lugar:

1. **Construcción de la Matriz Aumentada:** 
   - Para Combinación Lineal, acomoda los vectores $v_1, \dots, v_k$ como columnas y el vector $b$ como el término independiente: $[v_1 \; v_2 \; \dots \; v_k \mid b]$.
   - Para Independencia Lineal, acomoda los vectores y pone cero en el término independiente: $[v_1 \; v_2 \; \dots \; v_k \mid \vec{0}]$.
2. **Reducción Gauss-Jordan:** Pasa esta matriz por la función central `resolver_gauss_jordan()`, reduciéndola a su Forma Escalonada Reducida (RREF).
3. **Interpretación de Variables Libres:**
   - Si la RREF no tiene variables libres $\rightarrow$ los vectores son **Linealmente Independientes (L.I.)**.
   - Si la RREF tiene variables libres $\rightarrow$ los vectores son **Linealmente Dependientes (L.D.)**. El algoritmo asigna un valor de $1$ a la variable libre para despejar y reconstruir automáticamente la **relación de dependencia no trivial** ($c_1 v_1 + c_2 v_2 + \dots = \vec{0}$).

---

### B. Algoritmo de Triple Bucle Anidado (Multiplicación Matricial)
Para el producto $C = A \cdot B$ de matrices $A_{m \times n}$ y $B_{n \times p}$:

```python
for i in range(m):          # 1. Recorre cada fila i de la Matriz A
    for j in range(p):      # 2. Recorre cada columna j de la Matriz B
        acumulador = 0
        for k in range(n):  # 3. Hace el producto punto: A[i][k] * B[k][j]
            acumulador += A[i][k] * B[k][j]
        C[i][j] = acumulador
```
El bucle interior $k$ no solo acumula la suma de productos numéricos, sino que construye simultáneamente la representación en texto didáctico (ej. `c₁₁ = (1)·(4) + (2)·(3) = 10`) que se muestra en la pantalla del usuario.
