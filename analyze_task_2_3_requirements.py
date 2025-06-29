#!/usr/bin/env python3
"""
Analisi requisiti Task 2.3 - Frontend Components per Sistema Etichettatura Unificato
Analizza lo stato attuale delle view e identifica dove integrare i nuovi componenti.
"""

import os
import re
from pathlib import Path

def analyze_advanced_view_structure(view_path):
    """Analizza la struttura di una view advanced per identificare punti di integrazione"""
    try:
        with open(view_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = {
            'total_lines': len(content.split('\n')),
            'has_data_section': bool(re.search(r'data-container|table-container|cells-container', content)),
            'has_sidebar_space': bool(re.search(r'col s8|col s9|col s10', content)),
            'has_modals': bool(re.search(r'modal', content, re.IGNORECASE)),
            'javascript_blocks': len(re.findall(r'<script.*?</script>', content, re.DOTALL)),
            'form_elements': len(re.findall(r'<form|<input|<select|<textarea', content, re.IGNORECASE)),
            'materialize_components': {
                'cards': len(re.findall(r'class="card', content)),
                'buttons': len(re.findall(r'class=".*btn', content)),
                'dropdowns': len(re.findall(r'dropdown', content, re.IGNORECASE)),
                'tabs': len(re.findall(r'tabs', content, re.IGNORECASE))
            }
        }
        
        # Identifica sezioni principali
        sections = {
            'breadcrumb': bool(re.search(r'breadcrumb', content)),
            'header_info': bool(re.search(r'card-title.*info|header.*info', content, re.IGNORECASE)),
            'data_display': bool(re.search(r'table|grid|list', content, re.IGNORECASE)),
            'actions': bool(re.search(r'card-action|action-buttons', content, re.IGNORECASE))
        }
        
        analysis['sections'] = sections
        return analysis
        
    except Exception as e:
        return {'error': str(e)}

def identify_integration_points(view_path):
    """Identifica i punti migliori per integrare i componenti di etichettatura"""
    try:
        with open(view_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        integration_points = []
        
        for i, line in enumerate(lines):
            # Cerca spazi dove era il pannello rimosso
            if 'col s8' in line or 'col s9' in line:
                integration_points.append({
                    'line': i + 1,
                    'type': 'sidebar_space',
                    'context': line.strip(),
                    'suggestion': 'Aggiungere pannello etichettatura qui (col s3 o s4)'
                })
            
            # Cerca punti dopo sezioni dati
            if 'card-content' in line and i < len(lines) - 1:
                if 'table' in lines[i+1] or 'grid' in lines[i+1]:
                    integration_points.append({
                        'line': i + 2,
                        'type': 'after_data',
                        'context': line.strip(),
                        'suggestion': 'Possibile punto per componenti etichettatura'
                    })
        
        return integration_points
        
    except Exception as e:
        return []

def analyze_api_endpoints_availability():
    """Verifica che gli endpoint API necessari siano disponibili"""
    api_file = "/home/nugh75/Git/anatema2/app/views/api.py"
    
    if not os.path.exists(api_file):
        return {'available': False, 'error': 'File API non trovato'}
    
    try:
        with open(api_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Cerca endpoint del Task 2.2
        required_endpoints = [
            'get_project_labels',
            'create_project_label', 
            'apply_manual_label',
            'request_ai_label',
            'authorize_label_application',
            'get_label_suggestions'
        ]
        
        available_endpoints = []
        for endpoint in required_endpoints:
            if endpoint in content:
                available_endpoints.append(endpoint)
        
        return {
            'available': True,
            'total_required': len(required_endpoints),
            'available_count': len(available_endpoints),
            'available_endpoints': available_endpoints,
            'missing_endpoints': [e for e in required_endpoints if e not in available_endpoints]
        }
        
    except Exception as e:
        return {'available': False, 'error': str(e)}

def main():
    print("=== ANALISI TASK 2.3 - FRONTEND COMPONENTS ===\n")
    
    base_dir = "/home/nugh75/Git/anatema2"
    
    # Analizza le view advanced esistenti
    views_to_analyze = [
        'app/templates/ml/advanced_column_view.html',
        'app/templates/ml/advanced_row_view.html'
    ]
    
    print("🔍 ANALISI VIEW ESISTENTI:\n")
    
    for view_path in views_to_analyze:
        full_path = os.path.join(base_dir, view_path)
        if os.path.exists(full_path):
            print(f"📄 {view_path}:")
            
            # Analizza struttura
            structure = analyze_advanced_view_structure(full_path)
            print(f"   📊 Righe totali: {structure.get('total_lines', 'N/A')}")
            print(f"   🏗️  Sezione dati: {'✅' if structure.get('has_data_section') else '❌'}")
            print(f"   📱 Spazio sidebar: {'✅' if structure.get('has_sidebar_space') else '❌'}")
            print(f"   🪟 Modal esistenti: {structure.get('javascript_blocks', 0)}")
            
            # Componenti Materialize
            mat_components = structure.get('materialize_components', {})
            print(f"   🎨 Card: {mat_components.get('cards', 0)}, Bottoni: {mat_components.get('buttons', 0)}")
            
            # Punti di integrazione
            integration_points = identify_integration_points(full_path)
            print(f"   🔗 Punti integrazione trovati: {len(integration_points)}")
            
            for point in integration_points[:3]:  # Mostra solo i primi 3
                print(f"      - Linea {point['line']}: {point['type']} - {point['suggestion']}")
            
            print()
        else:
            print(f"❌ {view_path}: File non trovato\n")
    
    # Verifica disponibilità API
    print("🔌 VERIFICA API BACKEND (Task 2.2):\n")
    api_status = analyze_api_endpoints_availability()
    
    if api_status.get('available'):
        print(f"   ✅ File API trovato")
        print(f"   📊 Endpoint richiesti: {api_status['total_required']}")
        print(f"   ✅ Endpoint disponibili: {api_status['available_count']}")
        
        if api_status['available_endpoints']:
            print("   📋 Endpoint disponibili:")
            for endpoint in api_status['available_endpoints']:
                print(f"      - {endpoint}")
        
        if api_status['missing_endpoints']:
            print("   ❌ Endpoint mancanti:")
            for endpoint in api_status['missing_endpoints']:
                print(f"      - {endpoint}")
    else:
        print(f"   ❌ Errore API: {api_status.get('error')}")
    
    print()
    
    # Raccomandazioni implementazione
    print("💡 RACCOMANDAZIONI IMPLEMENTAZIONE:\n")
    
    print("🎯 COMPONENTI DA CREARE:")
    components = [
        {
            'name': 'LabelingPanel',
            'description': 'Pannello principale etichettatura',
            'location': 'Colonna destra nelle view (col s3)',
            'features': ['Selezione celle attive', 'Dropdown etichette progetto', 'Bottoni azione']
        },
        {
            'name': 'LabelSelector',
            'description': 'Dropdown/autocomplete etichette',
            'location': 'Interno al LabelingPanel',
            'features': ['Autocomplete', 'Filtraggio', 'Preview descrizione']
        },
        {
            'name': 'LabelCreator',
            'description': 'Modal creazione nuova etichetta',
            'location': 'Modal overlay',
            'features': ['Form validato', 'Color picker', 'Anteprima']
        },
        {
            'name': 'AILabelingSuggestions',
            'description': 'Interfaccia suggerimenti AI',
            'location': 'Modal overlay',
            'features': ['Lista suggerimenti', 'Confidence score', 'Azioni approvazione']
        },
        {
            'name': 'AuthorizationQueue',
            'description': 'Gestione autorizzazioni pendenti',
            'location': 'Header notifica + modal',
            'features': ['Badge count', 'Lista richieste', 'Azioni batch']
        }
    ]
    
    for comp in components:
        print(f"   🔧 {comp['name']}:")
        print(f"      📍 Posizione: {comp['location']}")
        print(f"      ⚡ Funzionalità: {', '.join(comp['features'])}")
        print()
    
    print("🏗️  PIANO IMPLEMENTAZIONE:")
    steps = [
        "1. Creare file JavaScript separato per gestione etichettatura",
        "2. Implementare LabelingPanel come template parziale",
        "3. Integrare pannello nelle view advanced (spazio sidebar)",
        "4. Implementare modals per creazione etichette e autorizzazioni",
        "5. Connettere con API backend (Task 2.2)",
        "6. Testare workflow completo umano + AI",
        "7. Aggiungere sistema notifiche autorizzazioni"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print()
    
    print("⚠️  CONSIDERAZIONI TECNICHE:")
    considerations = [
        "Utilizzare Materialize CSS per coerenza UI",
        "JavaScript vanilla o jQuery (esistente nel progetto)",
        "Gestire stati di loading per chiamate AJAX", 
        "Implementare validazione client-side per form",
        "Considerare responsività mobile",
        "Mantenere accessibilità (ARIA labels)"
    ]
    
    for consideration in considerations:
        print(f"   • {consideration}")
    
    print()
    print("✅ Analisi completata! Pronto per implementazione Task 2.3")

if __name__ == "__main__":
    main()
