"""empty message

Revision ID: 4e83aa9044e8
Revises: 
Create Date: 2020-02-13 01:42:53.952485

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e83aa9044e8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('files',
    sa.Column('id', sa.String(length=128), nullable=False),
    sa.Column('file_name', sa.Text(), nullable=False),
    sa.Column('url', sa.String(length=128), nullable=False),
    sa.Column('upload_date', sa.DateTime(), nullable=True),
    sa.Column('file_size', sa.Float(precision=1, asdecimal=True), nullable=False),
    sa.Column('file_origin', sa.Text(), nullable=True),
    sa.Column('hash_digest', sa.String(), nullable=True),
    sa.Column('file_owner', sa.String(length=128), nullable=False),
    sa.Column('bill_attached_to', sa.String(length=128), nullable=False),
    sa.ForeignKeyConstraint(['bill_attached_to'], ['bills.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('files')
    # ### end Alembic commands ###