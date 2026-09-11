"""
Modelo de Asignacion Optima y Balanceo Dinamico (Algoritmo Hungaro)
Capa de Modelo Cuantitativo — Metodos Cuantitativos
Universidad Jose Antonio Paez
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np

try:
    from scipy.optimize import linear_sum_assignment
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

from src.utils.config import ALPHA_DEFECTO, PENALIZACION_ENLACE_CAIDO


@dataclass
class AsignacionResultado:
    """Estructura que encapsula el resultado de la optimizacion del Algoritmo Hungaro."""
    pares_asignados: List[Tuple[int, int]]  # Tuplas (flujo_idx, enlace_idx)
    costo_total: float                     # Suma de costos de los enlaces asignados
    matriz_costos: np.ndarray              # Matriz de costos evaluada C_{ij}
    flujos_sin_asignar: List[int]          # Flujos que no pudieron ser asignados
    enlaces_libres: List[int]              # Enlaces que quedaron sin flujo asignado
    metodo_utilizado: str                  # "SciPy (linear_sum_assignment)" o "Kuhn-Munkres Nativo"


class ModeloAsignacionHungaro:
    """
    Controlador de balanceo de carga y enrutamiento dinamico.
    Resuelve el problema de asignacion optima 1 a 1 entre N flujos pendientes
    y M enlaces disponibles minimizando la funcion de costo:
        C_{ij} = Latencia_Actual_{ij} + alpha * (Saturacion_Buffer_Nodo_j)
    """

    def __init__(self, alpha: float = ALPHA_DEFECTO):
        """
        :param alpha: Factor de ponderacion de saturacion del buffer en milisegundos.
        """
        self.alpha = float(alpha)
        self.historial_optimizaciones = 0
        self.ultimo_resultado: Optional[AsignacionResultado] = None

    def calcular_matriz_costos(
        self,
        num_flujos: int,
        enlaces_info: List[Dict],
    ) -> np.ndarray:
        """
        Construye la matriz de costos C_{ij} de dimension (num_flujos x num_enlaces).
        
        :param num_flujos: Cantidad N de flujos de paquetes pendientes.
        :param enlaces_info: Lista con metadata de cada enlace j:
               - 'latencia_ms': float
               - 'saturacion_nodo_destino': float (0.0 a 1.0)
               - 'activo': bool
        :return: Matriz 2D de NumPy con los costos C_{ij}.
        """
        num_enlaces = len(enlaces_info)
        if num_flujos == 0 or num_enlaces == 0:
            return np.empty((num_flujos, num_enlaces), dtype=float)

        matriz = np.zeros((num_flujos, num_enlaces), dtype=float)

        for j, info in enumerate(enlaces_info):
            activo = info.get("activo", True)
            latencia = float(info.get("latencia_ms", 10.0))
            saturacion = float(info.get("saturacion_nodo_destino", 0.0))

            if not activo:
                costo_j = PENALIZACION_ENLACE_CAIDO
            else:
                costo_j = latencia + (self.alpha * saturacion)

            matriz[:, j] = costo_j

        return matriz

    def resolver_asignacion(
        self,
        num_flujos: int,
        enlaces_info: List[Dict],
        forzar_nativo: bool = False,
    ) -> AsignacionResultado:
        """
        Ejecuta el Algoritmo Hungaro para encontrar la asignacion de costo minimo.
        """
        self.historial_optimizaciones += 1

        if num_flujos == 0 or len(enlaces_info) == 0:
            res = AsignacionResultado(
                pares_asignados=[],
                costo_total=0.0,
                matriz_costos=np.empty((num_flujos, len(enlaces_info))),
                flujos_sin_asignar=list(range(num_flujos)),
                enlaces_libres=list(range(len(enlaces_info))),
                metodo_utilizado="Sin datos",
            )
            self.ultimo_resultado = res
            return res

        matriz_costos = self.calcular_matriz_costos(num_flujos, enlaces_info)

        # Seleccion de algoritmo (SciPy preferido; Kuhn-Munkres nativo de respaldo exacto)
        if SCIPY_AVAILABLE and not forzar_nativo:
            filas_asig, cols_asig = linear_sum_assignment(matriz_costos)
            metodo = "SciPy (linear_sum_assignment)"
        else:
            filas_asig, cols_asig = self._hungarian_nativo_exacto(matriz_costos)
            metodo = "Algoritmo Hungaro Nativo (Kuhn-Munkres)"

        # Filtrar asignaciones que correspondan a enlaces caidos (costo prohibitivo)
        pares_validos = []
        costo_total = 0.0
        flujos_cubiertos = set()
        enlaces_ocupados = set()

        for f_idx, e_idx in zip(filas_asig, cols_asig):
            costo = matriz_costos[f_idx, e_idx]
            if costo < (PENALIZACION_ENLACE_CAIDO * 0.5):
                pares_validos.append((int(f_idx), int(e_idx)))
                costo_total += float(costo)
                flujos_cubiertos.add(int(f_idx))
                enlaces_ocupados.add(int(e_idx))

        flujos_sin_asignar = [i for i in range(num_flujos) if i not in flujos_cubiertos]
        enlaces_libres = [j for j in range(len(enlaces_info)) if j not in enlaces_ocupados]

        resultado = AsignacionResultado(
            pares_asignados=pares_validos,
            costo_total=round(costo_total, 2),
            matriz_costos=matriz_costos,
            flujos_sin_asignar=flujos_sin_asignar,
            enlaces_libres=enlaces_libres,
            metodo_utilizado=metodo,
        )
        self.ultimo_resultado = resultado
        return resultado

    def _hungarian_nativo_exacto(self, cost_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Implementacion exacta y determinista O(n^3) del Algoritmo Hungaro (Jonker-Volgenant / Kuhn-Munkres).
        Maneja matrices rectangulares (N != M) mediante expansion con filas o columnas ficticias.
        """
        cost = np.array(cost_matrix, dtype=float, copy=True)
        n_rows, n_cols = cost.shape

        dim = max(n_rows, n_cols)
        # Para M > N (mas enlaces que flujos), las filas dummy tienen costo 0 (recursos no utilizados)
        # Para N > M (mas flujos que enlaces), las columnas dummy tienen costo prohibitivo
        sq_matrix = np.zeros((dim, dim), dtype=float)
        if n_rows > n_cols:
            sq_matrix[:, n_cols:] = PENALIZACION_ENLACE_CAIDO
        sq_matrix[:n_rows, :n_cols] = cost

        n = dim
        u = np.zeros(n + 1, dtype=float)
        v = np.zeros(n + 1, dtype=float)
        p = np.zeros(n + 1, dtype=int)
        way = np.zeros(n + 1, dtype=int)

        for i in range(1, n + 1):
            p[0] = i
            j0 = 0
            minv = np.full(n + 1, float("inf"), dtype=float)
            used = np.zeros(n + 1, dtype=bool)

            while True:
                used[j0] = True
                i0 = p[j0]
                delta = float("inf")
                j1 = 0

                for j in range(1, n + 1):
                    if not used[j]:
                        cur = sq_matrix[i0 - 1, j - 1] - u[i0] - v[j]
                        if cur < minv[j]:
                            minv[j] = cur
                            way[j] = j0
                        if minv[j] < delta:
                            delta = minv[j]
                            j1 = j

                for j in range(n + 1):
                    if used[j]:
                        u[p[j]] += delta
                        v[j] -= delta
                    else:
                        minv[j] -= delta

                j0 = j1
                if p[j0] == 0:
                    break

            while True:
                j1 = way[j0]
                p[j0] = p[j1]
                j0 = j1
                if j0 == 0:
                    break

        final_rows = []
        final_cols = []
        for j in range(1, n + 1):
            r = p[j] - 1
            c = j - 1
            if r < n_rows and c < n_cols:
                final_rows.append(r)
                final_cols.append(c)

        # Ordenar por indice de fila para consistencia con SciPy
        pares = sorted(zip(final_rows, final_cols), key=lambda x: x[0])
        rows = np.array([p[0] for p in pares], dtype=int)
        cols = np.array([p[1] for p in pares], dtype=int)
        return rows, cols

    def generar_reporte(self) -> str:
        """Genera resumen de auditoria de asignacion."""
        if not self.ultimo_resultado:
            return "No se han ejecutado optimizaciones de asignacion aun.\n"

        res = self.ultimo_resultado
        lineas = [
            "==================================================",
            "   REPORTE DE ASIGNACION OPTIMA: ALGORITMO HUNGARO",
            "==================================================",
            f"Metodo de Resolucion: {res.metodo_utilizado}",
            f"Sensibilidad a Saturacion (alpha): {self.alpha:.1f} ms",
            f"Total Asignaciones Realizadas: {self.historial_optimizaciones}",
            f"Costo de Transito Minimo Actual: {res.costo_total:.2f} ms",
            f"Pares Enrutados: {res.pares_asignados}",
            f"Flujos sin Asignar: {res.flujos_sin_asignar}",
            f"Enlaces Libres: {res.enlaces_libres}",
            "==================================================",
        ]
        return "\n".join(lineas) + "\n"
