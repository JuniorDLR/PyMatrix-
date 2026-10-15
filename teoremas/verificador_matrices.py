"""Acceso académico a los teoremas matriciales exigidos en la Tarea 6.

Reexporta el verificador exacto compartido con la interfaz gráfica.
Elaborado por: Grupo x.
"""

from src.core.teoremas_matrices import (
    EspecificacionTeorema,
    ResultadoTeorema,
    TEOREMAS,
    verificar_teorema,
)

__all__ = ["EspecificacionTeorema", "ResultadoTeorema", "TEOREMAS", "verificar_teorema"]
