# INFORME DE PROGRAMACIÓN EN PYTHON · PROGRAMA 9
## MÉTODO ABIERTO: BÚSQUEDA DE RAÍCES POR NEWTON-RAPHSON
### CALCULADORA DE ÁLGEBRA LINEAL (PYMATRIX)

**Facultad de Ingeniería y Arquitectura (FIA) · Universidad Americana (UAM)**  
**Asignatura:** Álgebra Lineal (MTM0120)  
**Docente:** José Andrés Munguía Cortez  
**Modalidad:** Grupal (Grupo 3: De La Rocha - Armengol) con defensa individual  
**Evaluación:** Tercer Corte Evaluativo (Valor: 15 puntos)  

---

*(Espacio para portada de entrega)*

---

## 1. Descripción del Algoritmo y Fundamento Matemático

El método de **Newton-Raphson** es un algoritmo abierto iterativo para la aproximación de raíces de funciones no lineales diferenciables $f(x) = 0$. A diferencia de los métodos cerrados (como el método de Bisección), no requiere acotar la raíz dentro de un intervalo inicial $[a, b]$ donde ocurra un cambio de signo ($f(a) \cdot f(b) < 0$). En su lugar, requiere únicamente un único valor de partida $x_0$ y se apoya en el concepto del cálculo diferencial: la recta tangente y su pendiente $f'(x)$.

### 1.1 Deducción Geométrica de la Fórmula Iterativa
En cada iteración $i$, se evalúa la función en la aproximación actual $x_i$, obteniéndose el punto $(x_i, f(x_i))$. La ecuación de la recta tangente a la curva $y = f(x)$ en dicho punto, con pendiente dada por la primera derivada $f'(x_i)$, es:

$$y - f(x_i) = f'(x_i) \cdot (x - x_i)$$

La siguiente aproximación $x_{i+1}$ se define como el punto geométrico donde dicha recta tangente corta el eje horizontal de las abscisas (haciendo $y = 0$):

$$0 - f(x_i) = f'(x_i) \cdot (x_{i+1} - x_i)$$

Despejando algebraicamente el término $x_{i+1}$ se obtiene la fórmula canónica de recurrencia de Newton-Raphson:

$$x_{i+1} = x_i - \frac{f(x_i)}{f'(x_i)}$$

### 1.2 Derivación Simbólica con SymPy y Evaluación con NumPy
Para evitar aproximaciones por diferencias finitas que introduzcan errores de redondeo o truncamiento en la pendiente, el software utiliza **SymPy** (`sympy.diff`) para obtener la derivada analítica simbólica exacta $f'(x) = \frac{df}{dx}$. Luego, las evaluaciones puntuales $f(x_i)$ y $f'(x_i)$ se calculan mediante **NumPy** (`numpy.float64`), asegurando evaluaciones finitas y control de excepciones.

### 1.3 Cálculo de Errores y Criterio de Parada
El programa monitorea simultáneamente dos métricas de error entre aproximaciones consecutivas:
1. **Error aproximado absoluto:**
   $$\varepsilon_a = |x_{i+1} - x_i|$$
2. **Error relativo porcentual:**
   $$\varepsilon_a(\%) = \left|\frac{x_{i+1} - x_i}{x_{i+1}}\right| \times 100\% \quad (\text{para } x_{i+1} \neq 0)$$

*Tratamiento de División por Cero:* Si la aproximación $x_{i+1}$ resulta ser exactamente 0, el programa conmuta automáticamente a evaluar el error absoluto para evitar una indeterminación.

*Criterio de Parada y Comprobación del Residuo:* Las iteraciones se detienen cuando $\varepsilon_a < \text{Tol}$ o al alcanzar el límite máximo de iteraciones ($N_{\max}$). Cumplir la tolerancia de error aproximado no garantiza por sí solo que se haya encontrado una raíz (por ejemplo, en pendientes casi horizontales); por ello, el programa calcula y reporta obligatoriamente el **residuo final** $|f(x_{\text{aprox}})|$, rotulando la solución siempre como *"raíz aproximada"* o *"aproximación obtenida"* y nunca como *"raíz exacta"*.

### 1.4 Condiciones de Fallo y Validaciones ("Sad Path")
- **Derivada Nula ($f'(x_i) = 0$):** Recta tangente horizontal sin corte con el eje $x$. El programa detiene el cálculo de inmediato y emite un mensaje didáctico de advertencia.
- **Derivada Críticamente Pequeña ($|f'(x_i)| < 10^{-12}$):** Evita saltos inestables desproporcionados fuera del dominio de convergencia.
- **Detección de Ciclos u Oscilaciones:** Inspecciona el historial de aproximaciones para detectar bucles periódicos (como el ciclo $0 \leftrightarrow 1$ en $x^3 - 2x + 2$).
- **Control de Valores no Finitos:** Captura excepciones ante desbordamientos numéricos (Overflow / NaN / Inf) en funciones divergentes como $\arctan(x)$.

---

## 2. Evidencia de Integración en la Calculadora de Álgebra Lineal

El módulo de Newton-Raphson fue integrado armónicamente dentro de la Calculadora de Álgebra Lineal (`PyMatrix`):
- Accesible desde el **Dashboard de Inicio** mediante la tarjeta *"🎯 Métodos Numéricos"*.
- Accesible desde el **Menú Lateral Persistente (Sidebar)**.
- Ejecutable directamente desde el lanzador raíz `Programa 9_Grupo 3.py`.

*(Ver captura adjunta: evidencias/01_integracion_menu_principal.png)*

---

## 3. Casos de Prueba Obligatorios

### 3.1 Caso 1: Convergencia Rápida (Ejemplo Oficial de Clase)
- **Función:** $f(x) = e^{-x} - x$ (`exp(-x) - x`)
- **Derivada analítica (SymPy):** $f'(x) = -e^{-x} - 1$
- **Valor inicial:** $x_0 = 0.0$
- **Tolerancia:** $\varepsilon_s = 10^{-4}$ ($0.0001$)
- **Criterio:** Error absoluto $\varepsilon_a < 10^{-4}$

**Resultados:**
- El método converge en **4 iteraciones** a la raíz aproximada **$x \approx 0.56714329$**.
- Error alcanzado: $\varepsilon_a = 1.2537 \times 10^{-7}$ ($\varepsilon_a(\%) = 0.0000\%$).
- Residuo final evaluado: $|f(x_{\text{aprox}})| = 4.4409 \times 10^{-15}$ (prácticamente cero numérico).
- La gráfica con **Matplotlib** proyecta las rectas tangentes en $x_0, x_1, x_2$ y resalta la raíz aproximada.
- El **contraste opcional con SciPy** (`scipy.optimize.newton`) confirma exactamente la misma aproximación ($0.5671432904$) en 4 iteraciones.

*(Ver capturas adjuntas: evidencias/02_caso1_convergencia_tabla.png, 03_caso1_convergencia_grafica.png, 04_caso1_convergencia_procedimiento.png y 05_caso1_contraste_scipy.png)*

### 3.2 Caso 2: Derivada Nula o Cercana a Cero
- **Función:** $f(x) = x^2 - 4$
- **Derivada analítica (SymPy):** $f'(x) = 2x$
- **Valor inicial:** $x_0 = 0.0$
- **Tolerancia:** $\varepsilon = 0.0001$

**Evidencia y Resultado:**
Al evaluar en $x_0 = 0$, $f'(0) = 0$. La recta tangente en el vértice es horizontal y paralela al eje $x$, haciendo imposible la división entre cero.  
El software intercepta la condición de fallo preventivamente y muestra el mensaje claro:  
`"Proceso detenido en iteración 1: La derivada analítica f'(0.0) es exactamente cero. La recta tangente es totalmente horizontal y no intersecta el eje x (división por cero indefinida)."`

*(Ver captura adjunta: evidencias/06_caso2_derivada_nula.png)*

### 3.3 Caso 3: No Alcanza el Criterio de Parada / Oscilación Periódica
- **Función:** $f(x) = x^3 - 2x + 2$
- **Derivada analítica (SymPy):** $f'(x) = 3x^2 - 2$
- **Valor inicial:** $x_0 = 0.0$
- **Límite de iteraciones:** 30

**Evidencia y Resultado:**
Desde $x_0 = 0$, la primera iteración produce $x_1 = 1.0$. La segunda iteración produce $x_2 = 0.0$, atrapando al algoritmo en un ciclo cerrado $0 \leftrightarrow 1$.  
El software analiza el historial y diagnostica:  
`"Se detectó un ciclo u oscilación en la iteración 2. El valor x_3 = 0.000000 coincide con el valor previo x_0 = 0.000000. El método está atrapado en un bucle periódico oscilante y no convergerá a una raíz desde este x0."`  
Cumple la directriz docente de informar el fallo sin presentar un resultado engañoso.

*(Ver captura adjunta: evidencias/07_caso3_oscilacion_no_convergencia.png)*

---

## 4. Orientaciones para la Defensa Individual

1. **Significado geométrico:** La fórmula iterativa $x_{i+1} = x_i - \frac{f(x_i)}{f'(x_i)}$ representa el punto de corte con el eje $x$ ($y=0$) de la recta tangente a la curva trazada en $(x_i, f(x_i))$.
2. **Convergencia cuadrática:** Para raíces simples con $x_0$ cercano, el error $|e_{i+1}| \approx C \cdot |e_i|^2$, lo que duplica aproximadamente el número de cifras significativas exactas por cada iteración.
3. **Derivada nula:** Si $f'(x_i) = 0$, la pendiente es horizontal y la división se indetermina. Si es muy pequeña, genera saltos enormes e inestabilidad numérica.
4. **Residuo obligatorio:** Se debe comprobar $|f(x_{\text{aprox}})|$ porque un $\varepsilon_a$ pequeño no asegura que la función esté cerca de cero si la pendiente es casi plana.
