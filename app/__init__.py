from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config.config import config
from app.database import db
import os
import json

# Initialize extensions
migrate = Migrate()
login_manager = LoginManager()
jwt = JWTManager()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Per favore effettua il login per accedere a questa pagina.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(user_id)
    
    # Register blueprints
    from app.views.auth import auth_bp
    from app.views.main import main_bp
    from app.views.projects import projects_bp
    from app.views.files import files_bp
    from app.views.labels import labels_bp
    from app.views.api import api_bp
    from app.views.ml import ml_bp  # Keep original name for compatibility
    from app.views.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(files_bp, url_prefix='/files')
    app.register_blueprint(labels_bp, url_prefix='/labels')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(ml_bp, url_prefix='/ml')  # Keep /ml URL prefix
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Add custom Jinja2 filters
    @app.template_filter('tojsonfilter')
    def to_json_filter(obj):
        """Convert Python object to JSON string for use in templates"""
        try:
            return json.dumps(obj, ensure_ascii=False, default=str)
        except (TypeError, ValueError):
            return '{}'
    
    # Create upload directory
    upload_dir = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    return app