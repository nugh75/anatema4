from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.database import db
from app.models import User
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    return len(password) >= 6

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        if request.is_json:
            # API request
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '')
        else:
            # Form request
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
        
        if not username or not password:
            if request.is_json:
                return jsonify({'error': 'Username e password sono richiesti'}), 400
            flash('Username e password sono richiesti', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.check_password(password) and user.is_active:
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            if request.is_json:
                access_token = create_access_token(identity=str(user.id))
                refresh_token = create_refresh_token(identity=str(user.id))
                return jsonify({
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': user.to_dict()
                })
            else:
                login_user(user, remember=True)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            if request.is_json:
                return jsonify({'error': 'Credenziali non valide'}), 401
            flash('Credenziali non valide', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
        else:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username deve essere di almeno 3 caratteri')
        
        if not email or not validate_email(email):
            errors.append('Email non valida')
        
        if not password or not validate_password(password):
            errors.append('Password deve essere di almeno 6 caratteri')
        
        if password != confirm_password:
            errors.append('Le password non coincidono')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            errors.append('Username già esistente')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email già registrata')
        
        if errors:
            if request.is_json:
                return jsonify({'errors': errors}), 400
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            role='user'
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        if request.is_json:
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            return jsonify({
                'message': 'Registrazione completata con successo',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }), 201
        else:
            login_user(user, remember=True)
            flash('Registrazione completata con successo!', 'success')
            return redirect(url_for('main.dashboard'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout effettuato con successo', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/profile', methods=['POST'])
@login_required
def update_profile():
    if request.is_json:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
    else:
        email = request.form.get('email', '').strip().lower()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
    
    errors = []
    
    # Validate email
    if email and email != current_user.email:
        if not validate_email(email):
            errors.append('Email non valida')
        elif User.query.filter_by(email=email).first():
            errors.append('Email già utilizzata da un altro utente')
        else:
            current_user.email = email
    
    # Change password if provided
    if new_password:
        if not current_password:
            errors.append('Password attuale richiesta per cambiarla')
        elif not current_user.check_password(current_password):
            errors.append('Password attuale non corretta')
        elif not validate_password(new_password):
            errors.append('Nuova password deve essere di almeno 6 caratteri')
        else:
            current_user.set_password(new_password)
    
    if errors:
        if request.is_json:
            return jsonify({'errors': errors}), 400
        for error in errors:
            flash(error, 'error')
        return render_template('auth/profile.html', user=current_user)
    
    db.session.commit()
    
    if request.is_json:
        return jsonify({
            'message': 'Profilo aggiornato con successo',
            'user': current_user.to_dict()
        })
    else:
        flash('Profilo aggiornato con successo', 'success')
        return redirect(url_for('auth.profile'))

# API endpoints for JWT authentication
@auth_bp.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': new_token})

@auth_bp.route('/api/me')
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user:
        return jsonify({'user': user.to_dict()})
    return jsonify({'error': 'User not found'}), 404