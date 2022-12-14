"""empty message

Revision ID: 52177add850c
Revises: a69835464933
Create Date: 2022-08-03 14:50:39.455037

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52177add850c'
down_revision = 'a69835464933'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('grouparticles', sa.Column('departament_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'grouparticles', 'departament', ['departament_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'grouparticles', type_='foreignkey')
    op.drop_column('grouparticles', 'departament_id')
    # ### end Alembic commands ###
