#!/usr/bin/env python3
"""
Script per correggere le configurazioni ML
"""

import os
import sys
sys.path.append('.')

from app.database import db
from app.models import MLConfiguration, Project, User
import logging

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_ml_configuration():
    """Corregge le configurazioni ML"""
    try:
        from run import app
        with app.app_context():
            logger.info("🔧 Correzione configurazioni ML...")
            
            # Trova tutte le configurazioni
            configs = MLConfiguration.query.all()
            logger.info(f"⚙️ Configurazioni trovate: {len(configs)}")
            
            for config in configs:
                logger.info(f"  - Config: {config.name} (Project: {config.project.name})")
                
                # Correggi API URL se vuoto
                if not config.api_url and config.ml_provider == 'openrouter':
                    config.api_url = 'https://openrouter.ai/api/v1'
                    logger.info(f"    ✅ Corretto API URL: {config.api_url}")
                
                # Verifica modello
                if config.ml_model:
                    logger.info(f"    ✅ Modello: {config.ml_model}")
                
                # Verifica API key
                if config.api_key_encrypted:
                    logger.info(f"    ✅ API Key presente")
                else:
                    logger.warning(f"    ⚠️ API Key mancante")
            
            # Trova tutti i progetti
            projects = Project.query.all()
            logger.info(f"\n📂 Progetti trovati: {len(projects)}")
            
            for project in projects:
                logger.info(f"  - Progetto: {project.name} (ID: {project.id})")
                
                # Verifica se ha configurazione ML attiva
                project_config = MLConfiguration.query.filter_by(
                    project_id=project.id, 
                    is_active=True
                ).first()
                
                if project_config:
                    logger.info(f"    ✅ Ha configurazione ML attiva: {project_config.name}")
                else:
                    logger.warning(f"    ⚠️ Nessuna configurazione ML attiva")
                    
                    # Cerca configurazione disponibile per copiare
                    available_config = MLConfiguration.query.filter_by(is_active=True).first()
                    if available_config:
                        logger.info(f"    💡 Creo configurazione ML per questo progetto...")
                        
                        # Trova il proprietario del progetto
                        owner = project.owner
                        
                        # Crea nuova configurazione per questo progetto
                        new_config = MLConfiguration(
                            project_id=project.id,
                            created_by=owner.id,
                            name=f"openrouter-{project.name.lower().replace(' ', '-')}",
                            description=f"Configurazione ML per progetto {project.name}",
                            ml_provider=available_config.ml_provider,
                            ml_model=available_config.ml_model,
                            api_key_encrypted=available_config.api_key_encrypted,
                            api_url=available_config.api_url or 'https://openrouter.ai/api/v1',
                            is_active=True
                        )
                        
                        db.session.add(new_config)
                        logger.info(f"    ✅ Configurazione creata: {new_config.name}")
            
            # Salva modifiche
            db.session.commit()
            logger.info("\n💾 Modifiche salvate!")
            
            # Verifica finale
            logger.info("\n🔍 Verifica finale...")
            active_configs = MLConfiguration.query.filter_by(is_active=True).all()
            logger.info(f"✅ Configurazioni ML attive totali: {len(active_configs)}")
            
            for config in active_configs:
                logger.info(f"  - {config.name} (Project: {config.project.name})")
                logger.info(f"    Provider: {config.ml_provider}")
                logger.info(f"    Model: {config.ml_model}")
                logger.info(f"    API URL: {config.api_url}")
                logger.info(f"    API Key: {'✅' if config.api_key_encrypted else '❌'}")
                
    except Exception as e:
        logger.error(f"❌ Errore durante la correzione: {str(e)}")
        db.session.rollback()
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_ml_configuration()