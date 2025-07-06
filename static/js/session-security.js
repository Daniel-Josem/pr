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
    
    // Limpiar cache cuando se cierra la ventana
    window.addEventListener('unload', function() {
        // Enviar request para invalidar sesión si es necesario
        navigator.sendBeacon('/api/cleanup-session');
    });
    
})();
