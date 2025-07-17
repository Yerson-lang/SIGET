#!/usr/bin/env python
"""
Script para crear un usuario administrador en S.IG-ED
"""

import sys
import getpass
from app import app, db
from models.models import User

def create_admin():
    """Crear usuario administrador"""
    print("🔐 Creación de Usuario Administrador para S.IG-ED\n")
    
    # Solicitar datos
    username = input("Nombre de usuario: ").strip()
    if not username:
        print("❌ El nombre de usuario no puede estar vacío")
        return False
    
    email = input("Email: ").strip().lower()
    if not email or '@' not in email:
        print("❌ Email inválido")
        return False
    
    # Solicitar contraseña de forma segura
    password = getpass.getpass("Contraseña: ")
    if len(password) < 8:
        print("❌ La contraseña debe tener al menos 8 caracteres")
        return False
    
    confirm_password = getpass.getpass("Confirmar contraseña: ")
    if password != confirm_password:
        print("❌ Las contraseñas no coinciden")
        return False
    
    with app.app_context():
        # Verificar si el usuario ya existe
        if User.get_by_username(username):
            print(f"❌ El usuario '{username}' ya existe")
            return False
        
        if User.get_by_email(email):
            print(f"❌ El email '{email}' ya está registrado")
            return False
        
        try:
            # Crear usuario administrador
            admin = User.create(
                username=username,
                email=email,
                password=password,
                role='admin'
            )
            
            print(f"\n✅ Usuario administrador '{username}' creado exitosamente!")
            print(f"📧 Email: {email}")
            print(f"🔑 Rol: Administrador")
            print("\n🚀 Ya puedes iniciar sesión en http://localhost:5000")
            return True
            
        except Exception as e:
            print(f"❌ Error al crear usuario: {str(e)}")
            return False

def list_users():
    """Listar usuarios existentes"""
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("No hay usuarios registrados.")
            return
        
        print("\n👥 Usuarios registrados:\n")
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Rol':<15} {'Estado':<10}")
        print("-" * 85)
        
        for user in users:
            status = "Activo" if user.active else "Inactivo"
            print(f"{user.id:<5} {user.username:<20} {user.email:<30} {user.role:<15} {status:<10}")
        
        print(f"\nTotal: {len(users)} usuarios") {'Estado':<10}")
        print("-" * 80)
        
        for user in users:
            status = "Activo" if user.get('active', True) else "Inactivo"
            print(f"{user['username']:<20} {user['email']:<30} {user['role']:<15} {status:<10}")
        
        print(f"\nTotal: {len(users)} usuarios")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        list_users()
    else:
        create_admin()