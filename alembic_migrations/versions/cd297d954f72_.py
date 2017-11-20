"""empty message

Revision ID: cd297d954f72
Revises: d02c378a22c1
Create Date: 2017-11-19 15:09:56.865586

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd297d954f72'
down_revision = 'd02c378a22c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('supervisor_id', sa.Integer(), nullable=True))
    op.create_foreign_key('supervisor_fk', 'user', 'user', ['supervisor_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('supervisor_fk', 'user', type_='foreignkey')
    op.drop_column('user', 'supervisor_id')
    # ### end Alembic commands ###
