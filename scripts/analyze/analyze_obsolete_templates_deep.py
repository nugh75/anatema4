#!/usr/bin/env python3
"""
Analisi approfondita dei template potenzialmente obsoleti - Task 1.4
Verifica l'uso effettivo e la sostituibilità dei template identificati come potenzialmente obsoleti.
"""

import os
import re
import json
from pathlib import Path

def search_template_usage(template_name, search_dirs):
    """Cerca l'uso di un template in file Python e HTML"""
    results = []
    
    for search_dir in search_dirs:
        for root, dirs, files in os.walk(search_dir):
            for file in files:
                if file.endswith(('.py', '.html')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Cerca riferimenti al template
                        patterns = [
                            rf'render_template\(["\'].*{template_name}["\']',
                            rf'redirect.*{template_name}',
                            rf'url_for.*{template_name}',
                            rf'{template_name}',
                            rf'template.*{template_name}',
                            rf'include.*{template_name}',
                            rf'extends.*{template_name}'
                        ]
                        
                        for pattern in patterns:
                            matches = re.finditer(pattern, content, re.IGNORECASE)
                            for match in matches:
                                # Ottieni il contesto (3 righe prima e dopo)
                                lines = content.split('\n')
                                match_line = content[:match.start()].count('\n')
                                start_line = max(0, match_line - 3)
                                end_line = min(len(lines), match_line + 4)
                                context = '\n'.join(lines[start_line:end_line])
                                
                                results.append({
                                    'file': file_path,
                                    'line': match_line + 1,
                                    'match': match.group(),
                                    'context': context,
                                    'pattern': pattern
                                })
                                
                    except Exception as e:
                        print(f"Errore leggendo {file_path}: {e}")
    
    return results

def analyze_template_functionality(template_path):
    """Analizza la funzionalità di un template"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Analizza elementi del template
        analysis = {
            'extends_base': 'extends' in content,
            'has_forms': 'form' in content.lower(),
            'has_javascript': 'script' in content.lower(),
            'has_ajax': 'ajax' in content.lower() or 'fetch' in content.lower(),
            'blocks': re.findall(r'{% block (\w+) %}', content),
            'includes': re.findall(r'{% include ["\']([^"\']+)["\']', content),
            'variables': re.findall(r'{{ (\w+)', content),
            'filters': re.findall(r'\|(\w+)', content),
            'line_count': len(content.split('\n')),
            'complexity': 'for' in content or 'if' in content or 'with' in content
        }
        
        return analysis
    except Exception as e:
        return {'error': str(e)}

def check_route_usage(template_name):
    """Verifica se ci sono route che usano il template"""
    views_dir = "/home/nugh75/Git/anatema2/app/views"
    route_usage = []
    
    for file in os.listdir(views_dir):
        if file.endswith('.py'):
            file_path = os.path.join(views_dir, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Cerca route che potrebbero usare il template
                route_patterns = [
                    r'@[a-zA-Z_]+\.route\([^)]+\)\s*def\s+(\w+)[^:]*:.*?return.*?render_template\(["\'][^"\']*' + template_name.replace('.html', '') + r'[^"\']*["\']',
                    r'def\s+(\w+)[^:]*:.*?render_template\(["\'][^"\']*' + template_name.replace('.html', '') + r'[^"\']*["\']'
                ]
                
                for pattern in route_patterns:
                    matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
                    for match in matches:
                        route_usage.append({
                            'file': file_path,
                            'function': match.group(1) if match.groups() else 'unknown',
                            'context': match.group()[:200] + '...' if len(match.group()) > 200 else match.group()
                        })
            except Exception as e:
                print(f"Errore analizzando {file_path}: {e}")
    
    return route_usage

def main():
    print("=== ANALISI APPROFONDITA TEMPLATE OBSOLETI - TASK 1.4 ===\n")
    
    # Template identificati come potenzialmente obsoleti
    potentially_obsolete_templates = [
        'view_columns.html',
        'view_rows.html', 
        'select_column.html',
        'select_row.html',
        'single_column_view.html',
        'single_row_view.html'
    ]
    
    base_dir = "/home/nugh75/Git/anatema2"
    search_dirs = [
        os.path.join(base_dir, "app"),
        os.path.join(base_dir, "config"),
        os.path.join(base_dir, "migrations")
    ]
    
    analysis_results = {}
    
    for template in potentially_obsolete_templates:
        print(f"\n{'='*60}")
        print(f"ANALISI TEMPLATE: {template}")
        print(f"{'='*60}")
        
        template_path = f"/home/nugh75/Git/anatema2/app/templates/ml/{template}"
        
        # 1. Verifica esistenza
        if not os.path.exists(template_path):
            print(f"❌ Template non trovato: {template_path}")
            continue
        
        # 2. Analizza funzionalità del template
        print("\n📋 ANALISI FUNZIONALITÀ:")
        functionality = analyze_template_functionality(template_path)
        for key, value in functionality.items():
            print(f"  {key}: {value}")
        
        # 3. Cerca utilizzi nel codice
        print("\n🔍 UTILIZZI NEL CODICE:")
        usages = search_template_usage(template, search_dirs)
        if usages:
            for usage in usages:
                print(f"  📁 {usage['file']}:{usage['line']}")
                print(f"  🎯 Match: {usage['match']}")
                print(f"  📄 Contesto:")
                for line in usage['context'].split('\n'):
                    print(f"    {line}")
                print()
        else:
            print("  ❌ Nessun utilizzo trovato nel codice")
        
        # 4. Verifica route associate
        print("\n🛣️  ROUTE ASSOCIATE:")
        routes = check_route_usage(template)
        if routes:
            for route in routes:
                print(f"  📁 {route['file']}")
                print(f"  🔧 Funzione: {route['function']}")
                print(f"  📄 Contesto: {route['context']}")
                print()
        else:
            print("  ❌ Nessuna route trovata")
        
        # 5. Raccomandazione
        print("\n💡 RACCOMANDAZIONE:")
        if not usages and not routes:
            print("  🗑️  RIMUOVI: Template non utilizzato")
            recommendation = "REMOVE"
        elif len(usages) <= 2 and not functionality.get('complexity', False):
            print("  ⚠️  CONSIDERA RIMOZIONE: Uso limitato e semplice")
            recommendation = "CONSIDER_REMOVE"
        elif functionality.get('complexity', False) and usages:
            print("  ✅ MANTIENI: Template complesso e utilizzato")
            recommendation = "KEEP"
        else:
            print("  🤔 ANALISI MANUALE: Necessaria verifica approfondita")
            recommendation = "MANUAL_REVIEW"
        
        analysis_results[template] = {
            'functionality': functionality,
            'usages': usages,
            'routes': routes,
            'recommendation': recommendation
        }
    
    # 6. Summary e azioni raccomandate
    print(f"\n{'='*60}")
    print("📊 RIASSUNTO E AZIONI RACCOMANDATE")
    print(f"{'='*60}")
    
    to_remove = []
    to_review = []
    to_keep = []
    
    for template, analysis in analysis_results.items():
        recommendation = analysis['recommendation']
        if recommendation == 'REMOVE':
            to_remove.append(template)
        elif recommendation in ['CONSIDER_REMOVE', 'MANUAL_REVIEW']:
            to_review.append(template)
        else:
            to_keep.append(template)
    
    if to_remove:
        print(f"\n🗑️  DA RIMUOVERE IMMEDIATAMENTE ({len(to_remove)}):")
        for template in to_remove:
            print(f"  - {template}")
    
    if to_review:
        print(f"\n🤔 DA ANALIZZARE MANUALMENTE ({len(to_review)}):")
        for template in to_review:
            print(f"  - {template} ({analysis_results[template]['recommendation']})")
    
    if to_keep:
        print(f"\n✅ DA MANTENERE ({len(to_keep)}):")
        for template in to_keep:
            print(f"  - {template}")
    
    # Salva risultati dettagliati
    output_file = "/home/nugh75/Git/anatema2/template_analysis_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Risultati dettagliati salvati in: {output_file}")
    print("\n✅ Analisi completata!")

if __name__ == "__main__":
    main()
