"""Task 2.1: Add authorization fields for unified labeling system

Revision ID: fe7f4e6d2ea1
Revises: 1b3e32d81e77
Create Date: 2025-06-29 19:58:25.976164

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe7f4e6d2ea1'
down_revision = '1b3e32d81e77'
branch_labels = None
depends_on = None


def upgrade():
    # Add fields to labels table for unified labeling system
    op.add_column('labels', sa.Column('created_by', sa.UUID(), nullable=True))
    op.add_column('labels', sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Add foreign key constraint for created_by
    op.create_foreign_key('fk_labels_created_by', 'labels', 'users', ['created_by'], ['id'])
    
    # Add fields to label_applications table for authorization workflow
    op.add_column('label_applications', sa.Column('authorized_by', sa.UUID(), nullable=True))
    op.add_column('label_applications', sa.Column('authorized_at', sa.DateTime(), nullable=True))
    
    # Add foreign key constraint for authorized_by
    op.create_foreign_key('fk_label_applications_authorized_by', 'label_applications', 'users', ['authorized_by'], ['id'])
    
    # Add fields to label_suggestions table for enhanced AI workflow
    op.add_column('label_suggestions', sa.Column('project_id', sa.UUID(), nullable=True))
    op.add_column('label_suggestions', sa.Column('suggestion_type', sa.String(20), nullable=False, server_default='store_label'))
    op.add_column('label_suggestions', sa.Column('target_cells', sa.JSON(), nullable=True))
    op.add_column('label_suggestions', sa.Column('suggested_label_id', sa.Integer(), nullable=True))
    op.add_column('label_suggestions', sa.Column('created_by', sa.UUID(), nullable=True))
    
    # Add foreign key constraints for label_suggestions
    op.create_foreign_key('fk_label_suggestions_project_id', 'label_suggestions', 'projects', ['project_id'], ['id'])
    op.create_foreign_key('fk_label_suggestions_suggested_label_id', 'label_suggestions', 'labels', ['suggested_label_id'], ['id'])
    op.create_foreign_key('fk_label_suggestions_created_by', 'label_suggestions', 'users', ['created_by'], ['id'])


def downgrade():
    # Remove foreign key constraints first
    op.drop_constraint('fk_label_suggestions_created_by', 'label_suggestions', type_='foreignkey')
    op.drop_constraint('fk_label_suggestions_suggested_label_id', 'label_suggestions', type_='foreignkey')
    op.drop_constraint('fk_label_suggestions_project_id', 'label_suggestions', type_='foreignkey')
    op.drop_constraint('fk_label_applications_authorized_by', 'label_applications', type_='foreignkey')
    op.drop_constraint('fk_labels_created_by', 'labels', type_='foreignkey')
    
    # Remove columns from label_suggestions
    op.drop_column('label_suggestions', 'created_by')
    op.drop_column('label_suggestions', 'suggested_label_id')
    op.drop_column('label_suggestions', 'target_cells')
    op.drop_column('label_suggestions', 'suggestion_type')
    op.drop_column('label_suggestions', 'project_id')
    
    # Remove columns from label_applications
    op.drop_column('label_applications', 'authorized_at')
    op.drop_column('label_applications', 'authorized_by')
    
    # Remove columns from labels
    op.drop_column('labels', 'usage_count')
    op.drop_column('labels', 'created_by')
