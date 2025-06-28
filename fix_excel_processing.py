#!/usr/bin/env python3
"""
Script per riprocessare i file Excel esistenti nel sistema di etichettatura.
Trova tutti i file Excel senza record ExcelSheet e li processa.
"""

import os
import sys
sys.path.append('.')

from app.database import db
from app.models import File, ExcelSheet
from app.views.files import process_excel_file
import logging

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_unprocessed_excel_files():
    """Trova tutti i file Excel che non hanno fogli associati"""
    excel_files = File.query.filter(
        File.file_type.in_(['xlsx', 'xls'])
    ).all()
    
    unprocessed = []
    for file in excel_files:
        sheet_count = ExcelSheet.query.filter_by(file_id=file.id).count()
        if sheet_count == 0:
            unprocessed.append(file)
    
    return unprocessed

def reprocess_excel_file(file_record):
    """Riprocessa un singolo file Excel"""
    try:
        file_path = file_record.get_file_path()
        
        if not os.path.exists(file_path):
            logger.error(f"File fisico non trovato: {file_path}")
            return False
        
        logger.info(f"Processando file: {file_record.original_name} (ID: {file_record.id})")
        
        # Elimina eventuali fogli esistenti
        ExcelSheet.query.filter_by(file_id=file_record.id).delete()
        db.session.commit()
        
        # Riprocessa il file
        file_record.processing_status = 'processing'
        db.session.commit()
        
        success = process_excel_file(file_path, file_record)
        
        if success:
            logger.info(f"✅ File processato con successo: {file_record.original_name}")
            return True
        else:
            logger.error(f"❌ Errore nel processamento: {file_record.original_name}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Eccezione durante il processamento di {file_record.original_name}: {str(e)}")
        db.session.rollback()
        return False

def main():
    """Funzione principale dello script"""
    try:
        from run import app
        with app.app_context():
            logger.info("🔍 Ricerca file Excel non processati...")
            
            unprocessed_files = find_unprocessed_excel_files()
            
            if not unprocessed_files:
                logger.info("✅ Tutti i file Excel sono già stati processati!")
                return
            
            logger.info(f"📋 Trovati {len(unprocessed_files)} file Excel da processare:")
            for file in unprocessed_files:
                logger.info(f"  - {file.original_name} (ID: {file.id})")
            
            print(f"\n🚀 Vuoi processare {len(unprocessed_files)} file Excel? (y/N): ", end="")
            response = input().strip().lower()
            
            if response != 'y':
                logger.info("❌ Operazione annullata dall'utente")
                return
            
            logger.info("🔧 Inizio processamento...")
            
            successful = 0
            failed = 0
            
            for file_record in unprocessed_files:
                if reprocess_excel_file(file_record):
                    successful += 1
                else:
                    failed += 1
            
            logger.info(f"\n📊 Riepilogo processamento:")
            logger.info(f"  ✅ Successi: {successful}")
            logger.info(f"  ❌ Fallimenti: {failed}")
            logger.info(f"  📋 Totale: {len(unprocessed_files)}")
            
            if successful > 0:
                logger.info("\n🎉 Processamento completato! I file Excel dovrebbero ora essere disponibili nel sistema di etichettatura.")
            
    except Exception as e:
        logger.error(f"❌ Errore generale: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)