"""
========================================================================================
UNIVERSIDAD JOSÉ ANTONIO PÁEZ
FACULTAD DE INGENIERÍA - ESCUELA DE INGENIERÍA EN COMPUTACIÓN
MÉTODOS CUANTITATIVOS / INVESTIGACIÓN DE OPERACIONES II

MODELO DE TAMAÑO DE LA FUERZA DE TRABAJO MEDIANTE PROGRAMACIÓN DINÁMICA
Implementación orientada a objetos (POO) con resolución por etapas hacia atrás
(Backward Recursion) y trazado de política óptima hacia adelante (Forward Traceback).
========================================================================================
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional


class PoliticaCostos:
    """
    Encapsula los parámetros y funciones de costo del modelo de fuerza de trabajo.

    Parámetros del problema:
    - Mano de obra excedente: $300 por trabajador por semana conservado.
    - Nueva contratación: Costo fijo de $400 más $200 por trabajador por semana.
    - Despido: Sin costo ($0).
    """

    def __init__(
        self,
        costo_excedente_unitario: float = 300.0,
        costo_fijo_contratacion: float = 400.0,
        costo_variable_contratacion: float = 200.0,
        costo_despido_unitario: float = 0.0,
    ):
        self._validar_costo("costo_excedente_unitario", costo_excedente_unitario)
        self._validar_costo("costo_fijo_contratacion", costo_fijo_contratacion)
        self._validar_costo("costo_variable_contratacion", costo_variable_contratacion)
        self._validar_costo("costo_despido_unitario", costo_despido_unitario)

        self.costo_excedente_unitario = costo_excedente_unitario
        self.costo_fijo_contratacion = costo_fijo_contratacion
        self.costo_variable_contratacion = costo_variable_contratacion
        self.costo_despido_unitario = costo_despido_unitario

    @staticmethod
    def _validar_costo(nombre: str, valor) -> None:
        """Un costo debe ser numerico (int o float, nunca bool) y >= 0."""
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor < 0:
            raise ValueError(
                f"{nombre} debe ser un numero mayor o igual a 0 (se recibio {valor!r})."
            )

    def calcular_costo_excedente(self, x_actual: int, b_requerido: int) -> float:
        """C_1(x_i - b_i): Costo por mantener mano de obra en exceso a la requerida."""
        if x_actual > b_requerido:
            return self.costo_excedente_unitario * (x_actual - b_requerido)
        return 0.0

    def calcular_costo_contratacion(self, x_actual: int, x_previo: int) -> float:
        """C_2(x_i - x_{i-1}): Costo fijo + variable si hay contratación neta."""
        if x_actual > x_previo:
            contratados = x_actual - x_previo
            return self.costo_fijo_contratacion + (self.costo_variable_contratacion * contratados)
        return 0.0

    def calcular_costo_despido(self, x_actual: int, x_previo: int) -> float:
        """Costo por despidos (0 en este modelo según especificaciones)."""
        if x_actual < x_previo:
            despedidos = x_previo - x_actual
            return self.costo_despido_unitario * despedidos
        return 0.0

    def calcular_costo_inmediato(self, x_actual: int, x_previo: int, b_requerido: int) -> Tuple[float, float, float]:
        """Calcula el costo inmediato desglosado: (excedente, contratación/despido, total_inmediato)."""
        c_exc = self.calcular_costo_excedente(x_actual, b_requerido)
        c_con = self.calcular_costo_contratacion(x_actual, x_previo)
        c_des = self.calcular_costo_despido(x_actual, x_previo)
        return c_exc, (c_con + c_des), (c_exc + c_con + c_des)


@dataclass
class EvaluacionAlternativa:
    """Representa el cálculo de una alternativa de decisión puntual x_i dado x_{i-1}."""
    x_previo: int
    x_actual: int
    costo_excedente: float
    costo_transicion: float
    costo_inmediato: float
    costo_futuro: float
    costo_total: float


class EstadoEtapa:
    """
    Almacena los resultados de evaluar todas las alternativas x_i para un estado inicial x_{i-1}.
    Determina la decisión óptima x_i* y el valor mínimo f_i(x_{i-1}).
    """

    def __init__(self, x_previo: int):
        self.x_previo = x_previo
        self.evaluaciones: List[EvaluacionAlternativa] = []
        self.mejor_x_actual: Optional[int] = None
        self.costo_minimo: float = float("inf")

    def registrar_alternativa(self, evaluacion: EvaluacionAlternativa):
        self.evaluaciones.append(evaluacion)
        if evaluacion.costo_total < self.costo_minimo:
            self.costo_minimo = evaluacion.costo_total
            self.mejor_x_actual = evaluacion.x_actual


class EtapaFuerzaTrabajo:
    """
    Representa una semana individual (etapa i) en el modelo de Programación Dinámica.
    Maneja las alternativas x_i, los estados de entrada x_{i-1} y la resolución recursiva.
    """

    def __init__(self, semana: int, b_requerido: int, estados_entrada: List[int], alternativas: List[int]):
        self.semana = semana
        self.b_requerido = b_requerido
        self.estados_entrada = sorted(estados_entrada)
        self.alternativas = sorted(alternativas)
        self.estados: Dict[int, EstadoEtapa] = {}

    def resolver(self, etapa_siguiente: Optional["EtapaFuerzaTrabajo"], politica: PoliticaCostos):
        """
        Aplica la ecuación recursiva de Bellman para la etapa:
        f_i(x_{i-1}) = min_{x_i >= b_i} { C_1(x_i - b_i) + C_2(x_i - x_{i-1}) + f_{i+1}(x_i) }
        """
        for x_prev in self.estados_entrada:
            estado = EstadoEtapa(x_prev)
            for x_act in self.alternativas:
                c_exc, c_trans, c_inm = politica.calcular_costo_inmediato(x_act, x_prev, self.b_requerido)

                # Costo futuro acumulado f_{i+1}(x_i)
                if etapa_siguiente is None:
                    c_futuro = 0.0
                else:
                    if x_act in etapa_siguiente.estados:
                        c_futuro = etapa_siguiente.estados[x_act].costo_minimo
                    else:
                        raise ValueError(f"El estado x_{self.semana}={x_act} no existe en la etapa siguiente.")

                c_total = c_inm + c_futuro
                evaluacion = EvaluacionAlternativa(
                    x_previo=x_prev,
                    x_actual=x_act,
                    costo_excedente=c_exc,
                    costo_transicion=c_trans,
                    costo_inmediato=c_inm,
                    costo_futuro=c_futuro,
                    costo_total=c_total,
                )
                estado.registrar_alternativa(evaluacion)

            self.estados[x_prev] = estado


@dataclass
class ResumenSemanal:
    """Estructura de datos para presentar la política óptima semana a semana."""
    semana: int
    req_minimo: int
    fuerza_inicial: int
    fuerza_optima: int
    accion_decision: str
    variacion_personal: int
    costo_excedente: float
    costo_contratacion: float
    costo_semana: float
    costo_acumulado: float


class ModeloFuerzaTrabajoDP:
    """
    Controlador general del Modelo de Tamaño de la Fuerza de Trabajo.
    Orquesta la configuración de etapas, la recursividad hacia atrás y el resumen final.
    """

    def __init__(self, requerimientos: List[int], politica: PoliticaCostos, fuerza_inicial: int = 0):
        self._validar_requerimientos(requerimientos)
        self._validar_fuerza_inicial(fuerza_inicial)

        self.requerimientos = requerimientos
        self.politica = politica
        self.fuerza_inicial = fuerza_inicial
        self.n_semanas = len(requerimientos)
        self.etapas: Dict[int, EtapaFuerzaTrabajo] = {}
        self.plan_optimo: List[ResumenSemanal] = []

    @staticmethod
    def _validar_requerimientos(requerimientos) -> None:
        """Las demandas deben ser una lista no vacia de enteros >= 0 (nunca bool ni float)."""
        if not isinstance(requerimientos, list) or not requerimientos:
            raise ValueError("requerimientos (demandas) debe ser una lista no vacia de enteros mayores o iguales a 0.")
        for b in requerimientos:
            if isinstance(b, bool) or not isinstance(b, int) or b < 0:
                raise ValueError(f"Cada demanda debe ser un entero mayor o igual a 0 (se recibio {b!r}).")

    @staticmethod
    def _validar_fuerza_inicial(fuerza_inicial) -> None:
        """La fuerza inicial x_0 debe ser un entero >= 0 (nunca bool ni float)."""
        if isinstance(fuerza_inicial, bool) or not isinstance(fuerza_inicial, int) or fuerza_inicial < 0:
            raise ValueError(f"fuerza_inicial debe ser un entero mayor o igual a 0 (se recibio {fuerza_inicial!r}).")

    def configurar_espacios_estados(self):
        """
        Calcula los espacios de estados y de alternativas a partir de las demandas,
        en vez de usar los conjuntos fijos de la guia teorica:

        - Alternativas de la semana i: x_i en el rango [b_i, max(b_i, ..., b_n)]. Nunca
          conviene tener menos personal que lo que exige la semana (x_i < b_i no es
          factible) ni mas que la mayor demanda que queda por cubrir de ahi en adelante
          (tener mas no evita ningun costo futuro y solo agrega costo de excedente).
        - Estados de entrada x_{i-1}: en la semana 1 es [fuerza_inicial] (x_0); de la
          semana 2 en adelante son las alternativas de la semana anterior, porque el
          estado de entrada de una etapa es la decision que se tomo en la etapa previa.

        Con las demandas de la tarea (5, 7, 8, 4, 6) este calculo reproduce exactamente
        los conjuntos de la guia de clase: x1 en {5,6,7,8}, x2 en {7,8}, x3 en {8},
        x4 en {4,5,6}, x5 en {6}.
        """
        alternativas_por_semana: Dict[int, List[int]] = {}
        for i in range(1, self.n_semanas + 1):
            b_i = self.requerimientos[i - 1]
            maximo_restante = max(self.requerimientos[i - 1:])
            alternativas_por_semana[i] = list(range(b_i, maximo_restante + 1))

        for semana in range(1, self.n_semanas + 1):
            b = self.requerimientos[semana - 1]
            alternativas = alternativas_por_semana[semana]
            estados = [self.fuerza_inicial] if semana == 1 else alternativas_por_semana[semana - 1]
            self.etapas[semana] = EtapaFuerzaTrabajo(semana, b, estados, alternativas)

    def resolver(self):
        """Ejecuta la recursividad hacia atrás (de la semana 5 a la 1)."""
        if not self.etapas:
            self.configurar_espacios_estados()

        for semana in range(self.n_semanas, 0, -1):
            siguiente = self.etapas.get(semana + 1, None)
            self.etapas[semana].resolver(siguiente, self.politica)

        self.reconstruir_politica_optima()

    def reconstruir_politica_optima(self):
        """Reconstruye la trayectoria óptima hacia adelante desde x_0 hasta x_n."""
        self.plan_optimo.clear()
        x_actual = self.fuerza_inicial
        acumulado = 0.0

        for semana in range(1, self.n_semanas + 1):
            etapa = self.etapas[semana]
            estado = etapa.estados[x_actual]
            x_siguiente = estado.mejor_x_actual

            c_exc = self.politica.calcular_costo_excedente(x_siguiente, etapa.b_requerido)
            c_con = self.politica.calcular_costo_contratacion(x_siguiente, x_actual)
            costo_sem = c_exc + c_con
            acumulado += costo_sem

            dif = x_siguiente - x_actual
            if dif > 0:
                accion = f"Contratar {dif} trabajadores"
            elif dif < 0:
                accion = f"Despedir {abs(dif)} trabajadores"
            else:
                accion = "Ningun cambio"

            if x_siguiente > etapa.b_requerido:
                exceso = x_siguiente - etapa.b_requerido
                accion += f" ({exceso} excedente{'s' if exceso > 1 else ''})"

            self.plan_optimo.append(
                ResumenSemanal(
                    semana=semana,
                    req_minimo=etapa.b_requerido,
                    fuerza_inicial=x_actual,
                    fuerza_optima=x_siguiente,
                    accion_decision=accion,
                    variacion_personal=dif,
                    costo_excedente=c_exc,
                    costo_contratacion=c_con,
                    costo_semana=costo_sem,
                    costo_acumulado=acumulado,
                )
            )
            x_actual = x_siguiente
