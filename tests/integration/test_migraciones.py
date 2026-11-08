"""
Prueba de las migraciones.

Aplica la migración sobre una base vacía y comprueba que el esquema que
queda es exactamente el que describen los modelos. Si alguien cambia un
modelo y se olvida de crear la migración correspondiente, esta prueba falla.
"""
from pathlib import Path

from alembic import command
from alembic.config import Config

RAIZ = Path(__file__).resolve().parents[2]


def test_las_migraciones_crean_el_esquema_que_describen_los_modelos(tmp_path):
    base_de_prueba = tmp_path / "migrada.db"

    config = Config(str(RAIZ / "alembic.ini"))
    config.set_main_option("script_location", str(RAIZ / "migrations"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{base_de_prueba.as_posix()}")

    command.upgrade(config, "head")

    # check falla si los modelos tienen algo que la migración no creó
    command.check(config)