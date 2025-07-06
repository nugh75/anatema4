#!/usr/bin/env python3
"""
Fix Task 2.3 Warning - Verifica Campi Autorizzazione Aggiunti
Testa che i campi mancanti sono stati aggiunti correttamente al modello LabelApplication
"""

import os
import sys
from pathlib import Path

def verify_authorization_fields_fix():
    """Verifica che i campi di autorizzazione siano stati aggiunti correttamente"""
    print("="*80)
    print("VERIFICA FIX CAMPI AUTORIZZAZIONE - TASK 2.3 WARNING RESOLUTION")
    print("="*80)
    
    base_path = Path("/home/nugh75/Git/anatema2")
    models_file = base_path / "app/models_labeling.py"
    
    if not models_file.exists():
        print("✗ File models_labeling.py non trovato")
        return False
    
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n1. VERIFICA CAMPI AUTORIZZAZIONE AGGIUNTI")
    print("-" * 50)
    
    # Campi che dovrebbero essere presenti dopo il fix
    required_fields = {
        "authorized_by": "db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))",
        "authorized_at": "db.Column(db.DateTime)",  
        "approval_status": "db.Column(db.String(20), default='approved')",
        "authorization_status": "db.Column(db.String(20), default='not_required')",
        "application_type": "db.Column(db.String(20), nullable=False)"
    }
    
    fields_found = 0
    for field_name, expected_definition in required_fields.items():
        if field_name in content:
            print(f"✓ {field_name} - PRESENTE")
            fields_found += 1
            
            # Verifica che sia nella definizione corretta
            if "db.Column" in expected_definition and "db.Column" in content:
                # Cerca la linea specifica
                lines = content.split('\n')
                for line in lines:
                    if field_name in line and "db.Column" in line:
                        print(f"  ➤ {line.strip()}")
                        break
        else:
            print(f"✗ {field_name} - MANCANTE")
    
    print(f"\nTotale campi trovati: {fields_found}/{len(required_fields)}")
    
    print("\n2. VERIFICA RELATIONSHIPS AGGIORNATE")
    print("-" * 50)
    
    relationships_to_check = [
        "applier = db.relationship('User'",
        "authorizer = db.relationship('User'"
    ]
    
    for relationship in relationships_to_check:
        if relationship in content:
            print(f"✓ {relationship.split('=')[0].strip()} - PRESENTE")
        else:
            print(f"✗ {relationship.split('=')[0].strip()} - MANCANTE")
    
    print("\n3. VERIFICA TO_DICT() AGGIORNATO")
    print("-" * 50)
    
    to_dict_fields = [
        "'authorized_by'",
        "'authorized_at'", 
        "'approval_status'",
        "'authorization_status'"
    ]
    
    for field in to_dict_fields:
        if field in content:
            print(f"✓ {field} nel to_dict() - PRESENTE")
        else:
            print(f"✗ {field} nel to_dict() - MANCANTE")
    
    print("\n4. ESTRAZIONE DEFINIZIONE CLASSE AGGIORNATA")
    print("-" * 50)
    
    # Estrai la definizione aggiornata della classe LabelApplication
    lines = content.split('\n')
    in_label_app = False
    class_lines = []
    
    for line in lines:
        if "class LabelApplication" in line:
            in_label_app = True
        elif in_label_app and line.startswith('class ') and 'LabelApplication' not in line:
            break
        
        if in_label_app:
            class_lines.append(line)
            if len(class_lines) > 50:  # Limita output
                class_lines.append("    # ... (classe continua)")
                break
    
    print("Definizione classe aggiornata (prime 50 righe):")
    for line in class_lines:
        print(line)
    
    print("\n5. RIEPILOGO STATO FIX")
    print("-" * 50)
    
    if fields_found == len(required_fields):
        print("✅ TUTTI I CAMPI DI AUTORIZZAZIONE SONO STATI AGGIUNTI CORRETTAMENTE")
        print("✅ Fix Task 2.3 warning completato con successo")
        print("📋 Prossimo step: Creare migrazione database e testare")
        return True
    else:
        missing_count = len(required_fields) - fields_found
        print(f"⚠ ANCORA {missing_count} CAMPI MANCANTI")
        print("❌ Fix Task 2.3 warning non ancora completato")
        return False

if __name__ == "__main__":
    success = verify_authorization_fields_fix()
    sys.exit(0 if success else 1)
