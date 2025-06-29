"""
Sistema di etichettatura separato dal ML
Workflow a due fasi:
1. Generazione etichette AI -> Approvazione umana 
2. Applicazione etichette (manuale/AI) ai dati
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app.database import db
from app.models import Project, File, ExcelSheet, ExcelRow, Label
from app.models_labeling import (
    LabelTemplate, LabelGeneration, LabelSuggestion, 
    LabelApplication, AILabelingSession, LabelAnalytics
)
from app.ml.api_client import MLAPIClient
from app.ml.analyzer import DataAnalyzer
import json
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
import uuid

logger = logging.getLogger(__name__)

labeling_bp = Blueprint('labeling', __name__)

# ================================
# DASHBOARD E NAVIGAZIONE
# ================================

@labeling_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard generale del sistema di etichettatura"""
    # Progetti dell'utente
    projects = Project.query.filter_by(owner_id=current_user.id)\
        .order_by(Project.updated_at.desc()).all()
    
    # Statistiche generali
    stats = {
        'templates_count': LabelTemplate.query.join(Project).filter(
            Project.owner_id == current_user.id
        ).count(),
        'pending_suggestions': LabelSuggestion.query.join(LabelGeneration)\
            .join(Project).filter(
                Project.owner_id == current_user.id,
                LabelSuggestion.status == 'pending'
            ).count(),
        'approved_labels': Label.query.join(Project).filter(
            Project.owner_id == current_user.id
        ).count(),
        'total_applications': LabelApplication.query.join(Project).filter(
            Project.owner_id == current_user.id,
            LabelApplication.is_active == True
        ).count()
    }
    
    # Generazioni recenti
    recent_generations = LabelGeneration.query.join(Project).filter(
        Project.owner_id == current_user.id
    ).order_by(LabelGeneration.created_at.desc()).limit(5).all()
    
    if request.is_json:
        return jsonify({
            'projects': [p.to_dict() for p in projects],
            'stats': stats,
            'recent_generations': [g.to_dict() for g in recent_generations]
        })
    
    return render_template('labeling/dashboard.html',
                         projects=projects,
                         stats=stats,
                         recent_generations=recent_generations)

@labeling_bp.route('/projects/<uuid:project_id>/dashboard')
@login_required
def project_dashboard(project_id):
    """Dashboard principale del sistema di etichettatura"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Statistiche generali
    stats = {
        'total_labels': Label.query.filter_by(project_id=project.id).count(),
        'total_templates': LabelTemplate.query.filter_by(project_id=project.id).count(),
        'pending_suggestions': LabelSuggestion.query.join(LabelGeneration).filter(
            LabelGeneration.project_id == project.id,
            LabelSuggestion.status == 'pending'
        ).count(),
        'total_applications': LabelApplication.query.filter_by(project_id=project.id).count()
    }
    
    # Template più utilizzati
    popular_templates = LabelTemplate.query.filter_by(
        project_id=project.id, 
        is_active=True
    ).order_by(LabelTemplate.usage_count.desc()).limit(5).all()
    
    # Generazioni recenti
    recent_generations = LabelGeneration.query.filter_by(
        project_id=project.id
    ).order_by(LabelGeneration.created_at.desc()).limit(5).all()
    
    # Etichette più usate
    popular_labels = db.session.query(Label, db.func.count(LabelApplication.id).label('usage_count'))\
        .join(LabelApplication, Label.id == LabelApplication.label_id, isouter=True)\
        .filter(Label.project_id == project.id)\
        .group_by(Label.id)\
        .order_by(db.text('usage_count DESC'))\
        .limit(5).all()
    
    # Fogli Excel disponibili
    sheets = ExcelSheet.query.join(File).filter(
        File.project_id == project.id
    ).all()
    
    if request.is_json:
        return jsonify({
            'project': project.to_dict(),
            'stats': stats,
            'popular_templates': [t.to_dict() for t in popular_templates],
            'recent_generations': [g.to_dict() for g in recent_generations],
            'popular_labels': [{'label': label.to_dict(), 'usage_count': count} for label, count in popular_labels],
            'sheets': [s.to_dict() for s in sheets]
        })
    
    return render_template('labeling/dashboard.html',
                         project=project,
                         stats=stats,
                         popular_templates=popular_templates,
                         recent_generations=recent_generations,
                         popular_labels=popular_labels,
                         sheets=sheets)

# ================================
# GESTIONE TEMPLATE
# ================================

@labeling_bp.route('/projects/<uuid:project_id>/templates')
@login_required
def list_templates(project_id):
    """Lista template di prompt per la generazione etichette"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    templates = LabelTemplate.query.filter_by(project_id=project.id)\
        .order_by(LabelTemplate.updated_at.desc()).all()
    
    if request.is_json:
        return jsonify({
            'project': project.to_dict(),
            'templates': [t.to_dict() for t in templates]
        })
    
    return render_template('labeling/templates.html',
                         project=project,
                         templates=templates)

@labeling_bp.route('/create-template', methods=['GET', 'POST'])
@login_required
def create_template():
    """Crea nuovo template di prompt"""
    project_id = request.args.get('project_id') or request.form.get('project_id')
    
    project = None
    if project_id:
        project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Se non c'è progetto specificato, prendi il primo dell'utente
    if not project:
        project = Project.query.filter_by(owner_id=current_user.id).first()
        if not project:
            flash('Crea prima un progetto per utilizzare il sistema di etichettatura', 'error')
            return redirect(url_for('projects.create_project'))
    
    # Resto della logica originale del template
    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            # Validazione
            name = data.get('name', '').strip()
            if not name:
                error_msg = 'Nome template richiesto'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('labeling/create_template.html', project=project, data=data)
            
            # Crea template
            template = LabelTemplate(
                project_id=project.id,
                created_by=current_user.id,
                name=name,
                description=data.get('description', ''),
                category=data.get('category', 'custom'),
                system_prompt=data.get('system_prompt', ''),
                user_prompt_template=data.get('user_prompt_template', ''),
                preferred_model=data.get('preferred_model', 'anthropic/claude-3-haiku'),
                temperature=float(data.get('temperature', 0.7)),
                max_tokens=int(data.get('max_tokens', 1000)),
                expected_labels_count=int(data.get('expected_labels_count', 5)),
                output_format=data.get('output_format', 'json')
            )
            
            db.session.add(template)
            db.session.commit()
            
            message = f'Template "{name}" creato con successo'
            if request.is_json:
                return jsonify({
                    'message': message,
                    'template': template.to_dict()
                }), 201
            
            flash(message, 'success')
            return redirect(url_for('labeling.dashboard'))
            
        except Exception as e:
            logger.error(f"Errore nella creazione template: {str(e)}")
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': str(e)}), 500
            flash(f'Errore nella creazione: {str(e)}', 'error')
    
    # GET request - mostra form con template predefiniti
    return render_template('labeling/create_template.html', project=project)

@labeling_bp.route('/projects/<uuid:project_id>/templates/create', methods=['GET', 'POST'])
@login_required
def create_template_with_project(project_id):
    """Crea nuovo template di prompt per progetto specifico"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            # Validazione
            name = data.get('name', '').strip()
            if not name:
                error_msg = 'Nome template richiesto'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('labeling/create_template.html', project=project, data=data)
            
            # Crea template
            template = LabelTemplate(
                project_id=project.id,
                created_by=current_user.id,
                name=name,
                description=data.get('description', ''),
                category=data.get('category', 'custom'),
                system_prompt=data.get('system_prompt', ''),
                user_prompt_template=data.get('user_prompt_template', ''),
                preferred_model=data.get('preferred_model', 'anthropic/claude-3-haiku'),
                temperature=float(data.get('temperature', 0.7)),
                max_tokens=int(data.get('max_tokens', 1000)),
                expected_labels_count=int(data.get('expected_labels_count', 5)),
                output_format=data.get('output_format', 'json')
            )
            
            db.session.add(template)
            db.session.commit()
            
            message = f'Template "{name}" creato con successo'
            if request.is_json:
                return jsonify({
                    'message': message,
                    'template': template.to_dict()
                }), 201
            
            flash(message, 'success')
            return redirect(url_for('labeling.list_templates', project_id=project.id))
            
        except Exception as e:
            logger.error(f"Errore nella creazione template: {str(e)}")
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': str(e)}), 500
            flash(f'Errore nella creazione: {str(e)}', 'error')
    
    # GET request - default templates
    default_templates = [
        {
            'name': 'Analisi Sentiment - Base',
            'category': 'sentiment',
            'description': 'Classifica il sentiment del testo in positivo, negativo, neutro',
            'system_prompt': 'Sei un esperto analista di sentiment. Analizza il testo e classifica il sentiment in modo accurato.',
            'user_prompt_template': 'Analizza i seguenti dati della colonna "{column_name}" e genera 3-4 etichette per classificare il sentiment:\n\n{sample_data}\n\nGenera etichette chiare come: Positivo, Negativo, Neutro, Misto.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 4
        },
        {
            'name': 'Sentiment Avanzato - 5 Scale',
            'category': 'sentiment',
            'description': 'Sentiment analysis su scala a 5 livelli per analisi più dettagliate',
            'system_prompt': 'Sei un esperto analista di sentiment. Usa una scala a 5 livelli per una classificazione più granulare.',
            'user_prompt_template': 'Analizza i seguenti dati della colonna "{column_name}" e genera 5 etichette per sentiment su scala dettagliata:\n\n{sample_data}\n\nGenera etichette come: Molto Positivo, Positivo, Neutro, Negativo, Molto Negativo.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 5
        },
        {
            'name': 'Classificazione Emozioni - Ekman',
            'category': 'emotion',
            'description': 'Classifica secondo le 6 emozioni base di Paul Ekman',
            'system_prompt': 'Sei un esperto psicologo. Classifica le emozioni secondo il modello di Paul Ekman.',
            'user_prompt_template': 'Analizza i seguenti dati della colonna "{column_name}" e identifica le emozioni base presenti:\n\n{sample_data}\n\nGenera etichette per le 6 emozioni base: Gioia, Tristezza, Rabbia, Paura, Sorpresa, Disgusto.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 6
        },
        {
            'name': 'Emozioni Complesse',
            'category': 'emotion',
            'description': 'Identifica emozioni complesse e sfaccettate nel testo',
            'system_prompt': 'Sei un esperto psicologo. Identifica emozioni complesse oltre quelle base.',
            'user_prompt_template': 'Analizza i seguenti dati della colonna "{column_name}" e identifica emozioni complesse:\n\n{sample_data}\n\nGenera etichette per emozioni come: Nostalgia, Frustrazione, Entusiasmo, Ansia, Soddisfazione, Delusione, Speranza.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 7
        },
        {
            'name': 'Tono di Comunicazione',
            'category': 'tone',
            'description': 'Classifica il tono e stile di comunicazione del testo',
            'system_prompt': 'Sei un esperto di comunicazione. Analizza il tono e lo stile del linguaggio.',
            'user_prompt_template': 'Analizza i seguenti dati della colonna "{column_name}" e identifica il tono di comunicazione:\n\n{sample_data}\n\nGenera etichette per toni come: Formale, Informale, Professionale, Colloquiale, Ironico, Serio, Scherzoso.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 6
        },
        {
            'name': 'Analisi Comportamentale',
            'category': 'behavior',
            'description': 'Classifica comportamenti e azioni descritte nel testo',
            'system_prompt': 'Sei un esperto analista comportamentale. Classifica i comportamenti descritti.',
            'user_prompt_template': 'Analizza i seguenti dati della colonna "{column_name}" e classifica i comportamenti:\n\n{sample_data}\n\nGenera etichette per comportamenti come: Collaborativo, Competitivo, Passivo, Assertivo, Aggressivo.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 5
        },
        {
            'name': 'Classificazione Tematiche',
            'category': 'topic',
            'description': 'Identifica i temi e argomenti principali del contenuto',
            'system_prompt': 'Sei un esperto analista di contenuti. Identifica i temi principali nei testi.',
            'user_prompt_template': 'Analizza i seguenti dati della colonna "{column_name}" e identifica i temi principali:\n\n{sample_data}\n\nGenera etichette per i temi più ricorrenti nel contenuto.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 8
        },
        {
            'name': 'Urgenza e Priorità',
            'category': 'priority',
            'description': 'Classifica il livello di urgenza o priorità del contenuto',
            'system_prompt': 'Sei un esperto di gestione delle priorità. Classifica l\'urgenza dei contenuti.',
            'user_prompt_template': 'Analizza i seguenti dati della colonna "{column_name}" e classifica per urgenza/priorità:\n\n{sample_data}\n\nGenera etichette come: Urgente, Alta Priorità, Media Priorità, Bassa Priorità, Non Urgente.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 5
        },
        {
            'name': 'Qualità del Feedback',
            'category': 'quality',
            'description': 'Valuta la qualità e utilità di feedback o recensioni',
            'system_prompt': 'Sei un esperto di customer experience. Valuta la qualità dei feedback.',
            'user_prompt_template': 'Analizza i seguenti dati della colonna "{column_name}" e valuta la qualità del feedback:\n\n{sample_data}\n\nGenera etichette come: Molto Utile, Utile, Moderatamente Utile, Poco Utile, Non Utile.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 5
        },
        {
            'name': 'Intenzioni dell\'Utente',
            'category': 'intent',
            'description': 'Identifica le intenzioni o obiettivi dell\'utente nel testo',
            'system_prompt': 'Sei un esperto di user experience. Identifica le intenzioni degli utenti.',
            'user_prompt_template': 'Analizza i seguenti dati della colonna "{column_name}" e identifica le intenzioni:\n\n{sample_data}\n\nGenera etichette per intenzioni come: Richiesta Info, Reclamo, Complimento, Suggerimento, Richiesta Supporto.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 6
        },
        {
            'name': 'Livello di Expertise',
            'category': 'expertise',
            'description': 'Classifica il livello di competenza tecnica mostrato nel testo',
            'system_prompt': 'Sei un esperto formatore. Valuta il livello di competenza mostrato nei contenuti.',
            'user_prompt_template': 'Analizza i seguenti dati della colonna "{column_name}" e valuta il livello di expertise:\n\n{sample_data}\n\nGenera etichette come: Principiante, Intermedio, Avanzato, Esperto, Specialista.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 5
        },
        {
            'name': 'Personalità - Big Five',
            'category': 'personality',
            'description': 'Identifica tratti di personalità secondo il modello Big Five',
            'system_prompt': 'Sei un esperto psicologo della personalità. Identifica i tratti del Big Five.',
            'user_prompt_template': 'Analizza i seguenti dati della colonna "{column_name}" e identifica tratti di personalità:\n\n{sample_data}\n\nGenera etichette per: Estroversione, Gradevolezza, Coscienziosità, Neuroticismo, Apertura.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 5
        }
    ]
    
    return render_template('labeling/create_template.html',
                         project=project,
                         default_templates=default_templates)

@labeling_bp.route('/templates/<uuid:template_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_template(template_id):
    """Modifica template esistente"""
    template = LabelTemplate.query.join(Project).filter(
        LabelTemplate.id == template_id,
        Project.owner_id == current_user.id
    ).first_or_404()
    
    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            # Aggiorna template
            template.name = data.get('name', template.name).strip()
            template.description = data.get('description', template.description)
            template.category = data.get('category', template.category)
            template.system_prompt = data.get('system_prompt', template.system_prompt)
            template.user_prompt_template = data.get('user_prompt_template', template.user_prompt_template)
            template.preferred_model = data.get('preferred_model', template.preferred_model)
            template.temperature = float(data.get('temperature', template.temperature))
            template.max_tokens = int(data.get('max_tokens', template.max_tokens))
            template.expected_labels_count = int(data.get('expected_labels_count', template.expected_labels_count))
            template.output_format = data.get('output_format', template.output_format)
            template.is_active = data.get('is_active', template.is_active)
            template.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            message = f'Template "{template.name}" aggiornato con successo'
            if request.is_json:
                return jsonify({
                    'message': message,
                    'template': template.to_dict()
                })
            
            flash(message, 'success')
            return redirect(url_for('labeling.list_templates', project_id=template.project_id))
            
        except Exception as e:
            logger.error(f"Errore nell'aggiornamento template: {str(e)}")
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': str(e)}), 500
            flash(f'Errore nell\'aggiornamento: {str(e)}', 'error')
    
    return render_template('labeling/edit_template.html',
                         project=template.project,
                         template=template)

# ================================
# FASE 1: GENERAZIONE ETICHETTE AI
# ================================

@labeling_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/generate-labels', methods=['GET', 'POST'])
@login_required
def generate_labels_phase1(project_id, sheet_id):
    """Fase 1: Genera etichette AI da un campione di dati"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Verifica che il foglio appartenga al progetto
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            template_id = data.get('template_id')
            column_name = data.get('column_name', '').strip()
            sample_size = int(data.get('sample_size', 20))
            
            if not template_id or not column_name:
                error_msg = 'Template e nome colonna richiesti'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return redirect(request.url)
            
            # Carica dati Excel
            file_path = sheet.file.get_file_path()
            df = pd.read_excel(file_path, sheet_name=sheet.name)
            
            if column_name not in df.columns:
                error_msg = f'Colonna "{column_name}" non trovata'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return redirect(request.url)
            
            # Campiona dati
            sample_data = df[column_name].dropna().sample(
                min(sample_size, len(df[column_name].dropna()))
            ).tolist()
            
            # Recupera template
            template = LabelTemplate.query.filter_by(
                id=template_id, 
                project_id=project.id
            ).first_or_404()
            
            # Crea sessione di generazione
            generation = LabelGeneration(
                project_id=project.id,
                sheet_id=sheet.id,
                template_id=template.id,
                created_by=current_user.id,
                column_name=column_name,
                sample_data=sample_data
            )
            
            db.session.add(generation)
            db.session.flush()
            
            # Genera etichette con AI
            success = _generate_labels_with_ai(generation, template, sample_data, column_name)
            
            if success:
                db.session.commit()
                message = f'Generazione etichette completata per colonna "{column_name}"'
                if request.is_json:
                    return jsonify({
                        'message': message,
                        'generation_id': str(generation.id)
                    })
                flash(message, 'success')
                return redirect(url_for('labeling.review_suggestions', 
                                      project_id=project.id, 
                                      generation_id=generation.id))
            else:
                db.session.rollback()
                error_msg = generation.error_message or 'Errore nella generazione etichette'
                if request.is_json:
                    return jsonify({'error': error_msg}), 500
                flash(error_msg, 'error')
                
        except Exception as e:
            logger.error(f"Errore nella generazione etichette: {str(e)}")
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': str(e)}), 500
            flash(f'Errore nella generazione: {str(e)}', 'error')
    
    # GET request - mostra form
    # Carica template disponibili
    templates = LabelTemplate.query.filter_by(
        project_id=project.id, 
        is_active=True
    ).all()
    
    # Carica colonne disponibili
    try:
        file_path = sheet.file.get_file_path()
        df = pd.read_excel(file_path, sheet_name=sheet.name)
        columns = list(df.columns)
    except Exception as e:
        logger.error(f"Errore nel caricamento colonne: {str(e)}")
        columns = []
        flash(f'Errore nel caricamento dati: {str(e)}', 'error')
    
    return render_template('labeling/generate_labels_phase1.html',
                         project=project,
                         sheet=sheet,
                         templates=templates,
                         columns=columns)

def _generate_labels_with_ai(generation: LabelGeneration, template: LabelTemplate,
                           sample_data: List[str], column_name: str) -> bool:
    """Funzione helper ULTRA-ROBUSTA per generare etichette con AI"""
    try:
        from app.models import MLConfiguration
        import json
        import re
        
        # Recupera configurazione ML attiva
        ml_config = MLConfiguration.query.filter_by(
            project_id=generation.project_id,
            is_active=True
        ).first()
        
        if not ml_config:
            generation.status = 'error'
            generation.error_message = 'Nessuna configurazione ML attiva trovata'
            return False
        
        # Crea client AI con timeout più breve
        client = MLAPIClient(
            provider=ml_config.ml_provider,
            api_key=ml_config.api_key_encrypted,
            api_url=ml_config.api_url,
            model=template.preferred_model or ml_config.ml_model
        )
        
        # Costruisci prompt ottimizzato (sample ridotto per velocità)
        sample_text = '\n'.join([f"- {str(item)[:100]}" for item in sample_data[:10]])  # Ridotto da 15 a 10, max 100 char
        
        # Prompt migliorato per garantire formato JSON consistente
        enhanced_prompt = f"""
{template.system_prompt}

IMPORTANTE: Rispondi SOLO con un oggetto JSON valido nel seguente formato:
{{
    "labels": [
        {{"name": "Nome Etichetta", "description": "Descrizione breve", "category": "{template.category}", "color": "#1976d2"}},
        {{"name": "Altra Etichetta", "description": "Altra descrizione", "category": "{template.category}", "color": "#1976d2"}}
    ]
}}

Dati da analizzare dalla colonna "{column_name}":
{sample_text}

Genera {template.expected_labels_count} etichette appropriate per questa categoria: {template.category}
"""
        
        # Esegui generazione con retry logic
        start_time = datetime.utcnow()
        response = None
        
        # Tentativo 1: Prompt ottimizzato
        try:
            logger.info("🚀 Tentativo 1: Generazione AI con prompt ottimizzato")
            response = client.analyze_text(
                prompt=enhanced_prompt,
                analysis_type='categorization',
                return_json=True
            )
        except Exception as e:
            logger.warning(f"⚠️ Tentativo 1 fallito: {str(e)}")
            
        # Tentativo 2: Prompt semplificato se il primo fallisce
        if not response or not response.get('success', False):
            try:
                logger.info("🔄 Tentativo 2: Prompt semplificato")
                simple_prompt = f"Analizza questi dati: {sample_text}\nGenera 3-5 etichette per categoria '{template.category}' in formato JSON."
                response = client.analyze_text(
                    prompt=simple_prompt,
                    analysis_type='categorization',
                    return_json=True
                )
            except Exception as e:
                logger.warning(f"⚠️ Tentativo 2 fallito: {str(e)}")
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Aggiorna generazione con dati di base
        generation.ai_provider = ml_config.ml_provider
        generation.ai_model = template.preferred_model or ml_config.ml_model
        generation.processing_time = processing_time
        
        if response and response.get('success', False):
            # PARSING ULTRA-ROBUSTO
            analysis_data = response.get('analysis', {})
            generation.raw_ai_response = str(analysis_data)
            
            # Normalizza in dict
            if isinstance(analysis_data, str):
                # Prova parsing JSON diretto
                try:
                    analysis_data = json.loads(analysis_data)
                except json.JSONDecodeError:
                    # Estrai JSON con regex se malformato
                    json_match = re.search(r'\{.*\}', analysis_data, re.DOTALL)
                    if json_match:
                        try:
                            analysis_data = json.loads(json_match.group())
                        except:
                            analysis_data = {}
                    else:
                        # Parsing testo libero come fallback
                        analysis_data = _parse_text_fallback(analysis_data, template.category)
            
            # Estrazione MULTI-FORMATO
            suggestions_list = []
            
            # Formato 1: JSON strutturato con 'labels'
            if isinstance(analysis_data, dict) and 'labels' in analysis_data:
                logger.info("✅ Formato 'labels' riconosciuto")
                labels = analysis_data.get('labels', [])
                for label in labels:
                    if isinstance(label, dict):
                        suggestions_list.append({
                            'name': label.get('name', '').strip(),
                            'description': label.get('description', '').strip(),
                            'category': label.get('category', template.category),
                            'color': label.get('color', '#1976d2'),
                            'confidence': label.get('confidence', 0.8),
                            'reasoning': label.get('reasoning', 'Generata dall\'AI'),
                            'sample_values': label.get('sample_values', [])
                        })
                    elif isinstance(label, str) and label.strip():
                        suggestions_list.append({
                            'name': label.strip(),
                            'description': f'Etichetta {template.category}: {label.strip()}',
                            'category': template.category,
                            'color': '#1976d2',
                            'confidence': 0.8,
                            'reasoning': 'Generata dall\'AI',
                            'sample_values': []
                        })
            
            # Formato 2: JSON con 'categories'
            elif isinstance(analysis_data, dict) and 'categories' in analysis_data:
                logger.info("✅ Formato 'categories' riconosciuto")
                categories = analysis_data.get('categories', [])
                for category in categories:
                    if isinstance(category, dict):
                        cat_labels = category.get('labels', [])
                        for label in cat_labels:
                            label_name = label if isinstance(label, str) else label.get('name', '')
                            if label_name.strip():
                                suggestions_list.append({
                                    'name': label_name.strip(),
                                    'description': category.get('description', f'Categoria: {category.get("name", template.category)}'),
                                    'category': category.get('name', template.category),
                                    'color': '#1976d2',
                                    'confidence': 0.8,
                                    'reasoning': category.get('description', 'Generata dall\'AI'),
                                    'sample_values': category.get('sample_texts', [])
                                })
            
            # Formato 3: Fallback - parsing diretto di campi top-level
            else:
                logger.info("🔄 Parsing fallback di campi generici")
                # Cerca qualsiasi campo che contiene array di stringhe
                for key, value in (analysis_data.items() if isinstance(analysis_data, dict) else {}):
                    if isinstance(value, list) and len(value) > 0:
                        for item in value:
                            if isinstance(item, str) and item.strip():
                                suggestions_list.append({
                                    'name': item.strip(),
                                    'description': f'Etichetta {template.category}: {item.strip()}',
                                    'category': template.category,
                                    'color': '#1976d2',
                                    'confidence': 0.7,
                                    'reasoning': f'Estratta da campo "{key}"',
                                    'sample_values': []
                                })
                        break  # Prendi solo il primo array trovato
            
            # Fallback finale: etichette predefinite se nulla funziona
            if len(suggestions_list) == 0:
                logger.warning("⚠️ Nessuna etichetta estratta - Uso fallback predefinito")
                fallback_labels = _get_fallback_labels(template.category)
                for label_name in fallback_labels:
                    suggestions_list.append({
                        'name': label_name,
                        'description': f'Etichetta predefinita per {template.category}',
                        'category': template.category,
                        'color': '#757575',  # Grigio per indicare fallback
                        'confidence': 0.5,
                        'reasoning': 'Etichetta di fallback - AI non disponibile',
                        'sample_values': []
                    })
            
            # Crea i suggerimenti nel database
            created_count = 0
            for suggestion_data in suggestions_list[:template.expected_labels_count]:  # Limita al numero atteso
                if suggestion_data.get('name', '').strip():  # Solo se ha un nome valido
                    suggestion = LabelSuggestion(
                        generation_id=generation.id,
                        suggested_name=suggestion_data.get('name', '').strip(),
                        suggested_description=suggestion_data.get('description', '').strip(),
                        suggested_category=suggestion_data.get('category', template.category),
                        suggested_color=suggestion_data.get('color', '#1976d2'),
                        ai_confidence=suggestion_data.get('confidence', 0.8),
                        ai_reasoning=suggestion_data.get('reasoning', ''),
                        sample_values=suggestion_data.get('sample_values', [])
                    )
                    db.session.add(suggestion)
                    created_count += 1
            
            generation.status = 'completed'
            generation.total_suggestions = created_count
            
            # Aggiorna contatore uso template
            template.usage_count += 1
            
            logger.info(f"✅ Generazione completata: {created_count} etichette create")
            return True
        else:
            # Fallback completo quando l'AI fallisce
            logger.warning("⚠️ AI non disponibile - Uso etichette predefinite")
            fallback_labels = _get_fallback_labels(template.category)
            created_count = 0
            
            for label_name in fallback_labels:
                suggestion = LabelSuggestion(
                    generation_id=generation.id,
                    suggested_name=label_name,
                    suggested_description=f'Etichetta predefinita per {template.category}',
                    suggested_category=template.category,
                    suggested_color='#757575',
                    ai_confidence=0.5,
                    ai_reasoning='Etichetta di fallback - AI non disponibile',
                    sample_values=[]
                )
                db.session.add(suggestion)
                created_count += 1
            
            generation.status = 'completed'
            generation.total_suggestions = created_count
            generation.error_message = response.get('error', 'AI non disponibile') if response else 'Timeout API - usate etichette predefinite'
            
            return True  # Ritorna True anche con fallback
            
    except Exception as e:
        logger.error(f"❌ Errore critico nella generazione AI: {str(e)}")
        # Anche in caso di errore critico, prova a creare etichette di fallback
        try:
            fallback_labels = _get_fallback_labels(template.category)
            for label_name in fallback_labels:
                suggestion = LabelSuggestion(
                    generation_id=generation.id,
                    suggested_name=label_name,
                    suggested_description=f'Etichetta di emergenza per {template.category}',
                    suggested_category=template.category,
                    suggested_color='#f44336',  # Rosso per indicare errore
                    ai_confidence=0.3,
                    ai_reasoning=f'Etichetta di emergenza - Errore: {str(e)}',
                    sample_values=[]
                )
                db.session.add(suggestion)
            
            generation.status = 'completed'
            generation.total_suggestions = len(fallback_labels)
            generation.error_message = f'Errore AI risolto con fallback: {str(e)}'
            return True
        except:
            # Ultimo fallback
            generation.status = 'error'
            generation.error_message = str(e)
            return False

def _parse_text_fallback(text: str, category: str) -> dict:
    """Parsing di testo libero quando JSON fallisce"""
    import re
    
    # Cerca pattern come "1. Etichetta" o "- Etichetta"
    patterns = [
        r'^\d+\.\s*(.+?)(?:\n|$)',  # "1. Etichetta"
        r'^[-*]\s*(.+?)(?:\n|$)',   # "- Etichetta" o "* Etichetta"
        r'^(.+?)(?:\n|$)'           # Qualsiasi riga
    ]
    
    labels = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.MULTILINE)
        if matches:
            labels = [match.strip() for match in matches if match.strip()]
            break
    
    return {'labels': labels[:5]} if labels else {}

def _get_fallback_labels(category: str) -> List[str]:
    """Restituisce etichette predefinite per categoria"""
    fallback_map = {
        'sentiment': ['Positivo', 'Negativo', 'Neutro', 'Misto'],
        'emotion': ['Gioia', 'Tristezza', 'Rabbia', 'Paura', 'Sorpresa'],
        'tone': ['Formale', 'Informale', 'Professionale', 'Colloquiale'],
        'priority': ['Alta', 'Media', 'Bassa', 'Urgente'],
        'quality': ['Ottima', 'Buona', 'Sufficiente', 'Insufficiente'],
        'topic': ['Tema A', 'Tema B', 'Tema C', 'Altro'],
        'behavior': ['Positivo', 'Neutro', 'Negativo'],
        'intent': ['Informazione', 'Reclamo', 'Complimento', 'Richiesta'],
        'custom': ['Categoria 1', 'Categoria 2', 'Categoria 3', 'Altro']
    }
    
    return fallback_map.get(category, fallback_map['custom'])

# Continuo con le altre funzioni...

@labeling_bp.route('/projects/<uuid:project_id>/generations/<uuid:generation_id>/review')
@login_required
def review_suggestions(project_id, generation_id):
    """Revisiona i suggerimenti di etichette generati dall'AI"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    generation = LabelGeneration.query.filter_by(
        id=generation_id, 
        project_id=project.id
    ).first_or_404()
    
    suggestions = LabelSuggestion.query.filter_by(
        generation_id=generation.id
    ).order_by(LabelSuggestion.created_at).all()
    
    if request.is_json:
        return jsonify({
            'project': project.to_dict(),
            'generation': generation.to_dict(),
            'suggestions': [s.to_dict() for s in suggestions]
        })
    
    return render_template('labeling/review_suggestions.html',
                         project=project,
                         generation=generation,
                         suggestions=suggestions)

@labeling_bp.route('/suggestions/<uuid:suggestion_id>/approve', methods=['POST'])
@login_required
def approve_suggestion(suggestion_id):
    """Approva un suggerimento AI e crea l'etichetta"""
    suggestion = LabelSuggestion.query.join(LabelGeneration).join(Project).filter(
        LabelSuggestion.id == suggestion_id,
        Project.owner_id == current_user.id
    ).first_or_404()
    
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        # Crea l'etichetta nel sistema principale
        label = Label(
            project_id=suggestion.generation.project_id,
            name=data.get('final_label', suggestion.suggested_name),
            description=data.get('final_description', suggestion.suggested_description),
            color=data.get('final_color', suggestion.suggested_color),
            categories=[data.get('final_category', suggestion.suggested_category)] if data.get('final_category', suggestion.suggested_category) else []
        )
        
        db.session.add(label)
        db.session.flush()
        
        # Aggiorna suggerimento
        suggestion.status = 'approved'
        suggestion.reviewed_by = current_user.id
        suggestion.reviewed_at = datetime.utcnow()
        suggestion.review_notes = data.get('notes', '')
        suggestion.final_name = label.name
        suggestion.final_description = label.description
        suggestion.final_category = label.categories[0] if label.categories else None
        suggestion.final_color = label.color
        suggestion.created_label_id = label.id
        
        # Aggiorna contatori generazione
        generation = suggestion.generation
        generation.approved_suggestions += 1
        
        db.session.commit()
        
        message = f'Etichetta "{label.name}" approvata e creata'
        if request.is_json:
            return jsonify({
                'message': message,
                'label': label.to_dict()
            })
        
        flash(message, 'success')
        return redirect(request.referrer or url_for('labeling.review_suggestions', 
                                                  project_id=generation.project_id,
                                                  generation_id=generation.id))
        
    except Exception as e:
        logger.error(f"Errore nell'approvazione suggerimento: {str(e)}")
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nell\'approvazione: {str(e)}', 'error')
        return redirect(request.referrer)

@labeling_bp.route('/suggestions/<uuid:suggestion_id>/reject', methods=['POST'])
@login_required
def reject_suggestion(suggestion_id):
    """Rifiuta un suggerimento AI"""
    suggestion = LabelSuggestion.query.join(LabelGeneration).join(Project).filter(
        LabelSuggestion.id == suggestion_id,
        Project.owner_id == current_user.id
    ).first_or_404()
    
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        suggestion.status = 'rejected'
        suggestion.reviewed_by = current_user.id
        suggestion.reviewed_at = datetime.utcnow()
        suggestion.review_notes = data.get('notes', '')
        
        # Aggiorna contatori generazione
        generation = suggestion.generation
        generation.rejected_suggestions += 1
        
        db.session.commit()
        
        message = f'Suggerimento "{suggestion.suggested_name}" rifiutato'
        if request.is_json:
            return jsonify({'message': message})
        
        flash(message, 'info')
        return redirect(request.referrer or url_for('labeling.review_suggestions', 
                                                  project_id=generation.project_id,
                                                  generation_id=generation.id))
        
    except Exception as e:
        logger.error(f"Errore nel rifiuto suggerimento: {str(e)}")
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nel rifiuto: {str(e)}', 'error')
        return redirect(request.referrer)

# ================================
# FASE 2: APPLICAZIONE ETICHETTE
# ================================

@labeling_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/apply-labels', methods=['GET', 'POST'])
@login_required
def apply_labels_phase2(project_id, sheet_id):
    """Fase 2: Applica etichette esistenti ai dati (manuale o AI)"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            mode = data.get('mode')  # 'manual', 'ai_batch'
            
            if mode == 'manual':
                return _apply_label_manual(project, sheet, data)
            elif mode == 'ai_batch':
                return _apply_labels_ai_batch(project, sheet, data)
            else:
                error_msg = 'Tipo di applicazione non valido'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                
        except Exception as e:
            logger.error(f"Errore nell'applicazione etichette: {str(e)}")
            if request.is_json:
                return jsonify({'error': str(e)}), 500
            flash(f'Errore nell\'applicazione: {str(e)}', 'error')
    
    # GET request - mostra interfaccia
    available_labels = Label.query.filter_by(project_id=project.id).all()
    
    # Carica dati Excel per preview
    try:
        file_path = sheet.file.get_file_path()
        df = pd.read_excel(file_path, sheet_name=sheet.name)
        columns = list(df.columns)
        sample_data = df.head(10).to_dict('records')
    except Exception as e:
        logger.error(f"Errore nel caricamento dati: {str(e)}")
        columns = []
        sample_data = []
        flash(f'Errore nel caricamento dati: {str(e)}', 'error')
    
    # Applicazioni recenti (ultime 10)
    recent_applications = LabelApplication.query.filter_by(
        project_id=project.id,
        sheet_id=sheet.id,
        is_active=True
    ).order_by(LabelApplication.applied_at.desc()).limit(10).all()
    
    return render_template('labeling/apply_labels_phase2.html',
                         project=project,
                         sheet=sheet,
                         available_labels=available_labels,
                         columns=columns,
                         recent_applications=recent_applications)

def _apply_label_manual(project, sheet, data):
    """Applica etichetta manualmente a una cella specifica"""
    label_id = int(data.get('label_id'))
    row_index = int(data.get('row_index'))
    column_name = data.get('column_name', '').strip()
    cell_value = data.get('cell_value', '')
    
    if not all([label_id, row_index is not None, column_name]):
        error_msg = 'Parametri mancanti per l\'applicazione manuale'
        if request.is_json:
            return jsonify({'error': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(request.referrer)
    
    # Verifica che l'etichetta appartenga al progetto
    label = Label.query.filter_by(id=label_id, project_id=project.id).first()
    if not label:
        error_msg = 'Etichetta non trovata'
        if request.is_json:
            return jsonify({'error': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(request.referrer)
    
    # Rimuovi applicazione esistente per questa cella
    existing = LabelApplication.query.filter_by(
        project_id=project.id,
        sheet_id=sheet.id,
        row_index=row_index,
        column_name=column_name,
        is_active=True
    ).first()
    
    if existing:
        existing.is_active = False
    
    # Crea nuova applicazione
    application = LabelApplication(
        project_id=project.id,
        sheet_id=sheet.id,
        label_id=label_id,
        applied_by=current_user.id,
        row_index=row_index,
        column_name=column_name,
        cell_value=cell_value,
        application_type='manual',
        confidence_score=1.0
    )
    
    db.session.add(application)
    db.session.commit()
    
    message = f'Etichetta "{label.name}" applicata alla cella ({row_index}, {column_name})'
    if request.is_json:
        return jsonify({
            'message': message,
            'application': application.to_dict()
        })
    
    flash(message, 'success')
    return redirect(request.referrer)

def _apply_labels_ai_batch(project, sheet, data):
    """Applica etichette in batch usando AI"""
    target_type = data.get('target_type')  # 'column' o 'row'
    target_name = data.get('target_name', '').strip()
    custom_prompt = data.get('custom_prompt', '').strip()
    
    # Gestisci selected_labels come lista o singolo valore
    selected_labels = data.get('selected_labels', [])
    if isinstance(selected_labels, str):
        selected_labels = [selected_labels]
    elif not isinstance(selected_labels, list):
        selected_labels = []
    
    # Converti ID stringa in int
    try:
        selected_labels = [int(id_str) for id_str in selected_labels if id_str]
    except (ValueError, TypeError):
        selected_labels = []
    
    if not all([target_type, target_name, selected_labels]):
        error_msg = f'Parametri mancanti: target_type={target_type}, target_name={target_name}, labels={len(selected_labels)}'
        if request.is_json:
            return jsonify({'error': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(request.referrer)
    
    # Verifica etichette
    available_labels = Label.query.filter(
        Label.id.in_(selected_labels),
        Label.project_id == project.id
    ).all()
    
    if not available_labels:
        error_msg = f'Nessuna etichetta valida selezionata tra gli ID: {selected_labels}'
        if request.is_json:
            return jsonify({'error': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(request.referrer)
    
    # Crea sessione AI
    session = AILabelingSession(
        project_id=project.id,
        sheet_id=sheet.id,
        created_by=current_user.id,
        target_type=target_type,
        target_name=target_name,
        available_labels=[{'id': label.id, 'name': label.name, 'description': label.description} for label in available_labels],
        custom_prompt=custom_prompt
    )
    
    db.session.add(session)
    db.session.flush()
    
    # Esegui applicazione AI
    success = _execute_ai_labeling_session(session, sheet, available_labels)
    
    if success:
        db.session.commit()
        message = f'Applicazione AI completata: {session.successful_applications} celle etichettate'
        if request.is_json:
            return jsonify({
                'message': message,
                'session_id': str(session.id),
                'results': {
                    'successful_applications': session.successful_applications,
                    'failed_applications': session.failed_applications,
                    'total_cells_processed': session.total_cells_processed
                }
            })
        flash(message, 'success')
    else:
        db.session.rollback()
        error_msg = session.error_message or 'Errore nell\'applicazione AI'
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'error')
    
    return redirect(request.referrer)

def _execute_ai_labeling_session(session: AILabelingSession, sheet, available_labels: List[Label]) -> bool:
    """Esegue una sessione di etichettatura AI"""
    try:
        from app.models import MLConfiguration
        
        # Recupera configurazione ML
        ml_config = MLConfiguration.query.filter_by(
            project_id=session.project_id, 
            is_active=True
        ).first()
        
        if not ml_config:
            session.status = 'error'
            session.error_message = 'Nessuna configurazione ML attiva trovata'
            return False
        
        # Carica dati Excel
        file_path = sheet.file.get_file_path()
        df = pd.read_excel(file_path, sheet_name=sheet.name)
        
        # Prepara dati per l'analisi
        if session.target_type == 'column':
            if session.target_name not in df.columns:
                session.status = 'error'
                session.error_message = f'Colonna "{session.target_name}" non trovata'
                return False
            
            target_data = df[session.target_name].dropna()
            cells_to_process = [(i, session.target_name, str(value)) for i, value in target_data.items()]
        else:
            # TODO: Implementare per righe
            session.status = 'error'
            session.error_message = 'Applicazione AI per righe non ancora implementata'
            return False
        
        # Crea client AI
        client = MLAPIClient(
            provider=ml_config.ml_provider,
            api_key=ml_config.api_key_encrypted,
            api_url=ml_config.api_url,
            model=ml_config.ml_model
        )
        
        # Prepara prompt
        labels_desc = '\n'.join([f"- {label.name}: {label.description}" for label in available_labels])
        base_prompt = f"""Analizza il seguente testo e assegna l'etichetta più appropriata tra quelle disponibili.

Etichette disponibili:
{labels_desc}

{session.custom_prompt if session.custom_prompt else ''}

Rispondi solo con il nome esatto dell'etichetta (o 'NONE' se nessuna etichetta è appropriata)."""
        
        # Processa celle in batch
        session.status = 'processing'
        session.ai_provider = ml_config.ml_provider
        session.ai_model = ml_config.ml_model
        
        start_time = datetime.utcnow()
        successful = 0
        failed = 0
        
        for row_index, column_name, cell_value in cells_to_process[:50]:  # Limita a 50 per test
            try:
                prompt = f"{base_prompt}\n\nTesto da analizzare: {cell_value}"
                response = client.analyze_text(prompt)
                
                if response.get('success', False):
                    suggested_label_name = response.get('analysis', '').strip()
                    
                    # Trova etichetta corrispondente
                    matching_label = None
                    for label in available_labels:
                        if label.name.lower() == suggested_label_name.lower():
                            matching_label = label
                            break
                    
                    if matching_label and suggested_label_name.upper() != 'NONE':
                        # Rimuovi applicazione esistente
                        existing = LabelApplication.query.filter_by(
                            project_id=session.project_id,
                            sheet_id=session.sheet_id,
                            row_index=row_index,
                            column_name=column_name,
                            is_active=True
                        ).first()
                        
                        if existing:
                            existing.is_active = False
                        
                        # Crea nuova applicazione
                        application = LabelApplication(
                            project_id=session.project_id,
                            sheet_id=session.sheet_id,
                            label_id=matching_label.id,
                            applied_by=session.created_by,
                            row_index=row_index,
                            column_name=column_name,
                            cell_value=cell_value,
                            application_type='ai_batch',
                            confidence_score=response.get('confidence', 0.8),
                            ai_session_id=session.id,
                            ai_reasoning=response.get('reasoning', '')
                        )
                        
                        db.session.add(application)
                        successful += 1
                    else:
                        failed += 1
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(f"Errore nel processamento cella {row_index}: {str(e)}")
                failed += 1
        
        # Aggiorna sessione
        session.status = 'completed'
        session.processing_time = (datetime.utcnow() - start_time).total_seconds()
        session.total_cells_processed = successful + failed
        session.successful_applications = successful
        session.failed_applications = failed
        
        return True
        
    except Exception as e:
        logger.error(f"Errore nella sessione AI: {str(e)}")
        session.status = 'error'
        session.error_message = str(e)
        return False

# ================================
# ANALISI ETICHETTE
# ================================

@labeling_bp.route('/projects/<uuid:project_id>/analytics')
@login_required
def label_analytics(project_id):
    """Schermata di analisi delle etichette applicate"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Calcola statistiche in tempo reale
    analytics_data = _calculate_label_analytics(project)
    
    # Recupera analisi salvate
    saved_analytics = LabelAnalytics.query.filter_by(project_id=project.id)\
        .order_by(LabelAnalytics.calculated_at.desc()).all()
    
    # Prepara dati per i grafici
    chart_data = {
        'labelDistribution': {
            'labels': [item['name'] for item in analytics_data.get('label_distribution', [])],
            'values': [item['count'] for item in analytics_data.get('label_distribution', [])]
        },
        'timelineData': {
            'labels': [item['date'] for item in analytics_data.get('timeline_data', [])],
            'values': [item['count'] for item in analytics_data.get('timeline_data', [])]
        },
        'confidenceDistribution': [0, 0, 0, 0, 0],  # Default vuoto per 5 fasce
        'manualApplications': analytics_data.get('manual_applications', 0),
        'aiApplications': analytics_data.get('ai_applications', 0)
    }
    
    # Calcola distribuzione confidenza se ci sono dati
    if analytics_data.get('total_applications', 0) > 0:
        applications_with_confidence = LabelApplication.query.filter_by(
            project_id=project.id,
            is_active=True
        ).filter(LabelApplication.confidence_score.isnot(None)).all()
        
        confidence_counts = [0, 0, 0, 0, 0]  # 0-20%, 21-40%, 41-60%, 61-80%, 81-100%
        for app in applications_with_confidence:
            if app.confidence_score is not None:
                conf = app.confidence_score * 100
                if conf <= 20:
                    confidence_counts[0] += 1
                elif conf <= 40:
                    confidence_counts[1] += 1
                elif conf <= 60:
                    confidence_counts[2] += 1
                elif conf <= 80:
                    confidence_counts[3] += 1
                else:
                    confidence_counts[4] += 1
        chart_data['confidenceDistribution'] = confidence_counts
    
    # Lista progetti per filtri
    projects = Project.query.filter_by(owner_id=current_user.id).all()
    
    if request.is_json:
        return jsonify({
            'project': project.to_dict(),
            'analytics': analytics_data,
            'saved_analytics': [a.to_dict() for a in saved_analytics],
            'chart_data': chart_data
        })
    
    return render_template('labeling/analytics.html',
                         project=project,
                         analytics=analytics_data,
                         saved_analytics=saved_analytics,
                         chart_data=chart_data,
                         projects=projects)

def _calculate_label_analytics(project) -> Dict[str, Any]:
    """Calcola analytics in tempo reale per le etichette"""
    from app.models_labeling import LabelSuggestion
    
    # Statistiche generali
    total_applications = LabelApplication.query.filter_by(
        project_id=project.id, 
        is_active=True
    ).count()
    
    manual_applications = LabelApplication.query.filter_by(
        project_id=project.id,
        application_type='manual',
        is_active=True
    ).count()
    
    ai_applications = total_applications - manual_applications
    
    # Calcola confidenza media
    avg_confidence_result = db.session.query(
        db.func.avg(LabelApplication.confidence_score)
    ).filter(
        LabelApplication.project_id == project.id,
        LabelApplication.is_active == True,
        LabelApplication.confidence_score.isnot(None)
    ).first()
    
    avg_confidence = avg_confidence_result[0] if avg_confidence_result[0] is not None else 0.0
    
    # Numero totale di etichette
    total_labels = Label.query.filter_by(project_id=project.id).count()
    
    # Top labels con confidenza media
    top_labels_query = db.session.query(
        Label.name,
        Label.color,
        db.func.count(LabelApplication.id).label('count'),
        db.func.avg(LabelApplication.confidence_score).label('avg_confidence')
    ).join(LabelApplication, Label.id == LabelApplication.label_id)\
     .filter(Label.project_id == project.id, LabelApplication.is_active == True)\
     .group_by(Label.id, Label.name, Label.color)\
     .order_by(db.text('count DESC')).limit(10).all()
    
    top_labels = [
        {
            'label_name': name,
            'color': color,
            'count': count,
            'avg_confidence': float(avg_conf) if avg_conf is not None else 0.0
        }
        for name, color, count, avg_conf in top_labels_query
    ]
    
    # Statistiche dei suggerimenti (se esistono)
    total_suggestions = db.session.query(LabelSuggestion)\
        .join(LabelGeneration, LabelSuggestion.generation_id == LabelGeneration.id)\
        .filter(LabelGeneration.project_id == project.id).count()
        
    approved_suggestions = db.session.query(LabelSuggestion)\
        .join(LabelGeneration, LabelSuggestion.generation_id == LabelGeneration.id)\
        .filter(LabelGeneration.project_id == project.id, LabelSuggestion.status == 'approved').count()
        
    approval_rate = (approved_suggestions / total_suggestions) if total_suggestions > 0 else 0.0
    
    # Calcoli di precisione AI (basato sui suggerimenti approvati)
    ai_precision = approval_rate  # Semplificazione
    
    # Punteggio di efficienza (basato sul rapporto AI/manuale)
    efficiency_score = (ai_applications / total_applications) if total_applications > 0 else 0.0
    
    # Completezza (percentuale di celle etichettate)
    total_cells = db.session.query(db.func.count()).select_from(ExcelRow)\
        .join(ExcelSheet).filter(ExcelSheet.file_id.in_(
            db.session.query(File.id).filter(File.project_id == project.id)
        )).scalar()
    
    completeness = (total_applications / total_cells) if total_cells > 0 else 0.0
    
    # Attività recenti per timeline con formato corretto per il template
    recent_activities_query = db.session.query(
        LabelApplication.applied_at,
        Label.name.label('label_name'),
        LabelApplication.application_type,
        LabelApplication.confidence_score
    ).join(Label, LabelApplication.label_id == Label.id)\
     .filter(LabelApplication.project_id == project.id, LabelApplication.is_active == True)\
     .order_by(LabelApplication.applied_at.desc()).limit(10).all()
    
    recent_activities = []
    for activity in recent_activities_query:
        activity_type = 'application'
        description = f'Etichetta "{activity.label_name}" applicata'
        if activity.application_type == 'ai_batch':
            description = f'Etichetta "{activity.label_name}" applicata automaticamente dall\'AI'
        
        recent_activities.append({
            'type': activity_type,
            'description': description,
            'project_name': project.name,
            'timestamp': activity.applied_at,
            'confidence': float(activity.confidence_score) if activity.confidence_score is not None else 0.0
        })
    
    # Statistiche di progetto nel formato corretto per il template
    project_stats = [
        {
            'project_name': project.name,
            'unique_labels': total_labels,
            'total_applications': total_applications
        }
    ]
    
    # Distribuzione per etichetta
    label_distribution = db.session.query(
        Label.name, Label.color, db.func.count(LabelApplication.id).label('count')
    ).join(LabelApplication, Label.id == LabelApplication.label_id)\
     .filter(Label.project_id == project.id, LabelApplication.is_active == True)\
     .group_by(Label.id, Label.name, Label.color)\
     .order_by(db.text('count DESC')).all()
    
    # Distribuzione per foglio
    sheet_distribution = db.session.query(
        ExcelSheet.name, db.func.count(LabelApplication.id).label('count')
    ).join(LabelApplication, ExcelSheet.id == LabelApplication.sheet_id)\
     .filter(LabelApplication.project_id == project.id, LabelApplication.is_active == True)\
     .group_by(ExcelSheet.id, ExcelSheet.name)\
     .order_by(db.text('count DESC')).all()
    
    # Distribuzione per colonna
    column_distribution = db.session.query(
        LabelApplication.column_name, db.func.count(LabelApplication.id).label('count')
    ).filter(LabelApplication.project_id == project.id, LabelApplication.is_active == True)\
     .group_by(LabelApplication.column_name)\
     .order_by(db.text('count DESC')).all()
    
    # Timeline applicazioni (ultimi 30 giorni)
    from sqlalchemy import func, extract
    timeline_data = db.session.query(
        func.date(LabelApplication.applied_at).label('date'),
        func.count(LabelApplication.id).label('count')
    ).filter(
        LabelApplication.project_id == project.id,
        LabelApplication.is_active == True,
        LabelApplication.applied_at >= datetime.utcnow() - pd.Timedelta(days=30)
    ).group_by(func.date(LabelApplication.applied_at))\
     .order_by(func.date(LabelApplication.applied_at)).all()
    
    return {
        'total_applications': total_applications,
        'manual_applications': manual_applications,
        'ai_applications': ai_applications,
        'ai_percentage': round((ai_applications / total_applications * 100), 2) if total_applications > 0 else 0,
        'avg_confidence': avg_confidence,
        'total_labels': total_labels,
        'top_labels': top_labels,
        'project_stats': project_stats,
        'approval_rate': approval_rate,
        'approved_suggestions': approved_suggestions,
        'total_suggestions': total_suggestions,
        'ai_precision': ai_precision,
        'efficiency_score': efficiency_score,
        'completeness': completeness,
        'recent_activities': recent_activities,
        'label_distribution': [
            {'name': name, 'color': color, 'count': count} 
            for name, color, count in label_distribution
        ],
        'sheet_distribution': [
            {'name': name, 'count': count} 
            for name, count in sheet_distribution
        ],
        'column_distribution': [
            {'name': name, 'count': count} 
            for name, count in column_distribution
        ],
        'timeline_data': [
            {'date': date.isoformat(), 'count': count} 
            for date, count in timeline_data
        ]
    }

# ================================
# EXPORT ANALYTICS
# ================================

@labeling_bp.route('/projects/<uuid:project_id>/analytics/export/<format>')
@login_required
def export_analytics(project_id, format):
    """Esporta i dati analitici in diversi formati"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Calcola statistiche
    analytics_data = _calculate_label_analytics(project)
    
    if format.lower() == 'csv':
        return _export_analytics_csv(project, analytics_data)
    elif format.lower() == 'excel':
        return _export_analytics_excel(project, analytics_data)
    elif format.lower() == 'json':
        return _export_analytics_json(project, analytics_data)
    else:
        flash('Formato di export non supportato', 'error')
        return redirect(url_for('labeling.label_analytics', project_id=project_id))

def _export_analytics_csv(project, analytics_data):
    """Esporta analytics in formato CSV"""
    import csv
    import io
    from flask import make_response
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header del file
    writer.writerow(['Progetto', project.name])
    writer.writerow(['Data Export', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    
    # Statistiche generali
    writer.writerow(['STATISTICHE GENERALI'])
    writer.writerow(['Totale Applicazioni', analytics_data['total_applications']])
    writer.writerow(['Applicazioni Manuali', analytics_data['manual_applications']])
    writer.writerow(['Applicazioni AI', analytics_data['ai_applications']])
    writer.writerow(['Percentuale AI', f"{analytics_data['ai_percentage']}%"])
    writer.writerow(['Confidenza Media', f"{analytics_data['avg_confidence']:.2f}"])
    writer.writerow(['Totale Etichette', analytics_data['total_labels']])
    writer.writerow([])
    
    # Top etichette
    writer.writerow(['TOP ETICHETTE'])
    writer.writerow(['Nome', 'Utilizzi', 'Confidenza Media'])
    for label in analytics_data['top_labels']:
        writer.writerow([
            label['label_name'],
            label['count'],
            f"{label['avg_confidence']:.2f}"
        ])
    writer.writerow([])
    
    # Distribuzione per colonna
    writer.writerow(['DISTRIBUZIONE PER COLONNA'])
    writer.writerow(['Colonna', 'Utilizzi'])
    for col in analytics_data['column_distribution']:
        writer.writerow([col['name'], col['count']])
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=analytics_{project.name}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

def _export_analytics_excel(project, analytics_data):
    """Esporta analytics in formato Excel"""
    import io
    from flask import make_response
    
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Statistiche generali
        general_stats = pd.DataFrame([
            ['Totale Applicazioni', analytics_data['total_applications']],
            ['Applicazioni Manuali', analytics_data['manual_applications']],
            ['Applicazioni AI', analytics_data['ai_applications']],
            ['Percentuale AI', f"{analytics_data['ai_percentage']}%"],
            ['Confidenza Media', analytics_data['avg_confidence']],
            ['Totale Etichette', analytics_data['total_labels']],
        ], columns=['Metrica', 'Valore'])
        general_stats.to_excel(writer, sheet_name='Statistiche Generali', index=False)
        
        # Top etichette
        if analytics_data['top_labels']:
            top_labels_df = pd.DataFrame(analytics_data['top_labels'])
            top_labels_df.to_excel(writer, sheet_name='Top Etichette', index=False)
        
        # Distribuzione per etichetta
        if analytics_data['label_distribution']:
            label_dist_df = pd.DataFrame(analytics_data['label_distribution'])
            label_dist_df.to_excel(writer, sheet_name='Distribuzione Etichette', index=False)
        
        # Distribuzione per colonna
        if analytics_data['column_distribution']:
            col_dist_df = pd.DataFrame(analytics_data['column_distribution'])
            col_dist_df.to_excel(writer, sheet_name='Distribuzione Colonne', index=False)
        
        # Timeline
        if analytics_data['timeline_data']:
            timeline_df = pd.DataFrame(analytics_data['timeline_data'])
            timeline_df.to_excel(writer, sheet_name='Timeline', index=False)
        
        # Attività recenti
        if analytics_data['recent_activities']:
            activities_df = pd.DataFrame(analytics_data['recent_activities'])
            activities_df.to_excel(writer, sheet_name='Attività Recenti', index=False)
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename=analytics_{project.name}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return response

def _export_analytics_json(project, analytics_data):
    """Esporta analytics in formato JSON"""
    from flask import make_response
    import json
    
    export_data = {
        'project': {
            'id': str(project.id),
            'name': project.name,
            'export_date': datetime.utcnow().isoformat()
        },
        'analytics': analytics_data
    }
    
    response = make_response(json.dumps(export_data, indent=2, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename=analytics_{project.name}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
    
    return response

@labeling_bp.route('/projects/<uuid:project_id>/analytics/pdf-report')
@login_required
def generate_pdf_report(project_id):
    """Genera report PDF delle analisi"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    try:
        # Per ora, genera un CSV come fallback
        # TODO: Implementare generazione PDF con reportlab o weasyprint
        analytics_data = _calculate_label_analytics(project)
        return _export_analytics_csv(project, analytics_data)
        
    except Exception as e:
        logger.error(f"Errore nella generazione report PDF: {str(e)}")
        flash(f'Errore nella generazione report: {str(e)}', 'error')
        return redirect(url_for('labeling.label_analytics', project_id=project_id))

# ================================
# API ENDPOINTS
# ================================

@labeling_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/columns')
@login_required
def api_get_columns(project_id, sheet_id):
    """API: Recupera colonne di un foglio Excel"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    try:
        file_path = sheet.file.get_file_path()
        df = pd.read_excel(file_path, sheet_name=sheet.name)
        columns = list(df.columns)
        
        return jsonify({
            'columns': columns,
            'total_rows': len(df)
        })
    except Exception as e:
        logger.error(f"Errore nel caricamento colonne: {str(e)}")
        return jsonify({'error': str(e)}), 500

@labeling_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/rows')
@login_required
def api_get_rows(project_id, sheet_id):
    """API: Recupera righe di una colonna specifica"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    column_name = request.args.get('column_name')
    if not column_name:
        return jsonify({'error': 'Nome colonna richiesto'}), 400
    
    try:
        file_path = sheet.file.get_file_path()
        df = pd.read_excel(file_path, sheet_name=sheet.name)
        
        if column_name not in df.columns:
            return jsonify({'error': f'Colonna "{column_name}" non trovata'}), 400
        
        # Crea lista righe con indice e valore
        rows = []
        for idx, value in df[column_name].items():
            if pd.notna(value):  # Solo righe non vuote
                rows.append({
                    'index': int(idx),
                    'value': str(value)[:100],  # Tronca valore per preview
                    'display': f"{idx}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}"
                })
        
        return jsonify({
            'rows': rows[:100],  # Limita a 100 righe per performance
            'total_rows': len(rows)
        })
    except Exception as e:
        logger.error(f"Errore nel caricamento righe: {str(e)}")
        return jsonify({'error': str(e)}), 500

@labeling_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/targets')
@login_required
def api_get_targets(project_id, sheet_id):
    """API: Recupera target per applicazione AI batch"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    target_type = request.args.get('target_type')
    if not target_type:
        return jsonify({'error': 'Tipo target richiesto'}), 400
    
    try:
        file_path = sheet.file.get_file_path()
        df = pd.read_excel(file_path, sheet_name=sheet.name)
        
        targets = []
        
        if target_type == 'column':
            for col in df.columns:
                non_empty_count = df[col].notna().sum()
                targets.append({
                    'value': col,
                    'display': f"{col} ({non_empty_count} valori)",
                    'description': f"Colonna con {non_empty_count} celle non vuote"
                })
        elif target_type == 'row':
            # Per righe, mostra prime 20 righe
            for idx in range(min(20, len(df))):
                non_empty_cols = df.iloc[idx].notna().sum()
                targets.append({
                    'value': str(idx),
                    'display': f"Riga {idx} ({non_empty_cols} colonne)",
                    'description': f"Riga con {non_empty_cols} colonne non vuote"
                })
        elif target_type == 'range':
            # Per range, restituisci informazioni per costruire il form
            targets = [{
                'value': 'custom_range',
                'display': 'Range Personalizzato',
                'description': 'Definisci un range specifico di celle'
            }]
        
        return jsonify({
            'targets': targets,
            'total_columns': len(df.columns),
            'total_rows': len(df)
        })
    except Exception as e:
        logger.error(f"Errore nel caricamento target: {str(e)}")
        return jsonify({'error': str(e)}), 500

@labeling_bp.route('/projects/<uuid:project_id>/labels')
@login_required
def api_get_labels(project_id):
    """API: Recupera tutte le etichette del progetto"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    labels = Label.query.filter_by(project_id=project.id).all()
    
    return jsonify({
        'labels': [label.to_dict() for label in labels]
    })

@labeling_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/applications')
@login_required
def api_get_applications(project_id, sheet_id):
    """API: Recupera applicazioni etichette per un foglio"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    applications = LabelApplication.query.filter_by(
        project_id=project.id,
        sheet_id=sheet_id,
        is_active=True
    ).all()
    
    return jsonify({
        'applications': [app.to_dict() for app in applications]
    })

@labeling_bp.route('/applications/<uuid:application_id>/remove', methods=['DELETE'])
@login_required
def api_remove_application(application_id):
    """API: Rimuove un'applicazione di etichetta"""
    application = LabelApplication.query.join(Project).filter(
        LabelApplication.id == application_id,
        Project.owner_id == current_user.id
    ).first_or_404()
    
    try:
        application.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Applicazione rimossa con successo'})
        
    except Exception as e:
        logger.error(f"Errore nella rimozione applicazione: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ================================
# ROTTE SEMPLIFICATE (senza project_id in URL)
# ================================

@labeling_bp.route('/review-suggestions')
@login_required
def review_suggestions_simple():
    """Revisiona suggerimenti - versione semplificata"""
    generation_id = request.args.get('generation_id')
    
    if not generation_id:
        flash('ID generazione richiesto', 'error')
        return redirect(url_for('labeling.dashboard'))
    
    # Trova generazione dell'utente
    generation = LabelGeneration.query.join(Project).filter(
        LabelGeneration.id == generation_id,
        Project.owner_id == current_user.id
    ).first_or_404()
    
    # Redirect alla versione completa
    return redirect(url_for('labeling.review_suggestions',
                          project_id=generation.project_id,
                          generation_id=generation.id))

@labeling_bp.route('/analytics')
@login_required
def analytics_simple():
    """Analytics - versione semplificata"""
    project_id = request.args.get('project_id')
    
    if project_id:
        # Verifica che il progetto appartenga all'utente
        project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
        return redirect(url_for('labeling.label_analytics', project_id=project.id))
    
    # Mostra lista progetti per selezione
    projects = Project.query.filter_by(owner_id=current_user.id)\
        .order_by(Project.updated_at.desc()).all()
    
    if not projects:
        flash('Nessun progetto trovato', 'error')
        return redirect(url_for('projects.create_project'))
    
    return render_template('labeling/select_project_analytics.html', projects=projects)

@labeling_bp.route('/generate-labels')
@login_required
def generate_labels_simple():
    """Genera etichette - versione semplificata"""
    project_id = request.args.get('project_id')
    sheet_id = request.args.get('sheet_id')
    
    if project_id and sheet_id:
        # Verifica parametri e redirect alla versione completa
        project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
        sheet = ExcelSheet.query.join(File).filter(
            ExcelSheet.id == sheet_id,
            File.project_id == project.id
        ).first_or_404()
        
        return redirect(url_for('labeling.generate_labels_phase1',
                              project_id=project.id,
                              sheet_id=sheet.id))
    
    # Mostra form di selezione progetto/foglio
    projects = Project.query.filter_by(owner_id=current_user.id)\
        .order_by(Project.updated_at.desc()).all()
    
    if not projects:
        flash('Nessun progetto trovato', 'error')
        return redirect(url_for('projects.create_project'))
    
    # Se c'è solo un progetto, carica i suoi fogli
    sheets = []
    if len(projects) == 1:
        sheets = ExcelSheet.query.join(File).filter(
            File.project_id == projects[0].id
        ).all()
    
    return render_template('labeling/select_project_sheet.html',
                         projects=projects,
                         sheets=sheets)

@labeling_bp.route('/apply-labels')
@login_required
def apply_labels_simple():
    """Applica etichette - versione semplificata"""
    project_id = request.args.get('project_id')
    sheet_id = request.args.get('sheet_id')
    
    if project_id and sheet_id:
        # Verifica parametri e redirect alla versione completa
        project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
        sheet = ExcelSheet.query.join(File).filter(
            ExcelSheet.id == sheet_id,
            File.project_id == project.id
        ).first_or_404()
        
        return redirect(url_for('labeling.apply_labels_phase2',
                              project_id=project.id,
                              sheet_id=sheet.id))
    
    # Mostra form di selezione progetto/foglio
    projects = Project.query.filter_by(owner_id=current_user.id)\
        .order_by(Project.updated_at.desc()).all()
    
    if not projects:
        flash('Nessun progetto trovato', 'error')
        return redirect(url_for('projects.create_project'))
    
    # Se c'è solo un progetto, carica i suoi fogli
    sheets = []
    if len(projects) == 1:
        sheets = ExcelSheet.query.join(File).filter(
            File.project_id == projects[0].id
        ).all()
    
    return render_template('labeling/select_project_sheet.html',
                         projects=projects,
                         sheets=sheets)

# ================================
# INTEGRAZIONE CON SISTEMA ML
# ================================

def create_template_from_ml_column(project_id, sheet_id, column_name, sample_data=None, analysis_type=None):
    """
    Crea un template di etichettatura basato su una colonna ML e avvia la generazione
    Chiamata dal sistema ML per integrare i due workflow
    """
    try:
        from app.models import Project, ExcelSheet, File
        
        # Verifica parametri
        project = Project.query.filter_by(id=project_id).first()
        if not project:
            return {'success': False, 'error': 'Progetto non trovato'}
            
        sheet = ExcelSheet.query.join(File).filter(
            ExcelSheet.id == sheet_id,
            File.project_id == project.id
        ).first()
        if not sheet:
            return {'success': False, 'error': 'Foglio non trovato'}
        
        # Carica dati colonna se non forniti
        if not sample_data:
            try:
                import pandas as pd
                file_path = sheet.file.get_file_path()
                df = pd.read_excel(file_path, sheet_name=sheet.name)
                
                if column_name not in df.columns:
                    return {'success': False, 'error': f'Colonna "{column_name}" non trovata'}
                
                # Campiona fino a 15 valori non vuoti
                sample_data = df[column_name].dropna().head(15).tolist()
            except Exception as e:
                logger.error(f"Errore nel caricamento dati colonna: {str(e)}")
                return {'success': False, 'error': f'Errore nel caricamento dati: {str(e)}'}
        
        # Determina tipo di analisi dalla colonna
        if not analysis_type:
            analysis_type = _detect_column_analysis_type(column_name, sample_data)
        
        # Seleziona template predefinito appropriato
        template_config = _get_ml_integration_template(analysis_type, column_name)
        
        # Crea template personalizzato per questa colonna
        template_name = f"ML-{analysis_type.title()}-{column_name}".replace('_', ' ')[:100]
        
        # Verifica se esiste già un template simile
        existing_template = LabelTemplate.query.filter_by(
            project_id=project.id,
            name=template_name
        ).first()
        
        if existing_template:
            # Usa template esistente ma aggiorna timestamp
            template = existing_template
            template.updated_at = datetime.utcnow()
        else:
            # Crea nuovo template
            template = LabelTemplate(
                project_id=project.id,
                created_by=project.owner_id,  # Usa l'owner del progetto
                name=template_name,
                description=template_config['description'].format(column_name=column_name),
                category=template_config['category'],
                system_prompt=template_config['system_prompt'],
                user_prompt_template=template_config['user_prompt_template'],
                preferred_model='anthropic/claude-3-haiku',  # Modello veloce per ML
                temperature=0.3,  # Più deterministico per consistenza
                max_tokens=800,
                expected_labels_count=template_config['expected_labels_count'],
                output_format='json'
            )
            
            db.session.add(template)
            db.session.flush()
        
        # Crea sessione di generazione automatica
        generation = LabelGeneration(
            project_id=project.id,
            sheet_id=sheet.id,
            template_id=template.id,
            created_by=project.owner_id,
            column_name=column_name,
            sample_data=sample_data[:10],  # Limita per performance
            status='pending'
        )
        
        db.session.add(generation)
        db.session.flush()
        
        # Genera etichette immediatamente
        logger.info(f"🚀 Avvio generazione ML per colonna '{column_name}' con template '{template.name}'")
        success = _generate_labels_with_ai(generation, template, sample_data[:10], column_name)
        
        if success:
            db.session.commit()
            
            # Conta suggerimenti creati
            suggestions_count = LabelSuggestion.query.filter_by(
                generation_id=generation.id
            ).count()
            
            return {
                'success': True,
                'message': f'Template creato e {suggestions_count} etichette generate per colonna "{column_name}"',
                'template_id': str(template.id),
                'generation_id': str(generation.id),
                'suggestions_count': suggestions_count,
                'template_name': template.name,
                'analysis_type': analysis_type,
                'review_url': f'/labeling/projects/{project.id}/generations/{generation.id}/review'
            }
        else:
            db.session.rollback()
            error_msg = generation.error_message or 'Errore nella generazione AI'
            return {
                'success': False,
                'error': f'Template creato ma generazione fallita: {error_msg}'
            }
            
    except Exception as e:
        logger.error(f"❌ Errore critico in create_template_from_ml_column: {str(e)}")
        db.session.rollback()
        return {
            'success': False,
            'error': f'Errore interno: {str(e)}'
        }

def _detect_column_analysis_type(column_name, sample_data):
    """Rileva automaticamente il tipo di analisi appropriato per una colonna"""
    column_lower = column_name.lower()
    
    # Analisi basata sul nome della colonna
    if any(keyword in column_lower for keyword in ['sentiment', 'opinione', 'giudizio', 'valutazione']):
        return 'sentiment'
    elif any(keyword in column_lower for keyword in ['emozione', 'emotion', 'feeling', 'umore']):
        return 'emotion'
    elif any(keyword in column_lower for keyword in ['tono', 'tone', 'stile', 'style']):
        return 'tone'
    elif any(keyword in column_lower for keyword in ['priorità', 'priority', 'urgenza', 'urgent']):
        return 'priority'
    elif any(keyword in column_lower for keyword in ['qualità', 'quality', 'rating', 'voto']):
        return 'quality'
    elif any(keyword in column_lower for keyword in ['argomento', 'topic', 'tema', 'subject']):
        return 'topic'
    elif any(keyword in column_lower for keyword in ['comportamento', 'behavior', 'azione', 'action']):
        return 'behavior'
    elif any(keyword in column_lower for keyword in ['intenzione', 'intent', 'obiettivo', 'goal']):
        return 'intent'
    elif any(keyword in column_lower for keyword in ['competenza', 'expertise', 'skill', 'livello']):
        return 'expertise'
    
    # Analisi basata sul contenuto (primi 5 campioni)
    sample_text = ' '.join([str(item)[:50] for item in sample_data[:5]]).lower()
    
    if any(keyword in sample_text for keyword in ['positivo', 'negativo', 'bello', 'brutto', 'buono', 'cattivo']):
        return 'sentiment'
    elif any(keyword in sample_text for keyword in ['felice', 'triste', 'arrabbiato', 'paura', 'gioia']):
        return 'emotion'
    elif any(keyword in sample_text for keyword in ['urgente', 'importante', 'critico', 'bassa', 'alta']):
        return 'priority'
    elif len(sample_text) > 100:  # Testi lunghi -> probabilmente topic analysis
        return 'topic'
    
    # Default: analisi sentiment (più generale)
    return 'sentiment'

def _get_ml_integration_template(analysis_type, column_name):
    """Restituisce configurazione template per integrazione ML"""
    templates_map = {
        'sentiment': {
            'category': 'sentiment',
            'description': 'Template ML automatico per analisi sentiment della colonna "{column_name}"',
            'system_prompt': 'Sei un esperto analista di sentiment integrato con sistema ML. Analizza il sentiment del testo in modo coerente e accurato.',
            'user_prompt_template': 'Analizza i dati della colonna "{column_name}" e genera etichette per sentiment:\n\n{sample_data}\n\nGenera 3-4 etichette precise per sentiment come: Positivo, Negativo, Neutro, Misto.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 4
        },
        'emotion': {
            'category': 'emotion',
            'description': 'Template ML automatico per analisi emozioni della colonna "{column_name}"',
            'system_prompt': 'Sei un esperto psicologo per analisi emozioni integrato con sistema ML. Identifica emozioni in modo preciso.',
            'user_prompt_template': 'Analizza i dati della colonna "{column_name}" e identifica le emozioni principali:\n\n{sample_data}\n\nGenera 5-6 etichette per emozioni come: Gioia, Tristezza, Rabbia, Paura, Sorpresa, Disgusto.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 6
        },
        'tone': {
            'category': 'tone',
            'description': 'Template ML automatico per analisi tono della colonna "{column_name}"',
            'system_prompt': 'Sei un esperto di comunicazione integrato con sistema ML. Analizza il tono e stile di comunicazione.',
            'user_prompt_template': 'Analizza i dati della colonna "{column_name}" e identifica il tono:\n\n{sample_data}\n\nGenera etichette per toni come: Formale, Informale, Professionale, Colloquiale, Ironico, Serio.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 6
        },
        'priority': {
            'category': 'priority',
            'description': 'Template ML automatico per analisi priorità della colonna "{column_name}"',
            'system_prompt': 'Sei un esperto di gestione priorità integrato con sistema ML. Classifica urgenza e importanza.',
            'user_prompt_template': 'Analizza i dati della colonna "{column_name}" e classifica per priorità:\n\n{sample_data}\n\nGenera etichette come: Urgente, Alta Priorità, Media Priorità, Bassa Priorità, Non Urgente.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 5
        },
        'quality': {
            'category': 'quality',
            'description': 'Template ML automatico per analisi qualità della colonna "{column_name}"',
            'system_prompt': 'Sei un esperto di valutazione qualità integrato con sistema ML. Valuta qualità e utilità del contenuto.',
            'user_prompt_template': 'Analizza i dati della colonna "{column_name}" e valuta la qualità:\n\n{sample_data}\n\nGenera etichette come: Eccellente, Molto Buona, Buona, Sufficiente, Insufficiente.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 5
        },
        'topic': {
            'category': 'topic',
            'description': 'Template ML automatico per analisi tematiche della colonna "{column_name}"',
            'system_prompt': 'Sei un esperto analista di contenuti integrato con sistema ML. Identifica temi e argomenti principali.',
            'user_prompt_template': 'Analizza i dati della colonna "{column_name}" e identifica i temi principali:\n\n{sample_data}\n\nGenera etichette per i temi più ricorrenti nel contenuto.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 8
        },
        'behavior': {
            'category': 'behavior',
            'description': 'Template ML automatico per analisi comportamentale della colonna "{column_name}"',
            'system_prompt': 'Sei un esperto analista comportamentale integrato con sistema ML. Classifica comportamenti e azioni.',
            'user_prompt_template': 'Analizza i dati della colonna "{column_name}" e classifica i comportamenti:\n\n{sample_data}\n\nGenera etichette per comportamenti come: Collaborativo, Competitivo, Passivo, Assertivo, Aggressivo.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 5
        },
        'intent': {
            'category': 'intent',
            'description': 'Template ML automatico per analisi intenzioni della colonna "{column_name}"',
            'system_prompt': 'Sei un esperto di user experience integrato con sistema ML. Identifica intenzioni e obiettivi.',
            'user_prompt_template': 'Analizza i dati della colonna "{column_name}" e identifica le intenzioni:\n\n{sample_data}\n\nGenera etichette per intenzioni come: Richiesta Info, Reclamo, Complimento, Suggerimento, Richiesta Supporto.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 6
        },
        'expertise': {
            'category': 'expertise',
            'description': 'Template ML automatico per analisi expertise della colonna "{column_name}"',
            'system_prompt': 'Sei un esperto formatore integrato con sistema ML. Valuta livelli di competenza tecnica.',
            'user_prompt_template': 'Analizza i dati della colonna "{column_name}" e valuta il livello di expertise:\n\n{sample_data}\n\nGenera etichette come: Principiante, Intermedio, Avanzato, Esperto, Specialista.\nRispondi in formato JSON con: name, description, category, color.',
            'expected_labels_count': 5
        }
    }
    
    # Restituisci template specifico o default sentiment
    return templates_map.get(analysis_type, templates_map['sentiment'])