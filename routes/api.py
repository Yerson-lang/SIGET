from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from models.models import db, User, Emergency, Report, EmergencyUpdate
from sqlalchemy import func, and_, or_
import json

api_bp = Blueprint('api', __name__)

# Decorador para requerir rol específico
def require_role(role):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if role == 'admin' and not current_user.is_admin():
                return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador'}), 403
            elif role == 'operator' and not current_user.is_operator():
                return jsonify({'error': 'Acceso denegado. Se requiere rol de operador'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Utilidad para serializar modelos SQLAlchemy
def serialize_emergency(emergency):
    return {
        '_id': emergency.id,
        'type': emergency.type,
        'title': emergency.title,
        'description': emergency.description,
        'location': {
            'lat': emergency.latitude,
            'lng': emergency.longitude,
            'address': emergency.address,
            'city': emergency.city,
            'region': emergency.region
        },
        'severity': emergency.severity,
        'status': emergency.status,
        'active': emergency.active,
        'affected_people': emergency.affected_people,
        'reported_by': emergency.reported_by,
        'created_at': emergency.created_at.isoformat() if emergency.created_at else None,
        'updated_at': emergency.updated_at.isoformat() if emergency.updated_at else None,
        'resolved_at': emergency.resolved_at.isoformat() if emergency.resolved_at else None
    }

def serialize_report(report):
    return {
        '_id': report.id,
        'title': report.title,
        'type': report.type,
        'content': report.content,
        'emergency_id': report.emergency_id,
        'created_by': report.created_by,
        'created_at': report.created_at.isoformat() if report.created_at else None,
        'status': report.status,
        'visibility': report.visibility,
        'tags': report.tags.split(',') if report.tags else [],
        'views': report.views
    }

# ============= EMERGENCIAS API =============

@api_bp.route('/emergencies', methods=['GET'])
@login_required
def get_emergencies():
    """Obtener lista de emergencias con filtros"""
    # Parámetros de filtro
    active_only = request.args.get('active', 'false').lower() == 'true'
    emergency_type = request.args.get('type')
    status = request.args.get('status')
    severity = request.args.get('severity')
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    # Construir query
    query = Emergency.query
    
    if active_only:
        query = query.filter_by(active=True)
    if emergency_type:
        query = query.filter_by(type=emergency_type)
    if status:
        query = query.filter_by(status=status)
    if severity:
        query = query.filter_by(severity=severity)
    
    # Ejecutar query
    total = query.count()
    emergencies = query.order_by(Emergency.created_at.desc()).offset(offset).limit(limit).all()
    
    return jsonify({
        'success': True,
        'data': [serialize_emergency(e) for e in emergencies],
        'total': total,
        'limit': limit,
        'offset': offset
    })

@api_bp.route('/emergencies/<int:emergency_id>', methods=['GET'])
@login_required
def get_emergency(emergency_id):
    """Obtener detalle de una emergencia"""
    emergency = Emergency.query.get_or_404(emergency_id)
    return jsonify({
        'success': True,
        'data': serialize_emergency(emergency)
    })

@api_bp.route('/emergencies', methods=['POST'])
@login_required
def create_emergency():
    """Crear nueva emergencia"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400
    
    # Validaciones
    required_fields = ['title', 'description', 'type', 'lat', 'lng']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    # Agregar usuario que reporta
    data['reported_by'] = current_user.id
    
    try:
        emergency_id = Emergency.create(data)
        return jsonify({
            'success': True,
            'message': 'Emergencia creada exitosamente',
            'emergency_id': emergency_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api_bp.route('/emergencies/<int:emergency_id>', methods=['PUT'])
@require_role('operator')
def update_emergency(emergency_id):
    """Actualizar emergencia (solo operadores/admin)"""
    emergency = Emergency.query.get_or_404(emergency_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400
    
    try:
        # Actualizar campos permitidos
        allowed_fields = ['title', 'description', 'status', 'severity', 
                         'affected_people', 'address', 'city', 'region']
        
        for field in allowed_fields:
            if field in data:
                setattr(emergency, field, data[field])
        
        # Si se actualiza el estado
        if 'status' in data:
            emergency.update_status(data['status'], current_user.id)
        else:
            emergency.updated_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Emergencia actualizada exitosamente'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api_bp.route('/emergencies/<int:emergency_id>', methods=['DELETE'])
@require_role('admin')
def delete_emergency(emergency_id):
    """Eliminar emergencia (solo admin)"""
    emergency = Emergency.query.get_or_404(emergency_id)
    
    try:
        db.session.delete(emergency)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Emergencia eliminada exitosamente'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# ============= REPORTES API =============

@api_bp.route('/reports', methods=['GET'])
@login_required
def get_reports():
    """Obtener lista de reportes"""
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    
    query = Report.query.filter_by(status='published')
    total = query.count()
    reports = query.order_by(Report.created_at.desc()).offset(offset).limit(limit).all()
    
    return jsonify({
        'success': True,
        'data': [serialize_report(r) for r in reports],
        'total': total,
        'limit': limit,
        'offset': offset
    })

@api_bp.route('/reports', methods=['POST'])
@require_role('operator')
def create_report():
    """Crear nuevo reporte"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400
    
    # Validaciones
    required_fields = ['title', 'type', 'content']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    data['created_by'] = current_user.id
    
    try:
        report_id = Report.create(data)
        return jsonify({
            'success': True,
            'message': 'Reporte creado exitosamente',
            'report_id': report_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# ============= ESTADÍSTICAS API =============

@api_bp.route('/stats/dashboard', methods=['GET'])
@login_required
def get_dashboard_stats():
    """Obtener estadísticas para el dashboard"""
    # Usar consultas SQL optimizadas
    total_emergencies = db.session.query(func.count(Emergency.id)).scalar()
    active_emergencies = db.session.query(func.count(Emergency.id)).filter_by(active=True).scalar()
    
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    resolved_today = db.session.query(func.count(Emergency.id)).filter(
        Emergency.resolved_at >= today_start
    ).scalar()
    
    total_reports = db.session.query(func.count(Report.id)).scalar()
    total_users = db.session.query(func.count(User.id)).filter_by(active=True).scalar()
    response_teams = db.session.query(func.count(User.id)).filter(
        User.role.in_(['operator', 'admin']),
        User.active == True
    ).scalar()
    
    stats = {
        'total_emergencies': total_emergencies,
        'active_emergencies': active_emergencies,
        'resolved_today': resolved_today,
        'total_reports': total_reports,
        'total_users': total_users,
        'response_teams': response_teams
    }
    
    return jsonify({
        'success': True,
        'data': stats
    })

@api_bp.route('/stats/emergencies/by-type', methods=['GET'])
@login_required
def get_emergencies_by_type():
    """Obtener emergencias agrupadas por tipo"""
    days = int(request.args.get('days', 30))
    start_date = datetime.now() - timedelta(days=days)
    
    result = db.session.query(
        Emergency.type,
        func.count(Emergency.id).label('count')
    ).filter(
        Emergency.created_at >= start_date
    ).group_by(Emergency.type).order_by(func.count(Emergency.id).desc()).all()
    
    data = [{'_id': r.type, 'count': r.count} for r in result]
    
    return jsonify({
        'success': True,
        'data': data,
        'period_days': days
    })

@api_bp.route('/stats/emergencies/by-location', methods=['GET'])
@login_required
def get_emergencies_by_location():
    """Obtener emergencias agrupadas por ubicación"""
    result = db.session.query(
        Emergency.city,
        Emergency.region,
        func.count(Emergency.id).label('count'),
        func.sum(func.if_(Emergency.active == True, 1, 0)).label('active')
    ).group_by(
        Emergency.city,
        Emergency.region
    ).order_by(func.count(Emergency.id).desc()).limit(20).all()
    
    data = []
    for r in result:
        data.append({
            '_id': {
                'city': r.city or 'Sin ciudad',
                'region': r.region or 'Sin región'
            },
            'count': r.count,
            'active': r.active or 0
        })
    
    return jsonify({
        'success': True,
        'data': data
    })

# ============= USUARIOS API =============

@api_bp.route('/users', methods=['GET'])
@require_role('admin')
def get_users():
    """Obtener lista de usuarios (solo admin)"""
    users = User.query.all()
    
    users_data = []
    for user in users:
        users_data.append({
            '_id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'active': user.active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        })
    
    return jsonify({
        'success': True,
        'data': users_data,
        'total': len(users_data)
    })

@api_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@require_role('admin')
def update_user_status(user_id):
    """Activar/desactivar usuario (solo admin)"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'active' not in data:
        return jsonify({'error': 'Campo "active" requerido'}), 400
    
    try:
        user.active = bool(data['active'])
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Usuario {"activado" if data["active"] else "desactivado"} exitosamente'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# ============= BÚSQUEDA API =============

@api_bp.route('/search', methods=['GET'])
@login_required
def search():
    """Búsqueda general en emergencias"""
    query_text = request.args.get('q', '')
    if not query_text:
        return jsonify({'error': 'Parámetro de búsqueda requerido'}), 400
    
    search_filter = f'%{query_text}%'
    results = Emergency.query.filter(
        or_(
            Emergency.title.like(search_filter),
            Emergency.description.like(search_filter),
            Emergency.address.like(search_filter),
            Emergency.city.like(search_filter)
        )
    ).order_by(Emergency.created_at.desc()).limit(20).all()
    
    return jsonify({
        'success': True,
        'data': [serialize_emergency(e) for e in results],
        'query': query_text,
        'count': len(results)
    })

# ============= HEALTH CHECK =============

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Verificar estado del API"""
    try:
        # Verificar conexión a la base de datos
        db.session.execute('SELECT 1')
        db_status = 'OK'
    except:
        db_status = 'ERROR'
    
    return jsonify({
        'status': 'OK' if db_status == 'OK' else 'ERROR',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'S.IG-ED API',
        'version': '1.0.0',
        'database': db_status
    })