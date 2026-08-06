import argparse
import os
import sys

# Ensure local `src` package is importable when running the script directly
HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from src.core.mm1_model import MM1Model
from src.services.reporter import ReportService


def format_value(name: str, value: float, extra: str = '') -> str:
    return f"{name}: {value:.6f}{('  ' + extra) if extra else ''}"


def main():
    parser = argparse.ArgumentParser(description='MM1 Calculator (CLI)')
    parser.add_argument('--lambda', dest='lamb', type=float, default=0.8,
                        help='Tasa de llegada (llegadas por minuto). Default: 0.8')
    parser.add_argument('--mu', dest='mu', type=float, default=1.0,
                        help='Tasa de servicio (servicios por minuto). Default: 1.0')
    parser.add_argument('--k', dest='k', type=int, default=3,
                        help='Valor k para P(n>k). Default: 3')

    args = parser.parse_args()

    lamb = args.lamb
    mu = args.mu
    k = args.k

    model = MM1Model(lamb, mu)
    reporter = ReportService(model)

    # Print a clear per-formula output
    print('\nM/M/1 - Resultados detallados')
    print('--------------------------------')
    print(format_value('Lambda (llegadas/min)', model.lamb))
    print(format_value('Mu (servicios/min)', model.mu))
    print(format_value('Rho (utilizacion)', model.rho, 'rho = lambda / mu'))
    print(format_value('P0 (servidor ocioso)', model.p0, 'P0 = 1 - rho'))
    print(format_value('L (en sistema)', model.l, 'L = rho / (1 - rho)'))
    print(format_value('Lq (en cola)', model.lq, 'Lq = rho^2 / (1 - rho)'))
    print(format_value('W (tiempo en sistema, min)', model.w, 'W = 1 / (mu - lambda)'))
    print(format_value('Wq (tiempo en cola, min)', model.wq, 'Wq = lambda / (mu * (mu - lambda))'))
    print(format_value(f'P(n > {k})', model.prob_more_than(k), f'rho^(k+1) with k={k}'))

    # Also print the compact reporter summary
    print('\nResumen:\n')
    print(reporter.generate_text_report())


if __name__ == '__main__':
    main()
