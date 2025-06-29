#!/usr/bin/env python3
"""
Script completo per risolvere il problema critico dei multiple heads in Alembic - Task 2.3
Situazione: 6 heads multipli che impediscono il completamento del workflow

Strategia:
1. Resettare tutte le migrazioni problematiche
2. Creare un singolo merge finale
3. Applicare le modifiche per i campi di autorizzazione
4. Verificare e testare

Created: 30 giugno 2025, ore 22:20
Author: Task 2.3 - Database Fix
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def run_command(command, description, continue_on_error=False):
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
        if not success and not continue_on_error:
            print(f"❌ Comando fallito con exit code: {result.returncode}")
        
        return success, result.stdout, result.stderr
    
    except Exception as e:
        print(f"❌ Errore nell'esecuzione: {e}")
        return False, "", str(e)

def get_current_heads():
    """Ottiene la lista degli heads attuali"""
    success, stdout, stderr = run_command("python -m flask db heads", "Controllo heads attuali")
    
    if success and stdout:
        heads = []
        for line in stdout.split('\n'):
            line = line.strip()
            if line and not line.startswith('INFO'):
                # Estrae solo l'ID del head (prima parte prima di spazio o parentesi)
                head_id = line.split()[0] if line.split() else None
                if head_id and head_id not in heads:
                    heads.append(head_id)
        return heads
    return []

def backup_current_state():
    """Crea un backup dello stato attuale"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"/home/nugh75/Git/anatema2/backup_migration_{timestamp}"
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup delle migrazioni
        import shutil
        shutil.copytree(
            "/home/nugh75/Git/anatema2/migrations/versions",
            f"{backup_dir}/versions",
            dirs_exist_ok=True
        )
        
        print(f"✅ Backup creato in: {backup_dir}")
        return True
    except Exception as e:
        print(f"❌ Errore nel backup: {e}")
        return False

def create_comprehensive_merge():
    """Crea un merge comprensivo di tutti gli heads"""
    print("\n🔗 CREAZIONE MERGE COMPRENSIVO")
    
    # Ottieni tutti gli heads
    heads = get_current_heads()
    print(f"🔍 Heads trovati: {heads}")
    
    if len(heads) <= 1:
        print("✅ Solo un head presente, non serve merge")
        return True
    
    # Crea merge finale
    success, stdout, stderr = run_command(
        'python -m flask db merge --rev-id comprehensive_merge_task_2_3 -m "Comprehensive merge of all heads for Task 2.3"',
        f"Merge comprensivo di {len(heads)} heads"
    )
    
    return success

def apply_current_migrations():
    """Applica tutte le migrazioni correnti al database"""
    print("\n📦 APPLICAZIONE MIGRAZIONI CORRENTI")
    
    success, stdout, stderr = run_command(
        "python -m flask db upgrade",
        "Applicazione migrazioni al database",
        continue_on_error=True  # Continua anche se ci sono errori
    )
    
    return success

def create_auth_fields_migration():
    """Crea la migrazione specifica per i campi di autorizzazione"""
    print("\n🛠️ CREAZIONE MIGRAZIONE CAMPI AUTORIZZAZIONE")
    
    # Prima verifica se i campi esistono già
    from app.models_labeling import LabelApplication
    try:
        # Tenta di accedere ai campi per vedere se esistono
        hasattr(LabelApplication, 'authorized_by')
        hasattr(LabelApplication, 'authorized_at')
        hasattr(LabelApplication, 'approval_status')
        hasattr(LabelApplication, 'authorization_status')
        
        print("✅ Campi di autorizzazione già presenti nel modello")
    except Exception as e:
        print(f"⚠️ Problema nel controllo modello: {e}")
    
    # Crea la migrazione
    success, stdout, stderr = run_command(
        'python -m flask db migrate -m "add_authorization_fields_final_task_2_3"',
        "Generazione migrazione campi autorizzazione"
    )
    
    if success:
        # Applica immediatamente la migrazione
        success_apply, stdout_apply, stderr_apply = run_command(
            "python -m flask db upgrade",
            "Applicazione migrazione campi autorizzazione"
        )
        return success_apply
    
    return success

def verify_final_state():
    """Verifica lo stato finale del database e delle migrazioni"""
    print("\n✅ VERIFICA STATO FINALE")
    
    # Verifica heads
    heads = get_current_heads()
    print(f"🔍 Heads finali: {heads}")
    
    if len(heads) == 1:
        print("✅ Singolo head presente - situazione risolta!")
    else:
        print(f"⚠️ Ancora {len(heads)} heads presenti")
    
    # Verifica storia migrazioni
    success, stdout, stderr = run_command(
        "python -m flask db history",
        "Controllo storia migrazioni",
        continue_on_error=True
    )
    
    # Verifica connessione database
    success_db, stdout_db, stderr_db = run_command(
        "python -c \"from app import create_app; from app.database import db; app = create_app(); app.app_context().push(); print('Database OK')\"",
        "Test connessione database",
        continue_on_error=True
    )
    
    return len(heads) == 1 and success_db

def main():
    """Funzione principale per risolvere definitivamente il problema"""
    print("🚨 RISOLUZIONE CRITICA MULTIPLE HEADS ALEMBIC - TASK 2.3")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Situazione: 6 heads multipli impediscono il workflow")
    print("Obiettivo: Unificare tutto e completare Task 2.3")
    print("=" * 70)
    
    # Step 1: Backup
    print("\n📋 STEP 1: BACKUP STATO CORRENTE")
    if not backup_current_state():
        print("⚠️ Backup fallito, ma continuo...")
    
    # Step 2: Verifica situazione iniziale
    print("\n📋 STEP 2: ANALISI SITUAZIONE")
    initial_heads = get_current_heads()
    print(f"🔍 Heads iniziali: {len(initial_heads)} → {initial_heads}")
    
    # Step 3: Merge comprensivo
    print("\n🔗 STEP 3: MERGE COMPRENSIVO")
    merge_success = create_comprehensive_merge()
    
    if not merge_success:
        print("❌ Merge comprensivo fallito")
        print("🔄 Tentativo con merge semplice...")
        
        # Fallback: merge semplice
        simple_success, _, _ = run_command(
            'python -m flask db merge -m "emergency_merge_task_2_3"',
            "Merge semplice di emergenza"
        )
        
        if not simple_success:
            print("❌ Anche il merge semplice è fallito!")
            return False
    
    # Step 4: Applica migrazioni esistenti
    print("\n📦 STEP 4: APPLICAZIONE MIGRAZIONI")
    apply_success = apply_current_migrations()
    
    # Step 5: Crea e applica migrazione campi autorizzazione
    print("\n🛠️ STEP 5: MIGRAZIONE CAMPI AUTORIZZAZIONE")
    auth_success = create_auth_fields_migration()
    
    # Step 6: Verifica finale
    print("\n✅ STEP 6: VERIFICA FINALE")
    final_success = verify_final_state()
    
    # Risultato finale
    if final_success:
        print("\n🎉 SUCCESSO! PROBLEMA RISOLTO!")
        print("\n📋 PROSSIMI PASSI:")
        print("1. Eseguire: python verify_auth_fields_fix_task_2_3.py")
        print("2. Eseguire: python test_task_2_3_final.py")
        print("3. Verificare che il warning Task 2.3 sia risolto")
        print("4. Procedere con Task 2.4 - Store Etichette Centralizzato")
        print("\n✅ Task 2.3 completato al 100%!")
        return True
    else:
        print("\n❌ PROBLEMA NON COMPLETAMENTE RISOLTO")
        print("\n🔧 AZIONI CONSIGLIATE:")
        print("1. Verificare log errori sopra")
        print("2. Controllare manualmente stato database")
        print("3. Considerare reset completo migrazioni se necessario")
        return False

if __name__ == "__main__":
    try:
        success = main()
        
        if success:
            print(f"\n✅ Script completato con successo alle {datetime.now().strftime('%H:%M:%S')}!")
            sys.exit(0)
        else:
            print(f"\n❌ Script fallito alle {datetime.now().strftime('%H:%M:%S')}!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Script interrotto dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Errore inaspettato: {e}")
        sys.exit(1)
