#!/usr/bin/env python3
"""
Test Script per Anatema
Script di test per verificare il funzionamento dell'applicazione
"""

import requests
import json
import time
import sys
from pathlib import Path

# Configurazione
BASE_URL = 'http://127.0.0.1:5000'
TEST_USER = {
    'username': 'test_user',
    'email': 'test@anatema.com',
    'password': 'test123',
    'confirm_password': 'test123'
}

class AnatemaTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.project_id = None
        
    def print_status(self, message, status='info'):
        """Stampa messaggi di stato colorati"""
        colors = {
            'info': '\033[94m',
            'success': '\033[92m',
            'warning': '\033[93m',
            'error': '\033[91m',
            'end': '\033[0m'
        }
        
        icon = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        
        print(f"{colors.get(status, '')}{icon.get(status, '')} {message}{colors['end']}")
    
    def test_server_connection(self):
        """Test connessione al server"""
        self.print_status("Testing server connection...")
        try:
            response = self.session.get(f'{BASE_URL}/')
            if response.status_code == 200:
                self.print_status("Server is running", 'success')
                return True
            else:
                self.print_status(f"Server returned status {response.status_code}", 'error')
                return False
        except requests.exceptions.ConnectionError:
            self.print_status("Cannot connect to server. Make sure it's running on http://127.0.0.1:5000", 'error')
            return False
    
    def test_user_registration(self):
        """Test registrazione utente"""
        self.print_status("Testing user registration...")
        
        response = self.session.post(
            f'{BASE_URL}/auth/register',
            json=TEST_USER,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            data = response.json()
            self.access_token = data.get('access_token')
            self.user_id = data.get('user', {}).get('id')
            self.print_status("User registration successful", 'success')
            return True
        elif response.status_code == 400:
            # User might already exist, try login
            self.print_status("User might already exist, trying login...", 'warning')
            return self.test_user_login()
        else:
            self.print_status(f"Registration failed: {response.text}", 'error')
            return False
    
    def test_user_login(self):
        """Test login utente"""
        self.print_status("Testing user login...")
        
        login_data = {
            'username': TEST_USER['username'],
            'password': TEST_USER['password']
        }
        
        response = self.session.post(
            f'{BASE_URL}/auth/login',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access_token')
            self.user_id = data.get('user', {}).get('id')
            self.print_status("User login successful", 'success')
            return True
        else:
            self.print_status(f"Login failed: {response.text}", 'error')
            return False
    
    def test_dashboard_access(self):
        """Test accesso dashboard"""
        self.print_status("Testing dashboard access...")
        
        response = self.session.get(f'{BASE_URL}/dashboard')
        
        if response.status_code == 200:
            self.print_status("Dashboard access successful", 'success')
            return True
        else:
            self.print_status(f"Dashboard access failed: {response.status_code}", 'error')
            return False
    
    def test_api_authentication(self):
        """Test autenticazione API"""
        self.print_status("Testing API authentication...")
        
        if not self.access_token:
            self.print_status("No access token available", 'error')
            return False
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = self.session.get(f'{BASE_URL}/api/me', headers=headers)
        
        if response.status_code == 200:
            self.print_status("API authentication successful", 'success')
            return True
        else:
            self.print_status(f"API authentication failed: {response.status_code}", 'error')
            return False
    
    def test_project_creation(self):
        """Test creazione progetto"""
        self.print_status("Testing project creation...")
        
        project_data = {
            'name': 'Test Project',
            'description': 'Progetto di test creato automaticamente',
            'is_public': False
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = self.session.post(
            f'{BASE_URL}/api/projects',
            json=project_data,
            headers=headers
        )
        
        if response.status_code == 201:
            data = response.json()
            self.project_id = data.get('project', {}).get('id')
            self.print_status("Project creation successful", 'success')
            return True
        else:
            self.print_status(f"Project creation failed: {response.text}", 'error')
            return False
    
    def test_project_list(self):
        """Test lista progetti"""
        self.print_status("Testing project list...")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = self.session.get(f'{BASE_URL}/api/projects', headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            projects_count = len(data.get('projects', []))
            self.print_status(f"Project list successful ({projects_count} projects)", 'success')
            return True
        else:
            self.print_status(f"Project list failed: {response.status_code}", 'error')
            return False
    
    def test_label_creation(self):
        """Test creazione etichetta"""
        self.print_status("Testing label creation...")
        
        if not self.project_id:
            self.print_status("No project ID available", 'error')
            return False
        
        label_data = {
            'name': 'Test Label',
            'description': 'Etichetta di test',
            'color': '#ff5722',
            'categories': ['test', 'automation']
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = self.session.post(
            f'{BASE_URL}/api/projects/{self.project_id}/labels',
            json=label_data,
            headers=headers
        )
        
        if response.status_code == 201:
            self.print_status("Label creation successful", 'success')
            return True
        else:
            self.print_status(f"Label creation failed: {response.text}", 'error')
            return False
    
    def test_search_functionality(self):
        """Test funzionalità di ricerca"""
        self.print_status("Testing search functionality...")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = self.session.get(
            f'{BASE_URL}/api/search?q=test',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {})
            total_results = (len(results.get('projects', [])) + 
                           len(results.get('files', [])) + 
                           len(results.get('labels', [])))
            self.print_status(f"Search successful ({total_results} results)", 'success')
            return True
        else:
            self.print_status(f"Search failed: {response.status_code}", 'error')
            return False
    
    def cleanup_test_data(self):
        """Pulisce i dati di test"""
        self.print_status("Cleaning up test data...")
        
        if self.project_id:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Elimina progetto di test
            response = self.session.delete(
                f'{BASE_URL}/api/projects/{self.project_id}',
                headers=headers
            )
            
            if response.status_code == 200:
                self.print_status("Test project deleted", 'success')
            else:
                self.print_status("Failed to delete test project", 'warning')
    
    def run_all_tests(self):
        """Esegue tutti i test"""
        self.print_status("🚀 Starting Anatema Test Suite", 'info')
        print("=" * 50)
        
        tests = [
            ('Server Connection', self.test_server_connection),
            ('User Registration/Login', self.test_user_registration),
            ('Dashboard Access', self.test_dashboard_access),
            ('API Authentication', self.test_api_authentication),
            ('Project Creation', self.test_project_creation),
            ('Project List', self.test_project_list),
            ('Label Creation', self.test_label_creation),
            ('Search Functionality', self.test_search_functionality),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.print_status(f"Test error: {str(e)}", 'error')
                failed += 1
            
            time.sleep(0.5)  # Pausa tra i test
        
        # Cleanup
        print(f"\n🧹 Cleanup")
        self.cleanup_test_data()
        
        # Risultati finali
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS")
        print("=" * 50)
        
        if failed == 0:
            self.print_status(f"All tests passed! ✨ ({passed}/{len(tests)})", 'success')
            return True
        else:
            self.print_status(f"Tests completed with issues: {passed} passed, {failed} failed", 'warning')
            return False

def main():
    """Funzione principale"""
    print("🧪 Anatema Application Tester")
    print("=" * 50)
    
    # Verifica che il server sia in esecuzione
    tester = AnatemaTester()
    
    if not tester.test_server_connection():
        print("\n💡 To start the server:")
        print("   python run.py")
        print("   # or")
        print("   flask run")
        sys.exit(1)
    
    # Esegui tutti i test
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("✅ Anatema is working correctly!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == '__main__':
    main()