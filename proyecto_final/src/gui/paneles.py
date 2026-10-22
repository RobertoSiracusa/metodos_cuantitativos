"""Paneles del dashboard Pygame (R8, R9, R10). Cada panel solo lee EstadoSimulacion."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pygame

from src.simulation.motor_simpy import EstadoSimulacion

FONDO = (24, 26, 32)
FONDO_PANEL = (34, 37, 46)
BORDE = (60, 64, 78)
TEXTO = (220, 222, 230)
TEXTO_TENUE = (140, 145, 160)
VERDE = (80, 200, 120)
ROJO = (230, 80, 80)
AMARILLO = (240, 200, 80)
AZUL = (90, 160, 240)
NARANJA = (245, 150, 70)
COLORES_CLUSTER = [(90, 160, 240), (180, 120, 240), (80, 200, 200), (240, 130, 180)]

_fuentes: dict[int, pygame.font.Font] = {}


def fuente(tamano: int) -> pygame.font.Font:
    if tamano not in _fuentes:
        _fuentes[tamano] = pygame.font.SysFont("menlo,consolas,monospace", tamano)
    return _fuentes[tamano]


def texto(superficie: pygame.Surface, cadena: str, pos: tuple[int, int], color=TEXTO, tamano: int = 13) -> None:
    superficie.blit(fuente(tamano).render(cadena, True, color), pos)


def serie(
    superficie: pygame.Surface,
    rect: pygame.Rect,
    xs: list[float],
    ys: list[float],
    color,
    rango_x: tuple[float, float],
    rango_y: tuple[float, float],
    ancho: int = 2,
) -> None:
    """Dibuja una polilinea escalando (x, y) al rectangulo `rect`."""
    if len(xs) < 2:
        return
    (x0, x1), (y0, y1) = rango_x, rango_y
    dx = (x1 - x0) or 1.0
    dy = (y1 - y0) or 1.0
    puntos = [
        (rect.left + (x - x0) / dx * rect.width, rect.bottom - (y - y0) / dy * rect.height)
        for x, y in zip(xs, ys)
    ]
    pygame.draw.lines(superficie, color, False, puntos, ancho)


class Panel(ABC):
    """Area rectangular del dashboard. La aplicacion hace `for p in paneles: p.dibujar(...)`."""

    def __init__(self, rect: pygame.Rect, titulo: str) -> None:
        self.rect = rect
        self.titulo = titulo

    def dibujar(self, superficie: pygame.Surface, estado: EstadoSimulacion) -> None:
        pygame.draw.rect(superficie, FONDO_PANEL, self.rect, border_radius=6)
        pygame.draw.rect(superficie, BORDE, self.rect, 1, border_radius=6)
        texto(superficie, self.titulo, (self.rect.left + 10, self.rect.top + 6), TEXTO, 14)
        self._contenido(superficie, estado, self.rect.inflate(-24, -40).move(0, 10))

    @abstractmethod
    def _contenido(self, superficie: pygame.Surface, estado: EstadoSimulacion, area: pygame.Rect) -> None:
        raise NotImplementedError


class PanelTopologia(Panel):
    """R8 + R9: topologia, paquetes animados, nodos caidos y rutas optimas con destello al cambiar."""

    DURACION_DESTELLO = 3.0  # unidades de tiempo de simulacion

    def __init__(self, rect: pygame.Rect) -> None:
        super().__init__(rect, "Topologia de la red  (R8, R9)")
        self._ultima_ruta: dict[str, tuple[str, ...]] = {}
        self._cambio_en: dict[str, float] = {}

    def _a_pantalla(self, pos: tuple[float, float], area: pygame.Rect) -> tuple[int, int]:
        # las posiciones del escenario estan en un lienzo de ~800 x 500
        return int(area.left + pos[0] / 800 * area.width), int(area.top + pos[1] / 500 * area.height)

    def _contenido(self, superficie, estado, area):
        pos = {nid: self._a_pantalla(p, area) for nid, p in estado.posiciones.items()}

        for cid, ruta in estado.rutas.items():
            if cid in self._ultima_ruta and self._ultima_ruta[cid] != ruta:
                self._cambio_en[cid] = estado.tiempo
            self._ultima_ruta[cid] = ruta

        for (a, b), ocupacion in estado.ocupacion_enlaces.items():
            color = tuple(int(c1 + (c2 - c1) * min(ocupacion / 0.6, 1)) for c1, c2 in zip(BORDE, ROJO))
            pygame.draw.line(superficie, color, pos[a], pos[b], 1 + int(ocupacion * 6))

        for i, (cid, ruta) in enumerate(estado.rutas.items()):
            color = COLORES_CLUSTER[i % len(COLORES_CLUSTER)]
            destello = estado.tiempo - self._cambio_en.get(cid, -1e9) < self.DURACION_DESTELLO
            if destello and int(estado.tiempo * 4) % 2 == 0:
                color = AMARILLO
            desplazamiento = (i - 1.5) * 2
            for a, b in zip(ruta, ruta[1:]):
                pa = (pos[a][0], pos[a][1] + desplazamiento)
                pb = (pos[b][0], pos[b][1] + desplazamiento)
                pygame.draw.line(superficie, color, pa, pb, 4 if destello else 2)

        for cid, servidores in estado.clusteres.items():
            tor = pos[estado.tor_de_cluster[cid]]
            for sid in servidores:
                pygame.draw.line(superficie, BORDE, tor, pos[sid], 1)

        for pid, a, b, progreso in estado.en_transito:
            x = pos[a][0] + (pos[b][0] - pos[a][0]) * progreso
            y = pos[a][1] + (pos[b][1] - pos[a][1]) * progreso
            pygame.draw.circle(superficie, AMARILLO, (int(x), int(y)), 3)

        for nid, p in pos.items():
            operativo = estado.operativos[nid]
            if estado.capas[nid] == "servidor":
                carga = estado.carga_servidores[nid]
                caja = pygame.Rect(0, 0, 46, 18)
                caja.center = p
                pygame.draw.rect(superficie, FONDO, caja)
                relleno = caja.copy()
                relleno.width = int(caja.width * carga / 100)
                pygame.draw.rect(superficie, NARANJA if carga > 70 else VERDE, relleno)
                pygame.draw.rect(superficie, TEXTO if operativo else ROJO, caja, 1 if operativo else 2)
                texto(superficie, f"{nid} q{estado.colas[nid]}", (caja.right + 4, caja.top + 2), TEXTO if operativo else ROJO, 11)
            else:
                pygame.draw.circle(superficie, AZUL if operativo else ROJO, p, 13)
                if not operativo:
                    pygame.draw.line(superficie, TEXTO, (p[0] - 8, p[1] - 8), (p[0] + 8, p[1] + 8), 2)
                    pygame.draw.line(superficie, TEXTO, (p[0] - 8, p[1] + 8), (p[0] + 8, p[1] - 8), 2)
                etiqueta = fuente(11).render(nid, True, FONDO if operativo else TEXTO)
                superficie.blit(etiqueta, etiqueta.get_rect(center=p))

        y = area.bottom - 16
        for i, cid in enumerate(estado.rutas):
            color = COLORES_CLUSTER[i % len(COLORES_CLUSTER)]
            pygame.draw.line(superficie, color, (area.left + i * 90, y + 7), (area.left + i * 90 + 18, y + 7), 3)
            texto(superficie, f"ruta {cid}", (area.left + i * 90 + 22, y), TEXTO_TENUE, 11)
        texto(superficie, "amarillo parpadeante = la ruta cambio", (area.left + 380, y), AMARILLO, 11)


class PanelTermico(Panel):
    """R3: curva T(c) con puntos estacionarios, inflexion, punto critico y la carga actual."""

    def __init__(self, rect: pygame.Rect) -> None:
        super().__init__(rect, "Modelo termico T(c)  (R3)")

    def _contenido(self, superficie, estado, area):
        cs = [c for c, _ in estado.curva_termica]
        ts = [t for _, t in estado.curva_termica]
        rango_y = (min(ts) - 2, max(ts) + 2)
        grafico = area.inflate(0, -20).move(0, 10)

        def a_pantalla(c, t):
            return (
                int(grafico.left + c / 100 * grafico.width),
                int(grafico.bottom - (t - rango_y[0]) / (rango_y[1] - rango_y[0]) * grafico.height),
            )

        if estado.punto_critico is not None:
            x = a_pantalla(estado.punto_critico, rango_y[0])[0]
            pygame.draw.rect(superficie, (70, 40, 44), (x, grafico.top, grafico.right - x, grafico.height))
        serie(superficie, grafico, cs, ts, TEXTO, (0, 100), rango_y)
        for c, t, tipo in estado.puntos_estacionarios:
            pygame.draw.circle(superficie, VERDE if tipo == "minimo" else NARANJA, a_pantalla(c, t), 5)
            texto(superficie, f"{tipo} {c:.0f}%", (a_pantalla(c, t)[0] - 30, a_pantalla(c, t)[1] - 18), TEXTO_TENUE, 11)
        if estado.punto_inflexion is not None:
            c = estado.punto_inflexion
            pygame.draw.circle(superficie, AZUL, a_pantalla(c, ts[int(round(c))]), 5)
        pygame.draw.circle(superficie, ROJO if estado.emergencia else AMARILLO, a_pantalla(estado.carga, estado.temperatura), 7, 2)

        estado_txt = "EMERGENCIA" if estado.emergencia else "normal"
        texto(
            superficie,
            f"carga {estado.carga:5.1f}%  T {estado.temperatura:5.1f} C  critico {estado.punto_critico or 0:.0f}%  {estado_txt}",
            (area.left, area.top - 4),
            ROJO if estado.emergencia else TEXTO_TENUE,
            11,
        )


class PanelGradiente(Panel):
    """R4 + R10: trayectoria de la velocidad del ventilador v(t) frente al optimo v*(t)."""

    VENTANA = 60.0

    def __init__(self, rect: pygame.Rect) -> None:
        super().__init__(rect, "Gradiente: velocidad del ventilador  (R4)")

    def _contenido(self, superficie, estado, area):
        s = estado.series_gradiente
        if not s.get("tiempo"):
            return
        t1 = s["tiempo"][-1]
        t0 = max(0.0, t1 - self.VENTANA)
        desde = next(i for i, t in enumerate(s["tiempo"]) if t >= t0)
        grafico = area.inflate(0, -20).move(0, 10)
        rango_y = (0, max(max(s["velocidad"][desde:]), max(s["velocidad_optima"][desde:])) * 1.2)
        serie(superficie, grafico, s["tiempo"][desde:], s["velocidad_optima"][desde:], TEXTO_TENUE, (t0, t1 or 1), rango_y, 1)
        serie(superficie, grafico, s["tiempo"][desde:], s["velocidad"][desde:], AZUL, (t0, t1 or 1), rango_y)
        texto(
            superficie,
            f"v = {s['velocidad'][-1]:.3f}   v* = {s['velocidad_optima'][-1]:.3f}   E(v) = {s['energia'][-1]:.3f}",
            (area.left, area.top - 4),
            TEXTO_TENUE,
            11,
        )


class PanelLagrange(Panel):
    """R5 + R10: barras de energia asignada a cada cluster y evolucion de lambda."""

    VENTANA = 60.0

    def __init__(self, rect: pygame.Rect) -> None:
        super().__init__(rect, "Lagrange: reparto de energia  (R5)")

    def _contenido(self, superficie, estado, area):
        mitad = area.width // 2
        barras = pygame.Rect(area.left, area.top + 14, mitad - 10, area.height - 14)
        total = sum(estado.energia_clusteres.values()) or 1.0
        ancho = barras.width // max(len(estado.energia_clusteres), 1)
        for i, (cid, energia) in enumerate(estado.energia_clusteres.items()):
            alto = int(energia / total * (barras.height - 18))
            caja = pygame.Rect(barras.left + i * ancho + 4, barras.bottom - 14 - alto, ancho - 8, alto)
            pygame.draw.rect(superficie, COLORES_CLUSTER[i % len(COLORES_CLUSTER)], caja)
            texto(superficie, f"{cid} {energia:.0f}", (caja.left, barras.bottom - 12), TEXTO_TENUE, 10)

        s = estado.series_lagrange
        texto(superficie, f"lambda = {estado.lambda_:.4f}", (area.left + mitad, area.top - 4), TEXTO_TENUE, 11)
        if s.get("tiempo"):
            t1 = s["tiempo"][-1]
            t0 = max(0.0, t1 - self.VENTANA)
            desde = next(i for i, t in enumerate(s["tiempo"]) if t >= t0)
            lambdas = s["lambda"][desde:]
            grafico = pygame.Rect(area.left + mitad, area.top + 14, mitad, area.height - 14)
            serie(superficie, grafico, s["tiempo"][desde:], lambdas, AMARILLO, (t0, t1 or 1), (0, max(lambdas) * 1.2 or 1))


class PanelEventos(Panel):
    """Registro de eventos (fallas, cambios de ruta, emergencias) y metricas de colas."""

    COLORES = {"falla": ROJO, "reparacion": VERDE, "cambio_ruta": AMARILLO, "emergencia": ROJO, "normal": VERDE}

    def __init__(self, rect: pygame.Rect) -> None:
        super().__init__(rect, "Eventos y metricas  (R6)")

    def _contenido(self, superficie, estado, area):
        filas = max((area.height) // 15, 1)
        for i, evento in enumerate(reversed(estado.eventos[-filas:])):
            texto(
                superficie,
                f"t={evento.tiempo:6.1f} {evento.tipo:<11} {evento.mensaje}"[:70],
                (area.left, area.top + i * 15),
                self.COLORES.get(evento.tipo, TEXTO),
                11,
            )
        m = estado.metricas
        lineas = [
            f"generados   {m['generados']}",
            f"completados {m['completados']}",
            f"perdidos    {m['perdidos']}",
            f"Wq  {m['Wq']:.3f}",
            f"W   {m['W']:.3f}",
            f"Lq  {m['Lq']:.3f}",
            f"util {100 * m['utilizacion']:.1f} %",
            f"thr {m['throughput']:.3f}/t",
        ]
        x = area.left + int(area.width * 0.72)
        for i, linea in enumerate(lineas):
            texto(superficie, linea, (x, area.top + i * 15), TEXTO, 12)
