from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import User, Project, File, Label, ExcelSheet, ExcelRow, ExcelColumn, CellLabel
from functools import wraps

api_bp = Blueprint('api', __name__)

def jwt_or_login_required(f):
    """Decorator that accepts both JWT and session-based authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Try JWT first
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if user:
                # Set current_user-like object for JWT
                request.current_user = user
                return f(*args, **kwargs)
        except:
            pass
        
        # Fall back to session-based auth
        if current_user.is_authenticated:
            request.current_user = current_user
            return f(*args, **kwargs)
        
        return jsonify({'error': 'Authentication required'}), 401
    
    return decorated_function

def get_current_api_user():
    """Get current user for API requests"""
    return getattr(request, 'current_user', current_user)

# Authentication endpoints
@api_bp.route('/login', methods=['POST'])
def api_login():
    """API login endpoint"""
    from app.views.auth import login
    return login()

@api_bp.route('/register', methods=['POST'])
def api_register():
    """API register endpoint"""
    from app.views.auth import register
    return register()

@api_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def api_refresh():
    """API token refresh endpoint"""
    from app.views.auth import refresh
    return refresh()

@api_bp.route('/me')
@jwt_or_login_required
def api_me():
    """Get current user info"""
    user = get_current_api_user()
    return jsonify({'user': user.to_dict()})

# Projects endpoints
@api_bp.route('/projects')
@jwt_or_login_required
def api_projects():
    """Get user projects"""
    user = get_current_api_user()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    projects = Project.query.filter_by(owner_id=user.id)\
        .order_by(Project.updated_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'projects': [p.to_dict() for p in projects.items],
        'pagination': {
            'page': projects.page,
            'pages': projects.pages,
            'per_page': projects.per_page,
            'total': projects.total,
            'has_next': projects.has_next,
            'has_prev': projects.has_prev
        }
    })

@api_bp.route('/projects', methods=['POST'])
@jwt_or_login_required
def api_create_project():
    """Create new project"""
    user = get_current_api_user()
    data = request.get_json()
    
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    is_public = data.get('is_public', False)
    
    if not name:
        return jsonify({'error': 'Nome progetto richiesto'}), 400
    
    # Check if project name already exists for this user
    existing = Project.query.filter_by(owner_id=user.id, name=name).first()
    if existing:
        return jsonify({'error': 'Progetto con questo nome già esistente'}), 400
    
    project = Project(
        name=name,
        description=description,
        is_public=is_public,
        owner_id=user.id
    )
    
    db.session.add(project)
    db.session.commit()
    
    return jsonify({
        'message': 'Progetto creato con successo',
        'project': project.to_dict()
    }), 201

@api_bp.route('/projects/<uuid:project_id>')
@jwt_or_login_required
def api_project(project_id):
    """Get project details"""
    user = get_current_api_user()
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first_or_404()
    
    # Get project files
    files = File.query.filter_by(project_id=project.id)\
        .order_by(File.uploaded_at.desc()).all()
    
    # Get project labels
    labels = Label.query.filter_by(project_id=project.id)\
        .order_by(Label.name).all()
    
    return jsonify({
        'project': project.to_dict(),
        'files': [f.to_dict() for f in files],
        'labels': [l.to_dict() for l in labels]
    })

@api_bp.route('/projects/<uuid:project_id>', methods=['PUT'])
@jwt_or_login_required
def api_update_project(project_id):
    """Update project"""
    user = get_current_api_user()
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first_or_404()
    
    data = request.get_json()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    is_public = data.get('is_public', False)
    
    if not name:
        return jsonify({'error': 'Nome progetto richiesto'}), 400
    
    # Check if project name already exists for this user (excluding current project)
    existing = Project.query.filter(
        Project.owner_id == user.id,
        Project.name == name,
        Project.id != project.id
    ).first()
    
    if existing:
        return jsonify({'error': 'Progetto con questo nome già esistente'}), 400
    
    project.name = name
    project.description = description
    project.is_public = is_public
    
    db.session.commit()
    
    return jsonify({
        'message': 'Progetto aggiornato con successo',
        'project': project.to_dict()
    })

@api_bp.route('/projects/<uuid:project_id>', methods=['DELETE'])
@jwt_or_login_required
def api_delete_project(project_id):
    """Delete project"""
    user = get_current_api_user()
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first_or_404()
    
    project_name = project.name
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'message': f'Progetto "{project_name}" eliminato con successo'})

# Files endpoints
@api_bp.route('/files/<uuid:file_id>')
@jwt_or_login_required
def api_file(file_id):
    """Get file details"""
    user = get_current_api_user()
    file = File.query.join(Project).filter(
        File.id == file_id,
        Project.owner_id == user.id
    ).first_or_404()
    
    # Get Excel sheets if applicable
    sheets = []
    if file.file_type in ['xlsx', 'xls']:
        sheets = ExcelSheet.query.filter_by(file_id=file.id).all()
    
    return jsonify({
        'file': file.to_dict(),
        'sheets': [s.to_dict() for s in sheets]
    })

@api_bp.route('/files/<uuid:file_id>/sheets/<uuid:sheet_id>/data')
@jwt_or_login_required
def api_sheet_data(file_id, sheet_id):
    """Get sheet data"""
    user = get_current_api_user()
    file = File.query.join(Project).filter(
        File.id == file_id,
        Project.owner_id == user.id
    ).first_or_404()
    
    sheet = ExcelSheet.query.filter_by(id=sheet_id, file_id=file.id).first_or_404()
    
    # Get sheet data with pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    rows = ExcelRow.query.filter_by(sheet_id=sheet.id)\
        .order_by(ExcelRow.row_index)\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    columns = ExcelColumn.query.filter_by(sheet_id=sheet.id)\
        .order_by(ExcelColumn.column_index).all()
    
    return jsonify({
        'sheet': sheet.to_dict(),
        'columns': [c.to_dict() for c in columns],
        'rows': [r.to_dict() for r in rows.items],
        'pagination': {
            'page': rows.page,
            'pages': rows.pages,
            'per_page': rows.per_page,
            'total': rows.total,
            'has_next': rows.has_next,
            'has_prev': rows.has_prev
        }
    })

# Labels endpoints
@api_bp.route('/projects/<uuid:project_id>/labels')
@jwt_or_login_required
def api_project_labels(project_id):
    """Get all labels for a project (store centralizzato)"""
    user = get_current_api_user()
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first_or_404()
    
    # Get all labels for this project
    labels = Label.query.filter_by(project_id=project.id)\
        .order_by(Label.usage_count.desc(), Label.name).all()
    
    # Get usage statistics
    from app.models_labeling import LabelApplication
    total_applications = LabelApplication.query.filter_by(project_id=project.id).count()
    
    return jsonify({
        'success': True,
        'labels': [l.to_dict() for l in labels],
        'statistics': {
            'total_labels': len(labels),
            'total_applications': total_applications,
            'project_id': str(project.id)
        }
    })

@api_bp.route('/projects/<uuid:project_id>/labels', methods=['POST'])
@jwt_or_login_required
def api_create_project_label(project_id):
    """Create new label for project (manual creation)"""
    user = get_current_api_user()
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first_or_404()
    
    data = request.get_json()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    color = data.get('color', '#1976d2')
    categories = data.get('categories', [])
    
    if not name:
        return jsonify({'error': 'Nome etichetta richiesto'}), 400
    
    if not description:
        return jsonify({'error': 'Descrizione etichetta richiesta'}), 400
    
    # Check if label name already exists for this project
    existing = Label.query.filter_by(project_id=project.id, name=name).first()
    if existing:
        return jsonify({'error': 'Etichetta con questo nome già esistente nel progetto'}), 400
    
    # Create new label
    label = Label(
        project_id=project.id,
        name=name,
        description=description,
        color=color,
        categories=categories,
        created_by=user.id,
        usage_count=0
    )
    
    db.session.add(label)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Etichetta creata con successo',
        'label': label.to_dict()
    }), 201

@api_bp.route('/projects/<uuid:project_id>/labels/<int:label_id>', methods=['PUT'])
@jwt_or_login_required  
def api_update_project_label(project_id, label_id):
    """Update existing label"""
    user = get_current_api_user()
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first_or_404()
    label = Label.query.filter_by(id=label_id, project_id=project.id).first_or_404()
    
    data = request.get_json()
    
    # Update fields if provided
    if 'name' in data:
        name = data['name'].strip()
        if not name:
            return jsonify({'error': 'Nome etichetta non può essere vuoto'}), 400
        
        # Check uniqueness
        existing = Label.query.filter_by(project_id=project.id, name=name)\
            .filter(Label.id != label.id).first()
        if existing:
            return jsonify({'error': 'Etichetta con questo nome già esistente'}), 400
        
        label.name = name
    
    if 'description' in data:
        description = data['description'].strip()
        if not description:
            return jsonify({'error': 'Descrizione etichetta non può essere vuota'}), 400
        label.description = description
    
    if 'color' in data:
        label.color = data['color']
    
    if 'categories' in data:
        label.categories = data['categories']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Etichetta aggiornata con successo',
        'label': label.to_dict()
    })

@api_bp.route('/projects/<uuid:project_id>/labels/<int:label_id>', methods=['DELETE'])
@jwt_or_login_required
def api_delete_project_label(project_id, label_id):
    """Delete label (only if not used)"""
    user = get_current_api_user()
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first_or_404()
    label = Label.query.filter_by(id=label_id, project_id=project.id).first_or_404()
    
    # Check if label is used in applications
    from app.models_labeling import LabelApplication
    applications_count = LabelApplication.query.filter_by(label_id=label.id).count()
    
    if applications_count > 0:
        return jsonify({
            'error': f'Impossibile eliminare etichetta: utilizzata in {applications_count} applicazioni'
        }), 400
    
    db.session.delete(label)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Etichetta eliminata con successo'
    })

# Applicazione Etichette
@api_bp.route('/projects/<uuid:project_id>/labels/apply-manual', methods=['POST'])
@jwt_or_login_required
def api_apply_manual_labels(project_id):
    """Apply labels manually (immediate application)"""
    user = get_current_api_user()
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first_or_404()
    
    data = request.get_json()
    label_id = data.get('label_id')
    target_cells = data.get('target_cells', [])  # List of {sheet_id, row_index, column_name, cell_value}
    
    if not label_id:
        return jsonify({'error': 'ID etichetta richiesto'}), 400
    
    if not target_cells:
        return jsonify({'error': 'Celle target richieste'}), 400
    
    # Verify label exists in project
    label = Label.query.filter_by(id=label_id, project_id=project.id).first_or_404()
    
    from app.models_labeling import LabelApplication
    from datetime import datetime
    
    applications_created = []
    
    for cell in target_cells:
        # Verify sheet belongs to project
        sheet = ExcelSheet.query.filter_by(
            id=cell.get('sheet_id'),
            file_id=File.project_id.is_(project.id)
        ).first()
        
        if not sheet:
            continue  # Skip invalid sheets
        
        # Create application
        application = LabelApplication(
            project_id=project.id,
            sheet_id=cell.get('sheet_id'),
            label_id=label.id,
            applied_by=user.id,
            row_index=cell.get('row_index'),
            column_name=cell.get('column_name'),
            cell_value=cell.get('cell_value'),
            application_type='manual',
            is_active=True,
            applied_at=datetime.utcnow()
        )
        
        db.session.add(application)
        applications_created.append(application)
    
    # Update label usage count
    label.usage_count = (label.usage_count or 0) + len(applications_created)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Etichette applicate manualmente a {len(applications_created)} celle',
        'applications_created': len(applications_created),
        'label_used': label.to_dict()
    }), 201

@api_bp.route('/projects/<uuid:project_id>/labels/apply-ai', methods=['POST'])
@jwt_or_login_required
def api_request_ai_labeling(project_id):
    """Request AI labeling (requires authorization)"""
    user = get_current_api_user()
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first_or_404()
    
    data = request.get_json()
    target_cells = data.get('target_cells', [])
    ai_prompt = data.get('ai_prompt', '')
    
    if not target_cells:
        return jsonify({'error': 'Celle target richieste'}), 400
    
    if not ai_prompt:
        return jsonify({'error': 'Prompt AI richiesto'}), 400
    
    # Simulate AI label suggestions
    import random
    from app.models_labeling import LabelApplication
    from datetime import datetime
    
    # Get existing labels for this project to suggest from
    existing_labels = Label.query.filter_by(project_id=project.id).all()
    
    pending_applications = []
    
    for cell in target_cells:
        if existing_labels:
            suggested_label = random.choice(existing_labels)
        else:
            # Create a temporary suggested label
            suggested_label = None
        
        # Create pending application (requires authorization)
        application = LabelApplication(
            project_id=project.id,
            sheet_id=cell.get('sheet_id'),
            label_id=suggested_label.id if suggested_label else None,
            applied_by=user.id,
            row_index=cell.get('row_index'),
            column_name=cell.get('column_name'),
            cell_value=cell.get('cell_value'),
            application_type='ai_pending',  # Pending authorization
            confidence_score=random.uniform(0.7, 0.95),
            ai_reasoning=f'AI analizzato il testo "{cell.get("cell_value", "")[:50]}..." con prompt "{ai_prompt[:50]}..."',
            is_active=False,  # Not active until authorized
            applied_at=datetime.utcnow()
        )
        
        db.session.add(application)
        pending_applications.append(application)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Richieste AI create per {len(pending_applications)} celle',
        'pending_applications': len(pending_applications),
        'status': 'pending_authorization',
        'note': 'Le applicazioni AI richiedono autorizzazione prima di essere attive'
    }), 201

@api_bp.route('/projects/<uuid:project_id>/labels/authorize/<uuid:application_id>', methods=['PUT'])
@jwt_or_login_required
def api_authorize_ai_application(project_id, application_id):
    """Authorize or reject AI label application"""
    user = get_current_api_user()
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first_or_404()
    
    from app.models_labeling import LabelApplication
    application = LabelApplication.query.filter_by(
        id=application_id, 
        project_id=project.id,
        application_type='ai_pending'
    ).first_or_404()
    
    data = request.get_json()
    action = data.get('action')  # 'approve' or 'reject'
    
    if action not in ['approve', 'reject']:
        return jsonify({'error': 'Azione deve essere "approve" o "reject"'}), 400
    
    from datetime import datetime
    
    if action == 'approve':
        application.application_type = 'ai_approved'
        application.is_active = True
        application.authorized_by = user.id
        application.authorized_at = datetime.utcnow()
        
        # Update label usage count
        if application.label_id:
            label = Label.query.get(application.label_id)
            if label:
                label.usage_count = (label.usage_count or 0) + 1
        
        message = 'Applicazione AI approvata'
    else:
        application.application_type = 'ai_rejected'
        application.is_active = False
        application.authorized_by = user.id
        application.authorized_at = datetime.utcnow()
        
        message = 'Applicazione AI rifiutata'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': message,
        'application': {
            'id': str(application.id),
            'status': application.application_type,
            'is_active': application.is_active,
            'authorized_by': str(application.authorized_by),
            'authorized_at': application.authorized_at.isoformat() if application.authorized_at else None
        }
    })

# Gestione Suggerimenti
@api_bp.route('/projects/<uuid:project_id>/suggestions')
@jwt_or_login_required
def api_project_suggestions(project_id):
    """Get all pending suggestions for project"""
    user = get_current_api_user()
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first_or_404()
    
    from app.models_labeling import LabelSuggestion, LabelApplication
    
    # Get pending label suggestions (for store)
    label_suggestions = LabelSuggestion.query.filter_by(
        project_id=project.id,
        status='pending'
    ).order_by(LabelSuggestion.created_at.desc()).all()
    
    # Get pending AI applications (for authorization)
    pending_applications = LabelApplication.query.filter_by(
        project_id=project.id,
        application_type='ai_pending'
    ).order_by(LabelApplication.applied_at.desc()).all()
    
    return jsonify({
        'success': True,
        'suggestions': {
            'store_labels': [s.to_dict() for s in label_suggestions],
            'ai_applications': [{
                'id': str(app.id),
                'row_index': app.row_index,
                'column_name': app.column_name,
                'cell_value': app.cell_value,
                'suggested_label_id': app.label_id,
                'confidence_score': app.confidence_score,
                'ai_reasoning': app.ai_reasoning,
                'applied_at': app.applied_at.isoformat()
            } for app in pending_applications]
        },
        'counts': {
            'pending_store_labels': len(label_suggestions),
            'pending_ai_applications': len(pending_applications),
            'total_pending': len(label_suggestions) + len(pending_applications)
        }
    })

@api_bp.route('/projects/<uuid:project_id>/suggestions/<uuid:suggestion_id>/approve', methods=['PUT'])
@jwt_or_login_required
def api_approve_suggestion(project_id, suggestion_id):
    """Approve label suggestion for store"""
    user = get_current_api_user()
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first_or_404()
    
    from app.models_labeling import LabelSuggestion
    suggestion = LabelSuggestion.query.filter_by(
        id=suggestion_id,
        project_id=project.id,
        status='pending'
    ).first_or_404()
    
    data = request.get_json()
    action = data.get('action')  # 'approve' or 'reject'
    
    if action not in ['approve', 'reject']:
        return jsonify({'error': 'Azione deve essere "approve" o "reject"'}), 400
    
    from datetime import datetime
    
    if action == 'approve':
        # Create new label in store
        label = Label(
            project_id=project.id,
            name=suggestion.suggested_name,
            description=suggestion.suggested_description,
            color='#1976d2',  # Default color
            categories=[suggestion.suggested_category] if suggestion.suggested_category else [],
            created_by=user.id,
            usage_count=0
        )
        
        db.session.add(label)
        suggestion.status = 'approved'
        suggestion.reviewed_by = user.id
        suggestion.reviewed_at = datetime.utcnow()
        
        message = 'Suggerimento approvato e etichetta aggiunta al store'
    else:
        suggestion.status = 'rejected'
        suggestion.reviewed_by = user.id
        suggestion.reviewed_at = datetime.utcnow()
        
        message = 'Suggerimento rifiutato'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': message,
        'suggestion_status': suggestion.status
    })

# AI Suggestions for Store Labels
@api_bp.route('/projects/<uuid:project_id>/labels/ai-suggest', methods=['POST'])
@jwt_or_login_required
def api_ai_suggest_store_labels(project_id):
    """AI suggests new labels for project store"""
    user = get_current_api_user()
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first_or_404()
    
    data = request.get_json()
    sample_data = data.get('sample_data', [])  # Sample cell values for analysis
    analysis_context = data.get('context', '')  # Additional context for AI
    
    if not sample_data:
        return jsonify({'error': 'Dati campione richiesti per analisi AI'}), 400
    
    # Simulate AI analysis for new label suggestions
    import random
    from app.models_labeling import LabelSuggestion
    from datetime import datetime
    
    # Simulated AI suggestions based on data analysis
    suggested_categories = ['sentiment', 'emotion', 'topic', 'intent', 'behavior']
    suggestions_created = []
    
    for i in range(random.randint(2, 5)):  # Generate 2-5 suggestions
        category = random.choice(suggested_categories)
        
        suggestion = LabelSuggestion(
            project_id=project.id,
            suggestion_type='store_label',
            suggested_name=f'{category.title()}_AI_{i+1}',
            suggested_description=f'Etichetta {category} suggerita da AI basata su analisi dati progetto',
            suggested_category=category,
            ai_confidence=random.uniform(0.7, 0.9),
            ai_reasoning=f'Analisi AI ha identificato pattern {category} ricorrenti nei dati campione',
            sample_values=sample_data[:5],  # Store sample values used for analysis
            status='pending',
            created_by=user.id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(suggestion)
        suggestions_created.append(suggestion)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'AI ha generato {len(suggestions_created)} suggerimenti per nuove etichette',
        'suggestions_created': len(suggestions_created),
        'note': 'I suggerimenti richiedono approvazione prima di essere aggiunti al store'
    }), 201

# TASK 2.4: Store Etichette - Statistiche Dettagliate
@api_bp.route('/projects/<uuid:project_id>/labels/stats')
@jwt_or_login_required
def api_project_labels_stats(project_id):
    """Get detailed statistics for project labels (Task 2.4)"""
    user = get_current_api_user()
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first_or_404()
    
    from app.models_labeling import LabelApplication, LabelSuggestion
    from sqlalchemy import func, desc
    from datetime import datetime, timedelta
    
    # Basic counts
    total_labels = Label.query.filter_by(project_id=project.id).count()
    total_applications = LabelApplication.query.filter_by(project_id=project.id).count()
    
    # Application types breakdown
    manual_applications = LabelApplication.query.filter_by(
        project_id=project.id, 
        application_type='manual'
    ).count()
    
    ai_applications = LabelApplication.query.filter(
        LabelApplication.project_id == project.id,
        LabelApplication.application_type.in_(['ai_single', 'ai_batch'])
    ).count()
    
    # Most used labels
    most_used_labels = db.session.query(
        Label.id, Label.name, Label.color,
        func.count(LabelApplication.id).label('usage_count')
    ).join(LabelApplication).filter(
        Label.project_id == project.id
    ).group_by(Label.id, Label.name, Label.color)\
     .order_by(desc('usage_count')).limit(10).all()
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_applications = LabelApplication.query.filter(
        LabelApplication.project_id == project.id,
        LabelApplication.applied_at >= week_ago
    ).count()
    
    # Pending AI suggestions for store
    pending_suggestions = LabelSuggestion.query.filter_by(
        project_id=project.id,
        suggestion_type='store_label',
        status='pending'
    ).count()
    
    # Labels with no usage
    unused_labels = db.session.query(Label).filter(
        Label.project_id == project.id,
        ~Label.id.in_(
            db.session.query(LabelApplication.label_id).filter(
                LabelApplication.project_id == project.id
            )
        )
    ).count()
    
    return jsonify({
        'success': True,
        'statistics': {
            'overview': {
                'total_labels': total_labels,
                'total_applications': total_applications,
                'unused_labels': unused_labels,
                'pending_ai_suggestions': pending_suggestions
            },
            'applications': {
                'manual': manual_applications,
                'ai': ai_applications,
                'recent_week': recent_applications,
                'manual_percentage': round((manual_applications / total_applications) * 100, 1) if total_applications > 0 else 0,
                'ai_percentage': round((ai_applications / total_applications) * 100, 1) if total_applications > 0 else 0
            },
            'most_used_labels': [
                {
                    'id': label.id,
                    'name': label.name,
                    'color': label.color,
                    'usage_count': label.usage_count
                } for label in most_used_labels
            ],
            'activity': {
                'last_week_applications': recent_applications
            }
        }
    })

# Task 2.5 - Notifications System
@api_bp.route('/notifications/count')
@jwt_or_login_required
def api_notifications_count():
    """Get notification count for current user"""
    user = get_current_api_user()
    
    from app.models_labeling import LabelSuggestion, LabelApplication
    
    # Count pending suggestions across all user's projects
    user_projects = Project.query.filter_by(owner_id=user.id).all()
    project_ids = [p.id for p in user_projects]
    
    # Store label suggestions count
    pending_store_suggestions = LabelSuggestion.query.filter(
        LabelSuggestion.project_id.in_(project_ids),
        LabelSuggestion.status == 'pending'
    ).count()
    
    # AI applications requiring authorization
    pending_ai_applications = LabelApplication.query.filter(
        LabelApplication.project_id.in_(project_ids),
        LabelApplication.authorization_status == 'pending'
    ).count()
    
    total_notifications = pending_store_suggestions + pending_ai_applications
    
    return jsonify({
        'success': True,
        'notifications': {
            'pending_store_suggestions': pending_store_suggestions,
            'pending_ai_applications': pending_ai_applications,
            'total': total_notifications
        }
    })