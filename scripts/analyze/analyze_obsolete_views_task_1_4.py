#!/usr/bin/env python3
"""
Analisi View Obsolete - Task 1.4
Identifica template, route e codice non più utilizzati nel sistema ML

Analizza:
1. Template ML non più referenziati
2. Route duplicate o obsolete  
3. Codice JavaScript non utilizzato
4. Funzioni Python non chiamate
"""

import os
import re
from pathlib import Path

def analyze_ml_obsolete_views():
    """
    Analizza le view ML per identificare elementi obsoleti
    """
    print("🔍 ANALISI VIEW OBSOLETE - TASK 1.4")
    print("=" * 50)
    
    # Path del progetto
    base_path = "/home/nugh75/Git/anatema2"
    ml_templates_path = f"{base_path}/app/templates/ml"
    ml_views_path = f"{base_path}/app/views/ml.py"
    
    # 1. Analisi template utilizzati vs esistenti
    print("\n📋 1. ANALISI TEMPLATE ML")
    print("-" * 30)
    
    # Lista tutti i template ML
    template_files = []
    if os.path.exists(ml_templates_path):
        template_files = [f for f in os.listdir(ml_templates_path) if f.endswith('.html')]
    
    print(f"Template trovati: {len(template_files)}")
    for template in sorted(template_files):
        print(f"  📄 {template}")
    
    # Analizza i template referenziati nel codice
    referenced_templates = set()
    
    # Legge ml.py per trovare render_template calls
    if os.path.exists(ml_views_path):
        with open(ml_views_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Trova tutti i render_template
        template_pattern = r"render_template\(['\"]ml/([^'\"]+)['\"]"
        matches = re.findall(template_pattern, content)
        referenced_templates.update(matches)
    
    print(f"\nTemplate referenziati nel codice: {len(referenced_templates)}")
    for template in sorted(referenced_templates):
        print(f"  ✅ {template}")
    
    # Identifica template non utilizzati
    unreferenced_templates = set(template_files) - referenced_templates
    print(f"\n❌ Template NON UTILIZZATI: {len(unreferenced_templates)}")
    for template in sorted(unreferenced_templates):
        print(f"  🗑️ {template}")
    
    # 2. Analisi route duplicate o simili
    print("\n📋 2. ANALISI ROUTE ML")
    print("-" * 30)
    
    route_pattern = r"@ml_bp\.route\(['\"]([^'\"]+)['\"]"
    routes = re.findall(route_pattern, content)
    
    print(f"Route totali: {len(routes)}")
    
    # Cerca pattern simili che potrebbero essere duplicati
    similar_routes = {}
    for route in routes:
        # Normalizza il route rimuovendo gli UUID
        normalized = re.sub(r'<uuid:[^>]+>', '<uuid>', route)
        normalized = re.sub(r'<[^>]+>', '<param>', normalized)
        
        if normalized not in similar_routes:
            similar_routes[normalized] = []
        similar_routes[normalized].append(route)
    
    # Identifica potenziali duplicati
    potential_duplicates = {k: v for k, v in similar_routes.items() if len(v) > 1}
    
    if potential_duplicates:
        print("\n⚠️ POSSIBILI ROUTE DUPLICATE:")
        for pattern, routes_list in potential_duplicates.items():
            print(f"  📝 Pattern: {pattern}")
            for route in routes_list:
                print(f"    - {route}")
    else:
        print("✅ Nessuna route duplicata trovata")
    
    # 3. Analisi funzioni inutilizzate
    print("\n📋 3. ANALISI FUNZIONI ML")
    print("-" * 30)
    
    # Trova tutte le funzioni definite
    function_pattern = r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
    functions = re.findall(function_pattern, content)
    
    # Trova le funzioni chiamate
    called_functions = set()
    call_pattern = r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
    calls = re.findall(call_pattern, content)
    called_functions.update(calls)
    
    # Route handler sono sempre "utilizzate"
    route_handlers = set()
    for line in content.split('\n'):
        if line.strip().startswith('def ') and '@ml_bp.route' in content[:content.find(line)]:
            func_name = re.search(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)", line)
            if func_name:
                route_handlers.add(func_name.group(1))
    
    print(f"Funzioni definite: {len(functions)}")
    print(f"Route handlers: {len(route_handlers)}")
    
    # Funzioni helper potenzialmente non utilizzate
    helper_functions = set(functions) - route_handlers
    potentially_unused = helper_functions - called_functions
    
    if potentially_unused:
        print(f"\n⚠️ FUNZIONI HELPER POTENZIALMENTE NON UTILIZZATE: {len(potentially_unused)}")
        for func in sorted(potentially_unused):
            print(f"  🔍 {func}")
    else:
        print("✅ Tutte le funzioni helper sembrano utilizzate")
    
    # 4. Analisi view principali vs obsolete
    print("\n📋 4. CLASSIFICAZIONE VIEW")
    print("-" * 30)
    
    # View principali che sappiamo essere utilizzate
    main_views = {
        'new_dashboard.html': 'Dashboard principale (Task 1.2)',
        'advanced_column_view.html': 'View colonne avanzata (attiva)',
        'advanced_row_view.html': 'View righe avanzata (attiva)',
        'configure.html': 'Configurazione progetto ML',
        'analysis_results.html': 'Risultati analisi AI'
    }
    
    # View che potrebbero essere obsolete
    potentially_obsolete = {
        'dashboard.html': 'Dashboard vecchio (sostituito da new_dashboard.html)',
        'view_columns.html': 'View colonne semplice (forse sostituita da advanced)',
        'view_rows.html': 'View righe semplice (forse sostituita da advanced)',
        'select_column.html': 'Selezione colonna (UI obsoleta?)',
        'select_row.html': 'Selezione riga (UI obsoleta?)',
        'single_column_view.html': 'View singola colonna (duplicato?)',
        'single_row_view.html': 'View singola riga (duplicato?)'
    }
    
    print("✅ VIEW PRINCIPALI (DA MANTENERE):")
    for view, description in main_views.items():
        status = "✅ UTILIZZATA" if view in referenced_templates else "❓ NON REFERENZIATA"
        print(f"  📄 {view:25} - {description} [{status}]")
    
    print("\n⚠️ VIEW POTENZIALMENTE OBSOLETE:")
    for view, description in potentially_obsolete.items():
        status = "⚠️ ANCORA UTILIZZATA" if view in referenced_templates else "🗑️ NON UTILIZZATA"
        print(f"  📄 {view:25} - {description} [{status}]")
    
    # 5. Raccomandazioni finali
    print("\n📊 RACCOMANDAZIONI TASK 1.4")
    print("=" * 50)
    
    recommendations = []
    
    if unreferenced_templates:
        recommendations.append(f"🗑️ Rimuovere {len(unreferenced_templates)} template non utilizzati")
    
    # Verifica template obsoleti ancora utilizzati
    obsolete_still_used = set(potentially_obsolete.keys()) & referenced_templates
    if obsolete_still_used:
        recommendations.append(f"🔄 Analizzare {len(obsolete_still_used)} view obsolete ancora utilizzate")
    
    if potentially_unused:
        recommendations.append(f"🔍 Verificare {len(potentially_unused)} funzioni helper non utilizzate")
    
    if potential_duplicates:
        recommendations.append(f"⚡ Unificare {len(potential_duplicates)} pattern di route simili")
    
    if recommendations:
        print("AZIONI CONSIGLIATE:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    else:
        print("✅ NESSUNA PULIZIA NECESSARIA - Codice già ottimizzato")
    
    return {
        'unreferenced_templates': unreferenced_templates,
        'obsolete_still_used': obsolete_still_used,
        'potentially_unused_functions': potentially_unused,
        'potential_duplicate_routes': potential_duplicates,
        'recommendations': recommendations
    }

if __name__ == "__main__":
    try:
        results = analyze_ml_obsolete_views()
        
        if results['recommendations']:
            print(f"\n🎯 TASK 1.4: PULIZIA NECESSARIA")
            print(f"📊 Elementi da rivedere: {sum([
                len(results['unreferenced_templates']),
                len(results['obsolete_still_used']), 
                len(results['potentially_unused_functions']),
                len(results['potential_duplicate_routes'])
            ])}")
        else:
            print(f"\n✅ TASK 1.4: NESSUNA PULIZIA NECESSARIA")
            
    except Exception as e:
        print(f"❌ ERRORE durante analisi: {e}")
