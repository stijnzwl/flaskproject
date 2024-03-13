"""empty message

Revision ID: c24b19c96021
Revises: a5c30de62223
Create Date: 2024-03-12 21:40:28.541557

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c24b19c96021'
down_revision = 'a5c30de62223'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game_status', schema=None) as batch_op:
        batch_op.alter_column('deck',
               existing_type=sa.VARCHAR(length=10),
               type_=sa.Text(),
               existing_nullable=False)
        batch_op.alter_column('player_decision',
               existing_type=sa.VARCHAR(length=10),
               type_=sa.String(10),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game_status', schema=None) as batch_op:
        batch_op.alter_column('deck',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=10),
               existing_nullable=False)
        batch_op.alter_column('player_decision',
               existing_type=sa.String(length=10),
               type_=sa.VARCHAR(length=10),
               existing_nullable=True)

    # ### end Alembic commands ###
