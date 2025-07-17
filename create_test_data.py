#!/usr/bin/env python

from app import app, db
from models.models import User, Emergency, Report
from datetime import datetime, timedelta
import random

def create_test_data():
    """Crear datos de prueba"""
    print("🚀 Creando datos de prueba para S.IG-ED...\n")
    
    with app.app_context():
        # Verificar si ya existe un admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("✅ Creando usuario administrador...")
            admin = User.create(
                username='admin',
                email='admin@siged.com',
                password='admin123',
                role='admin'
            )
            admin.full_name = 'Administrador del Sistema'
            db.session.commit()
            print("   Usuario: admin")
            print("   Contraseña: admin123")
        
        # Crear un operador de prueba
        operator = User.query.filter_by(username='operador1').first()
        if not operator:
            print("\n✅ Creando usuario operador...")
            operator = User.create(
                username='operador1',
                email='operador1@siged.com',
                password='operador123',
                role='operator'
            )
            operator.full_name = 'Juan Pérez'
            operator.phone = '+51 999 888 777'
            operator.organization = 'Centro de Control'
            db.session.commit()
            print("   Usuario: operador1")
            print("   Contraseña: operador123")
        
        # Crear emergencias de prueba
        print("\n✅ Creando emergencias de prueba...")
        
        emergency_data = [
            {
                'type': 'fire',
                'title': 'Incendio en edificio residencial',
                'description': 'Incendio de grandes proporciones en edificio de 10 pisos. Se reportan personas atrapadas en los pisos superiores. Se necesitan unidades de bomberos adicionales.',
                'lat': -12.0553,
                'lng': -77.0451,
                'address': 'Av. Javier Prado Este 1234, San Isidro',
                'city': 'Lima',
                'region': 'Lima',
                'severity': 'high',
                'affected_people': 50,
                'status': 'responding'
            },
            {
                'type': 'accident',
                'title': 'Accidente vehicular múltiple en Panamericana Sur',
                'description': 'Colisión múltiple involucrando 5 vehículos. Hay heridos graves que necesitan atención médica urgente.',
                'lat': -12.1819,
                'lng': -76.9478,
                'address': 'Panamericana Sur Km 25',
                'city': 'Lurín',
                'region': 'Lima',
                'severity': 'critical',
                'affected_people': 12,
                'status': 'confirmed'
            },
            {
                'type': 'flood',
                'title': 'Inundación en zona residencial',
                'description': 'Desborde del río Rímac ha causado inundaciones en varias manzanas. Familias necesitan ser evacuadas.',
                'lat': -11.9895,
                'lng': -77.0073,
                'address': 'Jr. Los Álamos, Ate',
                'city': 'Ate',
                'region': 'Lima',
                'severity': 'medium',
                'affected_people': 200,
                'status': 'reported'
            },
            {
                'type': 'medical',
                'title': 'Emergencia médica masiva - Intoxicación alimentaria',
                'description': 'Múltiples casos de intoxicación en evento público. Se requieren ambulancias y personal médico adicional.',
                'lat': -12.0873,
                'lng': -77.0503,
                'address': 'Centro de Convenciones, San Borja',
                'city': 'San Borja',
                'region': 'Lima',
                'severity': 'high',
                'affected_people': 80,
                'status': 'responding'
            },
            {
                'type': 'earthquake',
                'title': 'Sismo de 5.2 grados - Daños estructurales',
                'description': 'Sismo ha causado daños en varias edificaciones antiguas. Se requiere evaluación estructural urgente.',
                'lat': -12.0464,
                'lng': -77.0428,
                'address': 'Centro Histórico de Lima',
                'city': 'Lima',
                'region': 'Lima',
                'severity': 'critical',
                'affected_people': 500,
                'status': 'resolved',
                'resolved': True
            }
        ]
        
        emergencies_created = 0
        for data in emergency_data:
            # Verificar si ya existe una emergencia similar
            existing = Emergency.query.filter_by(title=data['title']).first()
            if not existing:
                resolved = data.pop('resolved', False)
                data['reported_by'] = admin.id
                emergency_id = Emergency.create(data)
                
                # Si está resuelta, actualizar fecha
                if resolved:
                    emergency = Emergency.query.get(emergency_id)
                    emergency.resolved_at = datetime.utcnow() - timedelta(hours=random.randint(1, 24))
                    emergency.active = False
                    db.session.commit()
                
                emergencies_created += 1
        
        print(f"   Creadas {emergencies_created} emergencias de prueba")
        
        # Crear reportes de prueba
        print("\n✅ Creando reportes de prueba...")
        
        report_data = [
            {
                'title': 'Informe Mensual de Emergencias - Julio 2025',
                'type': 'summary',
                'content': 'Este informe presenta un resumen detallado de todas las emergencias atendidas durante el mes de julio de 2025. Se registraron un total de 45 emergencias, con un tiempo promedio de respuesta de 15 minutos.',
                'created_by': admin.id,
                'tags': ['mensual', 'julio', '2025', 'estadísticas']
            },
            {
                'title': 'Análisis de Respuesta ante Incendios',
                'type': 'analysis',
                'content': 'Análisis detallado de los protocolos de respuesta ante incendios implementados en el último trimestre. Se identificaron áreas de mejora en la coordinación entre unidades.',
                'created_by': operator.id,
                'tags': ['incendios', 'protocolos', 'análisis']
            },
            {
                'title': 'Reporte de Emergencia Médica - Centro de Convenciones',
                'type': 'emergency',
                'content': 'Reporte completo del incidente de intoxicación masiva ocurrido en el Centro de Convenciones. Se atendieron 80 personas, de las cuales 15 requirieron hospitalización.',
                'created_by': operator.id,
                'tags': ['médica', 'intoxicación', 'masiva']
            }
        ]
        
        reports_created = 0
        for data in report_data:
            existing = Report.query.filter_by(title=data['title']).first()
            if not existing:
                report_id = Report.create(data)
                reports_created += 1
        
        print(f"   Creados {reports_created} reportes de prueba")
        
        db.session.commit()
        
        print("\n✅ Datos de prueba creados exitosamente!")
        print("\n📋 Usuarios creados:")
        print("   - admin / admin123 (Administrador)")
        print("   - operador1 / operador123 (Operador)")
        print("\n🚀 Ya puedes iniciar sesión y explorar el sistema!")

if __name__ == '__main__':
    create_test_data()