"""Increase column_name field length to handle long column names

Revision ID: increase_column_name_length
Revises: 
Create Date: 2025-06-29 14:32:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'increase_column_name_length'
down_revision = 'f78cf5b68592'  # Last migration
branch_labels = None
depends_on = None


def upgrade():
    """Increase column_name field length from 255 to 1000 characters"""
    
    # AutoLabelApplication table
    op.alter_column('auto_label_applications', 'column_name',
                    existing_type=sa.String(255),
                    type_=sa.String(1000),
                    existing_nullable=False)
    
    # AutoLabel table 
    op.alter_column('auto_labels', 'column_name',
                    existing_type=sa.String(255),
                    type_=sa.String(1000),
                    existing_nullable=False)
    
    # CellLabel table
    op.alter_column('cell_labels', 'column_name',
                    existing_type=sa.String(255),
                    type_=sa.String(1000),
                    existing_nullable=True)
    
    # ColumnAnalysis table
    op.alter_column('column_analysis', 'column_name',
                    existing_type=sa.String(255),
                    type_=sa.String(1000),
                    existing_nullable=False)


def downgrade():
    """Rollback column_name field length to 255 characters"""
    
    # Note: This may fail if there are existing records with column names > 255 chars
    op.alter_column('column_analysis', 'column_name',
                    existing_type=sa.String(1000),
                    type_=sa.String(255),
                    existing_nullable=False)
    
    op.alter_column('cell_labels', 'column_name',
                    existing_type=sa.String(1000),
                    type_=sa.String(255),
                    existing_nullable=True)
    
    op.alter_column('auto_labels', 'column_name',
                    existing_type=sa.String(1000),
                    type_=sa.String(255),
                    existing_nullable=False)
    
    op.alter_column('auto_label_applications', 'column_name',
                    existing_type=sa.String(1000),
                    type_=sa.String(255),
                    existing_nullable=False)
