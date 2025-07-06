#!/usr/bin/env python3
"""
Script per analizzare la documentazione in docs/ e identificare file obsoleti/duplicati
"""
import os
from pathlib import Path
import re

def analyze_docs_structure():
    """Analizza la struttura della documentazione"""
    docs_path = Path("/home/nugh75/Git/anatema2/docs")
    
    print("📚 ANALISI DOCUMENTAZIONE")
    print("=" * 50)
    
    # Lista tutti i file markdown
    md_files = list(docs_path.glob("*.md"))
    
    # Categorizza i file
    categories = {
        "master": [],
        "task_reports": [],
        "technical": [],
        "obsolete_candidates": []
    }
    
    for file in md_files:
        name = file.name.lower()
        
        if "master" in name or "indice" in name:
            categories["master"].append(file.name)
        elif "task_" in name:
            categories["task_reports"].append(file.name)
        elif any(x in name for x in ["analisi", "database", "sistema", "multiple"]):
            categories["technical"].append(file.name)
        elif any(x in name for x in ["piano", "ristrutturazione"]):
            categories["obsolete_candidates"].append(file.name)
        else:
            categories["technical"].append(file.name)
    
    # Report categorizzazione
    for category, files in categories.items():
        if files:
            print(f"\n📁 {category.upper().replace('_', ' ')}:")
            for file in sorted(files):
                print(f"   - {file}")
    
    # Identifica potenziali duplicati
    print(f"\n🔍 POTENZIALI PROBLEMI:")
    
    # Piano vs piano
    piano_files = [f for f in md_files if "piano" in f.name.lower()]
    if len(piano_files) > 1:
        print("⚠️  Multipli file PIANO:")
        for f in piano_files:
            print(f"   - {f.name}")
    
    # Task reports
    task_files = [f for f in md_files if "task_" in f.name.lower()]
    if task_files:
        print("📋 Task reports da integrare:")
        for f in task_files:
            print(f"   - {f.name}")
    
    print("\n" + "=" * 50)
    print(f"📊 TOTALE FILE: {len(md_files)}")
    
    return categories

if __name__ == "__main__":
    analyze_docs_structure()
