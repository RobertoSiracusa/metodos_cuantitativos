"""
Fixtures compartidos de la suite.

Regla de la suite: NINGUN test sale a la red. La auditoria con IA se prueba solo
por el motor experto local de respaldo y por la construccion del prompt.

Las corridas de simulacion son deterministas (semilla fija) y de alcance session
para no repetir 28.800 pasos de integracion en cada test.
"""

import sys
from pathlib import Path

import pytest

# La raiz del proyecto debe estar en sys.path para importar el paquete `src`
# al correr pytest desde cualquier directorio.
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.simulation.continuous_sim import ClusterSimulation  # noqa: E402
from src.simulation.discrete_sim import FabricaSimulation  # noqa: E402

SEMILLA_TEST = 2026
HORAS_TEST = 8.0


@pytest.fixture(scope="session")
def metricas_p1():
    """Metricas de una corrida oficial de 8 h del Problema 1, con semilla fija."""
    return FabricaSimulation(semilla=SEMILLA_TEST).ejecutar(HORAS_TEST)


@pytest.fixture(scope="session")
def metricas_p2():
    """Metricas de una corrida oficial de 8 h del Problema 2, con semilla fija."""
    return ClusterSimulation(semilla=SEMILLA_TEST).ejecutar(HORAS_TEST)


@pytest.fixture
def sim_fabrica_corta():
    """Motor de fabrica sin ejecutar, con los parametros oficiales."""
    return FabricaSimulation(semilla=SEMILLA_TEST)


@pytest.fixture
def sim_cluster_corta():
    """Motor de cluster sin ejecutar, con los parametros oficiales."""
    return ClusterSimulation(semilla=SEMILLA_TEST)
