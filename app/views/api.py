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
    """Get project labels"""
    user = get_current_api_user()
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first_or_404()
    
    labels = Label.query.filter_by(project_id=project.id)\
        .order_by(Label.name).all()
    
    return jsonify({
        'project': project.to_dict(),
        'labels': [l.to_dict() for l in labels]
    })

@api_bp.route('/projects/<uuid:project_id>/labels', methods=['POST'])
@jwt_or_login_required
def api_create_label(project_id):
    """Create new label"""
    user = get_current_api_user()
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first_or_404()
    
    data = request.get_json()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    color = data.get('color', '#1976d2').strip()
    categories = data.get('categories', [])
    
    if not name:
        return jsonify({'error': 'Nome etichetta richiesto'}), 400
    
    # Check if label name already exists in this project
    existing = Label.query.filter_by(project_id=project.id, name=name).first()
    if existing:
        return jsonify({'error': 'Etichetta con questo nome già esistente'}), 400
    
    label = Label(
        project_id=project.id,
        name=name,
        description=description,
        color=color,
        categories=categories if categories else []
    )
    
    db.session.add(label)
    db.session.commit()
    
    return jsonify({
        'message': 'Etichetta creata con successo',
        'label': label.to_dict()
    }), 201

@api_bp.route('/labels/<int:label_id>/apply', methods=['POST'])
@jwt_or_login_required
def api_apply_label(label_id):
    """Apply label to cell"""
    user = get_current_api_user()
    data = request.get_json()
    
    row_id = data.get('row_id')
    column_index = data.get('column_index')
    cell_value = data.get('cell_value', '')
    
    if not row_id:
        return jsonify({'error': 'Row ID richiesto'}), 400
    
    # Verify row belongs to user's project
    row = ExcelRow.query.join(ExcelSheet).join(File).join(Project).filter(
        ExcelRow.id == row_id,
        Project.owner_id == user.id
    ).first()
    
    if not row:
        return jsonify({'error': 'Riga non trovata'}), 404
    
    # Verify label belongs to the same project
    label = Label.query.filter_by(id=label_id, project_id=row.sheet.file.project_id).first()
    
    if not label:
        return jsonify({'error': 'Etichetta non trovata'}), 404
    
    # Check if label already applied to this cell
    existing = CellLabel.query.filter_by(
        row_id=row_id,
        label_id=label_id,
        column_index=column_index
    ).first()
    
    if existing:
        return jsonify({'error': 'Etichetta già applicata a questa cella'}), 400
    
    # Create cell label
    cell_label = CellLabel(
        row_id=row_id,
        label_id=label_id,
        column_index=column_index,
        cell_value=cell_value,
        created_by=user.id
    )
    
    db.session.add(cell_label)
    db.session.commit()
    
    return jsonify({
        'message': 'Etichetta applicata con successo',
        'cell_label': cell_label.to_dict()
    }), 201

# Search endpoint
@api_bp.route('/search')
@jwt_or_login_required
def api_search():
    """Search across user's data"""
    user = get_current_api_user()
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'results': []})
    
    # Search in projects
    projects = Project.query.filter(
        Project.owner_id == user.id,
        Project.name.ilike(f'%{query}%')
    ).limit(10).all()
    
    # Search in files
    files = File.query.join(Project).filter(
        Project.owner_id == user.id,
        File.original_name.ilike(f'%{query}%')
    ).limit(10).all()
    
    # Search in labels
    labels = Label.query.join(Project).filter(
        Project.owner_id == user.id,
        Label.name.ilike(f'%{query}%')
    ).limit(10).all()
    
    results = {
        'projects': [p.to_dict() for p in projects],
        'files': [f.to_dict() for f in files],
        'labels': [l.to_dict() for l in labels]
    }
    
    return jsonify({'results': results})

# Labeling-specific API endpoints
@api_bp.route('/projects/<uuid:project_id>/sheets')
@jwt_or_login_required
def get_project_sheets(project_id):
    """API: Recupera fogli Excel di un progetto"""
    user = get_current_api_user()
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first()
    
    if not project:
        return jsonify({'error': 'Progetto non trovato'}), 404
    
    from app.models import ExcelSheet
    # Query corretta per recuperare fogli Excel
    sheets = ExcelSheet.query.join(File).filter(
        File.project_id == project.id
    ).all()
    
    return jsonify({
        'project': project.to_dict(),
        'sheets': [
            {
                'id': str(sheet.id),
                'name': sheet.name,
                'sheet_index': sheet.sheet_index,
                'row_count': sheet.row_count,
                'column_count': sheet.column_count,
                'file': {
                    'id': str(sheet.file.id),
                    'filename': sheet.file.filename,
                    'original_name': sheet.file.original_name,
                    'uploaded_at': sheet.file.uploaded_at.isoformat() if sheet.file.uploaded_at else None
                }
            } for sheet in sheets
        ]
    })

@api_bp.route('/column-preview')
@jwt_or_login_required
def get_column_preview():
    """Get column data preview for labeling"""
    user = get_current_api_user()
    project_id = request.args.get('project_id')
    column_name = request.args.get('column_name')
    limit = request.args.get('limit', 10, type=int)
    
    if not project_id or not column_name:
        return jsonify({'error': 'project_id e column_name richiesti'}), 400
    
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first()
    if not project:
        return jsonify({'error': 'Progetto non trovato'}), 404
    
    try:
        # Load project data
        import pandas as pd
        df = pd.read_excel(project.file_path)
        
        if column_name not in df.columns:
            return jsonify({'error': 'Colonna non trovata'}), 404
        
        # Get sample data
        column_data = df[column_name].head(limit).fillna('').tolist()
        
        return jsonify({
            'success': True,
            'data': column_data,
            'column_name': column_name,
            'total_rows': len(df)
        })
        
    except Exception as e:
        return jsonify({'error': f'Errore nel caricamento dati: {str(e)}'}), 500

@api_bp.route('/column-rows')
@jwt_or_login_required
def get_column_rows():
    """Get all rows for a specific column"""
    user = get_current_api_user()
    project_id = request.args.get('project_id')
    column_name = request.args.get('column_name')
    
    if not project_id or not column_name:
        return jsonify({'error': 'project_id e column_name richiesti'}), 400
    
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first()
    if not project:
        return jsonify({'error': 'Progetto non trovato'}), 404
    
    try:
        # Load project data
        import pandas as pd
        df = pd.read_excel(project.file_path)
        
        if column_name not in df.columns:
            return jsonify({'error': 'Colonna non trovata'}), 404
        
        # Get all column data
        column_data = df[column_name].fillna('').tolist()
        
        return jsonify({
            'success': True,
            'rows': column_data,
            'column_name': column_name,
            'total_rows': len(column_data)
        })
        
    except Exception as e:
        return jsonify({'error': f'Errore nel caricamento dati: {str(e)}'}), 500

@api_bp.route('/project-columns')
@jwt_or_login_required
def get_project_columns():
    """Get all columns for a project"""
    user = get_current_api_user()
    project_id = request.args.get('project_id')
    
    if not project_id:
        return jsonify({'error': 'project_id richiesto'}), 400
    
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first()
    if not project:
        return jsonify({'error': 'Progetto non trovato'}), 404
    
    try:
        # Load project data
        import pandas as pd
        df = pd.read_excel(project.file_path)
        
        columns = df.columns.tolist()
        
        return jsonify({
            'success': True,
            'items': columns,
            'total_columns': len(columns)
        })
        
    except Exception as e:
        return jsonify({'error': f'Errore nel caricamento colonne: {str(e)}'}), 500

@api_bp.route('/project-rows')
@jwt_or_login_required
def get_project_rows():
    """Get row indices for a project"""
    user = get_current_api_user()
    project_id = request.args.get('project_id')
    
    if not project_id:
        return jsonify({'error': 'project_id richiesto'}), 400
    
    project = Project.query.filter_by(id=project_id, owner_id=user.id).first()
    if not project:
        return jsonify({'error': 'Progetto non trovato'}), 404
    
    try:
        # Load project data
        import pandas as pd
        df = pd.read_excel(project.file_path)
        
        # Generate row indices
        row_indices = list(range(len(df)))
        
        return jsonify({
            'success': True,
            'items': row_indices,
            'total_rows': len(row_indices)
        })
        
    except Exception as e:
        return jsonify({'error': f'Errore nel caricamento righe: {str(e)}'}), 500

@api_bp.route('/generate-labels', methods=['POST'])
@jwt_or_login_required
def generate_labels():
    """Generate labels using AI"""
    user = get_current_api_user()
    data = request.get_json()
    
    prompt = data.get('prompt', '')
    column_data = data.get('column_data', [])
    column_name = data.get('column_name', '')
    
    if not prompt or not column_data:
        return jsonify({'error': 'prompt e column_data richiesti'}), 400
    
    try:
        # Mock AI response - in real implementation, integrate with actual AI service
        import random
        import time
        
        # Simulate AI processing time
        time.sleep(2)
        
        # Generate mock suggestions
        suggestions = []
        sentiment_labels = ['positivo', 'negativo', 'neutro']
        emotion_labels = ['gioia', 'tristezza', 'rabbia', 'paura', 'sorpresa', 'neutro']
        
        for i, text in enumerate(column_data[:10]):  # Process first 10 items
            if 'sentiment' in prompt.lower():
                label = random.choice(sentiment_labels)
            elif 'emoz' in prompt.lower():
                label = random.choice(emotion_labels)
            else:
                label = f'categoria_{random.randint(1, 5)}'
            
            confidence = random.uniform(0.6, 0.95)
            
            suggestions.append({
                'text': str(text),
                'suggested_label': label,
                'confidence': confidence,
                'reasoning': f'Analisi basata su pattern linguistici e contesto semantico del testo "{str(text)[:50]}..."'
            })
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'total_processed': len(suggestions),
            'metadata': {
                'column_name': column_name,
                'prompt_used': prompt,
                'processing_time': 2.0
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Errore nella generazione: {str(e)}'}), 500