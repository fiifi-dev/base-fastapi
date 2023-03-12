"""add store

Revision ID: 9e651047efb2
Revises: 2924ce252100
Create Date: 2023-03-12 16:21:00.758764

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e651047efb2'
down_revision = '2924ce252100'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('store',
    sa.Column('link', sa.String(length=150), nullable=False),
    sa.Column('thumb', sa.String(length=150), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('store')
    # ### end Alembic commands ###
