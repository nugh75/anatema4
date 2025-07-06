#!/usr/bin/env python3
"""
Script per trovare progetti e fogli validi nel database
"""

import sys
import os

# Aggiungi il path del progetto
sys.path.append('/home/nugh75/Git/anatema2')

from app import create_app
from app.models import Project, ExcelSheet, File, User
from app.database import db

def find_valid_project_and_sheet():
    """Trova un progetto e foglio validi per il test"""
    
    app = create_app()
    
    with app.app_context():
        # Trova l'utente daniele.d
        user = User.query.filter_by(email='daniele.d@example.com').first()
        if not user:
            print("❌ Utente daniele.d@example.com non trovato")
            return None, None
        
        print(f"✅ Utente trovato: {user.email} (ID: {user.id})")
        
        # Trova progetti dell'utente
        projects = Project.query.filter_by(owner_id=user.id).all()
        print(f"📁 Progetti trovati: {len(projects)}")
        
        for project in projects:
            print(f"   - {project.name} (ID: {project.id})")
            
            # Trova fogli Excel per questo progetto
            sheets = ExcelSheet.query.join(File).filter(
                File.project_id == project.id
            ).all()
            
            print(f"     📊 Fogli Excel: {len(sheets)}")
            for sheet in sheets:
                print(f"        - {sheet.name} (ID: {sheet.id})")
                
                if sheets:  # Se abbiamo almeno un foglio, usiamo questo progetto
                    return project.id, sheets[0].id
        
        print("❌ Nessun progetto con fogli Excel trovato")
        return None, None

if __name__ == "__main__":
    project_id, sheet_id = find_valid_project_and_sheet()
    
    if project_id and sheet_id:
        print(f"\n🎯 Progetto e foglio da usare per il test:")
        print(f"   Project ID: {project_id}")
        print(f"   Sheet ID: {sheet_id}")
    else:
        print("\n❌ Nessun progetto/foglio valido trovato")
