from typing import Any


class ReportService:
    _LABEL_WIDTH = 14  # len('Sustitucion:') + 2, alinea las tres etiquetas

    def __init__(self, model: Any):
        self.model = model

    def generate_steps_report(self, steps, note=None) -> str:
        """Formatea el desarrollo paso a paso: Formula / Sustitucion / Resultado."""
        lines = []
        for i, (title, formula, sustitucion, resultado) in enumerate(steps, start=1):
            lines.append(f'Paso {i} - {title}')
            lines.append(f'  {"Formula:".ljust(self._LABEL_WIDTH)}{formula}')
            lines.append(f'  {"Sustitucion:".ljust(self._LABEL_WIDTH)}{sustitucion}')
            lines.append(f'  {"Resultado:".ljust(self._LABEL_WIDTH)}{resultado}')
            lines.append('')
        if note:
            lines.append(note)
            lines.append('')
        return '\n'.join(lines).rstrip('\n')

    def generate_text_report(self) -> str:
        lines = []
        lines.append('M/M/1 Reporte')
        lines.append('---------------')
        lines.append(f'Lambda (llegadas/min): {self.model.lamb:.4f}')
        lines.append(f'Mu (servicios/min): {self.model.mu:.4f}')
        lines.append(f'Factor de utilización (rho): {self.model.rho:.4f}')
        lines.append(f'P0 (servidor ocioso): {self.model.p0:.4f}')
        lines.append(f'L (en sistema): {self.model.l:.4f}')
        lines.append(f'Lq (en cola): {self.model.lq:.4f}')
        lines.append(f'W (tiempo en sistema, min): {self.model.w:.4f}')
        lines.append(f'Wq (tiempo en cola, min): {self.model.wq:.4f}')
        k = 3
        lines.append(f'P(n > {k}): {self.model.prob_more_than(k):.6f}')
        return '\n'.join(lines)

    def generate_general_report(self, label: str, time_unit: str = 'minutos') -> str:
        """Reporte para modelos de servicio general (M/G/c, M/D/c). Sin Erlang-C."""
        m = self.model
        lines = []
        lines.append(f'{label} Reporte')
        lines.append('----------------')
        lines.append(f'Lambda (llegadas/{time_unit}): {m.lamb:.4f}')
        lines.append(f'Mu (servicios/{time_unit}): {m.mu:.4f}')
        lines.append(f'Servidores: {m.servers}')
        lines.append(f'Sigma (desv. est. del servicio): {m.sigma:.4f}')
        lines.append(f'Cs^2 (coef. variación al cuadrado): {m.scv:.4f}')
        lines.append(f'Factor de utilización (rho): {m.rho:.4f}')
        lines.append(f'P0 (sistema vacío): {m.p0:.4f}')
        lines.append(f'Lq (en cola): {m.lq:.4f}')
        lines.append(f'L (en sistema): {m.l:.4f}')
        lines.append(f'Wq (tiempo en cola, {time_unit}): {m.wq:.4f}')
        lines.append(f'W (tiempo en sistema, {time_unit}): {m.w:.4f}')
        if not m.is_exact:
            lines.append('Nota: c > 1 con servicio general usa la aproximación de Allen-Cunneen.')
        return '\n'.join(lines)

    def generate_mmc_report(self, time_unit: str = 'horas') -> str:
        lines = []
        lines.append(f'M/M/{getattr(self.model, "servers", 1)} Reporte')
        lines.append('----------------')
        lines.append(f'Lambda (llegadas/{time_unit}): {self.model.lamb:.4f}')
        lines.append(f'Mu (servicios/{time_unit}): {self.model.mu:.4f}')
        lines.append(f'Servidores: {self.model.servers}')
        lines.append(f'Factor de utilización (rho): {self.model.rho:.4f}')
        lines.append(f'P0 (sistema vacío): {self.model.p0:.4f}')
        lines.append(f'Lq (en cola): {self.model.lq:.4f}')
        lines.append(f'W (tiempo en sistema, {time_unit}): {self.model.w:.4f}')
        lines.append(f'W ({time_unit}) = {self.model.w:.4f} | {self.model.w * 60:.2f} minutos')
        lines.append(f'Pw (Erlang-C): {self.model.pw:.4f}')
        return '\n'.join(lines)
