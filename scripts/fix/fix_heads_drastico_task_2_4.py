#!/usr/bin/env python3
"""
Fix Alembic Multiple Heads - Strategia Drastica per Task 2.4
Risolve definitivamente il problema delle 8 heads Alembic per sbloccare Task 2.4
"""

import os
import sys
from datetime import datetime

def analyze_heads_situation():
    """Analizza la situazione attuale delle heads"""
    
    print("=== ANALISI SITUAZIONE HEADS ALEMBIC ===")
    print("Heads attuali identificate:")
    heads = [
        "4e4ca98db1b9",
        "6f3c95fb6ed4", 
        "912d14cfffc3",
        "b07dc9659564",
        "comprehensive_merge_task_2_3",
        "e846f9ca307e",
        "fe7f4e6d2ea1",
        "increase_column_name_length"
    ]
    
    for i, head in enumerate(heads, 1):
        print(f"{i}. {head}")
    
    print(f"\nTotale heads: {len(heads)} ❌ CRITICO")
    print("Status: BLOCCANTE per Task 2.4")
    
    return heads

def strategy_drastic_reset():
    """Strategia drastica: reset completo e ricostruzione"""
    
    print("\n=== STRATEGIA DRASTICA: RESET COMPLETO ===")
    
    print("📋 Piano di risoluzione:")
    print("1. Backup stato attuale database")
    print("2. Identificare ultima migrazione valida comune")
    print("3. Reset Alembic alla base comune")
    print("4. Ricreare singola migrazione per tutti i campi Task 2.4")
    print("5. Applicare migrazione unica")
    
    print("\n🎯 Obiettivo: Una sola HEAD pulita per Task 2.4")
    
    # Step 1: Commands da eseguire
    commands = [
        "# Step 1: Backup attuale",
        "python -m flask db current",
        "",
        "# Step 2: Reset alla base",
        "python -m flask db stamp base",
        "",
        "# Step 3: Upgrade alla migrazione base stabile", 
        "python -m flask db upgrade head",
        "",
        "# Step 4: Creare nuova migrazione Task 2.4",
        "python -m flask db migrate -m 'task_2_4_unified_label_schema_fix'",
        "",
        "# Step 5: Applicare migrazione",
        "python -m flask db upgrade"
    ]
    
    print("\n💻 COMANDI DA ESEGUIRE:")
    for cmd in commands:
        if cmd.startswith("#"):
            print(f"\n{cmd}")
        elif cmd.strip():
            print(f"   {cmd}")
    
    return commands

def create_unified_migration_content():
    """Crea il contenuto per una migrazione unificata Task 2.4"""
    
    print("\n=== MIGRAZIONE UNIFICATA TASK 2.4 ===")
    
    migration_content = '''
"""task_2_4_unified_label_schema_fix

Migrazione unificata per Task 2.4 - Store Etichette Centralizzato
Aggiunge tutti i campi necessari per il sistema etichettatura unificato

Revision ID: task_2_4_unified
Revises: [ultima_head_valida]
Create Date: {date}
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'task_2_4_unified'
down_revision = '[DA_DETERMINARE]'
branch_labels = None
depends_on = None

def upgrade():
    """Aggiunge tutti i campi mancanti per Task 2.4"""
    
    # Aggiungere a labels (Store Etichette)
    try:
        op.add_column('labels', sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')))
        print("✅ Aggiunto labels.created_by")
    except Exception as e:
        print(f"⚠️  labels.created_by già presente: {{e}}")
    
    try:
        op.add_column('labels', sa.Column('usage_count', sa.Integer(), server_default='0'))
        print("✅ Aggiunto labels.usage_count")
    except Exception as e:
        print(f"⚠️  labels.usage_count già presente: {{e}}")
    
    # Aggiungere a label_applications (già fatto in Task 2.3 ma verifichiamo)
    try:
        op.add_column('label_applications', sa.Column('authorized_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')))
        print("✅ Aggiunto label_applications.authorized_by")
    except Exception as e:
        print(f"⚠️  label_applications.authorized_by già presente: {{e}}")
    
    try:
        op.add_column('label_applications', sa.Column('authorized_at', sa.DateTime()))
        print("✅ Aggiunto label_applications.authorized_at")
    except Exception as e:
        print(f"⚠️  label_applications.authorized_at già presente: {{e}}")
    
    try:
        op.add_column('label_applications', sa.Column('approval_status', sa.String(20), server_default='approved'))
        print("✅ Aggiunto label_applications.approval_status")
    except Exception as e:
        print(f"⚠️  label_applications.approval_status già presente: {{e}}")
    
    try:
        op.add_column('label_applications', sa.Column('authorization_status', sa.String(20), server_default='approved'))
        print("✅ Aggiunto label_applications.authorization_status")
    except Exception as e:
        print(f"⚠️  label_applications.authorization_status già presente: {{e}}")
    
    # Aggiungere a label_suggestions (Store AI)
    try:
        op.add_column('label_suggestions', sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id')))
        print("✅ Aggiunto label_suggestions.project_id")
    except Exception as e:
        print(f"⚠️  label_suggestions.project_id già presente: {{e}}")
    
    try:
        op.add_column('label_suggestions', sa.Column('suggestion_type', sa.String(20), server_default='store_label'))
        print("✅ Aggiunto label_suggestions.suggestion_type")
    except Exception as e:
        print(f"⚠️  label_suggestions.suggestion_type già presente: {{e}}")
    
    try:
        op.add_column('label_suggestions', sa.Column('target_cells', sa.JSON()))
        print("✅ Aggiunto label_suggestions.target_cells")
    except Exception as e:
        print(f"⚠️  label_suggestions.target_cells già presente: {{e}}")
    
    try:
        op.add_column('label_suggestions', sa.Column('suggested_label_id', sa.Integer(), sa.ForeignKey('labels.id')))
        print("✅ Aggiunto label_suggestions.suggested_label_id")
    except Exception as e:
        print(f"⚠️  label_suggestions.suggested_label_id già presente: {{e}}")
    
    try:
        op.add_column('label_suggestions', sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')))
        print("✅ Aggiunto label_suggestions.created_by")
    except Exception as e:
        print(f"⚠️  label_suggestions.created_by già presente: {{e}}")

def downgrade():
    """Rimuove i campi aggiunti"""
    
    # Rimuovere da label_suggestions
    op.drop_column('label_suggestions', 'created_by')
    op.drop_column('label_suggestions', 'suggested_label_id')
    op.drop_column('label_suggestions', 'target_cells')
    op.drop_column('label_suggestions', 'suggestion_type')
    op.drop_column('label_suggestions', 'project_id')
    
    # Rimuovere da label_applications
    op.drop_column('label_applications', 'authorization_status')
    op.drop_column('label_applications', 'approval_status')
    op.drop_column('label_applications', 'authorized_at')
    op.drop_column('label_applications', 'authorized_by')
    
    # Rimuovere da labels
    op.drop_column('labels', 'usage_count')
    op.drop_column('labels', 'created_by')
'''.format(date=datetime.now().isoformat())
    
    print("📄 Contenuto migrazione unificata preparato")
    print("🎯 Include tutti i campi necessari per Task 2.4")
    
    return migration_content

def alternative_strategy_force_single_head():
    """Strategia alternativa: forzare una singola head"""
    
    print("\n=== STRATEGIA ALTERNATIVA: FORCE SINGLE HEAD ===")
    
    print("🔧 Approccio diretto:")
    print("1. Scegliere una head come 'master'")
    print("2. Eliminare fisicamente le altre migration files")
    print("3. Ricreare revision history pulita")
    print("4. Forzare upgrade a head unica")
    
    master_head_candidates = [
        "fe7f4e6d2ea1",  # Task 2.1 authorization fields
        "912d14cfffc3",  # Merge task 2.1
        "increase_column_name_length"  # Campo column_name fix
    ]
    
    print("\n🎯 Candidati per head master:")
    for i, head in enumerate(master_head_candidates, 1):
        print(f"{i}. {head}")
    
    print("\n💻 COMANDI ALTERNATIVI:")
    print("   # Opzione 1: Force upgrade alla head più stabile")
    print("   python -m flask db stamp fe7f4e6d2ea1")
    print("   python -m flask db upgrade head")
    print("")
    print("   # Opzione 2: Manual merge tutte le heads")
    print("   python -m flask db merge -m 'task_2_4_resolve_all_heads' fe7f4e6d2ea1 912d14cfffc3")
    
    return master_head_candidates

def check_database_current_status():
    """Verifica lo stato attuale del database"""
    
    print("\n=== VERIFICA STATO DATABASE ===")
    
    print("📋 Cosa verificare:")
    print("1. Quali campi sono già presenti nel DB")
    print("2. Qual è l'ultima migrazione applicata")
    print("3. Se il DB è funzionante nonostante le multiple heads")
    
    print("\n💻 COMANDI VERIFICA:")
    print("   python -m flask db current")
    print("   python -m flask db show [head_id]")
    print("   python verify_auth_fields_fix_task_2_3.py")
    
    return True

def main():
    print("🔧 FIX ALEMBIC MULTIPLE HEADS - STRATEGIA DRASTICA TASK 2.4")
    print("=" * 70)
    
    heads = analyze_heads_situation()
    
    print(f"\n⚠️  PROBLEMA CRITICO: {len(heads)} heads bloccano Task 2.4")
    print("🎯 OBIETTIVO: Risolvere per procedere con Store Etichette")
    
    strategy_drastic_reset()
    alternative_strategy_force_single_head() 
    check_database_current_status()
    create_unified_migration_content()
    
    print("\n🚨 RACCOMANDAZIONE IMMEDIATA:")
    print("1. Verificare stato database attuale con verify script")
    print("2. Se DB funziona, usare strategia FORCE SINGLE HEAD")
    print("3. Scegliere fe7f4e6d2ea1 come head master (Task 2.1)")
    print("4. Creare nuova migrazione Task 2.4 solo per campi labels")
    print("5. Procedere con implementazione Task 2.4")
    
    print("\n✅ PROSSIMO STEP: Eseguire verify script e decidere strategia")

if __name__ == "__main__":
    main()
