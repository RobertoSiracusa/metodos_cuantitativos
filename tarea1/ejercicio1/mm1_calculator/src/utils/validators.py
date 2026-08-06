def validate_positive_rate(value: float, name: str) -> None:
    if not isinstance(value, (int, float)):
        raise TypeError(f'{name} must be a number')
    if value <= 0:
        raise ValueError(f'{name} must be positive')


def validate_stable_system(lamb: float, mu: float) -> None:
    if lamb >= mu:
        raise ValueError('System is unstable: lambda must be less than mu (rho < 1)')
