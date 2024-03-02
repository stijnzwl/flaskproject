"""empty message

Revision ID: 2641ca4c5751
Revises: f89186f437ff
Create Date: 2024-03-02 12:35:44.007988

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2641ca4c5751'
down_revision = 'f89186f437ff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game_status', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dealer_score', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('player_score', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game_status', schema=None) as batch_op:
        batch_op.drop_column('player_score')
        batch_op.drop_column('dealer_score')

    # ### end Alembic commands ###
