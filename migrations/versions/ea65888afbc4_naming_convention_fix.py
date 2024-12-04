"""Naming Convention Fix

Revision ID: ea65888afbc4
Revises: 91a4a7f02a7c
Create Date: 2024-12-02 13:54:24.458504

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea65888afbc4'
down_revision = '91a4a7f02a7c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('eventStartTime', sa.DateTime(), nullable=False))
        batch_op.add_column(sa.Column('eventEndTime', sa.DateTime(), nullable=False))
        batch_op.drop_column('createdBy')
        batch_op.drop_column('eventEndDate')
        batch_op.drop_column('eventStartDate')

    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sendTime', sa.DateTime(), nullable=True))
        batch_op.drop_column('sendDate')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sendDate', sa.DATETIME(), nullable=True))
        batch_op.drop_column('sendTime')

    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('eventStartDate', sa.DATETIME(), nullable=False))
        batch_op.add_column(sa.Column('eventEndDate', sa.DATETIME(), nullable=False))
        batch_op.add_column(sa.Column('createdBy', sa.INTEGER(), nullable=False))
        batch_op.drop_column('eventEndTime')
        batch_op.drop_column('eventStartTime')

    # ### end Alembic commands ###
