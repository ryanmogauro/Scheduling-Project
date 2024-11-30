"""Add sendDate to notification

Revision ID: 9770052513b0
Revises: 5400e0bbbd10
Create Date: 2024-11-29 18:33:48.893369

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9770052513b0'
down_revision = '5400e0bbbd10'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sendDate', sa.DateTime(), nullable=True))
        batch_op.drop_column('date')

    with op.batch_alter_table('unavailability', schema=None) as batch_op:
        batch_op.alter_column('employeeID',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('unavailability', schema=None) as batch_op:
        batch_op.alter_column('employeeID',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date', sa.DATETIME(), nullable=False))
        batch_op.drop_column('sendDate')

    # ### end Alembic commands ###
