# PyMatrix

Calculadora gráfica de álgebra lineal y métodos numéricos en Python y CustomTkinter. Los algoritmos matemáticos son propios y usan `fractions.Fraction` cuando se requiere exactitud. NumPy se usa para mostrar el épsilon de máquina y SciPy exclusivamente para contrastar la raíz calculada por el método de bisección propio.

## Iniciar

Se necesita Python 3.11 o posterior.

```powershell
python -m pip install -r requirements.txt
python main.py
```

`main.py` abre la interfaz gráfica; no hay menú de terminal.

## Herramientas

- Gauss y Gauss-Jordan con historial de operaciones y clasificación de sistemas.
- Vectores y operaciones matriciales, incluyendo transpuesta, determinante e inversa.
- Factorización `A = L·U` para matrices rectangulares sin intercambio de filas. La vista muestra cada multiplicador y comprueba `L·U = A`.
- Resolución de `A·x = b` por LU para matrices cuadradas con pivotes no nulos: muestra `[L | b] → [I | y]`, `[U | y] → [I | x]` y verifica `A·x = b`.
- Verificador de propiedades de operaciones, transposición, inversa y determinante que calcula ambos miembros y comunica si coinciden.
- Banco compartido de matrices para reutilizar `L`, `U` u otras matrices guardadas.
- Métodos Numéricos: bisección oficial del Programa 7 con función escrita y contraste SciPy, ejercicio de la Sesión 19, graficador con dominio controlado, notación posicional 10/2 y errores numéricos con propagación.

En Bisección y el Graficador se escriben funciones de una variable con `x`, operadores `+`, `-`, `*`, `/`, `**` y `sin`, `cos`, `tan`, `exp`, `log`, `sqrt` o `abs`. El texto se valida con una lista blanca de AST; nunca se ejecuta con `eval()`. La gráfica y los resultados de funciones trascendentes utilizan `float`; en formato Fracción, `≈` identifica aproximaciones racionales. El módulo de la Sesión 19 conserva su criterio de ancho actualizado; el Programa 7 usa la cota de semiancho antes de actualizar.

En las vistas LU y Teoremas se pueden pegar matrices libres: filas separadas por Enter o `;`; columnas separadas por espacios, tabuladores o comas. Se aceptan enteros, decimales y fracciones como `3/4`. La vista LU obtiene las dimensiones de `A` automáticamente. Un pivote que exige intercambio de filas se comunica como necesidad de `P·A = L·U`; la calculadora no presenta una factorización LU inválida.

Los paneles de entrada y resultado tienen desplazamiento independiente para pantallas pequeñas. El selector global permite mostrar resultados como fracciones o decimales sin perder los valores exactos calculados.

## Estructura

- `src/core/`: funciones matemáticas puras, incluyendo `lu.py`, `teoremas_matrices.py` y `numericos/`.
- `src/ui/`: interfaz CustomTkinter, navegación, vistas y las cuatro opciones de `numericos/`.
- `modulos/modulo_lu.py` y `teoremas/verificador_matrices.py`: accesos compatibles con la estructura de entrega de la Tarea 6; reutilizan el mismo núcleo matemático.
- `tests/`: pruebas de operaciones, propiedades, LU, entradas y rutas de error.

Para verificar el proyecto:

```powershell
python -m pytest tests/ -q
```
