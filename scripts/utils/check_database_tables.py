#!/usr/bin/env python3
"""
Script per verificare quali tabelle sono effettivamente presenti nel database
"""
import sys
import os

# Aggiungi il percorso dell'app
sys.path.append('/home/nugh75/Git/anatema2')

from app import create_app
from app.database import db
from sqlalchemy import inspect, text

def check_database_tables():
    """Controlla quali tabelle sono presenti nel database"""
    print("🔍 Verifica Tabelle Database Anatema2")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Ottieni l'inspector del database
            inspector = inspect(db.engine)
            
            # Ottieni tutte le tabelle esistenti
            existing_tables = inspector.get_table_names()
            existing_tables.sort()
            
            print(f"📊 Tabelle presenti nel database: {len(existing_tables)}")
            print("-" * 40)
            
            # Raggruppa le tabelle per categoria
            core_tables = []
            ml_tables = []
            admin_tables = []
            labeling_tables = []
            other_tables = []
            
            for table in existing_tables:
                if table in ['users', 'projects', 'files', 'excel_sheets', 'excel_columns', 
                           'excel_rows', 'labels', 'cell_labels']:
                    core_tables.append(table)
                elif table.startswith('ml_') or table.startswith('auto_') or table.startswith('column_'):
                    ml_tables.append(table)
                elif (table.startswith('global_') or table.startswith('system_') or 
                      table.startswith('user_role') or table.startswith('audit_')):
                    admin_tables.append(table)
                elif table.startswith('label_') or table.startswith('ai_labeling'):
                    labeling_tables.append(table)
                else:
                    other_tables.append(table)
            
            # Stampa le categorie
            print("🏗️  TABELLE CORE:")
            for table in core_tables:
                print(f"   ✅ {table}")
            
            print(f"\n🤖 TABELLE ML ({len(ml_tables)}):")
            for table in ml_tables:
                print(f"   ✅ {table}")
            
            print(f"\n🏷️  TABELLE LABELING ({len(labeling_tables)}):")
            for table in labeling_tables:
                print(f"   ✅ {table}")
            
            print(f"\n🛡️  TABELLE ADMIN ({len(admin_tables)}):")
            if admin_tables:
                for table in admin_tables:
                    print(f"   ✅ {table}")
            else:
                print("   ❌ Nessuna tabella admin trovata")
            
            if other_tables:
                print(f"\n📋 ALTRE TABELLE ({len(other_tables)}):")
                for table in other_tables:
                    print(f"   ✅ {table}")
            
            # Verifica tabelle attese ma non trovate
            print("\n" + "=" * 60)
            print("📋 ANALISI COMPLETEZZA SCHEMA")
            print("-" * 40)
            
            expected_core = ['users', 'projects', 'files', 'excel_sheets', 'excel_columns', 
                           'excel_rows', 'labels', 'cell_labels']
            expected_ml = ['ml_analyses', 'ml_configurations', 'column_analyses', 
                          'auto_labels', 'auto_label_applications']
            expected_admin = ['global_llm_configurations', 'user_roles', 'user_role_assignments',
                            'system_settings', 'audit_logs']
            expected_labeling = ['label_templates', 'label_generations', 'label_suggestions',
                               'label_applications', 'ai_labeling_sessions', 'label_analytics']
            
            missing_core = [t for t in expected_core if t not in existing_tables]
            missing_ml = [t for t in expected_ml if t not in existing_tables]
            missing_admin = [t for t in expected_admin if t not in existing_tables]
            missing_labeling = [t for t in expected_labeling if t not in existing_tables]
            
            if missing_core:
                print("❌ TABELLE CORE MANCANTI:")
                for table in missing_core:
                    print(f"   - {table}")
            
            if missing_ml:
                print("❌ TABELLE ML MANCANTI:")
                for table in missing_ml:
                    print(f"   - {table}")
            
            if missing_admin:
                print("❌ TABELLE ADMIN MANCANTI:")
                for table in missing_admin:
                    print(f"   - {table}")
            
            if missing_labeling:
                print("❌ TABELLE LABELING MANCANTI:")
                for table in missing_labeling:
                    print(f"   - {table}")
            
            # Verifica migrazioni applicate
            print("\n" + "=" * 60)
            print("📋 MIGRAZIONI APPLICATE")
            print("-" * 40)
            
            try:
                result = db.session.execute(text("SELECT version_num FROM alembic_version"))
                current_version = result.fetchone()
                if current_version:
                    print(f"✅ Versione migrazione corrente: {current_version[0]}")
                else:
                    print("❌ Nessuna migrazione applicata")
            except Exception as e:
                print(f"❌ Errore nel controllare le migrazioni: {e}")
            
            print("\n" + "=" * 60)
            print("📊 RIASSUNTO:")
            print(f"   • Tabelle totali presenti: {len(existing_tables)}")
            print(f"   • Tabelle core: {len(core_tables)}")
            print(f"   • Tabelle ML: {len(ml_tables)}")
            print(f"   • Tabelle labeling: {len(labeling_tables)}")
            print(f"   • Tabelle admin: {len(admin_tables)}")
            print(f"   • Altre tabelle: {len(other_tables)}")
            
            return existing_tables
            
        except Exception as e:
            print(f"❌ Errore nel connettersi al database: {e}")
            return []

if __name__ == "__main__":
    check_database_tables()
