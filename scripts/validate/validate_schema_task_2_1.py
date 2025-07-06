#!/usr/bin/env python3
"""
Validazione Schema Database per Task 2.1
Sistema Etichettatura Unificato con Autorizzazioni

Verifica che tutti i campi necessari siano stati aggiunti correttamente
alle tabelle labels, label_applications e label_suggestions.
"""

import os
import sys
from sqlalchemy import create_engine, inspect, text
from config.config import config

def validate_database_schema():
    """
    Valida che lo schema database supporti il sistema di etichettatura unificato
    """
    print("🔍 VALIDAZIONE SCHEMA DATABASE - TASK 2.1")
    print("=" * 60)
    
    # Connessione al database
    config_obj = config['development']
    engine = create_engine(config_obj.SQLALCHEMY_DATABASE_URI)
    inspector = inspect(engine)
    
    # Test risultati
    results = {
        'labels': {'status': '❌', 'missing': [], 'present': []},
        'label_applications': {'status': '❌', 'missing': [], 'present': []},
        'label_suggestions': {'status': '❌', 'missing': [], 'present': []},
        'foreign_keys': {'status': '❌', 'missing': [], 'present': []}
    }
    
    # 1. Verifica tabella LABELS
    print("\n📋 1. VERIFICA TABELLA 'labels'")
    print("-" * 40)
    
    labels_columns = inspector.get_columns('labels')
    labels_column_names = [col['name'] for col in labels_columns]
    
    required_labels_fields = ['created_by', 'usage_count']
    
    for field in required_labels_fields:
        if field in labels_column_names:
            results['labels']['present'].append(field)
            print(f"✅ Campo '{field}' presente")
        else:
            results['labels']['missing'].append(field)
            print(f"❌ Campo '{field}' MANCANTE")
    
    if not results['labels']['missing']:
        results['labels']['status'] = '✅'
    
    # 2. Verifica tabella LABEL_APPLICATIONS
    print("\n📋 2. VERIFICA TABELLA 'label_applications'")
    print("-" * 40)
    
    label_app_columns = inspector.get_columns('label_applications')
    label_app_column_names = [col['name'] for col in label_app_columns]
    
    required_label_app_fields = ['authorized_by', 'authorized_at']
    
    for field in required_label_app_fields:
        if field in label_app_column_names:
            results['label_applications']['present'].append(field)
            print(f"✅ Campo '{field}' presente")
        else:
            results['label_applications']['missing'].append(field)
            print(f"❌ Campo '{field}' MANCANTE")
    
    if not results['label_applications']['missing']:
        results['label_applications']['status'] = '✅'
    
    # 3. Verifica tabella LABEL_SUGGESTIONS
    print("\n📋 3. VERIFICA TABELLA 'label_suggestions'")
    print("-" * 40)
    
    label_sugg_columns = inspector.get_columns('label_suggestions')
    label_sugg_column_names = [col['name'] for col in label_sugg_columns]
    
    required_label_sugg_fields = [
        'project_id', 'suggestion_type', 'target_cells', 
        'suggested_label_id', 'created_by'
    ]
    
    for field in required_label_sugg_fields:
        if field in label_sugg_column_names:
            results['label_suggestions']['present'].append(field)
            print(f"✅ Campo '{field}' presente")
        else:
            results['label_suggestions']['missing'].append(field)
            print(f"❌ Campo '{field}' MANCANTE")
    
    if not results['label_suggestions']['missing']:
        results['label_suggestions']['status'] = '✅'
    
    # 4. Verifica Foreign Keys
    print("\n🔗 4. VERIFICA FOREIGN KEYS")
    print("-" * 40)
    
    # Verifica FK per labels
    labels_fks = inspector.get_foreign_keys('labels')
    labels_fk_columns = [fk['constrained_columns'][0] for fk in labels_fks]
    
    # Verifica FK per label_applications  
    label_app_fks = inspector.get_foreign_keys('label_applications')
    label_app_fk_columns = [fk['constrained_columns'][0] for fk in label_app_fks]
    
    # Verifica FK per label_suggestions
    label_sugg_fks = inspector.get_foreign_keys('label_suggestions')
    label_sugg_fk_columns = [fk['constrained_columns'][0] for fk in label_sugg_fks]
    
    expected_fks = {
        'labels.created_by': 'created_by' in labels_fk_columns,
        'label_applications.authorized_by': 'authorized_by' in label_app_fk_columns,
        'label_suggestions.project_id': 'project_id' in label_sugg_fk_columns,
        'label_suggestions.suggested_label_id': 'suggested_label_id' in label_sugg_fk_columns,
        'label_suggestions.created_by': 'created_by' in label_sugg_fk_columns
    }
    
    fk_all_present = True
    for fk_name, is_present in expected_fks.items():
        if is_present:
            results['foreign_keys']['present'].append(fk_name)
            print(f"✅ FK '{fk_name}' presente")
        else:
            results['foreign_keys']['missing'].append(fk_name)
            print(f"❌ FK '{fk_name}' MANCANTE")
            fk_all_present = False
    
    if fk_all_present:
        results['foreign_keys']['status'] = '✅'
    
    # 5. Test Workflow Supportati
    print("\n⚙️ 5. VERIFICA WORKFLOW SUPPORTATI")
    print("-" * 40)
    
    workflow_tests = {
        'etichettatura_umana': True,  # Non richiede campi aggiuntivi
        'etichettatura_ai_con_autorizzazione': all([
            'authorized_by' in label_app_column_names,
            'authorized_at' in label_app_column_names
        ]),
        'store_etichette_centralizzato': all([
            'created_by' in labels_column_names,
            'usage_count' in labels_column_names
        ]),
        'suggerimenti_ai_per_store': all([
            'suggestion_type' in label_sugg_column_names,
            'suggested_label_id' in label_sugg_column_names,
            'target_cells' in label_sugg_column_names
        ])
    }
    
    for workflow, supported in workflow_tests.items():
        if supported:
            print(f"✅ Workflow '{workflow}' SUPPORTATO")
        else:
            print(f"❌ Workflow '{workflow}' NON SUPPORTATO")
    
    # 6. Riepilogo Finale
    print("\n📊 RIEPILOGO VALIDAZIONE")
    print("=" * 60)
    
    all_tables_ok = all(result['status'] == '✅' for result in results.values())
    all_workflows_ok = all(workflow_tests.values())
    
    if all_tables_ok and all_workflows_ok:
        print("🎉 TASK 2.1 COMPLETATO CON SUCCESSO!")
        print("✅ Tutti i campi necessari sono presenti")
        print("✅ Tutte le foreign keys sono configurate")
        print("✅ Tutti i workflow sono supportati")
        print("\n🚀 PRONTO PER TASK 2.2 (Backend API)")
        return True
    else:
        print("❌ TASK 2.1 NON COMPLETATO")
        print("⚠️ Alcuni campi o foreign keys mancano")
        print("⚠️ Verificare la migrazione database")
        return False

if __name__ == "__main__":
    try:
        success = validate_database_schema()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"❌ ERRORE durante validazione: {e}")
        sys.exit(1)
