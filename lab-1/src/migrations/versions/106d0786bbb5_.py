"""empty message

Revision ID: 106d0786bbb5
Revises: 09b6565cf4e7
Create Date: 2018-04-13 22:19:40.081273

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '106d0786bbb5'
down_revision = '09b6565cf4e7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('affiliation', sa.String(length=120), nullable=True))
    op.add_column('user', sa.Column('description', sa.String(length=320), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'description')
    op.drop_column('user', 'affiliation')
    # ### end Alembic commands ###
