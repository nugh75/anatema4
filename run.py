from app import create_app
from app.database import db
from app.models import User, Project, File, ExcelSheet, ExcelColumn, ExcelRow, Label, CellLabel
import os

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Project': Project,
        'File': File,
        'ExcelSheet': ExcelSheet,
        'ExcelColumn': ExcelColumn,
        'ExcelRow': ExcelRow,
        'Label': Label,
        'CellLabel': CellLabel
    }

@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized!')

@app.cli.command()
def create_admin():
    """Create admin user."""
    from werkzeug.security import generate_password_hash
    
    admin = User(
        username='admin',
        email='admin@anatema.com',
        role='admin'
    )
    admin.set_password('admin123')
    
    db.session.add(admin)
    db.session.commit()
    print('Admin user created!')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)