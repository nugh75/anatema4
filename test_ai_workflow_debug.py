#!/usr/bin/env python3
"""
Debug specifico del workflow di generazione etichette AI
Testa direttamente la catena: configurazione → client → generazione
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from app.models import MLConfiguration, Project
from app.ml.api_client import MLAPIClient
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ai_workflow():
    """Test del workflow completo di generazione AI"""
    
    logger.info("🔍 Debug workflow generazione etichette AI")
    
    # Crea app context
    app = create_app()
    with app.app_context():
        
        # Step 1: Verifica configurazioni ML nel database
        logger.info("1️⃣ Verifica configurazioni ML...")
        
        project_id = "2efbcd28-f2ce-4f29-9819-f2079ff9fea3"
        ml_config = MLConfiguration.query.filter_by(
            project_id=project_id, 
            is_active=True
        ).first()
        
        if not ml_config:
            logger.error("❌ Nessuna configurazione ML attiva trovata")
            return False
        
        logger.info(f"✅ Configurazione trovata: {ml_config.name}")
        logger.info(f"   Provider: {ml_config.ml_provider}")
        logger.info(f"   Model: {ml_config.ml_model}")
        logger.info(f"   API URL: {ml_config.api_url}")
        logger.info(f"   API Key presente: {'Sì' if ml_config.api_key_encrypted else 'No'}")
        
        if ml_config.api_key_encrypted:
            # Mostra parte dell'API key per debug (mascherata per sicurezza)
            api_key_preview = ml_config.api_key_encrypted[:10] + "..." if len(ml_config.api_key_encrypted) > 10 else ml_config.api_key_encrypted
            logger.info(f"   API Key preview: {api_key_preview}")
            
            # Verifica se sembra criptata o in chiaro
            if ml_config.api_key_encrypted.startswith(('sk-', 'or-')):
                logger.info("   💡 API Key sembra essere in chiaro (inizia con sk- o or-)")
                api_key_to_use = ml_config.api_key_encrypted
            else:
                logger.warning("   ⚠️ API Key potrebbe essere criptata")
                api_key_to_use = ml_config.api_key_encrypted  # Per ora testiamo comunque
        else:
            logger.error("❌ API Key mancante")
            return False
        
        # Step 2: Test diretto del MLAPIClient
        logger.info("2️⃣ Test diretto MLAPIClient...")
        
        try:
            client = MLAPIClient(
                provider=ml_config.ml_provider,
                api_key=api_key_to_use,
                api_url=ml_config.api_url,
                model=ml_config.ml_model
            )
            
            logger.info(f"   Client creato - Provider: {client.provider}")
            logger.info(f"   API URL: {client.api_url}")
            logger.info(f"   Model: {client.model}")
            
            # Test connessione
            logger.info("3️⃣ Test connessione API...")
            connection_result = client.test_connection()
            
            if connection_result.get('status') == 'success':
                logger.info("✅ Connessione API riuscita!")
                logger.info(f"   Response time: {connection_result.get('response_time', 'N/A')}s")
            else:
                logger.error(f"❌ Connessione API fallita: {connection_result.get('error', 'Errore sconosciuto')}")
                return False
            
            # Step 4: Test generazione etichette
            logger.info("4️⃣ Test generazione etichette...")
            
            # Dati di esempio per test
            sample_data = [
                "Prodotto ottimo, molto soddisfatto",
                "Servizio pessimo, non lo consiglio",
                "Qualità nella media, prezzo giusto",
                "Eccellente esperienza di acquisto",
                "Problemi con la consegna, ma prodotto ok"
            ]
            
            # Usa il metodo analyze_text come nel codice di labeling.py
            test_prompt = """
Sei un esperto analista di sentiment. Analizza il testo e classifica il sentiment.

Analizza questi dati della colonna "feedback" e genera etichette per sentiment:

- Prodotto ottimo, molto soddisfatto
- Servizio pessimo, non lo consiglio  
- Qualità nella media, prezzo giusto
- Eccellente esperienza di acquisto
- Problemi con la consegna, ma prodotto ok

Genera etichette JSON con name, description, category, color.
"""
            
            ai_response = client.analyze_text(
                prompt=test_prompt,
                analysis_type='categorization',
                return_json=True
            )
            
            logger.info(f"   Risposta AI ricevuta: {ai_response.get('success', False)}")
            
            if ai_response.get('success'):
                logger.info("✅ Generazione etichette AI riuscita!")
                
                analysis_data = ai_response.get('analysis', {})
                logger.info(f"   Tipo analysis: {type(analysis_data)}")
                
                if isinstance(analysis_data, dict):
                    logger.info(f"   Chiavi analysis: {list(analysis_data.keys())}")
                    
                    # Cerca etichette nella risposta
                    if 'categories' in analysis_data:
                        categories = analysis_data.get('categories', [])
                        logger.info(f"   ✅ Trovate {len(categories)} categorie")
                        for i, cat in enumerate(categories[:3]):  # Mostra prime 3
                            logger.info(f"      {i+1}. {cat}")
                    elif 'labels' in analysis_data:
                        labels = analysis_data.get('labels', [])
                        logger.info(f"   ✅ Trovate {len(labels)} etichette")
                        for i, label in enumerate(labels[:3]):  # Mostra prime 3
                            logger.info(f"      {i+1}. {label}")
                    else:
                        logger.warning(f"   ⚠️ Formato risposta inaspettato: {analysis_data}")
                else:
                    logger.warning(f"   ⚠️ Analysis non è dict: {analysis_data}")
                
                return True
            else:
                logger.error(f"❌ Generazione etichette fallita: {ai_response.get('error', 'Errore sconosciuto')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Errore durante test workflow: {str(e)}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
            return False

if __name__ == "__main__":
    try:
        success = test_ai_workflow()
        if success:
            logger.info("🎉 Workflow AI completamente funzionante!")
        else:
            logger.error("❌ Workflow AI presenta problemi")
    except Exception as e:
        logger.error(f"❌ Errore critico: {e}")