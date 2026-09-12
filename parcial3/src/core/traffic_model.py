"""
Generador de trafico entrante del Problema 2.

El enunciado especifica una Normal(media 3 Gbps, desviacion 1 Gbps) TRUNCADA al
rango [1, 5] Gbps. Truncar no es recortar: se descarta la muestra fuera de rango
y se vuelve a sortear (rejection sampling), que es la definicion de la normal
truncada y preserva la forma de la campana dentro del intervalo. Recortar al
limite (clipping) acumularia masa de probabilidad en 1 y en 5, creando dos picos
artificiales que no existen en el modelo.

Con media 3, desviacion 1 y limites en +/- 2 sigma, la tasa de rechazo es ~4.6%,
asi que el sorteo converge en muy pocos intentos.
"""

import random
from typing import List, Optional

from src.utils.config import (
    TRAFICO_DESV_GBPS,
    TRAFICO_MAX_GBPS,
    TRAFICO_MEDIA_GBPS,
    TRAFICO_MIN_GBPS,
)
from src.utils.validators import ValidacionError, validar_rango_trafico

# Tope de reintentos del rejection sampling antes de caer al recorte de seguridad.
# Con los parametros del enunciado la probabilidad de agotarlo es ~0.046^200,
# es decir, practicamente nula: es una red de seguridad, no el camino normal.
MAX_INTENTOS_SORTEO = 200


class GeneradorTrafico:
    """
    Sortea la demanda instantanea del cluster en Gbps.

    Se inyecta el generador aleatorio para que las corridas sean reproducibles
    con una semilla fija (requisito de los tests y de la entrega).
    """

    def __init__(
        self,
        media: float = TRAFICO_MEDIA_GBPS,
        desviacion: float = TRAFICO_DESV_GBPS,
        minimo: float = TRAFICO_MIN_GBPS,
        maximo: float = TRAFICO_MAX_GBPS,
        semilla: Optional[int] = None,
    ) -> None:
        if desviacion <= 0:
            raise ValidacionError(
                f"La desviacion del trafico debe ser positiva. Recibido: {desviacion}."
            )
        validar_rango_trafico(minimo, maximo)
        if not (minimo <= media <= maximo):
            raise ValidacionError(
                f"La media del trafico ({media}) debe caer dentro del rango "
                f"[{minimo}, {maximo}]; si no, casi toda la masa se rechaza."
            )

        self.media = float(media)
        self.desviacion = float(desviacion)
        self.minimo = float(minimo)
        self.maximo = float(maximo)
        self._rng = random.Random(semilla)
        self.muestras_rechazadas: int = 0
        self.muestras_generadas: int = 0

    def muestrear(self) -> float:
        """
        Devuelve una muestra de la normal truncada, garantizada en [minimo, maximo].

        Bucle de rechazo: se descartan las colas fuera de rango. El recorte final
        solo se alcanza si se agotan los reintentos, escenario practicamente
        imposible con los parametros del enunciado.
        """
        for _ in range(MAX_INTENTOS_SORTEO):
            valor = self._rng.gauss(self.media, self.desviacion)
            if self.minimo <= valor <= self.maximo:
                self.muestras_generadas += 1
                return valor
            self.muestras_rechazadas += 1

        # Red de seguridad: nunca se devuelve un valor fuera de contrato.
        valor = min(self.maximo, max(self.minimo, self._rng.gauss(self.media, self.desviacion)))
        self.muestras_generadas += 1
        return valor

    def muestrear_serie(self, cantidad: int) -> List[float]:
        """Sortea una serie de muestras independientes."""
        if cantidad < 0:
            raise ValidacionError(f"La cantidad de muestras no puede ser negativa: {cantidad}.")
        return [self.muestrear() for _ in range(cantidad)]

    @property
    def tasa_rechazo(self) -> float:
        """Fraccion de sorteos descartados por caer fuera del rango de truncamiento."""
        intentos = self.muestras_generadas + self.muestras_rechazadas
        if intentos == 0:
            return 0.0
        return self.muestras_rechazadas / intentos

    def __repr__(self) -> str:
        return (
            f"GeneradorTrafico(Normal({self.media}, {self.desviacion}) truncada a "
            f"[{self.minimo}, {self.maximo}] Gbps)"
        )


def _selfcheck() -> None:
    """Verifica truncamiento estricto y media muestral."""
    gen = GeneradorTrafico(semilla=2026)
    muestras = gen.muestrear_serie(20000)
    assert len(muestras) == 20000
    assert all(1.0 <= x <= 5.0 for x in muestras), "se colo una muestra fuera de [1, 5]"
    media = sum(muestras) / len(muestras)
    assert abs(media - 3.0) < 0.05, f"media muestral fuera de tolerancia: {media}"
    assert 0.0 < gen.tasa_rechazo < 0.15, gen.tasa_rechazo

    # Reproducibilidad con la misma semilla
    a = GeneradorTrafico(semilla=7).muestrear_serie(50)
    b = GeneradorTrafico(semilla=7).muestrear_serie(50)
    assert a == b, "el generador no es reproducible con semilla fija"

    try:
        GeneradorTrafico(minimo=5.0, maximo=1.0)
    except ValidacionError:
        pass
    else:
        raise AssertionError("el generador acepto un rango invertido")

    print(f"selfcheck traffic_model: OK (media={media:.4f}, rechazo={gen.tasa_rechazo:.4%})")


if __name__ == "__main__":
    _selfcheck()
