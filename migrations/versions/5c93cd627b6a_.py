"""empty message

Revision ID: 5c93cd627b6a
Revises: 8362c3b0cfa7
Create Date: 2022-07-29 15:55:14.149596

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c93cd627b6a'
down_revision = '8362c3b0cfa7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('name', sa.String(length=200), nullable=True))
    op.add_column('users', sa.Column('foto', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'foto')
    op.drop_column('users', 'name')
    # ### end Alembic commands ###