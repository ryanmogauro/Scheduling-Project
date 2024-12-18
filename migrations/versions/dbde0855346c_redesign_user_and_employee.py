"""Redesign user and employee

Revision ID: dbde0855346c
Revises: 6e09b25c6492
Create Date: 2024-12-04 15:22:33.878782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dbde0855346c'
down_revision = '6e09b25c6492'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.drop_column('sendDate')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sendDate', sa.DATETIME(), nullable=True))

    # ### end Alembic commands ###
