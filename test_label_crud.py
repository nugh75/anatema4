#!/usr/bin/env python3
"""
Script di test per le operazioni CRUD delle etichette
Testa creazione, lettura, aggiornamento e cancellazione
"""

import requests
import json
import time
from datetime import datetime

# Configurazione
BASE_URL = "http://localhost:5000"
PROJECT_ID = "2efbcd28-f2ce-4f29-9819-f2079ff9fea3"
USERNAME = "daniele-d"
PASSWORD = "Temp1234!"

def test_label_crud():
    """Test completo delle operazioni CRUD per le etichette"""
    print("🔵 INIZIO TEST CRUD ETICHETTE")
    print("=" * 50)
    
    # Crea una sessione per mantenere i cookies
    session = requests.Session()
    
    # Step 1: Login
    print("\n1. 🔐 TEST LOGIN")
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = session.post(f"{BASE_URL}/auth/login", data=login_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ❌ Login fallito: {response.text}")
        return False
    
    print("   ✅ Login riuscito")
    
    # Step 2: Verifica accesso al progetto
    print("\n2. 📂 TEST ACCESSO PROGETTO")
    project_url = f"{BASE_URL}/projects/{PROJECT_ID}"
    response = session.get(project_url)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ❌ Accesso al progetto fallito")
        return False
    
    print("   ✅ Accesso al progetto riuscito")
    
    # Step 3: CREATE - Crea nuova etichetta
    print("\n3. ➕ TEST CREAZIONE ETICHETTA")
    
    label_data = {
        "name": f"Test Label {datetime.now().strftime('%H:%M:%S')}",
        "description": "Etichetta di test creata automaticamente",
        "color": "#FF5722",
        "categories": ["test", "automation"]
    }
    
    create_url = f"{BASE_URL}/api/projects/{PROJECT_ID}/labels"
    response = session.post(
        create_url,
        json=label_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    
    if response.status_code == 401:
        print("   ❌ Non autorizzato - problema di autenticazione")
        return False
    
    try:
        result = response.json()
        print(f"   Response: {result}")
        
        if response.status_code == 201 or (result.get('success') or result.get('message')):
            print("   ✅ Etichetta creata con successo")
            label_id = result.get('label', {}).get('id')
            if not label_id:
                print("   ⚠️  ID etichetta non trovato nella risposta")
        else:
            print(f"   ❌ Creazione fallita: {result.get('error', 'Errore sconosciuto')}")
            return False
    except json.JSONDecodeError:
        print(f"   ❌ Risposta non è JSON valido: {response.text}")
        return False
    
    # Step 4: READ - Leggi lista etichette
    print("\n4. 📋 TEST LETTURA ETICHETTE")
    
    store_url = f"{BASE_URL}/labels/{PROJECT_ID}"
    response = session.get(store_url)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Lista etichette recuperata")
        # Controlla se la nostra etichetta è presente
        if label_data["name"] in response.text:
            print("   ✅ Etichetta creata trovata nella lista")
        else:
            print("   ⚠️  Etichetta creata non trovata nella lista")
    else:
        print(f"   ❌ Lettura fallita: {response.status_code}")
        return False
    
    # Step 5: UPDATE - Aggiorna etichetta (se abbiamo l'ID)
    if 'label_id' in locals() and label_id:
        print(f"\n5. ✏️  TEST AGGIORNAMENTO ETICHETTA (ID: {label_id})")
        
        update_data = {
            "name": f"Updated Test Label {datetime.now().strftime('%H:%M:%S')}",
            "description": "Etichetta aggiornata dal test automatico",
            "color": "#4CAF50",
            "categories": ["test", "automation", "updated"]
        }
        
        update_url = f"{BASE_URL}/api/projects/{PROJECT_ID}/labels/{label_id}"
        response = session.put(
            update_url,
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        
        try:
            result = response.json()
            print(f"   Response: {result}")
            
            if response.status_code == 200 or result.get('success'):
                print("   ✅ Etichetta aggiornata con successo")
            else:
                print(f"   ❌ Aggiornamento fallito: {result.get('error', 'Errore sconosciuto')}")
        except json.JSONDecodeError:
            print(f"   ❌ Risposta non è JSON valido: {response.text}")
    
    # Step 6: DELETE - Elimina etichetta (se abbiamo l'ID)
    if 'label_id' in locals() and label_id:
        print(f"\n6. 🗑️  TEST ELIMINAZIONE ETICHETTA (ID: {label_id})")
        
        delete_url = f"{BASE_URL}/api/projects/{PROJECT_ID}/labels/{label_id}"
        response = session.delete(delete_url)
        
        print(f"   Status: {response.status_code}")
        
        try:
            result = response.json()
            print(f"   Response: {result}")
            
            if response.status_code == 200 or result.get('success'):
                print("   ✅ Etichetta eliminata con successo")
            else:
                print(f"   ❌ Eliminazione fallita: {result.get('error', 'Errore sconosciuto')}")
        except json.JSONDecodeError:
            print(f"   ❌ Risposta non è JSON valido: {response.text}")
    
    print("\n" + "=" * 50)
    print("🔵 TEST COMPLETATO")
    return True

if __name__ == "__main__":
    try:
        test_label_crud()
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()
