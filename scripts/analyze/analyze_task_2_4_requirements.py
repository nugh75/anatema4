#!/usr/bin/env python3
"""
Analisi Requirements Task 2.4 - Store Etichette Centralizzato
Analizza i requisiti e componenti da implementare per il task 2.4
"""

import os
import sys

def analyze_existing_components():
    """Analizza i componenti esistenti per capire l'integrazione"""
    
    print("=== ANALISI COMPONENTI ESISTENTI ===")
    
    # 1. Route labels esistenti
    labels_py_path = "/home/nugh75/Git/anatema2/app/views/labels.py"
    if os.path.exists(labels_py_path):
        print("✅ app/views/labels.py - Route CRUD etichette ESISTENTI")
        with open(labels_py_path, 'r') as f:
            content = f.read()
            routes = [line.strip() for line in content.split('\n') if '@labels_bp.route' in line]
            print(f"   - Route trovate: {len(routes)}")
            for route in routes:
                print(f"     {route}")
    else:
        print("❌ app/views/labels.py - NON TROVATO")
    
    # 2. Template labels esistenti  
    templates_dir = "/home/nugh75/Git/anatema2/app/templates/labels"
    if os.path.exists(templates_dir):
        print(f"✅ {templates_dir} - Template etichette ESISTENTI")
        templates = os.listdir(templates_dir)
        print(f"   - Template trovati: {templates}")
    else:
        print(f"❌ {templates_dir} - NON TROVATO")
    
    # 3. Modello Label
    models_py_path = "/home/nugh75/Git/anatema2/app/models.py"
    if os.path.exists(models_py_path):
        print("✅ app/models.py - Modello Label")
        with open(models_py_path, 'r') as f:
            content = f.read()
            if "class Label(db.Model):" in content:
                print("   ✅ Modello Label trovato")
                # Analizza i campi
                lines = content.split('\n')
                label_section = False
                fields = []
                for line in lines:
                    if "class Label(db.Model):" in line:
                        label_section = True
                        continue
                    if label_section and line.strip().startswith('class '):
                        break
                    if label_section and ' = db.Column(' in line:
                        field_name = line.strip().split(' = ')[0]
                        fields.append(field_name)
                
                print(f"   - Campi trovati: {fields}")
                
                # Verifica campi mancanti per Task 2.4
                required_fields = ['created_by', 'usage_count']
                missing_fields = [f for f in required_fields if f not in fields]
                if missing_fields:
                    print(f"   ❌ Campi mancanti: {missing_fields}")
                else:
                    print("   ✅ Tutti i campi richiesti presenti")
            else:
                print("   ❌ Modello Label NON trovato")
    
    # 4. Integration con project view
    project_view_path = "/home/nugh75/Git/anatema2/app/templates/projects/view.html"
    if os.path.exists(project_view_path):
        print("✅ app/templates/projects/view.html - Template progetto")
        with open(project_view_path, 'r') as f:
            content = f.read()
            if 'labels' in content.lower():
                print("   ✅ Riferimenti a etichette presenti")
            else:
                print("   ❌ Nessun riferimento a etichette")
    
    print()

def analyze_task_2_4_requirements():
    """Analizza i requisiti specifici del Task 2.4"""
    
    print("=== REQUIREMENTS TASK 2.4 ===")
    
    requirements = {
        "Pagina Store Etichette": {
            "route": "/projects/{id}/labels",
            "description": "Pagina principale gestione etichette progetto",
            "components": [
                "Lista etichette con paginazione",
                "Statistiche utilizzo",
                "Filtri e ricerca", 
                "Azioni bulk"
            ]
        },
        "Vista Lista Etichette": {
            "description": "Tabella con nome, descrizione, utilizzo, data creazione",
            "features": [
                "Ordinamento per nome/data/utilizzo",
                "Paginazione",
                "Contatori utilizzo",
                "Status etichette (attive/inattive)"
            ]
        },
        "Modal Creazione": {
            "description": "Form validato per nuove etichette manuali",
            "fields": [
                "Nome (obbligatorio, univoco)",
                "Descrizione (opzionale)",
                "Colore (picker)",
                "Categorie (tags)"
            ],
            "validation": [
                "Nome non vuoto",
                "Nome univoco nel progetto",
                "Colore valido hex"
            ]
        },
        "Modal Modifica": {
            "description": "Editing etichette esistenti con controllo dipendenze",
            "features": [
                "Pre-popolamento campi",
                "Controllo utilizzo esistente",
                "Warning se etichetta in uso",
                "Validazione come creazione"
            ]
        },
        "Sistema Eliminazione": {
            "description": "Soft delete con controllo applicazioni attive",
            "features": [
                "Controllo applicazioni attive",
                "Warning prima eliminazione",
                "Soft delete (is_active = False)",
                "Possibilità di ripristino"
            ]
        },
        "Statistiche Utilizzo": {
            "description": "Contatori applicazioni per etichetta",
            "metrics": [
                "Numero applicazioni totali",
                "Applicazioni manuali vs AI",
                "Ultima applicazione",
                "Trend utilizzo"
            ]
        },
        "Gestione Suggerimenti AI": {
            "description": "Sezione per approvare suggerimenti AI per store",
            "features": [
                "Lista suggerimenti AI pending",
                "Anteprima suggerimento",
                "Approva/Rifiuta batch",
                "Integrazione con LabelSuggestion"
            ]
        }
    }
    
    for component, details in requirements.items():
        print(f"\n📋 {component}")
        print(f"   {details['description']}")
        
        if 'route' in details:
            print(f"   Route: {details['route']}")
        
        if 'components' in details:
            print("   Componenti:")
            for comp in details['components']:
                print(f"     - {comp}")
        
        if 'features' in details:
            print("   Features:")
            for feature in details['features']:
                print(f"     - {feature}")
        
        if 'fields' in details:
            print("   Campi:")
            for field in details['fields']:
                print(f"     - {field}")
                
        if 'validation' in details:
            print("   Validazione:")
            for val in details['validation']:
                print(f"     - {val}")
        
        if 'metrics' in details:
            print("   Metriche:")
            for metric in details['metrics']:
                print(f"     - {metric}")
    
    print()

def analyze_integration_points():
    """Analizza i punti di integrazione necessari"""
    
    print("=== PUNTI DI INTEGRAZIONE ===")
    
    integrations = {
        "Navigation": {
            "where": "app/templates/projects/view.html",
            "what": "Aggiungere link 'Gestione Etichette' nel menu progetto",
            "implementation": "Sezione dedicata con icona e statistiche rapide"
        },
        "API Backend": {
            "where": "app/views/api.py", 
            "what": "Utilizzare API Task 2.2 esistenti",
            "endpoints": [
                "GET /api/labels/{project_id} - Lista etichette",
                "POST /api/labels/{project_id} - Crea etichetta", 
                "PUT /api/labels/{project_id}/{label_id} - Modifica",
                "DELETE /api/labels/{project_id}/{label_id} - Elimina",
                "GET /api/labels/{project_id}/stats - Statistiche"
            ]
        },
        "Database Models": {
            "where": "app/models.py, app/models_labeling.py",
            "what": "Verificare/aggiungere campi mancanti",
            "required": [
                "Label.created_by - FK users.id",
                "Label.usage_count - INTEGER DEFAULT 0",
                "LabelApplication.authorized_by - già presente",
                "LabelSuggestion.suggestion_type - per store suggestions"
            ]
        },
        "Frontend JS": {
            "where": "app/static/js/",
            "what": "Script dedicato per label store management",
            "features": [
                "Modal management",
                "AJAX operations", 
                "Live statistics update",
                "Batch operations"
            ]
        }
    }
    
    for integration, details in integrations.items():
        print(f"\n🔗 {integration}")
        print(f"   Dove: {details['where']}")
        print(f"   Cosa: {details['what']}")
        
        if 'implementation' in details:
            print(f"   Implementazione: {details['implementation']}")
        
        if 'endpoints' in details:
            print("   Endpoints:")
            for endpoint in details['endpoints']:
                print(f"     - {endpoint}")
        
        if 'required' in details:
            print("   Richiesto:")
            for req in details['required']:
                print(f"     - {req}")
        
        if 'features' in details:
            print("   Features:")
            for feature in details['features']:
                print(f"     - {feature}")
    
    print()

def analyze_existing_api():
    """Verifica le API già disponibili dal Task 2.2"""
    
    print("=== VERIFICA API TASK 2.2 ===")
    
    api_py_path = "/home/nugh75/Git/anatema2/app/views/api.py"
    if os.path.exists(api_py_path):
        print("✅ app/views/api.py trovato")
        with open(api_py_path, 'r') as f:
            content = f.read()
        
        # Cerca endpoints per etichette
        api_routes = [line.strip() for line in content.split('\n') if '@api_bp.route' in line and 'label' in line.lower()]
        print(f"   📡 API Etichette trovate: {len(api_routes)}")
        for route in api_routes:
            print(f"     {route}")
        
        # Verifica funzioni specifiche per Task 2.4
        required_functions = [
            'get_project_labels',
            'create_label', 
            'update_label',
            'delete_label',
            'get_label_stats'
        ]
        
        for func in required_functions:
            if func in content:
                print(f"   ✅ {func} - presente")
            else:
                print(f"   ❌ {func} - mancante")
    else:
        print("❌ app/views/api.py NON trovato")
    
    print()

def generate_implementation_plan():
    """Genera il piano di implementazione step-by-step"""
    
    print("=== PIANO IMPLEMENTAZIONE TASK 2.4 ===")
    
    steps = [
        {
            "step": "1. Database Schema Update",
            "description": "Aggiornare modello Label con campi mancanti",
            "files": ["app/models.py"],
            "actions": [
                "Aggiungere campo created_by (FK users.id)", 
                "Aggiungere campo usage_count (INTEGER DEFAULT 0)",
                "Aggiornare to_dict() method",
                "Creare migration Alembic"
            ],
            "priority": "ALTA"
        },
        {
            "step": "2. Backend API Enhancement", 
            "description": "Verificare/completare API endpoints Task 2.2",
            "files": ["app/views/api.py"],
            "actions": [
                "Verificare endpoint /api/labels/{project_id}",
                "Aggiungere endpoint statistiche /api/labels/{project_id}/stats",
                "Aggiungere filtri e paginazione",
                "Gestione soft delete"
            ],
            "priority": "ALTA"
        },
        {
            "step": "3. Main Labels Store Page",
            "description": "Implementare pagina principale /projects/{id}/labels",
            "files": [
                "app/views/labels.py", 
                "app/templates/labels/store.html"
            ],
            "actions": [
                "Aggiornare route list_labels per store view",
                "Creare template store con tabella + modals",
                "Integrare statistiche e filtri",
                "Implementare paginazione"
            ],
            "priority": "ALTA"
        },
        {
            "step": "4. Modal Components",
            "description": "Implementare modals per CRUD operations",
            "files": [
                "app/templates/labels/modals/create.html",
                "app/templates/labels/modals/edit.html", 
                "app/templates/labels/modals/delete.html"
            ],
            "actions": [
                "Modal creazione con form validato",
                "Modal modifica con pre-popolamento",
                "Modal eliminazione con controlli",
                "Validazione frontend + backend"
            ],
            "priority": "MEDIA"
        },
        {
            "step": "5. Frontend JavaScript",
            "description": "Implementare logica frontend per store",
            "files": ["app/static/js/label_store.js"],
            "actions": [
                "Gestione modals",
                "AJAX operations per CRUD",
                "Live update statistiche",
                "Gestione errori e feedback"
            ],
            "priority": "MEDIA"
        },
        {
            "step": "6. Project Integration",
            "description": "Integrare store nel template progetto",
            "files": ["app/templates/projects/view.html"],
            "actions": [
                "Aggiungere sezione 'Gestione Etichette'",
                "Link a /projects/{id}/labels",
                "Statistiche rapide etichette",
                "Icone e styling"
            ],
            "priority": "MEDIA"
        },
        {
            "step": "7. AI Suggestions Integration",
            "description": "Integrare gestione suggerimenti AI", 
            "files": [
                "app/templates/labels/suggestions.html",
                "app/views/labels.py"
            ],
            "actions": [
                "Sezione suggerimenti AI pending",
                "Bulk approve/reject",
                "Integrazione con LabelSuggestion model",
                "Workflow approvazione"
            ],
            "priority": "BASSA"
        },
        {
            "step": "8. Testing & Validation",
            "description": "Test completi funzionalità",
            "files": ["test_task_2_4_complete.py"],
            "actions": [
                "Test CRUD operations",
                "Test statistiche e filtri", 
                "Test integrazione con API",
                "Test workflow completo"
            ],
            "priority": "BASSA"
        }
    ]
    
    for i, step in enumerate(steps, 1):
        print(f"\n🔢 STEP {i}: {step['step']}")
        print(f"   📝 {step['description']}")
        print(f"   🎯 Priorità: {step['priority']}")
        print(f"   📁 Files: {', '.join(step['files'])}")
        print("   ✅ Actions:")
        for action in step['actions']:
            print(f"      - {action}")
    
    print()

def main():
    print("🏷️  ANALISI REQUIREMENTS TASK 2.4 - STORE ETICHETTE CENTRALIZZATO")
    print("=" * 80)
    
    analyze_existing_components()
    analyze_task_2_4_requirements() 
    analyze_integration_points()
    analyze_existing_api()
    generate_implementation_plan()
    
    print("🎯 CONCLUSIONI:")
    print("- Componenti base (route, template, model) già presenti")
    print("- API Task 2.2 disponibili per integrazione") 
    print("- Necessario aggiornare schema DB con campi mancanti")
    print("- Focus su UX e integrazione con progetto")
    print("- Implementazione incrementale per priorità")
    print("\n✅ Pronto per iniziare implementazione Task 2.4")

if __name__ == "__main__":
    main()
