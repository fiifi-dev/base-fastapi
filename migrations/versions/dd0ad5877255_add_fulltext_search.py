"""add fulltext search

Revision ID: dd0ad5877255
Revises: 2a8dcacb5af9
Create Date: 2023-03-14 17:05:26.775518

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd0ad5877255'
down_revision = '2a8dcacb5af9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('idx_email_name', 'user', ['email', 'last_name', 'first_name'], unique=False, mydialect_length=5, mysql_prefix='FULLTEXT', mariadb_prefix='FULLTEXT')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_email_name', table_name='user', mydialect_length=5, mysql_prefix='FULLTEXT', mariadb_prefix='FULLTEXT')
    # ### end Alembic commands ###
