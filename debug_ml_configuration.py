#!/usr/bin/env python3
"""
Script per verificare le configurazioni ML e testare la connessione
"""

import os
import sys
sys.path.append('.')

from app.database import db
from app.models import MLConfiguration, Project, User
from app.ml.api_client import MLAPIClient
import logging

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_ml_configuration():
    """Debug delle configurazioni ML"""
    try:
        from run import app
        with app.app_context():
            logger.info("🔍 Debug configurazioni ML...")
            
            # Controlla utenti
            users = User.query.all()
            logger.info(f"👥 Utenti totali: {len(users)}")
            
            # Controlla progetti
            projects = Project.query.all()
            logger.info(f"📂 Progetti totali: {len(projects)}")
            
            # Controlla configurazioni ML
            ml_configs = MLConfiguration.query.all()
            logger.info(f"⚙️ Configurazioni ML totali: {len(ml_configs)}")
            
            # Configurazioni attive
            active_configs = MLConfiguration.query.filter_by(is_active=True).all()
            logger.info(f"✅ Configurazioni ML attive: {len(active_configs)}")
            
            for config in active_configs:
                logger.info(f"  - Config: {config.name}")
                logger.info(f"    Provider: {config.ml_provider}")
                logger.info(f"    Model: {config.ml_model}")
                logger.info(f"    API URL: {config.api_url}")
                logger.info(f"    Progetto: {config.project.name}")
                logger.info(f"    API Key presente: {'Sì' if config.api_key_encrypted else 'No'}")
            
            # Controlla variabili d'ambiente
            logger.info("\n🌍 Variabili d'ambiente:")
            logger.info(f"  OPENROUTER_API_KEY: {'Configurata' if os.getenv('OPENROUTER_API_KEY') and os.getenv('OPENROUTER_API_KEY') != 'your-openrouter-api-key' else 'Non configurata'}")
            logger.info(f"  OPENAI_API_KEY: {'Configurata' if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your-openai-api-key' else 'Non configurata'}")
            
            # Test connessione base
            logger.info("\n🧪 Test connessione API Client...")
            try:
                # Test con parametri di default
                client = MLAPIClient()
                logger.info(f"  Provider: {client.provider}")
                logger.info(f"  Model: {client.model}")
                logger.info(f"  API URL: {client.api_url}")
                logger.info(f"  API Key presente: {'Sì' if client.api_key and client.api_key != 'your-openrouter-api-key' else 'No'}")
                
                # Test connessione
                if client.api_key and client.api_key != 'your-openrouter-api-key':
                    test_result = client.test_connection()
                    logger.info(f"  Test connessione: {test_result}")
                else:
                    logger.warning("  ⚠️ Impossibile testare connessione: API key non configurata")
                    
            except Exception as e:
                logger.error(f"  ❌ Errore nel test client: {str(e)}")
            
            # Suggerimenti
            logger.info("\n💡 Suggerimenti:")
            if len(active_configs) == 0:
                logger.info("  1. Crea una configurazione ML attiva nel progetto")
                logger.info("  2. Configura le API key nel database o nel file .env")
            elif not os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENROUTER_API_KEY') == 'your-openrouter-api-key':
                logger.info("  1. Configura OPENROUTER_API_KEY nel file .env")
                logger.info("  2. Oppure inserisci la API key nella configurazione ML del database")
            
            # Test specifico per progetto
            if projects:
                project = projects[0]
                logger.info(f"\n🎯 Test specifico per progetto: {project.name}")
                
                # Cerca configurazione ML per questo progetto
                project_config = MLConfiguration.query.filter_by(
                    project_id=project.id, 
                    is_active=True
                ).first()
                
                if project_config:
                    logger.info(f"  ✅ Configurazione ML trovata: {project_config.name}")
                    
                    # Test con questa configurazione
                    try:
                        test_client = MLAPIClient(
                            provider=project_config.ml_provider,
                            api_key=project_config.api_key_encrypted,
                            api_url=project_config.api_url,
                            model=project_config.ml_model
                        )
                        
                        # Test semplice
                        test_response = test_client.analyze_text(
                            "Test di connessione",
                            analysis_type='general',
                            return_json=False
                        )
                        logger.info(f"  ✅ Test riuscito: {test_response.get('success', False)}")
                        
                    except Exception as e:
                        logger.error(f"  ❌ Errore nel test con configurazione progetto: {str(e)}")
                        
                else:
                    logger.warning(f"  ⚠️ Nessuna configurazione ML attiva per il progetto {project.name}")
                    
    except Exception as e:
        logger.error(f"❌ Errore durante il debug: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ml_configuration()