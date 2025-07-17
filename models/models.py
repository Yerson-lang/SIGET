from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Modelo de Usuario"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # user, operator, admin
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Perfil adicional
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    organization = db.Column(db.String(100))
    avatar = db.Column(db.String(200))
    
    # Relaciones
    emergencies = db.relationship('Emergency', backref='reporter', lazy='dynamic', foreign_keys='Emergency.reported_by')
    reports = db.relationship('Report', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        """Establecer contraseña encriptada"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Actualizar último login"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def is_admin(self):
        """Verificar si es administrador"""
        return self.role == 'admin'
    
    def is_operator(self):
        """Verificar si es operador"""
        return self.role in ['admin', 'operator']
    
    @staticmethod
    def create(username, email, password, role='user'):
        """Crear nuevo usuario"""
        user = User(
            username=username,
            email=email,
            role=role,
            active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_by_username(username):
        """Obtener usuario por nombre de usuario"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_by_email(email):
        """Obtener usuario por email"""
        return User.query.filter_by(email=email).first()


class Emergency(db.Model):
    """Modelo de Emergencia"""
    __tablename__ = 'emergencies'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), default='other')  # fire, flood, earthquake, etc.
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Ubicación
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    region = db.Column(db.String(100))
    
    # Estado y severidad
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    status = db.Column(db.String(20), default='reported')  # reported, confirmed, responding, resolved
    active = db.Column(db.Boolean, default=True)
    
    # Información adicional
    affected_people = db.Column(db.Integer, default=0)
    resources_needed = db.Column(db.Text)  # JSON string
    
    # Relaciones y timestamps
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Relaciones
    updates = db.relationship('EmergencyUpdate', backref='emergency', lazy='dynamic', cascade='all, delete-orphan')
    
    TYPES = {
        'fire': {'name': 'Incendio', 'icon': '🔥', 'color': '#E74C3C'},
        'flood': {'name': 'Inundación', 'icon': '🌊', 'color': '#3498DB'},
        'earthquake': {'name': 'Terremoto', 'icon': '🏚️', 'color': '#8B4513'},
        'storm': {'name': 'Tormenta', 'icon': '⛈️', 'color': '#7F8C8D'},
        'accident': {'name': 'Accidente', 'icon': '🚨', 'color': '#E67E22'},
        'medical': {'name': 'Emergencia Médica', 'icon': '🏥', 'color': '#27AE60'},
        'other': {'name': 'Otro', 'icon': '⚠️', 'color': '#95A5A6'}
    }
    
    @staticmethod
    def create(data):
        """Crear nueva emergencia"""
        emergency = Emergency(
            type=data.get('type', 'other'),
            title=data['title'],
            description=data['description'],
            latitude=float(data['lat']),
            longitude=float(data['lng']),
            address=data.get('address', ''),
            city=data.get('city', ''),
            region=data.get('region', ''),
            severity=data.get('severity', 'medium'),
            reported_by=data.get('reported_by'),
            affected_people=data.get('affected_people', 0)
        )
        db.session.add(emergency)
        db.session.commit()
        return emergency.id
    
    def update_status(self, status, user_id=None):
        """Actualizar estado de emergencia"""
        self.status = status
        self.updated_at = datetime.utcnow()
        
        if status == 'resolved':
            self.active = False
            self.resolved_at = datetime.utcnow()
        
        # Agregar actualización al historial
        update = EmergencyUpdate(
            emergency_id=self.id,
            user_id=user_id,
            action=f'Status changed to {status}',
            timestamp=datetime.utcnow()
        )
        db.session.add(update)
        db.session.commit()


class EmergencyUpdate(db.Model):
    """Modelo de Actualizaciones de Emergencia"""
    __tablename__ = 'emergency_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    emergency_id = db.Column(db.Integer, db.ForeignKey('emergencies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(200))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='emergency_updates')


class Report(db.Model):
    """Modelo de Reporte"""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    emergency_id = db.Column(db.Integer, db.ForeignKey('emergencies.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    visibility = db.Column(db.String(20), default='public')  # public, private, restricted
    tags = db.Column(db.String(500))  # Comma-separated tags
    views = db.Column(db.Integer, default=0)
    
    # Relaciones
    emergency = db.relationship('Emergency', backref='reports')
    
    @staticmethod
    def create(data):
        """Crear nuevo reporte"""
        report = Report(
            title=data['title'],
            type=data['type'],
            content=data['content'],
            emergency_id=data.get('emergency_id'),
            created_by=data['created_by'],
            status='published',
            visibility=data.get('visibility', 'public'),
            tags=','.join(data.get('tags', []))
        )
        db.session.add(report)
        db.session.commit()
        return report.id
    
    def increment_views(self):
        """Incrementar vistas del reporte"""
        self.views += 1
        db.session.commit()