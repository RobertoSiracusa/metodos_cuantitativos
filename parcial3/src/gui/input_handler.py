"""
Traduccion de eventos de teclado y mouse a comandos sobre el estado de la app.

Patron tomado de clasePrompts/estacion/src/engine/input_handler.py. El estado
de la aplicacion (`AppState`, definido en app.py) es quien realmente decide
que hacer; este modulo solo interpreta los eventos de Pygame y llama a los
metodos correspondientes, sin guardar nada por su cuenta.

Controles (ver el brief / README para la tabla completa):
  ESPACIO  pausa/reanuda la ANIMACION (el motor sigue calculando)
  P        pausa total (motor incluido)
  1-4      escala de tiempo
  R        reinicia la vista actual
  ESC      vuelve al selector; desde el selector, sale
"""

import pygame

TECLA_A_NIVEL_ESCALA = {
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_4: 4,
}


class InputHandler:
    """Procesa la cola de eventos de Pygame y actualiza el AppState recibido."""

    @staticmethod
    def procesar_eventos(estado) -> bool:
        """
        Consume pygame.event.get() y aplica los comandos sobre `estado`.

        Devuelve False si el usuario pidio salir de la aplicacion por
        completo (cerrar ventana, o ESC desde el selector). True para seguir.
        """
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

            if evento.type == pygame.KEYDOWN:
                if not InputHandler._procesar_tecla(estado, evento.key):
                    return False

            elif evento.type == pygame.MOUSEBUTTONDOWN and estado.pantalla == "selector":
                InputHandler._procesar_click_selector(estado, evento.pos)

        return True

    @staticmethod
    def _procesar_tecla(estado, tecla: int) -> bool:
        """Devuelve False solo cuando corresponde salir de la aplicacion."""
        if estado.pantalla == "selector":
            if tecla == pygame.K_ESCAPE:
                return False
            if tecla == pygame.K_1:
                estado.ir_a_vista(problema=1)
            elif tecla == pygame.K_2:
                estado.ir_a_vista(problema=2)
            return True

        # pantalla == "vista"
        controller = estado.controller
        if tecla == pygame.K_ESCAPE:
            estado.ir_a_selector()
        elif tecla == pygame.K_SPACE:
            controller.pausa_animacion = not controller.pausa_animacion
        elif tecla == pygame.K_p:
            controller.pausa_total = not controller.pausa_total
        elif tecla == pygame.K_r:
            controller.reiniciar()
        elif tecla in TECLA_A_NIVEL_ESCALA:
            controller.fijar_escala(TECLA_A_NIVEL_ESCALA[tecla])
        return True

    @staticmethod
    def _procesar_click_selector(estado, pos) -> None:
        """Traduce un clic del mouse sobre una tarjeta del selector."""
        if estado.tarjeta_problema1.collidepoint(pos):
            estado.ir_a_vista(problema=1)
        elif estado.tarjeta_problema2.collidepoint(pos):
            estado.ir_a_vista(problema=2)


def _selfcheck() -> None:
    """Verifica el mapeo de teclas a niveles de escala, sin abrir pygame."""
    assert TECLA_A_NIVEL_ESCALA[pygame.K_1] == 1
    assert TECLA_A_NIVEL_ESCALA[pygame.K_2] == 2
    assert TECLA_A_NIVEL_ESCALA[pygame.K_3] == 3
    assert TECLA_A_NIVEL_ESCALA[pygame.K_4] == 4
    assert len(TECLA_A_NIVEL_ESCALA) == 4
    print("selfcheck input_handler: OK")


if __name__ == "__main__":
    _selfcheck()
