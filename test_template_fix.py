#!/usr/bin/env python3
"""
Test fix per errore Jinja2 template projects/view.html
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from app.models import Project, Label, User
from flask_login import login_user
import uuid

def test_template_fix():
    """Test che il template projects/view.html funzioni senza errori"""
    
    app = create_app()
    
    with app.app_context():
        # Setup test user
        with app.test_client() as client:
            # Create test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash='test_hash'
            )
            db.session.add(test_user)
            db.session.commit()
            
            # Create test project
            project = Project(
                name='Test Project',
                description='Test project for template fix',
                owner_id=test_user.id
            )
            db.session.add(project)
            db.session.commit()
            
            # Create test labels
            label1 = Label(
                name='Test Label 1',
                project_id=project.id,
                created_by=test_user.id,
                usage_count=5
            )
            label2 = Label(
                name='Test Label 2',
                project_id=project.id,
                created_by=test_user.id,
                usage_count=0
            )
            db.session.add_all([label1, label2])
            db.session.commit()
            
            print("✅ Setup test data completato")
            
            # Simulate login
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user.id)
                sess['_fresh'] = True
            
            # Test access to project view
            response = client.get(f'/projects/{project.id}')
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Template projects/view.html funziona correttamente!")
                print("✅ Fix errore Jinja2 applicato con successo")
                return True
            else:
                print(f"❌ Errore: {response.status_code}")
                print(f"❌ Response: {response.get_data(as_text=True)[:200]}...")
                return False

if __name__ == "__main__":
    try:
        success = test_template_fix()
        if success:
            print("\n🎉 TEST COMPLETATO CON SUCCESSO!")
        else:
            print("\n❌ TEST FALLITO!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRORE DURANTE IL TEST: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
