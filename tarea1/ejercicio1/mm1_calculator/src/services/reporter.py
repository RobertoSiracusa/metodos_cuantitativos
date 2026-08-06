from typing import Any


class ReportService:
    def __init__(self, model: Any):
        self.model = model

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
