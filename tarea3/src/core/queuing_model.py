"""
Modelo de Teoria de Colas (Lineas de Espera M/M/1/K y Redes)
Capa de Modelo Cuantitativo — Metodos Cuantitativos
Universidad Jose Antonio Paez
"""

import math
from typing import Dict, Optional, Tuple


class ModeloColasRed:
    """
    Encapsula el modelado analitico y empirico de Teoria de Colas para la red de computadoras.
    Permite contrastar los resultados teoricos de estado estable con las metricas
    obtenidas en la simulacion estocastica en tiempo real.
    """

    def __init__(
        self,
        lamb: float,
        mu: float,
        capacidad_k: int = 50,
        servidores_paralelos: int = 4
    ):
        """
        :param lamb: Tasa de llegada de paquetes por segundo (lambda).
        :param mu: Tasa de atencion por servidor (paquetes/segundo).
        :param capacidad_k: Capacidad maxima del buffer (K = S + 1 en servidor).
        :param servidores_paralelos: Cantidad de routers en paralelo en la capa core.
        """
        self.lamb = float(lamb)
        self.mu = float(mu)
        self.capacidad_k = int(capacidad_k)
        self.servidores_paralelos = int(servidores_paralelos)

        # Metricas analiticas teoricas
        self.rho = 0.0
        self.p0 = 0.0
        self.prob_bloqueo_pk = 0.0
        self.lambda_efectivo = 0.0
        self.l_teorico = 0.0
        self.lq_teorico = 0.0
        self.w_teorico = 0.0
        self.wq_teorico = 0.0

        # Metricas empiricas (provenientes de la simulacion)
        self.metricas_simuladas: Optional[Dict] = None

    def calcular_teorico(self) -> None:
        """
        Calcula las metricas analiticas de estado estable bajo el modelo M/M/1/K
        distribuido equitativamente entre los routers disponibles.
        """
        # Tasa asignada a cada router individual bajo balanceo ideal
        lambda_nodo = self.lamb / max(1, self.servidores_paralelos)
        k = max(1, self.capacidad_k)

        if self.mu <= 0:
            return

        rho = lambda_nodo / self.mu
        self.rho = rho

        if abs(rho - 1.0) < 1e-7:
            # Caso rho = 1
            self.p0 = 1.0 / (k + 1.0)
            self.prob_bloqueo_pk = self.p0
            self.l_teorico = k / 2.0
        else:
            # Caso rho != 1
            self.p0 = (1.0 - rho) / (1.0 - (rho ** (k + 1)))
            self.prob_bloqueo_pk = self.p0 * (rho ** k)
            self.l_teorico = (rho / (1.0 - rho)) - (((k + 1.0) * (rho ** (k + 1))) / (1.0 - (rho ** (k + 1))))

        # Tasa efectiva admitida (descontando bloqueos por desborde)
        self.lambda_efectivo = lambda_nodo * (1.0 - self.prob_bloqueo_pk)

        if self.lambda_efectivo > 0:
            self.w_teorico = self.l_teorico / self.lambda_efectivo
            self.wq_teorico = max(0.0, self.w_teorico - (1.0 / self.mu))
            self.lq_teorico = self.lambda_efectivo * self.wq_teorico
        else:
            self.w_teorico = 0.0
            self.wq_teorico = 0.0
            self.lq_teorico = 0.0

    def registrar_metricas_simuladas(self, metricas: Dict) -> None:
        """Almacena las metricas observadas en la corrida de simulacion."""
        self.metricas_simuladas = metricas

    def verificar_ley_little(self, l_observado: float, w_observado: float, tasa_efectiva: float) -> Tuple[bool, float]:
        """
        Verifica el cumplimiento de la Ley de Little: L = lambda_eff * W.
        Retorna (cumple: bool, error_porcentual: float).
        """
        l_esperado = tasa_efectiva * w_observado
        if l_esperado > 0:
            error_pct = abs(l_observado - l_esperado) / l_esperado * 100.0
            return (error_pct < 15.0, round(error_pct, 2))
        return (True, 0.0)

    def generar_reporte(self) -> str:
        """Genera un reporte tecnico estructurado del modulo de colas."""
        self.calcular_teorico()
        rep = (
            "==================================================\n"
            "   REPORTE DE TEORIA DE COLAS: RED DE ENLACES M/M/1/K\n"
            "==================================================\n"
            "Parametros de Trafico y Servidores:\n"
            f" - Tasa de Llegada Total (lambda): {self.lamb:.2f} paq/s\n"
            f" - Tasa de Servicio por Servidor (mu): {self.mu:.2f} paq/s\n"
            f" - Numero de Routers Core: {self.servidores_paralelos}\n"
            f" - Capacidad Finita del Sistema (K): {self.capacidad_k} paquetes\n"
            f" - Factor de Utilizacion por Router (rho): {self.rho:.4f}\n\n"
            "Resultados Analiticos de Estado Estable (Por Router):\n"
            f" - Probabilidad de Sistema Vacio (P0): {self.p0:.6f}\n"
            f" - Probabilidad de Bloqueo / Descarte (PK): {self.prob_bloqueo_pk:.6%}\n"
            f" - Promedio de Paquetes en el Sistema (L): {self.l_teorico:.4f}\n"
            f" - Promedio de Paquetes en Cola (Lq): {self.lq_teorico:.4f}\n"
            f" - Tiempo Medio en el Sistema (W): {self.w_teorico:.4f} s\n"
            f" - Tiempo Medio en Cola (Wq): {self.wq_teorico:.4f} s\n"
        )
        if self.metricas_simuladas:
            rep += (
                "\nMetricas Observadas en Simulacion Dinamica:\n"
                f" - Wq Empirico: {self.metricas_simuladas.get('tiempo_medio_cola_wq_s', 0.0):.4f} s\n"
                f" - L Empirico: {self.metricas_simuladas.get('promedio_paquetes_sistema_l', 0.0):.2f}\n"
                f" - Tasa de Perdida Observada: {self.metricas_simuladas.get('tasa_perdida_pct', 0.0):.2f}%\n"
            )
        rep += "==================================================\n"
        return rep
