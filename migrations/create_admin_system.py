#!/usr/bin/env python3
"""
Script di migrazione per creare il sistema di amministrazione
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from app import create_app
from app.database import db
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet
from sqlalchemy import text

def create_admin_tables():
    """Crea le tabelle del sistema admin"""
    
    # Connessione al database
    app = create_app()
    
    with app.app_context():
        print("🔧 Creazione tabelle sistema amministrazione...")
        
        # Import dei modelli admin
        from app.models_admin import (
            GlobalLLMConfiguration, UserRole, UserRoleAssignment,
            SystemSettings, AuditLog
        )
        
        # Crea tutte le tabelle
        db.create_all()
        print("✅ Tabelle create con successo")
        
        # Aggiungi le nuove colonne alla tabella users se non esistono
        try:
            print("📝 Controllo e aggiunta nuove colonne alla tabella users...")
            
            # Lista delle colonne da controllare/aggiungere
            columns_to_add = [
                ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                ("first_name", "VARCHAR(100)"),
                ("last_name", "VARCHAR(100)"),
                ("admin_flag", "BOOLEAN DEFAULT FALSE"),
                ("is_superuser", "BOOLEAN DEFAULT FALSE"),
                ("last_login", "TIMESTAMP"),
                ("login_attempts", "INTEGER DEFAULT 0"),
                ("locked_until", "TIMESTAMP"),
                ("email_verified", "BOOLEAN DEFAULT FALSE"),
                ("email_verification_token", "VARCHAR(100)"),
                ("email_verified_at", "TIMESTAMP")
            ]
            
            for column_name, column_def in columns_to_add:
                # Controlla se la colonna esiste
                result = db.session.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='{column_name}'"))
                if not result.fetchone():
                    try:
                        db.session.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"))
                        print(f"  ✅ Aggiunta colonna: {column_name}")
                    except Exception as col_e:
                        print(f"  ⚠️  Errore aggiungendo {column_name}: {col_e}")
                else:
                    print(f"  ℹ️  Colonna già esistente: {column_name}")
            
            db.session.commit()
            print("✅ Controllo colonne completato")
                
        except Exception as e:
            print(f"⚠️  Errore durante l'aggiunta delle colonne: {e}")
            db.session.rollback()
        
        return True

def create_default_roles():
    """Crea i ruoli di default del sistema"""
    
    app = create_app()
    
    with app.app_context():
        print("👥 Creazione ruoli di default...")
        
        from app.models_admin import UserRole
        
        # Ruoli di default
        default_roles = [
            {
                'name': 'superadmin',
                'description': 'Accesso completo a tutto il sistema',
                'permissions': [
                    'admin_access', 'user_management', 'role_management',
                    'system_settings', 'llm_management', 'audit_logs',
                    'maintenance_mode', 'backup_restore'
                ]
            },
            {
                'name': 'admin',
                'description': 'Gestione utenti e configurazioni LLM',
                'permissions': [
                    'admin_access', 'user_management', 'llm_management',
                    'system_settings', 'audit_logs'
                ]
            },
            {
                'name': 'moderator',
                'description': 'Gestione limitata degli utenti',
                'permissions': [
                    'admin_access', 'user_view', 'audit_logs'
                ]
            },
            {
                'name': 'user',
                'description': 'Utente standard del sistema',
                'permissions': [
                    'project_create', 'project_manage', 'file_upload'
                ]
            }
        ]
        
        for role_data in default_roles:
            # Controlla se il ruolo esiste già
            existing_role = UserRole.query.filter_by(name=role_data['name']).first()
            if not existing_role:
                role = UserRole(
                    name=role_data['name'],
                    description=role_data['description'],
                    permissions=role_data['permissions'],
                    created_at=datetime.utcnow()
                )
                db.session.add(role)
                print(f"  ✅ Creato ruolo: {role_data['name']}")
            else:
                print(f"  ℹ️  Ruolo già esistente: {role_data['name']}")
        
        db.session.commit()
        print("✅ Ruoli di default creati")

def create_default_settings():
    """Crea le impostazioni di default del sistema"""
    
    app = create_app()
    
    with app.app_context():
        print("⚙️  Creazione impostazioni di default...")
        
        from app.models_admin import SystemSettings
        
        # Controlla se esistono già impostazioni
        existing_settings = SystemSettings.query.first()
        if not existing_settings:
            settings = SystemSettings(
                app_name='Anatema - Sistema di Analisi e Labeling',
                app_version='2.0.0',
                app_description='Sistema avanzato per l\'analisi e labeling di dati Excel con AI',
                theme='light',
                primary_color='#1976d2',
                secondary_color='#dc004e',
                max_projects_per_user=10,
                max_file_size_mb=100,
                max_files_per_project=50,
                session_timeout_minutes=120,
                password_min_length=8,
                require_email_verification=False,
                max_login_attempts=5,
                enable_email_notifications=False,
                enable_system_logs=True,
                log_level='INFO',
                maintenance_mode=False,
                maintenance_message='Il sistema è temporaneamente in manutenzione. Riprova più tardi.',
                created_at=datetime.utcnow()
            )
            
            db.session.add(settings)
            db.session.commit()
            print("  ✅ Impostazioni di default create")
        else:
            print("  ℹ️  Impostazioni già esistenti")

def create_default_llm_config():
    """Crea una configurazione LLM di default"""
    
    app = create_app()
    
    with app.app_context():
        print("🤖 Creazione configurazione LLM di default...")
        
        from app.models_admin import GlobalLLMConfiguration
        
        # Controlla se esiste già una configurazione
        existing_config = GlobalLLMConfiguration.query.filter_by(is_active=True).first()
        if not existing_config:
            config = GlobalLLMConfiguration(
                name='Configurazione OpenRouter di Default',
                description='Configurazione predefinita per OpenRouter con Claude 3 Haiku',
                provider='openrouter',
                model_name='anthropic/claude-3-haiku',
                api_url='https://openrouter.ai/api/v1',
                max_tokens=4000,
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                max_requests_per_minute=60,
                max_requests_per_day=1000,
                cost_per_token=0.000001,
                is_active=True,
                is_default=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(config)
            db.session.commit()
            print("  ✅ Configurazione LLM di default creata")
        else:
            print("  ℹ️  Configurazione LLM già esistente")

def create_admin_user():
    """Crea l'utente amministratore di default"""
    
    app = create_app()
    
    with app.app_context():
        print("👤 Creazione utente amministratore...")
        
        from app.models import User
        from app.models_admin import UserRole, UserRoleAssignment
        
        # Controlla se esiste già un admin
        admin_user = User.query.filter(
            (User.role == 'admin') | (User.admin_flag == True) | (User.is_superuser == True)
        ).first()
        
        if not admin_user:
            # Crea l'utente admin
            admin = User(
                id=uuid.uuid4(),
                username='admin',
                email='admin@anatema.local',
                first_name='Amministratore',
                last_name='Sistema',
                role='admin',
                admin_flag=True,
                is_superuser=True,
                is_active=True,
                email_verified=True,
                email_verified_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            admin.set_password('admin123!')  # Cambierà alla prima login
            
            db.session.add(admin)
            db.session.flush()  # Per ottenere l'ID
            
            # Assegna il ruolo superadmin
            superadmin_role = UserRole.query.filter_by(name='superadmin').first()
            if superadmin_role:
                assignment = UserRoleAssignment(
                    user_id=admin.id,
                    role_id=superadmin_role.id,
                    assigned_at=datetime.utcnow()
                )
                db.session.add(assignment)
            
            db.session.commit()
            print("  ✅ Utente amministratore creato:")
            print(f"     Username: admin")
            print(f"     Password: admin123!")
            print(f"     Email: admin@anatema.local")
            print("  ⚠️  CAMBIA LA PASSWORD AL PRIMO LOGIN!")
        else:
            print(f"  ℹ️  Utente amministratore già esistente: {admin_user.username}")

def log_migration():
    """Registra la migrazione nei log di audit"""
    
    app = create_app()
    
    with app.app_context():
        print("📝 Registrazione migrazione nei log...")
        
        from app.models_admin import AuditLog
        
        log_entry = AuditLog(
            action='system_migration',
            resource_type='system',
            resource_id='admin_system_setup',
            description='Migrazione sistema amministrazione completata',
            new_values={
                'migration': 'create_admin_system',
                'version': '2.0.0',
                'timestamp': datetime.utcnow().isoformat(),
                'components': [
                    'admin_tables',
                    'default_roles',
                    'default_settings',
                    'default_llm_config',
                    'admin_user'
                ]
            },
            ip_address='127.0.0.1',
            user_agent='Migration Script',
            timestamp=datetime.utcnow()
        )
        
        db.session.add(log_entry)
        db.session.commit()
        print("✅ Migrazione registrata nei log")

def main():
    """Esegue la migrazione completa"""
    print("🚀 Avvio migrazione sistema amministrazione Anatema")
    print("=" * 60)
    
    try:
        # 1. Crea le tabelle
        create_admin_tables()
        
        # 2. Crea i ruoli di default
        create_default_roles()
        
        # 3. Crea le impostazioni di default
        create_default_settings()
        
        # 4. Crea la configurazione LLM di default
        create_default_llm_config()
        
        # 5. Crea l'utente amministratore
        create_admin_user()
        
        # 6. Registra la migrazione
        log_migration()
        
        print("=" * 60)
        print("🎉 Migrazione completata con successo!")
        print()
        print("📋 PROSSIMI PASSI:")
        print("1. Avvia l'applicazione")
        print("2. Effettua il login con admin/admin123!")
        print("3. Cambia immediatamente la password dell'amministratore")
        print("4. Configura le chiavi API per i provider LLM")
        print("5. Personalizza le impostazioni del sistema")
        
    except Exception as e:
        print(f"❌ Errore durante la migrazione: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    main()