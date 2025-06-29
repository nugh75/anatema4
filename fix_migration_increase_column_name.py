#!/usr/bin/env python3
"""
Script per risolvere il problema della migrazione increase_column_name_length.py
Rimuove la modifica errata della colonna column_name in cell_labels che non esiste.

Task 2.4 - Risoluzione multiple heads Alembic
"""

import os
import shutil
from pathlib import Path

def main():
    print("🔧 RISOLUZIONE MIGRAZIONE increase_column_name_length.py")
    print("=" * 60)
    
    # Percorsi file
    migrations_dir = Path("/home/nugh75/Git/anatema2/migrations/versions")
    problematic_file = migrations_dir / "increase_column_name_length.py"
    backup_file = migrations_dir / "increase_column_name_length.py.backup"
    
    # Backup del file originale
    if problematic_file.exists():
        print(f"📁 Backup file originale: {backup_file}")
        shutil.copy2(problematic_file, backup_file)
        
        # Leggiamo il contenuto attuale
        with open(problematic_file, 'r') as f:
            content = f.read()
        
        # Contenuto corretto (rimuoviamo solo la parte errata per cell_labels)
        corrected_content = '''"""Increase column_name field length to handle long column names

Revision ID: increase_column_name_length
Revises: f78cf5b68592
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
    
    # RIMOSSO: CellLabel table - la colonna column_name non esiste
    # La tabella cell_labels usa column_index (INTEGER), non column_name (VARCHAR)
    
    # ColumnAnalysis table
    op.alter_column('column_analysis', 'column_name',
                    existing_type=sa.String(255),
                    type_=sa.String(1000),
                    existing_nullable=False)


def downgrade():
    """Rollback column_name field length to 255 characters"""
    
    # Note: This may fail if there are existing records with column names > 255 chars
    
    # ColumnAnalysis table
    op.alter_column('column_analysis', 'column_name',
                    existing_type=sa.String(1000),
                    type_=sa.String(255),
                    existing_nullable=False)
    
    # AutoLabel table
    op.alter_column('auto_labels', 'column_name',
                    existing_type=sa.String(1000),
                    type_=sa.String(255),
                    existing_nullable=False)
    
    # AutoLabelApplication table
    op.alter_column('auto_label_applications', 'column_name',
                    existing_type=sa.String(1000),
                    type_=sa.String(255),
                    existing_nullable=False)
'''
        
        # Scriviamo il contenuto corretto
        with open(problematic_file, 'w') as f:
            f.write(corrected_content)
        
        print("✅ Migrazione corretta salvata")
        print("📝 Modifiche applicate:")
        print("  - ❌ Rimossa modifica errata per cell_labels.column_name")
        print("  - ✅ Mantenute modifiche valide per auto_label_applications.column_name")
        print("  - ✅ Mantenute modifiche valide per auto_labels.column_name") 
        print("  - ✅ Mantenute modifiche valide per column_analysis.column_name")
        
    else:
        print(f"❌ File {problematic_file} non trovato")
        return False
    
    print("\n🎯 PROSSIMO PASSO:")
    print("Eseguire: flask db upgrade 2944c79a0f76")
    
    return True

if __name__ == "__main__":
    main()
