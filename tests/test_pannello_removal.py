#!/usr/bin/env python3
"""
Test per verificare la rimozione del "Pannello Etichettatura" dalle view colonne/righe
Task 1.3 del Piano di Ristrutturazione
"""
import os
import sys

def test_pannello_etichettatura_removal():
    """
    Verifica che il "Pannello Etichettatura" sia stato rimosso dai template
    """
    print("🧪 Test: Rimozione Pannello Etichettatura dalle view colonne/righe")
    print("=" * 70)
    
    success = True
    
    # File da controllare
    templates_to_check = [
        {
            'file': '/home/nugh75/Git/anatema2/app/templates/ml/advanced_column_view.html',
            'name': 'View Colonne'
        },
        {
            'file': '/home/nugh75/Git/anatema2/app/templates/ml/advanced_row_view.html', 
            'name': 'View Righe'
        }
    ]
    
    # Elementi che NON dovrebbero essere presenti
    forbidden_elements = [
        'Pannello Etichettatura',
        'Etichette del Progetto',
        'Etichettatura Manuale',
        'Suggerimenti AI',
        'Controllo Qualità',
        'project-label-chip',
        'manual-label',
        'manual-description',
        'get-ai-suggestions',
        'auto-validation',
        'confidence-score'
    ]
    
    for template in templates_to_check:
        print(f"\n📄 Controllo {template['name']}: {template['file']}")
        
        if not os.path.exists(template['file']):
            print(f"   ❌ ERRORE: File non trovato!")
            success = False
            continue
            
        with open(template['file'], 'r', encoding='utf-8') as f:
            content = f.read()
            
        found_forbidden = []
        for element in forbidden_elements:
            if element in content:
                found_forbidden.append(element)
                
        if found_forbidden:
            print(f"   ❌ ERRORE: Trovati elementi che dovevano essere rimossi:")
            for element in found_forbidden:
                print(f"      - {element}")
            success = False
        else:
            print(f"   ✅ OK: Nessun elemento del pannello trovato")
            
        # Verifica specifica per elementi della view righe
        if 'row_view' in template['file']:
            row_specific = [
                'Azioni Rapide',
                'label-all-positive',
                'label-all-negative', 
                'Statistiche Riga',
                'row-total-cells'
            ]
            
            found_row_specific = []
            for element in row_specific:
                if element in content:
                    found_row_specific.append(element)
                    
            if found_row_specific:
                print(f"   ❌ ERRORE: Trovati elementi specifici della view righe:")
                for element in found_row_specific:
                    print(f"      - {element}")
                success = False
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 SUCCESSO: Pannello Etichettatura rimosso correttamente da entrambe le view!")
        print("📋 Task 1.3 del Piano di Ristrutturazione: COMPLETATO")
    else:
        print("❌ FALLIMENTO: Alcuni elementi del pannello sono ancora presenti!")
        print("🔧 Verifica i file e rimuovi gli elementi rimanenti.")
        
    return success

def test_template_validity():
    """
    Verifica che i template siano ancora validi HTML dopo le modifiche
    """
    print("\n🔍 Test: Validità dei template dopo le modifiche")
    print("=" * 70)
    
    templates = [
        '/home/nugh75/Git/anatema2/app/templates/ml/advanced_column_view.html',
        '/home/nugh75/Git/anatema2/app/templates/ml/advanced_row_view.html'
    ]
    
    success = True
    
    for template in templates:
        print(f"\n📄 Validazione: {os.path.basename(template)}")
        
        with open(template, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check basic HTML structure
        checks = [
            ('{% extends "base.html" %}', 'Template extends base'),
            ('{% block content %}', 'Content block opens'),
            ('{% endblock %}', 'Content block closes'),
            ('<div class="container-fluid">', 'Main container'),
            ('<!-- Modal', 'Modal sections present')
        ]
        
        for check, description in checks:
            if check in content:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ MANCANTE: {description}")
                success = False
                
    return success

if __name__ == "__main__":
    print("🧪 Test Rimozione Pannello Etichettatura")
    print("Task 1.3 del Piano di Ristrutturazione Etichettatura\n")
    
    # Esegui i test
    test1_success = test_pannello_etichettatura_removal()
    test2_success = test_template_validity()
    
    print("\n" + "=" * 70)
    print("📊 RISULTATI FINALI:")
    print(f"   Test Rimozione Pannello: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"   Test Validità Template: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 TUTTI I TEST PASSATI!")
        print("   Task 1.3 completato con successo.")
        sys.exit(0)
    else:
        print("\n❌ ALCUNI TEST FALLITI!")
        print("   Controlla gli errori sopra.")
        sys.exit(1)
