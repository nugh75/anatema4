#!/usr/bin/env python3
"""
Test semplificato per verificare che il fix funzioni
"""

import sys
import os

# Aggiungi il path dell'app
sys.path.insert(0, '/home/nugh75/Git/anatema2')

from app import create_app
from app.database import db
from app.models import Project, ExcelSheet, User
from app.models import AutoLabel, AutoLabelApplication, MLAnalysis

def test_direct_db():
    """Test diretto del database"""
    print("🔍 Test diretto del database...")
    
    app = create_app()
    
    with app.app_context():
        # Trova un utente
        user = User.query.filter_by(username='daniele-d').first()
        if not user:
            print("❌ Utente daniele-d non trovato")
            return False
        
        print(f"✅ Utente trovato: {user.username} (ID: {user.id})")
        
        # Trova un progetto dell'utente
        project = Project.query.filter_by(owner_id=user.id).first()
        if not project:
            print("❌ Nessun progetto trovato per l'utente")
            return False
            
        print(f"✅ Progetto trovato: {project.name} (ID: {project.id})")
        
        # Trova un sheet
        sheet = ExcelSheet.query.join(File).filter(File.project_id == project.id).first()
        if not sheet:
            print("❌ Nessun sheet trovato")
            return False
            
        print(f"✅ Sheet trovato: {sheet.name} (ID: {sheet.id})")
        
        # Test creazione AutoLabel
        try:
            # Crea un'analisi ML
            ml_analysis = MLAnalysis(
                project_id=project.id,
                file_id=sheet.file_id,
                sheet_id=sheet.id,
                ml_provider='manual',
                ml_model='manual_labeling',
                analysis_type='manual_labeling',
                status='completed',
                results={'manual_labeling_session': True},
                processing_time=0.0
            )
            db.session.add(ml_analysis)
            db.session.flush()
            
            print(f"✅ MLAnalysis creata: {ml_analysis.id}")
            
            # Test creazione AutoLabel
            auto_label = AutoLabel(
                ml_analysis_id=ml_analysis.id,
                label_name='Test Label Fixed',
                label_description='Test Description',
                category='manual',  # Questo è il parametro corretto, non 'label_category'
                confidence_score=1.0
            )
            db.session.add(auto_label)
            db.session.flush()
            
            print(f"✅ AutoLabel creata: {auto_label.id}")
            
            # Test creazione AutoLabelApplication
            label_app = AutoLabelApplication(
                auto_label_id=auto_label.id,
                row_index=0,
                column_name='Test Column',
                confidence_score=1.0,
                status='applied'
            )
            db.session.add(label_app)
            db.session.commit()
            
            print(f"✅ AutoLabelApplication creata: {label_app.id}")
            print("🎉 Tutti i test del database sono passati!")
            return True
            
        except Exception as e:
            print(f"❌ Errore nella creazione: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    test_direct_db()
