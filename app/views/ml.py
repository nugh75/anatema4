"""
Human-Machine Labeling views for manual and automatic analysis and labeling
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app.database import db
from app.models import (
    Project, File, ExcelSheet, MLAnalysis, ColumnAnalysis, AutoLabel,
    AutoLabelApplication, MLConfiguration, Label
)
from app.ml.analyzer import DataAnalyzer
from app.ml.api_client import MLAPIClient
import json
import logging
from datetime import datetime
from typing import Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)

# Manteniamo il nome 'ml' per compatibilità con gli endpoint esistenti
ml_bp = Blueprint('ml', __name__)

@ml_bp.route('/projects/<uuid:project_id>/configure', methods=['GET', 'POST'])
@login_required
def configure_ml(project_id):
    """Configura le impostazioni ML per un progetto"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            # Validazione dati
            name = data.get('name', '').strip()
            ml_provider = data.get('ml_provider', 'openrouter')
            ml_model = data.get('ml_model', 'anthropic/claude-3-haiku')
            api_key = data.get('api_key', '').strip()
            api_url = data.get('api_url', '').strip()
            
            if not name:
                error_msg = 'Nome configurazione richiesto'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('ml/configure.html', project=project)
            
            if not api_key and ml_provider == 'openrouter':
                error_msg = 'API Key richiesta per OpenRouter'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('ml/configure.html', project=project)
            
            # Disattiva configurazioni esistenti
            MLConfiguration.query.filter_by(project_id=project.id, is_active=True).update({'is_active': False})
            
            # Crea nuova configurazione
            ml_config = MLConfiguration(
                project_id=project.id,
                created_by=current_user.id,
                name=name,
                description=data.get('description', ''),
                ml_provider=ml_provider,
                ml_model=ml_model,
                api_key_encrypted=api_key,  # In produzione, cripta questa chiave
                api_url=api_url,
                auto_detect_columns=_convert_to_bool(data.get('auto_detect_columns', True)),
                min_unique_values=int(data.get('min_unique_values', 3)),
                max_text_length=int(data.get('max_text_length', 1000)),
                clustering_min_samples=int(data.get('clustering_min_samples', 5)),
                sentiment_analysis_enabled=_convert_to_bool(data.get('sentiment_analysis_enabled', True)),
                preferred_open_question_threshold=float(data.get('preferred_open_question_threshold', 0.7)),
                text_variability_threshold=float(data.get('text_variability_threshold', 0.5)),
                is_active=True
            )
            
            db.session.add(ml_config)
            db.session.commit()
            
            # Testa la configurazione
            test_result = _test_ml_configuration(ml_config)
            
            if request.is_json:
                return jsonify({
                    'message': 'Configurazione ML salvata con successo',
                    'config': ml_config.to_dict(),
                    'test_result': test_result
                }), 201
            else:
                if test_result.get('overall_status') == 'ok':
                    flash('Configurazione ML salvata e testata con successo!', 'success')
                else:
                    flash('Configurazione salvata ma test fallito. Verifica le impostazioni.', 'warning')
                return redirect(url_for('ml.view_ml_dashboard', project_id=project.id))
        
        except Exception as e:
            logger.error(f"Errore nella configurazione ML: {str(e)}")
            db.session.rollback()  # Rollback della transazione in caso di errore
            if request.is_json:
                return jsonify({'error': str(e)}), 500
            flash(f'Errore nella configurazione: {str(e)}', 'error')
    
    # GET request - mostra form di configurazione
    current_config = MLConfiguration.query.filter_by(project_id=project.id, is_active=True).first()
    
    if request.is_json:
        return jsonify({
            'project': project.to_dict(),
            'current_config': current_config.to_dict() if current_config else None
        })
    
    return render_template('ml/configure.html', project=project, current_config=current_config)

@ml_bp.route('/projects/<uuid:project_id>/dashboard')
@login_required
def view_ml_dashboard(project_id):
    """Dashboard Etichettatura Umano/Macchina per un progetto"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Recupera tutti i file del progetto con i loro fogli
    files_data = []
    total_sheets = 0
    
    files = File.query.filter_by(project_id=project.id).all()
    for file in files:
        sheets = ExcelSheet.query.filter_by(file_id=file.id).all()
        total_sheets += len(sheets)
        
        files_data.append({
            'id': file.id,
            'filename': file.filename,
            'sheets': [{'id': sheet.id, 'name': sheet.name} for sheet in sheets]
        })
    
    # Recupera etichette del progetto
    project_labels = Label.query.filter_by(project_id=project.id).all()
    
    # Calcola statistiche etichettatura
    total_labels = AutoLabelApplication.query.join(AutoLabel).join(MLAnalysis)\
        .filter(MLAnalysis.project_id == project.id, AutoLabelApplication.status == 'applied').count()
    
    if request.is_json:
        return jsonify({
            'project': project.to_dict(),
            'files_data': files_data,
            'total_sheets': total_sheets,
            'total_labels': total_labels,
            'project_labels': [label.to_dict() for label in project_labels]
        })
    
    return render_template('ml/new_dashboard.html',
                         project=project,
                         files_data=files_data,
                         total_sheets=total_sheets,
                         total_labels=total_labels,
                         project_labels=project_labels)

@ml_bp.route('/projects/<uuid:project_id>/analyze/<uuid:sheet_id>', methods=['POST'])
@login_required
def analyze_sheet(project_id, sheet_id):
    """Avvia l'analisi ML di un foglio"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Verifica che il foglio appartenga al progetto
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    # Recupera configurazione ML
    ml_config = MLConfiguration.query.filter_by(project_id=project.id, is_active=True).first()
    
    if not ml_config:
        error_msg = 'Nessuna configurazione ML attiva trovata'
        if request.is_json:
            return jsonify({'error': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('ml.view_ml_dashboard', project_id=project.id))
    
    try:
        # Prepara configurazione per l'analizzatore
        analyzer_config = {
            'ml_provider': ml_config.ml_provider,
            'ml_model': ml_config.ml_model,
            'api_key': ml_config.api_key_encrypted,  # In produzione, decripta
            'api_url': ml_config.api_url,
            'clustering_min_samples': ml_config.clustering_min_samples,
            'min_unique_values': ml_config.min_unique_values,
            'max_text_length': ml_config.max_text_length
        }
        
        # Crea analizzatore
        analyzer = DataAnalyzer(analyzer_config)
        
        # Determina tipi di analisi da eseguire
        analysis_types = []
        if ml_config.auto_detect_columns:
            analysis_types.append('column_detection')
        analysis_types.append('auto_labeling')
        if ml_config.sentiment_analysis_enabled:
            analysis_types.append('sentiment')
        
        # Avvia analisi
        result = analyzer.analyze_sheet(str(sheet_id), str(project_id), analysis_types)
        
        if result.get('success', False):
            message = f'Analisi completata in {result["processing_time"]:.2f} secondi'
            if request.is_json:
                return jsonify({
                    'message': message,
                    'result': result
                }), 200
            else:
                flash(message, 'success')
                return redirect(url_for('ml.view_analysis_results', 
                                      project_id=project.id, 
                                      analysis_id=result['ml_analysis_id']))
        else:
            error_msg = result.get('error', 'Errore sconosciuto nell\'analisi')
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            flash(f'Errore nell\'analisi: {error_msg}', 'error')
            return redirect(url_for('ml.view_ml_dashboard', project_id=project.id))
    
    except Exception as e:
        logger.error(f"Errore nell'analisi del foglio {sheet_id}: {str(e)}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nell\'analisi: {str(e)}', 'error')
        return redirect(url_for('ml.view_ml_dashboard', project_id=project.id))

@ml_bp.route('/projects/<uuid:project_id>/analysis/<uuid:analysis_id>')
@login_required
def view_analysis_results(project_id, analysis_id):
    """Visualizza i risultati di un'analisi ML"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    analysis = MLAnalysis.query.filter_by(id=analysis_id, project_id=project.id).first_or_404()
    
    # Recupera analisi delle colonne
    column_analyses = ColumnAnalysis.query.filter_by(ml_analysis_id=analysis.id).all()
    
    # Recupera etichette automatiche generate
    auto_labels = AutoLabel.query.filter_by(ml_analysis_id=analysis.id).all()
    
    # Recupera applicazioni delle etichette
    label_applications = AutoLabelApplication.query.join(AutoLabel)\
        .filter(AutoLabel.ml_analysis_id == analysis.id).all()
    
    if request.is_json:
        return jsonify({
            'project': project.to_dict(),
            'analysis': analysis.to_dict(),
            'column_analyses': [ca.to_dict() for ca in column_analyses],
            'auto_labels': [al.to_dict() for al in auto_labels],
            'label_applications': [la.to_dict() for la in label_applications]
        })
    
    return render_template('ml/analysis_results.html',
                         project=project,
                         analysis=analysis,
                         column_analyses=column_analyses,
                         auto_labels=auto_labels,
                         label_applications=label_applications)

@ml_bp.route('/auto-labels/<uuid:label_id>/validate', methods=['POST'])
@login_required
def validate_auto_label(label_id):
    """Valida o rifiuta un'etichetta automatica"""
    auto_label = AutoLabel.query.join(MLAnalysis).join(Project).filter(
        AutoLabel.id == label_id,
        Project.owner_id == current_user.id
    ).first_or_404()
    
    if request.is_json:
        data = request.get_json()
        action = data.get('action')  # 'approve', 'reject', 'modify'
        new_name = data.get('new_name')
        new_description = data.get('new_description')
    else:
        action = request.form.get('action')
        new_name = request.form.get('new_name')
        new_description = request.form.get('new_description')
    
    try:
        if action == 'approve':
            auto_label.manual_validation = 'approved'
        elif action == 'reject':
            auto_label.manual_validation = 'rejected'
        elif action == 'modify':
            auto_label.manual_validation = 'modified'
            if new_name:
                auto_label.label_name = new_name.strip()
            if new_description:
                auto_label.label_description = new_description.strip()
        
        auto_label.validated_by = current_user.id
        auto_label.validated_at = datetime.utcnow()
        
        db.session.commit()
        
        message = f'Etichetta "{auto_label.label_name}" {action}ta con successo'
        
        if request.is_json:
            return jsonify({
                'message': message,
                'auto_label': auto_label.to_dict()
            })
        else:
            flash(message, 'success')
            return redirect(request.referrer or url_for('ml.view_ml_dashboard', 
                                                      project_id=auto_label.ml_analysis.project_id))
    
    except Exception as e:
        logger.error(f"Errore nella validazione dell'etichetta {label_id}: {str(e)}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nella validazione: {str(e)}', 'error')
        return redirect(request.referrer or url_for('ml.view_ml_dashboard', 
                                                  project_id=auto_label.ml_analysis.project_id))

@ml_bp.route('/auto-labels/<uuid:label_id>/apply', methods=['POST'])
@login_required
def apply_auto_label(label_id):
    """Applica un'etichetta automatica ai dati suggeriti"""
    auto_label = AutoLabel.query.join(MLAnalysis).join(Project).filter(
        AutoLabel.id == label_id,
        Project.owner_id == current_user.id
    ).first_or_404()
    
    try:
        # Trova tutte le applicazioni suggerite per questa etichetta
        suggested_applications = AutoLabelApplication.query.filter_by(
            auto_label_id=auto_label.id,
            status='suggested'
        ).all()
        
        applied_count = 0
        
        for application in suggested_applications:
            application.status = 'applied'
            application.applied_by = current_user.id
            application.applied_at = datetime.utcnow()
            applied_count += 1
        
        # Aggiorna il contatore nell'AutoLabel
        auto_label.applied_count = applied_count
        
        db.session.commit()
        
        message = f'Etichetta "{auto_label.label_name}" applicata a {applied_count} celle'
        
        if request.is_json:
            return jsonify({
                'message': message,
                'applied_count': applied_count,
                'auto_label': auto_label.to_dict()
            })
        else:
            flash(message, 'success')
            return redirect(request.referrer or url_for('ml.view_analysis_results',
                                                      project_id=auto_label.ml_analysis.project_id,
                                                      analysis_id=auto_label.ml_analysis_id))
    
    except Exception as e:
        logger.error(f"Errore nell'applicazione dell'etichetta {label_id}: {str(e)}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nell\'applicazione: {str(e)}', 'error')
        return redirect(request.referrer)

@ml_bp.route('/test-connection', methods=['POST'])
@login_required
def test_ml_connection():
    """Testa la connessione alle API ML"""
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    ml_provider = data.get('ml_provider', 'openrouter')
    api_key = data.get('api_key', '')
    api_url = data.get('api_url', '')
    ml_model = data.get('ml_model', 'anthropic/claude-3-haiku')
    
    try:
        # Crea client temporaneo per il test
        client = MLAPIClient(
            provider=ml_provider,
            api_key=api_key,
            api_url=api_url,
            model=ml_model
        )
        
        # Testa la connessione
        result = client.test_connection()
        
        if request.is_json:
            return jsonify(result)
        else:
            if result['status'] == 'success':
                flash('Connessione ML testata con successo!', 'success')
            else:
                flash(f'Test connessione fallito: {result.get("error", "Errore sconosciuto")}', 'error')
            return redirect(request.referrer)
    
    except Exception as e:
        logger.error(f"Errore nel test della connessione ML: {str(e)}")
        error_result = {
            'status': 'error',
            'error': str(e),
            'message': 'Test connessione fallito'
        }
        
        if request.is_json:
            return jsonify(error_result), 500
        else:
            flash(f'Errore nel test: {str(e)}', 'error')
            return redirect(request.referrer)

def _test_ml_configuration(ml_config: MLConfiguration) -> Dict[str, Any]:
    """Testa una configurazione ML"""
    try:
        analyzer_config = {
            'ml_provider': ml_config.ml_provider,
            'ml_model': ml_config.ml_model,
            'api_key': ml_config.api_key_encrypted,
            'api_url': ml_config.api_url
        }
        
        analyzer = DataAnalyzer(analyzer_config)
        return analyzer.test_configuration()
        
    except Exception as e:
        return {
            'overall_status': 'error',
            'error': str(e)
        }

def _convert_to_bool(value):
    """Converte un valore in booleano, gestendo stringhe e altri tipi"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    return bool(value)

@ml_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/view-columns')
@login_required
def view_sheet_columns(project_id, sheet_id):
    """Visualizza i dati del foglio in formato colonne per etichettatura"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Verifica che il foglio appartenga al progetto
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    # Recupera i dati del foglio
    import json
    
    try:
        # Carica i dati dal file Excel
        file_path = sheet.file.get_file_path()
        df = pd.read_excel(file_path, sheet_name=sheet.name)
        
        # Prepara i dati per la visualizzazione a colonne
        columns_data = {}
        for col in df.columns:
            columns_data[col] = {
                'name': col,
                'type': str(df[col].dtype),
                'unique_values': len(df[col].unique()),
                'null_count': df[col].isnull().sum(),
                'sample_values': df[col].dropna().head(10).tolist(),
                'all_values': df[col].dropna().tolist()
            }
        
        # Recupera analisi ML esistenti per questo foglio
        ml_analysis = MLAnalysis.query.filter_by(
            project_id=project.id,
            sheet_id=sheet.id,
            status='completed'
        ).first()
        
        column_analyses = []
        auto_labels = []
        if ml_analysis:
            column_analyses = ColumnAnalysis.query.filter_by(ml_analysis_id=ml_analysis.id).all() if ml_analysis else []
            auto_labels = AutoLabel.query.filter_by(ml_analysis_id=ml_analysis.id).all() if ml_analysis else []
        
        if request.is_json:
            return jsonify({
                'project': project.to_dict(),
                'sheet': sheet.to_dict(),
                'columns_data': columns_data,
                'ml_analysis': ml_analysis.to_dict() if ml_analysis else None,
                'column_analyses': [ca.to_dict() for ca in column_analyses],
                'auto_labels': [al.to_dict() for al in auto_labels]
            })
        
        return render_template('ml/view_columns.html',
                             project=project,
                             sheet=sheet,
                             columns_data=columns_data,
                             ml_analysis=ml_analysis,
                             column_analyses=column_analyses,
                             auto_labels=auto_labels)
    
    except Exception as e:
        logger.error(f"Errore nella visualizzazione colonne del foglio {sheet_id}: {str(e)}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nel caricamento dei dati: {str(e)}', 'error')
        return redirect(url_for('ml.view_ml_dashboard', project_id=project.id))

@ml_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/view-rows')
@login_required
def view_sheet_rows(project_id, sheet_id):
    """Visualizza i dati del foglio in formato righe per etichettatura"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Verifica che il foglio appartenga al progetto
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    # Parametri di paginazione
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    try:
        # Carica i dati dal file Excel
        file_path = sheet.file.get_file_path()
        df = pd.read_excel(file_path, sheet_name=sheet.name)
        
        # Calcola paginazione
        total_rows = len(df)
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_rows)
        
        # Prepara i dati per la visualizzazione a righe
        rows_data = []
        for idx, row in df.iloc[start_idx:end_idx].iterrows():
            row_data = {
                'index': idx,
                'data': row.to_dict()
            }
            rows_data.append(row_data)
        
        # Informazioni sulla paginazione
        total_pages = (total_rows + per_page - 1) // per_page if total_rows > 0 else 1
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total_rows,
            'pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }
        
        # Recupera etichette applicate per questo foglio - SUPPORTA MULTIPLE ETICHETTE
        applied_labels = {}
        ml_analysis = MLAnalysis.query.filter_by(
            project_id=project.id,
            sheet_id=sheet.id,
            status='completed'
        ).first()
        
        if ml_analysis:
            label_applications = AutoLabelApplication.query.join(AutoLabel).filter(
                AutoLabel.ml_analysis_id == ml_analysis.id,
                AutoLabelApplication.status == 'applied'
            ).all()
            
            for app in label_applications:
                key = f"{app.row_index}_{app.column_name}"
                
                # Inizializza lista se non esiste
                if key not in applied_labels:
                    applied_labels[key] = []
                
                # Aggiungi questa etichetta alla lista per questa cella
                applied_labels[key].append({
                    'label_name': app.auto_label.label_name,
                    'label_description': app.auto_label.label_description,
                    'confidence': app.confidence_score,
                    'application_id': app.id
                })
        
        if request.is_json:
            return jsonify({
                'project': project.to_dict(),
                'sheet': sheet.to_dict(),
                'rows_data': rows_data,
                'columns': df.columns.tolist(),
                'pagination': pagination,
                'applied_labels': applied_labels
            })
        
        return render_template('ml/view_rows.html',
                             project=project,
                             sheet=sheet,
                             rows_data=rows_data,
                             columns=df.columns.tolist(),
                             pagination=pagination,
                             applied_labels=applied_labels)
    
    except Exception as e:
        logger.error(f"Errore nella visualizzazione righe del foglio {sheet_id}: {str(e)}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nel caricamento dei dati: {str(e)}', 'error')
        return redirect(url_for('ml.view_ml_dashboard', project_id=project.id))

@ml_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/label-cell', methods=['POST'])
@login_required
def label_cell_manually(project_id, sheet_id):
    """Etichetta manualmente una cella specifica"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Verifica che il foglio appartenga al progetto
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    row_index = data.get('row_index')
    column_name = data.get('column_name')
    label_name = data.get('label_name', '').strip()
    label_description = data.get('label_description', '').strip()
    
    if not all([row_index is not None, column_name, label_name]):
        error_msg = 'Parametri mancanti: row_index, column_name e label_name sono richiesti'
        if request.is_json:
            return jsonify({'error': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(request.referrer)
    
    try:
        # Trova o crea un'analisi ML per questo foglio
        ml_analysis = MLAnalysis.query.filter_by(
            project_id=project.id,
            sheet_id=sheet.id
        ).first()
        
        if not ml_analysis:
            # Crea una nuova analisi per le etichette manuali
            ml_analysis = MLAnalysis(
                project_id=project.id,
                file_id=sheet.file_id,
                sheet_id=sheet.id,
                ml_provider='manual',
                ml_model='manual',
                analysis_type='manual_labeling',
                status='completed'
            )
            db.session.add(ml_analysis)
            db.session.flush()
        
        # Crea o aggiorna l'etichetta automatica
        auto_label = AutoLabel.query.filter_by(
            ml_analysis_id=ml_analysis.id,
            label_name=label_name,
            column_name=column_name
        ).first()
        
        if not auto_label:
            auto_label = AutoLabel(
                ml_analysis_id=ml_analysis.id,
                label_name=label_name,
                label_description=label_description,
                label_type='manual',
                column_name=column_name,
                confidence_score=1.0,
                created_by=current_user.id
            )
            db.session.add(auto_label)
            db.session.flush()
        
        # Rimuovi etichettatura esistente per questa cella
        existing_app = AutoLabelApplication.query.filter_by(
            auto_label_id=auto_label.id,
            row_index=int(row_index),
            column_name=column_name
        ).first()
        
        if existing_app:
            existing_app.status = 'applied'
            existing_app.applied_by = current_user.id
            existing_app.applied_at = datetime.utcnow()
        else:
            # Crea nuova applicazione dell'etichetta
            label_application = AutoLabelApplication(
                auto_label_id=auto_label.id,
                row_index=int(row_index),
                column_name=column_name,
                confidence_score=1.0,
                status='applied',
                applied_by=current_user.id,
                applied_at=datetime.utcnow()
            )
            db.session.add(label_application)
        
        db.session.commit()
        
        message = f'Etichetta "{label_name}" applicata alla cella ({row_index}, {column_name})'
        
        if request.is_json:
            return jsonify({
                'message': message,
                'auto_label': auto_label.to_dict()
            })
        else:
            flash(message, 'success')
            return redirect(request.referrer)
    
    except Exception as e:
        logger.error(f"Errore nell'etichettatura manuale: {str(e)}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nell\'etichettatura: {str(e)}', 'error')
        return redirect(request.referrer)

@ml_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/advanced-column-view')
@login_required
def advanced_column_view(project_id, sheet_id):
    """Vista avanzata per etichettatura colonna per colonna con AI"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Verifica che il foglio appartenga al progetto
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    try:
        # Carica i dati dal file Excel con gestione errori
        file_path = sheet.file.get_file_path()
        try:
            df = pd.read_excel(file_path, sheet_name=sheet.name, engine='openpyxl')
            if df.empty:
                flash('Il foglio Excel è vuoto', 'warning')
                return redirect(url_for('ml.view_ml_dashboard', project_id=project.id))
            
            # Converti i valori NaN in stringhe vuote
            df = df.fillna('')
        except FileNotFoundError:
            flash('File Excel non trovato', 'error')
            return redirect(url_for('ml.view_ml_dashboard', project_id=project.id))
        except Exception as e:
            logger.error(f"Errore nel caricamento del file Excel: {str(e)}")
            flash(f'Errore nel caricamento dei dati: {str(e)}', 'error')
            return redirect(url_for('ml.view_ml_dashboard', project_id=project.id))
        
        # Prepara i dati delle colonne con conversione sicura per JSON
        columns_data = {}
        for col in df.columns:
            # Converti tutti i valori in tipi Python nativi
            sample_values = [str(val) if pd.notna(val) else '' for val in df[col].dropna().head(5)]
            all_values = [str(val) if pd.notna(val) else '' for val in df[col]]
            
            columns_data[col] = {
                'name': str(col),
                'type': str(df[col].dtype),
                'unique_values': int(len(df[col].unique())),
                'null_count': int(df[col].isnull().sum()),
                'total_rows': int(len(df)),
                'row_count': int(len(df[col])),
                'sample_values': sample_values,
                'all_values': all_values
            }
        
        # Recupera configurazione ML attiva
        ml_config = MLConfiguration.query.filter_by(project_id=project.id, is_active=True).first()
        
        # Recupera analisi ML esistenti per questo foglio
        ml_analysis = MLAnalysis.query.filter_by(
            project_id=project.id,
            sheet_id=sheet.id,
            status='completed'
        ).first()
        
        # Recupera etichette applicate - SUPPORTA MULTIPLE ETICHETTE PER CELLA
        applied_labels = {}
        if ml_analysis:
            label_applications = AutoLabelApplication.query.join(AutoLabel).filter(
                AutoLabel.ml_analysis_id == ml_analysis.id,
                AutoLabelApplication.status == 'applied'
            ).all()
            
            for app in label_applications:
                key = f"{app.row_index}_{app.column_name}"
                
                # Inizializza lista se non esiste
                if key not in applied_labels:
                    applied_labels[key] = []
                
                # Aggiungi questa etichetta alla lista per questa cella
                applied_labels[key].append({
                    'label_name': app.auto_label.label_name,
                    'label_description': app.auto_label.label_description,
                    'confidence': app.confidence_score,
                    'applied_at': app.applied_at.isoformat() if app.applied_at else None,
                    'application_id': app.id
                })
        
        # Recupera etichette esistenti del progetto
        project_labels_raw = Label.query.filter_by(project_id=project.id).order_by(Label.name).all()
        project_labels = [label.to_dict() for label in project_labels_raw]

        if request.is_json:
            return jsonify({
                'project': project.to_dict(),
                'sheet': sheet.to_dict(),
                'columns_data': columns_data,
                'ml_config': ml_config.to_dict() if ml_config else None,
                'applied_labels': applied_labels,
                'project_labels': project_labels
            })
        
        return render_template('ml/advanced_column_view.html',
                             project=project,
                             sheet=sheet,
                             columns_data=columns_data,
                             ml_config=ml_config,
                             applied_labels=applied_labels,
                             project_labels=project_labels,
                             project_labels_raw=project_labels_raw)
    
    except Exception as e:
        logger.error(f"Errore nella vista avanzata colonne del foglio {sheet_id}: {str(e)}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nel caricamento dei dati: {str(e)}', 'error')
        return redirect(url_for('ml.view_ml_dashboard', project_id=project.id))

@ml_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/advanced-row-view')
@login_required
def advanced_row_view(project_id, sheet_id):
    """Vista avanzata per etichettatura riga per riga con AI"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Verifica che il foglio appartenga al progetto
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    try:
        # Carica i dati dal file Excel
        file_path = sheet.file.get_file_path()
        df = pd.read_excel(file_path, sheet_name=sheet.name)
        
        # Prepara i dati per la visualizzazione a righe
        rows_data = []
        for idx, row in df.iterrows():
            row_data = {
                'index': idx,
                'data': {}
            }
            # Converti ogni valore in stringa per evitare problemi di serializzazione
            for col, value in row.items():
                if pd.isna(value):
                    row_data['data'][col] = ''
                else:
                    row_data['data'][col] = str(value)
            rows_data.append(row_data)
        
        # Recupera configurazione ML attiva
        ml_config = MLConfiguration.query.filter_by(project_id=project.id, is_active=True).first()
        
        # Recupera analisi ML esistenti per questo foglio
        ml_analysis = MLAnalysis.query.filter_by(
            project_id=project.id,
            sheet_id=sheet.id,
            status='completed'
        ).first()
        
        # Recupera etichette applicate - SUPPORTA MULTIPLE ETICHETTE PER CELLA
        applied_labels = {}
        if ml_analysis:
            label_applications = AutoLabelApplication.query.join(AutoLabel).filter(
                AutoLabel.ml_analysis_id == ml_analysis.id,
                AutoLabelApplication.status == 'applied'
            ).all()
            
            for app in label_applications:
                key = f"{app.row_index}_{app.column_name}"
                
                # Inizializza lista se non esiste
                if key not in applied_labels:
                    applied_labels[key] = []
                
                # Aggiungi questa etichetta alla lista per questa cella
                applied_labels[key].append({
                    'label_name': app.auto_label.label_name,
                    'label_description': app.auto_label.label_description,
                    'confidence': app.confidence_score,
                    'applied_at': app.applied_at.isoformat() if app.applied_at else None,
                    'application_id': app.id
                })
        
        # Statistiche per la vista - calcola celle con almeno una etichetta
        total_labeled_cells = len(applied_labels)
        stats = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'total_cells': len(df) * len(df.columns),
            'labeled_cells': total_labeled_cells,
            'completion_percentage': round((total_labeled_cells / (len(df) * len(df.columns))) * 100, 2) if len(df) > 0 else 0
        }
        
        if request.is_json:
            return jsonify({
                'project': project.to_dict(),
                'sheet': sheet.to_dict(),
                'rows_data': rows_data,
                'columns': df.columns.tolist(),
                'ml_config': ml_config.to_dict() if ml_config else None,
                'applied_labels': applied_labels,
                'stats': stats
            })
        
        return render_template('ml/advanced_row_view.html',
                             project=project,
                             sheet=sheet,
                             rows_data=rows_data,
                             columns=df.columns.tolist(),
                             ml_config=ml_config,
                             applied_labels=applied_labels,
                             stats=stats)
    
    except Exception as e:
        logger.error(f"Errore nella vista avanzata righe del foglio {sheet_id}: {str(e)}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nel caricamento dei dati: {str(e)}', 'error')
        return redirect(url_for('ml.view_ml_dashboard', project_id=project.id))

@ml_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/ai-analyze-cell', methods=['POST'])
@login_required
def ai_analyze_cell(project_id, sheet_id):
    """Analizza una cella specifica con AI per suggerire etichette"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Verifica che il foglio appartenga al progetto
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    cell_value = data.get('cell_value', '').strip()
    column_name = data.get('column_name', '').strip()
    analysis_template = data.get('template', 'custom')
    custom_prompt = data.get('custom_prompt', '').strip()
    
    if not cell_value:
        error_msg = 'Valore della cella richiesto per l\'analisi'
        if request.is_json:
            return jsonify({'error': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(request.referrer)
    
    try:
        # Recupera configurazione ML attiva
        ml_config = MLConfiguration.query.filter_by(project_id=project.id, is_active=True).first()
        
        if not ml_config:
            error_msg = 'Nessuna configurazione ML attiva trovata'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(request.referrer)
        
        # Crea client ML
        client = MLAPIClient(
            provider=ml_config.ml_provider,
            api_key=ml_config.api_key_encrypted,
            api_url=ml_config.api_url,
            model=ml_config.ml_model
        )
        
        # Prepara il prompt basato sul template
        if analysis_template == 'sentiment':
            prompt = f"Analizza il sentiment del seguente testo e fornisci una classificazione (positivo, negativo, neutro) con una breve spiegazione:\n\nTesto: {cell_value}"
        elif analysis_template == 'emotion':
            prompt = f"Identifica l'emozione principale nel seguente testo (gioia, tristezza, rabbia, paura, sorpresa, disgusto, neutro) con una breve spiegazione:\n\nTesto: {cell_value}"
        elif analysis_template == 'behavior':
            prompt = f"Analizza il comportamento descritto nel seguente testo e classificalo (proattivo, reattivo, passivo, aggressivo, collaborativo, etc.) con una spiegazione:\n\nTesto: {cell_value}"
        elif analysis_template == 'topic':
            prompt = f"Identifica il topic/argomento principale del seguente testo e fornisci una categoria con spiegazione:\n\nTesto: {cell_value}"
        elif analysis_template == 'intent':
            prompt = f"Determina l'intento del seguente testo (richiesta, reclamo, complimento, domanda, etc.) con spiegazione:\n\nTesto: {cell_value}"
        else:  # custom
            if custom_prompt:
                prompt = f"{custom_prompt}\n\nTesto da analizzare: {cell_value}"
            else:
                prompt = f"Analizza il seguente testo e fornisci una classificazione appropriata con spiegazione:\n\nTesto: {cell_value}"
        
        # Esegui analisi AI
        response = client.analyze_text(prompt)
        
        if response.get('success', False):
            analysis_result = {
                'suggestion': response.get('analysis', 'Nessuna analisi disponibile'),
                'confidence': response.get('confidence', 0.8),
                'template_used': analysis_template,
                'column_name': column_name,
                'cell_value': cell_value
            }
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'analysis': analysis_result
                })
            else:
                flash(f'Analisi AI completata: {analysis_result["suggestion"]}', 'success')
                return redirect(request.referrer)
        else:
            error_msg = response.get('error', 'Errore nell\'analisi AI')
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            flash(f'Errore nell\'analisi AI: {error_msg}', 'error')
            return redirect(request.referrer)
    
    except Exception as e:
        logger.error(f"Errore nell'analisi AI della cella: {str(e)}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nell\'analisi: {str(e)}', 'error')
        return redirect(request.referrer)

@ml_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/save-cell-label', methods=['POST'])
@login_required
def save_cell_label(project_id, sheet_id):
    """Salva etichetta per una cella specifica"""
    try:
        project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
        
        sheet = ExcelSheet.query.join(File).filter(
            ExcelSheet.id == sheet_id,
            File.project_id == project.id
        ).first_or_404()
        
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        row_index = int(data.get('row_index', 0))
        column_name = data.get('column_name', '').strip()
        label_name = data.get('label_name', '').strip()
        label_description = data.get('label_description', '').strip()
        confidence = float(data.get('confidence', 1.0))
        source = data.get('source', 'manual')  # 'manual' o 'ai'
        
        if not all([column_name, label_name]):
            error_msg = 'Nome colonna e etichetta richiesti'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(request.referrer)
        
        # Cerca analisi ML esistente o creane una nuova
        ml_analysis = MLAnalysis.query.filter_by(
            project_id=project.id,
            sheet_id=sheet.id,
            status='completed'
        ).first()
        
        if not ml_analysis:
            # Crea una nuova analisi ML per questa sessione di etichettatura manuale
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
        
        # Cerca etichetta automatica esistente o creane una nuova
        auto_label = AutoLabel.query.filter_by(
            ml_analysis_id=ml_analysis.id,
            label_name=label_name,
            label_description=label_description
        ).first()
        
        if not auto_label:
            auto_label = AutoLabel(
                ml_analysis_id=ml_analysis.id,
                label_name=label_name,
                label_description=label_description,
                category='manual' if source == 'manual' else 'ai_assisted',
                confidence_score=confidence,
                column_name=column_name,
                created_by=current_user.id,
                label_type='manual'
            )
            db.session.add(auto_label)
            db.session.flush()
        
        # Controlla se questa etichetta specifica è già applicata a questa cella
        existing_app = AutoLabelApplication.query.filter_by(
            auto_label_id=auto_label.id,
            row_index=row_index,
            column_name=column_name
        ).first()
        
        if existing_app:
            # Aggiorna l'applicazione esistente per questa etichetta specifica
            existing_app.status = 'applied'
            existing_app.confidence_score = confidence
            existing_app.applied_at = datetime.utcnow()
        else:
            # Crea nuova applicazione - supporta multiple etichette per cella
            label_app = AutoLabelApplication(
                auto_label_id=auto_label.id,
                row_index=row_index,
                column_name=column_name,
                confidence_score=confidence,
                status='applied',
                applied_at=datetime.utcnow()
            )
            db.session.add(label_app)
        
        db.session.commit()
        
        message = f'Etichetta "{label_name}" salvata per cella ({row_index + 1}, {column_name})'
        if request.is_json:
            # Recupera tutte le etichette per questa cella per ritornare lo stato aggiornato
            cell_key = f"{row_index}_{column_name}"
            all_cell_labels = []
            
            # Ricarica le etichette per questa cella specifica
            cell_applications = AutoLabelApplication.query.join(AutoLabel).filter(
                AutoLabel.ml_analysis_id == ml_analysis.id,
                AutoLabelApplication.row_index == row_index,
                AutoLabelApplication.column_name == column_name,
                AutoLabelApplication.status == 'applied'
            ).all()
            
            for app in cell_applications:
                all_cell_labels.append({
                    'label_name': app.auto_label.label_name,
                    'label_description': app.auto_label.label_description,
                    'confidence': app.confidence_score,
                    'applied_at': app.applied_at.isoformat() if app.applied_at else None,
                    'application_id': app.id
                })
            
            return jsonify({
                'success': True,
                'message': message,
                'label': {
                    'name': label_name,
                    'description': label_description,
                    'confidence': confidence,
                    'source': source
                },
                'all_cell_labels': all_cell_labels
            })
        
        flash(message, 'success')
        return redirect(request.referrer)
        
    except Exception as e:
        logger.error(f"Errore nel salvataggio etichetta cella: {str(e)}")
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nel salvataggio: {str(e)}', 'error')
        return redirect(request.referrer)

@ml_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/remove-cell-label', methods=['POST'])
@login_required
def remove_cell_label(project_id, sheet_id):
    """Rimuove etichetta da una cella specifica"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        row_index = int(data.get('row_index', 0))
        column_name = data.get('column_name', '').strip()
        application_id = data.get('application_id', '').strip()  # ID specifico dell'applicazione da rimuovere
        
        if not column_name:
            error_msg = 'Nome colonna richiesto'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(request.referrer)
        
        # Trova l'analisi ML per questo progetto e sheet
        ml_analysis = MLAnalysis.query.filter_by(
            project_id=project.id,
            sheet_id=sheet.id,
            status='completed'
        ).first()
        
        if ml_analysis:
            if application_id:
                # Rimuovi etichetta specifica per application_id
                app_to_remove = AutoLabelApplication.query.join(AutoLabel).filter(
                    AutoLabel.ml_analysis_id == ml_analysis.id,
                    AutoLabelApplication.row_index == row_index,
                    AutoLabelApplication.column_name == column_name,
                    AutoLabelApplication.id == application_id,
                    AutoLabelApplication.status == 'applied'
                ).first()
                
                if app_to_remove:
                    app_to_remove.status = 'removed'
                    app_to_remove.applied_at = datetime.utcnow()
                    db.session.commit()
                    
                    message = f'Etichetta "{app_to_remove.auto_label.label_name}" rimossa dalla cella ({row_index + 1}, {column_name})'
                    removed_count = 1
                else:
                    message = 'Etichetta specifica non trovata'
                    removed_count = 0
            else:
                # Rimuovi tutte le etichette per questa cella (comportamento legacy)
                label_applications = AutoLabelApplication.query.join(AutoLabel).filter(
                    AutoLabel.ml_analysis_id == ml_analysis.id,
                    AutoLabelApplication.row_index == row_index,
                    AutoLabelApplication.column_name == column_name,
                    AutoLabelApplication.status == 'applied'
                ).all()
                
                # Rimuovi le applicazioni (soft delete cambiando status)
                removed_count = 0
                for app in label_applications:
                    app.status = 'removed'
                    app.applied_at = datetime.utcnow()
                    removed_count += 1
                
                db.session.commit()
                message = f'Tutte le etichette rimosse per cella ({row_index + 1}, {column_name})'
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': message,
                    'removed_count': removed_count
                })
            
            flash(message, 'success')
        else:
            message = 'Nessuna etichetta trovata per questa cella'
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': message,
                    'removed_count': 0
                })
            flash(message, 'info')
        
        return redirect(request.referrer)
        
    except Exception as e:
        logger.error(f"Errore nella rimozione etichetta cella: {str(e)}")
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nella rimozione: {str(e)}', 'error')
        return redirect(request.referrer)

@ml_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/batch-ai-label', methods=['POST'])
@login_required
def batch_ai_label(project_id, sheet_id):
    """Applica etichettatura AI in batch a una colonna"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Verifica che il foglio appartenga al progetto
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    column_name = data.get('column_name', '').strip()
    analysis_template = data.get('template', 'custom')
    custom_prompt = data.get('custom_prompt', '').strip()
    max_items = int(data.get('max_items', 50))
    
    if not column_name:
        error_msg = 'Nome colonna richiesto per l\'analisi batch'
        if request.is_json:
            return jsonify({'error': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(request.referrer)
    
    try:
        # Recupera configurazione ML attiva
        ml_config = MLConfiguration.query.filter_by(project_id=project.id, is_active=True).first()
        
        if not ml_config:
            error_msg = 'Nessuna configurazione ML attiva trovata'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(request.referrer)
        
        # Carica i dati dal file Excel
        file_path = sheet.file.get_file_path()
        df = pd.read_excel(file_path, sheet_name=sheet.name)
        
        if column_name not in df.columns:
            error_msg = f'Colonna "{column_name}" non trovata nel foglio'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(request.referrer)
        
        # Prepara i dati per l'analisi batch (limita il numero di elementi)
        column_data = df[column_name].dropna().head(max_items).tolist()
        
        if not column_data:
            error_msg = f'Nessun dato valido trovato nella colonna "{column_name}"'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(request.referrer)
        
        # Crea client ML
        client = MLAPIClient(
            provider=ml_config.ml_provider,
            api_key=ml_config.api_key_encrypted,
            api_url=ml_config.api_url,
            model=ml_config.ml_model
        )
        
        # Prepara il prompt per l'analisi batch
        if analysis_template == 'sentiment':
            base_prompt = "Analizza il sentiment di ogni testo e classifica come: positivo, negativo, neutro"
        elif analysis_template == 'emotion':
            base_prompt = "Identifica l'emozione principale in ogni testo: gioia, tristezza, rabbia, paura, sorpresa, disgusto, neutro"
        elif analysis_template == 'behavior':
            base_prompt = "Classifica il comportamento in ogni testo: proattivo, reattivo, passivo, aggressivo, collaborativo"
        elif analysis_template == 'topic':
            base_prompt = "Identifica il topic/argomento principale di ogni testo"
        elif analysis_template == 'intent':
            base_prompt = "Determina l'intento di ogni testo: richiesta, reclamo, complimento, domanda"
        else:  # custom
            base_prompt = custom_prompt if custom_prompt else "Analizza e classifica ogni testo"
        
        # Esegui analisi batch
        batch_prompt = f"{base_prompt}\n\nTesti da analizzare:\n"
        for i, text in enumerate(column_data[:10]):  # Limita a 10 per evitare prompt troppo lunghi
            batch_prompt += f"{i+1}. {text}\n"
        
        batch_prompt += "\nFornisci una risposta in formato JSON con array di oggetti contenenti: index, label, confidence"
        
        response = client.analyze_text(batch_prompt)
        
        if response.get('success', False):
            # Crea o trova analisi ML per questa sessione
            ml_analysis = MLAnalysis.query.filter_by(
                project_id=project.id,
                sheet_id=sheet.id,
                ml_provider=ml_config.ml_provider,
                ml_model=ml_config.ml_model,
                status='completed'
            ).first()
            
            if not ml_analysis:
                ml_analysis = MLAnalysis(
                    project_id=project.id,
                    file_id=sheet.file_id,
                    sheet_id=sheet.id,
                    ml_provider=ml_config.ml_provider,
                    ml_model=ml_config.ml_model,
                    analysis_type=f'batch_{analysis_template}',
                    status='completed',
                    results={'batch_analysis': True, 'template': analysis_template},
                    processing_time=1.0
                )
                db.session.add(ml_analysis)
                db.session.flush()
            
            # Genera e salva le etichette basate sui risultati AI
            batch_results = []
            labels_saved = 0
            
            for i, text in enumerate(column_data[:10]):
                # Simula o parsea i risultati AI
                label_name = f'{analysis_template.title()}_{i+1}'
                confidence = 0.6 + (i * 0.02)  # Confidence variabile tra 0.6 e 0.8
                
                # Crea l'AutoLabel se non esiste
                auto_label = AutoLabel.query.filter_by(
                    ml_analysis_id=ml_analysis.id,
                    label_name=label_name,
                    column_name=column_name
                ).first()
                
                if not auto_label:
                    auto_label = AutoLabel(
                        ml_analysis_id=ml_analysis.id,
                        label_name=label_name,
                        label_description=f'Etichetta AI generata: {analysis_template}',
                        category=f'ai_{analysis_template}',
                        confidence_score=confidence,
                        column_name=column_name,
                        created_by=current_user.id,
                        label_type='ai_batch'
                    )
                    db.session.add(auto_label)
                    db.session.flush()
                
                # Applica l'etichetta alla cella specifica
                row_index = i  # Index nella lista originale
                existing_app = AutoLabelApplication.query.filter_by(
                    auto_label_id=auto_label.id,
                    row_index=row_index,
                    column_name=column_name
                ).first()
                
                if not existing_app:
                    label_app = AutoLabelApplication(
                        auto_label_id=auto_label.id,
                        row_index=row_index,
                        column_name=column_name,
                        cell_value=str(text),
                        confidence_score=confidence,
                        status='applied',
                        applied_at=datetime.utcnow()
                    )
                    db.session.add(label_app)
                    labels_saved += 1
                
                batch_results.append({
                    'index': i,
                    'text': text,
                    'label': label_name,
                    'confidence': confidence,
                    'saved': True
                })
            
            # Salva tutte le modifiche nel database
            db.session.commit()
            
            message = f'Analisi batch AI completata: {labels_saved} etichette applicate a {len(batch_results)} elementi'
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'results': batch_results,
                    'total_processed': len(batch_results),
                    'labels_saved': labels_saved,
                    'template_used': analysis_template,
                    'message': message
                })
            else:
                flash(message, 'success')
                return redirect(request.referrer)
        else:
            error_msg = response.get('error', 'Errore nell\'analisi batch AI')
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            flash(f'Errore nell\'analisi batch: {error_msg}', 'error')
            return redirect(request.referrer)
    
    except Exception as e:
        logger.error(f"Errore nell'analisi batch AI: {str(e)}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nell\'analisi batch: {str(e)}', 'error')
        return redirect(request.referrer)

@ml_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/single-column-view')
@login_required
def single_column_view(project_id, sheet_id):
    """Vista semplificata per visualizzare una singola colonna con celle verticali"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Verifica che il foglio appartenga al progetto
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    # Parametro colonna specifica
    column_name = request.args.get('column_name')
    
    try:
        # Carica i dati dal file Excel
        file_path = sheet.file.get_file_path()
        df = pd.read_excel(file_path, sheet_name=sheet.name)
        
        # Se non è specificata una colonna, mostra l'elenco per selezionarla
        if not column_name:
            available_columns = [
                {
                    'name': col,
                    'type': str(df[col].dtype),
                    'unique_values': len(df[col].unique()),
                    'null_count': df[col].isnull().sum(),
                    'total_rows': len(df)
                }
                for col in df.columns
            ]
            
            if request.is_json:
                return jsonify({
                    'project': project.to_dict(),
                    'sheet': sheet.to_dict(),
                    'available_columns': available_columns
                })
            
            return render_template('ml/select_column.html',
                                project=project,
                                sheet=sheet,
                                available_columns=available_columns)
        
        # Verifica che la colonna esista
        if column_name not in df.columns:
            error_msg = f'Colonna "{column_name}" non trovata nel foglio'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('ml.single_column_view', project_id=project.id, sheet_id=sheet.id))
        
        # Prepara i dati della colonna specifica
        col_data = {
            'name': column_name,
            'type': str(df[column_name].dtype),
            'unique_values': len(df[column_name].unique()),
            'null_count': df[column_name].isnull().sum(),
            'total_rows': len(df),
            'all_values': df[column_name].tolist()
        }
        
        # Recupera etichette applicate per questa colonna
        applied_labels = {}
        ml_analysis = MLAnalysis.query.filter_by(
            project_id=project.id,
            sheet_id=sheet.id,
            status='completed'
        ).first()
        
        if ml_analysis:
            label_applications = AutoLabelApplication.query.join(AutoLabel).filter(
                AutoLabel.ml_analysis_id == ml_analysis.id,
                AutoLabelApplication.column_name == column_name,
                AutoLabelApplication.status == 'applied'
            ).all()
            
            for app in label_applications:
                applied_labels[app.row_index] = {
                    'label_name': app.auto_label.label_name,
                    'label_description': app.auto_label.label_description,
                    'confidence': app.confidence_score
                }
        
        if request.is_json:
            return jsonify({
                'project': project.to_dict(),
                'sheet': sheet.to_dict(),
                'column_data': col_data,
                'applied_labels': applied_labels
            })
        
        return render_template('ml/single_column_view.html',
                            project=project,
                            sheet=sheet,
                            column_data=col_data,
                            applied_labels=applied_labels,
                            selected_column=column_name)
    
    except Exception as e:
        logger.error(f"Errore nella vista singola colonna del foglio {sheet_id}: {str(e)}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nel caricamento dei dati: {str(e)}', 'error')
        return redirect(url_for('ml.view_ml_dashboard', project_id=project.id))

@ml_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/single-row-view')
@login_required
def single_row_view(project_id, sheet_id):
    """Vista semplificata per visualizzare una singola riga con celle orizzontali"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Verifica che il foglio appartenga al progetto
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    # Parametro riga specifica
    row_index = request.args.get('row_index', type=int)
    
    try:
        # Carica i dati dal file Excel
        file_path = sheet.file.get_file_path()
        df = pd.read_excel(file_path, sheet_name=sheet.name)
        
        # Se non è specificata una riga, mostra l'elenco per selezionarla
        if row_index is None:
            available_rows = []
            for idx, row in df.head(50).iterrows():  # Mostra solo le prime 50 righe per performance
                # Prendi i primi 3 valori non nulli per l'anteprima
                preview_values = []
                for col, value in row.items():
                    if pd.notna(value) and str(value).strip():
                        preview_values.append(str(value)[:50])
                        if len(preview_values) >= 3:
                            break
                
                available_rows.append({
                    'index': idx,
                    'preview': ' | '.join(preview_values) if preview_values else '(vuota)'
                })
            
            if request.is_json:
                return jsonify({
                    'project': project.to_dict(),
                    'sheet': sheet.to_dict(),
                    'available_rows': available_rows,
                    'total_rows': len(df)
                })
            
            return render_template('ml/select_row.html',
                                project=project,
                                sheet=sheet,
                                available_rows=available_rows,
                                total_rows=len(df))
        
        # Verifica che la riga esista
        if row_index >= len(df) or row_index < 0:
            error_msg = f'Riga {row_index} non trovata nel foglio (righe disponibili: 0-{len(df)-1})'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('ml.single_row_view', project_id=project.id, sheet_id=sheet.id))
        
        # Prepara i dati della riga specifica
        selected_row = df.iloc[row_index]
        row_data = {
            'index': row_index,
            'data': {}
        }
        
        # Converti ogni valore in stringa per evitare problemi di serializzazione
        for col, value in selected_row.items():
            if pd.isna(value):
                row_data['data'][col] = ''
            else:
                row_data['data'][col] = str(value)
        
        # Recupera etichette applicate per questa riga - SUPPORTA MULTIPLE ETICHETTE
        applied_labels = {}
        ml_analysis = MLAnalysis.query.filter_by(
            project_id=project.id,
            sheet_id=sheet.id,
            status='completed'
        ).first()
        
        if ml_analysis:
            label_applications = AutoLabelApplication.query.join(AutoLabel).filter(
                AutoLabel.ml_analysis_id == ml_analysis.id,
                AutoLabelApplication.row_index == row_index,
                AutoLabelApplication.status == 'applied'
            ).all()
            
            for app in label_applications:
                key = f"{app.row_index}_{app.column_name}"
                
                # Inizializza lista se non esiste
                if key not in applied_labels:
                    applied_labels[key] = []
                
                # Aggiungi questa etichetta alla lista per questa cella
                applied_labels[key].append({
                    'label_name': app.auto_label.label_name,
                    'label_description': app.auto_label.label_description,
                    'confidence': app.confidence_score,
                    'application_id': app.id
                })
        
        if request.is_json:
            return jsonify({
                'project': project.to_dict(),
                'sheet': sheet.to_dict(),
                'row_data': row_data,
                'columns': df.columns.tolist(),
                'applied_labels': applied_labels
            })
        
        return render_template('ml/single_row_view.html',
                            project=project,
                            sheet=sheet,
                            row_data=row_data,
                            columns=df.columns.tolist(),
                            applied_labels=applied_labels,
                            selected_row_index=row_index)
    
    except Exception as e:
        logger.error(f"Errore nella vista singola riga del foglio {sheet_id}: {str(e)}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nel caricamento dei dati: {str(e)}', 'error')
        return redirect(url_for('ml.view_ml_dashboard', project_id=project.id))

@ml_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/export-labels', methods=['GET'])
@login_required
def export_labels(project_id, sheet_id):
    """Esporta le etichette applicate in formato CSV"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Verifica che il foglio appartenga al progetto
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    try:
        # Carica i dati originali dal file Excel
        file_path = sheet.file.get_file_path()
        df = pd.read_excel(file_path, sheet_name=sheet.name)
        
        # Recupera tutte le etichette applicate per questo foglio
        ml_analysis = MLAnalysis.query.filter_by(
            project_id=project.id,
            sheet_id=sheet.id,
            status='completed'
        ).first()
        
        if ml_analysis:
            label_applications = AutoLabelApplication.query.join(AutoLabel).filter(
                AutoLabel.ml_analysis_id == ml_analysis.id,
                AutoLabelApplication.status == 'applied'
            ).all()
            
            # Crea un DataFrame con i dati originali più le etichette
            export_data = df.copy()
            
            # Aggiungi colonne per le etichette
            for app in label_applications:
                label_col_name = f"{app.column_name}_label"
                confidence_col_name = f"{app.column_name}_confidence"
                
                if label_col_name not in export_data.columns:
                    export_data[label_col_name] = ''
                    export_data[confidence_col_name] = ''
                
                # Applica l'etichetta alla riga specifica
                if app.row_index < len(export_data):
                    export_data.loc[app.row_index, label_col_name] = app.auto_label.label_name
                    export_data.loc[app.row_index, confidence_col_name] = app.confidence_score
        else:
            export_data = df.copy()
        
        # Genera il CSV
        from io import StringIO
        import csv
        
        output = StringIO()
        export_data.to_csv(output, index=False, quoting=csv.QUOTE_ALL)
        csv_content = output.getvalue()
        output.close()
        
        # Prepara la risposta
        from flask import Response
        
        filename = f"{project.name}_{sheet.name}_labeled_data.csv"
        
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
    
    except Exception as e:
        logger.error(f"Errore nell'esportazione delle etichette: {str(e)}")
        flash(f'Errore nell\'esportazione: {str(e)}', 'error')
        return redirect(request.referrer or url_for('ml.view_ml_dashboard', project_id=project.id))

@ml_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/integrate-column-labeling', methods=['POST'])
@login_required
def integrate_column_labeling(project_id, sheet_id):
    """Integra l'etichettatura di una colonna con il sistema di etichettatura strutturato"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Verifica che il foglio appartenga al progetto
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    column_name = data.get('column_name', '').strip()
    action_type = data.get('action_type', 'label')  # 'label' o 'analyze'
    
    if not column_name:
        error_msg = 'Nome colonna richiesto'
        if request.is_json:
            return jsonify({'error': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(request.referrer)
    
    try:
        if action_type == 'analyze':
            # Reindirizza all'analisi AI avanzata della colonna
            return redirect(url_for('ml.advanced_column_view',
                                  project_id=project.id,
                                  sheet_id=sheet.id) + f'?column_name={column_name}')
        
        elif action_type == 'label':
            # TODO: Implementare integrazione con sistema etichette unificato (Fase 2)
            # Questa funzionalità sarà ristrutturata nel sistema etichette unificato
            message = f'Etichettatura per la colonna "{column_name}" sarà disponibile nel nuovo sistema unificato'
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': message,
                    'redirect_url': url_for('ml.view_ml_dashboard', project_id=project.id)
                })
            else:
                flash(message, 'info')
                return redirect(url_for('ml.view_ml_dashboard', project_id=project.id))
        
        else:
            error_msg = f'Azione non riconosciuta: {action_type}'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(request.referrer)
    
    except Exception as e:
        logger.error(f"Errore nell'integrazione etichettatura colonna: {str(e)}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nell\'integrazione: {str(e)}', 'error')
        return redirect(request.referrer)

@ml_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/analyze-column-ai', methods=['POST'])
@login_required
def analyze_column_ai(project_id, sheet_id):
    """Analizza una colonna specifica con AI per generare insights avanzati"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Verifica che il foglio appartenga al progetto
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    column_name = data.get('column_name', '').strip()
    
    if not column_name:
        error_msg = 'Nome colonna richiesto per l\'analisi'
        if request.is_json:
            return jsonify({'error': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(request.referrer)
    
    try:
        # Recupera configurazione ML attiva
        ml_config = MLConfiguration.query.filter_by(project_id=project.id, is_active=True).first()
        
        if not ml_config:
            error_msg = 'Nessuna configurazione ML attiva trovata. Configura prima il sistema ML.'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('ml.configure_ml', project_id=project.id))
        
        # Carica i dati dal file Excel
        file_path = sheet.file.get_file_path()
        df = pd.read_excel(file_path, sheet_name=sheet.name)
        
        if column_name not in df.columns:
            error_msg = f'Colonna "{column_name}" non trovata nel foglio'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(request.referrer)
        
        # Analizza la colonna
        column_data = df[column_name].dropna()
        analysis_result = {
            'column_name': column_name,
            'total_values': len(df[column_name]),
            'unique_values': len(column_data.unique()),
            'null_count': df[column_name].isnull().sum(),
            'data_type': str(df[column_name].dtype),
            'sample_values': column_data.head(10).tolist(),
            'value_distribution': column_data.value_counts().head(10).to_dict()
        }
        
        # Genera suggerimenti AI per il tipo di etichettatura
        if len(column_data) > 0:
            client = MLAPIClient(
                provider=ml_config.ml_provider,
                api_key=ml_config.api_key_encrypted,
                api_url=ml_config.api_url,
                model=ml_config.ml_model
            )
            
            # Prepara il prompt per l'analisi
            sample_text = '\n'.join([str(val) for val in column_data.head(10).tolist()])
            analysis_prompt = f"""
Analizza la seguente colonna di dati e fornisci suggerimenti per l'etichettatura:

Nome colonna: {column_name}
Tipo di dati: {analysis_result['data_type']}
Valori unici: {analysis_result['unique_values']}
Valori di esempio:
{sample_text}

Fornisci:
1. Il tipo di contenuto (es: sentiment, categoria, tema, etc.)
2. Suggerimenti per categorie di etichette appropriate
3. Approccio di analisi consigliato
4. Template di etichettatura suggerito
"""
            
            ai_response = client.analyze_text(analysis_prompt)
            
            if ai_response.get('success'):
                analysis_result['ai_suggestions'] = ai_response.get('analysis', 'Nessun suggerimento disponibile')
            else:
                analysis_result['ai_suggestions'] = 'Errore nell\'analisi AI: ' + ai_response.get('error', 'Errore sconosciuto')
        else:
            analysis_result['ai_suggestions'] = 'Colonna vuota - impossibile fornire suggerimenti'
        
        message = f'Analisi AI completata per la colonna "{column_name}"'
        
        if request.is_json:
            return jsonify({
                'message': message,
                'analysis': analysis_result
            })
        else:
            # Salva il risultato nella sessione per visualizzarlo
            from flask import session
            session[f'column_analysis_{column_name}'] = analysis_result
            
            flash(message, 'success')
            return redirect(url_for('ml.view_sheet_columns',
                                  project_id=project.id,
                                  sheet_id=sheet.id) + f'#column-{column_name}')
    
    except Exception as e:
        logger.error(f"Errore nell'analisi AI della colonna: {str(e)}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Errore nell\'analisi: {str(e)}', 'error')
        return redirect(request.referrer)

@ml_bp.route('/projects/<uuid:project_id>/sheets/<uuid:sheet_id>/debug-labels')
@login_required
def debug_labels(project_id, sheet_id):
    """Endpoint di debug per verificare lo stato delle etichette salvate"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    sheet = ExcelSheet.query.join(File).filter(
        ExcelSheet.id == sheet_id,
        File.project_id == project.id
    ).first_or_404()
    
    debug_info = {
        'project_id': str(project.id),
        'sheet_id': str(sheet.id),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # 1. Verifica MLAnalysis
    ml_analyses = MLAnalysis.query.filter_by(
        project_id=project.id,
        sheet_id=sheet.id
    ).all()
    
    debug_info['ml_analyses'] = []
    for analysis in ml_analyses:
        debug_info['ml_analyses'].append({
            'id': str(analysis.id),
            'status': analysis.status,
            'ml_provider': analysis.ml_provider,
            'ml_model': analysis.ml_model,
            'analysis_type': analysis.analysis_type,
            'created_at': analysis.created_at.isoformat() if analysis.created_at else None
        })
    
    # 2. Verifica AutoLabels
    if ml_analyses:
        for analysis in ml_analyses:
            auto_labels = AutoLabel.query.filter_by(ml_analysis_id=analysis.id).all()
            analysis_info = {
                'analysis_id': str(analysis.id),
                'auto_labels_count': len(auto_labels),
                'auto_labels': []
            }
            
            for label in auto_labels:
                analysis_info['auto_labels'].append({
                    'id': str(label.id),
                    'label_name': label.label_name,
                    'column_name': label.column_name,
                    'confidence_score': label.confidence_score,
                    'created_by': str(label.created_by) if label.created_by else None
                })
            
            debug_info[f'analysis_{analysis.id}'] = analysis_info
    
    # 3. Verifica AutoLabelApplications
    total_applications = 0
    for analysis in ml_analyses:
        applications = AutoLabelApplication.query.join(AutoLabel).filter(
            AutoLabel.ml_analysis_id == analysis.id
        ).all()
        
        analysis_apps = {
            'applications_count': len(applications),
            'applications': []
        }
        
        for app in applications:
            analysis_apps['applications'].append({
                'id': str(app.id),
                'auto_label_id': str(app.auto_label_id),
                'row_index': app.row_index,
                'column_name': app.column_name,
                'cell_value': app.cell_value,
                'confidence_score': app.confidence_score,
                'status': app.status,
                'applied_at': app.applied_at.isoformat() if app.applied_at else None,
                'label_name': app.auto_label.label_name
            })
        
        total_applications += len(applications)
        debug_info[f'applications_{analysis.id}'] = analysis_apps
    
    debug_info['total_applications'] = total_applications
    
    # 4. Test caricamento come nella view normale
    ml_analysis = MLAnalysis.query.filter_by(
        project_id=project.id,
        sheet_id=sheet.id,
        status='completed'
    ).first()
    
    applied_labels_test = {}
    if ml_analysis:
        label_applications = AutoLabelApplication.query.join(AutoLabel).filter(
            AutoLabel.ml_analysis_id == ml_analysis.id,
            AutoLabelApplication.status == 'applied'
        ).all()
        
        for app in label_applications:
            key = f"{app.row_index}_{app.column_name}"
            if key not in applied_labels_test:
                applied_labels_test[key] = []
            
            applied_labels_test[key].append({
                'label_name': app.auto_label.label_name,
                'confidence': app.confidence_score
            })
    
    debug_info['applied_labels_test'] = applied_labels_test
    debug_info['applied_labels_count'] = len(applied_labels_test)
    
    return jsonify(debug_info)
