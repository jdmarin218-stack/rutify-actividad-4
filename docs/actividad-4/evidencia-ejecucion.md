# Evidencia de ejecución — Actividad 4

Este archivo reúne la salida real de las verificaciones del proyecto. Se obtuvo el 8 de noviembre de 2026, en Windows con Python 3.11.9 y pytest 9.2.0, desde un **clon limpio** del repositorio (clonado de GitHub en una carpeta temporal, con un entorno virtual nuevo e instalando solo lo que dice `requirements.txt`). Eso demuestra que cualquiera puede reproducir el proyecto con los pasos del README.

Commit verificado: `c5729d0` (migraciones con Alembic).

## 1. Aplicación de la migración

Comando: `alembic upgrade head`

```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 0001, crear tabla entregas
```

En el proyecto de trabajo, además, se comprobó que el esquema coincide con los modelos:

- `alembic current` respondió `0001 (head)`.
- `alembic check` respondió `No new upgrade operations detected.`

## 2. Pruebas automáticas

Comando: `pytest tests -v`

```
tests/integration/test_asignar_repartidor_api.py::test_flujo_completo_asigna_repartidor_y_queda_guardado PASSED [  9%]
tests/integration/test_asignar_repartidor_api.py::test_no_permite_asignar_dos_repartidores_a_la_misma_entrega PASSED [ 18%]
tests/integration/test_asignar_repartidor_api.py::test_entrega_inexistente_responde_404 PASSED [ 27%]
tests/integration/test_asignar_repartidor_api.py::test_repartidor_sin_capacidad_responde_409_y_no_toca_la_entrega PASSED [ 36%]
tests/integration/test_asignar_repartidor_api.py::test_entrega_que_no_esta_pendiente_responde_409_y_no_500 PASSED [ 45%]
tests/integration/test_migraciones.py::test_las_migraciones_crean_el_esquema_que_describen_los_modelos PASSED [ 54%]
tests/unit/test_arquitectura.py::test_el_dominio_no_depende_de_otras_capas_ni_de_frameworks PASSED [ 63%]
tests/unit/test_arquitectura.py::test_la_aplicacion_no_depende_de_infraestructura_ni_de_frameworks PASSED [ 72%]
tests/unit/test_entrega.py::test_asignar_repartidor_a_entrega_pendiente_funciona PASSED [ 81%]
tests/unit/test_entrega.py::test_no_se_puede_asignar_dos_veces_la_misma_entrega PASSED [ 90%]
tests/unit/test_entrega.py::test_no_se_puede_asignar_repartidor_a_entrega_ya_entregada PASSED [100%]

======================== 11 passed, 1 warning in 1.33s ========================
```

El único aviso es `StarletteDeprecationWarning` sobre `httpx` en `TestClient`. Está registrado como riesgo R7 y no afecta los resultados.

## 3. Qué demuestra cada grupo de pruebas

| Grupo | Pruebas | Qué demuestra |
|---|---|---|
| Dominio | 3 | La entidad `Entrega` protege sus reglas por sí misma. |
| Integración (API) | 5 | El flujo completo por HTTP: éxito (200), doble asignación (409), entrega inexistente (404), repartidor sin capacidad (409) y entrega que no está pendiente (409). |
| Integración (migraciones) | 1 | La migración crea el esquema que describen los modelos. |
| Arquitectura | 2 | El dominio y la aplicación no importan infraestructura, API ni frameworks. |

## 4. Otras evidencias en el repositorio

- Respuestas del servidor en ejecución y logs reales con identificador y motivo: [observabilidad.md](observabilidad.md).
- Prueba de que el chequeo de arquitectura detecta violaciones (se metió un `import sqlalchemy` en el dominio y la prueba falló): [riesgos.md](riesgos.md).
- Riesgos con su mitigación y su estado: [riesgos.md](riesgos.md).