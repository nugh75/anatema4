#!/usr/bin/env python3
"""
Script per testare l'API del sistema di etichettatura con dati reali.
"""

import os
import sys
sys.path.append('.')

from app.database import db
from app.models import User, Project, File, ExcelSheet
import logging

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_labeling_api():
    """Testa l'API del sistema di etichettatura"""
    try:
        from run import app
        with app.app_context():
            logger.info("🧪 Test API sistema di etichettatura...")
            
            # Trova il progetto con file Excel
            project_with_files = Project.query.join(File).filter(
                File.file_type.in_(['xlsx', 'xls'])
            ).first()
            
            if not project_with_files:
                logger.error("❌ Nessun progetto con file Excel trovato!")
                return
            
            logger.info(f"📂 Test progetto: {project_with_files.name} (ID: {project_with_files.id})")
            
            # Test query corretta per API
            sheets = ExcelSheet.query.join(File).filter(
                File.project_id == project_with_files.id
            ).all()
            
            logger.info(f"📊 Fogli trovati: {len(sheets)}")
            
            if sheets:
                logger.info("✅ Query API funziona correttamente!")
                for sheet in sheets:
                    logger.info(f"  - Foglio: {sheet.name}")
                    logger.info(f"    File: {sheet.file.original_name}")
                    logger.info(f"    Righe: {sheet.row_count}, Colonne: {sheet.column_count}")
                    
                    # Simula risposta API
                    api_response = {
                        'id': str(sheet.id),
                        'name': sheet.name,
                        'sheet_index': sheet.sheet_index,
                        'row_count': sheet.row_count,
                        'column_count': sheet.column_count,
                        'file': {
                            'id': str(sheet.file.id),
                            'filename': sheet.file.filename,
                            'original_name': sheet.file.original_name,
                            'uploaded_at': sheet.file.uploaded_at.isoformat() if sheet.file.uploaded_at else None
                        }
                    }
                    logger.info(f"    📡 Risposta API simulata: {api_response}")
                
                logger.info("\n🎉 Il sistema di etichettatura dovrebbe funzionare correttamente!")
                logger.info(f"💡 Prova ad accedere con l'utente '{project_with_files.owner.username}' e seleziona il progetto '{project_with_files.name}'")
                
            else:
                logger.error("❌ Query API non restituisce fogli!")
                
            # Test anche la chiamata diretta all'endpoint API
            logger.info(f"\n🔧 Test endpoint API diretto...")
            
            from app.views.api import get_project_sheets
            from flask import Flask
            from unittest.mock import Mock
            
            # Simula una richiesta con l'utente corretto
            with app.test_request_context():
                # Mock dell'utente autenticato
                import app.views.api as api_module
                
                # Backup della funzione originale
                original_get_current_api_user = api_module.get_current_api_user
                
                # Mock per restituire l'owner del progetto
                api_module.get_current_api_user = lambda: project_with_files.owner
                
                try:
                    response = get_project_sheets(project_with_files.id)
                    if hasattr(response, 'get_json'):
                        data = response.get_json()
                        logger.info(f"📡 Risposta endpoint API: {len(data.get('sheets', []))} fogli")
                        if data.get('sheets'):
                            logger.info("✅ Endpoint API funziona correttamente!")
                        else:
                            logger.error("❌ Endpoint API non restituisce fogli!")
                    else:
                        logger.info(f"📡 Risposta endpoint API (raw): {response}")
                        
                finally:
                    # Ripristina la funzione originale
                    api_module.get_current_api_user = original_get_current_api_user
                
    except Exception as e:
        logger.error(f"❌ Errore durante il test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_labeling_api()