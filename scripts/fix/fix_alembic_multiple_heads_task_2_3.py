#!/usr/bin/env python3
"""
Script per risolvere il problema dei multiple heads in Alembic - Task 2.3
Questo script automatizza il processo di merge e creazione della migrazione finale
per i campi di autorizzazione mancanti.

Created: 30 giugno 2025
Author: Refactoring Task 2.3
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Esegue un comando e restituisce il risultato"""
    print(f"\n🔄 {description}")
    print(f"Comando: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd="/home/nugh75/Git/anatema2"
        )
        
        if result.stdout:
            print(f"✅ Output:\n{result.stdout}")
        
        if result.stderr:
            print(f"⚠️ Errori:\n{result.stderr}")
        
        return result.returncode == 0, result.stdout, result.stderr
    
    except Exception as e:
        print(f"❌ Errore nell'esecuzione: {e}")
        return False, "", str(e)

def check_heads():
    """Verifica lo stato attuale degli heads"""
    print("📋 VERIFICA STATO HEADS ALEMBIC")
    success, stdout, stderr = run_command("python -m flask db heads", "Controllo heads attuali")
    
    if success and stdout:
        heads = [line.strip() for line in stdout.split('\n') if line.strip()]
        print(f"🔍 Trovati {len(heads)} heads:")
        for head in heads:
            print(f"  - {head}")
        return len(heads), heads
    else:
        print("❌ Impossibile verificare heads")
        return 0, []

def merge_all_heads():
    """Esegue merge di tutti gli heads"""
    print("\n🔗 MERGE DI TUTTI GLI HEADS")
    
    # Verifica heads iniziali
    num_heads, heads = check_heads()
    
    if num_heads <= 1:
        print("✅ Solo un head presente, non serve merge")
        return True
    
    # Esegue merge finale
    success, stdout, stderr = run_command(
        'python -m flask db merge -m "final_merge_all_heads_for_auth_fields"',
        f"Merge finale di {num_heads} heads"
    )
    
    if not success:
        print("❌ Errore nel merge finale")
        return False
    
    # Verifica risultato
    num_heads_after, _ = check_heads()
    
    if num_heads_after == 1:
        print("✅ Merge completato con successo!")
        return True
    else:
        print(f"⚠️ Ancora {num_heads_after} heads presenti, potrebbe servire altro merge")
        return num_heads_after < num_heads  # Progresso fatto

def apply_migrations():
    """Applica tutte le migrazioni al database"""
    print("\n📦 APPLICAZIONE MIGRAZIONI AL DATABASE")
    
    success, stdout, stderr = run_command(
        "python -m flask db upgrade",
        "Applicazione di tutte le migrazioni"
    )
    
    return success

def create_auth_fields_migration():
    """Crea la migrazione per i campi di autorizzazione mancanti"""
    print("\n🛠️ CREAZIONE MIGRAZIONE CAMPI AUTORIZZAZIONE")
    
    success, stdout, stderr = run_command(
        'python -m flask db migrate -m "add_missing_authorization_fields_to_label_applications"',
        "Generazione migrazione per campi autorizzazione"
    )
    
    return success

def main():
    """Funzione principale per risolvere il problema degli heads multipli"""
    print("🚀 RISOLUZIONE MULTIPLE HEADS ALEMBIC - TASK 2.3")
    print("=" * 60)
    
    # Step 1: Verifica situazione iniziale
    print("\n📋 STEP 1: VERIFICA SITUAZIONE INIZIALE")
    initial_heads, _ = check_heads()
    
    if initial_heads <= 1:
        print("✅ Situazione già risolta!")
        return True
    
    # Step 2: Merge di tutti gli heads
    print("\n🔗 STEP 2: MERGE DEGLI HEADS")
    merge_success = merge_all_heads()
    
    if not merge_success:
        print("❌ Merge fallito, interrompo il processo")
        return False
    
    # Step 3: Applica migrazioni esistenti
    print("\n📦 STEP 3: APPLICAZIONE MIGRAZIONI")
    apply_success = apply_migrations()
    
    if not apply_success:
        print("⚠️ Errore nell'applicazione migrazioni, ma continuo...")
    
    # Step 4: Crea migrazione per campi autorizzazione
    print("\n🛠️ STEP 4: MIGRAZIONE CAMPI AUTORIZZAZIONE")
    migrate_success = create_auth_fields_migration()
    
    if migrate_success:
        print("✅ Migrazione campi autorizzazione creata!")
        
        # Step 5: Applica la nuova migrazione
        print("\n📦 STEP 5: APPLICAZIONE NUOVA MIGRAZIONE")
        final_apply = apply_migrations()
        
        if final_apply:
            print("🎉 PROCESSO COMPLETATO CON SUCCESSO!")
            print("\n📋 PROSSIMI PASSI:")
            print("1. Eseguire verify_auth_fields_fix_task_2_3.py")
            print("2. Eseguire test_task_2_3_final.py")
            print("3. Verificare che il warning sia risolto")
            return True
        else:
            print("⚠️ Errore nell'applicazione finale")
            return False
    else:
        print("❌ Errore nella creazione migrazione campi autorizzazione")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ Script completato con successo!")
        sys.exit(0)
    else:
        print("\n❌ Script fallito!")
        sys.exit(1)
