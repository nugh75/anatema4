#!/usr/bin/env python3
"""
Script per creare un utente di test nel database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from app.models import User

def create_test_user():
    """Crea l'utente di test"""
    app = create_app()
    
    with app.app_context():
        try:
            # Controlla se l'utente esiste già
            existing_user = User.query.filter_by(username='daniele-d').first()
            if existing_user:
                print("✅ Utente 'daniele-d' già esistente")
                return True
            
            # Crea nuovo utente
            new_user = User(
                username='daniele-d',
                email='daniele@test.com',
                first_name='Daniele',
                last_name='D',
                role='admin',
                admin_flag=True,
                is_active=True,
                email_verified=True
            )
            new_user.set_password('Temp1234!')
            
            db.session.add(new_user)
            db.session.commit()
            
            print("✅ Utente 'daniele-d' creato con successo!")
            print("   Username: daniele-d")
            print("   Password: Temp1234!")
            print("   Ruolo: admin")
            return True
            
        except Exception as e:
            print(f"❌ Errore nella creazione utente: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = create_test_user()
    sys.exit(0 if success else 1)
