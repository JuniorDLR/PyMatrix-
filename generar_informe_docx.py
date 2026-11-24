"""Genera el documento Word (.docx) formal del Informe del Programa 9 con imágenes incrustadas."""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

doc = Document()

# Configurar márgenes estándar
for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

# Título Principal
h1 = doc.add_heading("INFORME DE PROGRAMACIÓN EN PYTHON · PROGRAMA 9", level=0)
h1.alignment = WD_ALIGN_PARAGRAPH.CENTER

sub = doc.add_paragraph("MÉTODO ABIERTO: BÚSQUEDA DE RAÍCES POR NEWTON-RAPHSON\nCALCULADORA DE ÁLGEBRA LINEAL (PYMATRIX)")
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub.runs[0].font.bold = True
sub.runs[0].font.size = Pt(13)
sub.runs[0].font.color.rgb = RGBColor(3, 105, 161)

doc.add_paragraph("(Espacio reservado para la Portada del Grupo 3: Universidad Americana, FIA, Álgebra Lineal MTM0120, Docente: José Andrés Munguía Cortez, Integrantes)")
doc.add_page_break()

# -----------------------------------------------------------------------------
# SECCIÓN 1: DESCRIPCIÓN DEL ALGORITMO Y FUNDAMENTO MATEMÁTICO
# -----------------------------------------------------------------------------
doc.add_heading("1. Descripción del Algoritmo y Fundamento Matemático", level=1)

p = doc.add_paragraph()
p.add_run("El método de Newton-Raphson es un método numérico abierto de aproximación de raíces para funciones no lineales diferenciables f(x) = 0. A diferencia de los métodos cerrados (como el método de Bisección), no requiere que el intervalo de búsqueda encierre la raíz [a, b] garantizando un cambio de signo (f(a)·f(b) < 0). En su lugar, utiliza únicamente un valor inicial de partida x₀ y aprovecha la información analítica de la primera derivada f'(x) para proyectar iterativamente aproximaciones sucesivas mediante rectas tangentes.")

doc.add_heading("1.1 Deducción Geométrica de la Fórmula Iterativa", level=2)
doc.add_paragraph(
    "Geométricamente, el método traza una recta tangente a la curva y = f(x) en el punto (xᵢ, f(xᵢ)). "
    "La ecuación general de dicha recta tangente con pendiente f'(xᵢ) viene dada por:\n\n"
    "    y - f(xᵢ) = f'(xᵢ) · (x - xᵢ)\n\n"
    "La siguiente aproximación xᵢ₊₁ se define como el punto donde esta recta tangente corta el eje horizontal (haciendo y = 0):\n\n"
    "    0 - f(xᵢ) = f'(xᵢ) · (xᵢ₊₁ - xᵢ)\n\n"
    "Despejando xᵢ₊₁ se obtiene la ecuación fundamental de recurrencia de Newton-Raphson:\n\n"
    "    xᵢ₊₁ = xᵢ - [ f(xᵢ) / f'(xᵢ) ]"
)

doc.add_heading("1.2 Derivación Simbólica con SymPy y Evaluación Numérica con NumPy", level=2)
doc.add_paragraph(
    "Para garantizar la exactitud matemática y evitar errores de truncamiento derivados de aproximaciones numéricas finitas, "
    "el módulo utiliza la librería SymPy para interpretar simbólicamente la función ingresada por el usuario y calcular analíticamente "
    "su derivada exacta f'(x) = d/dx[f(x)]. Posteriormente, las evaluaciones puntuales f(xᵢ) y f'(xᵢ) se ejecutan con alta precisión "
    "utilizando NumPy, asegurando evaluaciones finitas y control de dominio."
)

doc.add_heading("1.3 Cálculo del Error Aproximado y Criterio de Parada", level=2)
doc.add_paragraph(
    "En cada iteración se calcula tanto el error absoluto entre aproximaciones consecutivas como el error relativo porcentual:\n\n"
    "• Error aproximado absoluto:        ε_a = | xᵢ₊₁ - xᵢ |\n"
    "• Error relativo porcentual:       ε_a(%) = | (xᵢ₊₁ - xᵢ) / xᵢ₊₁ | × 100%   (para xᵢ₊₁ ≠ 0)\n\n"
    "Tratamiento de División por Cero en el Error: Si la aproximación xᵢ₊₁ resulta ser exactamente 0, "
    "el algoritmo evita una indeterminación matemática evaluando y reportando el criterio sobre el error absoluto |xᵢ₊₁ - xᵢ|.\n\n"
    "Criterio de Parada y Comprobación del Residuo: Las iteraciones continúan hasta que el error aproximado sea estrictamente menor "
    "que la tolerancia fijada (ε_a < Tol) o hasta alcanzar el número máximo permitido de iteraciones (N_max). "
    "Siguiendo rigurosamente las consideraciones docentes, cumplir el criterio de error no garantiza por sí solo una raíz verdadera "
    "(por ejemplo, en pendientes casi planas); por ello, el programa evalúa y reporta obligatoriamente el residuo final |f(x_aprox)|, "
    "rotulando siempre la solución como 'raíz aproximada' o 'aproximación obtenida' y nunca como 'raíz exacta'."
)

doc.add_heading("1.4 Condiciones de Fallo y Validaciones ('Sad Path')", level=2)
doc.add_paragraph(
    "El algoritmo implementa un diseño orientado a fallos (Fail-Fast) con las siguientes protecciones preventivas:\n\n"
    "1. Derivada Nula (f'(xᵢ) = 0): Si la derivada es exactamente cero, la recta tangente es horizontal y paralela al eje x. "
    "El programa detiene el proceso inmediatamente emitiendo un diagnóstico claro que explica la imposibilidad de dividir entre cero.\n\n"
    "2. Derivada Críticamente Cercana a Cero (|f'(xᵢ)| < 10⁻¹²): Cuando la pendiente es casi nula, el cociente f(xᵢ)/f'(xᵢ) produce "
    "un salto excesivamente desproporcionado que expulsa la iteración fuera de la región de interés. El sistema aborta controladamente.\n\n"
    "3. Detección de Oscilaciones y Ciclos Periódicos: Se almacena el historial de aproximaciones. Si xᵢ₊₁ coincide numéricamente con un valor "
    "evaluado en pasos anteriores (como el ciclo 0 ↔ 1 en x³ - 2x + 2), el algoritmo diagnostica que el método está atrapado en un bucle periódico.\n\n"
    "4. Control de Divergencia y Valores no Finitos: Si la función genera valores Inf, -Inf o NaN (como en arctan(x) con x₀=2), "
    "el sistema captura la condición y reporta la divergencia sin permitir caídas inesperadas de la interfaz."
)

doc.add_page_break()

# -----------------------------------------------------------------------------
# SECCIÓN 2: EVIDENCIA DE INTEGRACIÓN EN PYMATRIX
# -----------------------------------------------------------------------------
doc.add_heading("2. Evidencia de Integración en la Calculadora de Álgebra Lineal", level=1)
doc.add_paragraph(
    "El módulo de Newton-Raphson fue integrado armónicamente dentro del ecosistema de la Calculadora de Álgebra Lineal (PyMatrix). "
    "El acceso se encuentra disponible desde el menú interactivo del Dashboard de Inicio (tarjeta 'Métodos Numéricos') "
    "así como en el menú lateral persistente (Sidebar) y en el lanzador raíz 'Programa 9_Grupo 3.py'."
)

img_path = os.path.abspath("evidencias/01_integracion_menu_principal.png")
if os.path.exists(img_path):
    doc.add_picture(img_path, width=Inches(6.2))
    cap = doc.add_paragraph("Figura 1: Menú interactivo (Dashboard de Inicio) de PyMatrix mostrando el acceso integrado a Métodos Numéricos.")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.runs[0].font.italic = True
    cap.runs[0].font.size = Pt(9.5)

doc.add_page_break()

# -----------------------------------------------------------------------------
# SECCIÓN 3: CASOS DE PRUEBA OBLIGATORIOS
# -----------------------------------------------------------------------------
doc.add_heading("3. Casos de Prueba Obligatorios", level=1)

# CASO 1
doc.add_heading("3.1 Caso 1: Convergencia Rápida (Ejemplo Oficial de Clase)", level=2)
doc.add_paragraph(
    "• Función ingresada: f(x) = e⁻ˣ - x  (exp(-x) - x)\n"
    "• Derivada analítica obtenida con SymPy: f'(x) = -e⁻ˣ - 1\n"
    "• Valor inicial: x₀ = 0.0\n"
    "• Tolerancia de convergencia: ε_s = 10⁻⁴ (0.0001)\n"
    "• Criterio de parada: Error aproximado absoluto ε_a < 10⁻⁴\n\n"
    "Resultados Obtenidos:\n"
    "El método converge en exactamente 4 iteraciones alcanzando una aproximación de la raíz x ≈ 0.56714329. "
    "El error aproximado en la última iteración descendió a ε_a = 1.2537 × 10⁻⁷, satisfaciendo ampliamente la tolerancia. "
    "El residuo final comprobado en la función original es |f(x_aprox)| = 4.4409 × 10⁻¹⁵ (prácticamente cero numérico). "
    "En comparación con el método cerrado de Bisección (que requiere 14 iteraciones en [0, 1]), Newton-Raphson demostró su orden de convergencia cuadrático (p=2)."
)

img_path = os.path.abspath("evidencias/02_caso1_convergencia_tabla.png")
if os.path.exists(img_path):
    doc.add_picture(img_path, width=Inches(6.2))
    cap = doc.add_paragraph("Figura 2: Tabla de iteraciones y diagnóstico final del Caso 1 (Convergencia rápida en 4 iteraciones).")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.runs[0].font.italic = True
    cap.runs[0].font.size = Pt(9.5)

doc.add_paragraph()
img_path = os.path.abspath("evidencias/03_caso1_convergencia_grafica.png")
if os.path.exists(img_path):
    doc.add_picture(img_path, width=Inches(6.2))
    cap = doc.add_paragraph("Figura 3: Representación gráfica interactiva (Matplotlib) mostrando la curva f(x), puntos de iteración, rectas tangentes y la raíz aproximada.")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.runs[0].font.italic = True
    cap.runs[0].font.size = Pt(9.5)

doc.add_paragraph()
img_path = os.path.abspath("evidencias/04_caso1_convergencia_procedimiento.png")
if os.path.exists(img_path):
    doc.add_picture(img_path, width=Inches(6.2))
    cap = doc.add_paragraph("Figura 4: Desglose didáctico del procedimiento paso a paso estructurado según las 5 etapas de clase del docente.")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.runs[0].font.italic = True
    cap.runs[0].font.size = Pt(9.5)

doc.add_paragraph()
img_path = os.path.abspath("evidencias/05_caso1_contraste_scipy.png")
if os.path.exists(img_path):
    doc.add_picture(img_path, width=Inches(6.2))
    cap = doc.add_paragraph("Figura 5: Pestaña de Contraste Opcional con scipy.optimize.newton confirmando idéntica solución (x ≈ 0.56714329 en 4 iteraciones).")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.runs[0].font.italic = True
    cap.runs[0].font.size = Pt(9.5)

doc.add_page_break()

# CASO 2
doc.add_heading("3.2 Caso 2: Derivada Nula o Cercana a Cero", level=2)
doc.add_paragraph(
    "• Función ingresada: f(x) = x² - 4\n"
    "• Derivada analítica obtenida con SymPy: f'(x) = 2x\n"
    "• Valor inicial: x₀ = 0.0\n"
    "• Tolerancia: ε = 0.0001\n\n"
    "Evidencia y Resultado Esperado:\n"
    "Al evaluar la primera iteración en x₀ = 0, se obtiene f'(0) = 2(0) = 0. "
    "Dado que la fórmula iterativa exige dividir entre f'(xᵢ), la división 4/0 es matemáticamente indeterminada. "
    "Geométricamente, la recta tangente en el vértice de la parábola es perfectamente horizontal y paralela al eje de las abscisas, "
    "por lo que jamás lo cortará.\n\n"
    "Comportamiento del Software:\n"
    "El programa intercepta la condición de fallo mediante la validación previa 'Sad Path', detiene inmediatamente el proceso "
    "sin arrojar un error de consola (ZeroDivisionError) y despliega el mensaje diagnóstico comprensible al usuario:\n"
    "'Proceso detenido en iteración 1: La derivada analítica f'(0.0) es exactamente cero. La recta tangente es totalmente horizontal "
    "y no intersecta el eje x (división por cero indefinida)'."
)

img_path = os.path.abspath("evidencias/06_caso2_derivada_nula.png")
if os.path.exists(img_path):
    doc.add_picture(img_path, width=Inches(6.2))
    cap = doc.add_paragraph("Figura 6: Caso 2: Detención controlada inmediata ante derivada nula f'(0)=0 con mensaje de aviso explicativo.")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.runs[0].font.italic = True
    cap.runs[0].font.size = Pt(9.5)

doc.add_page_break()

# CASO 3
doc.add_heading("3.3 Caso 3: No Alcanza el Criterio de Parada / Oscilación Periódica", level=2)
doc.add_paragraph(
    "• Función ingresada: f(x) = x³ - 2x + 2\n"
    "• Derivada analítica obtenida con SymPy: f'(x) = 3x² - 2\n"
    "• Valor inicial: x₀ = 0.0\n"
    "• Límite de iteraciones: 30\n\n"
    "Evidencia y Resultado Esperado:\n"
    "En este caso clásico de la literatura matemática (presente en la diapositiva 32 del docente), al evaluar desde x₀ = 0:\n"
    "  - Iteración 1: x₁ = 0 - [ f(0) / f'(0) ] = 0 - [ 2 / (-2) ] = 1.0\n"
    "  - Iteración 2: f(1) = 1 - 2 + 2 = 1;  f'(1) = 3(1)² - 2 = 1 → x₂ = 1 - [ 1 / 1 ] = 0.0\n"
    "El algoritmo queda atrapado en un ciclo infinito oscilando periódicamente entre 0 y 1 (0 → 1 → 0 → 1...).\n\n"
    "Comportamiento del Software:\n"
    "La protección contra ciclos analiza el historial de puntos evaluados y detecta la repetición exacta del iterando. "
    "El programa aborta en la iteración 2 informando de forma transparente:\n"
    "'Se detectó un ciclo u oscilación en la iteración 2. El valor x_3 = 0.000000 coincide con el valor previo x_0 = 0.000000. "
    "El método está atrapado en un bucle periódico oscilante y no convergerá a una raíz desde este x0.'\n"
    "De esta manera, se cumple con la exigencia de la rúbrica de informar el estado sin presentar un resultado engañoso."
)

img_path = os.path.abspath("evidencias/07_caso3_oscilacion_no_convergencia.png")
if os.path.exists(img_path):
    doc.add_picture(img_path, width=Inches(6.2))
    cap = doc.add_paragraph("Figura 7: Caso 3: Detección automática de oscilación cíclica sin convergencia, evitando bucles infinitos.")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.runs[0].font.italic = True
    cap.runs[0].font.size = Pt(9.5)

doc.add_page_break()

# -----------------------------------------------------------------------------
# SECCIÓN 4: GUÍA PARA LA DEFENSA INDIVIDUAL
# -----------------------------------------------------------------------------
doc.add_heading("4. Guía de Preparación para la Defensa Individual", level=1)
doc.add_paragraph(
    "Conforme a las orientaciones de la sección 7 de la guía oficial, cada integrante del Grupo 3 debe dominar las siguientes preguntas clave:\n\n"
    "1. ¿Qué representa geométricamente la fórmula de Newton-Raphson?\n"
    "   Respuesta: Representa la intersección con el eje x de la recta tangente trazada a la curva en el punto (xᵢ, f(xᵢ)). "
    "   La pendiente de dicha tangente es f'(xᵢ), y al despejar el corte horizontal y=0 se llega a xᵢ₊₁ = xᵢ - f(xᵢ)/f'(xᵢ).\n\n"
    "2. ¿Por qué el método de Newton-Raphson tiene convergencia cuadrática?\n"
    "   Respuesta: Porque para raíces simples y valores iniciales suficientemente cercanos, el error en el paso i+1 es proporcional "
    "   al cuadrado del error en el paso anterior (|eᵢ₊₁| ≈ C · |eᵢ|²), lo que duplica aproximadamente el número de cifras decimales correctas en cada iteración.\n\n"
    "3. ¿Qué ocurre cuando f'(xᵢ) = 0 o es muy próxima a cero?\n"
    "   Respuesta: Si f'(xᵢ) = 0, la recta tangente es paralela al eje x y no lo corta; la división por cero no está definida. "
    "   Si f'(xᵢ) es muy pequeña (casi plana), la división produce un cociente desmesuradamente grande que dispara la aproximación xᵢ₊₁ "
    "   muy lejos de la raíz (divergencia o salto inestable).\n\n"
    "4. ¿Por qué es obligatorio comprobar el residuo |f(x_aprox)| y no conformarse solo con el error aproximado ε_a?\n"
    "   Respuesta: Porque en funciones con derivadas muy pequeñas o en regiones casi horizontales, dos iteraciones consecutivas pueden estar muy cerca "
    "   entre sí produciendo un ε_a pequeño, pero f(x) puede seguir estando muy lejos de cero. El residuo garantiza que realmente se trata de una raíz."
)

salida_docx = os.path.abspath("Informe_Programa_9_Grupo_3.docx")
doc.save(salida_docx)
print(f"✓ Informe Word generado exitosamente en: {salida_docx}")
