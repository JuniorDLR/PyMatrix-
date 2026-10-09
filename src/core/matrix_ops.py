"""Fachada modular de operaciones matriciales (Patrón Facade).
Reexporta operaciones básicas, ecuaciones Ax=b, determinantes e inversas.
Tema de clase: integración del Módulo III de Álgebra Matricial.
Elaborado por: Grupo x"""

from src.core.ecuaciones_ax import ResultadoProductoMatrizVector, multiplicar_matriz_vector, ResultadoEcuacionMatricial, resolver_ecuacion_matricial
from src.core.propiedades_ax import VerificacionPropiedadAditivaAx, VerificacionPropiedadEscalarAx, VerificacionLinealidadGeneralAx, verificar_propiedad_aditiva_ax, verificar_propiedad_escalar_ax, verificar_linealidad_general_ax
from src.core.operaciones_basicas import validar_dimensiones_matrices_iguales, sumar_matrices, restar_matrices, multiplicar_matriz_escalar, combinacion_matrices, ResultadoMultiplicacionMatricial, multiplicar_matrices, trasponer_matriz
from src.core.determinantes_facade import ResultadoDeterminante, calcular_determinante, calcular_determinante_cofactores_core, calcular_determinante_sarrus_core
from src.core.inversas_facade import ResultadoInversionMatriz, invertir_matriz, invertir_matriz_adjunta
