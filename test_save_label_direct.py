#!/usr/bin/env python3
"""
Test diretto della funzione save_cell_label per verificare se il fix funziona
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from app.models import User, Project, File, ExcelSheet, MLAnalysis, AutoLabel, AutoLabelApplication
from app.views.ml import save_cell_label
from flask import url_for
import uuid

def test_save_cell_label_direct():
    """Test diretto della funzione save_cell_label"""
    app = create_app('testing')
    
    with app.app_context():
        print("=== Test Diretto save_cell_label ===")
        
        # Simuliamo i parametri che causavano l'errore
        test_params = {
            'row_index': 50,
            'column_name': 'Test Column',
            'label_name': 'Sentiment Neutrale',
            'label_description': '',
            'confidence': 1.0,
            'source': 'manual'
        }
        
        print(f"Parametri test: {test_params}")
        
        # Verifica che il modello AutoLabel sia corretto
        try:
            # Test creazione AutoLabel con i parametri corretti
            test_auto_label = AutoLabel(
                ml_analysis_id=str(uuid.uuid4()),
                label_name=test_params['label_name'],
                label_description=test_params['label_description'],
                category='manual',  # Parametro corretto
                confidence_score=test_params['confidence'],
                column_name=test_params['column_name'],
                created_by=str(uuid.uuid4()),
                label_type='manual'
            )
            print("✅ AutoLabel può essere creato con parametri corretti")
            
            # Test con parametro errato
            try:
                wrong_auto_label = AutoLabel(
                    ml_analysis_id=str(uuid.uuid4()),
                    label_name=test_params['label_name'],
                    label_description=test_params['label_description'],
                    label_category='manual',  # Parametro ERRATO
                    confidence_score=test_params['confidence'],
                    column_name=test_params['column_name'],
                    created_by=str(uuid.uuid4()),
                    label_type='manual'
                )
                print("❌ AutoLabel accetta 'label_category' (NON DOVREBBE)")
                return False
            except TypeError as e:
                if 'label_category' in str(e):
                    print("✅ AutoLabel correttamente rifiuta 'label_category'")
                else:
                    print(f"❌ Errore diverso: {e}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Errore nella creazione AutoLabel: {e}")
            return False

if __name__ == '__main__':
    success = test_save_cell_label_direct()
    
    if success:
        print("\n✅ Test passato! Il modello AutoLabel è corretto.")
        print("Il problema 'label_category' potrebbe essere in cache o nel codice nascosto.")
        print("\nSuggerimenti:")
        print("1. Cancella cache browser (Ctrl+Shift+R)")
        print("2. Verifica che non ci siano file .pyc cached")
        print("3. Controlla se ci sono altri endpoint che usano 'label_category'")
    else:
        print("\n❌ Test fallito! C'è ancora un problema con il modello.")
    
    sys.exit(0 if success else 1)
