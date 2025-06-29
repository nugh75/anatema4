"""add_missing_columns_to_auto_labels_and_applications

Revision ID: d9a7149d6ee7
Revises: 31a1010edf92
Create Date: 2025-06-28 16:47:39.821242

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9a7149d6ee7'
down_revision = '31a1010edf92'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns to auto_labels table
    with op.batch_alter_table('auto_labels', schema=None) as batch_op:
        batch_op.add_column(sa.Column('column_name', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('label_type', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('created_by', sa.UUID(), nullable=True))
        
        # Add foreign key constraint for created_by
        batch_op.create_foreign_key('fk_auto_labels_created_by', 'users', ['created_by'], ['id'])
        
        # Make column_analysis_id nullable since it's optional for manual labels
        batch_op.alter_column('column_analysis_id', nullable=True)
    
    # Add missing columns to auto_label_applications table
    with op.batch_alter_table('auto_label_applications', schema=None) as batch_op:
        batch_op.add_column(sa.Column('row_index', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('column_name', sa.String(length=255), nullable=False, server_default=''))
        
        # Make row_id nullable since it's optional for manual labeling
        batch_op.alter_column('row_id', nullable=True)
        
        # Remove the old column_index column if it exists and replace with column_name
        # Note: We keep both for now to avoid data loss, but column_name should be used going forward


def downgrade():
    # Remove added columns from auto_label_applications table
    with op.batch_alter_table('auto_label_applications', schema=None) as batch_op:
        batch_op.drop_column('column_name')
        batch_op.drop_column('row_index')
        batch_op.alter_column('row_id', nullable=False)
    
    # Remove added columns from auto_labels table
    with op.batch_alter_table('auto_labels', schema=None) as batch_op:
        batch_op.drop_constraint('fk_auto_labels_created_by', type_='foreignkey')
        batch_op.drop_column('created_by')
        batch_op.drop_column('label_type')
        batch_op.drop_column('column_name')
        batch_op.alter_column('column_analysis_id', nullable=False)
