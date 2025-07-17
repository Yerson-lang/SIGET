from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:@localhost/siged_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Importar db desde models
from models.models import db

# Inicializar extensiones
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'

# Importar modelos DESPUÉS de crear db
from models.models import User, Emergency, Report

# Configuración de usuario para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Importar blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.api import api_bp

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(api_bp, url_prefix='/api')

# Rutas principales
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.main'))
    return render_template('index.html')

@app.route('/map')
@login_required
def map_view():
    # Obtener emergencias activas
    emergencies = Emergency.query.filter_by(active=True).all()
    emergencies_data = []
    for e in emergencies:
        emergencies_data.append({
            '_id': e.id,
            'title': e.title,
            'description': e.description,
            'type': e.type,
            'status': e.status,
            'severity': e.severity,
            'location': {
                'lat': e.latitude,
                'lng': e.longitude,
                'address': e.address,
                'city': e.city
            },
            'affected_people': e.affected_people,
            'created_at': e.created_at
        })
    
    return render_template('map.html', 
                         emergencies=emergencies_data,
                         google_maps_key=os.getenv('GOOGLE_MAPS_API_KEY'))

@app.route('/reports')
@login_required
def reports():
    # Obtener reportes recientes
    reports = Report.query.order_by(Report.created_at.desc()).limit(20).all()
    reports_data = []
    for r in reports:
        reports_data.append({
            '_id': r.id,
            'title': r.title,
            'type': r.type,
            'content': r.content,
            'created_by': r.author.username if r.author else 'Usuario',
            'created_at': r.created_at,
            'views': r.views,
            'tags': r.tags.split(',') if r.tags else []
        })
    
    return render_template('reports.html', reports=reports_data)

# Manejadores de errores
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Contexto global para templates
@app.context_processor
def inject_globals():
    return {
        'app_name': 'S.IG-ED',
        'current_year': datetime.now().year,
        'datetime': datetime,  # Agregar datetime al contexto
        'brand_colors': {
            'primary': '#5B9A9C',
            'secondary': '#F5E6D3',
            'dark': '#2C3E50',
            'light': '#ECF0F1'
        }
    }

# Crear tablas al iniciar
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)