# Script di Analisi Utilizzo Tabelle Etichette

import os
import sys
from sqlalchemy import text
sys.path.append('/home/nugh75/Git/anatema2')

# Configurazione Flask app
from flask import Flask
from config.config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Inizializzazione database
from app.database import db
db.init_app(app)

# Import modelli
from app.models import CellLabel, AutoLabelApplication
from app.models_labeling import LabelApplication

def analyze_table_usage():
    """Analizza l'utilizzo effettivo delle tabelle etichette"""
    
    with app.app_context():
        print("=== ANALISI UTILIZZO TABELLE ETICHETTE ===\n")
        
        try:
            # 1. CellLabel (Sistema Legacy)
            cell_label_count = CellLabel.query.count()
            print(f"📊 CellLabel (Legacy): {cell_label_count} record")
            
            if cell_label_count > 0:
                recent_cell_labels = CellLabel.query.order_by(CellLabel.created_at.desc()).limit(3).all()
                print("   Esempi recenti:")
                for cl in recent_cell_labels:
                    print(f"   - ID: {cl.id}, Label: {cl.label_id}, Row: {cl.row_id}, Col: {cl.column_index}")
            
            # 2. AutoLabelApplication (Sistema ML Legacy)
            auto_app_count = AutoLabelApplication.query.count()
            print(f"\n📊 AutoLabelApplication (ML Legacy): {auto_app_count} record")
            
            if auto_app_count > 0:
                recent_auto_apps = AutoLabelApplication.query.order_by(AutoLabelApplication.applied_at.desc()).limit(3).all()
                print("   Esempi recenti:")
                for aa in recent_auto_apps:
                    print(f"   - ID: {aa.id}, AutoLabel: {aa.auto_label_id}, Row: {aa.row_index}, Col: {aa.column_name}, Status: {aa.status}")
            
            # 3. LabelApplication (Sistema Nuovo)
            label_app_count = LabelApplication.query.count()
            print(f"\n📊 LabelApplication (Nuovo Sistema): {label_app_count} record")
            
            if label_app_count > 0:
                recent_label_apps = LabelApplication.query.order_by(LabelApplication.applied_at.desc()).limit(3).all()
                print("   Esempi recenti:")
                for la in recent_label_apps:
                    print(f"   - ID: {la.id}, Label: {la.label_id}, Row: {la.row_index}, Col: {la.column_name}, Type: {la.application_type}")
            
            # 4. Analisi sovrapposizioni
            print(f"\n🔍 ANALISI SOVRAPPOSIZIONI:")
            print(f"   Totale applicazioni etichette: {cell_label_count + auto_app_count + label_app_count}")
            
            # Verifica se ci sono dati in progetti attivi
            active_projects_query = text("""
                SELECT COUNT(DISTINCT p.id) 
                FROM projects p 
                WHERE p.is_active = true
            """)
            active_projects = db.session.execute(active_projects_query).scalar()
            print(f"   Progetti attivi: {active_projects}")
            
            # Controllo integrità referenziale
            print(f"\n🔧 CONTROLLO INTEGRITÀ:")
            
            # CellLabel con riferimenti validi
            valid_cell_labels = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM cell_labels cl 
                JOIN excel_rows er ON cl.row_id = er.id 
                JOIN labels l ON cl.label_id = l.id
            """)).scalar()
            print(f"   CellLabel con riferimenti validi: {valid_cell_labels}/{cell_label_count}")
            
            # AutoLabelApplication con riferimenti validi
            valid_auto_apps = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM auto_label_applications ala 
                JOIN auto_labels al ON ala.auto_label_id = al.id
            """)).scalar()
            print(f"   AutoLabelApplication con riferimenti validi: {valid_auto_apps}/{auto_app_count}")
            
            # LabelApplication con riferimenti validi
            valid_label_apps = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM label_applications la 
                JOIN labels l ON la.label_id = l.id 
                JOIN projects p ON la.project_id = p.id
            """)).scalar()
            print(f"   LabelApplication con riferimenti validi: {valid_label_apps}/{label_app_count}")
            
            print(f"\n✅ RACCOMANDAZIONE:")
            if label_app_count > 0:
                print("   - LabelApplication è il sistema più moderno e dovrebbe essere usato")
                print("   - Migrare i dati da CellLabel e AutoLabelApplication")
            elif auto_app_count > 0:
                print("   - Il sistema ML usa AutoLabelApplication")
                print("   - Considerare migrazione a LabelApplication per unificare")
            elif cell_label_count > 0:
                print("   - Solo sistema legacy attivo (CellLabel)")
                print("   - Upgrade urgente a LabelApplication")
            else:
                print("   - Nessuna etichetta applicata - perfetto per iniziare con LabelApplication")
            
        except Exception as e:
            print(f"❌ Errore durante l'analisi: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    analyze_table_usage()
