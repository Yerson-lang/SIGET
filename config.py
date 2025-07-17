import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-please-change-in-production'
    
    # MongoDB
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/siged_db'
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Google Maps
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY') or ''
    
    # Email (para notificaciones)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@siged.com'
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # API Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    
    # Logging
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'False') == 'True'
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Babel (i18n)
    BABEL_DEFAULT_LOCALE = 'es'
    BABEL_DEFAULT_TIMEZONE = 'America/Lima'
    
    # Cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    @staticmethod
    def init_app(app):
        """Inicializar la aplicación con configuración específica"""
        # Crear directorio de uploads si no existe
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Configurar logging
        if not app.debug and not app.testing:
            import logging
            from logging.handlers import RotatingFileHandler
            
            if Config.LOG_TO_STDOUT:
                stream_handler = logging.StreamHandler()
                stream_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
                app.logger.addHandler(stream_handler)
            else:
                if not os.path.exists('logs'):
                    os.mkdir('logs')
                file_handler = RotatingFileHandler('logs/siged.log',
                                                 maxBytes=10240000, backupCount=10)
                file_handler.setFormatter(logging.Formatter(
                    '%(asctime)s %(levelname)s: %(message)s '
                    '[in %(pathname)s:%(lineno)d]'))
                file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
                app.logger.addHandler(file_handler)
            
            app.logger.setLevel(getattr(logging, Config.LOG_LEVEL))
            app.logger.info('S.IG-ED startup')


class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True
    TESTING = False
    WTF_CSRF_ENABLED = False  # Desactivar CSRF para desarrollo
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Instalar extensiones de debug
        try:
            from flask_debugtoolbar import DebugToolbarExtension
            toolbar = DebugToolbarExtension(app)
        except ImportError:
            pass


class TestingConfig(Config):
    """Configuración de pruebas"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    MONGO_URI = 'mongodb://localhost:27017/siged_test_db'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False
    TESTING = False
    
    # Usar variables de entorno en producción
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY debe estar configurado en producción")
    
    # SSL
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Configurar para proxy reverso (nginx)
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
        
        # Enviar errores por email
        if app.config['MAIL_USERNAME']:
            import logging
            from logging.handlers import SMTPHandler
            
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=app.config['MAIL_DEFAULT_SENDER'],
                toaddrs=['admin@siged.com'],
                subject='S.IG-ED Error',
                credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']),
                secure=() if app.config['MAIL_USE_TLS'] else None
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)


# Configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Ejemplo de archivo .env
"""
# .env file
SECRET_KEY=your-super-secret-key-here
MONGO_URI=mongodb://localhost:27017/siged_db
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
FLASK_ENV=development
"""