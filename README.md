# S.IG-ED - Sistema de Gestión de Emergencias y Desastres 🔥

<div align="center">
  <img src="static/img/logo.png" alt="S.IG-ED Logo" width="200">
  <h3>Sistema de Gestión de Datos Distribuidos para Seguimiento de Emergencias y Desastres Naturales</h3>
  <p>
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/Flask-2.3.3-green.svg" alt="Flask">
    <img src="https://img.shields.io/badge/MongoDB-4.4+-green.svg" alt="MongoDB">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  </p>
</div>

## 📋 Descripción

S.IG-ED es un sistema integral de gestión de emergencias diseñado para coordinar y monitorear respuestas a desastres naturales y emergencias en tiempo real. El sistema proporciona herramientas para el reporte, seguimiento y resolución de emergencias, con visualización geográfica y análisis de datos.

## ✨ Características Principales

- 🗺️ **Mapa Interactivo**: Visualización en tiempo real de emergencias con Google Maps
- 📊 **Dashboard Analítico**: Estadísticas y métricas de emergencias
- 🚨 **Sistema de Alertas**: Notificaciones en tiempo real
- 👥 **Gestión de Usuarios**: Roles y permisos (Admin, Operador, Usuario)
- 📱 **Diseño Responsivo**: Accesible desde cualquier dispositivo
- 🔐 **Autenticación Segura**: Sistema de login con encriptación
- 📈 **Reportes Detallados**: Generación de informes y análisis
- 🌐 **API REST**: Integración con sistemas externos

## 🛠️ Tecnologías Utilizadas

### Backend
- **Flask**: Framework web principal
- **MongoDB**: Base de datos NoSQL
- **Flask-Login**: Gestión de sesiones
- **Flask-PyMongo**: Integración con MongoDB

### Frontend
- **Bootstrap 5**: Framework CSS
- **Chart.js**: Gráficos y visualizaciones
- **Google Maps API**: Mapas interactivos
- **jQuery**: Interactividad

## 📦 Instalación

### Requisitos Previos
- Python 3.8 o superior
- MongoDB 4.4 o superior
- API Key de Google Maps

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/tuusuario/siged.git
cd siged
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
Crear archivo `.env` en la raíz del proyecto:
```env
SECRET_KEY=tu-clave-secreta-aqui
GOOGLE_MAPS_API_KEY=tu-api-key-de-google-maps
FLASK_ENV=development
```


5. **Ejecutar la aplicación**
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## 🚀 Uso

### Primer Acceso
1. Navegar a `http://localhost:5000`
2. Crear una cuenta nueva
3. Iniciar sesión con las credenciales

### Crear Usuario Administrador
```python
# En la consola de Python
from app import app, mongo
from models.models import User

with app.app_context():
    admin = User.create(
        username='admin',
        email='admin@siged.com',
        password='admin123',
        role='admin'
    )
```

### Reportar Emergencia
1. Ir al Dashboard
2. Click en "Nueva Emergencia"
3. Completar el formulario con:
   - Tipo de emergencia
   - Ubicación (usar el mapa)
   - Descripción
   - Severidad
4. Enviar reporte

## 📁 Estructura del Proyecto

```
S.IG-ED/
├── app.py                 # Aplicación principal
├── config.py             # Configuraciones
├── requirements.txt      # Dependencias
├── .env                  # Variables de entorno (no incluir en git)
├── static/
│   ├── css/             # Estilos personalizados
│   ├── js/              # JavaScript
│   └── img/             # Imágenes
├── templates/
│   ├── base.html        # Template base
│   ├── login.html       # Página de login
│   ├── dashboard.html   # Panel principal
│   └── map.html         # Vista del mapa
├── models/
│   └── models.py        # Modelos de datos
├── routes/
│   ├── auth.py          # Rutas de autenticación
│   ├── dashboard.py     # Rutas del dashboard
│   └── api.py           # API endpoints
└── utils/
    └── decorators.py    # Utilidades
```

## 🔑 API Endpoints

### Autenticación
- `POST /auth/login` - Iniciar sesión
- `POST /auth/register` - Registrar usuario
- `GET /auth/logout` - Cerrar sesión

### Emergencias
- `GET /api/emergencies` - Listar emergencias
- `POST /api/emergencies` - Crear emergencia
- `GET /api/emergencies/<id>` - Obtener emergencia
- `PUT /api/emergencies/<id>` - Actualizar emergencia
- `DELETE /api/emergencies/<id>` - Eliminar emergencia

### Reportes
- `GET /api/reports` - Listar reportes
- `POST /api/reports` - Crear reporte
- `GET /api/reports/<id>` - Obtener reporte

## 🔧 Configuración Avanzada

### Configurar Google Maps API

1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear nuevo proyecto o seleccionar existente
3. Habilitar "Maps JavaScript API"
4. Crear credenciales (API Key)
5. Agregar restricciones de seguridad
6. Copiar API Key al archivo `.env`

### Configurar MongoDB en Producción

Para usar MongoDB Atlas (cloud):
```env
MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/siged_db?retryWrites=true&w=majority
```

### Despliegue en Producción

1. **Configurar Gunicorn**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

2. **Configurar Nginx**
```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /path/to/siged/static;
    }
}
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abrir Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Equipo

- **Desarrollador Principal**: Tu Nombre
- **Diseño UI/UX**: Equipo de Diseño
- **Backend**: Equipo de Desarrollo
- **Testing**: Equipo de QA

## 📞 Soporte

Para soporte y consultas:
- 📧 Email: soporte@siged.com
- 🐛 Issues: [GitHub Issues](https://github.com/tuusuario/siged/issues)
- 📖 Documentación: [Wiki](https://github.com/tuusuario/siged/wiki)

## 🙏 Agradecimientos

- A todos los equipos de emergencia que trabajan incansablemente
- A la comunidad open source por las herramientas utilizadas
- A los beta testers por sus valiosos comentarios

---

<div align="center">
  <p>Hecho con ❤️ para salvar vidas</p>
  <p>© 2025 S.IG-ED - Todos los derechos reservados</p>
</div>
