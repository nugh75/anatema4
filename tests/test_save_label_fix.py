#!/usr/bin/env python3
"""
Test script per verificare il fix del salvataggio etichette
"""

import requests
import json

# Configurazione del test - usa progetti reali dal database
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
# Usa un progetto che sappiamo esistere dal log del server
SAVE_LABEL_URL = f"{BASE_URL}/ml/projects/049863cd-44a4-4948-9e9b-206cead88943/sheets/10a1605b-fead-45a7-91fb-259b57e9a2ce/save-cell-label"

def test_label_saving():
    """Test del salvataggio etichette dopo il fix"""
    
    # Crea una sessione per mantenere i cookies
    session = requests.Session()
    
    # 1. Prima ottieni la pagina di login per i token CSRF
    print("1. Ottengo la pagina di login...")
    login_page = session.get(LOGIN_URL)
    print(f"Login page status: {login_page.status_code}")
    
    # 2. Login
    print("\n2. Effettuo login...")
    login_data = {
        'email': 'daniele-d',
        'password': 'Temp1234!'
    }
    
    response = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
    print(f"Login response status: {response.status_code}")
    print(f"Final URL dopo login: {response.url}")
    
    # Verifica se il login è andato a buon fine controllando se siamo stati reindirizzati alla dashboard
    if 'login' in response.url:
        print("❌ Login fallito - ancora sulla pagina di login")
        return False
    
    print("✅ Login effettuato con successo")
    
    # 3. Test salvataggio etichetta
    print("\n3. Test salvataggio etichetta...")
    label_data = {
        'row_index': 10,
        'column_name': 'Test Column',
        'label_name': 'Test Label',
        'label_description': 'Test Description',
        'confidence': 1.0,
        'source': 'manual'
    }
    
    # Prima prova con richiesta JSON
    response = session.post(
        SAVE_LABEL_URL,
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        json=label_data
    )
    
    print(f"Status code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    
    if response.status_code == 200:
        if 'application/json' in response.headers.get('Content-Type', ''):
            try:
                result = response.json()
                print("✅ Etichetta salvata con successo!")
                print(f"Response: {json.dumps(result, indent=2)}")
                return True
            except json.JSONDecodeError:
                print("⚠️ Errore nel parsing JSON")
                return False
        else:
            print("⚠️ Risposta 200 ma non è JSON - probabilmente redirect o HTML")
            print(f"Response text (primi 200 char): {response.text[:200]}...")
            
            # Prova con richiesta form data
            print("\n   Tentativo con form data...")
            form_response = session.post(SAVE_LABEL_URL, data=label_data)
            print(f"   Form request status: {form_response.status_code}")
            
            if form_response.status_code == 200:
                print("✅ Etichetta salvata con form data!")
                return True
            else:
                print(f"❌ Anche form data ha fallito: {form_response.status_code}")
                return False
    else:
        print(f"❌ Errore nel salvataggio: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Errore: {error_data}")
        except:
            print(f"Response text: {response.text[:500]}...")
        return False

if __name__ == "__main__":
    print("🧪 Test del fix per il salvataggio etichette\n")
    success = test_label_saving()
    
    if success:
        print("\n🎉 Tutti i test sono passati!")
    else:
        print("\n❌ I test hanno fallito")
