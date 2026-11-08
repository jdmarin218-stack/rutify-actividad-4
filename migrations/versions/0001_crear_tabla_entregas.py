"""crear tabla entregas

Migración inicial: crea la tabla donde se guardan las entregas.
Es la primera versión del esquema, así que no tiene migración anterior.

Revision ID: 0001
Revises:
Create Date: 2026-11-08
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "entregas",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("direccion_destino", sa.String(), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("repartidor_id", sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("entregas")