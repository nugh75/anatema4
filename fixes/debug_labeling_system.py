#!/usr/bin/env python3
"""
Script diagnostico per il sistema di etichettatura.
Verifica presenza di progetti, file Excel e fogli.
"""

import os
import sys
sys.path.append('.')

from app.database import db
from app.models import User, Project, File, ExcelSheet, ExcelColumn
import logging

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def diagnose_system():
    """Diagnostica completa del sistema di etichettatura"""
    try:
        from run import app
        with app.app_context():
            logger.info("🔍 Diagnostica sistema di etichettatura...")
            
            # Verifica utenti
            users = User.query.all()
            logger.info(f"👥 Utenti totali: {len(users)}")
            for user in users:
                logger.info(f"  - {user.username} (ID: {user.id})")
            
            # Verifica progetti
            projects = Project.query.all()
            logger.info(f"📁 Progetti totali: {len(projects)}")
            
            if not projects:
                logger.warning("⚠️  Nessun progetto trovato! Crea un progetto per testare il sistema.")
                return
            
            for project in projects:
                logger.info(f"\n📂 Progetto: {project.name} (ID: {project.id})")
                logger.info(f"   Proprietario: {project.owner.username}")
                
                # File del progetto
                files = File.query.filter_by(project_id=project.id).all()
                logger.info(f"   📄 File: {len(files)}")
                
                for file in files:
                    logger.info(f"     - {file.original_name} ({file.file_type}) - Status: {file.processing_status}")
                    
                    # Se è un file Excel, verifica i fogli
                    if file.file_type in ['xlsx', 'xls']:
                        sheets = ExcelSheet.query.filter_by(file_id=file.id).all()
                        logger.info(f"       📊 Fogli Excel: {len(sheets)}")
                        
                        for sheet in sheets:
                            logger.info(f"         → {sheet.name} ({sheet.row_count} righe, {sheet.column_count} colonne)")
                            
                            # Verifica colonne
                            columns = ExcelColumn.query.filter_by(sheet_id=sheet.id).limit(5).all()
                            if columns:
                                col_names = [col.name for col in columns]
                                logger.info(f"           Colonne (prime 5): {col_names}")
                            
                            # Verifica se il file fisico esiste
                            file_path = file.get_file_path()
                            if os.path.exists(file_path):
                                logger.info(f"           ✅ File fisico esistente: {file_path}")
                            else:
                                logger.error(f"           ❌ File fisico mancante: {file_path}")
                
                # Verifica etichette del progetto
                from app.models import Label
                labels = Label.query.filter_by(project_id=project.id).all()
                logger.info(f"   🏷️  Etichette: {len(labels)}")
                for label in labels:
                    logger.info(f"     - {label.name}")
            
            # Test API endpoint
            logger.info(f"\n🔧 Test API per il primo progetto...")
            if projects:
                first_project = projects[0]
                
                # Simula chiamata API
                sheets = ExcelSheet.query.join(File).filter(
                    File.project_id == first_project.id
                ).all()
                
                logger.info(f"📊 Fogli trovati via API query: {len(sheets)}")
                for sheet in sheets:
                    logger.info(f"  - {sheet.name} (File: {sheet.file.original_name})")
                
                if sheets:
                    logger.info("✅ API query funziona correttamente!")
                else:
                    logger.error("❌ API query non restituisce fogli - problema nella query!")
            
            logger.info("\n🎯 Diagnostica completata!")
            
    except Exception as e:
        logger.error(f"❌ Errore durante la diagnostica: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_system()