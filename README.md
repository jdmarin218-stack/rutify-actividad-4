# Rutify — Actividad 4: construcción, validación y defensa final

Implementación ejecutable del flujo **asignar un repartidor a una entrega**, diseñado en la Actividad 3 de Optativa 2 (Arquitectura de Software). Es un corte vertical completo: entrada HTTP, caso de uso, dominio y persistencia, con pruebas, registro de riesgos y señales de observabilidad.

**Autor:** Julián David Marín Ramírez — Tecnología en Desarrollo de Software, ITM.

## Qué hace

- `POST /entregas` crea una entrega en estado `Pendiente`. En el sistema real vendría de un pedido confirmado en el Contexto de Pedidos.
- `POST /entregas/{entrega_id}/asignar-repartidor` asigna un repartidor y deja la entrega en `Asignada`.

La regla central, que una entrega no puede tener dos repartidores, la protege la propia entidad `Entrega`, no el controller ni el caso de uso.

| Resultado | Código |
|---|---|
| Asignación exitosa | 200 |
| La entrega no existe | 404 |
| La entrega ya tiene repartidor | 409 |
| La entrega no está en estado Pendiente | 409 |
| El repartidor no tiene capacidad | 409 |

## Arquitectura

```
app/
  api/             entrada: endpoints FastAPI, DTOs y cableado de dependencias
  application/     caso de uso AsignarRepartidor y puertos (contratos)
  domain/          entidad Entrega, estados e invariantes
  infrastructure/  repositorio SQLAlchemy/SQLite y adaptador de disponibilidad
migrations/        migraciones de Alembic (esquema versionado de la base)
alembic.ini        configuración de Alembic
tests/
  unit/            invariantes del dominio y chequeo de arquitectura
  integration/     flujo completo por HTTP contra SQLite en memoria y prueba de migraciones
docs/
  expediente.md    decisiones y diagramas de las actividades 1 a 4
  actividad-4/     trazabilidad, decisiones, riesgos y observabilidad
```

Las dependencias van hacia adentro: el dominio no conoce a nadie, la aplicación solo conoce el dominio y los puertos, y la infraestructura implementa esos puertos. El archivo `app/api/dependencies.py` es el único lugar donde se conectan los puertos con sus implementaciones concretas.

## Cómo ejecutarlo

Requisitos: Python 3.11 y Git. Los comandos son para PowerShell en Windows.

```powershell
git clone https://github.com/jdmarin218-stack/rutify-actividad-4.git
cd rutify-actividad-4
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crear la base de datos aplicando las migraciones (solo la primera vez, o cuando haya migraciones nuevas):

```powershell
alembic upgrade head
```

Levantar el servidor:

```powershell
uvicorn app.api.main:app --reload
```

Luego abre http://127.0.0.1:8000/docs para probar los endpoints desde Swagger. El servidor ya no crea las tablas por su cuenta: si se salta el paso de `alembic upgrade head`, los endpoints fallarán porque la tabla `entregas` no existe.

## Pruebas

```powershell
pytest tests -v
```

Son 11 pruebas:

- **Dominio (3):** invariantes de la entidad `Entrega`.
- **Integración (6):** flujo completo por HTTP, doble asignación, entrega inexistente, repartidor sin capacidad, entrega que no está pendiente y una prueba de migraciones que aplica Alembic sobre una base vacía y comprueba que el esquema coincide con los modelos.
- **Arquitectura (2):** el dominio y la aplicación no importan infraestructura, API ni frameworks.

La salida incluye un aviso de deprecación de Starlette sobre `httpx`; está registrado como riesgo R7 y no afecta los resultados.

## Documentación

- [Expediente arquitectónico](docs/expediente.md): decisiones y diagramas de las Actividades 1 a 4, y qué pasó con cada decisión al implementar.
- [Trazabilidad](docs/actividad-4/trazabilidad.md): de cada elemento del diseño de la Actividad 3 al código y a la prueba que lo verifica, y lo que no se implementó.
- [Decisiones tecnológicas](docs/actividad-4/decisiones-tecnologicas.md): qué patrones aplican y cuáles no, y los ajustes frente al diseño de la Actividad 3.
- [Registro de riesgos](docs/actividad-4/riesgos.md): riesgos, mitigaciones, evidencia y riesgos residuales.
- [Observabilidad](docs/actividad-4/observabilidad.md): señales de log, evidencia real y cómo diagnosticar con ellas.

El diseño del dominio, el glosario y los diagramas están en el repositorio de la Actividad 3 (`rutify-actividad-3`).

## Limitaciones conocidas

- La disponibilidad del repartidor es una **simulación** en memoria; el servicio real de Ruteo no existe en este proyecto.
- Las migraciones cubren una sola versión del esquema (la tabla `entregas`) sobre SQLite; en un entorno real se repetiría el mismo mecanismo contra la base del servidor.
- No hay autenticación ni protección contra asignaciones concurrentes sobre la misma entrega.

El detalle y los siguientes pasos están en el registro de riesgos.

## Video de sustentación

Enlace: _pendiente de publicar_