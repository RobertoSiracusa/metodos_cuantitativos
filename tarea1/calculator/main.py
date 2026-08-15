import argparse
import os
import sys

# Ensure local `src` package is importable when running the script directly
HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from src.core.mm1_model import MM1Model
from src.core.mmc_model import MMCModel
from src.core.mg_model import MD1Model, MDCModel, MG1Model, MGCModel
from src.services.reporter import ReportService


def format_value(name: str, value: float, extra: str = '') -> str:
    return f"{name}: {value:.6f}{('  ' + extra) if extra else ''}"


def main():
    parser = argparse.ArgumentParser(description='MM1 Calculator (CLI)')
    parser.add_argument('--servers', dest='servers', type=int, default=1,
                        help='Número de servidores. Default: 1')
    parser.add_argument('--lambda', dest='lamb', type=float, default=0.8,
                        help='Tasa de llegada (llegadas por minuto). Default: 0.8')
    parser.add_argument('--mu', dest='mu', type=float, default=1.0,
                        help='Tasa de servicio (servicios por minuto). Default: 1.0')
    parser.add_argument('--k', dest='k', type=int, default=3,
                        help='Valor k para P(n>k). Default: 3')
    parser.add_argument('--exercise', dest='exercise', choices=['1', '2'], default='1',
                        help='Ejercicio a ejecutar: 1 para M/M/1, 2 para M/M/c. Default: 1')
    parser.add_argument('--model', dest='model', default=None,
                        choices=['mm1', 'mmc', 'md1', 'mdc', 'mg1', 'mgc'],
                        help='Modelo a usar. Si se omite, se deduce de --exercise/--servers')
    parser.add_argument('--sigma', dest='sigma', type=float, default=0.0,
                        help='Desviación estándar del tiempo de servicio (M/G/1, M/G/c). Default: 0')
    parser.add_argument('--no-steps', dest='no_steps', action='store_true',
                        help='Desactiva la salida paso a paso (activada por default).')

    args = parser.parse_args()

    lamb = args.lamb
    mu = args.mu
    k = args.k
    servers = args.servers

    if args.exercise == '2':
        if lamb == 0.8:
            lamb = 15.0
        if mu == 1.0:
            mu = 6.0
        if servers == 1:
            servers = 3

    if args.model in ('md1', 'mdc', 'mg1', 'mgc'):
        cls = {'md1': MD1Model, 'mdc': MDCModel, 'mg1': MG1Model, 'mgc': MGCModel}[args.model]
        if args.model in ('md1', 'mg1'):
            servers = 1
        model = cls(lamb=lamb, mu=mu, servers=servers, sigma=args.sigma)
        label = f'M/{"D" if args.model.startswith("md") else "G"}/{servers}'
    elif args.model == 'mm1' or (args.model is None and args.exercise == '1' and servers == 1):
        model = MM1Model(lamb, mu)
        label = 'M/M/1'
    else:
        model = MMCModel(lamb, mu, servers)
        label = f'M/M/{servers}'
    reporter = ReportService(model)

    if not args.no_steps:
        if hasattr(model, 'prob_more_than') and not hasattr(model, 'sigma'):
            steps = model.steps(k)
        else:
            steps = model.steps()
        note = model.steps_note() if hasattr(model, 'steps_note') else None
        print(f'\n{label} - Desarrollo paso a paso')
        print('--------------------------------')
        print(reporter.generate_steps_report(steps, note))

    # Print a clear per-formula output
    print(f'\n{label} - Resultados detallados')
    print('--------------------------------')
    print(format_value('Lambda (llegadas/min)', model.lamb))
    print(format_value('Mu (servicios/min)', model.mu))
    print(format_value('Servidores', getattr(model, 'servers', 1)))
    print(format_value('Rho (utilizacion)', model.rho, 'rho = lambda / (c * mu)'))
    print(format_value('P0 (sistema vacío)', model.p0))
    print(format_value('L (en sistema)', model.l))
    print(format_value('Lq (en cola)', model.lq))
    print(format_value('W (tiempo en sistema)', model.w))
    print(format_value('Wq (tiempo en cola)', model.wq))
    if hasattr(model, 'sigma'):
        print(format_value('Sigma (desv. est. servicio)', model.sigma))
        print(format_value('Cs^2 (coef. variacion^2)', model.scv))
    if getattr(model, 'supports_pw', True) and hasattr(model, 'pw'):
        print(format_value('Pw (Erlang-C)', model.pw))
    if hasattr(model, 'prob_more_than'):
        print(format_value(f'P(n > {k})', model.prob_more_than(k), f'rho^(k+1) with k={k}'))

    # Also print the compact reporter summary
    print('\nResumen:\n')
    if hasattr(model, 'sigma'):
        print(reporter.generate_general_report(label))
    elif getattr(model, 'servers', 1) == 1:
        print(reporter.generate_text_report())
    else:
        print(reporter.generate_mmc_report('horas'))


if __name__ == '__main__':
    main()
