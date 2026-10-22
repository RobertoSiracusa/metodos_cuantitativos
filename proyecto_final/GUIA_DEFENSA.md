# Guía de defensa

Orden sugerido para la defensa presencial (≈ 10 minutos) y respuestas a las preguntas más probables.

## 1. Demostración

1. `python -m pytest -q`: 71 tests en verde.
2. `python main.py --modulo m1`: mostrar la tabla por etapas (f y siguiente de cada nodo) y la
   ruta `GW → N1 → A2 → T1` (2 + 2 + 3 = 7). Después `--fallar A2` para ver cómo cambia la ruta
   (`GW → N1 → A1 → T1`, costo 8). Mochila de C1: P2 + P4 + P6 + P7 = 16 de peso, valor 30.
3. `python main.py --modulo m2`: puntos estacionarios (30 % máx., 70 % mín.), inflexión 50 %,
   punto crítico; el gradiente converge a v* = 1 en ~10 iteraciones; Lagrange suma exactamente E_max.
4. `python main.py`: dashboard. Señalar un nodo caído (rojo), una ruta que parpadea al cambiar
   (R9), la carga cruzando el punto crítico en el panel térmico, v(t) siguiendo a v*(t) y las barras
   de energía moviéndose con la demanda. Pulsar `P` para generar el PDF y abrirlo.

## 2. Dónde está cada concepto

| Concepto | Archivo | Qué mostrar |
|----------|---------|-------------|
| Principio de optimalidad de Bellman | `programacion_dinamica/base.py`, `ruta_mas_corta.py` | `_construir_tabla` recorre las etapas hacia atrás |
| Mochila 0/1 | `programacion_dinamica/mochila.py` | recurrencia `V[i][w]` y la reconstrucción hacia atrás |
| Derivadas y clasificación | `no_lineal/modelo_termico.py` | fórmula de la cuadrática sobre `T'` y signo de `T''` |
| Gradiente | `no_lineal/gradiente_enfriamiento.py` | `_paso`: `v ← v − α E'(v)` con las cotas |
| Lagrange y KKT | `no_lineal/lagrange_energia.py` | `resolver`: λ cerrado y el ciclo que fija los `E_i` negativos en 0 |
| Colas | `simulation/motor_simpy.py`, `metricas.py` | `_llegadas`, `_servir`, `_fallas`, `comparar_mm1` |
| Integración de módulos | `motor_simpy.py::_viajar`, `_despachador`, `_control` | M1 en cada paquete y ventana, M2 en cada tick |

## 3. POO

- **Abstracción**: `Nodo`, `ModeloProgramacionDinamica`, `Optimizador`, `Panel`, `ProveedorIA` son ABC.
- **Encapsulamiento**: atributos con `_`, propiedades de sólo lectura, `tabla`, `historial` y
  `estado()` devuelven copias; resultados como `@dataclass(frozen=True)`.
- **Herencia**: `Router`/`Servidor` de `Nodo`; `RutaMasCorta`/`Mochila` de la base de DP;
  `GradienteEnfriamiento`/`AsignadorLagrange` de `Optimizador`; cinco paneles de `Panel`.
- **Polimorfismo**: `for opt in self._optimizadores: opt.actualizar(entrada)`,
  `for panel in self._paneles: panel.dibujar(...)`, `nodo.tiempo_servicio(paquete)`,
  `proveedor.analizar(resumen)`.
- **Patrones**: Template Method (`resolver()` y `Optimizador.actualizar()`), Observer
  (`MotorSimulacion.suscribir`), Null Object (`ProveedorSinConexion`).

## 4. Preguntas probables

- **¿Por qué la ruta es por etapas y no Dijkstra?** Porque el enunciado pide programación dinámica:
  la red de un centro de datos ya es por capas, y la recursión por etapas es el modelo de la
  diligencia visto en clase. La tabla se puede leer etapa por etapa.
- **¿Cómo influye la congestión?** El costo del enlace es `l0(1 + ρ/(1−ρ))` con `ρ` = paquetes en
  tránsito / capacidad (tope 0.95). Cada paquete recalcula la ruta con los costos del momento; si
  la ruta de un clúster cambia, el motor emite `cambio_ruta` y el panel la hace parpadear.
- **¿Por qué esa función térmica?** Es un cúbico elegido para que el máximo, el mínimo y la
  inflexión caigan dentro de [0, 100] %, como pide R3. Lectura: la temperatura sube, baja cuando
  los ventiladores entran en régimen y luego se dispara.
- **¿El gradiente converge siempre?** Con α = 0.05 sí en el rango usado (`α < 2/E''(v*)`); además
  la velocidad se acota a `[v_min, v_max]`, lo que evita que un paso grande lo saque del dominio.
  El test `test_gradiente_converge_al_optimo` lo verifica contra `v*`.
- **¿Qué pasa si un clúster no tiene demanda?** Su `E_i` saldría negativo; KKT lo fija en 0 y se
  re-resuelve. Si nadie tiene demanda, la energía se reparte en partes iguales (R = 0 de todos modos).
- **¿Por qué no coinciden las métricas con el M/M/1?** El M/M/1 es sólo una referencia: los
  servidores atienden varias tareas en paralelo, se despachan por ventanas con la mochila y hay
  fallas. Por eso `Wq` simulado es mayor que el teórico.
- **¿Cómo se valida la entrada?** `Validador` rechaza tipos, rangos, ids duplicados, enlaces que no
  van a la capa siguiente, etc., y junta todos los errores. Los argumentos de la CLI usan el mismo
  `validar_rango` (por ejemplo `--carga 150` da error).
- **¿Cómo se demuestra la independencia de módulos?** `core/` no importa `simulation/`, `gui/` ni
  `services/`; `--modulo m1` y `--modulo m2` corren sin SimPy ni Pygame, y cada módulo tiene sus tests.
