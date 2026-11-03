"""initial schema

Revision ID: 5faaae5d2151
Revises: 
Create Date: 2026-09-12 15:54:22.094423

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5faaae5d2151'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # level y exp NO van acá: los agrega a9b25ca6b72c
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.Column('fecha_registro', sa.String(length=50), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('reporte_experiencia',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('usuario_id', sa.UUID(), nullable=False),
    sa.Column('comentario', sa.String(length=500), nullable=True),
    sa.Column('calificacion_general', sa.Integer(), nullable=True),
    sa.Column('calificacion_limpieza', sa.Integer(), nullable=True),
    sa.Column('calificacion_lleno', sa.String(), nullable=True),
    sa.Column('num_coche', sa.Integer(), nullable=True),
    sa.Column('fecha_reporte', sa.String(length=50), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['usuario_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('reporte_experiencia')
    op.drop_table('users')