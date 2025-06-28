#!/usr/bin/env python3
"""Script per testare il login dell'utente"""

import json
from app import create_app
from app.database import db
from app.models import User

def test_login_api():
    """Test del login tramite API"""
    app = create_app()
    
    with app.app_context():
        # Test con Flask test client
        with app.test_client() as client:
            # Test login con username
            response = client.post('/auth/login', 
                                 json={
                                     'username': 'daniele-d',
                                     'password': 'Temp1234!'
                                 },
                                 content_type='application/json')
            
            print(f"Login con username - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print("✓ Login riuscito!")
                print(f"  - Access token presente: {'access_token' in data}")
                print(f"  - User data presente: {'user' in data}")
                if 'user' in data:
                    print(f"  - Username: {data['user']['username']}")
                    print(f"  - Email: {data['user']['email']}")
            else:
                print("✗ Login fallito!")
                print(f"  - Response: {response.get_json()}")
            
            print()
            
            # Test login con email
            response = client.post('/auth/login', 
                                 json={
                                     'username': 'daniele.dragoni@gmail.com',
                                     'password': 'Temp1234!'
                                 },
                                 content_type='application/json')
            
            print(f"Login con email - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print("✓ Login riuscito!")
                print(f"  - Access token presente: {'access_token' in data}")
                print(f"  - User data presente: {'user' in data}")
            else:
                print("✗ Login fallito!")
                print(f"  - Response: {response.get_json()}")

def test_login_form():
    """Test del login tramite form"""
    app = create_app()
    
    with app.app_context():
        with app.test_client() as client:
            # Test login form
            response = client.post('/auth/login', 
                                 data={
                                     'username': 'daniele-d',
                                     'password': 'Temp1234!'
                                 })
            
            print(f"\nLogin form - Status: {response.status_code}")
            if response.status_code == 302:  # Redirect dopo login riuscito
                print("✓ Login form riuscito! (redirect)")
                print(f"  - Location: {response.headers.get('Location')}")
            else:
                print("✗ Login form fallito!")
                print(f"  - Response length: {len(response.data)}")

if __name__ == '__main__':
    print("=== Test Login API ===")
    test_login_api()
    
    print("\n=== Test Login Form ===")
    test_login_form()