from flask import render_template, request, session, current_app, jsonify
import logging
import traceback
from datetime import datetime
import os
import sqlite3

# Configuración básica de logging
def setup_error_logging(app):
    """Configura el sistema de logging para errores"""
    try:
        # Crear directorio de logs si no existe
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # Configurar logging de errores
        if not app.debug:
            file_handler = logging.FileHandler(os.path.join(logs_dir, 'error.log'))
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.ERROR)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.ERROR)
    except Exception as e:
        print(f"Error setting up logging: {e}")

def log_error(error_code, error_message, user_info=None, request_info=None):
    """Registra errores en el log con información detallada"""
    try:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_code': error_code,
            'error_message': error_message,
            'user_info': user_info or {},
            'request_info': request_info or {}
        }
        
        print(f"🚨 Error {error_code}: {error_message}")
        if current_app:
            current_app.logger.error(f"Error {error_code}: {error_message} | Details: {log_entry}")
    except Exception as e:
        print(f"Error logging failed: {e}")

def get_user_info():
    """Obtiene información segura del usuario para logging"""
    try:
        user_info = {
            'user_id': session.get('user_id'),
            'user_role': session.get('user_role'),
            'is_authenticated': 'user_id' in session
        }
        return user_info
    except:
        return {}

def get_request_info():
    """Obtiene información de la petición para logging"""
    try:
        request_info = {
            'url': request.url,
            'method': request.method,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')[:100]  # Limitar longitud
        }
        return request_info
    except:
        return {}

def register_error_handlers(app):
    """Registra todos los manejadores de errores personalizados"""
    
    # Configurar logging
    setup_error_logging(app)
    
    @app.errorhandler(404)
    def not_found_error(error):
        user_info = get_user_info()
        request_info = get_request_info()
        log_error(404, f"Página no encontrada: {request.url}", user_info, request_info)
        
        return render_template('error.html', 
                             error_code=404,
                             error_title="¡Oops! Página no encontrada",
                             error_message="La página que estás buscando no existe o fue movida."), 404

    @app.errorhandler(500)
    def internal_error(error):
        user_info = get_user_info()
        request_info = get_request_info()
        log_error(500, f"Error interno del servidor: {str(error)}", user_info, request_info)
        
        return render_template('error.html',
                             error_code=500,
                             error_title="Error interno del servidor",
                             error_message="Algo salió mal en nuestro servidor. Inténtalo de nuevo más tarde."), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        user_info = get_user_info()
        request_info = get_request_info()
        log_error(403, f"Acceso denegado", user_info, request_info)
        
        return render_template('error.html',
                             error_code=403,
                             error_title="Acceso denegado",
                             error_message="No tienes permisos para acceder a esta página."), 403

    @app.errorhandler(401)
    def unauthorized_error(error):
        user_info = get_user_info()
        request_info = get_request_info()
        log_error(401, f"Usuario no autorizado", user_info, request_info)
        
        return render_template('error.html',
                             error_code=401,
                             error_title="No autorizado",
                             error_message="Debes iniciar sesión para acceder a esta página."), 401

    @app.errorhandler(400)
    def bad_request_error(error):
        user_info = get_user_info()
        request_info = get_request_info()
        log_error(400, f"Solicitud incorrecta", user_info, request_info)
        
        return render_template('error.html',
                             error_code=400,
                             error_title="Solicitud incorrecta",
                             error_message="La solicitud que enviaste no es válida."), 400

    # Manejador genérico para otros errores
    @app.errorhandler(Exception)
    def handle_exception(e):
        user_info = get_user_info()
        request_info = get_request_info()
        
        # Si es un error HTTP, usa su código de estado
        if hasattr(e, 'code'):
            log_error(e.code, f"Error HTTP {e.code}: {str(e)}", user_info, request_info)
            return render_template('error.html',
                                 error_code=e.code,
                                 error_title=f"Error {e.code}",
                                 error_message=str(e)), e.code
        else:
            # Para errores no HTTP, devuelve un 500
            log_error(500, f"Error inesperado: {str(e)}", user_info, request_info)
            return render_template('error.html',
                                 error_code=500,
                                 error_title="Error interno",
                                 error_message="Ha ocurrido un error inesperado."), 500

# Rutas de prueba para errores
def register_test_routes(app):
    """Registra rutas de prueba para errores"""
    
    @app.route('/test-error/<int:error_code>')
    def test_error(error_code):
        """Ruta para probar diferentes tipos de errores"""
        from flask import abort
        
        if error_code == 404:
            abort(404)
        elif error_code == 500:
            raise Exception("Error simulado para pruebas")
        elif error_code == 403:
            abort(403)
        elif error_code == 401:
            abort(401)
        elif error_code == 400:
            abort(400)
        else:
            return "Código de error no soportado para pruebas"

# Rutas de monitoreo básicas
def register_monitoring_routes(app):
    """Registra rutas básicas de monitoreo"""
    
    @app.route('/health-check')
    def health_check():
        """Endpoint para verificar el estado de la aplicación"""
        try:
            # Verificación básica de base de datos
            conn = sqlite3.connect('gestor_de_tareas.db')
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            db_status = True
        except:
            db_status = False
        
        return jsonify({
            'status': 'healthy' if db_status else 'unhealthy',
            'database': db_status,
            'timestamp': datetime.now().isoformat()
        })

# Funciones simples sin middleware complejo
def register_security_middleware(app):
    """Registra verificaciones de seguridad básicas"""
    pass  # Deshabilitado temporalmente para evitar conflictos

def setup_rate_limiting(app):
    """Configura rate limiting básico"""
    pass  # Deshabilitado temporalmente para evitar conflictos
