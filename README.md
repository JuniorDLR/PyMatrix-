# PyMatrix 🔢

**PyMatrix** es una calculadora de álgebra lineal diseñada inicialmente para resolver sistemas de ecuaciones mediante el método de eliminación por filas (Gauss). Este proyecto está construido con un enfoque estricto en el uso de **Python estándar** para la lógica matemática, sin depender de bibliotecas externas como NumPy o SciPy, lo que lo hace perfecto con propósitos académicos y de aprendizaje de la lógica profunda detrás de las matrices.

> **Nota:** El proyecto está siendo desarrollado en fases. Este repositorio contiene actualmente la **Fase 1** (Eliminación de Gauss).

## 🚀 Características (Fase 1)

*   **Interfaz Gráfica Moderna:** Construida con `customtkinter` para una experiencia fluida, elegante y en modo oscuro.
*   **Entrada Dinámica:** Permite crear matrices de cualquier dimensión $m \times n$.
*   **Eliminación de Gauss Paso a Paso:** 
    *   Muestra la matriz aumentada inicial.
    *   Captura e imprime cada operación de pivoteo y reducción a ceros debajo del pivote.
*   **Clasificador Inteligente de Sistemas:**
    *   **Solución Única:** (Consistente Determinado). Encuentra e imprime las variables.
    *   **Infinitas Soluciones:** (Consistente Indeterminado). Identifica e indica las variables libres.
    *   **Sin Solución:** (Inconsistente). Detecta absurdos matemáticos ($0 = k$).
*   **Verificación Automática:** Módulo integrado que evalúa el resultado inyectándolo en las ecuaciones originales para comprobar posibles errores de punto flotante.

## 🛠️ Tecnologías Usadas

*   **Python 3** (Lógica base: Listas anidadas, recursividad simulada, Dataclasses).
*   **CustomTkinter** (Framework de UI).

## ⚙️ Instalación y Uso

1.  Clona este repositorio:
    ```bash
    git clone https://github.com/JuniorDLR/PyMatrix-.git
    cd PyMatrix-
    ```
2.  Instala la dependencia de interfaz gráfica:
    ```bash
    pip install customtkinter
    ```
3.  Ejecuta el script principal:
    ```bash
    python "Programa 1_Grupox.py"
    ```

## 📂 Arquitectura del Código

*   `Programa 1_Grupox.py`: Entry point principal de la aplicación.
*   `src/core/domain.py`: Definición de tipos inmutables (`dataclasses`) y tipos de retorno usando _Union Types_.
*   `src/core/gauss.py`: Algoritmo matemático estricto.
*   `src/ui/app.py`: Ventana principal y renderizado dinámico de la interfaz.

---
*Desarrollado como Proyecto Integrador de Álgebra Lineal.*
