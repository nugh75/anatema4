#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import MLConfiguration, LabelTemplate
from app.ml.api_client import MLAPIClient
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ai_response_format():
    """Test della struttura di risposta AI per il debugging"""
    logger.info("🔍 Test struttura risposta AI per generazione etichette")
    
    with create_app().app_context():
        # 1. Recupera configurazione ML
        ml_config = MLConfiguration.query.filter_by(is_active=True).first()
        if not ml_config:
            logger.error("❌ Nessuna configurazione ML attiva trovata")
            return False
            
        logger.info(f"✅ Configurazione ML: {ml_config.ml_provider} - {ml_config.ml_model}")
        
        # 2. Crea client
        client = MLAPIClient(
            provider=ml_config.ml_provider,
            api_key=ml_config.api_key_encrypted,
            api_url=ml_config.api_url,
            model=ml_config.ml_model
        )
        
        # 3. Simula un template predefinito
        test_template = {
            'system_prompt': 'Sei un esperto analista di sentiment. Analizza il testo e classifica il sentiment in modo accurato.',
            'user_prompt_template': 'Analizza i seguenti dati della colonna "{column_name}" e genera 3-4 etichette per classificare il sentiment:\n\n{sample_data}\n\nGenera etichette chiare come: Positivo, Negativo, Neutro, Misto.\nRispondi in formato JSON con: name, description, category, color.',
            'category': 'sentiment'
        }
        
        # 4. Dati di test
        sample_data = [
            "Sono molto soddisfatto del servizio ricevuto",
            "Il prodotto non ha soddisfatto le mie aspettative",
            "Tutto ok, niente di speciale",
            "Esperienza fantastica, lo consiglio a tutti",
            "Servizio pessimo, non tornerò mai più"
        ]
        
        # 5. Costruisci prompt esatto come nel sistema
        sample_text = '\n'.join([f"- {str(item)}" for item in sample_data])
        user_prompt = test_template['user_prompt_template'].format(
            column_name="feedback_clienti",
            sample_data=sample_text
        )
        
        full_prompt = f"""
{test_template['system_prompt']}

{user_prompt}
"""
        
        logger.info("📝 Prompt completo:")
        logger.info("=" * 50)
        logger.info(full_prompt)
        logger.info("=" * 50)
        
        # 6. Test della chiamata AI
        logger.info("🤖 Chiamata AI in corso...")
        response = client.analyze_text(
            prompt=full_prompt,
            analysis_type='categorization',
            return_json=True
        )
        
        logger.info(f"✅ Risposta AI ricevuta - Success: {response.get('success', False)}")
        
        if response.get('success', False):
            analysis = response.get('analysis', {})
            logger.info("📊 Struttura risposta AI:")
            logger.info(f"   Tipo analysis: {type(analysis)}")
            
            if isinstance(analysis, dict):
                logger.info(f"   Chiavi disponibili: {list(analysis.keys())}")
                for key, value in analysis.items():
                    logger.info(f"   - {key}: {type(value)} = {value}")
            else:
                logger.info(f"   Contenuto: {analysis}")
            
            # 7. Simula il parsing del sistema attuale
            logger.info("\n🔍 Test parsing sistema attuale:")
            
            # Parsing come nel sistema
            analysis_data = analysis
            if isinstance(analysis_data, str):
                try:
                    import json
                    analysis_data = json.loads(analysis_data)
                    logger.info("   ✅ JSON parsing riuscito")
                except json.JSONDecodeError:
                    logger.error("   ❌ JSON parsing fallito")
                    analysis_data = {}
            
            suggestions_list = []
            
            # Test formato 'categories'
            if 'categories' in analysis_data:
                logger.info("   ✅ Trovato formato 'categories'")
                categories = analysis_data.get('categories', [])
                for category in categories:
                    logger.info(f"      Categoria: {category}")
            else:
                logger.info("   ❌ Formato 'categories' NON trovato")
            
            # Test formato 'labels'
            if 'labels' in analysis_data:
                logger.info("   ✅ Trovato formato 'labels'")
                labels = analysis_data.get('labels', [])
                for label in labels:
                    logger.info(f"      Label: {label}")
            else:
                logger.info("   ❌ Formato 'labels' NON trovato")
            
            # Test altri possibili formati
            possible_keys = ['etichette', 'sentiment_labels', 'classifications', 'results']
            for key in possible_keys:
                if key in analysis_data:
                    logger.info(f"   ✅ Trovato formato alternativo '{key}': {analysis_data[key]}")
            
            return True
        else:
            logger.error(f"❌ Errore AI: {response.get('error', 'Sconosciuto')}")
            return False

if __name__ == "__main__":
    success = test_ai_response_format()
    if success:
        print("\n✅ Test completato - Analizza i log per identificare il problema nel parsing")
    else:
        print("\n❌ Test fallito")