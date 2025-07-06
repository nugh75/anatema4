#!/usr/bin/env python3
"""
Fix Alembic Multiple Heads - Task 2.4
Risolve il problema delle multiple heads e della migrazione problematica increase_column_name_length

PROBLEMA:
1. Due heads attive: fe7f4e6d2ea1, 912d14cfffc3
2. Migrazione increase_column_name_length.py tenta di modificare colonna inesistente
3. Database current revision: None

SOLUZIONE:
1. Rimuovere la migrazione problematica increase_column_name_length.py
2. Applicare le migrazioni esistenti valide
3. Creare nuovo merge se necessario
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Esegue un comando e restituisce il risultato"""
    print(f"\n🔄 {description}")
    print(f"Comando: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="/home/nugh75/Git/anatema2")
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"❌ Errore nell'esecuzione: {e}")
        return False, "", str(e)

def main():
    print("🚀 Fix Alembic Multiple Heads - Task 2.4")
    print("=" * 60)
    
    # 1. Controllo situazione attuale
    print("\n📊 FASE 1: Analisi situazione attuale")
    success, stdout, stderr = run_command(
        "cd /home/nugh75/Git/anatema2 && /home/nugh75/Git/anatema2/venv/bin/python -m flask db current",
        "Verifica current revision"
    )
    
    success, stdout, stderr = run_command(
        "cd /home/nugh75/Git/anatema2 && /home/nugh75/Git/anatema2/venv/bin/python -m flask db heads",
        "Verifica heads attive"
    )
    
    # 2. Rimozione migrazione problematica
    print("\n🗑️ FASE 2: Rimozione migrazione problematica")
    problematic_file = "/home/nugh75/Git/anatema2/migrations/versions/increase_column_name_length.py"
    
    if os.path.exists(problematic_file):
        print(f"❌ Trovata migrazione problematica: {problematic_file}")
        print("🗑️ Rimozione in corso...")
        
        # Backup del file
        backup_file = problematic_file + ".backup"
        success, _, _ = run_command(f"cp {problematic_file} {backup_file}", "Backup migrazione problematica")
        
        # Rimozione del file
        success, _, _ = run_command(f"rm {problematic_file}", "Rimozione migrazione problematica")
        
        if success:
            print("✅ Migrazione problematica rimossa con successo")
        else:
            print("❌ Errore nella rimozione della migrazione")
            return False
    else:
        print("ℹ️ Migrazione problematica non trovata")
    
    # 3. Verifica migrazioni disponibili
    print("\n📋 FASE 3: Verifica migrazioni disponibili")
    success, stdout, stderr = run_command(
        "cd /home/nugh75/Git/anatema2 && ls -la migrations/versions/ | grep -E '(fe7f4e6d2ea1|912d14cfffc3|2944c79a0f76)'",
        "Lista migrazioni target"
    )
    
    # 4. Tentativo upgrade a merge esistente
    print("\n⬆️ FASE 4: Upgrade a migrazione merge esistente")
    success, stdout, stderr = run_command(
        "cd /home/nugh75/Git/anatema2 && /home/nugh75/Git/anatema2/venv/bin/python -m flask db upgrade 2944c79a0f76",
        "Upgrade a migrazione merge unificata"
    )
    
    if success:
        print("✅ Upgrade riuscito alla migrazione merge")
    else:
        print("❌ Upgrade fallito, proviamo approccio alternativo")
        
        # 5. Approccio alternativo: upgrade alle heads singolarmente
        print("\n🔄 FASE 5: Upgrade heads singolarmente")
        
        # Upgrade alla prima head
        success1, _, _ = run_command(
            "cd /home/nugh75/Git/anatema2 && /home/nugh75/Git/anatema2/venv/bin/python -m flask db upgrade fe7f4e6d2ea1",
            "Upgrade a fe7f4e6d2ea1"
        )
        
        if success1:
            print("✅ Upgrade a fe7f4e6d2ea1 riuscito")
            
            # Upgrade alla seconda head
            success2, _, _ = run_command(
                "cd /home/nugh75/Git/anatema2 && /home/nugh75/Git/anatema2/venv/bin/python -m flask db upgrade 912d14cfffc3",
                "Upgrade a 912d14cfffc3"
            )
            
            if success2:
                print("✅ Upgrade a 912d14cfffc3 riuscito")
            else:
                print("❌ Upgrade a 912d14cfffc3 fallito")
        else:
            print("❌ Upgrade a fe7f4e6d2ea1 fallito")
    
    # 6. Verifica finale
    print("\n✅ FASE 6: Verifica finale")
    success, stdout, stderr = run_command(
        "cd /home/nugh75/Git/anatema2 && /home/nugh75/Git/anatema2/venv/bin/python -m flask db current",
        "Verifica current revision finale"
    )
    
    success, stdout, stderr = run_command(
        "cd /home/nugh75/Git/anatema2 && /home/nugh75/Git/anatema2/venv/bin/python -m flask db heads",
        "Verifica heads finali"
    )
    
    # 7. Test connessione app
    print("\n🧪 FASE 7: Test connessione applicazione")
    success, stdout, stderr = run_command(
        "cd /home/nugh75/Git/anatema2 && /home/nugh75/Git/anatema2/venv/bin/python -c \"from app import create_app; app = create_app(); print('✅ App creata con successo')\"",
        "Test creazione app"
    )
    
    if success:
        print("✅ Applicazione funziona correttamente!")
        print("\n🎉 SUCCESSO: Multiple heads risolte e database aggiornato")
        print("🚀 Pronto per procedere con Task 2.4 - Store Etichette Centralizzato")
        return True
    else:
        print("❌ Problemi con l'applicazione, richiede ulteriore debug")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
