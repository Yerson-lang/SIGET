// S.IG-ED - Sistema de Gestión de Emergencias y Desastres
// JavaScript Principal
// =========================================

// Configuración global
const CONFIG = {
    API_BASE_URL: '/api',
    REFRESH_INTERVAL: 30000, // 30 segundos
    NOTIFICATION_DURATION: 5000,
    MAP_DEFAULT_ZOOM: 12,
    MAP_DEFAULT_CENTER: { lat: -12.0464, lng: -77.0428 } // Lima, Perú
};

// Estado global de la aplicación
const AppState = {
    currentUser: null,
    activeEmergencies: [],
    notifications: [],
    mapInstance: null
};

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Inicializar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-cerrar alertas
    autoCloseAlerts();

    // Configurar AJAX global
    setupAjaxDefaults();

    // Inicializar notificaciones en tiempo real
    if (window.location.pathname.includes('dashboard')) {
        initializeRealTimeUpdates();
    }

    // Configurar formularios
    setupFormValidation();

    // Animaciones de scroll
    setupScrollAnimations();
}

// Configuración de AJAX
function setupAjaxDefaults() {
    $.ajaxSetup({
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        error: function(xhr, status, error) {
            handleAjaxError(xhr, status, error);
        }
    });
}

// Manejo de errores AJAX
function handleAjaxError(xhr, status, error) {
    let message = 'Error en la solicitud';
    
    if (xhr.status === 401) {
        message = 'Sesión expirada. Por favor, inicia sesión nuevamente.';
        setTimeout(() => {
            window.location.href = '/auth/login';
        }, 2000);
    } else if (xhr.status === 403) {
        message = 'No tienes permisos para realizar esta acción.';
    } else if (xhr.status === 404) {
        message = 'Recurso no encontrado.';
    } else if (xhr.status === 500) {
        message = 'Error del servidor. Por favor, intenta más tarde.';
    } else if (xhr.responseJSON && xhr.responseJSON.error) {
        message = xhr.responseJSON.error;
    }
    
    showNotification(message, 'error');
}

// Sistema de notificaciones
function showNotification(message, type = 'info', duration = CONFIG.NOTIFICATION_DURATION) {
    const notificationHtml = `
        <div class="alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show animate-slide-right" role="alert">
            <i class="bi bi-${type === 'error' ? 'exclamation-circle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.getElementById('notification-container') || createNotificationContainer();
    container.insertAdjacentHTML('beforeend', notificationHtml);
    
    // Auto-cerrar después del tiempo especificado
    setTimeout(() => {
        const alert = container.lastElementChild;
        if (alert) {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }
    }, duration);
}

function createNotificationContainer() {
    const container = document.createElement('div');
    container.id = 'notification-container';
    container.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 9999; max-width: 400px;';
    document.body.appendChild(container);
    return container;
}

// Auto-cerrar alertas
function autoCloseAlerts() {
    setTimeout(() => {
        $('.alert:not(.alert-permanent)').fadeOut('slow', function() {
            $(this).remove();
        });
    }, CONFIG.NOTIFICATION_DURATION);
}

// Validación de formularios
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// Animaciones de scroll
function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

// Actualizaciones en tiempo real
function initializeRealTimeUpdates() {
    // Actualizar dashboard cada 30 segundos
    updateDashboard();
    setInterval(updateDashboard, CONFIG.REFRESH_INTERVAL);
}

function updateDashboard() {
    $.get(`${CONFIG.API_BASE_URL}/stats/dashboard`)
        .done(function(response) {
            if (response.success) {
                updateDashboardStats(response.data);
            }
        });
}

function updateDashboardStats(stats) {
    // Actualizar números con animación
    Object.keys(stats).forEach(key => {
        const element = document.querySelector(`[data-stat="${key}"]`);
        if (element) {
            animateNumber(element, stats[key]);
        }
    });
}

// Animación de números
function animateNumber(element, newValue) {
    const currentValue = parseInt(element.textContent) || 0;
    const increment = (newValue - currentValue) / 20;
    let current = currentValue;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= newValue) || (increment < 0 && current <= newValue)) {
            current = newValue;
            clearInterval(timer);
        }
        element.textContent = Math.round(current);
    }, 50);
}

// Funciones de utilidad
function formatDate(date, format = 'DD/MM/YYYY HH:mm') {
    const d = new Date(date);
    const pad = (n) => n < 10 ? '0' + n : n;
    
    return format
        .replace('DD', pad(d.getDate()))
        .replace('MM', pad(d.getMonth() + 1))
        .replace('YYYY', d.getFullYear())
        .replace('HH', pad(d.getHours()))
        .replace('mm', pad(d.getMinutes()));
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Funciones de emergencia
function createEmergency(data) {
    return $.ajax({
        url: `${CONFIG.API_BASE_URL}/emergencies`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data)
    });
}

function updateEmergencyStatus(emergencyId, status) {
    return $.ajax({
        url: `${CONFIG.API_BASE_URL}/emergencies/${emergencyId}`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify({ status: status })
    });
}

// Exportar funciones para uso global
window.SIGED = {
    showNotification,
    createEmergency,
    updateEmergencyStatus,
    formatDate,
    debounce,
    CONFIG,
    AppState
};

// Service Worker para notificaciones push (opcional)
if ('serviceWorker' in navigator && 'PushManager' in window) {
    navigator.serviceWorker.register('/static/js/sw.js')
        .then(function(registration) {
            console.log('Service Worker registrado:', registration);
        })
        .catch(function(error) {
            console.log('Error al registrar Service Worker:', error);
        });
}

// Prevenir cierre accidental
window.addEventListener('beforeunload', function(e) {
    const forms = document.querySelectorAll('form.has-changes');
    if (forms.length > 0) {
        const message = '¿Estás seguro de que quieres salir? Los cambios no guardados se perderán.';
        e.returnValue = message;
        return message;
    }
});

// Detectar cambios en formularios
document.addEventListener('input', function(e) {
    if (e.target.form) {
        e.target.form.classList.add('has-changes');
    }
});

document.addEventListener('submit', function(e) {
    if (e.target.tagName === 'FORM') {
        e.target.classList.remove('has-changes');
    }
});