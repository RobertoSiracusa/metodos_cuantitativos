
# Métodos Cuantitativos — Repositorio

Este repositorio agrupa tareas del curso de Métodos Cuantitativos. Cada tarea se colocará en su propia carpeta (`tarea1/`, `tarea2/`, ...) y contendrá el código, tests y documentación necesarios para reproducir los ejercicios.

## Organización y convención de carpetas

- `tareaN/` — Carpeta por cada tarea (N = 1, 2, ...). Cada `tareaN` puede incluir subcarpetas con implementaciones, datos y documentación.
- Dentro de cada `tarea` se recomienda la siguiente estructura mínima:
  - `calculator/` o `src/` — Código de la tarea (módulos, scripts ejecutables).
  - `tests/` — Pruebas unitarias relacionadas con la tarea.
  - `README.md` — Documentación específica de la tarea (cómo ejecutar, parámetros, resultados esperados).

## Convención para añadir nuevas tareas

1. Crear una carpeta `tareaX/` en la raíz del repositorio.
2. Incluir el código en una subcarpeta (por ejemplo `calculator/` o `src/`).
3. Añadir tests en `tareaX/tests/` para validar el resultado.
4. Agregar un `README.md` dentro de `tareaX` explicando el objetivo, los datos usados y cómo ejecutar.

Esto permite mantener el repositorio ordenado y facilita que cada tarea sea autocontenida.

## Ejemplo: `tarea1`

`tarea1` contiene la implementación de una calculadora orientada a objetos para teoría de colas (modelos M/M/1 y M/M/c). Puntos clave:

- CLI: `tarea1/calculator/main.py` — Ejecuta los ejercicios y muestra resultados por pantalla.
- Modelos: `tarea1/calculator/src/core/mm1_model.py` y `tarea1/calculator/src/core/mmc_model.py`.
- Reportes: `tarea1/calculator/src/services/reporter.py`.
- Validaciones: `tarea1/calculator/src/utils/validators.py`.
- Tests: `tarea1/calculator/tests/test_mmc_model.py` (valida métricas M/M/c con datos de ejemplo).

Datos de ejemplo usados en `tarea1`:

- Ejercicio 1 (M/M/1): `lambda=0.8`, `mu=1.0`, `k=3`.
- Ejercicio 2 (M/M/c): `lambda=15.0`, `mu=6.0`, `servers=3`.

## Cómo ejecutar una tarea

Desde la raíz del repositorio, por ejemplo para `tarea1`:

```bash
cd tarea1/calculator
python main.py --exercise 2 --servers 3 --lambda 15.0 --mu 6.0
```

O bien ejecutar desde la raíz como módulo si prefieres el modo `-m`:

```bash
python -m calculator.main
```

## Ejecutar pruebas

```bash
cd tarea1/calculator
pytest
```

## Buenas prácticas y notas

- Cada tarea debe ser autocontenida y documentada en su propio `README.md`.
- Mantener tests que permitan verificar los resultados numéricos y evitar regresiones.
- Si agregas dependencias, registra un `requirements.txt` o `pyproject.toml` dentro de la tarea.

Si quieres, puedo:

- Crear una plantilla `tarea_template/` con la estructura recomendada y un `cookiecutter` simple.
- Añadir instrucciones de contribución o un `CONTRIBUTING.md`.
