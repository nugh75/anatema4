#!/usr/bin/env python3
"""
Setup Script per Anatema
Script di configurazione automatica per l'applicazione
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import secrets
import string

class AnatemSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / 'venv'
        self.env_file = self.project_root / '.env'
        
    def print_status(self, message, status='info'):
        """Stampa messaggi di stato colorati"""
        colors = {
            'info': '\033[94m',
            'success': '\033[92m',
            'warning': '\033[93m',
            'error': '\033[91m',
            'end': '\033[0m'
        }
        
        icon = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        
        print(f"{colors.get(status, '')}{icon.get(status, '')} {message}{colors['end']}")
    
    def check_python_version(self):
        """Verifica la versione di Python"""
        self.print_status("Checking Python version...")
        
        if sys.version_info < (3, 8):
            self.print_status("Python 3.8+ is required", 'error')
            return False
        
        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.print_status(f"Python {version} detected", 'success')
        return True
    
    def check_dependencies(self):
        """Verifica le dipendenze di sistema"""
        self.print_status("Checking system dependencies...")
        
        # Verifica pip
        try:
            subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                         check=True, capture_output=True)
            self.print_status("pip is available", 'success')
        except subprocess.CalledProcessError:
            self.print_status("pip is not available", 'error')
            return False
        
        # Verifica venv
        try:
            subprocess.run([sys.executable, '-m', 'venv', '--help'], 
                         check=True, capture_output=True)
            self.print_status("venv module is available", 'success')
        except subprocess.CalledProcessError:
            self.print_status("venv module is not available", 'error')
            return False
        
        return True
    
    def create_virtual_environment(self):
        """Crea l'ambiente virtuale"""
        self.print_status("Creating virtual environment...")
        
        if self.venv_path.exists():
            self.print_status("Virtual environment already exists", 'warning')
            return True
        
        try:
            subprocess.run([sys.executable, '-m', 'venv', str(self.venv_path)], 
                         check=True)
            self.print_status("Virtual environment created", 'success')
            return True
        except subprocess.CalledProcessError as e:
            self.print_status(f"Failed to create virtual environment: {e}", 'error')
            return False
    
    def get_pip_command(self):
        """Ottiene il comando pip per l'ambiente virtuale"""
        if os.name == 'nt':  # Windows
            return str(self.venv_path / 'Scripts' / 'pip')
        else:  # Unix/Linux/macOS
            return str(self.venv_path / 'bin' / 'pip')
    
    def get_python_command(self):
        """Ottiene il comando python per l'ambiente virtuale"""
        if os.name == 'nt':  # Windows
            return str(self.venv_path / 'Scripts' / 'python')
        else:  # Unix/Linux/macOS
            return str(self.venv_path / 'bin' / 'python')
    
    def install_requirements(self):
        """Installa i requirements"""
        self.print_status("Installing Python packages...")
        
        pip_cmd = self.get_pip_command()
        requirements_file = self.project_root / 'requirements.txt'
        
        if not requirements_file.exists():
            self.print_status("requirements.txt not found", 'error')
            return False
        
        try:
            # Aggiorna pip
            subprocess.run([pip_cmd, 'install', '--upgrade', 'pip'], 
                         check=True, capture_output=True)
            
            # Installa requirements
            subprocess.run([pip_cmd, 'install', '-r', str(requirements_file)], 
                         check=True)
            self.print_status("Python packages installed", 'success')
            return True
        except subprocess.CalledProcessError as e:
            self.print_status(f"Failed to install packages: {e}", 'error')
            return False
    
    def generate_secret_key(self):
        """Genera una chiave segreta"""
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def create_env_file(self):
        """Crea il file .env"""
        self.print_status("Creating environment configuration...")
        
        if self.env_file.exists():
            self.print_status(".env file already exists", 'warning')
            return True
        
        secret_key = self.generate_secret_key()
        jwt_secret = self.generate_secret_key()
        
        env_content = f"""# Anatema Configuration
# Environment
FLASK_ENV=development
FLASK_DEBUG=True

# Security
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret}

# Database
DATABASE_URL=sqlite:///anatema.db

# Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Mail Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Admin Configuration
ADMIN_EMAIL=admin@anatema.com
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
"""
        
        try:
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            self.print_status("Environment file created", 'success')
            return True
        except Exception as e:
            self.print_status(f"Failed to create .env file: {e}", 'error')
            return False
    
    def create_directories(self):
        """Crea le directory necessarie"""
        self.print_status("Creating necessary directories...")
        
        directories = [
            'uploads',
            'uploads/excel',
            'uploads/temp',
            'logs',
            'instance'
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.print_status("Directories created", 'success')
        return True
    
    def initialize_database(self):
        """Inizializza il database"""
        self.print_status("Initializing database...")
        
        python_cmd = self.get_python_command()
        
        try:
            # Inizializza il database
            subprocess.run([python_cmd, 'run.py', 'init-db'], 
                         check=True, cwd=str(self.project_root))
            self.print_status("Database initialized", 'success')
            return True
        except subprocess.CalledProcessError as e:
            self.print_status(f"Failed to initialize database: {e}", 'error')
            return False
    
    def create_admin_user(self):
        """Crea l'utente amministratore"""
        self.print_status("Creating admin user...")
        
        python_cmd = self.get_python_command()
        
        try:
            subprocess.run([python_cmd, 'run.py', 'create-admin'], 
                         check=True, cwd=str(self.project_root))
            self.print_status("Admin user created", 'success')
            return True
        except subprocess.CalledProcessError as e:
            self.print_status(f"Failed to create admin user: {e}", 'warning')
            return True  # Non è critico se fallisce
    
    def run_tests(self):
        """Esegue i test di base"""
        self.print_status("Running basic tests...")
        
        python_cmd = self.get_python_command()
        test_file = self.project_root / 'test_app.py'
        
        if not test_file.exists():
            self.print_status("Test file not found, skipping tests", 'warning')
            return True
        
        try:
            # Avvia il server in background per i test
            self.print_status("Starting test server...")
            server_process = subprocess.Popen(
                [python_cmd, 'run.py'],
                cwd=str(self.project_root),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Aspetta che il server si avvii
            import time
            time.sleep(3)
            
            # Esegui i test
            result = subprocess.run([python_cmd, str(test_file)], 
                                  cwd=str(self.project_root),
                                  capture_output=True, text=True)
            
            # Termina il server
            server_process.terminate()
            server_process.wait()
            
            if result.returncode == 0:
                self.print_status("Basic tests passed", 'success')
                return True
            else:
                self.print_status("Some tests failed", 'warning')
                return True  # Non è critico
                
        except Exception as e:
            self.print_status(f"Test execution failed: {e}", 'warning')
            return True  # Non è critico
    
    def print_completion_info(self):
        """Stampa le informazioni di completamento"""
        print("\n" + "=" * 60)
        self.print_status("🎉 Anatema setup completed successfully!", 'success')
        print("=" * 60)
        
        print("\n📋 Next steps:")
        print("1. Activate the virtual environment:")
        if os.name == 'nt':
            print("   .\\venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        
        print("\n2. Start the application:")
        print("   python run.py")
        print("   # or")
        print("   flask run")
        
        print("\n3. Open your browser and go to:")
        print("   http://127.0.0.1:5000")
        
        print("\n4. Login with admin credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        
        print("\n📁 Important files:")
        print("   .env          - Environment configuration")
        print("   anatema.db    - SQLite database")
        print("   uploads/      - File upload directory")
        print("   logs/         - Application logs")
        
        print("\n🔧 Useful commands:")
        print("   python run.py init-db      - Reinitialize database")
        print("   python run.py create-admin - Create admin user")
        print("   python test_app.py         - Run application tests")
        
        print("\n📖 Documentation:")
        print("   README.md     - Complete project documentation")
        
    def setup(self):
        """Esegue il setup completo"""
        print("🚀 Anatema Setup Script")
        print("=" * 60)
        
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Checking dependencies", self.check_dependencies),
            ("Creating virtual environment", self.create_virtual_environment),
            ("Installing requirements", self.install_requirements),
            ("Creating environment file", self.create_env_file),
            ("Creating directories", self.create_directories),
            ("Initializing database", self.initialize_database),
            ("Creating admin user", self.create_admin_user),
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                self.print_status(f"Setup failed at: {step_name}", 'error')
                return False
        
        # Test opzionali
        print(f"\n📋 Running tests...")
        self.run_tests()
        
        self.print_completion_info()
        return True

def main():
    """Funzione principale"""
    setup = AnatemSetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Anatema Setup Script")
        print("Usage: python setup.py")
        print("\nThis script will:")
        print("- Check Python version and dependencies")
        print("- Create virtual environment")
        print("- Install Python packages")
        print("- Create configuration files")
        print("- Initialize database")
        print("- Create admin user")
        print("- Run basic tests")
        return
    
    try:
        success = setup.setup()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()