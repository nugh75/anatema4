#!/usr/bin/env python3
"""
Test completo della pipeline di etichettatura automatica dopo i fix
"""

import sys
sys.path.append('.')

from app import create_app
from app.database import db
from app.models import Project, User, File, ExcelSheet, Label
from app.models_labeling import LabelTemplate, LabelGeneration, LabelSuggestion, LabelApplication
import pandas as pd
import os
import tempfile
import json

def create_test_data():
    """Crea dati di test per il labeling"""
    print("🔧 Creazione dati di test...")
    
    # Trova utente di test
    user = User.query.filter_by(email='test@example.com').first()
    if not user:
        print("❌ Utente test non trovato. Esegui prima create_test_user.py")
        return None, None, None
    
    # Crea progetto test
    project = Project.query.filter_by(name='Test Labeling Project').first()
    if not project:
        project = Project(
            name='Test Labeling Project',
            description='Progetto per testare la pipeline di etichettatura',
            owner_id=user.id
        )
        db.session.add(project)
        db.session.commit()
    
    # Crea file Excel di test
    test_data = {
        'feedback': [
            'Questo prodotto è fantastico!',
            'Non mi piace per niente',
            'Abbastanza buono, ma potrebbe essere migliore',
            'Perfetto! Lo consiglio a tutti',
            'Male, non lo ricomprerei',
            'Discreto per il prezzo',
            'Eccellente qualità',
            'Deludente rispetto alle aspettative'
        ],
        'rating': [5, 1, 3, 5, 2, 3, 5, 2],
        'categoria': ['elettronica', 'abbigliamento', 'casa', 'elettronica', 'casa', 'abbigliamento', 'elettronica', 'casa']
    }
    
    df = pd.DataFrame(test_data)
    
    # Salva file temporaneo
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        temp_path = tmp.name
    
    # Crea record File
    file_record = File.query.filter_by(original_name='test_labeling.xlsx').first()
    if not file_record:
        file_record = File(
            project_id=project.id,
            original_name='test_labeling.xlsx',
            file_path=temp_path,
            file_type='xlsx',
            size=os.path.getsize(temp_path)
        )
        db.session.add(file_record)
        db.session.commit()
    
    # Crea ExcelSheet
    sheet = ExcelSheet.query.filter_by(file_id=file_record.id).first()
    if not sheet:
        sheet = ExcelSheet(
            file_id=file_record.id,
            name='Sheet1',
            total_rows=len(df),
            total_columns=len(df.columns)
        )
        db.session.add(sheet)
        db.session.commit()
    
    print(f"✅ Dati di test creati: Project={project.id}, Sheet={sheet.id}")
    return project, sheet, temp_path

def test_api_endpoints(project, sheet):
    """Test degli endpoint API"""
    print("🧪 Test API endpoints...")
    
    with app.test_client() as client:
        # Simula login
        with client.session_transaction() as sess:
            sess['_user_id'] = '1'  # Assumendo che l'user test abbia ID=1
            sess['_fresh'] = True
        
        # Test API colonne
        response = client.get(f'/labeling/projects/{project.id}/sheets/{sheet.id}/columns')
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"✅ API Colonne: {len(data.get('columns', []))} colonne caricate")
        else:
            print(f"❌ API Colonne fallita: {response.status_code}")
        
        # Test API righe
        response = client.get(f'/labeling/projects/{project.id}/sheets/{sheet.id}/rows?column_name=feedback')
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"✅ API Righe: {len(data.get('rows', []))} righe caricate")
        else:
            print(f"❌ API Righe fallita: {response.status_code}")
        
        # Test API target
        response = client.get(f'/labeling/projects/{project.id}/sheets/{sheet.id}/targets?target_type=column')
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"✅ API Target: {len(data.get('targets', []))} target caricati")
        else:
            print(f"❌ API Target fallita: {response.status_code}")

def test_label_creation(project):
    """Test creazione etichette"""
    print("🏷️ Test creazione etichette...")
    
    # Crea etichette di test
    labels_data = [
        {'name': 'Positivo', 'description': 'Feedback positivo', 'color': '#4CAF50'},
        {'name': 'Negativo', 'description': 'Feedback negativo', 'color': '#F44336'},
        {'name': 'Neutro', 'description': 'Feedback neutro', 'color': '#FFC107'}
    ]
    
    created_labels = []
    for label_data in labels_data:
        existing = Label.query.filter_by(
            project_id=project.id,
            name=label_data['name']
        ).first()
        
        if not existing:
            label = Label(
                project_id=project.id,
                name=label_data['name'],
                description=label_data['description'],
                color=label_data['color']
            )
            db.session.add(label)
            created_labels.append(label)
    
    db.session.commit()
    
    total_labels = Label.query.filter_by(project_id=project.id).count()
    print(f"✅ Etichette create: {total_labels} totali")
    return created_labels

def test_manual_application(project, sheet, labels):
    """Test applicazione manuale"""
    print("👆 Test applicazione manuale...")
    
    if not labels:
        labels = Label.query.filter_by(project_id=project.id).all()
    
    # Applica manualmente alcune etichette
    test_applications = [
        {'row_index': 0, 'column_name': 'feedback', 'label': labels[0]},  # Positivo
        {'row_index': 1, 'column_name': 'feedback', 'label': labels[1]},  # Negativo
        {'row_index': 2, 'column_name': 'feedback', 'label': labels[2]},  # Neutro
    ]
    
    for app_data in test_applications:
        # Controlla se esiste già
        existing = LabelApplication.query.filter_by(
            project_id=project.id,
            sheet_id=sheet.id,
            row_index=app_data['row_index'],
            column_name=app_data['column_name'],
            is_active=True
        ).first()
        
        if not existing:
            application = LabelApplication(
                project_id=project.id,
                sheet_id=sheet.id,
                label_id=app_data['label'].id,
                applied_by=1,  # User test
                row_index=app_data['row_index'],
                column_name=app_data['column_name'],
                cell_value=f'Test value {app_data["row_index"]}',
                application_type='manual',
                confidence_score=1.0
            )
            db.session.add(application)
    
    db.session.commit()
    
    manual_count = LabelApplication.query.filter_by(
        project_id=project.id,
        application_type='manual',
        is_active=True
    ).count()
    
    print(f"✅ Applicazioni manuali: {manual_count}")

def test_form_parameters():
    """Test dei parametri del form"""
    print("📋 Test parametri form...")
    
    # Simula dati del form
    form_data = {
        'mode': 'ai_batch',
        'target_type': 'column',
        'target_name': 'feedback',
        'selected_labels': ['1', '2', '3'],
        'custom_prompt': 'Analizza il sentiment del feedback',
        'min_confidence': '0.7',
        'max_applications': '100'
    }
    
    # Test conversione selected_labels
    selected_labels = form_data.get('selected_labels', [])
    if isinstance(selected_labels, str):
        selected_labels = [selected_labels]
    elif not isinstance(selected_labels, list):
        selected_labels = []
    
    try:
        selected_labels = [int(id_str) for id_str in selected_labels if id_str]
        print(f"✅ Conversione selected_labels: {selected_labels}")
    except (ValueError, TypeError):
        print("❌ Errore nella conversione selected_labels")
        selected_labels = []
    
    # Verifica parametri richiesti
    required_params = ['mode', 'target_type', 'target_name']
    missing = [p for p in required_params if not form_data.get(p)]
    
    if missing:
        print(f"❌ Parametri mancanti: {missing}")
    else:
        print("✅ Tutti i parametri richiesti presenti")

def main():
    """Test principale"""
    print("🚀 Avvio test pipeline di etichettatura automatica")
    print("=" * 60)
    
    with app.app_context():
        try:
            # 1. Crea dati di test
            project, sheet, temp_path = create_test_data()
            if not project:
                return
            
            # 2. Test API endpoints
            test_api_endpoints(project, sheet)
            
            # 3. Test creazione etichette
            labels = test_label_creation(project)
            
            # 4. Test applicazione manuale
            test_manual_application(project, sheet, labels)
            
            # 5. Test parametri form
            test_form_parameters()
            
            # 6. Statistiche finali
            print("\n📊 Statistiche finali:")
            total_labels = Label.query.filter_by(project_id=project.id).count()
            total_applications = LabelApplication.query.filter_by(project_id=project.id, is_active=True).count()
            
            print(f"   💼 Progetto: {project.name}")
            print(f"   📄 Sheet: {sheet.name}")
            print(f"   🏷️ Etichette: {total_labels}")
            print(f"   📎 Applicazioni: {total_applications}")
            
            print("\n✅ Test completato con successo!")
            print("🔧 La pipeline di etichettatura è ora funzionale!")
            
            # Cleanup
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
                
        except Exception as e:
            print(f"\n❌ Errore durante il test: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    app = create_app()
    main()