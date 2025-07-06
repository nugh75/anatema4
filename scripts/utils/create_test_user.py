#!/usr/bin/env python3
"""Script per creare un utente di test"""

from app import create_app
from app.database import db
from app.models import User
from werkzeug.security import generate_password_hash

def create_test_user():
    app = create_app()
    
    with app.app_context():
        # Controlla se l'utente esiste già
        existing_user = User.query.filter_by(username='daniele-d').first()
        if existing_user:
            print("L'utente 'daniele-d' esiste già!")
            return
        
        # Crea il nuovo utente
        user = User(
            username='daniele-d',
            email='daniele@example.com',
            password_hash=generate_password_hash('Temp1234!')
        )
        
        db.session.add(user)
        db.session.commit()
        
        print("Utente 'daniele-d' creato con successo!")
        print("Username: daniele-d")
        print("Password: Temp1234!")

if __name__ == '__main__':
    create_test_user()