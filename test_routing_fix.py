#!/usr/bin/env python3
"""
Test rapido per verificare che il routing sia corretto dopo la rimozione del conflitto con labeling_bp
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import User, Project, File
from flask_login import login_user
import requests

def test_ml_dashboard_routing():
    """Test che l'endpoint ml.view_ml_dashboard sia correttamente registrato"""
    app = create_app('testing')
    
    with app.app_context():
        # Verifica che il route sia registrato
        print("=== Test Routing Fix ===")
        
        # Controlla i route registrati
        print("\nRoute registrati per 'ml':")
        for rule in app.url_map.iter_rules():
            if rule.endpoint and 'ml.' in rule.endpoint:
                print(f"  {rule.endpoint}: {rule.rule}")
        
        print("\nRoute registrati per 'labeling' (non dovrebbero esserci):")
        labeling_routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint and 'labeling.' in rule.endpoint:
                labeling_routes.append(f"  {rule.endpoint}: {rule.rule}")
        
        if labeling_routes:
            print("ERRORE: Trovati route per 'labeling':")
            for route in labeling_routes:
                print(route)
        else:
            print("  Nessun route 'labeling' trovato (corretto!)")
        
        # Test di costruzione URL
        try:
            with app.test_request_context():
                from flask import url_for
                test_url = url_for('ml.view_ml_dashboard', project_id='12345678-1234-1234-1234-123456789012')
                print(f"\nTest url_for('ml.view_ml_dashboard'): {test_url}")
                print("✅ URL costruito correttamente!")
        except Exception as e:
            print(f"\n❌ Errore nella costruzione URL: {e}")
            return False
        
        print("\n=== Test completato con successo! ===")
        return True

if __name__ == '__main__':
    success = test_ml_dashboard_routing()
    if not success:
        sys.exit(1)
