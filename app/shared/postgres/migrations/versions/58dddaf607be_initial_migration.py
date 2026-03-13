"""Initial migration

Revision ID: 58dddaf607be
Revises: 
Create Date: 2026-03-12 16:33:15.980779

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '58dddaf607be'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('roles',
    sa.Column('name', sa.String(length=32), nullable=False, comment='Unique role name used in RBAC checks'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Primary key identifier'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record creation timestamp'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('users',
    sa.Column('email', sa.String(length=254), nullable=False, comment='Unique email address; max 254 characters per RFC 5321'),
    sa.Column('hashed_password', sa.String(length=60), nullable=False, comment="Bcrypt hash of the user's password; bcrypt output is always exactly 60 characters"),
    sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False, comment='True once the user confirms their email address'),
    sa.Column('bio', sa.Text(), nullable=True, comment='Optional free-form biographical text provided by the user'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Primary key identifier'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record creation timestamp'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Last update timestamp'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('refresh_tokens',
    sa.Column('user_id', sa.Integer(), nullable=False, comment='Owner of this token; cascades deletion from users table'),
    sa.Column('token', sa.String(length=512), nullable=False, comment='Opaque random string; looked up by exact match on every refresh request'),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False, comment='UTC expiry timestamp; token is invalid at or after this moment'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Primary key identifier'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record creation timestamp'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.create_index(op.f('ix_refresh_tokens_expires_at'), 'refresh_tokens', ['expires_at'], unique=False)
    op.create_table('role_permissions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False, comment='Foreign key referencing the role this permission is assigned to.'),
    sa.Column('permission', sa.Enum('users:get_all', 'users:manage_roles', 'roles:create', 'roles:manage_permissions', name='permission'), nullable=False, comment='Permission granted to the role.'),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('role_id', 'permission', name='uq_role_permissions_role_permission')
    )
    op.create_table('user_roles',
    sa.Column('user_id', sa.Integer(), nullable=False, comment='Foreign key to the user who holds this role; leading column of the composite PK'),
    sa.Column('role_id', sa.Integer(), nullable=False, comment='Foreign key to the assigned role; trailing column of the composite PK'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record creation timestamp'),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'role_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
    sa.Enum(name='permission').drop(op.get_bind())
    op.drop_index(op.f('ix_refresh_tokens_expires_at'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('roles')