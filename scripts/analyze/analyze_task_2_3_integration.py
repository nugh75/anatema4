#!/usr/bin/env python3
"""
Analisi Task 2.3 - Validazione Integrazione Frontend Components
Verifica l'integrazione del sistema di etichettatura unificato nei template ML
Analizza la coerenza e completezza dell'implementazione
"""

import os
import re
from pathlib import Path

def analyze_file_content(file_path):
    """Analizza il contenuto di un file template"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"ERRORE lettura file: {e}"

def check_unified_labeling_integration():
    """Verifica l'integrazione del sistema di etichettatura unificato"""
    print("="*80)
    print("ANALISI INTEGRAZIONE SISTEMA ETICHETTATURA UNIFICATO - TASK 2.3")
    print("="*80)
    
    base_path = Path("/home/nugh75/Git/anatema2")
    
    # Template da verificare
    templates_to_check = [
        "app/templates/ml/advanced_column_view.html",
        "app/templates/ml/advanced_row_view.html"
    ]
    
    # File componenti
    components_to_check = [
        "app/templates/components/labeling_panel.html",
        "app/static/js/unified_labeling.js"
    ]
    
    print("\n1. VERIFICA ESISTENZA COMPONENTI UNIFICATI")
    print("-" * 50)
    
    for component in components_to_check:
        file_path = base_path / component
        if file_path.exists():
            print(f"✓ {component} - PRESENTE")
            if component.endswith('.js'):
                content = analyze_file_content(file_path)
                if 'UnifiedLabelingSystem' in content:
                    print(f"  ✓ Contiene classe UnifiedLabelingSystem")
                else:
                    print(f"  ⚠ Classe UnifiedLabelingSystem non trovata")
        else:
            print(f"✗ {component} - MANCANTE")
    
    print("\n2. VERIFICA INTEGRAZIONE NEI TEMPLATE ML")
    print("-" * 50)
    
    for template in templates_to_check:
        file_path = base_path / template
        template_name = os.path.basename(template)
        
        print(f"\n--- {template_name} ---")
        
        if not file_path.exists():
            print(f"✗ File non trovato")
            continue
            
        content = analyze_file_content(file_path)
        
        # Verifica include del pannello
        if "{% include 'components/labeling_panel.html' %}" in content:
            print("✓ Include pannello etichettatura unificato")
        else:
            print("✗ NON include pannello etichettatura unificato")
        
        # Verifica include script unificato
        if "unified_labeling.js" in content:
            print("✓ Include script etichettatura unificato")
        else:
            print("✗ NON include script etichettatura unificato")
        
        # Verifica istanziazione UnifiedLabelingSystem
        if "new UnifiedLabelingSystem" in content:
            print("✓ Istanzia UnifiedLabelingSystem")
        else:
            print("✗ NON istanzia UnifiedLabelingSystem")
        
        # Verifica rimozione vecchio sistema
        old_patterns = [
            "selected-column",
            "selected-value", 
            "manual-cell-label",
            "save-cell-label"
        ]
        
        old_found = []
        for pattern in old_patterns:
            if pattern in content:
                old_found.append(pattern)
        
        if old_found:
            print(f"⚠ Trovati elementi del vecchio sistema: {', '.join(old_found)}")
        else:
            print("✓ Vecchio sistema di etichettatura rimosso")
        
        # Verifica struttura celle compatibile
        if 'data-column=' in content and 'data-row=' in content:
            print("✓ Struttura celle compatibile con sistema unificato")
        else:
            print("⚠ Struttura celle potrebbe non essere compatibile")
    
    print("\n3. VERIFICA COERENZA API ENDPOINT")
    print("-" * 50)
    
    api_file = base_path / "app/views/api.py"
    if api_file.exists():
        api_content = analyze_file_content(api_file)
        
        # Endpoint del sistema unificato
        unified_endpoints = [
            "/api/v1/labels/store",
            "/api/v1/labels/apply", 
            "/api/v1/labels/suggestions",
            "/api/v1/labels/authorization"
        ]
        
        for endpoint in unified_endpoints:
            endpoint_name = endpoint.split('/')[-1]
            if f"'{endpoint_name}'" in api_content or f'"{endpoint_name}"' in api_content:
                print(f"✓ Endpoint {endpoint} disponibile")
            else:
                print(f"⚠ Endpoint {endpoint} potrebbe non essere disponibile")
    else:
        print("✗ File API non trovato")
    
    print("\n4. VERIFICA MODELLI DATABASE")
    print("-" * 50)
    
    models_file = base_path / "app/models_labeling.py"
    if models_file.exists():
        models_content = analyze_file_content(models_file)
        
        # Modelli richiesti per sistema unificato
        required_models = [
            "class Label",
            "class LabelApplication", 
            "class LabelSuggestion",
            "authorization_status",
            "suggestion_status"
        ]
        
        for model in required_models:
            if model in models_content:
                print(f"✓ {model} presente")
            else:
                print(f"⚠ {model} potrebbe non essere presente")
    else:
        print("✗ File modelli labeling non trovato")
    
    print("\n5. ANALISI COMPLETEZZA INTEGRAZIONE")
    print("-" * 50)
    
    # Verifica che entrambi i template abbiano la stessa struttura base
    column_view_path = base_path / "app/templates/ml/advanced_column_view.html"
    row_view_path = base_path / "app/templates/ml/advanced_row_view.html"
    
    if column_view_path.exists() and row_view_path.exists():
        column_content = analyze_file_content(column_view_path)
        row_content = analyze_file_content(row_view_path)
        
        # Elementi che dovrebbero essere presenti in entrambi
        common_elements = [
            "UnifiedLabelingSystem",
            "labeling_panel.html",
            "unified_labeling.js",
            "cell-item",
            "data-column"
        ]
        
        inconsistencies = []
        for element in common_elements:
            in_column = element in column_content
            in_row = element in row_content
            
            if in_column and in_row:
                print(f"✓ {element} presente in entrambi i template")
            elif in_column and not in_row:
                print(f"⚠ {element} presente solo in column_view")
                inconsistencies.append(f"{element} mancante in row_view")
            elif not in_column and in_row:
                print(f"⚠ {element} presente solo in row_view")
                inconsistencies.append(f"{element} mancante in column_view")
            else:
                print(f"✗ {element} mancante in entrambi")
                inconsistencies.append(f"{element} mancante in entrambi")
        
        if inconsistencies:
            print(f"\n⚠ INCONSISTENZE TROVATE:")
            for issue in inconsistencies:
                print(f"   - {issue}")
        else:
            print(f"\n✓ Template coerenti tra loro")
    
    print("\n6. VERIFICA DOCUMENTI AGGIORNATI")
    print("-" * 50)
    
    docs_path = base_path / "docs"
    master_doc = docs_path / "MASTER_REFACTORING.md"
    
    if master_doc.exists():
        master_content = analyze_file_content(master_doc)
        if "Task 2.3" in master_content and "Frontend Components" in master_content:
            print("✓ Documentazione master aggiornata con Task 2.3")
        else:
            print("⚠ Documentazione master potrebbe non essere aggiornata")
    else:
        print("✗ Documentazione master non trovata")
    
    print("\n" + "="*80)
    print("RIEPILOGO ANALISI COMPLETATA")
    print("="*80)
    print("Verifica manuale raccomanda ta:")
    print("1. Test funzionale dei template aggiornati")
    print("2. Verifica API endpoints in ambiente di sviluppo") 
    print("3. Test integrazione JavaScript con backend")
    print("4. Validazione flusso utente completo")

if __name__ == "__main__":
    check_unified_labeling_integration()
