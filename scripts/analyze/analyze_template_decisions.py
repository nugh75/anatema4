#!/usr/bin/env python3
"""
Analisi finale e decisioni sui template obsoleti - Task 1.4
Verifica duplicazioni e sovrapposizioni tra template normali e advanced.
"""

import os
import re
from pathlib import Path

def analyze_route_mapping():
    """Analizza le route e i template corrispondenti"""
    ml_views_path = "/home/nugh75/Git/anatema2/app/views/ml.py"
    
    with open(ml_views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Trova tutte le route e i loro template
    route_pattern = r'@ml_bp\.route\([^)]+\)\s*def\s+(\w+)[^:]*:.*?render_template\([\'"]([^\'\"]+)[\'"],[^)]*\)'
    matches = re.findall(route_pattern, content, re.DOTALL)
    
    route_mapping = {}
    for func_name, template in matches:
        route_mapping[func_name] = template
    
    return route_mapping

def compare_templates(template1_path, template2_path):
    """Confronta due template per similarità"""
    try:
        with open(template1_path, 'r', encoding='utf-8') as f:
            content1 = f.read()
        with open(template2_path, 'r', encoding='utf-8') as f:
            content2 = f.read()
        
        # Analizza similarità
        lines1 = set(content1.split('\n'))
        lines2 = set(content2.split('\n'))
        
        common_lines = lines1.intersection(lines2)
        similarity = len(common_lines) / max(len(lines1), len(lines2)) if max(len(lines1), len(lines2)) > 0 else 0
        
        return {
            'similarity': similarity,
            'lines_template1': len(lines1),
            'lines_template2': len(lines2),
            'common_lines': len(common_lines),
            'content1_length': len(content1),
            'content2_length': len(content2)
        }
    except Exception as e:
        return {'error': str(e)}

def check_template_usage_in_links():
    """Verifica l'uso dei template nei link di altri template"""
    templates_dir = "/home/nugh75/Git/anatema2/app/templates"
    template_usage = {}
    
    potentially_obsolete = [
        'view_columns.html',
        'view_rows.html', 
        'select_column.html',
        'select_row.html',
        'single_column_view.html',
        'single_row_view.html'
    ]
    
    for template_name in potentially_obsolete:
        usage_count = 0
        usage_files = []
        
        # Cerca in tutti i template
        for root, dirs, files in os.walk(templates_dir):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Cerca riferimenti diretti al template (nelle route)
                        template_base = template_name.replace('.html', '')
                        patterns = [
                            f'url_for.*{template_base}',
                            f'href.*{template_base}',
                            template_name
                        ]
                        
                        for pattern in patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                usage_count += 1
                                usage_files.append(file_path)
                                break
                                
                    except Exception as e:
                        pass
        
        template_usage[template_name] = {
            'usage_count': usage_count,
            'usage_files': usage_files
        }
    
    return template_usage

def main():
    print("=== ANALISI FINALE TEMPLATE OBSOLETI - TASK 1.4 ===\n")
    
    base_templates_dir = "/home/nugh75/Git/anatema2/app/templates/ml"
    
    # 1. Mappa route -> template
    print("🗺️  MAPPATURA ROUTE -> TEMPLATE:")
    route_mapping = analyze_route_mapping()
    for func, template in route_mapping.items():
        print(f"  {func} -> {template}")
    
    # 2. Confronta template normali vs advanced
    print(f"\n🔍 CONFRONTO TEMPLATE NORMALI VS ADVANCED:")
    
    comparisons = [
        ('view_columns.html', 'advanced_column_view.html'),
        ('view_rows.html', 'advanced_row_view.html'),
        ('single_column_view.html', 'advanced_column_view.html'),
        ('single_row_view.html', 'advanced_row_view.html')
    ]
    
    for template1, template2 in comparisons:
        path1 = os.path.join(base_templates_dir, template1)
        path2 = os.path.join(base_templates_dir, template2)
        
        if os.path.exists(path1) and os.path.exists(path2):
            comparison = compare_templates(path1, path2)
            print(f"\n  📊 {template1} vs {template2}:")
            print(f"    Similarità: {comparison.get('similarity', 0):.2%}")
            print(f"    Righe {template1}: {comparison.get('lines_template1', 0)}")
            print(f"    Righe {template2}: {comparison.get('lines_template2', 0)}")
            print(f"    Righe comuni: {comparison.get('common_lines', 0)}")
        else:
            print(f"\n  ❌ {template1} o {template2} non trovato")
    
    # 3. Verifica uso nei link
    print(f"\n🔗 USO NEI LINK DI ALTRI TEMPLATE:")
    template_usage = check_template_usage_in_links()
    for template, usage in template_usage.items():
        print(f"\n  📄 {template}:")
        print(f"    Uso in {usage['usage_count']} file")
        for file_path in usage['usage_files']:
            print(f"      - {file_path}")
    
    # 4. Decisioni finali
    print(f"\n💡 DECISIONI FINALI:")
    
    # Verifica se esistono route attive per i template
    active_templates = set(route_mapping.values())
    potentially_obsolete = [
        'view_columns.html',
        'view_rows.html', 
        'select_column.html',
        'select_row.html',
        'single_column_view.html',
        'single_row_view.html'
    ]
    
    for template in potentially_obsolete:
        template_path = f"ml/{template}"
        
        print(f"\n  📄 {template}:")
        
        # Verifica se ha route attiva
        has_active_route = template_path in active_templates
        print(f"    ✅ Route attiva: {'Sì' if has_active_route else 'No'}")
        
        # Verifica se ha versione advanced
        advanced_name = template.replace('view_', 'advanced_').replace('single_', 'advanced_')
        has_advanced = advanced_name in [t.split('/')[-1] for t in active_templates if 'advanced' in t]
        print(f"    🚀 Versione Advanced: {'Sì' if has_advanced else 'No'}")
        
        # Uso in altri template
        usage_count = template_usage.get(template, {}).get('usage_count', 0)
        print(f"    🔗 Uso in altri template: {usage_count}")
        
        # Raccomandazione
        if has_active_route and not has_advanced:
            print(f"    ✅ RACCOMANDAZIONE: MANTIENI (route attiva, no alternative)")
        elif has_active_route and has_advanced:
            print(f"    🤔 RACCOMANDAZIONE: VALUTA MIGRAZIONE (route attiva ma esiste advanced)")
        elif not has_active_route and usage_count == 0:
            print(f"    🗑️  RACCOMANDAZIONE: RIMUOVI (no route, no uso)")
        else:
            print(f"    ⚠️  RACCOMANDAZIONE: ANALISI MANUALE (situazione complessa)")
    
    print(f"\n✅ Analisi completata!")

if __name__ == "__main__":
    main()
