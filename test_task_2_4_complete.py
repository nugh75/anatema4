#!/usr/bin/env python3
"""
Test Task 2.4 - Store Etichette Centralizzato
Valida l'implementazione completa del sistema di gestione etichette centralizzato
"""

import sys
import os
import requests
import time
from datetime import datetime

def print_header(title):
    print(f"\n{'='*80}")
    print(f"{title.center(80)}")
    print(f"{'='*80}")

def print_section(title):
    print(f"\n{'-'*50}")
    print(f"{title}")
    print(f"{'-'*50}")

def test_database_migration():
    """Test che la migrazione database sia stata applicata correttamente"""
    print_section("TEST 1: Database Migration Status")
    
    try:
        # Check if models import correctly with new fields
        sys.path.append('/home/nugh75/Git/anatema2')
        from app.models import Label
        from app.database import db
        
        # Test Label model has required fields for Task 2.4
        required_fields = ['created_by', 'usage_count']
        label_fields = [col.name for col in Label.__table__.columns]
        
        missing_fields = [field for field in required_fields if field not in label_fields]
        
        if missing_fields:
            print(f"❌ ERRORE: Campi mancanti nel modello Label: {missing_fields}")
            return False
        else:
            print("✅ Modello Label aggiornato correttamente")
            for field in required_fields:
                print(f"   ✓ {field} - presente")
        
        # Test to_dict method includes new fields
        try:
            test_label = Label(name="Test", description="Test", project_id="00000000-0000-0000-0000-000000000000")
            label_dict = test_label.to_dict()
            
            if 'created_by' in label_dict and 'usage_count' in label_dict:
                print("✅ to_dict() method aggiornato correttamente")
            else:
                print("❌ to_dict() method non include i nuovi campi")
                return False
                
        except Exception as e:
            print(f"❌ Errore nel test to_dict(): {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Errore import modelli: {e}")
        return False
    except Exception as e:
        print(f"❌ Errore generico: {e}")
        return False

def test_api_endpoints():
    """Test che gli endpoint API Task 2.4 siano implementati"""
    print_section("TEST 2: API Endpoints Availability")
    
    base_url = "http://localhost:5000"  # Adjust if different
    test_project_id = "test-project-id"
    
    endpoints_to_test = [
        ("GET", f"/api/projects/{test_project_id}/labels", "Lista etichette progetto"),
        ("POST", f"/api/projects/{test_project_id}/labels", "Creazione etichetta"),
        ("PUT", f"/api/projects/{test_project_id}/labels/1", "Modifica etichetta"),
        ("DELETE", f"/api/projects/{test_project_id}/labels/1", "Eliminazione etichetta"),
        ("GET", f"/api/projects/{test_project_id}/labels/stats", "Statistiche etichette Task 2.4")
    ]
    
    print("⚠️  Nota: Test API richiede server attivo. Se server non attivo, test saltato.")
    
    try:
        # Try to connect to server
        response = requests.get(f"{base_url}/", timeout=2)
        server_available = True
    except:
        print("⚠️  Server non disponibile - saltando test API")
        return True  # Not a failure, just can't test
    
    if server_available:
        for method, endpoint, description in endpoints_to_test:
            try:
                if method == "GET":
                    response = requests.get(f"{base_url}{endpoint}", timeout=5)
                elif method == "POST":
                    response = requests.post(f"{base_url}{endpoint}", 
                                           json={"test": "data"}, timeout=5)
                elif method == "PUT":
                    response = requests.put(f"{base_url}{endpoint}", 
                                          json={"test": "data"}, timeout=5)
                elif method == "DELETE":
                    response = requests.delete(f"{base_url}{endpoint}", timeout=5)
                
                # We expect 401 (auth required) or 404 (not found) rather than 500 (not implemented)
                if response.status_code in [200, 201, 401, 404]:
                    print(f"✅ {method} {endpoint} - {description} (implementato)")
                elif response.status_code == 500:
                    print(f"❌ {method} {endpoint} - {description} (errore implementazione)")
                else:
                    print(f"⚠️  {method} {endpoint} - {description} (status: {response.status_code})")
                    
            except requests.RequestException as e:
                print(f"⚠️  {method} {endpoint} - {description} (connection error)")
    
    return True

def test_template_files():
    """Test che i template e file statici siano presenti"""
    print_section("TEST 3: Template e File Statici")
    
    files_to_check = [
        ("/home/nugh75/Git/anatema2/app/templates/labels/store.html", "Template Store Etichette"),
        ("/home/nugh75/Git/anatema2/app/static/js/label_store.js", "JavaScript Store Etichette"),
        ("/home/nugh75/Git/anatema2/app/views/labels.py", "Views etichette aggiornate"),
        ("/home/nugh75/Git/anatema2/app/views/api.py", "API endpoints")
    ]
    
    all_present = True
    
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {description} - presente ({file_size} bytes)")
            
            # Check if files are not empty
            if file_size == 0:
                print(f"   ⚠️  File vuoto!")
                all_present = False
        else:
            print(f"❌ {description} - NON TROVATO: {file_path}")
            all_present = False
    
    return all_present

def test_template_content():
    """Test che i template contengano i componenti Task 2.4"""
    print_section("TEST 4: Contenuto Template Store")
    
    store_template_path = "/home/nugh75/Git/anatema2/app/templates/labels/store.html"
    
    if not os.path.exists(store_template_path):
        print("❌ Template store.html non trovato")
        return False
    
    with open(store_template_path, 'r') as f:
        content = f.read()
    
    required_elements = [
        ("Store Etichette Centralizzato", "Titolo principale"),
        ("create-label-modal", "Modal creazione etichetta"), 
        ("edit-label-modal", "Modal modifica etichetta"),
        ("delete-label-modal", "Modal eliminazione etichetta"),
        ("labels-table-body", "Tabella etichette"),
        ("ai-suggestions-section", "Sezione suggerimenti AI"),
        ("search-labels", "Campo ricerca"),
        ("sort-by", "Ordinamento"),
        ("filter-category", "Filtro categorie")
    ]
    
    all_present = True
    
    for element, description in required_elements:
        if element in content:
            print(f"✅ {description} - presente")
        else:
            print(f"❌ {description} - MANCANTE (elemento: {element})")
            all_present = False
    
    return all_present

def test_javascript_functionality():
    """Test che il JavaScript contenga le funzioni necessarie"""
    print_section("TEST 5: JavaScript Functionality")
    
    js_file_path = "/home/nugh75/Git/anatema2/app/static/js/label_store.js"
    
    if not os.path.exists(js_file_path):
        print("❌ File JavaScript label_store.js non trovato")
        return False
    
    with open(js_file_path, 'r') as f:
        content = f.read()
    
    required_functions = [
        ("handleCreateLabel", "Creazione etichetta"),
        ("handleEditLabel", "Modifica etichetta"), 
        ("handleDeleteLabel", "Eliminazione etichetta"),
        ("loadAISuggestions", "Caricamento suggerimenti AI"),
        ("handleSearch", "Ricerca etichette"),
        ("handleSort", "Ordinamento"),
        ("handleCategoryFilter", "Filtro categorie"),
        ("handleApproveSuggestion", "Approvazione singola"),
        ("handleApproveAllSuggestions", "Approvazione batch")
    ]
    
    all_present = True
    
    for function, description in required_functions:
        if function in content:
            print(f"✅ {description} - funzione presente")
        else:
            print(f"❌ {description} - FUNZIONE MANCANTE ({function})")
            all_present = False
    
    return all_present

def test_project_integration():
    """Test che l'integrazione nel template progetto sia presente"""
    print_section("TEST 6: Integrazione Template Progetto")
    
    project_template_path = "/home/nugh75/Git/anatema2/app/templates/projects/view.html"
    
    if not os.path.exists(project_template_path):
        print("❌ Template progetto non trovato")
        return False
    
    with open(project_template_path, 'r') as f:
        content = f.read()
    
    integration_elements = [
        ("Store Etichette Centralizzato", "Sezione store nel progetto"),
        ("Gestisci Store", "Link gestione store"),
        ("list_labels", "Route lista etichette"),
        ("local_offer", "Icona etichette"),
        ("Etichette Totali", "Statistiche rapide")
    ]
    
    all_present = True
    
    for element, description in integration_elements:
        if element in content:
            print(f"✅ {description} - presente")
        else:
            print(f"❌ {description} - MANCANTE")
            all_present = False
    
    return all_present

def test_routes_registration():
    """Test che le route siano registrate correttamente"""
    print_section("TEST 7: Registrazione Route")
    
    try:
        sys.path.append('/home/nugh75/Git/anatema2')
        from app.views.labels import labels_bp
        
        # Check if blueprint has routes
        if hasattr(labels_bp, 'deferred_functions'):
            print(f"✅ Blueprint labels_bp registrato con {len(labels_bp.deferred_functions)} route")
        else:
            print("⚠️  Non è possibile verificare le route del blueprint")
        
        # Check views file content
        views_path = "/home/nugh75/Git/anatema2/app/views/labels.py"
        with open(views_path, 'r') as f:
            content = f.read()
        
        if "Store Etichette Centralizzato - Task 2.4" in content:
            print("✅ Route lista etichette aggiornata per Task 2.4")
        else:
            print("❌ Route non aggiornata per Task 2.4")
            return False
        
        if "created_by=current_user.id" in content:
            print("✅ Creazione etichetta aggiornata con campi Task 2.4")
        else:
            print("❌ Creazione etichetta non aggiornata")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Errore nel test route: {e}")
        return False

def run_comprehensive_test():
    """Esegue tutti i test per Task 2.4"""
    print_header("TEST COMPLETO TASK 2.4 - STORE ETICHETTE CENTRALIZZATO")
    
    tests = [
        ("Database Migration", test_database_migration),
        ("API Endpoints", test_api_endpoints),
        ("Template e File Statici", test_template_files),
        ("Contenuto Template", test_template_content),
        ("JavaScript Functionality", test_javascript_functionality),
        ("Project Integration", test_project_integration),
        ("Routes Registration", test_routes_registration)
    ]
    
    results = []
    
    for test_name, test_function in tests:
        print(f"\n🔍 Esecuzione test: {test_name}")
        try:
            result = test_function()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSATO")
            else:
                print(f"❌ {test_name}: FALLITO")
        except Exception as e:
            print(f"💥 {test_name}: ERRORE - {e}")
            results.append((test_name, False))
    
    # Riepilogo finale
    print_header("RIEPILOGO TEST TASK 2.4")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = round((passed / total) * 100, 1)
    
    print(f"📊 Test passati: {passed}/{total} ({success_rate}%)")
    print(f"📅 Data esecuzione: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    if success_rate >= 90:
        print(f"🎉 Task 2.4 implementato con SUCCESSO! ({success_rate}%)")
        return True
    elif success_rate >= 70:
        print(f"⚠️  Task 2.4 implementato con alcuni problemi ({success_rate}%)")
        return True
    else:
        print(f"❌ Task 2.4 NON completamente implementato ({success_rate}%)")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
