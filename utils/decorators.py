from functools import wraps
from flask import redirect, url_for, flash, request, jsonify
from flask_login import current_user
import time

def admin_required(f):
    """Decorador para requerir rol de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor inicia sesión para acceder a esta página.', 'error')
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_admin():
            flash('No tienes permisos para acceder a esta página.', 'error')
            return redirect(url_for('dashboard.main'))
        
        return f(*args, **kwargs)
    return decorated_function

def operator_required(f):
    """Decorador para requerir rol de operador o superior"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor inicia sesión para acceder a esta página.', 'error')
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_operator():
            flash('No tienes permisos para acceder a esta página.', 'error')
            return redirect(url_for('dashboard.main'))
        
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(calls=10, period=60):
    """Decorador para limitar llamadas a una función"""
    def decorator(f):
        calls_made = {}
        
        @wraps(f)
        def wrapper(*args, **kwargs):
            now = time.time()
            key = f"{current_user.id if current_user.is_authenticated else request.remote_addr}"
            
            # Limpiar llamadas antiguas
            calls_made[key] = [call for call in calls_made.get(key, []) 
                             if call > now - period]
            
            # Verificar límite
            if len(calls_made.get(key, [])) >= calls:
                return jsonify({
                    'error': 'Límite de llamadas excedido. Intenta más tarde.'
                }), 429
            
            # Registrar llamada
            calls_made.setdefault(key, []).append(now)
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

def measure_performance(f):
    """Decorador para medir el tiempo de ejecución de una función"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"{f.__name__} tomó {execution_time:.3f} segundos")
        
        # Si es una respuesta JSON, agregar el tiempo
        if isinstance(result, tuple) and len(result) == 2:
            response, status_code = result
            if isinstance(response, dict):
                response['_execution_time'] = f"{execution_time:.3f}s"
                return jsonify(response), status_code
        
        return result
    return wrapper

def validate_json(*expected_args):
    """Decorador para validar JSON en requests"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            json_data = request.get_json()
            
            if not json_data:
                return jsonify({'error': 'No se proporcionaron datos JSON'}), 400
            
            for arg in expected_args:
                if arg not in json_data:
                    return jsonify({
                        'error': f'Campo requerido faltante: {arg}'
                    }), 400
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

def async_task(f):
    """Decorador para ejecutar tareas en segundo plano (placeholder)"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        # En producción, esto podría usar Celery o similar
        # Por ahora, ejecuta sincrónicamente
        try:
            result = f(*args, **kwargs)
            return result
        except Exception as e:
            print(f"Error en tarea asíncrona {f.__name__}: {str(e)}")
            return None
    return wrapper

def cache_result(timeout=300):
    """Decorador simple de caché en memoria"""
    def decorator(f):
        cache = {}
        cache_time = {}
        
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Crear clave de caché
            key = str(args) + str(kwargs)
            
            # Verificar si está en caché y no ha expirado
            if key in cache and time.time() - cache_time[key] < timeout:
                return cache[key]
            
            # Ejecutar función y guardar en caché
            result = f(*args, **kwargs)
            cache[key] = result
            cache_time[key] = time.time()
            
            return result
        return wrapper
    return decorator    