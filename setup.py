#!/usr/bin/env python
"""
Script de configuración inicial para S.IG-ED
Crea la estructura de carpetas necesaria y archivos base
"""

import os
import shutil
import sys

def create_project_structure():
    """Crear estructura de carpetas del proyecto"""
    
    print("🚀 Configurando proyecto S.IG-ED...\n")
    
    # Definir estructura de carpetas
    folders = [
        'static',
        'static/css',
        'static/js',
        'static/img',
        'templates',
        'templates/errors',
        'models',
        'routes',
        'utils',
        'uploads',
        'logs'
    ]
    
    # Crear carpetas
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✓ Creada carpeta: {folder}")
    
    # Crear archivos __init__.py
    init_files = [
        'models/__init__.py',
        'routes/__init__.py',
        'utils/__init__.py'
    ]
    
    for init_file in init_files:
        with open(init_file, 'w') as f:
            f.write('# -*- coding: utf-8 -*-\n')
        print(f"✓ Creado archivo: {init_file}")
    
    # Crear archivo .env si no existe
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✓ Creado archivo .env desde .env.example")
            print("⚠️  IMPORTANTE: Edita el archivo .env con tus configuraciones")
        else:
            with open('.env', 'w') as f:
                f.write("""# Configuración de Flask
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-cambiar-en-produccion

# MongoDB
MONGO_URI=mongodb://localhost:27017/siged_db

# Google Maps API
GOOGLE_MAPS_API_KEY=

# Email (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=
MAIL_PASSWORD=
""")
            print("✓ Creado archivo .env básico")
            print("⚠️  IMPORTANTE: Agrega tu Google Maps API Key en .env")
    
    # Crear .gitignore si no existe
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Flask
instance/
.webassets-cache

# Environment
.env
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# Database
*.db
*.sqlite

# OS
.DS_Store
Thumbs.db

# Uploads
uploads/*
!uploads/.gitkeep

# Coverage
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover

# Pytest
.pytest_cache/
""")
        print("✓ Creado archivo .gitignore")
    
    # Crear archivo para mantener carpeta uploads en git
    with open('uploads/.gitkeep', 'w') as f:
        f.write('')
    
    # Verificar archivos esenciales
    essential_files = {
        'app.py': '❌ Falta el archivo principal app.py',
        'config.py': '❌ Falta el archivo config.py',
        'requirements.txt': '❌ Falta el archivo requirements.txt',
        'models/models.py': '❌ Falta el archivo models/models.py',
        'routes/auth.py': '❌ Falta el archivo routes/auth.py',
        'routes/dashboard.py': '❌ Falta el archivo routes/dashboard.py',
        'routes/api.py': '❌ Falta el archivo routes/api.py',
        'utils/decorators.py': '❌ Falta el archivo utils/decorators.py',
        'templates/base.html': '❌ Falta el template base.html',
        'templates/login.html': '❌ Falta el template login.html',
        'templates/register.html': '❌ Falta el template register.html',
        'templates/dashboard.html': '❌ Falta el template dashboard.html',
        'templates/map.html': '❌ Falta el template map.html',
        'templates/reports.html': '❌ Falta el template reports.html',
        'templates/index.html': '❌ Falta el template index.html',
        'templates/errors/404.html': '❌ Falta el template 404.html',
        'templates/errors/500.html': '❌ Falta el template 500.html',
        'static/css/style.css': '❌ Falta el archivo style.css',
        'static/js/main.js': '❌ Falta el archivo main.js'
    }
    
    print("\n📋 Verificando archivos esenciales:")
    all_files_ok = True
    for file_path, error_msg in essential_files.items():
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(error_msg)
            all_files_ok = False
    
    print("\n✅ Estructura del proyecto creada exitosamente!")
    
    if not all_files_ok:
        print("\n⚠️  ADVERTENCIA: Faltan algunos archivos esenciales.")
        print("   Asegúrate de tener todos los archivos del proyecto.")
    
    print("\n📋 Próximos pasos:")
    print("1. Instala las dependencias: pip install -r requirements.txt")
    print("2. Configura MongoDB (asegúrate de que esté corriendo)")
    print("3. Edita el archivo .env con tu Google Maps API Key")
    print("4. Ejecuta la aplicación: python app.py")
    print("\n🔑 Para crear un usuario administrador, ejecuta:")
    print("   python create_admin.py")

def check_dependencies():
    """Verificar dependencias del sistema"""
    print("\n🔍 Verificando dependencias...")
    
    # Verificar Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8 o superior es requerido")
        return False
    else:
        print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Verificar MongoDB
    try:
        import pymongo
        print("✓ PyMongo instalado")
    except ImportError:
        print("❌ PyMongo no está instalado. Ejecuta: pip install -r requirements.txt")
    
    return True

if __name__ == '__main__':
    if check_dependencies():
        create_project_structure()
    else:
        print("\n❌ Por favor, instala las dependencias faltantes antes de continuar.")