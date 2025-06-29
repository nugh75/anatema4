#!/usr/bin/env python3
"""
Test Task 2.3 - Validazione Finale Integrazione Frontend Components
Verifica completa del sistema di etichettatura unificato integrato
"""

import os
import re
from pathlib import Path

def test_unified_labeling_integration():
    """Test completo dell'integrazione del sistema unificato"""
    print("="*80)
    print("TEST FINALE INTEGRAZIONE SISTEMA ETICHETTATURA UNIFICATO - TASK 2.3")
    print("="*80)
    
    base_path = Path("/home/nugh75/Git/anatema2")
    results = {"passed": 0, "failed": 0, "warnings": 0}
    
    def log_result(test_name, status, message):
        if status == "PASS":
            print(f"✓ {test_name}: {message}")
            results["passed"] += 1
        elif status == "FAIL":
            print(f"✗ {test_name}: {message}")
            results["failed"] += 1
        else:  # WARNING
            print(f"⚠ {test_name}: {message}")
            results["warnings"] += 1
    
    print("\n1. TEST COMPONENTI CORE")
    print("-" * 50)
    
    # Test 1.1: Pannello etichettatura esiste e ha contenuto corretto
    panel_path = base_path / "app/templates/components/labeling_panel.html"
    if panel_path.exists():
        with open(panel_path, 'r', encoding='utf-8') as f:
            panel_content = f.read()
        
        required_elements = [
            "labeling-panel-container",
            "selection-info", 
            "project-labels-section",
            "label-selector",
            "apply-manual-label",
            "ai-suggestions"
        ]
        
        missing_elements = [elem for elem in required_elements if elem not in panel_content]
        
        if not missing_elements:
            log_result("1.1 Pannello Etichettatura", "PASS", "Tutti gli elementi richiesti presenti")
        else:
            log_result("1.1 Pannello Etichettatura", "FAIL", f"Elementi mancanti: {missing_elements}")
    else:
        log_result("1.1 Pannello Etichettatura", "FAIL", "File non trovato")
    
    # Test 1.2: Script unificato esiste e ha classe principale
    script_path = base_path / "app/static/js/unified_labeling.js"
    if script_path.exists():
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        if "class UnifiedLabelingSystem" in script_content:
            log_result("1.2 Script Unificato", "PASS", "Classe UnifiedLabelingSystem presente")
        else:
            log_result("1.2 Script Unificato", "FAIL", "Classe UnifiedLabelingSystem mancante")
    else:
        log_result("1.2 Script Unificato", "FAIL", "File non trovato")
    
    print("\n2. TEST INTEGRAZIONE TEMPLATE")
    print("-" * 50)
    
    templates = [
        ("advanced_column_view.html", "column_view"),
        ("advanced_row_view.html", "row_view")
    ]
    
    for template_name, view_type in templates:
        template_path = base_path / f"app/templates/ml/{template_name}"
        
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Test 2.1: Include del pannello
            if "{% include 'components/labeling_panel.html' %}" in content:
                log_result(f"2.1 {view_type} Include", "PASS", "Pannello incluso correttamente")
            else:
                log_result(f"2.1 {view_type} Include", "FAIL", "Pannello non incluso")
            
            # Test 2.2: Include script unificato
            if "unified_labeling.js" in content:
                log_result(f"2.2 {view_type} Script", "PASS", "Script unificato incluso")
            else:
                log_result(f"2.2 {view_type} Script", "FAIL", "Script unificato non incluso")
            
            # Test 2.3: Istanziazione classe
            if "new UnifiedLabelingSystem" in content:
                log_result(f"2.3 {view_type} Istanza", "PASS", "UnifiedLabelingSystem istanziato")
            else:
                log_result(f"2.3 {view_type} Istanza", "FAIL", "UnifiedLabelingSystem non istanziato")
            
            # Test 2.4: Struttura celle compatibile
            has_data_column = 'data-column=' in content or 'dataset.column' in content
            has_data_value = 'data-value=' in content or 'dataset.value' in content
            has_cell_item = 'cell-item' in content
            
            if has_data_column and has_data_value and has_cell_item:
                log_result(f"2.4 {view_type} Struttura", "PASS", "Struttura celle compatibile")
            else:
                missing = []
                if not has_data_column: missing.append("data-column")
                if not has_data_value: missing.append("data-value")
                if not has_cell_item: missing.append("cell-item")
                log_result(f"2.4 {view_type} Struttura", "FAIL", f"Elementi mancanti: {missing}")
            
            # Test 2.5: Rimozione vecchio sistema
            old_patterns = ["manual-cell-label", "save-cell-label", "current-cell-info"]
            old_found = [p for p in old_patterns if p in content]
            
            if not old_found:
                log_result(f"2.5 {view_type} Cleanup", "PASS", "Vecchio sistema rimosso")
            else:
                log_result(f"2.5 {view_type} Cleanup", "WARNING", f"Residui vecchio sistema: {old_found}")
        else:
            log_result(f"2.X {view_type}", "FAIL", "Template non trovato")
    
    print("\n3. TEST COERENZA TRA TEMPLATE")
    print("-" * 50)
    
    column_path = base_path / "app/templates/ml/advanced_column_view.html"
    row_path = base_path / "app/templates/ml/advanced_row_view.html"
    
    if column_path.exists() and row_path.exists():
        with open(column_path, 'r', encoding='utf-8') as f:
            column_content = f.read()
        with open(row_path, 'r', encoding='utf-8') as f:
            row_content = f.read()
        
        # Test 3.1: Stesso pannello incluso
        column_has_panel = "labeling_panel.html" in column_content
        row_has_panel = "labeling_panel.html" in row_content
        
        if column_has_panel and row_has_panel:
            log_result("3.1 Coerenza Pannello", "PASS", "Stesso pannello in entrambi i template")
        else:
            log_result("3.1 Coerenza Pannello", "FAIL", "Pannello non coerente tra template")
        
        # Test 3.2: Stesso script incluso
        column_has_script = "unified_labeling.js" in column_content
        row_has_script = "unified_labeling.js" in row_content
        
        if column_has_script and row_has_script:
            log_result("3.2 Coerenza Script", "PASS", "Stesso script in entrambi i template")
        else:
            log_result("3.2 Coerenza Script", "FAIL", "Script non coerente tra template")
        
        # Test 3.3: Stesse classi CSS
        common_classes = ["cell-item", "sticky-top", "section"]
        class_issues = []
        
        for css_class in common_classes:
            in_column = css_class in column_content
            in_row = css_class in row_content
            
            if not (in_column and in_row):
                class_issues.append(f"{css_class} non in entrambi")
        
        if not class_issues:
            log_result("3.3 Coerenza CSS", "PASS", "Classi CSS coerenti")
        else:
            log_result("3.3 Coerenza CSS", "WARNING", f"Problemi: {class_issues}")
    
    print("\n4. TEST API BACKEND CONNECTIVITY")
    print("-" * 50)
    
    api_path = base_path / "app/views/api.py"
    if api_path.exists():
        with open(api_path, 'r', encoding='utf-8') as f:
            api_content = f.read()
        
        # Test 4.1: Endpoint etichette store
        store_endpoints = ["get_project_labels", "create_project_label", "update_project_label"]
        store_found = [ep for ep in store_endpoints if ep in api_content]
        
        if len(store_found) >= 2:  # Almeno 2 dei 3 endpoint
            log_result("4.1 API Store", "PASS", f"Endpoint store presenti: {store_found}")
        else:
            log_result("4.1 API Store", "FAIL", f"Endpoint store insufficienti: {store_found}")
        
        # Test 4.2: Endpoint applicazione etichette
        apply_endpoints = ["apply_manual_labels", "request_ai_labeling", "authorize_ai_application"]
        apply_found = [ep for ep in apply_endpoints if ep in api_content]
        
        if len(apply_found) >= 2:
            log_result("4.2 API Apply", "PASS", f"Endpoint applicazione presenti: {apply_found}")
        else:
            log_result("4.2 API Apply", "FAIL", f"Endpoint applicazione insufficienti: {apply_found}")
        
        # Test 4.3: Endpoint autorizzazioni
        auth_endpoints = ["authorization", "approve", "reject"]
        auth_found = [ep for ep in auth_endpoints if any(ep in line for line in api_content.split('\n'))]
        
        if auth_found:
            log_result("4.3 API Auth", "PASS", f"Endpoint autorizzazione presenti: {auth_found}")
        else:
            log_result("4.3 API Auth", "WARNING", "Endpoint autorizzazione non chiari")
    else:
        log_result("4.X API", "FAIL", "File API non trovato")
    
    print("\n5. TEST MODELLI DATABASE")
    print("-" * 50)
    
    models_path = base_path / "app/models_labeling.py"
    if models_path.exists():
        with open(models_path, 'r', encoding='utf-8') as f:
            models_content = f.read()
        
        # Test 5.1: Modelli richiesti
        required_models = ["Label", "LabelApplication", "LabelSuggestion"]
        models_found = [m for m in required_models if f"class {m}" in models_content]
        
        if len(models_found) == len(required_models):
            log_result("5.1 Modelli Base", "PASS", f"Tutti i modelli presenti: {models_found}")
        else:
            missing = [m for m in required_models if m not in models_found]
            log_result("5.1 Modelli Base", "FAIL", f"Modelli mancanti: {missing}")
        
        # Test 5.2: Campi autorizzazione
        auth_fields = ["authorized_by", "authorized_at", "application_type"]
        auth_found = [f for f in auth_fields if f in models_content]
        
        if len(auth_found) >= 2:
            log_result("5.2 Campi Auth", "PASS", f"Campi autorizzazione: {auth_found}")
        else:
            log_result("5.2 Campi Auth", "WARNING", f"Campi autorizzazione limitati: {auth_found}")
    else:
        log_result("5.X Modelli", "FAIL", "File modelli non trovato")
    
    print("\n6. TEST DOCUMENTAZIONE")
    print("-" * 50)
    
    master_doc = base_path / "docs/MASTER_REFACTORING.md"
    if master_doc.exists():
        with open(master_doc, 'r', encoding='utf-8') as f:
            doc_content = f.read()
        
        # Test 6.1: Task 2.3 documentato
        if "Task 2.3" in doc_content and "Frontend Components" in doc_content:
            log_result("6.1 Doc Task 2.3", "PASS", "Task 2.3 documentato")
        else:
            log_result("6.1 Doc Task 2.3", "FAIL", "Task 2.3 non documentato")
        
        # Test 6.2: Stato aggiornato
        if "🔄 **PROSSIMO**" in doc_content or "✅ **COMPLETATO**" in doc_content:
            log_result("6.2 Doc Stato", "PASS", "Stato progetto aggiornato")
        else:
            log_result("6.2 Doc Stato", "WARNING", "Stato progetto da aggiornare")
    else:
        log_result("6.X Documentazione", "FAIL", "Documentazione master non trovata")
    
    print("\n" + "="*80)
    print("RIEPILOGO TEST INTEGRAZIONE")
    print("="*80)
    
    total_tests = results["passed"] + results["failed"] + results["warnings"]
    pass_rate = (results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"✓ Test Passati: {results['passed']}")
    print(f"⚠ Warning: {results['warnings']}")
    print(f"✗ Test Falliti: {results['failed']}")
    print(f"📊 Tasso di Successo: {pass_rate:.1f}%")
    
    if results["failed"] == 0:
        print("\n🎉 INTEGRAZIONE TASK 2.3 COMPLETATA CON SUCCESSO!")
        print("✅ Il sistema di etichettatura unificato è stato integrato correttamente")
        print("📝 Prossimo step: Aggiornare documentazione e procedere con Task 2.4")
    elif results["failed"] <= 2:
        print("\n⚠️ INTEGRAZIONE QUASI COMPLETA")
        print("🔧 Piccoli aggiustamenti necessari prima di considerare il task completato")
    else:
        print("\n❌ INTEGRAZIONE NON COMPLETA")
        print("🛠️ Sono necessarie correzioni significative")
    
    return results

if __name__ == "__main__":
    test_unified_labeling_integration()
