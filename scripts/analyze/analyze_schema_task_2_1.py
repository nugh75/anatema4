#!/usr/bin/env python3
"""
Analisi Schema Database per Task 2.1 - Sistema Etichettatura Unificato
Verifica stato attuale vs requisiti definiti nel MASTER_REFACTORING.md
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.database import db
from sqlalchemy import inspect, text
import json

def analyze_table_schema(table_name):
    """Analizza schema di una tabella specifica"""
    print(f"\n=== ANALISI TABELLA: {table_name.upper()} ===")
    
    inspector = inspect(db.engine)
    
    if not inspector.has_table(table_name):
        print(f"❌ Tabella '{table_name}' NON ESISTE")
        return False
    
    columns = inspector.get_columns(table_name)
    
    print(f"✅ Tabella '{table_name}' esistente con {len(columns)} colonne:")
    for col in columns:
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        default = f" DEFAULT {col['default']}" if col['default'] else ""
        print(f"  - {col['name']}: {col['type']} {nullable}{default}")
    
    # Verifica chiavi esterne
    foreign_keys = inspector.get_foreign_keys(table_name)
    if foreign_keys:
        print(f"\n🔗 Chiavi esterne ({len(foreign_keys)}):")
        for fk in foreign_keys:
            print(f"  - {fk['constrained_columns'][0]} -> {fk['referred_table']}.{fk['referred_columns'][0]}")
    
    return True

def check_required_fields():
    """Verifica campi richiesti per il nuovo sistema"""
    print("\n" + "="*60)
    print("VERIFICA CAMPI RICHIESTI PER SISTEMA UNIFICATO")
    print("="*60)
    
    # Campi richiesti per ogni tabella
    required_fields = {
        'labels': [
            'created_by',    # UUID FK users.id - DA AGGIUNGERE
            'usage_count',   # INTEGER DEFAULT 0 - DA AGGIUNGERE  
            'is_ai_suggested'  # BOOLEAN DEFAULT FALSE - DA AGGIUNGERE
        ],
        'label_applications': [
            'authorized_by',    # UUID FK users.id - DA AGGIUNGERE
            'authorized_at',    # TIMESTAMP - DA AGGIUNGERE
            'suggestion_id'     # UUID FK label_suggestions.id - DA AGGIUNGERE
        ],
        'label_suggestions': [
            'project_id',           # UUID FK projects.id - DA AGGIUNGERE
            'suggestion_type',      # VARCHAR(20) - DA AGGIUNGERE
            'target_cells',         # JSON - DA AGGIUNGERE
            'suggested_label_id',   # INTEGER FK labels.id - DA AGGIUNGERE
            'created_by'            # UUID FK users.id - DA AGGIUNGERE
        ]
    }
    
    inspector = inspect(db.engine)
    
    for table_name, fields in required_fields.items():
        print(f"\n📋 Verifica campi richiesti per '{table_name}':")
        
        if not inspector.has_table(table_name):
            print(f"  ❌ Tabella '{table_name}' non esiste!")
            continue
            
        existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
        
        for field in fields:
            if field in existing_columns:
                print(f"  ✅ {field} - GIÀ PRESENTE")
            else:
                print(f"  ❌ {field} - DA AGGIUNGERE")

def generate_migration_sql():
    """Genera SQL per le migrazioni necessarie"""
    print("\n" + "="*60)
    print("SQL MIGRAZIONI NECESSARIE")
    print("="*60)
    
    migration_sql = """
-- Task 2.1 - Database Schema per Sistema Etichettatura Unificato
-- Aggiunta campi per workflow autorizzazioni

-- 1. Modifica tabella 'labels' (Store Etichette)
ALTER TABLE labels ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id);
ALTER TABLE labels ADD COLUMN IF NOT EXISTS usage_count INTEGER DEFAULT 0;
ALTER TABLE labels ADD COLUMN IF NOT EXISTS is_ai_suggested BOOLEAN DEFAULT FALSE;

-- 2. Modifica tabella 'label_applications' (Applicazioni)
ALTER TABLE label_applications ADD COLUMN IF NOT EXISTS authorized_by UUID REFERENCES users(id);
ALTER TABLE label_applications ADD COLUMN IF NOT EXISTS authorized_at TIMESTAMP;
ALTER TABLE label_applications ADD COLUMN IF NOT EXISTS suggestion_id UUID REFERENCES label_suggestions(id);

-- 3. Modifica tabella 'label_suggestions' (Suggerimenti AI)
ALTER TABLE label_suggestions ADD COLUMN IF NOT EXISTS project_id UUID REFERENCES projects(id);
ALTER TABLE label_suggestions ADD COLUMN IF NOT EXISTS suggestion_type VARCHAR(20) DEFAULT 'store_label';
ALTER TABLE label_suggestions ADD COLUMN IF NOT EXISTS target_cells JSON;
ALTER TABLE label_suggestions ADD COLUMN IF NOT EXISTS suggested_label_id INTEGER REFERENCES labels(id);
ALTER TABLE label_suggestions ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id);

-- 4. Indici per performance
CREATE INDEX IF NOT EXISTS idx_labels_created_by ON labels(created_by);
CREATE INDEX IF NOT EXISTS idx_labels_project_usage ON labels(project_id, usage_count DESC);
CREATE INDEX IF NOT EXISTS idx_label_apps_authorized ON label_applications(authorized_by, authorized_at);
CREATE INDEX IF NOT EXISTS idx_label_suggestions_project ON label_suggestions(project_id, suggestion_type);
CREATE INDEX IF NOT EXISTS idx_label_suggestions_status ON label_suggestions(status, created_at DESC);

-- 5. Update usage_count per etichette esistenti (OPZIONALE - può essere calcolato dinamicamente)
-- UPDATE labels SET usage_count = (
--     SELECT COUNT(*) FROM label_applications 
--     WHERE label_applications.label_id = labels.id AND is_active = TRUE
-- );
"""
    
    print(migration_sql)
    return migration_sql

def main():
    app = create_app()
    
    with app.app_context():
        print("🔍 ANALISI SCHEMA DATABASE - TASK 2.1")
        print("Sistema Etichettatura Unificato")
        print("="*60)
        
        # Verifica connessione database
        try:
            # Usa la sintassi corretta per SQLAlchemy 2.x
            with db.engine.connect() as connection:
                result = connection.execute(text('SELECT 1'))
                result.fetchone()
            print("✅ Connessione database: OK")
        except Exception as e:
            print(f"❌ Errore connessione database: {e}")
            return
        
        # Analizza tabelle principali
        tables_to_analyze = ['labels', 'label_applications', 'label_suggestions']
        
        for table in tables_to_analyze:
            analyze_table_schema(table)
        
        # Verifica campi richiesti
        check_required_fields()
        
        # Genera SQL migrazioni
        migration_sql = generate_migration_sql()
        
        print("\n" + "="*60)
        print("RIEPILOGO TASK 2.1")
        print("="*60)
        print("✅ Schema esistente analizzato")
        print("📋 Campi mancanti identificati")  
        print("🔧 SQL migrazioni generato")
        print("\nProssimi step:")
        print("1. Creare file migrazione Alembic")
        print("2. Eseguire migrazione")
        print("3. Testare integrità schema")
        print("4. Validare workflow supportati")

if __name__ == '__main__':
    main()
