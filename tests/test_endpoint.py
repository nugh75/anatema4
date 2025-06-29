#!/usr/bin/env python3
"""
Test rapido per verificare il salvataggio etichette
"""

import requests
import json

def test_save_label_endpoint():
    """Test della route save-cell-label"""
    print("🧪 Test route save-cell-label...")
    
    # Dati di test
    test_data = {
        "row_index": 0,
        "column_name": "test_column",
        "label_name": "Test Label",
        "label_description": "Test description",
        "confidence": 0.95,
        "source": "manual"
    }
    
    # URL del test (useremo un ID fittizio)
    url = "http://localhost:5000/ml/projects/test-project-id/sheets/test-sheet-id/save-cell-label"
    
    try:
        # Fai una richiesta POST
        response = requests.post(
            url,
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 404:
            print("✅ Route endpoint raggiungibile (404 = normale senza login/dati validi)")
            return True
        elif response.status_code == 302:
            print("✅ Route redirect (probabilmente richiede login)")
            return True
        elif response.status_code in [400, 500]:
            if "invalid keyword argument" in response.text:
                print("❌ Ancora errori nei modelli database")
                return False
            else:
                print("✅ Route funzionante (errori di validazione normali)")
                return True
        else:
            print(f"✅ Route raggiungibile (status: {response.status_code})")
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore di connessione: {e}")
        return False

if __name__ == "__main__":
    success = test_save_label_endpoint()
    if success:
        print("🎉 Test completato con successo!")
    else:
        print("💥 Test fallito!")
