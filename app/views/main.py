from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from app.database import db
from app.models import Project, File, Label
from sqlalchemy import func

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user statistics
    user_projects = Project.query.filter_by(owner_id=current_user.id).count()
    user_files = File.query.join(Project).filter(Project.owner_id == current_user.id).count()
    user_labels = Label.query.join(Project).filter(Project.owner_id == current_user.id).count()
    
    # Get recent projects
    recent_projects = Project.query.filter_by(owner_id=current_user.id)\
        .order_by(Project.updated_at.desc()).limit(5).all()
    
    # Get recent files
    recent_files = File.query.join(Project)\
        .filter(Project.owner_id == current_user.id)\
        .order_by(File.uploaded_at.desc()).limit(5).all()
    
    stats = {
        'projects_count': user_projects,
        'files_count': user_files,
        'labels_count': user_labels,
        'recent_projects': [p.to_dict() for p in recent_projects],
        'recent_files': [f.to_dict() for f in recent_files]
    }
    
    if request.is_json:
        return jsonify(stats)
    
    return render_template('main/dashboard.html', stats=stats)

@main_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'results': []})
    
    # Search in projects
    projects = Project.query.filter(
        Project.owner_id == current_user.id,
        Project.name.ilike(f'%{query}%')
    ).limit(10).all()
    
    # Search in files
    files = File.query.join(Project).filter(
        Project.owner_id == current_user.id,
        File.original_name.ilike(f'%{query}%')
    ).limit(10).all()
    
    # Search in labels
    labels = Label.query.join(Project).filter(
        Project.owner_id == current_user.id,
        Label.name.ilike(f'%{query}%')
    ).limit(10).all()
    
    results = {
        'projects': [p.to_dict() for p in projects],
        'files': [f.to_dict() for f in files],
        'labels': [l.to_dict() for l in labels]
    }
    
    return jsonify({'results': results})

@main_bp.route('/help')
def help():
    return render_template('main/help.html')

@main_bp.route('/about')
def about():
    return render_template('main/about.html')

@main_bp.route('/test_frontend.html')
def test_frontend():
    """Pagina di test per CRUD etichette"""
    return send_from_directory('.', 'test_frontend.html')