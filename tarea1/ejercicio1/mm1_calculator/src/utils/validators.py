def validate_positive_rate(value: float, name: str) -> None:
    if not isinstance(value, (int, float)):
        raise TypeError(f'{name} must be a number')
    if value <= 0:
        raise ValueError(f'{name} must be positive')


def validate_servers(servers: int) -> None:
    if not isinstance(servers, int):
        raise TypeError('servers must be an integer')
    if servers < 1:
        raise ValueError('servers must be greater than or equal to 1')


def validate_stable_system(lamb: float, mu: float, servers: int = 1) -> None:
    if lamb >= servers * mu:
        raise ValueError('System is unstable: lambda must be less than servers * mu (rho < 1)')
