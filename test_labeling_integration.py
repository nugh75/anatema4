#!/usr/bin/env python3
"""
Test di integrazione per il sistema di etichettatura avanzato
"""

import requests
import json
import os
import sys
from datetime import datetime

def test_labeling_integration():
    """Test completo del sistema di etichettatura"""
    
    print("🔬 Test di Integrazione Sistema Etichettatura")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Verifica che il server sia attivo
    print("🧪 Test connettività server...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server Flask attivo e funzionante")
        else:
            print(f"❌ Server risponde con status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore di connessione al server: {e}")
        return False
    
    # Test 2: Verifica route ML
    print("\n🧪 Test route ML...")
    try:
        # Test dashboard ML (dovrebbe richiedere login)
        response = requests.get(f"{base_url}/ml/projects/test/dashboard", timeout=5)
        if response.status_code in [302, 401]:  # Redirect al login
            print("✅ Route ML protette correttamente")
        else:
            print(f"⚠️ Route ML non protette (status: {response.status_code})")
    except requests.exceptions.RequestException:
        print("⚠️ Route ML non raggiungibili (normale se non loggati)")
    
    # Test 3: Verifica template files
    print("\n🧪 Test file template...")
    
    # Test template colonne
    column_template = "app/templates/ml/advanced_column_view.html"
    if os.path.exists(column_template):
        with open(column_template, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'column-selector' in content and 'save_cell_label' in content:
                print(f"✅ {column_template} contiene elementi necessari")
            else:
                print(f"❌ {column_template} manca elementi essenziali")
                return False
    else:
        print(f"❌ Template non trovato: {column_template}")
        return False
    
    # Test template righe (controlli diversi)
    row_template = "app/templates/ml/advanced_row_view.html"
    if os.path.exists(row_template):
        with open(row_template, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'row-selector' in content or 'advanced_row_view' in content or 'labeling-interface' in content:
                print(f"✅ {row_template} contiene elementi necessari")
            else:
                print(f"⚠️ {row_template} potrebbe necessitare di aggiornamenti")
    else:
        print(f"⚠️ Template opzionale non trovato: {row_template}")
    
    # Test 4: Verifica modelli database
    print("\n🧪 Test struttura database...")
    try:
        with open("app/models.py", 'r', encoding='utf-8') as f:
            models_content = f.read()
            required_models = ["AutoLabel", "AutoLabelApplication", "MLAnalysis"]
            for model in required_models:
                if f"class {model}" in models_content:
                    print(f"✅ Modello {model} presente")
                else:
                    print(f"❌ Modello {model} mancante")
                    return False
    except FileNotFoundError:
        print("❌ File models.py non trovato")
        return False
    
    # Test 5: Verifica route backend
    print("\n🧪 Test route backend...")
    try:
        with open("app/views/ml.py", 'r', encoding='utf-8') as f:
            views_content = f.read()
            required_routes = ["save_cell_label", "remove_cell_label", "advanced_column_view"]
            for route in required_routes:
                if f"def {route}" in views_content:
                    print(f"✅ Route {route} presente")
                else:
                    print(f"❌ Route {route} mancante")
                    return False
    except FileNotFoundError:
        print("❌ File views/ml.py non trovato")
        return False
    
    # Test 6: Verifica static files
    print("\n🧪 Test file statici...")
    static_dirs = ["app/static/css", "app/static/js"]
    for static_dir in static_dirs:
        if os.path.exists(static_dir):
            print(f"✅ Directory {static_dir} presente")
        else:
            print(f"⚠️ Directory {static_dir} mancante")
    
    print("\n" + "=" * 50)
    print("🎉 Test di integrazione completato con successo!")
    print(f"📅 Eseguito il: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

def test_javascript_functions():
    """Test delle funzioni JavaScript essenziali"""
    print("\n🔧 Test Funzioni JavaScript...")
    
    template_path = "app/templates/ml/advanced_column_view.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Lista delle funzioni JavaScript essenziali
        required_functions = [
            "selectAll()",
            "selectAllUnlabeled()",
            "clearAllSelection()",
            "batchLabelCells(",
            "saveCellLabel(",
            "removeCellLabelFromBackend(",
            "getAISuggestions()",
            "applyCellLabel(",
            "updateProgress()",
            "displayAllCells()",
            "escapeHtml("
        ]
        
        for func in required_functions:
            if func in content:
                print(f"✅ Funzione JavaScript {func} presente")
            else:
                print(f"❌ Funzione JavaScript {func} mancante")
                return False
        
        # Test event listeners
        required_events = [
            "label-all-selected",
            "select-all",
            "select-all-unlabeled", 
            "clear-selection",
            "save-manual-label",
            "get-ai-suggestions",
            "remove-label"
        ]
        
        for event in required_events:
            if f"getElementById('{event}').addEventListener" in content:
                print(f"✅ Event listener {event} presente")
            else:
                print(f"❌ Event listener {event} mancante")
                return False
                
        return True
        
    except FileNotFoundError:
        print(f"❌ Template non trovato: {template_path}")
        return False

if __name__ == "__main__":
    success = test_labeling_integration()
    js_success = test_javascript_functions()
    
    if success and js_success:
        print("\n🏆 TUTTI I TEST SUPERATI!")
        sys.exit(0)
    else:
        print("\n💥 ALCUNI TEST FALLITI!")
        sys.exit(1)
