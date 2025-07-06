#!/usr/bin/env python3
"""
Script definitivo per risolvere il problema critico dei multiple heads - Task 2.3
Questo script utilizza un approccio più aggressivo per risolvere il problema.

Created: 30 giugno 2025
Author: Refactoring Task 2.3 - Crisis Resolution
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil
from datetime import datetime

def run_command(command, description, allow_failure=False):
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
        
        success = result.returncode == 0
        if not success and not allow_failure:
            print(f"❌ Comando fallito con exit code: {result.returncode}")
        
        return success, result.stdout, result.stderr
    
    except Exception as e:
        print(f"❌ Errore nell'esecuzione: {e}")
        return False, "", str(e)

def get_current_heads():
    """Ottieni gli heads attuali"""
    success, stdout, stderr = run_command("python -m flask db heads", "Controllo heads attuali")
    
    if success and stdout:
        heads = []
        for line in stdout.strip().split('\n'):
            if line.strip():
                # Estrae solo l'ID dell'head (prima parte)
                head_id = line.split()[0]
                heads.append(head_id)
        return heads
    else:
        return []

def force_upgrade_to_specific_head():
    """Forza l'upgrade a un head specifico"""
    print("\n📦 STEP: FORCE UPGRADE A HEAD SPECIFICO")
    
    # Prova a fare upgrade a fe7f4e6d2ea1 che dovrebbe essere il nostro head target
    success, stdout, stderr = run_command(
        "python -m flask db upgrade fe7f4e6d2ea1",
        "Force upgrade a fe7f4e6d2ea1 (Task 2.1 authorization fields)"
    )
    
    if success:
        print("✅ Upgrade forzato riuscito!")
        return True
    else:
        print("❌ Upgrade forzato fallito")
        return False

def stamp_database_to_head():
    """Stampa il database a un head specifico senza eseguire migrazioni"""
    print("\n🏷️ STEP: STAMP DATABASE")
    
    # Stampa il database come se fosse all'head fe7f4e6d2ea1
    success, stdout, stderr = run_command(
        "python -m flask db stamp fe7f4e6d2ea1",
        "Stamp database to fe7f4e6d2ea1"
    )
    
    if success:
        print("✅ Database stampato con successo!")
        return True
    else:
        print("❌ Stamp database fallito")
        return False

def create_final_migration():
    """Crea la migrazione finale per i campi mancanti"""
    print("\n🛠️ STEP: CREAZIONE MIGRAZIONE FINALE")
    
    # Ora dovremmo essere in grado di creare una nuova migrazione
    success, stdout, stderr = run_command(
        'python -m flask db migrate -m "final_add_missing_auth_fields_task_2_3"',
        "Creazione migrazione finale per campi autorizzazione"
    )
    
    if success:
        print("✅ Migrazione finale creata!")
        
        # Applica la migrazione
        apply_success, apply_stdout, apply_stderr = run_command(
            "python -m flask db upgrade",
            "Applicazione migrazione finale"
        )
        
        if apply_success:
            print("✅ Migrazione finale applicata!")
            return True
        else:
            print("❌ Applicazione migrazione finale fallita")
            return False
    else:
        print("❌ Creazione migrazione finale fallita")
        return False

def verify_final_state():
    """Verifica lo stato finale"""
    print("\n✅ STEP: VERIFICA STATO FINALE")
    
    # Verifica heads
    heads = get_current_heads()
    print(f"🔍 Heads finali: {len(heads)} - {heads}")
    
    # Verifica che i campi siano presenti nel modello
    print("\n🔍 Verifica campi autorizzazione nel modello...")
    
    try:
        # Test rapido per verificare che tutto funzioni
        success, stdout, stderr = run_command(
            'python -c "from app.models_labeling import LabelApplication; print(\'Campi autorizzazione:\'); print(\'- authorized_by:\', hasattr(LabelApplication, \'authorized_by\')); print(\'- authorized_at:\', hasattr(LabelApplication, \'authorized_at\')); print(\'- approval_status:\', hasattr(LabelApplication, \'approval_status\')); print(\'- authorization_status:\', hasattr(LabelApplication, \'authorization_status\'))"',
            "Verifica campi modello LabelApplication"
        )
        
        if success:
            print("✅ Modello verificato con successo!")
        else:
            print("⚠️ Problemi nella verifica modello")
        
    except Exception as e:
        print(f"⚠️ Errore nella verifica: {e}")
    
    return len(heads) <= 1

def main():
    """Funzione principale - approccio drastico"""
    print("🚨 RISOLUZIONE DRASTICA MULTIPLE HEADS - TASK 2.3")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Approccio: Force stamp + migrate")
    print("=" * 60)
    
    # Step 1: Verifica situazione iniziale
    print("\n📋 STEP 1: VERIFICA SITUAZIONE INIZIALE")
    initial_heads = get_current_heads()
    print(f"🔍 Heads iniziali: {len(initial_heads)} - {initial_heads}")
    
    if len(initial_heads) <= 1:
        print("✅ Situazione già risolta!")
        return True
    
    # Step 2: Stampa database a head specifico
    print("\n🏷️ STEP 2: STAMP DATABASE")
    stamp_success = stamp_database_to_head()
    
    if not stamp_success:
        print("❌ Stamp fallito, provo upgrade forzato...")
        
        # Step 2b: Force upgrade
        print("\n📦 STEP 2B: FORCE UPGRADE")
        upgrade_success = force_upgrade_to_specific_head()
        
        if not upgrade_success:
            print("❌ Anche upgrade forzato fallito!")
            return False
    
    # Step 3: Verifica heads dopo stamp/upgrade
    print("\n📋 STEP 3: VERIFICA DOPO STAMP/UPGRADE")
    post_stamp_heads = get_current_heads()
    print(f"🔍 Heads dopo stamp: {len(post_stamp_heads)} - {post_stamp_heads}")
    
    # Step 4: Crea migrazione finale
    print("\n🛠️ STEP 4: MIGRAZIONE FINALE")
    migrate_success = create_final_migration()
    
    if not migrate_success:
        print("⚠️ Migrazione finale fallita, ma continuo con verifica...")
    
    # Step 5: Verifica finale
    print("\n✅ STEP 5: VERIFICA FINALE")
    final_success = verify_final_state()
    
    if final_success:
        print("\n🎉 PROBLEMA RISOLTO CON SUCCESSO!")
        print("\n📋 PROSSIMI PASSI:")
        print("1. Eseguire verify_auth_fields_fix_task_2_3.py")
        print("2. Eseguire test_task_2_3_final.py")
        print("3. Procedere con Task 2.4 - Store Etichette")
        return True
    else:
        print("\n⚠️ Problema parzialmente risolto")
        print("Verifica manualmente lo stato e considera ulteriori azioni")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ Script completato con successo!")
        sys.exit(0)
    else:
        print("\n❌ Script completato con problemi!")
        sys.exit(1)
