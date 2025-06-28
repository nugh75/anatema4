from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.database import db
from app.models import Project, File, Label
from datetime import datetime
import uuid

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/')
@login_required
def list_projects():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    projects = Project.query.filter_by(owner_id=current_user.id)\
        .order_by(Project.updated_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    if request.is_json:
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
    
    return render_template('projects/list.html', projects=projects)

@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            name = data.get('name', '').strip()
            description = data.get('description', '').strip()
            is_public = data.get('is_public', False)
        else:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            is_public = request.form.get('is_public') == 'on'
        
        if not name:
            if request.is_json:
                return jsonify({'error': 'Nome progetto richiesto'}), 400
            flash('Nome progetto richiesto', 'error')
            return render_template('projects/create.html')
        
        # Check if project name already exists for this user
        existing = Project.query.filter_by(owner_id=current_user.id, name=name).first()
        if existing:
            if request.is_json:
                return jsonify({'error': 'Progetto con questo nome già esistente'}), 400
            flash('Progetto con questo nome già esistente', 'error')
            return render_template('projects/create.html')
        
        project = Project(
            name=name,
            description=description,
            is_public=is_public,
            owner_id=current_user.id
        )
        
        db.session.add(project)
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'message': 'Progetto creato con successo',
                'project': project.to_dict()
            }), 201
        else:
            flash('Progetto creato con successo!', 'success')
            return redirect(url_for('projects.view_project', project_id=project.id))
    
    return render_template('projects/create.html')

@projects_bp.route('/<uuid:project_id>')
@login_required
def view_project(project_id):
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Get project files
    files = File.query.filter_by(project_id=project.id)\
        .order_by(File.uploaded_at.desc()).all()
    
    # Get project labels
    labels = Label.query.filter_by(project_id=project.id)\
        .order_by(Label.name).all()
    
    if request.is_json:
        return jsonify({
            'project': project.to_dict(),
            'files': [f.to_dict() for f in files],
            'labels': [l.to_dict() for l in labels]
        })
    
    return render_template('projects/view.html', 
                         project=project, 
                         files=files, 
                         labels=labels)

@projects_bp.route('/<uuid:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            name = data.get('name', '').strip()
            description = data.get('description', '').strip()
            is_public = data.get('is_public', False)
        else:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            is_public = request.form.get('is_public') == 'on'
        
        if not name:
            if request.is_json:
                return jsonify({'error': 'Nome progetto richiesto'}), 400
            flash('Nome progetto richiesto', 'error')
            return render_template('projects/edit.html', project=project)
        
        # Check if project name already exists for this user (excluding current project)
        existing = Project.query.filter(
            Project.owner_id == current_user.id,
            Project.name == name,
            Project.id != project.id
        ).first()
        
        if existing:
            if request.is_json:
                return jsonify({'error': 'Progetto con questo nome già esistente'}), 400
            flash('Progetto con questo nome già esistente', 'error')
            return render_template('projects/edit.html', project=project)
        
        project.name = name
        project.description = description
        project.is_public = is_public
        project.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'message': 'Progetto aggiornato con successo',
                'project': project.to_dict()
            })
        else:
            flash('Progetto aggiornato con successo!', 'success')
            return redirect(url_for('projects.view_project', project_id=project.id))
    
    return render_template('projects/edit.html', project=project)

@projects_bp.route('/<uuid:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    project_name = project.name
    db.session.delete(project)
    db.session.commit()
    
    if request.is_json:
        return jsonify({'message': f'Progetto "{project_name}" eliminato con successo'})
    else:
        flash(f'Progetto "{project_name}" eliminato con successo', 'success')
        return redirect(url_for('projects.list_projects'))

@projects_bp.route('/<uuid:project_id>/stats')
@login_required
def project_stats(project_id):
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    # Get project statistics
    files_count = File.query.filter_by(project_id=project.id).count()
    labels_count = Label.query.filter_by(project_id=project.id).count()
    
    # Get file types distribution
    file_types = db.session.query(File.file_type, db.func.count(File.id))\
        .filter_by(project_id=project.id)\
        .group_by(File.file_type).all()
    
    # Get labels usage
    labels_usage = db.session.query(Label.name, db.func.count(Label.cell_labels))\
        .filter_by(project_id=project.id)\
        .group_by(Label.name).all()
    
    stats = {
        'project': project.to_dict(),
        'files_count': files_count,
        'labels_count': labels_count,
        'file_types': [{'type': ft[0], 'count': ft[1]} for ft in file_types],
        'labels_usage': [{'label': lu[0], 'usage': lu[1]} for lu in labels_usage]
    }
    
    return jsonify(stats)