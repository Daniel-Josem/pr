/**
 * Script de seguridad de sesión
 * Previene el acceso a páginas protegidas usando el botón atrás del navegador
 */

(function() {
    'use strict';
    
    // Prevenir cache del navegador
    if (window.history && window.history.pushState) {
        window.history.pushState('forward', null, window.location.href);
        window.addEventListener('popstate', function() {
            // Si el usuario intenta ir atrás, redirigir al login
            window.location.href = '/login';
        });
    }
    
    // Detectar cuando la página se carga desde cache
    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {
            // Si la página se carga desde cache, forzar recarga
            window.location.reload();
        }
    });
    
    // Detectar cuando el usuario intenta salir de la página
    window.addEventListener('beforeunload', function() {
        // Limpiar cualquier dato sensible del localStorage/sessionStorage
        localStorage.clear();
        sessionStorage.clear();
    });
    
    // Función para validar sesión periódicamente
    function validarSesion() {
        fetch('/api/validar-sesion', {
            method: 'GET',
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                // Si la sesión no es válida, redirigir al login
                window.location.href = '/login';
            }
        })
        .catch(() => {
            // En caso de error, redirigir al login
            window.location.href = '/login';
        });
    }
    
    // Validar sesión cada 5 minutos
    setInterval(validarSesion, 5 * 60 * 1000);
    
    // Variable para detectar si es una navegación interna
    let isInternalNavigation = false;
    
    // Marcar navegaciones internas (enlaces dentro de la app)
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'A' && e.target.href && e.target.href.includes(window.location.origin)) {
            isInternalNavigation = true;
        }
    });
    
    // Marcar envíos de formularios como navegación interna
    document.addEventListener('submit', function(e) {
        isInternalNavigation = true;
    });
    
    // Limpiar sesión solo cuando realmente se cierra la ventana/pestaña
    window.addEventListener('beforeunload', function(e) {
        // Solo limpiar si no es navegación interna
        if (!isInternalNavigation) {
            // Esta es una salida real de la aplicación
            navigator.sendBeacon('/api/cleanup-session', JSON.stringify({action: 'close'}));
        }
        // Reset para próxima navegación
        setTimeout(() => { isInternalNavigation = false; }, 0);
    });
    
})();
