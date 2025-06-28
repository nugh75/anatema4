"""
Modelli per il sistema di amministrazione
"""

from app.database import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from cryptography.fernet import Fernet
import os

class GlobalLLMConfiguration(db.Model):
    """Configurazione globale dell'LLM per tutta l'applicazione"""
    __tablename__ = 'global_llm_configurations'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Configurazione base
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=False)
    is_default = db.Column(db.Boolean, default=False)
    
    # Provider e modello
    provider = db.Column(db.String(50), nullable=False)  # 'openai', 'anthropic', 'google', etc.
    model_name = db.Column(db.String(100), nullable=False)
    api_url = db.Column(db.String(255))
    
    # Credenziali (criptate)
    api_key_encrypted = db.Column(db.Text)
    additional_headers = db.Column(db.JSON)  # Per header aggiuntivi
    
    # Parametri modello
    max_tokens = db.Column(db.Integer, default=4000)
    temperature = db.Column(db.Float, default=0.7)
    top_p = db.Column(db.Float, default=1.0)
    frequency_penalty = db.Column(db.Float, default=0.0)
    presence_penalty = db.Column(db.Float, default=0.0)
    
    # Limiti e controlli
    max_requests_per_minute = db.Column(db.Integer, default=60)
    max_requests_per_day = db.Column(db.Integer, default=1000)
    cost_per_token = db.Column(db.Float, default=0.0)
    
    # Metadati
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    
    # Statistiche utilizzo
    total_requests = db.Column(db.Integer, default=0)
    total_tokens_used = db.Column(db.Integer, default=0)
    total_cost = db.Column(db.Float, default=0.0)
    last_used_at = db.Column(db.DateTime)
    
    def set_api_key(self, api_key: str):
        """Cripta e salva la API key"""
        if api_key:
            key = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
            f = Fernet(key)
            self.api_key_encrypted = f.encrypt(api_key.encode()).decode()
    
    def get_api_key(self) -> str:
        """Decripta e restituisce la API key"""
        if self.api_key_encrypted:
            key = os.environ.get('ENCRYPTION_KEY')
            if key:
                f = Fernet(key.encode() if isinstance(key, str) else key)
                return f.decrypt(self.api_key_encrypted.encode()).decode()
        return ''
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'provider': self.provider,
            'model_name': self.model_name,
            'api_url': self.api_url,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'max_requests_per_minute': self.max_requests_per_minute,
            'max_requests_per_day': self.max_requests_per_day,
            'total_requests': self.total_requests,
            'total_tokens_used': self.total_tokens_used,
            'total_cost': self.total_cost,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None
        }

class UserRole(db.Model):
    """Ruoli degli utenti"""
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    permissions = db.Column(db.JSON)  # Lista di permessi
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions or [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserRoleAssignment(db.Model):
    """Assegnazione ruoli agli utenti"""
    __tablename__ = 'user_role_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('user_roles.id'), nullable=False)
    
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    
    # Relazioni
    role = db.relationship('UserRole')
    assigned_by_user = db.relationship('User', foreign_keys=[assigned_by])

class SystemSettings(db.Model):
    """Impostazioni generali del sistema"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Informazioni applicazione
    app_name = db.Column(db.String(100), default='Anatema')
    app_version = db.Column(db.String(20), default='2.0.0')
    app_description = db.Column(db.Text)
    
    # Configurazioni UI
    theme = db.Column(db.String(20), default='light')  # 'light', 'dark', 'auto'
    primary_color = db.Column(db.String(7), default='#1976d2')
    secondary_color = db.Column(db.String(7), default='#dc004e')
    
    # Limiti globali
    max_projects_per_user = db.Column(db.Integer, default=10)
    max_file_size_mb = db.Column(db.Integer, default=100)
    max_files_per_project = db.Column(db.Integer, default=50)
    
    # Sicurezza
    session_timeout_minutes = db.Column(db.Integer, default=120)
    password_min_length = db.Column(db.Integer, default=8)
    require_email_verification = db.Column(db.Boolean, default=False)
    max_login_attempts = db.Column(db.Integer, default=5)
    
    # Email settings
    smtp_server = db.Column(db.String(255))
    smtp_port = db.Column(db.Integer, default=587)
    smtp_username = db.Column(db.String(255))
    smtp_password_encrypted = db.Column(db.Text)
    smtp_use_tls = db.Column(db.Boolean, default=True)
    
    # Notifiche
    enable_email_notifications = db.Column(db.Boolean, default=False)
    enable_system_logs = db.Column(db.Boolean, default=True)
    log_level = db.Column(db.String(20), default='INFO')
    
    # Manutenzione
    maintenance_mode = db.Column(db.Boolean, default=False)
    maintenance_message = db.Column(db.Text)
    
    # Metadati
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'app_name': self.app_name,
            'app_version': self.app_version,
            'app_description': self.app_description,
            'theme': self.theme,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'max_projects_per_user': self.max_projects_per_user,
            'max_file_size_mb': self.max_file_size_mb,
            'max_files_per_project': self.max_files_per_project,
            'session_timeout_minutes': self.session_timeout_minutes,
            'password_min_length': self.password_min_length,
            'require_email_verification': self.require_email_verification,
            'max_login_attempts': self.max_login_attempts,
            'enable_email_notifications': self.enable_email_notifications,
            'enable_system_logs': self.enable_system_logs,
            'log_level': self.log_level,
            'maintenance_mode': self.maintenance_mode,
            'maintenance_message': self.maintenance_message,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AuditLog(db.Model):
    """Log delle attività per auditing"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Chi, cosa, quando
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))  # 'user', 'project', 'llm_config', etc.
    resource_id = db.Column(db.String(100))
    
    # Dettagli
    description = db.Column(db.Text)
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    
    # Metadati
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazioni vengono gestite tramite foreign key e backref dal modello User
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': str(self.user_id) if self.user_id else None,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'description': self.description,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }