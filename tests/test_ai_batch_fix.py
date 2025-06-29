#!/usr/bin/env python3
"""
Test per verificare che l'etichettatura AI batch ora salvi correttamente le etichette
"""

import sys
import os
import requests
import json
from datetime import datetime

def test_ai_batch_labeling():
    """Test per verificare che l'etichettatura AI batch salvi le etichette"""
    
    # Base URL del server (modifica se necessario)
    base_url = "http://127.0.0.1:5000"
    
    # IDs di test (sostituisci con IDs validi del tuo database)
    project_id = "049863cd-44a4-4948-9e9b-206cead88943"  # Da sostituire
    sheet_id = "10a1605b-fead-45a7-91fb-259b57e9a2ce"     # Da sostituire
    
    print("=== Test Etichettatura AI Batch ===")
    print(f"Data test: {datetime.now()}")
    print(f"URL server: {base_url}")
    print(f"Project ID: {project_id}")
    print(f"Sheet ID: {sheet_id}")
    
    # Dati per il test
    test_data = {
        'column_name': 'Test Column',  # Nome colonna di test
        'template': 'sentiment',
        'max_items': 5
    }
    
    url = f"{base_url}/ml/projects/{project_id}/sheets/{sheet_id}/batch-ai-label"
    
    try:
        print(f"\nInviando richiesta POST a: {url}")
        print(f"Dati: {json.dumps(test_data, indent=2)}")
        
        # Nota: questo test richiede un session cookie valido per l'autenticazione
        # In un ambiente di produzione dovresti gestire l'autenticazione
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Successo! Risposta:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get('labels_saved', 0) > 0:
                print(f"\n🎉 Etichette salvate correttamente: {result['labels_saved']}")
                return True
            else:
                print(f"\n⚠️ Nessuna etichetta salvata")
                return False
        else:
            print(f"\n❌ Errore HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"Errore: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Testo errore: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Errore di connessione: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Errore imprevisto: {e}")
        return False

if __name__ == '__main__':
    print("NOTA: Questo test richiede:")
    print("1. Server Flask in esecuzione su http://127.0.0.1:5000")
    print("2. IDs di progetto e foglio validi")
    print("3. Configurazione ML attiva nel progetto")
    print("4. Autenticazione utente (potrebbe fallire senza session cookie)")
    print()
    
    success = test_ai_batch_labeling()
    
    if success:
        print("\n✅ Test completato con successo!")
        sys.exit(0)
    else:
        print("\n❌ Test fallito!")
        print("Controlla i log del server per maggiori dettagli.")
        sys.exit(1)
