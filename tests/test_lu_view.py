"""Comprueba el procedimiento textual de LU con intercambio de filas."""

from src.core.lu import factorizar_lu, resolver_sistema_lu
from src.ui.lu_view import LUView


class TerminalLU:
    _formatear_matriz = LUView._formatear_matriz
    _formatear_vector = LUView._formatear_vector
    _lineas_sustitucion = LUView._lineas_sustitucion
    _mostrar_resultado = LUView._mostrar_resultado

    def __init__(self, modo: str):
        self.modo = modo
        self.texto = ""
        self._resultado_lu = factorizar_lu([[0, 2, 1], [1, 1, 0], [2, 3, 1]])
        self._resultado_sistema = resolver_sistema_lu(self._resultado_lu, [7, 3, 11])
        self._aviso = None

    def get_modo_numero(self) -> str:
        return self.modo

    def _escribir(self, texto: str) -> None:
        self.texto = texto


def test_terminal_muestra_permutacion_y_sustitucion_correcta():
    for modo in ("fraccion", "decimal"):
        terminal = TerminalLU(modo)
        terminal._mostrar_resultado()

        assert "F1 ↔ F2" in terminal.texto
        assert "PASO 2 · Comprobación P·A = L·U" in terminal.texto
        assert "✓ Se cumple: P·A = L·U." in terminal.texto
        assert "PASO 3 · Sustitución hacia adelante: L·y = P·b" in terminal.texto
        assert "P·b (mismo intercambio de filas) =\n[  3 ]\n[  7 ]\n[ 11 ]" in terminal.texto
        assert "✓ Comprobación exacta: A·x = b." in terminal.texto
