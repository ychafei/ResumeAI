"""Added suggestions column to Resume

Revision ID: 11bfe9115899
Revises: 
Create Date: 2025-03-19 20:31:35.681547

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11bfe9115899'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('job', schema=None) as batch_op:
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)
        batch_op.alter_column('description',
               existing_type=sa.TEXT(),
               nullable=False)

    with op.batch_alter_table('resume', schema=None) as batch_op:
        batch_op.add_column(sa.Column('suggestions', sa.Text(), nullable=True))
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('job_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('match_score',
               existing_type=sa.FLOAT(),
               nullable=False)
        batch_op.alter_column('submitted_at',
               existing_type=sa.DATETIME(),
               nullable=False)
        batch_op.drop_column('notified')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('role',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=20),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('role',
               existing_type=sa.String(length=20),
               type_=sa.VARCHAR(length=50),
               nullable=True)

    with op.batch_alter_table('resume', schema=None) as batch_op:
        batch_op.add_column(sa.Column('notified', sa.BOOLEAN(), nullable=True))
        batch_op.alter_column('submitted_at',
               existing_type=sa.DATETIME(),
               nullable=True)
        batch_op.alter_column('match_score',
               existing_type=sa.FLOAT(),
               nullable=True)
        batch_op.alter_column('job_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.drop_column('suggestions')

    with op.batch_alter_table('job', schema=None) as batch_op:
        batch_op.alter_column('description',
               existing_type=sa.TEXT(),
               nullable=True)
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)

    # ### end Alembic commands ###
