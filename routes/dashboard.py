from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.models import db, User, Emergency, Report, EmergencyUpdate
from datetime import datetime, timedelta
from sqlalchemy import func, and_

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def main():
    """Dashboard principal"""
    
    # Obtener estadísticas usando SQLAlchemy
    total_emergencies = Emergency.query.count()
    active_emergencies = Emergency.query.filter_by(active=True).count()
    
    # Emergencias resueltas hoy
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    resolved_today = Emergency.query.filter(
        Emergency.resolved_at >= today_start
    ).count()
    
    total_reports = Report.query.count()
    total_users = User.query.filter_by(active=True).count()
    response_teams = User.query.filter(
        User.role.in_(['operator', 'admin']),
        User.active == True
    ).count()
    
    stats = {
        'total_emergencies': total_emergencies,
        'active_emergencies': active_emergencies,
        'resolved_today': resolved_today,
        'total_reports': total_reports,
        'total_users': total_users,
        'response_teams': response_teams
    }
    
    # Emergencias recientes
    recent_emergencies = Emergency.query.order_by(
        Emergency.created_at.desc()
    ).limit(5).all()
    
    # Preparar datos de emergencias
    emergencies_data = []
    for e in recent_emergencies:
        emergencies_data.append({
            '_id': e.id,
            'title': e.title,
            'description': e.description,
            'type': e.type,
            'status': e.status,
            'location': {
                'city': e.city or 'Sin ciudad',
                'address': e.address or 'Sin dirección'
            },
            'created_at': e.created_at,
            'type_info': Emergency.TYPES.get(e.type, Emergency.TYPES['other'])
        })
    
    # Emergencias por tipo (últimos 30 días)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    emergency_types = db.session.query(
        Emergency.type,
        func.count(Emergency.id).label('count')
    ).filter(
        Emergency.created_at >= thirty_days_ago
    ).group_by(Emergency.type).all()
    
    emergency_types_data = {item.type: item.count for item in emergency_types}
    
    # Actividad diaria (últimos 7 días)
    seven_days_ago = datetime.now() - timedelta(days=7)
    daily_activity = []
    
    for i in range(7):
        date = seven_days_ago + timedelta(days=i)
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        count = Emergency.query.filter(
            and_(Emergency.created_at >= date_start,
                 Emergency.created_at <= date_end)
        ).count()
        
        daily_activity.append({
            '_id': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    return render_template('dashboard.html',
                         stats=stats,
                         recent_emergencies=emergencies_data,
                         emergency_types_data=emergency_types_data,
                         daily_activity_data=daily_activity)

@dashboard_bp.route('/emergency/new', methods=['GET', 'POST'])
@login_required
def new_emergency():
    """Crear nueva emergencia"""
    if request.method == 'POST':
        data = request.form.to_dict()
        data['reported_by'] = current_user.id
        
        try:
            emergency_id = Emergency.create(data)
            return jsonify({
                'success': True,
                'message': 'Emergencia creada exitosamente',
                'emergency_id': emergency_id
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    
    return render_template('new_emergency.html')

@dashboard_bp.route('/emergency/<int:emergency_id>')
@login_required
def emergency_detail(emergency_id):
    """Ver detalle de emergencia"""
    emergency = Emergency.query.get_or_404(emergency_id)
    
    # Obtener usuario que reportó
    reporter = User.query.get(emergency.reported_by) if emergency.reported_by else None
    
    # Obtener actualizaciones
    updates = []
    for update in emergency.updates:
        updates.append({
            'user_id': update.user_id,
            'message': update.message or update.action,
            'timestamp': update.timestamp,
            'user': update.user
        })
    
    return render_template('emergency_detail.html',
                         emergency=emergency,
                         reporter=reporter,
                         updates=updates)

@dashboard_bp.route('/emergency/<int:emergency_id>/update', methods=['POST'])
@login_required
def update_emergency(emergency_id):
    """Actualizar estado de emergencia"""
    emergency = Emergency.query.get_or_404(emergency_id)
    data = request.json
    action = data.get('action')
    
    try:
        if action == 'status':
            new_status = data.get('status')
            emergency.update_status(new_status, current_user.id)
            message = f'Estado actualizado a {new_status}'
        
        elif action == 'message':
            message_text = data.get('message')
            update = EmergencyUpdate(
                emergency_id=emergency_id,
                user_id=current_user.id,
                message=message_text,
                timestamp=datetime.utcnow()
            )
            db.session.add(update)
            db.session.commit()
            message = 'Actualización agregada'
        
        else:
            return jsonify({'success': False, 'message': 'Acción no válida'}), 400
        
        return jsonify({'success': True, 'message': message})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@dashboard_bp.route('/stats/overview')
@login_required
def stats_overview():
    """Vista de estadísticas generales"""
    # Estadísticas por mes (último año)
    one_year_ago = datetime.now() - timedelta(days=365)
    
    monthly_stats = db.session.query(
        func.year(Emergency.created_at).label('year'),
        func.month(Emergency.created_at).label('month'),
        func.count(Emergency.id).label('total'),
        func.sum(func.if_(Emergency.status == 'resolved', 1, 0)).label('resolved')
    ).filter(
        Emergency.created_at >= one_year_ago
    ).group_by(
        func.year(Emergency.created_at),
        func.month(Emergency.created_at)
    ).all()
    
    # Tiempo promedio de respuesta
    avg_response = db.session.query(
        func.avg(
            func.timestampdiff(
                'MINUTE',
                Emergency.created_at,
                Emergency.resolved_at
            )
        )
    ).filter(
        Emergency.status == 'resolved',
        Emergency.resolved_at.isnot(None)
    ).scalar()
    
    response_times = [{
        '_id': None,
        'avg_response_time': avg_response * 60000 if avg_response else 0  # Convertir a milisegundos
    }]
    
    # Emergencias por región
    by_region = db.session.query(
        Emergency.region,
        func.count(Emergency.id).label('count')
    ).group_by(Emergency.region).order_by(func.count(Emergency.id).desc()).limit(10).all()
    
    by_region_data = [{'_id': r.region or 'Sin región', 'count': r.count} for r in by_region]
    
    monthly_stats_data = []
    for stat in monthly_stats:
        monthly_stats_data.append({
            '_id': {'year': stat.year, 'month': stat.month},
            'total': stat.total,
            'resolved': stat.resolved or 0
        })
    
    return render_template('stats_overview.html',
                         monthly_stats=monthly_stats_data,
                         response_times=response_times,
                         by_region=by_region_data)

@dashboard_bp.route('/search')
@login_required
def search():
    """Búsqueda de emergencias"""
    query = request.args.get('q', '')
    emergency_type = request.args.get('type', '')
    status = request.args.get('status', '')
    date_from = request.args.get('from', '')
    date_to = request.args.get('to', '')
    
    # Construir consulta
    emergencies_query = Emergency.query
    
    if query:
        search_filter = f'%{query}%'
        emergencies_query = emergencies_query.filter(
            db.or_(
                Emergency.title.like(search_filter),
                Emergency.description.like(search_filter),
                Emergency.address.like(search_filter)
            )
        )
    
    if emergency_type:
        emergencies_query = emergencies_query.filter_by(type=emergency_type)
    
    if status:
        emergencies_query = emergencies_query.filter_by(status=status)
    
    if date_from:
        emergencies_query = emergencies_query.filter(
            Emergency.created_at >= datetime.strptime(date_from, '%Y-%m-%d')
        )
    
    if date_to:
        emergencies_query = emergencies_query.filter(
            Emergency.created_at <= datetime.strptime(date_to, '%Y-%m-%d')
        )
    
    # Ejecutar búsqueda
    results = emergencies_query.order_by(Emergency.created_at.desc()).limit(50).all()
    
    return render_template('search_results.html',
                         results=results,
                         query=query,
                         filters={
                             'type': emergency_type,
                             'status': status,
                             'from': date_from,
                             'to': date_to
                         })