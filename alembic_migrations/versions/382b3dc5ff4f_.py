"""empty message

Revision ID: 382b3dc5ff4f
Revises: 39e5898161df
Create Date: 2017-11-19 15:33:57.164917

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '382b3dc5ff4f'
down_revision = '39e5898161df'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('user', 'birthdate', type_=sa.Date(), postgresql_using='birthdate::date')
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###