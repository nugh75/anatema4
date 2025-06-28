"""
Modelli per il sistema di etichettatura separato dal ML
Sistema a due fasi: generazione etichette AI -> approvazione umana -> applicazione
"""

from app.database import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON

class LabelTemplate(db.Model):
    """Template di prompt per la generazione di etichette AI"""
    __tablename__ = 'label_templates'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Template information
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # 'sentiment', 'emotion', 'behavior', 'topic', 'intent', 'custom'
    
    # Prompt configuration
    system_prompt = db.Column(db.Text, nullable=False)
    user_prompt_template = db.Column(db.Text, nullable=False)
    
    # AI Model settings
    preferred_model = db.Column(db.String(100))  # Modello AI preferito per questo template
    temperature = db.Column(db.Float, default=0.7)
    max_tokens = db.Column(db.Integer, default=1000)
    
    # Template settings
    expected_labels_count = db.Column(db.Integer, default=5)  # Numero atteso di etichette generate
    output_format = db.Column(db.String(50), default='json')  # 'json', 'list', 'structured'
    
    # Usage tracking
    is_active = db.Column(db.Boolean, default=True)
    usage_count = db.Column(db.Integer, default=0)
    
    # Relationships
    project = db.relationship('Project', backref='label_templates')
    creator = db.relationship('User', backref='created_label_templates')
    label_generations = db.relationship('LabelGeneration', backref='template', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'project_id': str(self.project_id),
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'system_prompt': self.system_prompt,
            'user_prompt_template': self.user_prompt_template,
            'preferred_model': self.preferred_model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'expected_labels_count': self.expected_labels_count,
            'output_format': self.output_format,
            'is_active': self.is_active,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class LabelGeneration(db.Model):
    """Sessione di generazione etichette AI"""
    __tablename__ = 'label_generations'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    sheet_id = db.Column(UUID(as_uuid=True), db.ForeignKey('excel_sheets.id'), nullable=False)
    template_id = db.Column(UUID(as_uuid=True), db.ForeignKey('label_templates.id'), nullable=False)
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Generation details
    column_name = db.Column(db.String(255), nullable=False)
    sample_data = db.Column(JSON)  # Campione di dati analizzati
    
    # AI Response
    ai_provider = db.Column(db.String(50))
    ai_model = db.Column(db.String(100))
    raw_ai_response = db.Column(db.Text)
    processing_time = db.Column(db.Float)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'error'
    error_message = db.Column(db.Text)
    
    # Results summary
    total_suggestions = db.Column(db.Integer, default=0)
    approved_suggestions = db.Column(db.Integer, default=0)
    rejected_suggestions = db.Column(db.Integer, default=0)
    
    # Relationships
    project = db.relationship('Project', backref='label_generations')
    sheet = db.relationship('ExcelSheet', backref='label_generations')
    creator = db.relationship('User', backref='created_label_generations')
    suggestions = db.relationship('LabelSuggestion', backref='generation', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'project_id': str(self.project_id),
            'sheet_id': str(self.sheet_id),
            'template_id': str(self.template_id),
            'column_name': self.column_name,
            'sample_data': self.sample_data,
            'ai_provider': self.ai_provider,
            'ai_model': self.ai_model,
            'status': self.status,
            'error_message': self.error_message,
            'processing_time': self.processing_time,
            'total_suggestions': self.total_suggestions,
            'approved_suggestions': self.approved_suggestions,
            'rejected_suggestions': self.rejected_suggestions,
            'created_at': self.created_at.isoformat()
        }

class LabelSuggestion(db.Model):
    """Etichetta suggerita dall'AI in attesa di approvazione"""
    __tablename__ = 'label_suggestions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generation_id = db.Column(UUID(as_uuid=True), db.ForeignKey('label_generations.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Suggestion details
    suggested_name = db.Column(db.String(200), nullable=False)
    suggested_description = db.Column(db.Text)
    suggested_category = db.Column(db.String(100))
    suggested_color = db.Column(db.String(7), default='#1976d2')
    
    # AI confidence and reasoning
    ai_confidence = db.Column(db.Float)  # 0.0 to 1.0
    ai_reasoning = db.Column(db.Text)  # Spiegazione dell'AI per questa etichetta
    sample_values = db.Column(JSON)  # Valori di esempio che hanno portato a questa etichetta
    
    # Human review
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected', 'modified'
    reviewed_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    review_notes = db.Column(db.Text)
    
    # Final approved label (if modified)
    final_name = db.Column(db.String(200))
    final_description = db.Column(db.Text)
    final_category = db.Column(db.String(100))
    final_color = db.Column(db.String(7))
    
    # Link to created label
    created_label_id = db.Column(db.Integer, db.ForeignKey('labels.id'))
    
    # Relationships
    reviewer = db.relationship('User', backref='reviewed_label_suggestions')
    created_label = db.relationship('Label', backref='suggestion_source')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'generation_id': str(self.generation_id),
            'suggested_name': self.suggested_name,
            'suggested_description': self.suggested_description,
            'suggested_category': self.suggested_category,
            'suggested_color': self.suggested_color,
            'ai_confidence': self.ai_confidence,
            'ai_reasoning': self.ai_reasoning,
            'sample_values': self.sample_values,
            'status': self.status,
            'reviewed_by': str(self.reviewed_by) if self.reviewed_by else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'review_notes': self.review_notes,
            'final_name': self.final_name,
            'final_description': self.final_description,
            'final_category': self.final_category,
            'final_color': self.final_color,
            'created_label_id': self.created_label_id,
            'created_at': self.created_at.isoformat()
        }

class LabelApplication(db.Model):
    """Applicazione di etichette (manuale o AI) alle celle"""
    __tablename__ = 'label_applications'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    sheet_id = db.Column(UUID(as_uuid=True), db.ForeignKey('excel_sheets.id'), nullable=False)
    label_id = db.Column(db.Integer, db.ForeignKey('labels.id'), nullable=False)
    applied_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Cell location
    row_index = db.Column(db.Integer, nullable=False)
    column_name = db.Column(db.String(255), nullable=False)
    cell_value = db.Column(db.Text)
    
    # Application type and confidence
    application_type = db.Column(db.String(20), nullable=False)  # 'manual', 'ai_batch', 'ai_single'
    confidence_score = db.Column(db.Float)  # Per applicazioni AI
    
    # AI details (if AI-applied)
    ai_session_id = db.Column(UUID(as_uuid=True))  # Link a sessione di applicazione AI
    ai_reasoning = db.Column(db.Text)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)  # Per permettere "rimozione" logica
    
    # Relationships
    project = db.relationship('Project', backref='label_applications')
    sheet = db.relationship('ExcelSheet', backref='label_applications')
    label = db.relationship('Label', backref='applications')
    applier = db.relationship('User', backref='applied_label_applications')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'project_id': str(self.project_id),
            'sheet_id': str(self.sheet_id),
            'label_id': self.label_id,
            'label_name': self.label.name,
            'label_color': self.label.color,
            'row_index': self.row_index,
            'column_name': self.column_name,
            'cell_value': self.cell_value,
            'application_type': self.application_type,
            'confidence_score': self.confidence_score,
            'ai_session_id': str(self.ai_session_id) if self.ai_session_id else None,
            'ai_reasoning': self.ai_reasoning,
            'is_active': self.is_active,
            'applied_by': str(self.applied_by),
            'applied_at': self.applied_at.isoformat()
        }

class AILabelingSession(db.Model):
    """Sessione di etichettatura automatica AI (Fase 2)"""
    __tablename__ = 'ai_labeling_sessions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    sheet_id = db.Column(UUID(as_uuid=True), db.ForeignKey('excel_sheets.id'), nullable=False)
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Session configuration
    target_type = db.Column(db.String(20), nullable=False)  # 'column', 'row', 'range'
    target_name = db.Column(db.String(255))  # Nome colonna o indice riga
    available_labels = db.Column(JSON)  # Lista delle etichette disponibili per l'applicazione
    
    # AI Configuration
    ai_provider = db.Column(db.String(50))
    ai_model = db.Column(db.String(100))
    custom_prompt = db.Column(db.Text)  # Prompt personalizzato per questa sessione
    
    # Processing
    status = db.Column(db.String(20), default='pending')  # 'pending', 'processing', 'completed', 'error'
    error_message = db.Column(db.Text)
    processing_time = db.Column(db.Float)
    
    # Results
    total_cells_processed = db.Column(db.Integer, default=0)
    successful_applications = db.Column(db.Integer, default=0)
    failed_applications = db.Column(db.Integer, default=0)
    
    # Relationships
    project = db.relationship('Project', backref='ai_labeling_sessions')
    sheet = db.relationship('ExcelSheet', backref='ai_labeling_sessions')
    creator = db.relationship('User', backref='created_ai_labeling_sessions')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'project_id': str(self.project_id),
            'sheet_id': str(self.sheet_id),
            'target_type': self.target_type,
            'target_name': self.target_name,
            'available_labels': self.available_labels,
            'ai_provider': self.ai_provider,
            'ai_model': self.ai_model,
            'custom_prompt': self.custom_prompt,
            'status': self.status,
            'error_message': self.error_message,
            'processing_time': self.processing_time,
            'total_cells_processed': self.total_cells_processed,
            'successful_applications': self.successful_applications,
            'failed_applications': self.failed_applications,
            'created_at': self.created_at.isoformat()
        }

class LabelAnalytics(db.Model):
    """Analytics e statistiche per le etichette (cache delle metriche)"""
    __tablename__ = 'label_analytics'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    label_id = db.Column(db.Integer, db.ForeignKey('labels.id'), nullable=False)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Usage statistics
    total_applications = db.Column(db.Integer, default=0)
    manual_applications = db.Column(db.Integer, default=0)
    ai_applications = db.Column(db.Integer, default=0)
    
    # Distribution by sheet
    sheet_distribution = db.Column(JSON)  # {'sheet_id': count, ...}
    
    # Distribution by column
    column_distribution = db.Column(JSON)  # {'column_name': count, ...}
    
    # Temporal analysis
    first_used = db.Column(db.DateTime)
    last_used = db.Column(db.DateTime)
    usage_frequency = db.Column(db.Float)  # Utilizzi per giorno
    
    # Quality metrics
    avg_ai_confidence = db.Column(db.Float)
    human_override_rate = db.Column(db.Float)  # Percentuale di modifiche umane su suggerimenti AI
    
    # Relationships
    project = db.relationship('Project', backref='label_analytics')
    label = db.relationship('Label', backref='analytics')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'project_id': str(self.project_id),
            'label_id': self.label_id,
            'label_name': self.label.name,
            'total_applications': self.total_applications,
            'manual_applications': self.manual_applications,
            'ai_applications': self.ai_applications,
            'sheet_distribution': self.sheet_distribution,
            'column_distribution': self.column_distribution,
            'first_used': self.first_used.isoformat() if self.first_used else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'usage_frequency': self.usage_frequency,
            'avg_ai_confidence': self.avg_ai_confidence,
            'human_override_rate': self.human_override_rate,
            'calculated_at': self.calculated_at.isoformat()
        }

# Indexes for performance
db.Index('idx_label_templates_project', LabelTemplate.project_id)
db.Index('idx_label_generations_project', LabelGeneration.project_id)
db.Index('idx_label_generations_sheet', LabelGeneration.sheet_id)
db.Index('idx_label_suggestions_generation', LabelSuggestion.generation_id)
db.Index('idx_label_applications_project', LabelApplication.project_id)
db.Index('idx_label_applications_sheet', LabelApplication.sheet_id)
db.Index('idx_label_applications_label', LabelApplication.label_id)
db.Index('idx_ai_labeling_sessions_project', AILabelingSession.project_id)
db.Index('idx_label_analytics_project', LabelAnalytics.project_id)
db.Index('idx_label_analytics_label', LabelAnalytics.label_id)