"""
Configuración de Alembic para Rutify.

Dos decisiones importantes:
- La dirección de la base de datos sale de app/infrastructure/db/session.py,
  la misma que usa la aplicación, para que migraciones y servidor siempre
  apunten a la misma base. Solo se usa otra si alguien la define a mano en
  la configuración (como hace la prueba de migraciones).
- El target_metadata son los modelos del proyecto, así Alembic puede
  comparar la base contra el código (alembic check).
"""
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.infrastructure.db.models import Base
from app.infrastructure.db.session import DATABASE_URL

config = context.config

if config.config_file_name is not None:
    # disable_existing_loggers=False para no apagar los loggers de la app
    # cuando las migraciones se ejecutan desde las pruebas
    fileConfig(config.config_file_name, disable_existing_loggers=False)

if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Genera el SQL sin conectarse a la base (alembic upgrade head --sql)."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica las migraciones directamente sobre la base."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # SQLite no sabe alterar tablas directamente; este modo lo
            # resuelve copiando la tabla, y así las migraciones futuras
            # funcionan igual que en una base de servidor
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()