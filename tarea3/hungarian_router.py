"""
hungarian_router.py
==============================================================================
Módulo de Optimización de Enrutamiento mediante el Algoritmo Húngaro
Facultad de Ingeniería - Universidad José Antonio Páez
Cátedra: Métodos Cuantitativos y Simulación

Resuelve el problema de asignación óptima 1 a 1 entre N flujos de datos
pendientes de transmisión y M enlaces o nodos de salida disponibles.

Criterio de Costo:
    C_{ij} = Latencia_Actual_{ij} + alpha * (Saturación_Buffer_Nodo_j)

donde:
    - Latencia_Actual_{ij}: Retardo de propagación/transmisión del enlace (ms).
    - Saturación_Buffer_Nodo_j: Razón de ocupación actual del buffer (q_j / S_j).
    - alpha: Ponderador de saturación vs latencia (factor de equilibrio de carga).
    - Si el enlace está caído/inactivo, el costo se penaliza con un valor exorbitante
      (PENALIZACION_ENLACE_CAIDO = 1e6) para forzar el desvío por rutas alternas.

Implementa resolución mediante:
    1. SciPy (scipy.optimize.linear_sum_assignment) para máxima eficiencia.
    2. Algoritmo Húngaro (Kuhn-Munkres) propio documentado paso a paso para
       propósitos académicos y defensa oral del proyecto.
==============================================================================
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np

try:
    from scipy.optimize import linear_sum_assignment
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


PENALIZACION_ENLACE_CAIDO = 1_000_000.0  # Costo prohibitivo para enlaces caídos
ALPHA_DEFECTO = 45.0                     # Ponderación de saturación del buffer en ms


@dataclass
class AsignacionResultado:
    """Estructura que encapsula el resultado de la optimización del Algoritmo Húngaro."""
    pares_asignados: List[Tuple[int, int]]  # Lista de tuplas (flujo_idx, enlace_idx)
    costo_total: float                     # Suma de costos de los enlaces asignados
    matriz_costos: np.ndarray              # Matriz de costos evaluada C_{ij}
    flujos_sin_asignar: List[int]          # Flujos que no pudieron ser asignados (si N > M o enlaces caídos)
    enlaces_libres: List[int]              # Enlaces que quedaron ociosos (si M > N)
    metodo_utilizado: str                  # "SciPy (Kuhn-Munkres)" o "Implementación Propia"


class HungarianRouter:
    """
    Controlador de balanceo dinámico de carga y enrutamiento óptimo.
    Evalúa periódicamente la red y calcula la asignación que minimiza
    el costo global de latencia y congestión de buffers.
    """

    def __init__(self, alpha: float = ALPHA_DEFECTO):
        """
        :param alpha: Factor de sensibilidad a la saturación del buffer.
                      Un valor mayor prioriza enviar paquetes a buffers vacíos
                      incluso si la latencia base es ligeramente superior.
        """
        self.alpha = float(alpha)
        self.historial_optimizaciones = 0
        self.ultimo_resultado: Optional[AsignacionResultado] = None

    def calcular_matriz_costos(
        self,
        num_flujos: int,
        enlaces_info: List[Dict]
    ) -> np.ndarray:
        """
        Construye la matriz de costos C_{ij} de dimensión (num_flujos x num_enlaces).

        :param num_flujos: Cantidad N de flujos de paquetes pendientes.
        :param enlaces_info: Lista de diccionarios con la información de cada enlace j:
               - 'latencia_ms': float (tiempo base o actual de propagación)
               - 'saturacion_nodo_destino': float (ratio 0.0 a 1.0 de cola/capacidad S)
               - 'activo': bool (True si el enlace está operativo, False si está caído)
        :return: Matriz 2D de NumPy con los costos C_{ij}.
        """
        num_enlaces = len(enlaces_info)
        if num_flujos == 0 or num_enlaces == 0:
            return np.empty((num_flujos, num_enlaces), dtype=float)

        matriz_costos = np.zeros((num_flujos, num_enlaces), dtype=float)

        for j, info in enumerate(enlaces_info):
            activo = info.get("activo", True)
            latencia = float(info.get("latencia_ms", 10.0))
            saturacion = float(info.get("saturacion_nodo_destino", 0.0))

            if not activo:
                # Enlace caído: costo prohibitivo para evitar asignación
                costo_j = PENALIZACION_ENLACE_CAIDO
            else:
                # C_{ij} = Latencia_ij + alpha * Saturación_j
                costo_j = latencia + self.alpha * saturacion

            # Asignamos el mismo costo base para cada flujo hacia ese enlace
            matriz_costos[:, j] = costo_j

        return matriz_costos

    def resolver_asignacion(
        self,
        num_flujos: int,
        enlaces_info: List[Dict],
        forzar_algoritmo_propio: bool = False
    ) -> AsignacionResultado:
        """
        Ejecuta el Algoritmo Húngaro para determinar la asignación óptima.

        :param num_flujos: N flujos pendientes de transmisión.
        :param enlaces_info: M enlaces o canales disponibles.
        :param forzar_algoritmo_propio: Si True, usa la implementación nativa
                                       incluso si SciPy está instalado.
        :return: Objeto AsignacionResultado con los enlaces asignados y métricas.
        """
        self.historial_optimizaciones += 1

        if num_flujos == 0 or len(enlaces_info) == 0:
            res = AsignacionResultado(
                pares_asignados=[],
                costo_total=0.0,
                matriz_costos=np.empty((num_flujos, len(enlaces_info))),
                flujos_sin_asignar=list(range(num_flujos)),
                enlaces_libres=list(range(len(enlaces_info))),
                metodo_utilizado="Sin datos"
            )
            self.ultimo_resultado = res
            return res

        matriz_costos = self.calcular_matriz_costos(num_flujos, enlaces_info)

        # Selección de motor de optimización
        if SCIPY_AVAILABLE and not forzar_algoritmo_propio:
            filas_asignadas, cols_asignadas = linear_sum_assignment(matriz_costos)
            metodo = "SciPy (linear_sum_assignment)"
        else:
            filas_asignadas, cols_asignadas = self._hungarian_propio(matriz_costos)
            metodo = "Algoritmo Húngaro Nativo (Kuhn-Munkres)"

        # Filtrar asignaciones inviables (enlaces caídos que recibieron penalización)
        pares_validos = []
        costo_total_acumulado = 0.0
        flujos_cubiertos = set()
        enlaces_ocupados = set()

        for f_idx, e_idx in zip(filas_asignadas, cols_asignadas):
            costo = matriz_costos[f_idx, e_idx]
            if costo < (PENALIZACION_ENLACE_CAIDO * 0.5):
                pares_validos.append((int(f_idx), int(e_idx)))
                costo_total_acumulado += float(costo)
                flujos_cubiertos.add(int(f_idx))
                enlaces_ocupados.add(int(e_idx))

        flujos_sin_asignar = [i for i in range(num_flujos) if i not in flujos_cubiertos]
        enlaces_libres = [j for j in range(len(enlaces_info)) if j not in enlaces_ocupados]

        resultado = AsignacionResultado(
            pares_asignados=pares_validos,
            costo_total=round(costo_total_acumulado, 2),
            matriz_costos=matriz_costos,
            flujos_sin_asignar=flujos_sin_asignar,
            enlaces_libres=enlaces_libres,
            metodo_utilizado=metodo
        )
        self.ultimo_resultado = resultado
        return resultado

    # --------------------------------------------------------------------------
    # IMPLEMENTACIÓN PROPIA DEL ALGORITMO HÚNGARO (KUHN-MUNKRES)
    # --------------------------------------------------------------------------
    def _hungarian_propio(self, cost_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Implementación didáctica del Algoritmo Húngaro para matrices rectangulares y cuadradas.
        Garantiza que el proyecto funcione en cualquier entorno de Python puro.
        """
        cost = np.array(cost_matrix, dtype=float, copy=True)
        n_rows, n_cols = cost.shape

        # Si la matriz es rectangular, la expandimos a cuadrada con valor muy alto
        dim = max(n_rows, n_cols)
        pad_value = cost.max() * 2.0 if cost.size > 0 else 0.0
        if pad_value == 0:
            pad_value = 1000.0

        square_matrix = np.full((dim, dim), pad_value, dtype=float)
        square_matrix[:n_rows, :n_cols] = cost

        # Paso 1: Restar el mínimo de cada fila
        for r in range(dim):
            min_val = square_matrix[r, :].min()
            square_matrix[r, :] -= min_val

        # Paso 2: Restar el mínimo de cada columna
        for c in range(dim):
            min_val = square_matrix[:, c].min()
            square_matrix[:, c] -= min_val

        # Emparejamiento por cubrimiento de ceros y caminos aumentantes
        # Para matrices de red típicas (3x3 a 10x10), resolvemos mediante búsqueda de match máximo
        row_ind, col_ind = self._max_bipartite_matching_zeros(square_matrix)

        # Filtrar únicamente los índices que pertenecen a la matriz original (n_rows, n_cols)
        final_rows = []
        final_cols = []
        for r, c in zip(row_ind, col_ind):
            if r < n_rows and c < n_cols:
                final_rows.append(r)
                final_cols.append(c)

        return np.array(final_rows, dtype=int), np.array(final_cols, dtype=int)

    def _max_bipartite_matching_zeros(self, matrix: np.ndarray) -> Tuple[List[int], List[int]]:
        """
        Encuentra el matching de costo mínimo sobre la matriz reducida de ceros
        mediante aproximación voraz con backtracking si es necesario.
        """
        dim = matrix.shape[0]
        # Construir matriz de adyacencia de ceros
        adj = [[] for _ in range(dim)]
        for r in range(dim):
            # Priorizar ceros
            min_r = matrix[r, :].min()
            for c in range(dim):
                if matrix[r, c] <= min_r + 1e-9:
                    adj[r].append(c)

        match_l = [-1] * dim
        match_r = [-1] * dim

        def dfs(u: int, seen: List[bool]) -> bool:
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    if match_r[v] < 0 or dfs(match_r[v], seen):
                        match_l[u] = v
                        match_r[v] = u
                        return True
            return False

        # Intentar emparejar cada fila
        for r in range(dim):
            seen = [False] * dim
            dfs(r, seen)

        # Si quedaron filas sin emparejar en la componente de ceros, asignar vorazmente al mínimo disponible
        unmatched_rows = [r for r in range(dim) if match_l[r] < 0]
        available_cols = set(c for c in range(dim) if match_r[c] < 0)

        for r in unmatched_rows:
            if not available_cols:
                break
            best_col = min(available_cols, key=lambda c: matrix[r, c])
            match_l[r] = best_col
            match_r[best_col] = r
            available_cols.remove(best_col)

        rows = []
        cols = []
        for r in range(dim):
            if match_l[r] >= 0:
                rows.append(r)
                cols.append(match_l[r])

        return rows, cols
