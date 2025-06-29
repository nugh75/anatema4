#!/usr/bin/env python3
"""
Analisi Campi Autorizzazione Task 2.3 - Fix Warning Database
Verifica i campi di autorizzazione nel database e completa l'implementazione
"""

import os
from pathlib import Path

def analyze_authorization_fields():
    """Analizza i campi di autorizzazione nelle tabelle del database"""
    print("="*80)
    print("ANALISI CAMPI AUTORIZZAZIONE - FIX WARNING TASK 2.3")
    print("="*80)
    
    base_path = Path("/home/nugh75/Git/anatema2")
    
    print("\n1. VERIFICA CAMPI AUTORIZZAZIONE NEI MODELLI")
    print("-" * 50)
    
    # Analizza models_labeling.py
    models_file = base_path / "app/models_labeling.py"
    if models_file.exists():
        with open(models_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("--- Modello LabelApplication ---")
        
        # Campi di autorizzazione che dovrebbero essere presenti
        auth_fields = [
            "authorized_by",
            "authorized_at", 
            "application_type",
            "approval_status",
            "authorization_status"
        ]
        
        found_fields = []
        missing_fields = []
        
        for field in auth_fields:
            if field in content:
                found_fields.append(field)
                print(f"✓ {field} - PRESENTE")
            else:
                missing_fields.append(field)
                print(f"✗ {field} - MANCANTE")
        
        print(f"\nTotale campi trovati: {len(found_fields)}/{len(auth_fields)}")
        
        if missing_fields:
            print(f"⚠ Campi mancanti: {missing_fields}")
        else:
            print("✓ Tutti i campi di autorizzazione sono presenti")
    
    print("\n2. VERIFICA MIGRAZIONI AUTORIZZAZIONE")
    print("-" * 50)
    
    migrations_dir = base_path / "migrations/versions"
    if migrations_dir.exists():
        migration_files = list(migrations_dir.glob("*authorization*"))
        
        for migration in migration_files:
            print(f"✓ Migrazione trovata: {migration.name}")
            
            # Verifica contenuto migrazione
            with open(migration, 'r', encoding='utf-8') as f:
                migration_content = f.read()
            
            auth_operations = [
                "authorized_by",
                "authorized_at",
                "application_type"
            ]
            
            for operation in auth_operations:
                if operation in migration_content:
                    print(f"  ✓ Campo {operation} presente nella migrazione")
                else:
                    print(f"  ⚠ Campo {operation} non trovato nella migrazione")
    
    print("\n3. VERIFICA SCHEMA DATABASE ATTUALE")
    print("-" * 50)
    
    # Controlla se ci sono stati aggiornamenti recenti
    label_app_found = False
    if models_file.exists():
        with open(models_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "class LabelApplication" in content:
            label_app_found = True
            print("✓ Classe LabelApplication trovata")
            
            # Estrai la definizione della classe
            lines = content.split('\n')
            in_label_app = False
            class_definition = []
            
            for line in lines:
                if "class LabelApplication" in line:
                    in_label_app = True
                elif in_label_app and line.startswith('class ') and 'LabelApplication' not in line:
                    break
                
                if in_label_app:
                    class_definition.append(line)
            
            print("\nDefinizione attuale LabelApplication:")
            print("-" * 30)
            for line in class_definition[:20]:  # Prime 20 righe
                print(line)
    
    print("\n4. IDENTIFICAZIONE PROBLEMA E SOLUZIONE")
    print("-" * 50)
    
    if not label_app_found:
        print("✗ PROBLEMA: Classe LabelApplication non trovata")
        print("📋 SOLUZIONE: Verificare app/models_labeling.py")
    else:
        print("✓ Modello presente, verificare presenza campi specifici")
    
    print("\n5. PIANO RISOLUZIONE WARNING")
    print("-" * 50)
    print("1. Verificare presenza effettiva campi authorized_by, authorized_at")
    print("2. Se mancanti, aggiungerli al modello LabelApplication")
    print("3. Creare migrazione se necessario")
    print("4. Aggiornare test per verificare tutti i campi")
    print("5. Ri-testare integrazione per eliminare warning")

if __name__ == "__main__":
    analyze_authorization_fields()
