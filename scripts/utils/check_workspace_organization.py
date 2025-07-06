#!/usr/bin/env python3
"""
Script di verifica dell'organizzazione workspace
Controlla che tutti i file siano nelle cartelle corrette
"""
import os
from pathlib import Path

def check_workspace_organization():
    """Verifica l'organizzazione del workspace"""
    base_path = Path("/home/nugh75/Git/anatema2")
    
    print("🗂️ VERIFICA ORGANIZZAZIONE WORKSPACE")
    print("=" * 50)
    
    # Verifica cartelle principali
    expected_folders = [
        "app", "config", "migrations", "docs", 
        "tests", "scripts", "uploads", "logs"
    ]
    
    print("\n📁 Cartelle principali:")
    for folder in expected_folders:
        path = base_path / folder
        status = "✅" if path.exists() else "❌"
        print(f"{status} {folder}/")
    
    # Verifica sottocartelle scripts
    scripts_subfolders = ["analyze", "fix", "validate", "task", "utils"]
    
    print("\n📁 Sottocartelle scripts/:")
    for subfolder in scripts_subfolders:
        path = base_path / "scripts" / subfolder
        status = "✅" if path.exists() else "❌"
        count = len(list(path.glob("*.py"))) if path.exists() else 0
        print(f"{status} scripts/{subfolder}/ ({count} files)")
    
    # Verifica radice pulita
    print("\n📄 File nella radice:")
    root_files = [f for f in os.listdir(base_path) if os.path.isfile(base_path / f)]
    essential_files = [
        "run.py", "setup.py", "requirements.txt", 
        "README.md", ".env", ".gitignore"
    ]
    
    for file in root_files:
        if file.startswith('.'):
            continue
        status = "✅" if file in essential_files else "⚠️"
        print(f"{status} {file}")
    
    # Conta totale file per categoria
    print("\n📊 Statistiche file:")
    test_files = len(list((base_path / "tests").glob("*.py")))
    doc_files = len(list((base_path / "docs").glob("*.md")))
    script_files = sum(len(list((base_path / "scripts" / sub).glob("*.py"))) 
                      for sub in scripts_subfolders if (base_path / "scripts" / sub).exists())
    
    print(f"✅ Test files: {test_files}")
    print(f"✅ Documentation files: {doc_files}")
    print(f"✅ Script files: {script_files}")
    
    print("\n" + "=" * 50)
    print("✅ ORGANIZZAZIONE WORKSPACE COMPLETATA!")

if __name__ == "__main__":
    check_workspace_organization()
