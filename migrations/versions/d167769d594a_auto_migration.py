"""Auto migration

Revision ID: d167769d594a
Revises: 
Create Date: 2026-06-17 13:48:23.562460

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd167769d594a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('roles',
    sa.Column('name', sa.String(length=32), nullable=False, comment='Unique role name used in RBAC checks'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Primary key identifier for Role'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record creation timestamp'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('users',
    sa.Column('email', sa.String(length=254), nullable=False, comment='Unique email address; max 254 characters per RFC 5321'),
    sa.Column('hashed_password', sa.String(length=60), nullable=False, comment="Bcrypt hash of the user's password; bcrypt output is always exactly 60 characters"),
    sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False, comment='True once the user confirms their email address'),
    sa.Column('bio', sa.Text(), nullable=True, comment='Optional free-form biographical text provided by the user'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Primary key identifier for User'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record creation timestamp'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('role_permissions',
    sa.Column('id', sa.Integer(), nullable=False, comment='Surrogate primary key'),
    sa.Column('role_id', sa.Integer(), nullable=False, comment='Foreign key to the owning role; cascades deletion from roles table'),
    sa.Column('permission', sa.Enum('users:get', 'users:get_all', 'users:update', 'users:delete', 'users:manage_roles', 'roles:get', 'roles:get_all', 'roles:create', 'roles:delete', 'roles:manage_permissions', name='permission'), nullable=False, comment='Permission value stored as a native PostgreSQL enum'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record creation timestamp'),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('role_id', 'permission', name='uq_role_permissions_role_permission')
    )
    op.create_table('user_roles',
    sa.Column('user_id', sa.Integer(), nullable=False, comment='Foreign key to the user who holds this role; leading column of the composite PK index'),
    sa.Column('role_id', sa.Integer(), nullable=False, comment='Foreign key to the assigned role; trailing column of the composite PK index'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record creation timestamp'),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'role_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('roles')
    sa.Enum(name='permission').drop(op.get_bind(), checkfirst=True)
