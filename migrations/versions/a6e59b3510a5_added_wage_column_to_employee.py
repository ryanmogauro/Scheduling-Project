"""Added wage column to employee

Revision ID: a6e59b3510a5
Revises: 
Create Date: 2024-11-27 15:00:37.816514

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6e59b3510a5'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.add_column(sa.Column('wage', sa.Numeric(10, 2), nullable=False, server_default='0.00'))

def downgrade():
    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.drop_column('wage')
