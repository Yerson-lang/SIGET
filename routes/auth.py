from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models.models import User, db
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validar fortaleza de contraseña"""
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una mayúscula"
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una minúscula"
    if not re.search(r'[0-9]', password):
        return False, "La contraseña debe contener al menos un número"
    return True, "Contraseña válida"

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Vista de login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.main'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not username_or_email or not password:
            flash('Por favor completa todos los campos', 'error')
            return render_template('login.html')
        
        # Buscar usuario por username o email
        user = None
        if '@' in username_or_email:
            user = User.get_by_email(username_or_email)
        else:
            user = User.get_by_username(username_or_email)
        
        if user and user.check_password(password):
            if not user.active:
                flash('Tu cuenta ha sido desactivada. Contacta al administrador.', 'error')
                return render_template('login.html')
            
            login_user(user, remember=remember)
            user.update_last_login()
            
            # Redirigir a la página que intentaba acceder o al dashboard
            next_page = request.args.get('next')
            if next_page and not next_page.startswith('http'):
                return redirect(next_page)
            
            flash(f'¡Bienvenido {user.username}!', 'success')
            return redirect(url_for('dashboard.main'))
        else:
            flash('Usuario/Email o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Vista de registro"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.main'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validaciones
        errors = []
        
        if not username or not email or not password:
            errors.append('Todos los campos son obligatorios')
        
        if len(username) < 3:
            errors.append('El nombre de usuario debe tener al menos 3 caracteres')
        
        if not validate_email(email):
            errors.append('Email inválido')
        
        if password != confirm_password:
            errors.append('Las contraseñas no coinciden')
        
        valid_password, password_msg = validate_password(password)
        if not valid_password:
            errors.append(password_msg)
        
        # Verificar si el usuario ya existe
        if User.get_by_username(username):
            errors.append('El nombre de usuario ya está en uso')
        
        if User.get_by_email(email):
            errors.append('El email ya está registrado')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html', 
                                 username=username, 
                                 email=email)
        
        # Crear usuario
        try:
            user = User.create(username, email, password)
            db.session.commit()
            login_user(user)
            flash('¡Registro exitoso! Bienvenido a S.IG-ED', 'success')
            return redirect(url_for('dashboard.main'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear el usuario. Intenta nuevamente.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Ver perfil de usuario"""
    return render_template('profile.html', user=current_user)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Editar perfil de usuario"""
    if request.method == 'POST':
        # Aquí iría la lógica para actualizar el perfil
        flash('Perfil actualizado exitosamente', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('edit_profile.html', user=current_user)

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Recuperar contraseña"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.main'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not validate_email(email):
            flash('Email inválido', 'error')
            return render_template('forgot_password.html')
        
        user = User.get_by_email(email)
        if user:
            # Aquí iría la lógica para enviar email de recuperación
            flash('Se ha enviado un email con instrucciones para recuperar tu contraseña', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('No existe una cuenta con ese email', 'error')
    
    return render_template('forgot_password.html')