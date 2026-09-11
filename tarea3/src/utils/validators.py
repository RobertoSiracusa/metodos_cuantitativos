"""
Validadores de Parametros Cuantitativos
"""

def validar_tasa(valor: float, nombre: str = "Tasa") -> float:
    """Valida que una tasa (lambda o mu) sea estrictamente positiva."""
    val = float(valor)
    if val <= 0:
        raise ValueError(f"{nombre} debe ser mayor a 0. Recibido: {val}")
    return val


def validar_capacidad(valor: int, nombre: str = "Capacidad") -> int:
    """Valida que una capacidad de buffer sea un entero mayor o igual a 1."""
    val = int(valor)
    if val < 1:
        raise ValueError(f"{nombre} debe ser al menos 1. Recibido: {val}")
    return val


def validar_politica_inventario(s: int, S: int, Q: int) -> None:
    """Valida la consistencia de los parametros de la politica (s, Q) respecto a S."""
    if s < 0:
        raise ValueError(f"El umbral minimo s no puede ser negativo: {s}")
    if S <= s:
        raise ValueError(f"La capacidad maxima S ({S}) debe ser mayor que el umbral s ({s})")
    if Q <= 0:
        raise ValueError(f"El lote de reposicion Q ({Q}) debe ser mayor que cero")
