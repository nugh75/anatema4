#!/usr/bin/env python3
"""Script per correggere lo status is_active degli utenti esistenti"""

from app import create_app
from app.database import db
from app.models import User

def fix_user_active_status():
    app = create_app()
    
    with app.app_context():
        try:
            # Trova tutti gli utenti con is_active = None
            users_to_fix = User.query.filter(User.is_active.is_(None)).all()
            
            print(f"Trovati {len(users_to_fix)} utenti con is_active = None")
            
            for user in users_to_fix:
                print(f"Correggendo utente: {user.username} ({user.email})")
                user.is_active = True
            
            # Salva le modifiche
            db.session.commit()
            print("✓ Tutti gli utenti sono stati corretti!")
            
            # Verifica il risultato
            print("\nVerifica finale:")
            all_users = User.query.all()
            for user in all_users:
                print(f"- {user.username}: is_active = {user.is_active}")
                
        except Exception as e:
            print(f"✗ Errore durante la correzione: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    fix_user_active_status()