#!/usr/bin/env python3
"""
Script di diagnostica per il sistema di etichette
"""
import requests
import json

BASE_URL = "http://localhost:5000"
PROJECT_ID = "2efbcd28-f2ce-4f29-9819-f2079ff9fea3"

def diagnostic_check():
    print("🔧 DIAGNOSTICA SISTEMA ETICHETTE")
    print("=" * 50)
    
    # Test 1: Verifica autenticazione
    print("\n1. 🔐 Test Autenticazione")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/status", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Autenticato: {data.get('authenticated', False)}")
        else:
            print(f"   ❌ Non autenticato: {response.text}")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    # Test 2: Verifica API etichette
    print("\n2. 📋 Test API Etichette")
    try:
        response = requests.get(f"{BASE_URL}/api/projects/{PROJECT_ID}/labels", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            labels = data.get('labels', [])
            print(f"   ✅ Trovate {len(labels)} etichette")
            if labels:
                test_label = labels[0]
                print(f"   Prima etichetta: {test_label.get('name')} (ID: {test_label.get('id')})")
                return test_label.get('id')
        else:
            print(f"   ❌ Errore API: {response.text}")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    return None

def test_label_operations(label_id):
    if not label_id:
        print("\n❌ Nessun ID etichetta per i test")
        return
    
    print(f"\n3. 🔧 Test Operazioni Etichetta ID: {label_id}")
    
    # Test 3a: Get usage stats
    print("\n   3a. Test GET usage stats")
    try:
        response = requests.get(f"{BASE_URL}/api/projects/{PROJECT_ID}/labels/{label_id}/usage", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Usage count: {data.get('usage_count', 'N/A')}")
        else:
            print(f"   ❌ Errore usage: {response.text}")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    # Test 3b: Get cell values
    print("\n   3b. Test GET cell values")
    try:
        response = requests.get(f"{BASE_URL}/api/projects/{PROJECT_ID}/labels/{label_id}/cell-values", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            cell_values = data.get('cell_values', [])
            print(f"   ✅ Trovati {len(cell_values)} valori celle")
        else:
            print(f"   ❌ Errore cell values: {response.text}")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    # Test 3c: PUT update (test senza modificare davvero)
    print("\n   3c. Test PUT update (dry run)")
    test_data = {
        "name": "TEST_UPDATE",
        "description": "Test update",
        "color": "#FF0000",
        "categories": ["test"]
    }
    try:
        # Non eseguiamo davvero per non modificare i dati
        print(f"   📝 Dati test: {test_data}")
        print(f"   📍 URL: PUT {BASE_URL}/api/projects/{PROJECT_ID}/labels/{label_id}")
        print("   ⚠️  Test PUT non eseguito per sicurezza")
    except Exception as e:
        print(f"   ❌ Errore: {e}")

def test_javascript_compatibility():
    print("\n4. 🌐 Test Compatibilità JavaScript")
    
    # Test se il server risponde correttamente alle richieste AJAX
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/status", headers=headers, timeout=5)
        print(f"   Status con headers AJAX: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Server compatibile con AJAX")
        else:
            print(f"   ❌ Problema AJAX: {response.text}")
    except Exception as e:
        print(f"   ❌ Errore AJAX: {e}")

def test_session_handling():
    print("\n5. 🍪 Test Gestione Sessioni")
    
    # Crea una sessione per testare i cookie
    session = requests.Session()
    
    try:
        # Test con sessione
        response = session.get(f"{BASE_URL}/api/auth/status", timeout=5)
        print(f"   Status con sessione: {response.status_code}")
        
        # Verifica cookie
        cookies = session.cookies.get_dict()
        print(f"   Cookie trovati: {len(cookies)}")
        for name, value in cookies.items():
            print(f"   - {name}: {value[:20]}..." if len(value) > 20 else f"   - {name}: {value}")
        
        if cookies:
            print("   ✅ Gestione cookie funzionante")
        else:
            print("   ⚠️  Nessun cookie trovato")
            
    except Exception as e:
        print(f"   ❌ Errore sessione: {e}")

def check_api_endpoints():
    print("\n6. 🎯 Verifica Endpoint API Specifici")
    
    endpoints = [
        f"/api/projects/{PROJECT_ID}/labels",
        f"/api/auth/status", 
        f"/static/js/label_store.js",
        f"/labels/{PROJECT_ID}"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            status_icon = "✅" if response.status_code == 200 else "❌"
            print(f"   {status_icon} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: Errore - {e}")

if __name__ == "__main__":
    try:
        print("Avvio diagnostica completa...\n")
        
        # Esegui tutti i test
        label_id = diagnostic_check()
        test_label_operations(label_id)
        test_javascript_compatibility()
        test_session_handling()
        check_api_endpoints()
        
        print("\n" + "=" * 50)
        print("🏁 DIAGNOSTICA COMPLETATA")
        print("\nSe tutti i test sono ✅, il problema è nel JavaScript frontend.")
        print("Se ci sono ❌, il problema è nel backend/API.")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Diagnostica interrotta dall'utente")
    except Exception as e:
        print(f"\n\n💥 Errore durante diagnostica: {e}")
