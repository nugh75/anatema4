from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app.database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    projects = db.relationship('Project', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    uploaded_files = db.relationship('File', backref='uploader', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    
    # Relationships
    files = db.relationship('File', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    labels = db.relationship('Label', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description or '',
            'owner_id': str(self.owner_id),
            'owner_username': self.owner.username,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'files_count': self.files.count(),
            'labels_count': self.labels.count()
        }

class File(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    uploader_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    file_path = db.Column(db.String(500))
    processing_status = db.Column(db.String(20), default='pending')  # pending, processing, completed, error
    
    # Relationships
    sheets = db.relationship('ExcelSheet', backref='file', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_file_path(self):
        """Restituisce il percorso completo del file"""
        import os
        from flask import current_app
        
        if self.file_path:
            # Se il percorso è assoluto, usalo direttamente
            if os.path.isabs(self.file_path):
                return self.file_path
            else:
                # Altrimenti, costruisci il percorso relativo alla directory uploads
                upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                return os.path.join(upload_dir, self.file_path)
        else:
            # Fallback: costruisci il percorso basato su filename
            upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            return os.path.join(upload_dir, self.filename)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'filename': self.filename,
            'original_name': self.original_name,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'processing_status': self.processing_status,
            'uploaded_at': self.uploaded_at.isoformat(),
            'uploader_username': self.uploader.username,
            'sheets_count': self.sheets.count()
        }

class ExcelSheet(db.Model):
    __tablename__ = 'excel_sheets'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = db.Column(UUID(as_uuid=True), db.ForeignKey('files.id'), nullable=False)
    sheet_index = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    row_count = db.Column(db.Integer, default=0)
    column_count = db.Column(db.Integer, default=0)
    
    # Relationships
    columns = db.relationship('ExcelColumn', backref='sheet', lazy='dynamic', cascade='all, delete-orphan')
    rows = db.relationship('ExcelRow', backref='sheet', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'sheet_index': self.sheet_index,
            'row_count': self.row_count,
            'column_count': self.column_count
        }

class ExcelColumn(db.Model):
    __tablename__ = 'excel_columns'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sheet_id = db.Column(UUID(as_uuid=True), db.ForeignKey('excel_sheets.id'), nullable=False)
    column_index = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    data_type = db.Column(db.String(50), default='text')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'column_index': self.column_index,
            'data_type': self.data_type
        }

class ExcelRow(db.Model):
    __tablename__ = 'excel_rows'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sheet_id = db.Column(UUID(as_uuid=True), db.ForeignKey('excel_sheets.id'), nullable=False)
    row_index = db.Column(db.Integer, nullable=False)
    data = db.Column(db.JSON)  # Store row data as JSON
    
    # Relationships
    cell_labels = db.relationship('CellLabel', backref='row', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'row_index': self.row_index,
            'data': self.data,
            'labels_count': self.cell_labels.count()
        }

class Label(db.Model):
    __tablename__ = 'labels'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#1976d2')  # Hex color
    categories = db.Column(ARRAY(db.String), default=[])
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cell_labels = db.relationship('CellLabel', backref='label', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or '',
            'color': self.color,
            'categories': self.categories or [],
            'created_at': self.created_at.isoformat(),
            'usage_count': self.cell_labels.count()
        }

class CellLabel(db.Model):
    __tablename__ = 'cell_labels'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    row_id = db.Column(UUID(as_uuid=True), db.ForeignKey('excel_rows.id'), nullable=False)
    label_id = db.Column(db.Integer, db.ForeignKey('labels.id'), nullable=False)
    column_index = db.Column(db.Integer)  # Specific column in the row
    cell_value = db.Column(db.Text)  # The actual cell content that was labeled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    
    # Relationships
    creator = db.relationship('User', backref='created_labels')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'row_id': str(self.row_id),
            'label_id': self.label_id,
            'label_name': self.label.name,
            'label_color': self.label.color,
            'column_index': self.column_index,
            'cell_value': self.cell_value,
            'created_at': self.created_at.isoformat(),
            'created_by': self.creator.username if self.creator else None
        }

# Database indexes for performance
db.Index('idx_users_username', User.username)
db.Index('idx_users_email', User.email)
db.Index('idx_projects_owner', Project.owner_id)
db.Index('idx_files_project', File.project_id)
db.Index('idx_excel_sheets_file', ExcelSheet.file_id)
db.Index('idx_excel_rows_sheet', ExcelRow.sheet_id)
db.Index('idx_excel_columns_sheet', ExcelColumn.sheet_id)
db.Index('idx_labels_project', Label.project_id)
db.Index('idx_cell_labels_row', CellLabel.row_id)
db.Index('idx_cell_labels_label', CellLabel.label_id)

class MLAnalysis(db.Model):
    __tablename__ = 'ml_analyses'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    file_id = db.Column(UUID(as_uuid=True), db.ForeignKey('files.id'), nullable=False)
    sheet_id = db.Column(UUID(as_uuid=True), db.ForeignKey('excel_sheets.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Analysis configuration
    ml_provider = db.Column(db.String(50), nullable=False)  # 'openrouter' or 'ollama'
    ml_model = db.Column(db.String(100), nullable=False)
    analysis_type = db.Column(db.String(50), nullable=False)  # 'auto_labeling', 'column_detection', 'sentiment'
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, error
    
    # Results
    results = db.Column(db.JSON)  # Store analysis results
    error_message = db.Column(db.Text)
    processing_time = db.Column(db.Float)  # Processing time in seconds
    
    # Relationships
    project = db.relationship('Project', backref='ml_analyses')
    file = db.relationship('File', backref='ml_analyses')
    sheet = db.relationship('ExcelSheet', backref='ml_analyses')
    column_analyses = db.relationship('ColumnAnalysis', backref='ml_analysis', lazy='dynamic', cascade='all, delete-orphan')
    auto_labels = db.relationship('AutoLabel', backref='ml_analysis', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'project_id': str(self.project_id),
            'file_id': str(self.file_id),
            'sheet_id': str(self.sheet_id),
            'ml_provider': self.ml_provider,
            'ml_model': self.ml_model,
            'analysis_type': self.analysis_type,
            'status': self.status,
            'results': self.results,
            'error_message': self.error_message,
            'processing_time': self.processing_time,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ColumnAnalysis(db.Model):
    __tablename__ = 'column_analyses'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ml_analysis_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ml_analyses.id'), nullable=False)
    column_id = db.Column(UUID(as_uuid=True), db.ForeignKey('excel_columns.id'), nullable=False)
    
    # Column type detection
    detected_type = db.Column(db.String(50))  # 'timestamp', 'date', 'time', 'short_text', 'long_text', 'names', 'open_question'
    confidence_score = db.Column(db.Float)  # 0.0 to 1.0
    
    # Statistical analysis
    unique_values_count = db.Column(db.Integer)
    null_values_count = db.Column(db.Integer)
    avg_text_length = db.Column(db.Float)
    text_variability = db.Column(db.Float)  # Measure of text diversity
    
    # Open question analysis
    is_open_question = db.Column(db.Boolean, default=False)
    question_complexity = db.Column(db.String(20))  # 'simple', 'medium', 'complex'
    
    # Relationships
    column = db.relationship('ExcelColumn', backref='analyses')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'ml_analysis_id': str(self.ml_analysis_id),
            'column_id': str(self.column_id),
            'column_name': self.column.name,
            'column_index': self.column.column_index,
            'detected_type': self.detected_type,
            'confidence_score': self.confidence_score,
            'unique_values_count': self.unique_values_count,
            'null_values_count': self.null_values_count,
            'avg_text_length': self.avg_text_length,
            'text_variability': self.text_variability,
            'is_open_question': self.is_open_question,
            'question_complexity': self.question_complexity
        }

class AutoLabel(db.Model):
    __tablename__ = 'auto_labels'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ml_analysis_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ml_analyses.id'), nullable=False)
    column_analysis_id = db.Column(UUID(as_uuid=True), db.ForeignKey('column_analyses.id'), nullable=True)
    column_name = db.Column(db.String(255))  # Nome della colonna per etichettatura manuale
    
    # Generated label information
    label_name = db.Column(db.String(200), nullable=False)
    label_description = db.Column(db.Text)
    label_type = db.Column(db.String(50), default='auto')  # 'auto', 'manual'
    category = db.Column(db.String(100))
    theme = db.Column(db.String(100))
    
    # Clustering information
    cluster_id = db.Column(db.Integer)
    cluster_size = db.Column(db.Integer)
    representative_texts = db.Column(ARRAY(db.Text))  # Sample texts from this cluster
    
    # Sentiment analysis
    sentiment_label = db.Column(db.String(20))  # 'positive', 'negative', 'neutral'
    sentiment_score = db.Column(db.Float)  # -1.0 to 1.0
    emotion_tags = db.Column(ARRAY(db.String))  # ['joy', 'anger', 'fear', etc.]
    
    # Confidence and validation
    confidence_score = db.Column(db.Float)  # 0.0 to 1.0
    manual_validation = db.Column(db.String(20))  # 'pending', 'approved', 'rejected', 'modified'
    validated_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    validated_at = db.Column(db.DateTime)
    
    # Usage tracking
    applied_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    
    # Relationships
    column_analysis = db.relationship('ColumnAnalysis', backref='auto_labels')
    validator = db.relationship('User', foreign_keys=[validated_by], backref='validated_auto_labels')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_auto_labels')
    cell_applications = db.relationship('AutoLabelApplication', backref='auto_label', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'ml_analysis_id': str(self.ml_analysis_id),
            'column_analysis_id': str(self.column_analysis_id),
            'label_name': self.label_name,
            'label_description': self.label_description,
            'label_type': self.label_type,
            'column_name': self.column_name,
            'category': self.category,
            'theme': self.theme,
            'cluster_id': self.cluster_id,
            'cluster_size': self.cluster_size,
            'representative_texts': self.representative_texts or [],
            'sentiment_label': self.sentiment_label,
            'sentiment_score': self.sentiment_score,
            'emotion_tags': self.emotion_tags or [],
            'confidence_score': self.confidence_score,
            'manual_validation': self.manual_validation,
            'validated_by': str(self.validated_by) if self.validated_by else None,
            'validated_at': self.validated_at.isoformat() if self.validated_at else None,
            'applied_count': self.applied_count,
            'created_at': self.created_at.isoformat()
        }

class AutoLabelApplication(db.Model):
    __tablename__ = 'auto_label_applications'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auto_label_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auto_labels.id'), nullable=False)
    row_id = db.Column(UUID(as_uuid=True), db.ForeignKey('excel_rows.id'), nullable=True)  # Nullable per etichettatura manuale
    row_index = db.Column(db.Integer, nullable=False)  # Indice della riga
    column_name = db.Column(db.String(255), nullable=False)  # Nome della colonna
    
    # Application details
    cell_value = db.Column(db.Text)
    confidence_score = db.Column(db.Float)  # Confidence for this specific application
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    applied_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))  # User who approved the application
    
    # Status tracking
    status = db.Column(db.String(20), default='suggested')  # 'suggested', 'applied', 'rejected'
    
    # Relationships
    row = db.relationship('ExcelRow', backref='auto_label_applications')
    applier = db.relationship('User', backref='applied_auto_labels')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'auto_label_id': str(self.auto_label_id),
            'row_id': str(self.row_id) if self.row_id else None,
            'row_index': self.row_index,
            'column_name': self.column_name,
            'cell_value': self.cell_value,
            'confidence_score': self.confidence_score,
            'applied_at': self.applied_at.isoformat(),
            'applied_by': str(self.applied_by) if self.applied_by else None,
            'status': self.status,
            'auto_label': self.auto_label.to_dict() if self.auto_label else None
        }

class MLConfiguration(db.Model):
    __tablename__ = 'ml_configurations'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Configuration settings
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # ML Provider settings
    ml_provider = db.Column(db.String(50), nullable=False)
    ml_model = db.Column(db.String(100), nullable=False)
    api_key_encrypted = db.Column(db.Text)  # Encrypted API key
    api_url = db.Column(db.String(500))
    
    # Analysis settings
    auto_detect_columns = db.Column(db.Boolean, default=True)
    min_unique_values = db.Column(db.Integer, default=3)
    max_text_length = db.Column(db.Integer, default=1000)
    clustering_min_samples = db.Column(db.Integer, default=5)
    sentiment_analysis_enabled = db.Column(db.Boolean, default=True)
    
    # Column type preferences
    preferred_open_question_threshold = db.Column(db.Float, default=0.7)
    text_variability_threshold = db.Column(db.Float, default=0.5)
    
    # Active configuration flag
    is_active = db.Column(db.Boolean, default=False)
    
    # Relationships
    project = db.relationship('Project', backref='ml_configurations')
    creator = db.relationship('User', backref='created_ml_configurations')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'project_id': str(self.project_id),
            'created_by': str(self.created_by),
            'name': self.name,
            'description': self.description,
            'ml_provider': self.ml_provider,
            'ml_model': self.ml_model,
            'api_url': self.api_url,
            'auto_detect_columns': self.auto_detect_columns,
            'min_unique_values': self.min_unique_values,
            'max_text_length': self.max_text_length,
            'clustering_min_samples': self.clustering_min_samples,
            'sentiment_analysis_enabled': self.sentiment_analysis_enabled,
            'preferred_open_question_threshold': self.preferred_open_question_threshold,
            'text_variability_threshold': self.text_variability_threshold,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Additional indexes for ML tables
db.Index('idx_ml_analyses_project', MLAnalysis.project_id)
db.Index('idx_ml_analyses_file', MLAnalysis.file_id)
db.Index('idx_ml_analyses_sheet', MLAnalysis.sheet_id)
db.Index('idx_column_analyses_ml_analysis', ColumnAnalysis.ml_analysis_id)
db.Index('idx_column_analyses_column', ColumnAnalysis.column_id)
db.Index('idx_auto_labels_ml_analysis', AutoLabel.ml_analysis_id)
db.Index('idx_auto_labels_column_analysis', AutoLabel.column_analysis_id)
db.Index('idx_auto_label_applications_auto_label', AutoLabelApplication.auto_label_id)
db.Index('idx_auto_label_applications_row', AutoLabelApplication.row_id)
db.Index('idx_ml_configurations_project', MLConfiguration.project_id)