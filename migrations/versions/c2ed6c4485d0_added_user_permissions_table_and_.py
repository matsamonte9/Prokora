"""Updated user_permissions table columns

Revision ID: c2ed6c4485d0
Revises: c64703f2ff1d
Create Date: 2025-03-05 19:57:29.286188

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c2ed6c4485d0'
down_revision = 'c64703f2ff1d'
branch_labels = None
depends_on = None


def upgrade():
    # ### Alter columns for user_permissions table to make them nullable ###
    with op.batch_alter_table('user_permissions', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)  # Make user_id nullable
        batch_op.alter_column('permission_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)  # Make permission_id nullable

    # ### end Alembic commands ###


def downgrade():
    # ### Rollback column changes ###
    with op.batch_alter_table('user_permissions', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)  # Make user_id non-nullable
        batch_op.alter_column('permission_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)  # Make permission_id non-nullable

    # ### end Alembic commands ###
