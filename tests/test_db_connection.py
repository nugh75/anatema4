#!/usr/bin/env python3
"""Script per testare la connessione al database e verificare gli utenti"""

from app import create_app
from app.database import db
from app.models import User

def test_database():
    app = create_app()
    
    with app.app_context():
        try:
            # Test connessione database
            result = db.session.execute(db.text('SELECT 1'))
            print('✓ Connessione al database OK')
            
            # Verifica utenti esistenti
            users = User.query.all()
            print(f'Utenti nel database: {len(users)}')
            
            for user in users:
                print(f'- Username: {user.username}, Email: {user.email}, Attivo: {user.is_active}')
                
            # Test specifico per l'utente daniele-d
            test_user = User.query.filter_by(username='daniele-d').first()
            if test_user:
                print(f'✓ Utente daniele-d trovato: {test_user.email}')
                print(f'  - Attivo: {test_user.is_active}')
                print(f'  - Password hash: {test_user.password_hash[:20]}...')
                
                # Test password
                test_password = test_user.check_password('Temp1234!')
                print(f'  - Test password Temp1234!: {test_password}')
            else:
                print('✗ Utente daniele-d non trovato')
                
            # Test anche con email
            test_user_email = User.query.filter_by(email='daniele@example.com').first()
            if test_user_email:
                print(f'✓ Utente con email daniele@example.com trovato: {test_user_email.username}')
            else:
                print('✗ Utente con email daniele@example.com non trovato')
                
        except Exception as e:
            print(f'✗ Errore connessione database: {e}')
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_database()