from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.database import db
from app.models import Project, Label, CellLabel, ExcelRow, ExcelSheet, File
from datetime import datetime

labels_bp = Blueprint('labels', __name__)

@labels_bp.route('/<uuid:project_id>')
@login_required
def list_labels(project_id):
    """Store Etichette Centralizzato - Task 2.4"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    labels = Label.query.filter_by(project_id=project.id)\
        .order_by(Label.usage_count.desc(), Label.name)\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    # Calcola le statistiche per il template
    total_usages = sum(label.usage_count or label.cell_labels.count() for label in labels.items)
    average_usages = round(total_usages / labels.total, 1) if labels.total > 0 else 0
    labels_with_categories = sum(1 for label in labels.items if label.categories)
    
    # Ottieni tutte le categorie uniche per i filtri
    all_categories = set()
    for label in Label.query.filter_by(project_id=project.id).all():
        if label.categories:
            all_categories.update(label.categories)
    all_categories = sorted(list(all_categories))
    
    # Aggiungi le statistiche agli oggetti label per l'uso nel template
    for label in labels.items:
        if not hasattr(label, 'usage_count') or label.usage_count is None:
            label.usage_count = label.cell_labels.count()
    
    if request.is_json:
        return jsonify({
            'project': project.to_dict(),
            'labels': [l.to_dict() for l in labels.items],
            'pagination': {
                'page': labels.page,
                'pages': labels.pages,
                'per_page': labels.per_page,
                'total': labels.total,
                'has_next': labels.has_next,
                'has_prev': labels.has_prev
            },
            'statistics': {
                'total_usages': total_usages,
                'average_usages': average_usages,
                'labels_with_categories': labels_with_categories
            }
        })
    
    return render_template('labels/store.html', 
                         project=project, 
                         labels=labels,
                         total_usages=total_usages,
                         average_usages=average_usages,
                         labels_with_categories=labels_with_categories,
                         all_categories=all_categories)

@labels_bp.route('/<uuid:project_id>/create', methods=['GET', 'POST'])
@login_required
def create_label(project_id):
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            name = data.get('name', '').strip()
            description = data.get('description', '').strip()
            color = data.get('color', '#1976d2').strip()
            categories = data.get('categories', [])
        else:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            color = request.form.get('color', '#1976d2').strip()
            categories = request.form.getlist('categories')
        
        if not name:
            if request.is_json:
                return jsonify({'error': 'Nome etichetta richiesto'}), 400
            flash('Nome etichetta richiesto', 'error')
            return render_template('labels/create.html', project=project)
        
        # Check if label name already exists in this project
        existing = Label.query.filter_by(project_id=project.id, name=name).first()
        if existing:
            if request.is_json:
                return jsonify({'error': 'Etichetta con questo nome già esistente'}), 400
            flash('Etichetta con questo nome già esistente', 'error')
            return render_template('labels/create.html', project=project)
        
        label = Label(
            project_id=project.id,
            name=name,
            description=description,
            color=color,
            categories=categories if categories else [],
            created_by=current_user.id,  # Task 2.4: Track creator
            usage_count=0  # Task 2.4: Initialize usage count
        )
        
        db.session.add(label)
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'message': 'Etichetta creata con successo',
                'label': label.to_dict()
            }), 201
        else:
            flash('Etichetta creata con successo!', 'success')
            return redirect(url_for('labels.list_labels', project_id=project.id))
    
    return render_template('labels/create.html', project=project)

@labels_bp.route('/<int:label_id>')
@login_required
def view_label(label_id):
    label = Label.query.join(Project).filter(
        Label.id == label_id,
        Project.owner_id == current_user.id
    ).first_or_404()
    
    # Get label usage with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    cell_labels = CellLabel.query.filter_by(label_id=label.id)\
        .order_by(CellLabel.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    if request.is_json:
        return jsonify({
            'label': label.to_dict(),
            'cell_labels': [cl.to_dict() for cl in cell_labels.items],
            'pagination': {
                'page': cell_labels.page,
                'pages': cell_labels.pages,
                'per_page': cell_labels.per_page,
                'total': cell_labels.total,
                'has_next': cell_labels.has_next,
                'has_prev': cell_labels.has_prev
            }
        })
    
    return render_template('labels/view.html', label=label, cell_labels=cell_labels)

@labels_bp.route('/<int:label_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_label(label_id):
    label = Label.query.join(Project).filter(
        Label.id == label_id,
        Project.owner_id == current_user.id
    ).first_or_404()
    
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            name = data.get('name', '').strip()
            description = data.get('description', '').strip()
            color = data.get('color', '#1976d2').strip()
            categories = data.get('categories', [])
        else:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            color = request.form.get('color', '#1976d2').strip()
            categories = request.form.getlist('categories')
        
        if not name:
            if request.is_json:
                return jsonify({'error': 'Nome etichetta richiesto'}), 400
            flash('Nome etichetta richiesto', 'error')
            return render_template('labels/edit.html', label=label)
        
        # Check if label name already exists in this project (excluding current label)
        existing = Label.query.filter(
            Label.project_id == label.project_id,
            Label.name == name,
            Label.id != label.id
        ).first()
        
        if existing:
            if request.is_json:
                return jsonify({'error': 'Etichetta con questo nome già esistente'}), 400
            flash('Etichetta con questo nome già esistente', 'error')
            return render_template('labels/edit.html', label=label)
        
        label.name = name
        label.description = description
        label.color = color
        label.categories = categories if categories else []
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'message': 'Etichetta aggiornata con successo',
                'label': label.to_dict()
            })
        else:
            flash('Etichetta aggiornata con successo!', 'success')
            return redirect(url_for('labels.view_label', label_id=label.id))
    
    return render_template('labels/edit.html', label=label)

@labels_bp.route('/<int:label_id>/delete', methods=['POST'])
@login_required
def delete_label(label_id):
    label = Label.query.join(Project).filter(
        Label.id == label_id,
        Project.owner_id == current_user.id
    ).first_or_404()
    
    label_name = label.name
    project_id = label.project_id
    
    db.session.delete(label)
    db.session.commit()
    
    if request.is_json:
        return jsonify({'message': f'Etichetta "{label_name}" eliminata con successo'})
    else:
        flash(f'Etichetta "{label_name}" eliminata con successo', 'success')
        return redirect(url_for('labels.list_labels', project_id=project_id))

from flask import jsonify

@labels_bp.route('/apply', methods=['POST'])
@login_required
def apply_label():
    """Apply a label to a specific cell"""
    is_ajax = request.is_json
    
    if is_ajax:
        data = request.get_json() if request.is_json else request.form
        row_id = data.get('row_id')
        label_id = data.get('label_id')
        column_index = data.get('column_index')
        cell_value = data.get('cell_value', '')
    else:
        row_id = request.form.get('row_id')
        label_id = request.form.get('label_id')
        column_index = request.form.get('column_index', type=int)
        cell_value = request.form.get('cell_value', '')
    
    if not all([row_id, label_id]):
        if is_ajax:
            return jsonify({'error': 'Row ID e Label ID richiesti'}), 400
        flash('Row ID e Label ID richiesti', 'error')
        return redirect(request.referrer or url_for('main.dashboard'))
    
    # Verify row belongs to user's project
    row = ExcelRow.query.join(ExcelSheet).join(File).join(Project).filter(
        ExcelRow.id == row_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not row:
        if is_ajax:
            return jsonify({'error': 'Riga non trovata'}), 404
        flash('Riga non trovata', 'error')
        return redirect(request.referrer or url_for('main.dashboard'))
    
    # Verify label belongs to the same project
    label = Label.query.filter_by(id=label_id, project_id=row.sheet.file.project_id).first()
    
    if not label:
        if is_ajax:
            return jsonify({'error': 'Etichetta non trovata'}), 404
        flash('Etichetta non trovata', 'error')
        return redirect(request.referrer or url_for('main.dashboard'))
    
    # Check if label already applied to this cell
    existing = CellLabel.query.filter_by(
        row_id=row_id,
        label_id=label_id,
        column_index=column_index
    ).first()
    
    if existing:
        if is_ajax:
            return jsonify({'error': 'Etichetta già applicata a questa cella'}), 400
        flash('Etichetta già applicata a questa cella', 'warning')
        return redirect(request.referrer or url_for('main.dashboard'))

    # Create cell label
    cell_label = CellLabel(
        row_id=row_id,
        label_id=label_id,
        column_index=column_index,
        cell_value=cell_value,
        created_by=current_user.id
    )
    db.session.add(cell_label)
    db.session.commit()

    if is_ajax:
        return jsonify({
            'status': 'success',
            'message': 'Etichetta applicata con successo',
            'cell_label': cell_label.to_dict()
        }), 201
    else:
        flash('Etichetta applicata con successo!', 'success')
        return redirect(request.referrer or url_for('main.dashboard'))

@labels_bp.route('/remove/<uuid:cell_label_id>', methods=['POST'])
@login_required
def remove_label(cell_label_id):
    """Remove a label from a cell"""
    cell_label = CellLabel.query.join(ExcelRow).join(ExcelSheet).join(File).join(Project).filter(
        CellLabel.id == cell_label_id,
        Project.owner_id == current_user.id
    ).first_or_404()
    
    db.session.delete(cell_label)
    db.session.commit()
    
    if request.is_json:
        return jsonify({'message': 'Etichetta rimossa con successo'})
    else:
        flash('Etichetta rimossa con successo!', 'success')
        return redirect(request.referrer or url_for('main.dashboard'))

# Task 2.5 - Batch Processing Routes
@labels_bp.route('/<uuid:project_id>/suggestions/batch/approve', methods=['POST'])
@login_required
def batch_approve_suggestions(project_id):
    """Approva un batch di suggerimenti AI"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    suggestion_ids = data.get('suggestion_ids', [])
    
    if not suggestion_ids:
        return jsonify({'error': 'Nessun suggerimento selezionato'}), 400
    
    from app.models_labeling import LabelSuggestion
    approved_count = 0
    errors = []
    
    for suggestion_id in suggestion_ids:
        try:
            suggestion = LabelSuggestion.query.filter_by(
                id=suggestion_id,
                status='pending'
            ).first()
            
            if not suggestion:
                errors.append(f'Suggerimento {suggestion_id} non trovato o già processato')
                continue
            
            # Approva il suggerimento
            suggestion.status = 'approved'
            suggestion.reviewed_by = current_user.id
            suggestion.reviewed_at = datetime.utcnow()
            
            # Crea la label nel store se non esiste
            existing_label = Label.query.filter_by(
                project_id=project.id,
                name=suggestion.suggested_name
            ).first()
            
            if not existing_label:
                new_label = Label(
                    project_id=project.id,
                    name=suggestion.suggested_name,
                    description=suggestion.suggested_description,
                    color=suggestion.suggested_color,
                    categories=[suggestion.suggested_category] if suggestion.suggested_category else [],
                    created_by=current_user.id,
                    created_at=datetime.utcnow()
                )
                db.session.add(new_label)
            
            approved_count += 1
            
        except Exception as e:
            errors.append(f'Errore processando suggerimento {suggestion_id}: {str(e)}')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'approved_count': approved_count,
        'errors': errors,
        'message': f'Approvati {approved_count} suggerimenti'
    })

@labels_bp.route('/<uuid:project_id>/suggestions/batch/reject', methods=['POST'])
@login_required
def batch_reject_suggestions(project_id):
    """Rifiuta un batch di suggerimenti AI"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    suggestion_ids = data.get('suggestion_ids', [])
    rejection_reason = data.get('reason', 'Non specificato')
    
    if not suggestion_ids:
        return jsonify({'error': 'Nessun suggerimento selezionato'}), 400
    
    from app.models_labeling import LabelSuggestion
    rejected_count = 0
    errors = []
    
    for suggestion_id in suggestion_ids:
        try:
            suggestion = LabelSuggestion.query.filter_by(
                id=suggestion_id,
                status='pending'
            ).first()
            
            if not suggestion:
                errors.append(f'Suggerimento {suggestion_id} non trovato o già processato')
                continue
            
            # Rifiuta il suggerimento
            suggestion.status = 'rejected'
            suggestion.reviewed_by = current_user.id
            suggestion.reviewed_at = datetime.utcnow()
            suggestion.review_notes = rejection_reason
            
            rejected_count += 1
            
        except Exception as e:
            errors.append(f'Errore processando suggerimento {suggestion_id}: {str(e)}')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'rejected_count': rejected_count,
        'errors': errors,
        'message': f'Rifiutati {rejected_count} suggerimenti'
    })

@labels_bp.route('/<uuid:project_id>/applications/batch/authorize', methods=['POST'])
@login_required
def batch_authorize_applications(project_id):
    """Autorizza un batch di applicazioni AI"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    application_ids = data.get('application_ids', [])
    
    if not application_ids:
        return jsonify({'error': 'Nessuna applicazione selezionata'}), 400
    
    from app.models_labeling import LabelApplication
    authorized_count = 0
    errors = []
    
    for application_id in application_ids:
        try:
            application = LabelApplication.query.filter_by(
                id=application_id,
                project_id=project.id,
                authorization_status='pending'
            ).first()
            
            if not application:
                errors.append(f'Applicazione {application_id} non trovata o già processata')
                continue
            
            # Autorizza l'applicazione
            application.authorization_status = 'authorized'
            application.authorized_by = current_user.id
            application.authorized_at = datetime.utcnow()
            
            authorized_count += 1
            
        except Exception as e:
            errors.append(f'Errore processando applicazione {application_id}: {str(e)}')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'authorized_count': authorized_count,
        'errors': errors,
        'message': f'Autorizzate {authorized_count} applicazioni'
    })

@labels_bp.route('/<uuid:project_id>/suggestions/pending')
@login_required
def pending_suggestions_overview(project_id):
    """Pagina overview dei suggerimenti pendenti"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    from app.models_labeling import LabelSuggestion, LabelApplication, LabelGeneration
    
    # Suggerimenti per store labels
    store_suggestions = LabelSuggestion.query.join(
        LabelGeneration, LabelSuggestion.generation_id == LabelGeneration.id
    ).filter(
        LabelGeneration.project_id == project.id,
        LabelSuggestion.status == 'pending'
    ).order_by(LabelSuggestion.ai_confidence.desc()).all()
    
    # Applicazioni AI pendenti
    pending_applications = LabelApplication.query.filter_by(
        project_id=project.id,
        authorization_status='pending'
    ).order_by(LabelApplication.confidence_score.desc()).all()
    
    # Calcola statistiche per il template
    stats = {
        'total_pending': len(store_suggestions) + len(pending_applications),
        'store_suggestions_count': len(store_suggestions),
        'pending_applications_count': len(pending_applications),
        'high_confidence_count': len([s for s in store_suggestions if s.ai_confidence and s.ai_confidence >= 0.8]),
        'low_confidence_count': len([s for s in store_suggestions if s.ai_confidence and s.ai_confidence < 0.6])
    }
    
    return render_template('labeling/pending_suggestions_overview.html',
                         project=project,
                         store_suggestions=store_suggestions,
                         pending_applications=pending_applications,
                         stats=stats)

@labels_bp.route('/<uuid:project_id>/suggestions/auto-approve-high-confidence', methods=['POST'])
@login_required
def auto_approve_high_confidence(project_id):
    """Approva automaticamente i suggerimenti ad alta confidenza"""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    min_confidence = float(data.get('min_confidence', 0.85))  # Default 85%
    
    from app.models_labeling import LabelSuggestion, LabelGeneration
    
    # Trova suggerimenti ad alta confidenza
    high_confidence_suggestions = LabelSuggestion.query.join(
        LabelGeneration, LabelSuggestion.generation_id == LabelGeneration.id
    ).filter(
        LabelGeneration.project_id == project.id,
        LabelSuggestion.status == 'pending',
        LabelSuggestion.ai_confidence >= min_confidence
    ).all()
    
    approved_count = 0
    for suggestion in high_confidence_suggestions:
        try:
            # Approva il suggerimento
            suggestion.status = 'approved'
            suggestion.reviewed_by = current_user.id
            suggestion.reviewed_at = datetime.utcnow()
            suggestion.review_notes = f'Auto-approvato per alta confidenza ({suggestion.ai_confidence:.2%})'
            
            # Crea la label nel store se non esiste
            existing_label = Label.query.filter_by(
                project_id=project.id,
                name=suggestion.suggested_name
            ).first()
            
            if not existing_label:
                new_label = Label(
                    project_id=project.id,
                    name=suggestion.suggested_name,
                    description=suggestion.suggested_description,
                    color=suggestion.suggested_color,
                    categories=[suggestion.suggested_category] if suggestion.suggested_category else [],
                    created_by=current_user.id,
                    created_at=datetime.utcnow()
                )
                db.session.add(new_label)
            
            approved_count += 1
            
        except Exception as e:
            continue
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'approved_count': approved_count,
        'min_confidence': min_confidence,
        'message': f'Auto-approvati {approved_count} suggerimenti ad alta confidenza'
    })