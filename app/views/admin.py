"""
Views per il pannello di amministrazione
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from app.database import db
from app.models import User, Project
from app.models_admin import (
    GlobalLLMConfiguration, UserRole, UserRoleAssignment, 
    SystemSettings, AuditLog
)
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ================================
# DECORATORI E UTILITY
# ================================

def admin_required(f):
    """Decoratore per richiedere permessi di amministratore"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Accesso richiesto', 'error')
            return redirect(url_for('auth.login'))
        
        # Controlla se l'utente è admin
        if not has_permission(current_user, 'admin_access'):
            flash('Accesso negato: permessi di amministratore richiesti', 'error')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def has_permission(user, permission: str) -> bool:
    """Controlla se un utente ha un determinato permesso"""
    # Super admin ha tutti i permessi
    if hasattr(user, 'is_superuser') and user.is_superuser:
        return True
    
    # Controlla i ruoli dell'utente
    assignments = UserRoleAssignment.query.filter_by(user_id=user.id).all()
    for assignment in assignments:
        role = assignment.role
        if role and role.permissions:
            if permission in role.permissions:
                return True
    
    # Fallback per compatibilità - se non ci sono ruoli, considera admin chi ha is_admin=True
    return hasattr(user, 'is_admin') and user.is_admin

def log_action(action: str, resource_type: str = None, resource_id: str = None, 
               description: str = None, old_values: dict = None, new_values: dict = None):
    """Registra un'azione nel log di audit"""
    try:
        log_entry = AuditLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            description=description,
            old_values=old_values,
            new_values=new_values,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        logger.error(f"Errore nel logging audit: {str(e)}")

# ================================
# DASHBOARD AMMINISTRAZIONE
# ================================

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Dashboard principale dell'amministrazione"""
    # Statistiche generali
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'total_projects': Project.query.count(),
        'total_llm_configs': GlobalLLMConfiguration.query.count(),
        'active_llm_configs': GlobalLLMConfiguration.query.filter_by(is_active=True).count()
    }
    
    # Utenti registrati negli ultimi 30 giorni
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_users = User.query.filter(User.created_at >= thirty_days_ago).count()
    stats['recent_users'] = recent_users
    
    # Progetti creati negli ultimi 30 giorni
    recent_projects = Project.query.filter(Project.created_at >= thirty_days_ago).count()
    stats['recent_projects'] = recent_projects
    
    # Ultimi log di audit
    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    
    # Configurazione LLM attiva
    active_llm_config = GlobalLLMConfiguration.query.filter_by(is_active=True, is_default=True).first()
    
    # Impostazioni sistema
    system_settings = SystemSettings.query.first()
    
    if request.is_json:
        return jsonify({
            'stats': stats,
            'recent_logs': [log.to_dict() for log in recent_logs],
            'active_llm_config': active_llm_config.to_dict() if active_llm_config else None,
            'system_settings': system_settings.to_dict() if system_settings else None
        })
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_logs=recent_logs,
                         active_llm_config=active_llm_config,
                         system_settings=system_settings)

# ================================
# GESTIONE UTENTI
# ================================

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Gestione utenti"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filtri
    search = request.args.get('search', '').strip()
    role_filter = request.args.get('role')
    status_filter = request.args.get('status')
    
    # Query base
    query = User.query
    
    # Applica filtri
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%')
            )
        )
    
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    
    if role_filter:
        query = query.join(UserRoleAssignment).join(UserRole).filter(UserRole.name == role_filter)
    
    # Paginazione
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Ruoli disponibili
    roles = UserRole.query.all()
    
    if request.is_json:
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': users.page,
                'pages': users.pages,
                'per_page': users.per_page,
                'total': users.total
            },
            'roles': [role.to_dict() for role in roles]
        })
    
    return render_template('admin/users.html',
                         users=users,
                         roles=roles,
                         search=search,
                         role_filter=role_filter,
                         status_filter=status_filter)

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """Dettaglio utente"""
    user = User.query.get_or_404(user_id)
    
    # Ruoli dell'utente
    role_assignments = UserRoleAssignment.query.filter_by(user_id=user.id).all()
    
    # Progetti dell'utente
    projects = Project.query.filter_by(owner_id=user.id).all()
    
    # Log attività recenti
    recent_logs = AuditLog.query.filter_by(user_id=user.id)\
        .order_by(AuditLog.timestamp.desc()).limit(20).all()
    
    if request.is_json:
        return jsonify({
            'user': user.to_dict(),
            'role_assignments': [ra.role.to_dict() for ra in role_assignments],
            'projects': [p.to_dict() for p in projects],
            'recent_logs': [log.to_dict() for log in recent_logs]
        })
    
    return render_template('admin/user_detail.html',
                         user=user,
                         role_assignments=role_assignments,
                         projects=projects,
                         recent_logs=recent_logs)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Modifica utente"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form.to_dict()
            
            old_values = {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active
            }
            
            # Aggiorna campi
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.is_active = bool(data.get('is_active', user.is_active))
            
            # Gestisci ruoli
            new_role_ids = data.get('role_ids', [])
            if isinstance(new_role_ids, str):
                new_role_ids = [int(new_role_ids)] if new_role_ids else []
            elif isinstance(new_role_ids, list):
                new_role_ids = [int(rid) for rid in new_role_ids if rid]
            
            # Rimuovi ruoli esistenti
            UserRoleAssignment.query.filter_by(user_id=user.id).delete()
            
            # Aggiungi nuovi ruoli
            for role_id in new_role_ids:
                assignment = UserRoleAssignment(
                    user_id=user.id,
                    role_id=role_id,
                    assigned_by=current_user.id
                )
                db.session.add(assignment)
            
            db.session.commit()
            
            # Log azione
            log_action(
                action='user_updated',
                resource_type='user',
                resource_id=user.id,
                description=f'Utente {user.username} aggiornato',
                old_values=old_values,
                new_values={
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active,
                    'role_ids': new_role_ids
                }
            )
            
            message = f'Utente {user.username} aggiornato con successo'
            if request.is_json:
                return jsonify({'message': message, 'user': user.to_dict()})
            
            flash(message, 'success')
            return redirect(url_for('admin.user_detail', user_id=user.id))
            
        except Exception as e:
            logger.error(f"Errore nell'aggiornamento utente: {str(e)}")
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': str(e)}), 500
            flash(f'Errore nell\'aggiornamento: {str(e)}', 'error')
    
    # GET request
    roles = UserRole.query.all()
    user_role_ids = [ra.role_id for ra in UserRoleAssignment.query.filter_by(user_id=user.id)]
    
    return render_template('admin/edit_user.html',
                         user=user,
                         roles=roles,
                         user_role_ids=user_role_ids)

# ================================
# GESTIONE CONFIGURAZIONI LLM
# ================================

@admin_bp.route('/llm-configs')
@login_required
@admin_required
def manage_llm_configs():
    """Gestione configurazioni LLM globali"""
    configs = GlobalLLMConfiguration.query.order_by(
        GlobalLLMConfiguration.is_default.desc(),
        GlobalLLMConfiguration.created_at.desc()
    ).all()
    
    if request.is_json:
        return jsonify({
            'configs': [config.to_dict() for config in configs]
        })
    
    return render_template('admin/llm_configs.html', configs=configs)

@admin_bp.route('/llm-configs/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_llm_config():
    """Crea nuova configurazione LLM"""
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form.to_dict()
            
            # Se è impostata come default, rimuovi default dalle altre
            if data.get('is_default'):
                GlobalLLMConfiguration.query.update({'is_default': False})
            
            config = GlobalLLMConfiguration(
                name=data.get('name'),
                description=data.get('description', ''),
                provider=data.get('provider'),
                model_name=data.get('model_name'),
                api_url=data.get('api_url', ''),
                max_tokens=int(data.get('max_tokens', 4000)),
                temperature=float(data.get('temperature', 0.7)),
                top_p=float(data.get('top_p', 1.0)),
                frequency_penalty=float(data.get('frequency_penalty', 0.0)),
                presence_penalty=float(data.get('presence_penalty', 0.0)),
                max_requests_per_minute=int(data.get('max_requests_per_minute', 60)),
                max_requests_per_day=int(data.get('max_requests_per_day', 1000)),
                cost_per_token=float(data.get('cost_per_token', 0.0)),
                is_active=bool(data.get('is_active', True)),
                is_default=bool(data.get('is_default', False)),
                created_by=current_user.id
            )
            
            # Cripta e salva API key
            api_key = data.get('api_key', '').strip()
            if api_key:
                config.set_api_key(api_key)
            
            db.session.add(config)
            db.session.commit()
            
            # Log azione
            log_action(
                action='llm_config_created',
                resource_type='llm_config',
                resource_id=config.id,
                description=f'Configurazione LLM "{config.name}" creata'
            )
            
            message = f'Configurazione LLM "{config.name}" creata con successo'
            if request.is_json:
                return jsonify({'message': message, 'config': config.to_dict()}), 201
            
            flash(message, 'success')
            return redirect(url_for('admin.manage_llm_configs'))
            
        except Exception as e:
            logger.error(f"Errore nella creazione configurazione LLM: {str(e)}")
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': str(e)}), 500
            flash(f'Errore nella creazione: {str(e)}', 'error')
    
    # Template per providers comuni
    provider_templates = {
        'openai': {
            'name': 'OpenAI GPT',
            'api_url': 'https://api.openai.com/v1',
            'models': ['gpt-4', 'gpt-4-turbo-preview', 'gpt-3.5-turbo']
        },
        'anthropic': {
            'name': 'Anthropic Claude',
            'api_url': 'https://api.anthropic.com',
            'models': ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307']
        },
        'google': {
            'name': 'Google PaLM',
            'api_url': 'https://generativelanguage.googleapis.com',
            'models': ['text-bison-001', 'chat-bison-001']
        }
    }
    
    return render_template('admin/create_llm_config.html', 
                         provider_templates=provider_templates)

# ================================
# IMPOSTAZIONI SISTEMA
# ================================

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def system_settings():
    """Gestione impostazioni sistema"""
    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings()
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form.to_dict()
            
            old_values = settings.to_dict()
            
            # Aggiorna impostazioni
            settings.app_name = data.get('app_name', settings.app_name)
            settings.app_description = data.get('app_description', settings.app_description)
            settings.theme = data.get('theme', settings.theme)
            settings.primary_color = data.get('primary_color', settings.primary_color)
            settings.secondary_color = data.get('secondary_color', settings.secondary_color)
            settings.max_projects_per_user = int(data.get('max_projects_per_user', settings.max_projects_per_user))
            settings.max_file_size_mb = int(data.get('max_file_size_mb', settings.max_file_size_mb))
            settings.max_files_per_project = int(data.get('max_files_per_project', settings.max_files_per_project))
            settings.session_timeout_minutes = int(data.get('session_timeout_minutes', settings.session_timeout_minutes))
            settings.password_min_length = int(data.get('password_min_length', settings.password_min_length))
            settings.require_email_verification = bool(data.get('require_email_verification', settings.require_email_verification))
            settings.max_login_attempts = int(data.get('max_login_attempts', settings.max_login_attempts))
            settings.enable_email_notifications = bool(data.get('enable_email_notifications', settings.enable_email_notifications))
            settings.enable_system_logs = bool(data.get('enable_system_logs', settings.enable_system_logs))
            settings.log_level = data.get('log_level', settings.log_level)
            settings.maintenance_mode = bool(data.get('maintenance_mode', settings.maintenance_mode))
            settings.maintenance_message = data.get('maintenance_message', settings.maintenance_message)
            settings.updated_by = current_user.id
            
            db.session.commit()
            
            # Log azione
            log_action(
                action='system_settings_updated',
                resource_type='system_settings',
                resource_id=settings.id,
                description='Impostazioni sistema aggiornate',
                old_values=old_values,
                new_values=settings.to_dict()
            )
            
            message = 'Impostazioni sistema aggiornate con successo'
            if request.is_json:
                return jsonify({'message': message, 'settings': settings.to_dict()})
            
            flash(message, 'success')
            return redirect(url_for('admin.system_settings'))
            
        except Exception as e:
            logger.error(f"Errore nell'aggiornamento impostazioni: {str(e)}")
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': str(e)}), 500
            flash(f'Errore nell\'aggiornamento: {str(e)}', 'error')
    
    return render_template('admin/settings.html', settings=settings)

# ================================
# LOG DI AUDIT
# ================================

@admin_bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    """Visualizza log di audit"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Filtri
    user_filter = request.args.get('user')
    action_filter = request.args.get('action')
    resource_filter = request.args.get('resource_type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Query base
    query = AuditLog.query
    
    # Applica filtri
    if user_filter:
        query = query.filter(AuditLog.user_id == user_filter)
    
    if action_filter:
        query = query.filter(AuditLog.action.ilike(f'%{action_filter}%'))
    
    if resource_filter:
        query = query.filter(AuditLog.resource_type == resource_filter)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(AuditLog.timestamp >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(AuditLog.timestamp < date_to_obj)
        except ValueError:
            pass
    
    # Paginazione
    logs = query.order_by(AuditLog.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Opzioni per filtri
    users = User.query.all()
    actions = db.session.query(AuditLog.action).distinct().all()
    resource_types = db.session.query(AuditLog.resource_type).filter(AuditLog.resource_type.isnot(None)).distinct().all()
    
    if request.is_json:
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'pagination': {
                'page': logs.page,
                'pages': logs.pages,
                'per_page': logs.per_page,
                'total': logs.total
            }
        })
    
    return render_template('admin/audit_logs.html',
                         logs=logs,
                         users=users,
                         actions=[a[0] for a in actions],
                         resource_types=[rt[0] for rt in resource_types],
                         filters={
                             'user': user_filter,
                             'action': action_filter,
                             'resource_type': resource_filter,
                             'date_from': date_from,
                             'date_to': date_to
                         })