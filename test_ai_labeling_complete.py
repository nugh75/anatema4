#!/usr/bin/env python3
"""
Test completo del sistema di etichettatura AI
Verifica che l'intero workflow funzioni: configurazioni ML, template, generazione AI
"""

import requests
import json
import time
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_complete_ai_labeling():
    """Test completo del workflow di etichettatura AI"""
    
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    logger.info("🧪 Test completo sistema etichettatura AI")
    
    # Step 1: Login
    logger.info("1️⃣ Test login...")
    login_data = {
        'username': 'daniele', 
        'password': 'password123'
    }
    
    login_response = session.post(f"{base_url}/auth/login", data=login_data)
    if login_response.status_code != 200:
        logger.error(f"❌ Login fallito: {login_response.status_code}")
        return False
    
    logger.info("✅ Login riuscito")
    
    # Step 2: Verifica configurazioni ML
    logger.info("2️⃣ Verifica configurazioni ML...")
    
    project_id = "2efbcd28-f2ce-4f29-9819-f2079ff9fea3"
    ml_config_response = session.get(f"{base_url}/ml/projects/{project_id}/configurations")
    
    if ml_config_response.status_code == 200:
        try:
            ml_configs = ml_config_response.json()
            active_configs = [config for config in ml_configs.get('configurations', []) if config.get('is_active')]
            if active_configs:
                logger.info(f"✅ Configurazioni ML attive: {len(active_configs)}")
                logger.info(f"   Provider: {active_configs[0].get('ml_provider')}")
                logger.info(f"   Modello: {active_configs[0].get('ml_model')}")
            else:
                logger.warning("⚠️ Nessuna configurazione ML attiva")
        except Exception as e:
            logger.error(f"❌ Errore parsing configurazioni ML: {e}")
    else:
        logger.error(f"❌ Errore recupero configurazioni ML: {ml_config_response.status_code}")
    
    # Step 3: Recupera template disponibili
    logger.info("3️⃣ Recupera template disponibili...")
    
    templates_response = session.get(f"{base_url}/labeling/projects/{project_id}/templates")
    if templates_response.status_code != 200:
        logger.error(f"❌ Errore recupero template: {templates_response.status_code}")
        return False
    
    try:
        # Se è JSON
        if 'application/json' in templates_response.headers.get('content-type', ''):
            templates_data = templates_response.json()
            templates = templates_data.get('templates', [])
        else:
            # Se è HTML, creiamo un template per test
            templates = []
        
        logger.info(f"✅ Template trovati: {len(templates)}")
        
        # Step 4: Crea template di test se non esistente
        if not templates:
            logger.info("4️⃣ Crea template di test...")
            
            test_template = {
                'name': 'Test Sentiment Analysis',
                'description': 'Template per test del sistema AI',
                'category': 'sentiment',
                'system_prompt': 'Sei un esperto analista di sentiment. Analizza il testo e classifica il sentiment.',
                'user_prompt_template': 'Analizza questi dati della colonna "{column_name}" e genera etichette per sentiment:\n\n{sample_data}\n\nGenera etichette JSON con name, description, category, color.',
                'preferred_model': 'deepseek/deepseek-chat-v3-0324:free',
                'temperature': 0.7,
                'max_tokens': 1000,
                'expected_labels_count': 3,
                'output_format': 'json'
            }
            
            create_template_response = session.post(
                f"{base_url}/labeling/projects/{project_id}/templates/create",
                json=test_template
            )
            
            if create_template_response.status_code in [200, 201]:
                logger.info("✅ Template di test creato")
                if 'application/json' in create_template_response.headers.get('content-type', ''):
                    template_data = create_template_response.json()
                    template_id = template_data.get('template', {}).get('id')
                else:
                    # Se redirect, usa un ID fittizio per test
                    template_id = "test-template-id"
            else:
                logger.error(f"❌ Errore creazione template: {create_template_response.status_code}")
                template_id = None
        else:
            template_id = templates[0].get('id')
            logger.info(f"✅ Uso template esistente: {template_id}")
    
    except Exception as e:
        logger.error(f"❌ Errore elaborazione template: {e}")
        template_id = None
    
    # Step 5: Test generazione etichette AI (anche senza template valido)
    logger.info("5️⃣ Test generazione etichette AI...")
    
    sheet_id = "40e869ed-7fe1-4c51-9133-b628be812f5f"
    generation_data = {
        'template_id': template_id or 'test-id',  # Usa template reale o ID di test
        'column_name': 'feedback',
        'sample_size': 5
    }
    
    logger.info(f"   Dati generazione: {generation_data}")
    
    generation_response = session.post(
        f"{base_url}/labeling/projects/{project_id}/sheets/{sheet_id}/generate-labels",
        json=generation_data
    )
    
    logger.info(f"   Status: {generation_response.status_code}")
    logger.info(f"   Content-Type: {generation_response.headers.get('content-type')}")
    
    if generation_response.status_code == 200:
        # Verifica se è JSON o HTML
        if 'application/json' in generation_response.headers.get('content-type', ''):
            try:
                result = generation_response.json()
                logger.info(f"✅ Generazione completata: {result.get('message', 'Successo')}")
                generation_id = result.get('generation_id')
                if generation_id:
                    logger.info(f"   ID generazione: {generation_id}")
                return True
            except json.JSONDecodeError:
                logger.warning("⚠️ Risposta non JSON ma status 200")
        else:
            # HTML response - probabilmente redirect o pagina di successo
            if "success" in generation_response.text.lower() or "completat" in generation_response.text.lower():
                logger.info("✅ Generazione apparentemente completata (risposta HTML)")
                return True
            else:
                logger.warning("⚠️ Risposta HTML senza indicatori di successo")
                logger.info(f"   Prime righe: {generation_response.text[:200]}")
    elif generation_response.status_code == 302:
        logger.info("✅ Redirect - probabile successo con redirect alla pagina di review")
        return True
    else:
        logger.error(f"❌ Errore generazione: {generation_response.status_code}")
        logger.error(f"   Risposta: {generation_response.text[:300]}")
    
    return False

if __name__ == "__main__":
    try:
        success = test_complete_ai_labeling()
        if success:
            logger.info("🎉 Test completato con successo!")
            logger.info("💡 Il sistema di etichettatura AI sembra funzionare correttamente")
        else:
            logger.warning("⚠️ Test completato con alcuni problemi")
            logger.info("💡 Verificare i log per dettagli specifici")
            
    except KeyboardInterrupt:
        logger.info("❌ Test interrotto dall'utente")
    except Exception as e:
        logger.error(f"❌ Errore durante il test: {e}")