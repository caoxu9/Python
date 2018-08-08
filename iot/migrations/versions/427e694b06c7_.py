"""empty message

Revision ID: 427e694b06c7
Revises: c5666b76620b
Create Date: 2018-08-08 12:36:06.422194

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '427e694b06c7'
down_revision = 'c5666b76620b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('warings', sa.Column('about', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('warings', 'about')
    # ### end Alembic commands ###
